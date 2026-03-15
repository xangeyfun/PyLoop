from flask import Flask, redirect, jsonify, request, render_template, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from datetime import datetime
import requests
import secrets
import sqlite3
import json
import os

# Setup

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("TOKEN")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
HC_SECRET = os.getenv("HC_SECRET")
DEFAULT_GAME_DATA = {
    "loc": 0,
    "click_value": 1,
    "loc_per_sec": 0,
    "multiplier": 1,
    "u1_price": 25,
    "u1_owned": 1,
    "u2_owned": 1,
    "u2_price": 120,
    "u3_owned": 1,
    "u3_price": 400,
    "loc_u1_owned": 1,
    "loc_u1_price": 75,
    "loc_u2_owned": 1,
    "loc_u2_price": 900,
    "loc_u3_owned": 1,
    "loc_u3_price": 12000
}
if os.path.exists("ips.json"):
    with open("ips.json", "r") as f:
        ips = json.load(f)


# middleware

@app.before_request
def remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1])

def format_number(num):
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.1f}T"
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)
app.jinja_env.filters['format_number'] = format_number

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# pages

@app.route("/", methods=["GET"])
def home():
    if 'connected' not in session and 'user' in session:
        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("UPDATE users SET ip=?, last_request=? WHERE username=?", (request.remote_addr, datetime.now().isoformat(), session['user']))
            conn.commit()
            session['connected'] = True

        except Exception as e:
            with open("error_log.txt", "a") as f:
                f.write(f"app.py - [{datetime.now().isoformat()}] - Error updating IP for {session['user']}: {str(e)}\n")

        finally:
            conn.close()

    return render_template("index.html"), 200

@app.route("/game", methods=["GET"])
def play():
    return send_from_directory("static/game", "index.html"), 200

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html"), 200

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html"), 200

@app.route("/logout", methods=["GET"])
def logout():
    if 'user' not in session:
        flash("You are not logged in.", "error")
        return redirect("/login")
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect("/")

@app.route("/github", methods=["GET"])
def github():
    return redirect("https://github.com/xangeyfun/PyLoop")

@app.route("/profile", methods=["GET"])
def profile():
    if 'user' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect("/login")
    
    username = session['user']
    
    try:
        conn = get_db()
        cur = conn.cursor()
        user_data = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user_data:
            flash("User not found", "error")
            return redirect("/")
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error reading progress for {username}: {str(e)}\n")
        flash("An error occurred while reading your progress.", "error")
        return redirect("/")
    finally:
        conn.close()
    
    created_at = user_data["created_at"]
    created_at = datetime.fromisoformat(created_at).strftime("%B %d, %Y")
    
    game_data = json.loads(user_data["game_data"])
    
    return render_template("profile.html", username=username, created_at=created_at, game_data=game_data), 200

# API

@app.route("/profile/reset", methods=["POST"])
def profile_reset():
    if 'user' not in session:
        flash("Please log in to reset your progress.", "error")
        return redirect("/login")
    
    username = session['user']
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET game_data=?, last_request=? WHERE username=?", (json.dumps(DEFAULT_GAME_DATA), datetime.now().isoformat(), username))
        conn.commit()
        
        flash("Progress reset successfully!", "success")
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error resetting progress for {username}: {str(e)}\n")
        flash("An error occurred while resetting your progress.", "error")
    finally:
        conn.close()
    
    return redirect("/profile")

@app.route("/api/register", methods=["POST"]) # type: ignore
def api_register():
    captcha_response = request.form.get("h-captcha-response")
    if not captcha_response:
        flash("Please complete the captcha.", "error")
        return redirect("/register")

    data = {
        "secret": HC_SECRET,
        "response": captcha_response,
        "remoteip": request.remote_addr
    }
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    result = r.json()
    if not result.get("success"):
        flash("Captcha failed, try again.", "error")
        return redirect("/register")
    
    username = request.form.get("username", "").strip() # type: ignore
    password = request.form.get("password", "").strip() # type: ignore

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect("/register")

    if ' ' in username or ' ' in password:
        flash("Username and password cannot contain spaces.", "error")
        return redirect("/register")

    if len(username) < 3 or len(password) < 6:
        flash("Username must be at least 3 characters and password at least 6 characters.", "error")
        return redirect("/register")
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if cur.fetchone():
            flash("Username already exists.", "error")
            return redirect("/register")
        cur.execute("INSERT INTO users (username, password, token, created_at, game_data, last_request, ip) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, generate_password_hash(password), secrets.token_hex(8), datetime.now().isoformat(), json.dumps(DEFAULT_GAME_DATA), datetime.now().isoformat(), request.remote_addr))
        conn.commit()
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error creating user {username}: {str(e)}\n")
        flash("An error occurred while creating your account. Please try again.", "error")
        conn.close()
        return redirect("/register")
    finally:
        conn.close()
    
    flash("Account created successfully! Please log in.", "success")
    return redirect("/login")

@app.route("/api/login", methods=["POST"]) # type: ignore
def api_login():
    captcha_response = request.form.get("h-captcha-response")
    if not captcha_response:
        flash("Please complete the captcha.", "error")
        return redirect("/login")

    data = {
        "secret": HC_SECRET,
        "response": captcha_response,
        "remoteip": request.remote_addr
    }
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    result = r.json()
    if not result.get("success"):
        flash("Captcha failed, try again.", "error")
        return redirect("/login")
    
    username = request.form.get("username", "").strip() # type: ignore
    password = request.form.get("password", "").strip() # type: ignore

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    try:
        user = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password", "error")
            return redirect("/login")
        cur.execute("UPDATE users SET last_login=?, last_request=? WHERE username=?", (datetime.now().isoformat(), datetime.now().isoformat(), username))
        conn.commit()
        
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error during login for {username}: {str(e)}\n")
        flash("An error occurred while logging in. Please try again.", "error")
        return redirect("/login")
    finally:
        conn.close()
    
    session['user'] = username
    flash(f"Logged in succesfully as {username}", "success")
    return redirect("/")

@app.route("/api/construct", methods=["OPTIONS","GET","POST"]) # type: ignore
def api_construct():
    if request.method == "OPTIONS":
        return "", 200

    if request.headers.get("X-Secret-Key") != os.getenv("PYLOOP_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    username = session['user']

    try:
        conn = get_db()
        cur = conn.cursor()

        # LOAD
        if request.method == "GET":
            user_data = cur.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if not user_data:
                return jsonify({"error": "User not found"}), 404
            cur.execute("UPDATE users SET last_request=? WHERE username=?", (datetime.now().isoformat(), username))
            conn.commit()
            game_data = json.loads(user_data["game_data"])
            game_data["username"] = user_data["username"]
            return jsonify(game_data), 200

        # SAVE
        if request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400

            cur.execute("UPDATE users SET game_data=?, last_request=? WHERE username=?", (json.dumps(data), datetime.now().isoformat(), username))
            conn.commit()

            return jsonify({"message": "Saved"}), 200
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error during saving for {username}: {str(e)}\n")
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

# Run the app

if __name__ == "__main__":
    # Setup SQL database
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            token TEXT UNIQUE,
            created_at TEXT,
            game_data TEXT,
            last_login TEXT,
            last_request TEXT,
            ip TEXT
        )
        """)
        conn.commit()
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)
    finally:
        conn.close()

    # Run Flask Server
    app.run(debug=True, port=6000)
