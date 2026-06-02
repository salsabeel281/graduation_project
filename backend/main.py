import csv
import asyncio
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Literal
import os
import hashlib
import joblib
import pandas as pd
import numpy as np
import logging
from dotenv import load_dotenv

# ======================
# LOAD ENV FIRST
# ======================
load_dotenv()

# ======================
# STRUCTURED LOGGING
# ======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinelx")

# Set up file handler
file_handler = logging.FileHandler("sentinelx.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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

from config import FINGERPRINT_FILE
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

from .database import engine, SessionLocal, Base
from .models import BehaviorRecord, UserProfile, RiskLog, User, Notification, SecurityLog

# ======================
# CONFIGURATION
# ======================
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "raw_training_data.csv")

# ======================
# GLOBAL STATES
# ======================
from backend.auth import create_access_token, verify_access_token, is_token_blacklisted, revoke_user_tokens

security = HTTPBearer()
blocked_users = {}
active_monitors = {}
blocked_tokens: set[str] = set()
admin_connections = []
user_states = {}

ACTIVE = "active"
SUSPENDED = "suspended"
FROZEN = "frozen"

def get_fingerprint_from_db(db: Session, user_id: str):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return None
    return {
        "avg_key_interval": profile.avg_key_interval,
        "typing_variance": profile.typing_variance,
        "avg_mouse_speed": profile.avg_mouse_speed,
        "mouse_acceleration": profile.mouse_acceleration,
        "active_app_patterns": profile.active_app_patterns,
        "session_duration": profile.session_duration,
        "city": profile.city,
        "country": profile.country,
        "ip_address": profile.ip_address,
        "public_ip": profile.public_ip,
        "network_ssid": profile.network_ssid,
        "download_bytes": profile.download_bytes,
        "upload_bytes": profile.upload_bytes
    }

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
# Auth Dependency & Blacklist Check
# ==============================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    # Validate blacklist
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been blacklisted")

    # verify JWT token
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # fetch user from database
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # check if frozen
    if user.is_frozen:
        raise HTTPException(
            status_code=403,
            detail="Account is frozen. Contact admin."
        )

    # check if blocked
    user_id_str = str(user.id)
    if user_id_str in blocked_users:
        block_until = blocked_users[user_id_str]
        if datetime.utcnow() < block_until:
            raise HTTPException(
                status_code=403,
                detail="User is blocked. Try again later."
            )
        else:
            del blocked_users[user_id_str]

    return user

def verify_not_restricted(current_user: User = Depends(get_current_user)):
    if current_user.risk_state == "suspended":
        raise HTTPException(
            status_code=403,
            detail="Access to sensitive operation denied due to elevated risk level (Medium Risk)."
        )
    return current_user

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.account_type != "Administrator":
        raise HTTPException(status_code=403, detail="Admins only")
    if current_user.risk_state == "suspended":
        raise HTTPException(
            status_code=403,
            detail="Administrative action denied due to elevated risk level (Medium Risk)."
        )
    return current_user

# ==============================
# Password Hashing
# ==============================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
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
    gender: str
    department: Literal["Information Technology", "Human Resources", "Finance & Accounting", "Sales & Marketing", "Operations", "Research & Development", "Customer Support", "Legal", "Administration"]
    account_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

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

# ==========================================
# ML Models Training Pipeline Helper & Routes
# ==========================================
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor

