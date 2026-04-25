from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from datetime import datetime


class BehaviorRecord(Base):
    __tablename__ = "behavior_data"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String)
    avg_key_interval = Column(Float)
    avg_mouse_speed = Column(Float)
    city = Column(String)
    country = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True)
    avg_key_interval = Column(Float)
    avg_mouse_speed = Column(Float)
    total_samples = Column(Integer)


class RiskLog(Base):
    __tablename__ = "risk_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True)
    risk_score = Column(Integer)
    status = Column(String)
    alerts = Column(String)
    city = Column(String)
    country = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    city = Column(String)
    country = Column(String)
    gender = Column(String)
    department = Column(String)
    account_type = Column(String)
    is_frozen = Column(Boolean, default=False)
    

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    message = Column(String)
    status = Column(String)  # unread / read
    created_at = Column(DateTime, default=datetime.utcnow)

class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
