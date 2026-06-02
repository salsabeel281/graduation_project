import os
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.models import BehaviorRecord, UserProfile, RiskLog, User, Notification, SecurityLog
from backend.auth import revoke_user_tokens

logger = logging.getLogger("sentinelx")

class SecurityAction:
    MONITOR = "MONITOR"
    SUSPEND = "SUSPEND"
    FREEZE = "FREEZE"

class RiskEngine:
    @staticmethod
    def calculate_risk(record: dict, fingerprint: dict, user_id: str, db: Session) -> tuple[int, list[str]]:
        risk_score = 0
        alerts = []

        # 1. Keyboard interval deviation
        fp_key = fingerprint.get("avg_key_interval", 0.0)
        rec_key = float(record.get("avg_key_interval", 0.0))
        if fp_key > 0 and rec_key > 0:
            key_diff = abs(rec_key - fp_key) / fp_key
            if key_diff > 0.3:
                risk_score += 15
                alerts.append("Keyboard deviation")

        # 2. Typing variance deviation
        fp_var = fingerprint.get("typing_variance", 0.0)
        rec_var = float(record.get("typing_variance", 0.0))
        if fp_var > 0 and rec_var > 0:
            var_diff = abs(rec_var - fp_var) / (fp_var + 1e-5)
            if var_diff > 0.4:
                risk_score += 10
                alerts.append("Typing variance deviation")

        # 3. Mouse speed deviation
        fp_mouse = fingerprint.get("avg_mouse_speed", 0.0)
        rec_mouse = float(record.get("avg_mouse_speed", 0.0))
        if fp_mouse > 0 and rec_mouse > 0:
            mouse_diff = abs(rec_mouse - fp_mouse) / fp_mouse
            if mouse_diff > 0.3:
                risk_score += 15
                alerts.append("Mouse deviation")

        # 4. Mouse acceleration deviation
        fp_accel = fingerprint.get("mouse_acceleration", 0.0)
        rec_accel = float(record.get("mouse_acceleration", 0.0))
        if fp_accel != 0 and rec_accel != 0:
            accel_diff = abs(rec_accel - fp_accel) / (abs(fp_accel) + 1e-5)
            if accel_diff > 0.4:
                risk_score += 10
                alerts.append("Mouse acceleration deviation")

        # 5. Location change: Country
        fp_country = fingerprint.get("country", "Unknown")
        rec_country = record.get("country", "Unknown")
        if fp_country != "Unknown" and rec_country != "Unknown" and rec_country != fp_country:
            risk_score += 20
            alerts.append("Country change")

        # 6. Location change: City
        fp_city = fingerprint.get("city", "Unknown")
        rec_city = record.get("city", "Unknown")
        if fp_city != "Unknown" and rec_city != "Unknown" and rec_city != fp_city:
            risk_score += 10
            alerts.append("City change")

        # 7. Network: Local IP change
        fp_ip = fingerprint.get("ip_address", "Unknown")
        rec_ip = record.get("ip_address", "Unknown")
        if fp_ip != "Unknown" and rec_ip != "Unknown" and rec_ip != fp_ip:
            risk_score += 5
            alerts.append("Local IP change")

        # 8. Network: Public IP change
        fp_pub_ip = fingerprint.get("public_ip", "Unknown")
        rec_pub_ip = record.get("public_ip", "Unknown")
        if fp_pub_ip != "Unknown" and rec_pub_ip != "Unknown" and rec_pub_ip != fp_pub_ip:
            risk_score += 10
            alerts.append("Public IP change")

        # 9. Active application patterns
        app_patterns_str = fingerprint.get("active_app_patterns", "{}")
        try:
            app_patterns = json.loads(app_patterns_str)
        except Exception:
            app_patterns = {}
        rec_app = record.get("active_application", "Unknown")
        if app_patterns and rec_app != "Unknown" and rec_app not in app_patterns:
            risk_score += 10
            alerts.append("Unusual application pattern")

        # 10. Machine Learning Models Anomaly Detection (Votes)
        if_path = f"models/user_{user_id}_if.pkl"
        svm_path = f"models/user_{user_id}_svm.pkl"
        lof_path = f"models/user_{user_id}_lof.pkl"
        cols_path = f"models/user_{user_id}_columns.pkl"

        if os.path.exists(if_path) and os.path.exists(svm_path) and os.path.exists(lof_path) and os.path.exists(cols_path):
            try:
                if_model = joblib.load(if_path)
                svm_model = joblib.load(svm_path)
                lof_model = joblib.load(lof_path)
                feature_columns = joblib.load(cols_path)

                ml_record = {
                    "avg_key_interval": rec_key,
                    "typing_variance": rec_var,
                    "avg_mouse_speed": rec_mouse,
                    "mouse_acceleration": rec_accel,
                    "session_duration": float(record.get("session_duration", 0.0)),
                    "download_bytes": float(record.get("download_bytes", 0.0)),
                    "upload_bytes": float(record.get("upload_bytes", 0.0)),
                    "is_usual_app": 1.0 if rec_app in app_patterns else 0.0,
                    "is_usual_country": 1.0 if rec_country == fp_country else 0.0,
                    "is_usual_city": 1.0 if rec_city == fp_city else 0.0,
                    "is_usual_ip": 1.0 if (rec_ip == fp_ip or rec_pub_ip == fp_pub_ip) else 0.0
                }

                df = pd.DataFrame([ml_record])
                df = df.reindex(columns=feature_columns, fill_value=0.0).astype(float)

                votes = 0
                if if_model.predict(df)[0] == -1:
                    votes += 1
                if svm_model.predict(df)[0] == -1:
                    votes += 1
                if lof_model.predict(df)[0] == -1:
                    votes += 1

                ml_score = votes * 5
                risk_score += ml_score
                if votes > 0:
                    alerts.append(f"ML Anomaly ({votes} votes)")
                
                logger.info(f"[MODEL_PREDICTION] User: {user_id} | IF_anomaly={if_model.predict(df)[0] == -1} SVM_anomaly={svm_model.predict(df)[0] == -1} LOF_anomaly={lof_model.predict(df)[0] == -1} | Votes: {votes}")
            except Exception as e:
                logger.error(f"Error executing ML models for user {user_id}: {e}")
        else:
            logger.warning(f"ML models missing for user {user_id}. Skipping ML voting.")

        final_score = min(risk_score, 100)
        logger.info(f"[RISK_CALCULATION] User: {user_id} | Risk: {final_score} | Alerts: {alerts}")
        return final_score, alerts