def train_user_model(user_id: str, db: Session) -> bool:
    user_id = str(user_id)
    records = db.query(BehaviorRecord).filter(BehaviorRecord.user_id == user_id).all()
    if len(records) < 100:
        logger.warning(f"Not enough records to train user {user_id}: {len(records)} < 100")
        return False

    logger.info(f"Training ML models for user {user_id} using {len(records)} samples...")

    # Calculate app pattern frequencies
    app_counts = {}
    for r in records:
        app = r.active_app_patterns or "Unknown"
        if app != "Unknown":
            app_counts[app] = app_counts.get(app, 0) + 1
    
    import json
    app_patterns_str = json.dumps(app_counts)

    # Calculate fingerprint features averages
    avg_key = sum(r.avg_key_interval for r in records if r.avg_key_interval is not None) / len(records)
    avg_var = sum(r.typing_variance for r in records if r.typing_variance is not None) / len(records)
    avg_mouse = sum(r.avg_mouse_speed for r in records if r.avg_mouse_speed is not None) / len(records)
    avg_accel = sum(r.mouse_acceleration for r in records if r.mouse_acceleration is not None) / len(records)
    avg_duration = sum(r.session_duration for r in records if r.session_duration is not None) / len(records)
    avg_download = sum(r.download_bytes for r in records if r.download_bytes is not None) / len(records)
    avg_upload = sum(r.upload_bytes for r in records if r.upload_bytes is not None) / len(records)

    last_rec = records[-1]
    last_country = last_rec.country or "Unknown"
    last_city = last_rec.city or "Unknown"
    last_ip = last_rec.ip_address or "Unknown"
    last_pub_ip = last_rec.public_ip or "Unknown"
    last_ssid = last_rec.network_ssid or "Unknown"

    # Save to UserProfile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.avg_key_interval = avg_key
    profile.typing_variance = avg_var
    profile.avg_mouse_speed = avg_mouse
    profile.mouse_acceleration = avg_accel
    profile.session_duration = avg_duration
    profile.city = last_city
    profile.country = last_country
    profile.ip_address = last_ip
    profile.public_ip = last_pub_ip
    profile.network_ssid = last_ssid
    profile.download_bytes = avg_download
    profile.upload_bytes = avg_upload
    profile.active_app_patterns = app_patterns_str
    profile.total_samples = len(records)
    db.commit()

    # Generate training dataset
    train_data = []
    for r in records:
        train_data.append({
            "avg_key_interval": r.avg_key_interval or 0.0,
            "typing_variance": r.typing_variance or 0.0,
            "avg_mouse_speed": r.avg_mouse_speed or 0.0,
            "mouse_acceleration": r.mouse_acceleration or 0.0,
            "session_duration": r.session_duration or 0.0,
            "download_bytes": r.download_bytes or 0.0,
            "upload_bytes": r.upload_bytes or 0.0,
            "is_usual_app": 1.0,
            "is_usual_country": 1.0,
            "is_usual_city": 1.0,
            "is_usual_ip": 1.0
        })

    df = pd.DataFrame(train_data)
    feature_columns = df.columns.tolist()

    os.makedirs("models", exist_ok=True)
    
    # Save feature columns
    joblib.dump(feature_columns, f"models/user_{user_id}_columns.pkl")

    # Fit Isolation Forest
    if_model = IsolationForest(contamination=0.1, random_state=42)
    if_model.fit(df)
    joblib.dump(if_model, f"models/user_{user_id}_if.pkl")

    # Fit One-Class SVM
    svm_model = OneClassSVM(nu=0.1, kernel="rbf")
    svm_model.fit(df)
    joblib.dump(svm_model, f"models/user_{user_id}_svm.pkl")

    # Fit LOF
    lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True)
    lof_model.fit(df)
    joblib.dump(lof_model, f"models/user_{user_id}_lof.pkl")

    # Mark user as trained
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_trained = True
        user.training_samples = len(records)
        user.last_training_date = datetime.utcnow()
        user.model_version = (user.model_version or 1) + 1
        db.commit()

    logger.info(f"Model training succeeded for user {user_id}")
    return True

@app.post("/train-model/{user_id}")
def train_model(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(verify_not_restricted)):
    success = train_user_model(user_id, db)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to train model. Ensure user has at least 100 behavior samples."
        )
    return {"message": "Model trained successfully", "user_id": user_id}

@app.post("/set-fingerprint/{user_id}")
def set_fingerprint(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(verify_not_restricted)):
    success = train_user_model(user_id, db)
    if not success:
        return {"error": "Failed to train and set fingerprint. Need at least 100 samples."}
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    return {
        "message": "Fingerprint saved to DB successfully",
        "avg_key_interval": profile.avg_key_interval,
        "avg_mouse_speed": profile.avg_mouse_speed
    }

@app.post("/calculate-baseline/{user_id}")
def calculate_baseline(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(verify_not_restricted)):
    success = train_user_model(user_id, db)
    if not success:
        return {"error": "No records found or not enough records (minimum 100 required)"}
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    return {
        "message": "Baseline calculated",
        "avg_key_interval": profile.avg_key_interval,
        "avg_mouse_speed": profile.avg_mouse_speed
    }

