import os
import sys
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment variables before imports
os.environ["SECRET_KEY"] = "testsecretkey999"
os.environ["MAIL_USERNAME"] = "test@gmail.com"
os.environ["MAIL_PASSWORD"] = "password"
os.environ["MAIL_FROM"] = "test@gmail.com"
os.environ["MAIL_PORT"] = "587"
os.environ["MAIL_SERVER"] = "smtp.gmail.com"
os.environ["MAIL_STARTTLS"] = "True"
os.environ["MAIL_SSL_TLS"] = "False"
os.environ["CSV_FILE_PATH"] = "raw_training_data.csv"

# Import system elements
from backend.database import Base
from backend.models import User, BehaviorRecord, UserProfile, RiskLog
from backend.main import app, get_db, train_user_model, run_migrations
from core.engines import RiskEngine, DecisionEngine, ActionEngine, SecurityAction

class TestSentinelXRefactor(unittest.TestCase):
    db_path = "test_sentinel.db"

    @classmethod
    def setUpClass(cls):
        # Clean existing test db file if present
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except:
                pass
                
        # Configure SQLite database for testing
        cls.engine = create_engine(f"sqlite:///{cls.db_path}", connect_args={"check_same_thread": False})
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        
        # Override FastAPI dependency
        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Dispose engine and clean up database file
        cls.engine.dispose()
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except:
                pass

    def setUp(self):
        # Clear database tables before each test
        db = self.SessionLocal()
        db.query(User).delete()
        db.query(BehaviorRecord).delete()
        db.query(UserProfile).delete()
        db.query(RiskLog).delete()
        db.commit()
        db.close()

    def test_database_migrations_and_columns(self):
        # Test if run_migrations does not crash and applies without error
        try:
            run_migrations()
            migration_ok = True
        except Exception as e:
            migration_ok = False
            print("Migration failed:", e)
        self.assertTrue(migration_ok)

    def test_register_and_oauth_safeguards(self):
        db = self.SessionLocal()
        # Create standard user
        resp = self.client.post("/register", json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@sentinelx.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "gender": "female",
            "department": "Information Technology",
            "account_type": "Standard User"
        })
        self.assertEqual(resp.status_code, 200)
        
        # Try registering OAuth user
        oauth_user = User(
            email="oauth@sentinelx.com",
            first_name="Bob",
            last_name="Oauth",
            hashed_password=None,
            is_oauth=True,
            oauth_provider="google",
            account_type="Standard User"
        )
        db.add(oauth_user)
        db.commit()
        
        # Attempting standard login for OAuth user should fail
        login_resp = self.client.post("/login", json={
            "email": "oauth@sentinelx.com",
            "password": "anypassword"
        })
        self.assertEqual(login_resp.status_code, 400)
        self.assertIn("OAuth", login_resp.json()["detail"])
        db.close()

    def test_risk_and_decision_engines(self):
        # 1. Heuristics & ML Decision mapping
        # Test low risk (<60 is MONITOR)
        action_low1 = DecisionEngine.decide_action(20)
        self.assertEqual(action_low1, SecurityAction.MONITOR)

        action_low2 = DecisionEngine.decide_action(55)
        self.assertEqual(action_low2, SecurityAction.MONITOR)

        # Test medium/suspend risk (60-79 is SUSPEND)
        action_med1 = DecisionEngine.decide_action(60)
        self.assertEqual(action_med1, SecurityAction.SUSPEND)

        action_med2 = DecisionEngine.decide_action(79)
        self.assertEqual(action_med2, SecurityAction.SUSPEND)

        # Test freeze risk (>=80 is FREEZE)
        action_freeze1 = DecisionEngine.decide_action(80)
        self.assertEqual(action_freeze1, SecurityAction.FREEZE)

        action_freeze2 = DecisionEngine.decide_action(95)
        self.assertEqual(action_freeze2, SecurityAction.FREEZE)

    def test_onboarding_and_training_trigger(self):
        db = self.SessionLocal()
        
        # Create a test user
        user = User(
            first_name="Jane",
            last_name="Doe",
            email="jane@sentinelx.com",
            hashed_password="hashed_placeholder",
            is_trained=False,
            training_samples=0,
            account_type="Standard User"
        )
        db.add(user)
        db.commit()
        user_id = str(user.id)
        
        # Insert 100 behavior records for training
        for i in range(100):
            record = BehaviorRecord(
                id=f"rec_{i}",
                user_id=user_id,
                session_id="test_session",
                avg_key_interval=0.2,
                typing_variance=0.01,
                avg_mouse_speed=150.0,
                mouse_acceleration=2.0,
                active_app_patterns="PyCharm",
                session_duration=float(i * 5),
                city="Cairo",
                country="Egypt",
                ip_address="192.168.1.50",
                public_ip="197.34.12.90",
                download_bytes=1000.0,
                upload_bytes=500.0
            )
            db.add(record)
        db.commit()

        # Run model training
        success = train_user_model(user_id, db)
        self.assertTrue(success)
        
        # Re-check user training state
        db.refresh(user)
        self.assertTrue(user.is_trained)
        self.assertEqual(user.training_samples, 100)
        self.assertIsNotNone(user.last_training_date)
        
        # Verify ML models generated specifically for Jane
        self.assertTrue(os.path.exists(f"models/user_{user_id}_if.pkl"))
        self.assertTrue(os.path.exists(f"models/user_{user_id}_svm.pkl"))
        self.assertTrue(os.path.exists(f"models/user_{user_id}_lof.pkl"))
        self.assertTrue(os.path.exists(f"models/user_{user_id}_columns.pkl"))
        
        # Clean up ML models files
        for suffix in ["if", "svm", "lof", "columns"]:
            file_path = f"models/user_{user_id}_{suffix}.pkl"
            if os.path.exists(file_path):
                os.remove(file_path)
                
        db.close()

if __name__ == "__main__":
    unittest.main()
