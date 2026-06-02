from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from fastapi import APIRouter

router = APIRouter()

latest_token = None

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# JWT Blacklist & Active Registry State
blacklisted_tokens = set()
user_active_tokens = {}

def blacklist_token(token: str):
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens

def register_active_token(user_id: str, token: str):
    user_id = str(user_id)
    if user_id not in user_active_tokens:
        user_active_tokens[user_id] = set()
    user_active_tokens[user_id].add(token)

def revoke_user_tokens(user_id: str):
    user_id = str(user_id)
    tokens = user_active_tokens.pop(user_id, set())
    for t in tokens:
        blacklisted_tokens.add(t)


def create_access_token(user_id: int):
    to_encode = {"user_id": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    register_active_token(str(user_id), token)
    return token


def verify_access_token(token: str):
    if is_token_blacklisted(token):
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("user_id"))
    except JWTError:
        return None

@router.get("/send-token")
def send_token(token: str):
    global latest_token
    latest_token = token
    return {"ok": True}