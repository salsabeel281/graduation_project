from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.auth import create_access_token
from .database import SessionLocal
from .models import User
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
latest_token = None


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# ================= GOOGLE =================
REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/auth/google/login")
def google_login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
    )
    return {"url": url}

@router.get("/auth/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    access_token = token_json.get("access_token")

    if not access_token:
        return {"error": "Failed to get Google access token"}

    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    headers = {"Authorization": f"Bearer {access_token}"}

    user_response = requests.get(user_info_url, headers=headers)
    user_info = user_response.json()

    email = user_info.get("email")
    name = user_info.get("name", "GoogleUser")

    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        db_user = User(
            email=email,
            first_name=name.split(" ")[0],
            last_name=" ".join(name.split(" ")[1:]) if " " in name else "",
            hashed_password="google_auth"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    token = create_access_token(str(db_user.id))

    return RedirectResponse(
        f"http://127.0.0.1:8000/auth/callback/success?token={token}"
)



# ================= GITHUB =================
GITHUB_REDIRECT_URI = "http://127.0.0.1:8000/auth/github/callback"

@router.get("/auth/github/login")
def github_login():
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=user:email"
    )
    return {"url": url}

@router.get("/auth/github/callback")
def github_callback(code: str, db: Session = Depends(get_db)):

    token_url = "https://github.com/login/oauth/access_token"

    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code
    }

    headers = {
        "Accept": "application/json"
    }

    token_response = requests.post(token_url, data=data, headers=headers)
    token_json = token_response.json()

    access_token = token_json.get("access_token")

    if not access_token:
        return {"error": "Failed to get GitHub access token"}

    user_url = "https://api.github.com/user"

    headers = {
        "Authorization": f"token {access_token}"
    }

    user_response = requests.get(user_url, headers=headers)
    user_info = user_response.json()

    email = user_info.get("email")
    name = user_info.get("name") or user_info.get("login")

    if not email:
        emails_url = "https://api.github.com/user/emails"
        emails_response = requests.get(emails_url, headers=headers)
        emails = emails_response.json()

        if isinstance(emails, list) and len(emails) > 0:
            email = emails[0].get("email")

    if not email:
        return {"error": "GitHub email not found"}

    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        db_user = User(
            email=email,
            first_name=name,
            last_name="",
            hashed_password="github_auth"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    token = create_access_token(str(db_user.id))

    return {
        "access_token": token,
        "token_type": "bearer",
        "email": email
    }

from fastapi.responses import HTMLResponse

@router.get("/auth/callback/success")
def auth_success(token: str):
    return HTMLResponse(f"""
        <html>
            <body>
                <h2>Login Successful ✅</h2>
                <script>
                    fetch("http://127.0.0.1:8000/send-token?token={token}")
                    .then(() => {{
                        window.close();
                    }});
                </script>
            </body>
        </html>
    """)
@router.get("/send-token")
def send_token(token: str):
    global latest_token
    latest_token = token
    return {"token": token}

