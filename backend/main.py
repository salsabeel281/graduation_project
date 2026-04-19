import csv
import asyncio
from fastapi import FastAPI, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from config import FINGERPRINT_FILE
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

from .database import engine, SessionLocal, Base
from .models import BehaviorRecord, UserProfile, RiskLog, User
from fastapi import Header, HTTPException, status
from datetime import timedelta

security = HTTPBearer()
blocked_users = {}
blocked_tokens = set()


def load_fingerprint():
    try:
        with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
            row = next(csv.DictReader(f))
            fp = {}

            for k, v in row.items():
                try:
                    fp[k] = float(v)
                except:
                    fp[k] = v

            return fp
    except:
        return None

# ==============================
# Database Dependency
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

medium_sessions = {}
# ==============================
# Fake Token System
# ==============================
fake_tokens = {}


def create_token(user_id):
    token = str(uuid4())
    fake_tokens[token] = user_id
    return token

blocked_tokens = set()

def block_token(token):
    blocked_tokens.add(token)

# ==============================
# Auth
# ==============================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    print("Token:", token)

    # ❌ لو التوكن مش موجود
    if token not in fake_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 🚨 أهم سطر في السيستم كله
    if token in blocked_tokens:
        raise HTTPException(status_code=403, detail="Session terminated due to suspicious activity")

    user_id = fake_tokens[token]

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
# ==============================
# Password Hashing
# ==============================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ==============================
# FastAPI App
# ==============================
app = FastAPI()

Base.metadata.create_all(bind=engine)

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
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

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

    # ناخد القيم
    avg_key = float(data.get("avg_key_interval", 0))
    avg_mouse = float(data.get("avg_mouse_speed", 0))
    country = data.get("country", "Unknown")

    user = db.query(User).first()
    user_id = str(user.id)
    # نشوف هل فيه profile موجود
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


# ==============================
# CSV MONITOR
# ==============================
async def monitor_csv():
    print("🔥 MONITOR STARTED")

    fingerprint = load_fingerprint()

    if not fingerprint:
        print("❌ No fingerprint found")
        return

    while True:
        print("👀 LOOP RUNNING")

        db = SessionLocal()

        try:
            # =========================
            # ✅ Collect LIVE data بدل CSV
            # =========================
            record = {}
            record.update(collect_input_event())
            record.update(collect_active_application())
            record.update(collect_network_info())
            record.update(collect_location_info())

            avg_key_interval = float(record.get("avg_key_interval", 0))
            avg_mouse_speed = float(record.get("avg_mouse_speed", 0))
            country = record.get("country", "Unknown")

            print("➡️ Processing LIVE:", avg_key_interval, avg_mouse_speed, country)

            user = db.query(User).first()
            user_id = str(user.id)  # أو تبع session حقيقية
            # 🚨 لو اليوزر blocked → سيبيه
            if user_id in blocked_users:
                if datetime.utcnow() < blocked_users[str(user_id)]:
                    print("⛔ USER BLOCKED → skipping monitoring")
                    await asyncio.sleep(5)
                    continue
                else:
                      del blocked_users[str(user_id)]


            # =========================
            # Save Behavior
            # =========================
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
            # ✅ Compare with Fingerprint
            # =========================
            risk_score = 0
            alerts = []
            attack_location = country

            fp_key = fingerprint.get("avg_key_interval", 0)
            fp_mouse = fingerprint.get("avg_mouse_speed", 0)
            fp_country = fingerprint.get("country", "Unknown")

            key_diff = 0
            mouse_diff = 0

            if fp_key != 0:
                key_diff = abs(avg_key_interval - fp_key) / fp_key

            if fp_mouse != 0:
                mouse_diff = abs(avg_mouse_speed - fp_mouse) / fp_mouse

            if key_diff > 0.3:
                risk_score += 30
                alerts.append("Keyboard deviation")

            if mouse_diff > 0.3:
                risk_score += 30
                alerts.append("Mouse deviation")

            if fp_country != "Unknown" and country != fp_country:
                risk_score += 40
                alerts.append("Country change")

            # =========================
            # Risk Decision
            # =========================
            if risk_score < 30:
                status = "Low"
                action = "Warning"

                print("🟢 LOW RISK")

                message = f"Low risk detected (score={risk_score})"


            elif risk_score < 60:
                status = "Medium"
                action = "Verification Required"

                print("🟡 MEDIUM RISK")

                medium_sessions[user_id] = {
                    "risk_score": risk_score,
                    "status": "pending",
                    "country": country,
                    "timestamp": datetime.utcnow()
                }

            else:
                status = "High"
                action = "Blocked"

                print("🚨 HIGH RISK")
                print(f"🚨 ATTACK DETECTED FROM: {country}")

                # ⛔ 2. Block user لمدة 5 دقايق
                blocked_users[str(user_id)] = datetime.utcnow() + timedelta(minutes=5)

                # ❌ Block user
                for t, uid in fake_tokens.items():
                    if uid == user_id:
                        blocked_tokens.add(t)


            # =========================
            # Save Risk Log
            # =========================
            risk_entry = RiskLog(
                user_id=user_id,
                risk_score=risk_score,
                status=status,
                alerts=", ".join(alerts),
                location=attack_location
            )

            db.add(risk_entry)
            db.commit()

            print("💾 Risk saved:", risk_score, status, action)

        except Exception as e:
            print("Processing Error:", e)

        finally:
            db.close()

        await asyncio.sleep(5)  # ⏱️ كل 5 ثواني بدل 30

# ==============================
# IMPORT + DETECT MANUAL
# ==============================
@app.post("/import-latest-record")
def import_latest_record(
    current_user: str = Depends(get_current_user),
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

    existing_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email)
    ).first()

    if existing_user:
        return {"error": "User exists"}

    hashed_pw = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered",
        "user_id": new_user.id
    }

# ==============================
# Login
# ==============================
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

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
            # ⏱️ فك البلوك بعد الوقت
            del blocked_users[user_id]

    # ✅ لو مش blocked → يكمل عادي
    token = create_token(db_user.id)

    return {
        "access_token": token,
        "token_type": "Bearer"
    }
# ==============================
# START MONITOR
# ==============================
@app.on_event("startup")
async def start_monitor():
    print("🚀 Starting background monitor...")
    asyncio.create_task(monitor_csv())

@app.get("/medium-alert/{user_id}")
def medium_alert(user_id: str):
    if user_id not in medium_sessions:
        return {"status": "safe"}

    session = medium_sessions[user_id]

    return {
        "status": "MEDIUM_RISK",
        "message": "We detected unusual behavior. Please verify it's you.",
        "data": session
    }

@app.post("/verify-user/{user_id}")
def verify_user(user_id: str):
    if user_id in medium_sessions:
        del medium_sessions[user_id]
        return {
            "status": "verified",
            "message": "User confirmed, session restored"
        }

    return {"status": "no_verification_needed"}


@app.post("/force-high/{user_id}")
def force_high(user_id: str):

    print("🚨 FORCE HIGH TRIGGERED")

    # 🔒 block tokens القديمة
    for t, uid in fake_tokens.items():
        if str(uid) == str(user_id):
            blocked_tokens.add(t)

    # ⛔ block user نفسه 5 دقايق
    blocked_users[str(user_id)] = datetime.utcnow() + timedelta(minutes=5)

    return {
        "message": f"High risk simulated for user {user_id}"
    }