@app.post("/upload-fingerprint")
def upload_fingerprint(
    current_user: User = Depends(verify_not_restricted),
    db: Session = Depends(get_db)
):
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
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
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

# ==================================
# ONBOARDING TRAINING COLLECTOR TASK
# ==================================
async def collect_training_samples(user_id):
    logger.info(f"Onboarding collection started for user: {user_id}")
    user_id = str(user_id)
    
    while True:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.is_frozen:
                logger.info(f"Onboarding stopped for user {user_id} (frozen or not found)")
                break

            if user.is_trained:
                logger.info(f"Onboarding finished for user {user_id} (already trained)")
                if user_id not in active_monitors:
                    active_monitors[user_id] = True
                user_states[user_id] = ACTIVE
                asyncio.create_task(monitor_user(user_id))
                break

            # Collect record
            record = {}
            record.update(collect_input_event())
            record.update(collect_active_application())
            record.update(collect_network_info())
            record.update(collect_location_info())

            avg_key_interval = float(record.get("avg_key_interval", 0.0))
            typing_variance = float(record.get("typing_variance", 0.0))
            avg_mouse_speed = float(record.get("avg_mouse_speed", 0.0))
            mouse_acceleration = float(record.get("mouse_acceleration", 0.0))
            active_app = record.get("active_application", "Unknown")
            country = record.get("country", "Unknown")
            city = record.get("city", "Unknown")
            ip = record.get("ip_address", "Unknown")
            pub_ip = record.get("public_ip", "Unknown")
            ssid = record.get("network_ssid", "Unknown")
            download = float(record.get("download_bytes", 0.0))
            upload = float(record.get("upload_bytes", 0.0))

            if not user.session_start:
                user.session_start = datetime.utcnow()
                db.commit()

            duration = (datetime.utcnow() - user.session_start).total_seconds()

            new_record = BehaviorRecord(
                id=str(uuid4()),
                user_id=user_id,
                session_id="training_session",
                avg_key_interval=avg_key_interval,
                typing_variance=typing_variance,
                avg_mouse_speed=avg_mouse_speed,
                mouse_acceleration=mouse_acceleration,
                active_app_patterns=active_app,
                session_duration=duration,
                city=city,
                country=country,
                ip_address=ip,
                public_ip=pub_ip,
                network_ssid=ssid,
                download_bytes=download,
                upload_bytes=upload,
                timestamp=datetime.utcnow()
            )
            db.add(new_record)
            
            user.training_samples = (user.training_samples or 0) + 1
            db.commit()

            logger.info(f"Onboarding user {user_id}: collected sample {user.training_samples}/100")

            if user.training_samples >= 100:
                logger.info(f"Onboarding user {user_id}: threshold reached. Auto training model...")
                train_success = train_user_model(user_id, db)
                if train_success:
                    user_states[user_id] = ACTIVE
                    asyncio.create_task(monitor_user(user_id))
                    break

        except Exception as e:
            logger.error(f"Onboarding error for user {user_id}: {e}")
        finally:
            db.close()

        await asyncio.sleep(5)

# ==============================
# MONITORING ENGINE & BACKGROUND LOOP
# ==============================
from core.engines import RiskEngine, DecisionEngine, ActionEngine, SecurityAction

