from flask import Flask, redirect, jsonify, request, render_template
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

# Remove trailing slashes

@app.before_request
def remove_trailing_slash():
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1]), 301

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "X-Secret-Key, Content-Type"
    return response

# About pages

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html"), 200

@app.route("/play", methods=["GET"])
def play():
    return render_template("game.html"), 200

@app.route("/github", methods=["GET"])
def github():
    return redirect("https://github.com/xangey_fun/PyLoop"), 302

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