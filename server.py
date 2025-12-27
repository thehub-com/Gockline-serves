from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid
import time

app = Flask(__name__)
CORS(app)

# ✅ ПРАВИЛЬНАЯ инициализация Limiter
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# -------------------------
# ВРЕМЕННОЕ ХРАНИЛИЩЕ
# -------------------------
USERS = {}      # tg_id -> user data
TOKENS = {}     # token -> tg_id

# -------------------------
# УТИЛИТЫ
# -------------------------
def now():
    return int(time.time())

def auth_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token not in TOKENS:
            return jsonify({"error": "unauthorized"}), 403
        request.tg_id = TOKENS[token]
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# -------------------------
# ПРОВЕРКА СЕРВЕРА
# -------------------------
@app.route("/")
def index():
    return "GockLine server online"

# -------------------------
# РЕГИСТРАЦИЯ (ОТ БОТА)
# -------------------------
@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.json or {}
    tg_id = str(data.get("tg_id"))
    username = data.get("username")

    if not tg_id or not username:
        return {"error": "bad data"}, 400

    if tg_id not in USERS:
        USERS[tg_id] = {
            "id": len(USERS) + 1,
            "tg_id": tg_id,
            "username": username,
            "nick": username,
            "role": "user",
            "gip": 0
        }

    token = str(uuid.uuid4())
    TOKENS[token] = tg_id

    return {
        "id": USERS[tg_id]["id"],
        "token": token
    }

# -------------------------
# ПРОФИЛЬ
# -------------------------
@app.route("/profile", methods=["GET"])
@auth_required
def profile():
    return USERS[request.tg_id]

@app.route("/profile/edit", methods=["POST"])
@auth_required
def edit_profile():
    data = request.json or {}
    nick = data.get("nick")
    if nick and len(nick) >= 3:
        USERS[request.tg_id]["nick"] = nick
    return {"ok": True}

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
