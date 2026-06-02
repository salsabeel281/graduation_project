from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from datetime import datetime


class BehaviorRecord(Base):
    __tablename__ = "behavior_data"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String)
    avg_key_interval = Column(Float)
    typing_variance = Column(Float, default=0.0)
    avg_mouse_speed = Column(Float)
    mouse_acceleration = Column(Float, default=0.0)
    active_app_patterns = Column(String)  # Stored active app
    session_duration = Column(Float, default=0.0)
    city = Column(String)
    country = Column(String)
    ip_address = Column(String)
    public_ip = Column(String)
    network_ssid = Column(String)
    download_bytes = Column(Float, default=0.0)
    upload_bytes = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True)
    avg_key_interval = Column(Float)
    typing_variance = Column(Float, default=0.0)
    avg_mouse_speed = Column(Float)
    mouse_acceleration = Column(Float, default=0.0)
    active_app_patterns = Column(String)  # JSON-serialized app pattern frequencies
    session_duration = Column(Float, default=0.0)
    city = Column(String)
    country = Column(String)
    ip_address = Column(String)
    public_ip = Column(String)
    network_ssid = Column(String)
    download_bytes = Column(Float, default=0.0)
    upload_bytes = Column(Float, default=0.0)
    total_samples = Column(Integer)

    min_key_interval = Column(Float, default=0.0)
    max_key_interval = Column(Float, default=0.0)
    key_presses_count = Column(Float, default=0.0)
    min_mouse_speed = Column(Float, default=0.0)
    max_mouse_speed = Column(Float, default=0.0)
    mouse_moves_count = Column(Float, default=0.0)
    active_application = Column(String, default="Unknown")
    window_title = Column(String, default="Unknown")



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
    last_login = Column(DateTime, nullable=True)
    session_start = Column(DateTime, nullable=True)

    city = Column(String)
    country = Column(String)
    gender = Column(String)
    department = Column(String)
    account_type = Column(String)
    is_frozen = Column(Boolean, default=False)
    first_login = Column(DateTime, nullable=True)
    risk_state = Column(String, default="active")

    # ML Training progress fields
    is_trained = Column(Boolean, default=False)
    training_samples = Column(Integer, default=0)
    last_training_date = Column(DateTime, nullable=True)
    model_version = Column(Integer, default=1)

    # OAuth fields
    is_oauth = Column(Boolean, default=False)
    oauth_provider = Column(String, nullable=True)


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

