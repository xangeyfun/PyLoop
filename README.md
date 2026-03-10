# PyLoop

A coding-themed idle clicker game. Earn LOC by clicking or buying upgrades that generate progress over time.

**Live:** [pyloop.xangey.dev](https://pyloop.xangey.dev/)

---

## Local Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/yourusername/PyLoop.git
cd PyLoop
```

### 2. Create environment file

```bash
cp .env.example .env
```

Edit `.env` and add a secret key:
```
TOKEN=your-secret-key-here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

Development:
```bash
python app.py
```

Production (gunicorn):
```bash
gunicorn -w 2 -b 127.0.0.1:6000 app:app
```

The game will be available at `http://localhost:6000`.

---

## Project Structure

- `app.py` - Flask backend
- `saves/` - Player save data (JSON)
- `static/` - Frontend assets
- `templates/` - HTML templates

---

## Tech

Flask + Construct 3

---

[MIT License](LICENSE)
