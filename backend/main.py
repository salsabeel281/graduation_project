import csv
import asyncio
from fastapi import FastAPI, Depends, Header, HTTPException, status

from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext


from .database import engine, SessionLocal, Base
from .models import BehaviorRecord, UserProfile, RiskLog, User
from .auth import create_access_token, verify_access_token

from fastapi.middleware.cors import CORSMiddleware

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# Password Hashing
# ==============================
# Use pbkdf2_sha256 instead of bcrypt to avoid the 72-byte limit
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ==============================
# FastAPI App
# ==============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


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
# Auth Dependency
# ==============================
from fastapi import Header, HTTPException, status

def get_current_user(token: str = Header(..., alias="Authorization"), db: Session = Depends(get_db)):
    if token.startswith("Bearer "):
        token = token[7:]  # remove "Bearer " prefix
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

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
    username: str
    email: EmailStr
    password: str

#login schema here
class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(User).all()
# ==============================
# CSV PATH
# ==============================
CSV_FILE_PATH = r"D:\GRAD\raw_training_data.csv"

last_processed_row = 0


# ==============================
# CSV MONITOR
# ==============================
async def monitor_csv():
    global last_processed_row

    while True:
        try:

            with open(CSV_FILE_PATH, "r", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))

            if len(reader) > last_processed_row:

                new_rows = reader[last_processed_row:]

                for row in new_rows:

                    try:
                        avg_key_interval = float(row.get("avg_key_interval", 0))
                        avg_mouse_speed = float(row.get("avg_mouse_speed", 0))
                        country = row.get("country", "Unknown")

                        user_id = "1"  # All data goes to user 1

                        db = SessionLocal()

                        # Save Behavior
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

                        # =========================
                        # Load Baseline
                        # =========================
                        profile = db.query(UserProfile).filter(
                            UserProfile.user_id == user_id
                        ).first()

                        if profile:

                            risk_score = 0
                            alerts = []

                            key_diff = 0
                            mouse_diff = 0

                            if profile.avg_key_interval != 0:
                                key_diff = abs(avg_key_interval - profile.avg_key_interval) / profile.avg_key_interval

                            if profile.avg_mouse_speed != 0:
                                mouse_diff = abs(avg_mouse_speed - profile.avg_mouse_speed) / profile.avg_mouse_speed

                            if key_diff > 0.3:
                                risk_score += 30
                                alerts.append("Keyboard deviation")

                            if mouse_diff > 0.3:
                                risk_score += 30
                                alerts.append("Mouse deviation")

                            if country != "Egypt":
                                risk_score += 40
                                alerts.append("Country change")

                            if risk_score < 30:
                                status = "Low"
                                action = "Monitoring"

                            elif risk_score < 60:
                                status = "Medium"
                                action = "Re-authentication required"

                            else:
                                status = "High"
                                action = "Session terminated"

                            risk_entry = RiskLog(
                                user_id=user_id,
                                risk_score=risk_score,
                                status=status,
                                alerts=", ".join(alerts)
                            )

                            db.add(risk_entry)
                            db.commit()

                            logger.info(f"Risk: {risk_score}, Status: {status}")

                        db.close()

                    except Exception as e:
                        print("Processing Error:", e)

                last_processed_row = len(reader)

        except Exception as e:
            print("CSV Monitor Error:", e)

        await asyncio.sleep(30)


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
@app.post("/calculate-baseline")
def calculate_baseline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    records = db.query(BehaviorRecord).filter(
        BehaviorRecord.user_id == user_id
    ).all()


    # Combined check:
    if len(records) < 2:
        return {"error": f"Need at least 2 records to calculate baseline. You have {len(records)} records."}

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
@app.get("/risk-logs")
def get_risk_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = str(current_user.id)

    logs = db.query(RiskLog).filter(
        RiskLog.user_id == user_id
    ).order_by(RiskLog.timestamp.desc()).all()

    return logs
# ==============================
# USER SUMMARY
# ==============================
@app.get("/user-summary")
def get_user_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    records = db.query(BehaviorRecord).filter(BehaviorRecord.user_id == user_id).all()
    logs = db.query(RiskLog).filter(RiskLog.user_id == user_id).order_by(RiskLog.timestamp.desc()).all()

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
def system_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_users = db.query(User).count()
    total_records = db.query(BehaviorRecord).count()
    total_risks = db.query(RiskLog).count()

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
def latest_threats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

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
def top_risk_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

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
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Registered user: {new_user.username}, id: {new_user.id}")
    except Exception as e:
        db.rollback()
        print(f"Register error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "message": "User registered",
        "user_id": new_user.id
    }
# ==============================
# LOGIN
# ==============================
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(db_user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "Bearer"
    }
# ==============================
# START MONITOR
# ==============================
@app.on_event("startup")
async def start_monitor():
    asyncio.create_task(monitor_csv())

