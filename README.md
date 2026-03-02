# PyLoop

PyLoop is a coding-themed idle clicker game built using Flask and Construct 3.  
The game uses a backend server to store player progress and periodically syncs saves.

## 🎮 About the Project

PyLoop is a simple idle clicker game where players can earn **LOC** by clicking or using automated upgrades.

The project was made as a school assignment while experimenting with:

- Backend API development  
- Client-server communication  
- Persistent game storage  
- Basic security headers  
- Game audio integration  

## ✨ Features

- Automatic server saving every few seconds  
- Game progress persistence across sessions  
- Secret header authentication for API access  
- JSON based save storage  
- Offline fallback behavior  
- Background music system  
- Coding-themed UI design  

## 🧠 Architecture

The project uses:

### Frontend
- Construct 3 game engine  
- JavaScript scripting blocks  
- AJAX communication with backend API  

### Backend
- Flask web server  
- JSON file storage per player IP  
- CORS protection  
- Request validation  

## 💾 Save System

The game synchronizes progress with the server every few seconds.

Save data includes:

- LOC currency value  
- Click value  
- Auto-generation rate  
- Upgrade ownership and pricing  

If the server cannot be reached, the game continues in offline mode but progress may not be saved.

## 🔐 Security Notes

- Requests require a secret header key  
- Basic request validation is implemented  
- Player saves are separated by IP address  

*(This system is intended for a school project and is not production secure.)*

## 🚀 Running the Project

### Backend

Install dependencies:

```bash
pip install -r requirements.txt
````

Run server:

```bash
python app.py
```

Or if using production deployment:

```bash
gunicorn -w 2 -b 127.0.0.1:6000 app:app
```

## 📜 License

This project is licensed under the MIT License.

---

Made by xangey_fun