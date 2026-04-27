from fastapi import FastAPI

import csv
import asyncio
from fastapi import Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from typing import Literal

import smtplib
from email.mime.text import MIMEText
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from backend.auth import create_access_token
from backend.auth import verify_access_token

import hashlib
import random
import joblib
import pandas as pd
import numpy as np
import os

from dotenv import load_dotenv

# ======================
# LOAD ENV FIRST
# ======================
load_dotenv()

# ======================
# FASTAPI APP
# ======================
app = FastAPI()

# ======================
# ROUTERS
# ======================
from backend.auth import router as auth_router
from backend.oauth import router as oauth_router

app.include_router(auth_router)
app.include_router(oauth_router)

# باقي imports الخاصة بمشروعك
from config import FINGERPRINT_FILE
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

from .database import engine, SessionLocal, Base
from .models import BehaviorRecord, UserProfile, RiskLog, User, Notification, SecurityLog


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)



security = HTTPBearer()
blocked_users = {}
active_monitors = {}
blocked_tokens: set[str] = set()
admin_connections = []
user_states = {}
medium_sessions = {}
otp_store = {}
high_risk_counter = {}

ACTIVE = "active"
SUSPENDED = "suspended"
FROZEN = "frozen"
MEDIUM = "medium"

def generate_otp():
    return str(random.randint(100000, 999999))


async def send_otp_email(to_email: str, otp: str):
    message = MessageSchema(
        subject="SentinelX OTP Verification",
        recipients=[to_email],
        body=f"Your OTP code is: {otp}\nIt expires in 5 minutes.",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)



def get_fingerprint_from_db(db: Session, user_id: str):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        return None

    return {
        "avg_key_interval": profile.avg_key_interval,
        "avg_mouse_speed": profile.avg_mouse_speed,
        "country": profile.country
    }

# ==============================
# ML MODELS LOAD (GLOBAL)
# ==============================

if_model = joblib.load("models/user_1_if.pkl")
svm_model = joblib.load("models/user_1_svm.pkl")
lof_model = joblib.load("models/user_1_lof.pkl")
feature_columns = joblib.load("models/user_1_columns.pkl")

print("✅ ML models loaded")

# ==============================
# Database Dependency
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================
# Fake Token System
# ==============================
fake_tokens = {}

def cleanup_expired_tokens():
    now = datetime.utcnow()
    expired_tokens = []

    for token, data in list(fake_tokens.items()):
        if now > data["expires"]:
            expired_tokens.append(token)

    for token in expired_tokens:
        del fake_tokens[token]



def create_token(user_id, remember_me=False):
    token = str(uuid4())

    expiry = datetime.utcnow() + (
        timedelta(days=7) if remember_me else timedelta(hours=1)
    )

    fake_tokens[token] = {
        "user_id": str(user_id),
        "expires": expiry
    }

    return token