async def monitor_user(user_id):
    logger.info(f"Active monitoring started for user: {user_id}")
    user_id = str(user_id)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found. Monitoring aborted.")
            return
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.error(f"Fingerprint profile missing for user {user_id}. Monitoring aborted.")
            return
        
        fingerprint = {
            "avg_key_interval": profile.avg_key_interval,
            "typing_variance": profile.typing_variance,
            "avg_mouse_speed": profile.avg_mouse_speed,
            "mouse_acceleration": profile.mouse_acceleration,
            "active_app_patterns": profile.active_app_patterns,
            "session_duration": profile.session_duration,
            "city": profile.city,
            "country": profile.country,
            "ip_address": profile.ip_address,
            "public_ip": profile.public_ip,
            "network_ssid": profile.network_ssid,
            "download_bytes": profile.download_bytes,
            "upload_bytes": profile.upload_bytes
        }
    finally:
        db.close()

    loop_counter = 0
    while True:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.is_frozen:
                logger.info(f"Monitoring stopped for user {user_id} (frozen or deleted)")
                active_monitors.pop(user_id, None)
                break

            loop_counter += 1
            if loop_counter % 10 == 0:
                profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                if profile:
                    fingerprint = {
                        "avg_key_interval": profile.avg_key_interval,
                        "typing_variance": profile.typing_variance,
                        "avg_mouse_speed": profile.avg_mouse_speed,
                        "mouse_acceleration": profile.mouse_acceleration,
                        "active_app_patterns": profile.active_app_patterns,
                        "session_duration": profile.session_duration,
                        "city": profile.city,
                        "country": profile.country,
                        "ip_address": profile.ip_address,
                        "public_ip": profile.public_ip,
                        "network_ssid": profile.network_ssid,
                        "download_bytes": profile.download_bytes,
                        "upload_bytes": profile.upload_bytes
                    }

            user_state = user_states.get(user_id, ACTIVE)
            if user_state == "suspended":
                logger.info(f"User {user_id} is SUSPENDED. Slowing down monitoring loop.")
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(5)

            # Collect record
            record = {}
            record.update(collect_input_event())
            record.update(collect_active_application())
            record.update(collect_network_info())
            record.update(collect_location_info())

            avg_key_interval = float(record.get("avg_key_interval", 0.0))
            typing_variance = float(record.get("typing_variance", 0.0))
            avg_mouse_speed = float(record.get("avg_mouse_speed", 0.0))
            mouse_acceleration = float(record.get("mouse_acceleration", 0.0))
            active_app = record.get("active_application", "Unknown")
            country = record.get("country", "Unknown")
            city = record.get("city", "Unknown")
            ip = record.get("ip_address", "Unknown")
            pub_ip = record.get("public_ip", "Unknown")
            ssid = record.get("network_ssid", "Unknown")
            download = float(record.get("download_bytes", 0.0))
            upload = float(record.get("upload_bytes", 0.0))

            if not user.session_start:
                user.session_start = datetime.utcnow()
                db.commit()

            duration = (datetime.utcnow() - user.session_start).total_seconds()

            new_record = BehaviorRecord(
                id=str(uuid4()),
                user_id=user_id,
                session_id="agent_session",
                avg_key_interval=avg_key_interval,
                typing_variance=typing_variance,
                avg_mouse_speed=avg_mouse_speed,
                mouse_acceleration=mouse_acceleration,
                active_app_patterns=active_app,
                session_duration=duration,
                city=city,
                country=country,
                ip_address=ip,
                public_ip=pub_ip,
                network_ssid=ssid,
                download_bytes=download,
                upload_bytes=upload,
                timestamp=datetime.utcnow()
            )
            db.add(new_record)
            db.commit()

            current_record_dict = {
                "avg_key_interval": avg_key_interval,
                "typing_variance": typing_variance,
                "avg_mouse_speed": avg_mouse_speed,
                "mouse_acceleration": mouse_acceleration,
                "active_application": active_app,
                "country": country,
                "city": city,
                "ip_address": ip,
                "public_ip": pub_ip,
                "network_ssid": ssid,
                "download_bytes": download,
                "upload_bytes": upload,
                "session_duration": duration
            }

            # Pass record to engines
            risk_score, alerts = RiskEngine.calculate_risk(
                current_record_dict,
                fingerprint,
                user_id,
                db
            )

            # Decide Action
            action = DecisionEngine.decide_action(risk_score)

            # Execute Action
            await ActionEngine.execute(
                user_id=user_id,
                action=action,
                risk_score=risk_score,
                alerts=alerts,
                db=db,
                blocked_users=blocked_users,
                user_states=user_states,
                admin_connections=admin_connections,
                record=current_record_dict
            )

            if action == SecurityAction.FREEZE:
                active_monitors.pop(user_id, None)
                break

            # AUTOMATIC RETRAINING CHECK
            current_records_count = db.query(BehaviorRecord).filter(BehaviorRecord.user_id == user_id).count()
            last_training_count = user.training_samples or 0
            if current_records_count - last_training_count >= 50:
                logger.info(f"Auto retraining triggered for user {user_id}. New records count: {current_records_count - last_training_count}")
                retrain_success = train_user_model(user_id, db)
                if retrain_success:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        user.training_samples = current_records_count
                        db.commit()
                    logger.info(f"Auto retraining finished for user {user_id}. Model version is now {user.model_version if user else 'N/A'}")

        except Exception as e:
            logger.error(f"Monitor error for user {user_id}: {e}")
        finally:
            db.close()

        await asyncio.sleep(5)

