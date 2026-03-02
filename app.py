from flask import Flask, redirect, jsonify, request, render_template, session, flash, get_flashed_messages
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
app.secret_key = secrets.token_hex(32)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
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

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Secret-Key, Content-Type"
    return response

# pages

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html"), 200

@app.route("/play", methods=["GET"])
def play():
    if 'user' not in session:
        flash("Please log in to play the game.", "error")
        return redirect("/login")
    return render_template("game.html"), 200

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
    return redirect("https://github.com/xangey_fun/PyLoop")

@app.route("/profile/<user>", methods=["GET"])
def profile(user):
    if 'user' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect("/login")
    if user != session['user']:
        flash("You can only view your own profile.", "error")
        return redirect("/profile/" + session['user'])
    
    with open(f"saves/{user}.json", "r") as f:
        try:
            user_data = json.load(f)
        except Exception as e:
            with open("error_log.txt", "a") as f:
                f.write(f"app.py - [{datetime.now().isoformat()}] - Error reading profile data for {user}: {str(e)}\n")
            flash("An error occurred while loading your profile. Please try again.", "error")
            return redirect("/")
    return render_template("profile.html", data=user_data), 200

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
            json.dump({"username": username, "password": generate_password_hash(password), "token": secrets.token_hex(3)}, f, indent=4)
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

    if request.method == "GET":
        player_id = request.remote_addr
        if not os.path.exists(f"saves/{player_id}.json"):
            with open(f"saves/{player_id}.json", "w") as f:
                json.dump({
                    "loc": 0,
                    "click_value": 1,
                    "loc_per_sec": 0,
                    "multiplier": 1,
                    "u1_price": 25,
                    "u1_owned": 0,
                    "u2_owned": 0,
                    "u2_price": 120
                }, f, indent=4)
            return jsonify({
                "loc": 0,
                "click_value": 1,
                "loc_per_sec": 0,
                "multiplier": 1,
                "u1_price": 25,
                "u1_owned": 1,
                "u2_owned": 1,
                "u2_price": 120
            }), 200
        with open(f"saves/{player_id}.json", "r") as f:
            try:
                data = json.load(f)
                return jsonify(data), 200
            except Exception as e:
                with open("error_log.txt", "a") as f:
                    f.write(f"app.py - [{datetime.now().isoformat()}] - Error reading save file for {player_id}: {str(e)}\n")
                return jsonify({"error": "Failed to read save data"}), 500

    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        player_id = request.remote_addr
        keys = ["loc","click_value","loc_per_sec","multiplier","u1_price","u1_owned","u2_owned","u2_price"]

        if not all(key in data for key in keys):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            with open(f"saves/{player_id}.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            with open("error_log.txt", "a") as f:
                f.write(f"app.py - [{datetime.now().isoformat()}] - Error writing save file for {player_id}: {str(e)}\n")
            return jsonify({"error": "Failed to save data"}), 500

        return jsonify({"message": "Data saved successfully"}), 200

# Run the app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6000)