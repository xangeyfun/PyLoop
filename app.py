from flask import Flask, redirect, jsonify, request, render_template, session, flash, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from dotenv import load_dotenv
import secrets
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
os.makedirs("saves", exist_ok=True)

# middleware

@app.before_request
def remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1])

# Temporary ip restrction for testing

@app.before_request
def ip_restrict():
    if request.remote_addr not in ["127.0.0.1"] and request.path not in ["/", "/github"] and not request.path.startswith("/static/"):
        abort(401)

# pages

@app.route("/", methods=["GET"])
def home():
    if 'connected' not in session and 'user' in session:
        file_path = f"saves/{session['user']}.json"

        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                data["ip"] = request.remote_addr

                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)

                session['connected'] = True

            except Exception as e:
                with open("error_log.txt", "a") as f:
                    f.write(f"app.py - [{datetime.now().isoformat()}] - Error updating IP for {session['user']}: {str(e)}\n")

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

@app.route("/profile/<user>", methods=["GET"])
def profile(user):
    if 'user' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect("/login")
    if user != session['user']:
        flash("You can only view your own profile.", "error")
        return redirect("/profile/" + session['user'])
    
    with open(f"saves/{user}.json", "r") as f:
        data = json.load(f)
        with open(f"saves/{user}.json", "r") as f:
            data = json.load(f)

        game_data = data.get("game_data", {})

    return render_template("profile.html", data=data, game_data=game_data)

# API

@app.route("/api/register", methods=["POST"]) # type: ignore
def api_register():
    username = request.form.get("username").strip() # type: ignore
    password = request.form.get("password").strip() # type: ignore

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect("/register")

    if ' ' in username or ' ' in password:
        flash("Username and password cannot contain spaces.", "error")
        return redirect("/register")

    if len(username) < 3 or len(password) < 6:
        flash("Username must be at least 3 characters and password at least 6 characters.", "error")
        return redirect("/register")
    
    if os.path.exists(f"saves/{username}.json"):
        flash("Username already exists.", "error")
        return redirect("/register")

    try:
        with open(f"saves/{username}.json", "w") as f:
            json.dump({"username": username, "password": generate_password_hash(password), "token": secrets.token_hex(3),
            "game_data": {
                "loc": 0,
                "click_value": 1,
                "loc_per_sec": 0,
                "multiplier": 1,
                "u1_price": 25,
                "u1_owned": 1,
                "u2_owned": 1,
                "u2_price": 120
            }}, f, indent=4)
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error creating user {username}: {str(e)}\n")
        flash("An error occurred while creating your account. Please try again.", "error")
        return redirect("/register")
    flash("Account created successfully! Please log in.", "success")
    return redirect("/login")

@app.route("/api/login", methods=["POST"]) # type: ignore
def api_login():
    username = request.form.get("username").strip() # type: ignore
    password = request.form.get("password").strip() # type: ignore

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect("/login")

    if not os.path.exists(f"saves/{username}.json"):
        flash("Invalid username or password.", "error")
        return redirect("/login")

    try:
        with open(f"saves/{username}.json", "r") as f:
            data = json.load(f)
            if check_password_hash(data["password"], password):
                session['user'] = username
                flash("Logged in successfully!", "success")
                return redirect("/")
            else:
                flash("Invalid username or password.", "error")
                return redirect("/login")
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"app.py - [{datetime.now().isoformat()}] - Error during login for {username}: {str(e)}\n")
        flash("An error occurred while logging in. Please try again.", "error")
        return redirect("/login")

@app.route("/api/construct", methods=["OPTIONS","GET","POST"]) # type: ignore
def api_construct():
    if request.method == "OPTIONS":
        return "", 200

    if request.headers.get("X-Secret-Key") != os.getenv("PYLOOP_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    file_path = f"saves/{session['user']}.json"

    if not os.path.exists(file_path):
        return jsonify({"error": "User not found"}), 404

    # LOAD
    if request.method == "GET":
        with open(file_path, "r") as f:
            user_data = json.load(f)
        return jsonify(user_data.get("game_data", {
            "loc": 0,
            "click_value": 1,
            "loc_per_sec": 0,
            "multiplier": 1,
            "u1_price": 25,
            "u1_owned": 1,
            "u2_owned": 1,
            "u2_price": 120
        })), 200

    # SAVE
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        with open(file_path, "r") as f:
            user_data = json.load(f)

        user_data["game_data"] = data

        with open(file_path, "w") as f:
            json.dump(user_data, f, indent=4)

        return jsonify({"message": "Saved"}), 200

# Run the app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6000)
