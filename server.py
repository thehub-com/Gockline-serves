from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid, time

app = Flask(__name__)
CORS(app)

limiter = Limiter(app, key_func=get_remote_address)

USERS = {}     # tg_id -> user
TOKENS = {}    # token -> tg_id

def now():
    return int(time.time())

def auth_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token not in TOKENS:
            return {"error": "unauthorized"}, 403
        request.tg_id = TOKENS[token]
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/")
def index():
    return "GockLine server online"

# РЕГИСТРАЦИЯ ОТ БОТА
@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.json
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
        "token": token,
        "id": USERS[tg_id]["id"]
    }

# ПРОФИЛЬ
@app.route("/profile", methods=["GET"])
@auth_required
def profile():
    return USERS[request.tg_id]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
