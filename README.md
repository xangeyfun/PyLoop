# PyLoop

> Coding-themed idle clicker game built with Flask and Construct 3.

🌐 Website: [https://pyloop.nexohub.ddns.net/](https://pyloop.nexohub.ddns.net/)

PyLoop is an idle clicker game where players earn **LOC** by clicking or by purchasing automated upgrades that generate progress over time.

This project was developed while experimenting with backend APIs, persistent storage systems, and real-time game synchronization.

---

## 🎮 Features

* Session-based account save system
* Automatic progress synchronization
* Offline fallback mode when the server is unreachable
* Upgrade-based idle progression mechanics
* Background music and audio handling
* Coding-themed UI design
* Secure request validation headers

---

## 🧠 Technical Overview

### Frontend

* Construct 3 game engine
* JavaScript event scripting
* Fetch-based communication with backend APIs

### Backend

* Flask web server
* JSON file storage per player account
* Session-authenticated save management
* Response security headers
* Input validation middleware

---

## 💾 Save System

Player progress is periodically synchronized with the backend server during gameplay.

Stored game data includes:

* LOC currency value
* Click power multiplier
* Automatic income rate
* Upgrade ownership and pricing

If the server cannot be reached, the game switches to offline mode, but progress may not be saved until connection is restored.

> Note: This project is intended for educational use and is not production-level secure.

---

## 🔐 Security Design

* Header-based API authentication
* Session-managed player identity
* Basic request validation
* HTTPS-compatible cookie handling

---

## 🚀 Running Locally

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start backend server

```bash
python app.py
```

Production deployment:

```bash
gunicorn -w 2 -b 127.0.0.1:6000 app:app
```

---

## 📜 License

This project is licensed under the MIT License.

---

Made by xangey_fun