class DecisionEngine:
    @staticmethod
    def decide_action(risk_score: int) -> str:
        if risk_score <= 39:
            return SecurityAction.MONITOR
        elif risk_score <= 69:
            return SecurityAction.SUSPEND
        else:
            return SecurityAction.FREEZE


class ActionEngine:
    @staticmethod
    async def execute(
        user_id: str,
        action: str,
        risk_score: int,
        alerts: list[str],
        db: Session,
        blocked_users: dict,
        user_states: dict,
        admin_connections: list,
        record: dict
    ):
        user_id = str(user_id)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found during action execution")
            return

        old_state = user.risk_state or "active"

        # 1. State changes and specific action triggers
        if action == SecurityAction.MONITOR:
            user_states[user_id] = "active"
            user.risk_state = "active"
            db.commit()
            log_action = "LOW_RISK_MONITORING"
            details = f"Risk={risk_score}, Alerts={alerts}"

            # notify admins via ws
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

        elif action == SecurityAction.SUSPEND:
            user_states[user_id] = "suspended"
            user.risk_state = "suspended"
            db.commit()
            
            # Create alert/notification in database
            notif = Notification(
                id=str(uuid4()),
                user_id=user_id,
                message=f"Suspicious activity detected: monitoring suspended/slowed down (alerts: {alerts})",
                status="unread"
            )
            db.add(notif)
            db.commit()

            # notify admins
            for conn in admin_connections:
                try:
                    await conn.send_json({
                        "user_id": user_id,
                        "risk": risk_score,
                        "status": "SUSPENDED",
                        "alerts": alerts
                    })
                except:
                    pass

            log_action = "SUSPENDED_RISK_TRIGGER"
            details = f"Monitoring slowed down due to risk={risk_score}, Alerts={alerts}"

        elif action == SecurityAction.FREEZE:
            user_states[user_id] = "frozen"
            user.risk_state = "frozen"
            user.is_frozen = True
            db.commit()

            # Revoke all JWT active tokens immediately
            revoke_user_tokens(user_id)
            logger.warning(f"[FREEZE_EVENT] User: {user_id} | Account frozen, all active tokens revoked")

            # Temporarily block user for login
            blocked_users[user_id] = datetime.utcnow() + timedelta(minutes=5)

            notif = Notification(
                id=str(uuid4()),
                user_id=user_id,
                message=f"Account frozen due to critical risk: {alerts}",
                status="unread"
            )
            db.add(notif)
            db.commit()

            # notify admins
            for conn in admin_connections:
                try:
                    await conn.send_json({
                        "user_id": user_id,
                        "risk": risk_score,
                        "status": "HIGH",
                        "alerts": alerts
                    })
                except:
                    pass

            log_action = "FREEZE_RISK_TRIGGER"
            details = f"Account frozen. Risk={risk_score}, Alerts={alerts}"

        # 2. State change logging
        new_state = user.risk_state or "active"
        if old_state != new_state:
            logger.info(f"[STATE_CHANGE] User: {user_id} | Transitioned: {old_state.upper()} -> {new_state.upper()}")

        # 3. Log security event & risk logs in DB
        log = SecurityLog(
            id=str(uuid4()),
            user_id=user_id,
            action=log_action,
            details=details
        )
        db.add(log)

        risk_entry = RiskLog(
            user_id=user_id,
            risk_score=risk_score,
            status="High" if action == SecurityAction.FREEZE else ("Medium" if action == SecurityAction.SUSPEND else "Low"),
            alerts=", ".join(alerts),
            city=record.get("city", "Unknown"),
            country=record.get("country", "Unknown")
        )
        db.add(risk_entry)
        db.commit()