# ==============================
# Auth
# ==============================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    # 🔐 verify JWT token
    user_id = verify_access_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 👤 fetch user from database
    user = db.query(User).filter(User.id == str(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def medium_guard(current_user: User = Depends(get_current_user)):
    if str(current_user.id) in medium_sessions:
        raise HTTPException(
            status_code=403,
            detail="Access restricted until OTP verification"
        )


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.account_type != "Administrator":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user
# ==============================
# Password Hashing
# ==============================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ==============================
# Schemas
# ==============================
class BehaviorData(BaseModel):
    user_id: str
    session_id: str
    avg_key_interval: float
    avg_mouse_speed: float
    country: str
    timestamp: datetime


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str
    city: str | None = None
    country: str | None = None
    location: str | None = None
    gender: str   # male / female / other
    department: Literal["Information Technology", "Human Resources", "Finance & Accounting", "Sales & Marketing", "Operations", "Research & Development", "Customer Support", "Legal", "Administration"]
    account_type: str # Standard User / Administrator

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class OTPRequest(BaseModel):
    user_id: str
    otp: str




# ==============================
# Root
# ==============================
@app.get("/")
def root():
    return {"message": "SentinelX Backend is running"}


# ==============================
# Get Users
# ==============================
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/set-fingerprint/{user_id}")
def set_fingerprint(user_id: str, db: Session = Depends(get_db)):

    # 1) هات كل behavior records
    records = db.query(BehaviorRecord).filter(
        BehaviorRecord.user_id == user_id
    ).all()

    if not records:
        return {"error": "No behavior data found"}

    # 2) احسب المتوسطات
    avg_key = sum(r.avg_key_interval for r in records) / len(records)
    avg_mouse = sum(r.avg_mouse_speed for r in records) / len(records)

    # 3) هات أو اعمل profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    # 4) خزّن fingerprint في DB
    profile.avg_key_interval = avg_key
    profile.avg_mouse_speed = avg_mouse
    profile.country = records[-1].country
    profile.total_samples = len(records)

    db.commit()

    return {
        "message": "Fingerprint saved to DB successfully",
        "avg_key_interval": avg_key,
        "avg_mouse_speed": avg_mouse
    }

@app.post("/upload-fingerprint")
def upload_fingerprint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import csv

    try:
        with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        if not reader:
            return {"error": "Fingerprint file empty"}

        data = reader[0]

    except Exception as e:
        return {"error": str(e)}

    avg_key = float(data.get("avg_key_interval", 0))
    avg_mouse = float(data.get("avg_mouse_speed", 0))
    country = data.get("country", "Unknown")

    user_id = str(current_user.id)

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if profile:
        profile.avg_key_interval = avg_key
        profile.avg_mouse_speed = avg_mouse
        profile.total_samples = 1 
        profile.country = country
    else:
        profile = UserProfile(
            user_id=user_id,
            avg_key_interval=avg_key,
            avg_mouse_speed=avg_mouse,
            total_samples=1,
            country=country
        )
        db.add(profile)

    db.commit()

    return {
        "message": "Fingerprint uploaded successfully",
        "avg_key_interval": avg_key,
        "avg_mouse_speed": avg_mouse
    }

# ==============================
# CSV PATH
# ==============================
CSV_FILE_PATH = r"C:\Users\hp\Desktop\sentinelX\raw_training_data.csv"

last_processed_row = 0

def build_fingerprint(user_id: str, db: Session, records: list):

    avg_key = sum(float(r.get("avg_key_interval", 0)) for r in records) / len(records)
    avg_mouse = sum(float(r.get("avg_mouse_speed", 0)) for r in records) / len(records)
    country = records[-1].get("country", "Unknown")

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.avg_key_interval = avg_key
    profile.avg_mouse_speed = avg_mouse
    profile.total_samples = len(records)
    profile.country = country

    db.commit()

    return {
        "avg_key_interval": avg_key,
        "avg_mouse_speed": avg_mouse,
        "country": country
    }


# ==============================
# CSV MONITOR
# ==============================
async def monitor_user(user_id):
    print(f"🔥 Monitor started for user: {user_id}")

    db = SessionLocal()
    loop_counter = 0

    fingerprint = get_fingerprint_from_db(db, user_id)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"⛔ User {user_id} not found - stopping monitor")
        return

    if user.is_frozen:
        print(f"⛔ User {user_id} already frozen - stop monitor")
        return

    # =========================
    # BASELINE CREATION
    # =========================
    if not fingerprint:
        print("⚠️ No fingerprint found - collecting baseline...")

        temp_records = []

        for _ in range(10):
            record = {}
            record.update(collect_input_event())
            record.update(collect_active_application())
            record.update(collect_network_info())
            record.update(collect_location_info())

            temp_records.append(record)
            await asyncio.sleep(1)

        fingerprint = build_fingerprint(user_id, db, temp_records)

        print("✅ Auto fingerprint created")

    # =========================
    # MONITOR LOOP
    # =========================
    while True:
        db = SessionLocal()

        loop_counter += 1

        if loop_counter % 10 == 0:
            fingerprint = get_fingerprint_from_db(db, user_id)

        try:
            # باقي الكود عندك هنا...

            # ==============================
            # 🔐 OTP EXPIRATION CHECK (حطيه هنا)
            # ==============================
            if str(user_id) in otp_store:
                otp_data = otp_store[str(user_id)]

                if datetime.utcnow() > otp_data["expires"]:
                    print(f"⛔ OTP expired for {user_id}")

                    blocked_users[str(user_id)] = datetime.utcnow() + timedelta(minutes=15)

                    print(f"⛔ User {user_id} blocked بسبب تجاهل OTP")
                    return
            # ==============================
            # 🧠 STATE CHECK (NEW)
            # ==============================
            # 🔒 check DB first (source of truth)
            user = db.query(User).filter(User.id == user_id).first()

            if not user or user.is_frozen:
                print(f"⛔ User {user_id} is frozen in DB - stopping monitor")
                active_monitors.pop(user_id, None)
                return
            
            user_state = user_states.get(user_id, ACTIVE)
            if user_state == SUSPENDED:
                print(f"⚠️ User {user_id} is SUSPENDED - slow monitoring")
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(5)

            # ==============================
            # Collect Data
            # ==============================
            record = {}
            record.update(collect_input_event())
            record.update(collect_active_application())
            record.update(collect_network_info())
            record.update(collect_location_info())

            avg_key_interval = float(record.get("avg_key_interval", 0))
            avg_mouse_speed = float(record.get("avg_mouse_speed", 0))
            country = record.get("country", "Unknown")


            # =====================
            # Save Behavior
            # =====================
            new_record = BehaviorRecord(
                id=str(uuid4()),
                user_id=user_id,
                session_id="agent_session",
                avg_key_interval=avg_key_interval,
                avg_mouse_speed=avg_mouse_speed,
                country=country,
                timestamp=datetime.utcnow()
            )

            db.add(new_record)
            db.commit()

            # =====================
            # Compare fingerprint
            # =====================
            risk_score = 0
            alerts = []

            fp_key = fingerprint.get("avg_key_interval", 0)
            fp_mouse = fingerprint.get("avg_mouse_speed", 0)
            fp_country = fingerprint.get("country", "Unknown")

            if fp_key:
                key_diff = abs(avg_key_interval - fp_key) / fp_key
                if key_diff > 0.3:
                    risk_score += 15
                    alerts.append("Keyboard deviation")

            if fp_mouse:
                mouse_diff = abs(avg_mouse_speed - fp_mouse) / fp_mouse
                if mouse_diff > 0.3:
                    risk_score += 15
                    alerts.append("Mouse deviation")

            if fp_country != "Unknown" and country != fp_country:
                risk_score += 15
                alerts.append("Country change")

            # ================= ML SCORE =================
            df = pd.DataFrame([record])
            df = df.reindex(columns=feature_columns, fill_value=0).astype(float)

            votes = 0

            if if_model.predict(df)[0] == -1:
                votes += 1

            if svm_model.predict(df)[0] == -1:
                votes += 1

            if lof_model.predict(df)[0] == -1:
                votes += 1

            ml_score = votes * 5

            # 🔥 هنا الإضافة المهمة
            risk_score += ml_score

            

            # =====================
            # Save Risk
            # =====================
            print("======== DEBUG ========")
            print("risk_score:", risk_score)
            print("alerts:", alerts)
            print("=======================")

            status = "Low"
            if risk_score >= 60:
                status = "High"
            elif risk_score >= 30:
                status = "Medium"

            if status == "Low":
                high_risk_counter[user_id] = 0
                log = SecurityLog(
                    id=str(uuid4()),
                    user_id=user_id,
                    action="LOW_RISK_MONITORING",
                    details=f"Low risk detected: {alerts}"
                )
                db.add(log)
                db.commit()

            for conn in admin_connections:
                try:
                    await conn.send_json({
                        "user_id": user_id,
                        "status": "LOW",
                        "risk": risk_score,
                        "alerts": alerts,
                        "type": "info"
                    })
                except:
                    pass

            if status == "Medium" and str(user_id) not in otp_store:

                otp = generate_otp()

                otp_store[str(user_id)] = {
                    "otp": otp,
                    "expires": datetime.utcnow() + timedelta(minutes=5)
                }

                user = db.query(User).filter(User.id == user_id).first()

                if user:
                    await send_otp_email(user.email, otp)

                print(f"⚠️ MEDIUM RISK DETECTED for {user_id}")

                # 1. خزني session مؤقت
                medium_sessions[str(user_id)] = {
                    "risk_score": risk_score,
                    "alerts": alerts,
                    "timestamp": datetime.utcnow(),
                    "reason": alerts,
                }

                # 2. ابعتي notification
                notif = Notification(
                    id=str(uuid4()),
                    user_id=user_id,
                    message=f"Medium risk detected: verification required",
                    status="unread"
                )
                db.add(notif)
                db.commit()

                # 3. ابعتي للأدمن
                for conn in admin_connections:
                    try:
                        await conn.send_json({
                            "user_id": user_id,
                            "risk": risk_score,
                            "status": "MEDIUM",
                            "alerts": alerts
                        })
                    except:
                        pass

                print("⚠️ MEDIUM RISK - OTP required")
                

            elif status == "High":

                # زودي العداد
                high_risk_counter[user_id] = high_risk_counter.get(user_id, 0) + 1

                print(f"🚨 HIGH RISK DETECTED {user_id} count={high_risk_counter[user_id]}")

                # لو لسه أقل من 3 → ما تعمليش freeze
                if high_risk_counter[user_id] < 3:
                    print("⚠️ Waiting for confirmation before freezing...")
                    continue

                print(f"💥 CONFIRMED HIGH RISK for {user_id}")

                user = db.query(User).filter(User.id == user_id).first()

                if user:
                    user.is_frozen = True
                    db.commit()

                # block tokens
                for token, data in list(fake_tokens.items()):
                    if data["user_id"] == user_id:
                        blocked_tokens.add(token)

                blocked_users[user_id] = datetime.utcnow() + timedelta(minutes=5)

                print(f"🛑 User frozen after repeated high risk")

                return

            if status in ["High", "Medium"]:
                notif = Notification(
                    id=str(uuid4()),
                    user_id=user_id,
                    message=f"{status} risk detected: {alerts}",
                    status="unread"
                )
                db.add(notif)
                db.commit()

            for conn in admin_connections:
                try:
                    await conn.send_json({
                        "user_id": user_id,
                        "risk": risk_score,
                        "status": status,
                        "alerts": alerts
                    })
                except:
                    pass

            # 📜 log
            log = SecurityLog(
                id=str(uuid4()),
                user_id=user_id,
                action=f"{status}_RISK_TRIGGER",
                details=f"Risk={risk_score}, Alerts={alerts}"
            )
            db.add(log)
            db.commit()

            risk_entry = RiskLog(
                user_id=user_id,
                risk_score=risk_score,
                status=status,
                alerts=", ".join(alerts),
                country=country
            )

            db.add(risk_entry)
            db.commit()

            print(f"💾 Saved risk for {user_id}: {risk_score}")

        except Exception as e:
            print("Monitor error:", e)

        finally:
            db.close()

        await asyncio.sleep(5)

# ==============================
# IMPORT + DETECT MANUAL
# ==============================
@app.post("/import-latest-record")
def import_latest_record(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        with open(CSV_FILE_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            print("📊 rows:", len(reader))
            print("📊 last_processed_row:", last_processed_row)

            if not reader:
                return {"error": "CSV file empty"}

            latest = reader[-1]

    except Exception as e:
        return {"error": str(e)}

    avg_key_interval = float(latest.get("avg_key_interval", 0))
    avg_mouse_speed = float(latest.get("avg_mouse_speed", 0))
    country = latest.get("country", "Unknown")

    user_id = str(current_user.id)

    new_record = BehaviorRecord(
        id=str(uuid4()),
        user_id=user_id,
        session_id="agent_session",
        avg_key_interval=avg_key_interval,
        avg_mouse_speed=avg_mouse_speed,
        country=country,
        timestamp=datetime.utcnow()
    )

    db.add(new_record)
    db.commit()

    return {"message": "Record imported"}


# ==============================
# BASELINE
# ==============================
@app.post("/calculate-baseline/{user_id}")
def calculate_baseline(user_id: str, db: Session = Depends(get_db)):

    records = db.query(BehaviorRecord).filter(
        BehaviorRecord.user_id == user_id
    ).all()

    if not records:
        return {"error": "No records found"}

    avg_key = sum(r.avg_key_interval for r in records) / len(records)
    avg_mouse = sum(r.avg_mouse_speed for r in records) / len(records)

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()
    
    

    if profile:
        profile.avg_key_interval = avg_key
        profile.avg_mouse_speed = avg_mouse
        profile.total_samples = len(records)

    else:
        profile = UserProfile(
            user_id=user_id,
            avg_key_interval=avg_key,
            avg_mouse_speed=avg_mouse,
            total_samples=len(records)
        )

        db.add(profile)

    db.commit()

    return {
        "message": "Baseline calculated",
        "avg_key_interval": avg_key,
        "avg_mouse_speed": avg_mouse
    }


# ==============================
# RISK LOGS
# ==============================
@app.get("/risk-logs/{user_id}")
def get_risk_logs(user_id: str, db: Session = Depends(get_db)):

    logs = db.query(RiskLog).filter(
        RiskLog.user_id == user_id
    ).order_by(RiskLog.timestamp.desc()).all()

    return logs


# ==============================
# USER SUMMARY
# ==============================
@app.get("/user-summary/{user_id}")
def get_user_summary(user_id: str, db: Session = Depends(get_db)):

    records = db.query(BehaviorRecord).filter(
        BehaviorRecord.user_id == user_id
    ).all()

    logs = db.query(RiskLog).filter(
        RiskLog.user_id == user_id
    ).order_by(RiskLog.timestamp.desc()).all()

    if not logs:
        return {
            "total_samples": len(records),
            "total_risks": 0
        }

    avg_risk = sum(log.risk_score for log in logs) / len(logs)

    return {
        "total_samples": len(records),
        "total_risks": len(logs),
        "average_risk": round(avg_risk, 2),
        "last_status": logs[0].status
    }

# ==================================
# SYSTEM DASHBOARD
# ==================================
@app.get("/system-dashboard")
def system_dashboard(db: Session = Depends(get_db)):

    total_users = db.query(User).count()
    total_records = db.query(BehaviorRecord).count()
    total_risks = db.query(RiskLog).count()
    active_users = len(active_monitors)

    high_risk = db.query(RiskLog).filter(RiskLog.status == "High").count()
    medium_risk = db.query(RiskLog).filter(RiskLog.status == "Medium").count()
    low_risk = db.query(RiskLog).filter(RiskLog.status == "Low").count()

    if total_risks == 0:
        avg_risk = 0
    else:
        risks = db.query(RiskLog).all()
        avg_risk = sum(r.risk_score for r in risks) / total_risks

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_behavior_records": total_records,
        "total_risks_detected": total_risks,
        "high_risk_events": high_risk,
        "medium_risk_events": medium_risk,
        "low_risk_events": low_risk,
        "average_risk_score": round(avg_risk,2)
    }


# ==================================
# LATEST THREATS
# ==================================
@app.get("/latest-threats")
def latest_threats(db: Session = Depends(get_db)):

    logs = db.query(RiskLog).order_by(
        RiskLog.timestamp.desc()
    ).limit(10).all()

    return [
        {
            "user_id": log.user_id,
            "risk_score": log.risk_score,
            "status": log.status,
            "alerts": log.alerts,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

# ==================================
# TOP RISK USERS
# ==================================
@app.get("/top-risk-users")
def top_risk_users(db: Session = Depends(get_db)):

    users = db.query(RiskLog.user_id).distinct().all()

    results = []

    for u in users:
        user_id = u[0]

        logs = db.query(RiskLog).filter(
            RiskLog.user_id == user_id
        ).all()

        avg_risk = sum(l.risk_score for l in logs) / len(logs)

        results.append({
            "user_id": user_id,
            "average_risk": round(avg_risk,2),
            "events": len(logs)
        })

    results.sort(key=lambda x: x["average_risk"], reverse=True)

    return results[:5]


# ==============================
# REGISTER
# ==============================
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    city = user.city
    country = user.country

    if (not city or not country) and user.location:
        parts = user.location.split(",")

        if len(parts) == 2:
            city = parts[0].strip()
            country = parts[1].strip()
    print(user.dict())

    # check password confirmation
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        return {"error": "User already exists"}

    hashed_pw = hash_password(user.password)

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_pw,
        city=city,
        country=country,
        gender=user.gender,
        department=user.department,
        account_type=user.account_type
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": str(new_user.id)
    }

    

# ==============================
# Login
# ==============================
from fastapi import BackgroundTasks

@app.post("/login")
def login(
    user: UserLogin,
    background_tasks: BackgroundTasks,   
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 🔒 check if account is frozen
    if db_user.is_frozen:
        raise HTTPException(
            status_code=403,
            detail="Account is frozen. Contact admin."
        )

    # ⛔ MEDIUM RISK CHECK (IMPORTANT)
    if str(db_user.id) in medium_sessions:
        return {
            "message": "Verification required",
            "status": "medium_risk",
            "data": medium_sessions[str(db_user.id)]
        }

    user_id = str(db_user.id)

    # 🚨 check لو user blocked
    if user_id in blocked_users:
        block_until = blocked_users[user_id]

        if datetime.utcnow() < block_until:
            raise HTTPException(
                status_code=403,
                detail="User is blocked. Try again later."
            )
        else:
            del blocked_users[user_id]

    # ✅ هنا بس التعديل
    user_id = str(db_user.id)
    token = create_access_token(user_id)
    if user_id in active_monitors:
        print(f"⚠️ Monitor already running for {user_id}")
    else:
        active_monitors[user_id] = True
        user_states[user_id] = ACTIVE
        background_tasks.add_task(monitor_user, user_id)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "role": db_user.account_type,
        "user_id": str(db_user.id)
    }
# ==============================
# START MONITOR
# ==============================
@app.on_event("startup")
async def start_monitor():
    print("🚀 System started")
    Base.metadata.create_all(bind=engine)
    


@app.post("/force-high/{user_id}")
def force_high(user_id: str):

    print("🚨 FORCE HIGH TRIGGERED")

    # 🔒 block tokens القديمة
    for t, data in fake_tokens.items():
        if data["user_id"] == str(user_id):
            blocked_tokens.add(t)

    # ⛔ block user نفسه 5 دقايق
    blocked_users[str(user_id)] = datetime.utcnow() + timedelta(minutes=5)

    return {
        "message": f"High risk simulated for user {user_id}"
    }

@app.get("/admin/users")
def admin_get_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(User).all()

@app.delete("/admin/user/{user_id}")
def delete_user(
    user_id: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
     _ = Depends(medium_guard)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

@app.post("/admin/block/{user_id}")
def block_user(
    user_id: str,
    admin: User = Depends(get_admin_user)
):
    blocked_users[user_id] = datetime.utcnow() + timedelta(minutes=30)
    return {"message": "User blocked"}

@app.get("/admin/notifications")
def get_notifications(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(Notification).order_by(
        Notification.created_at.desc()
    ).all()

@app.get("/admin/threats-last-7-days")
def threats_last_7_days(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    result = []

    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)

        count = db.query(RiskLog).filter(
            RiskLog.timestamp >= day.replace(hour=0, minute=0),
            RiskLog.timestamp < day.replace(hour=23, minute=59)
        ).count()

        result.append({
            "date": day.strftime("%Y-%m-%d"),
            "threats": count
        })

    return result[::-1]


@app.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    admin_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        admin_connections.remove(websocket)

@app.get("/admin/frozen-users")
def get_frozen_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.is_frozen == True).all()
    return users

@app.get("/admin/user-logs/{user_id}")
def get_user_logs(
    user_id: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    logs = db.query(SecurityLog).filter(
        SecurityLog.user_id == user_id
    ).order_by(SecurityLog.timestamp.desc()).all()

    return logs

@app.post("/admin/unfreeze/{user_id}")
def unfreeze_user(
    user_id: str,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔓 Unfreeze (source of truth)
    user.is_frozen = False
    db.commit()

    return {"message": "User unfrozen successfully"}

@app.post("/verify-user/{user_id}")
def verify_user(user_id: str):
    user_id = str(user_id)

    if user_id in medium_sessions:
        del medium_sessions[user_id]

        return {
            "status": "verified",
            "message": "User confirmed, session restored"
        }

    return {"status": "no_verification_needed"}


@app.get("/medium-alert/{user_id}")
def medium_alert(user_id: str):
    if user_id not in medium_sessions:
        return {"status": "safe"}

    return {
        "status": "MEDIUM_RISK",
        "message": "We detected unusual behavior. Please verify it's you.",
        "data": medium_sessions[user_id]
    }

@app.post("/verify-otp")
def verify_otp(data: OTPRequest):
    record = otp_store.get(data.user_id)

    if not record:
        raise HTTPException(status_code=400, detail="No OTP found")

    if datetime.utcnow() > record["expires"]:
        raise HTTPException(status_code=400, detail="OTP expired")

    if record["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # ✅ امسحي OTP
    del otp_store[data.user_id]

    # ✅ امسحي medium session
    if data.user_id in medium_sessions:
        del medium_sessions[data.user_id]

    # ✅ رجعيه active
    user_states[data.user_id] = ACTIVE

    return {"message": "User verified successfully"}




@app.post("/admin/unblock/{user_id}")
def unblock_user(user_id: str):
    if user_id in blocked_users:
        del blocked_users[user_id]

    return {"message": "User unblocked"}

@app.get("/user-profile")
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == str(current_user.id)
    ).first()

    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "department": current_user.department,
        "account_type": current_user.account_type,
        "city": current_user.city,
        "country": current_user.country,
        "avg_key_interval": profile.avg_key_interval if profile else 0,
        "avg_mouse_speed": profile.avg_mouse_speed if profile else 0,
        "total_samples": profile.total_samples if profile else 0
    }