# ==============================
# IMPORT + DETECT MANUAL
# ==============================
@app.post("/import-latest-record")
def import_latest_record(
    current_user: User = Depends(verify_not_restricted),
    db: Session = Depends(get_db)
):
    try:
        with open(CSV_FILE_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
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
            "total_risks": 0,
            "average_risk": 0.0,
            "current_risk": 0,
            "highest_risk": 0,
            "risk_history": [],
            "risk_trends": []
        }

    avg_risk = sum(log.risk_score for log in logs) / len(logs)
    highest_risk = max(log.risk_score for log in logs)
    current_risk = logs[0].risk_score

    risk_history = [
        {
            "risk_score": log.risk_score,
            "status": log.status,
            "alerts": log.alerts,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]

    risk_trends = [
        {
            "risk_score": log.risk_score,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in reversed(logs)
    ]

    return {
        "total_samples": len(records),
        "total_risks": len(logs),
        "average_risk": round(avg_risk, 2),
        "last_status": logs[0].status,
        "current_risk": current_risk,
        "highest_risk": highest_risk,
        "risk_history": risk_history,
        "risk_trends": risk_trends
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
        account_type=user.account_type,
        is_oauth=False
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
@app.post("/login")
def login(
    user: UserLogin,
    background_tasks: BackgroundTasks,   
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Prevent standard password login for OAuth users who don't have password set
    if db_user.is_oauth and (db_user.hashed_password is None or db_user.hashed_password in ["google_auth", "github_auth", ""]):
        raise HTTPException(
            status_code=400,
            detail="This account uses OAuth. Please login via Google or GitHub."
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # check if account is frozen
    if db_user.is_frozen:
        raise HTTPException(
            status_code=403,
            detail="Account is frozen. Contact admin."
        )

    user_id = str(db_user.id)
    # check لو user blocked
    if user_id in blocked_users:
        block_until = blocked_users[user_id]
        if datetime.utcnow() < block_until:
            raise HTTPException(
                status_code=403,
                detail="User is blocked. Try again later."
            )
        else:
            del blocked_users[user_id]

    token = create_access_token(user_id)
    db_user.session_start = datetime.utcnow()
    db.commit()

    if user_id in active_monitors:
        logger.info(f"Monitor/Onboarding already running for {user_id}")
    else:
        active_monitors[user_id] = True
        if db_user.is_trained:
            user_states[user_id] = ACTIVE
            background_tasks.add_task(monitor_user, user_id)
        else:
            user_states[user_id] = ACTIVE
            background_tasks.add_task(collect_training_samples, user_id)

    return {
        "access_token": token,
        "token_type": "Bearer",
        "role": db_user.account_type,
        "user_id": str(db_user.id)
    }

# ==============================
# START MONITOR / MIGRATIONS
# ==============================
def run_migrations():
    from sqlalchemy import text
    db = SessionLocal()
    try:
        # Check User columns
        user_cols = [
            ("is_trained", "BOOLEAN DEFAULT 0"),
            ("training_samples", "INTEGER DEFAULT 0"),
            ("last_training_date", "DATETIME"),
            ("model_version", "INTEGER DEFAULT 1"),
            ("is_oauth", "BOOLEAN DEFAULT 0"),
            ("oauth_provider", "VARCHAR"),
            ("risk_state", "VARCHAR DEFAULT 'active'")
        ]
        for col, col_type in user_cols:
            try:
                db.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                db.commit()
            except Exception:
                db.rollback()

        # Check BehaviorRecord columns
        behavior_cols = [
            ("typing_variance", "FLOAT DEFAULT 0.0"),
            ("mouse_acceleration", "FLOAT DEFAULT 0.0"),
            ("active_app_patterns", "VARCHAR"),
            ("session_duration", "FLOAT DEFAULT 0.0"),
            ("network_ssid", "VARCHAR"),
            ("ip_address", "VARCHAR"),
            ("public_ip", "VARCHAR"),
            ("download_bytes", "FLOAT DEFAULT 0.0"),
            ("upload_bytes", "FLOAT DEFAULT 0.0")
        ]
        for col, col_type in behavior_cols:
            try:
                db.execute(text(f"ALTER TABLE behavior_data ADD COLUMN {col} {col_type}"))
                db.commit()
            except Exception:
                db.rollback()

        # Check UserProfile columns
        profile_cols = [
            ("typing_variance", "FLOAT DEFAULT 0.0"),
            ("mouse_acceleration", "FLOAT DEFAULT 0.0"),
            ("active_app_patterns", "VARCHAR"),
            ("session_duration", "FLOAT DEFAULT 0.0"),
            ("city", "VARCHAR"),
            ("ip_address", "VARCHAR"),
            ("public_ip", "VARCHAR"),
            ("network_ssid", "VARCHAR"),
            ("download_bytes", "FLOAT DEFAULT 0.0"),
            ("upload_bytes", "FLOAT DEFAULT 0.0")
        ]
        for col, col_type in profile_cols:
            try:
                db.execute(text(f"ALTER TABLE user_profiles ADD COLUMN {col} {col_type}"))
                db.commit()
            except Exception:
                db.rollback()

        # Clean old fake OAuth users passwords
        try:
            db.execute(text("UPDATE users SET is_oauth = 1, oauth_provider = 'google', hashed_password = NULL WHERE hashed_password = 'google_auth'"))
            db.execute(text("UPDATE users SET is_oauth = 1, oauth_provider = 'github', hashed_password = NULL WHERE hashed_password = 'github_auth'"))
            db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()

@app.on_event("startup")
async def start_monitor():
    logger.info("🚀 System startup: Running migrations...")
    run_migrations()
    Base.metadata.create_all(bind=engine)


@app.post("/force-medium/{user_id}")
async def force_medium(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == str(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = {
        "city": user.city or "Unknown",
        "country": user.country or "Unknown"
    }

    await ActionEngine.execute(
        user_id=str(user_id),
        action=SecurityAction.SUSPEND,
        risk_score=50,
        alerts=["Manual Medium Risk Test"],
        db=db,
        blocked_users=blocked_users,
        user_states=user_states,
        admin_connections=admin_connections,
        record=record
    )

    return {
        "message": f"Medium risk triggered for user {user_id}"
    }

    
@app.post("/force-high/{user_id}")
async def force_high(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.warning("========== FORCE HIGH ENTERED ==========")
    logger.warning(f"Current User: {current_user.email}")
    logger.warning(f"Forcing high risk and freeze for user {user_id}")

    user_id = str(user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    record = {
        "city": user.city or "Unknown",
        "country": user.country or "Unknown"
    }

    await ActionEngine.execute(
        user_id=user_id,
        action=SecurityAction.FREEZE,
        risk_score=100,
        alerts=["Manual Force-High Simulated"],
        db=db,
        blocked_users=blocked_users,
        user_states=user_states,
        admin_connections=admin_connections,
        record=record
    )

    logger.warning(f"FREEZE COMPLETED FOR USER {user_id}")

    return {
        "message": f"High risk forced and freeze action triggered for user {user_id}"
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
    db: Session = Depends(get_db)
):
    user_id = str(user_id)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    revoke_user_tokens(user_id)
    logger.info(f"[ADMIN_ACTION] Admin {admin.id} deleted user {user_id}")

    return {"message": "User deleted"}

@app.post("/admin/block/{user_id}")
def block_user(
    user_id: str,
    admin: User = Depends(get_admin_user)
):
    user_id = str(user_id)
    blocked_users[user_id] = datetime.utcnow() + timedelta(minutes=30)
    revoke_user_tokens(user_id)
    logger.info(f"[ADMIN_ACTION] Admin {admin.id} blocked user {user_id}")
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
    user_id = str(user_id)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_frozen = False
    db.commit()
    logger.info(f"[ADMIN_ACTION] Admin {admin.id} unfroze user {user_id}")

    return {"message": "User unfrozen successfully"}

@app.post("/admin/unblock/{user_id}")
def unblock_user(user_id: str):
    user_id = str(user_id)
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
        "avg_key_interval": profile.avg_key_interval if profile else 0.0,
        "avg_mouse_speed": profile.avg_mouse_speed if profile else 0.0,
        "total_samples": profile.total_samples if profile else 0
    }