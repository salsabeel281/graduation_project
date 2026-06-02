# ui/training_dialog.py
import sys
import os
import time
import csv
import json
import requests
import joblib
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush

from config import TRAINING_DURATION, SAVE_INTERVAL, FINGERPRINT_FILE, RAW_DATA_FILE
from core.buffer import Buffer
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor


class TrainingThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, token, user_id):
        super().__init__()
        self.token = token
        self.user_id = str(user_id) if user_id else "user_1"
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            # 1. Collect Data
            buffer = Buffer()
            records = []
            
            start_time = time.time()
            self.status.emit("Initializing behavioral collectors...")
            time.sleep(1)

            # Ensure models directory exists
            os.makedirs("models", exist_ok=True)

            duration = TRAINING_DURATION
            # Support shorter test duration from config
            if duration <= 0:
                duration = 600

            while time.time() - start_time < duration:
                if not self._is_running:
                    self.finished.emit(False, "Training was cancelled by the user.")
                    return

                record = {}
                record.update(collect_input_event())
                record.update(collect_active_application())
                record.update(collect_network_info())
                record.update(collect_location_info())

                buffer.add(record)
                buffer.flush()
                records.append(record)

                elapsed = time.time() - start_time
                progress_val = int((elapsed / duration) * 100)
                progress_val = min(progress_val, 99) # Save 100% for model training and upload completion

                self.progress.emit(progress_val)
                self.status.emit(f"Collecting behavior data: {int(elapsed)}s / {duration}s ({len(records)} samples)")

                time.sleep(SAVE_INTERVAL)

            if not records:
                self.finished.emit(False, "No behavioral data was collected. Please verify your input devices.")
                return

            # 2. Create Fingerprint
            self.progress.emit(95)
            self.status.emit("Calculating behavioral signature (fingerprint)...")
            time.sleep(1)

            fingerprint = {}
            for key in records[0].keys():
                values = [r[key] for r in records if isinstance(r[key], (int, float))]
                if values:
                    fingerprint[key + "_mean"] = float(np.mean(values))
                    fingerprint[key + "_std"] = float(np.std(values))
                else:
                    fingerprint[key] = records[-1][key]

            # Save local CSV fingerprint
            with open(FINGERPRINT_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fingerprint.keys())
                writer.writeheader()
                writer.writerow(fingerprint)

            # 3. Train ML Models
            self.status.emit("Fitting Machine Learning anomaly models...")
            time.sleep(1)

            df = pd.DataFrame(records)
            df_numeric = df.select_dtypes(include=[np.number]).fillna(0)
            feature_columns = df_numeric.columns.tolist()

            # Save columns
            joblib.dump(feature_columns, f"models/user_{self.user_id}_columns.pkl")

            if not df_numeric.empty:
                # Fit Isolation Forest
                if_model = IsolationForest(contamination=0.1, random_state=42)
                if_model.fit(df_numeric)
                joblib.dump(if_model, f"models/user_{self.user_id}_if.pkl")

                # Fit One-Class SVM
                svm_model = OneClassSVM(nu=0.1, kernel="rbf")
                svm_model.fit(df_numeric)
                joblib.dump(svm_model, f"models/user_{self.user_id}_svm.pkl")

                # Fit LOF
                lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True)
                lof_model.fit(df_numeric)
                joblib.dump(lof_model, f"models/user_{self.user_id}_lof.pkl")

            # 4. Upload Fingerprint to Backend Database
            self.status.emit("Uploading fingerprint to database...")
            time.sleep(1)

            url = "http://127.0.0.1:8000/upload-fingerprint"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.post(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                self.progress.emit(100)
                self.status.emit("Fingerprint successfully uploaded and activated!")
                time.sleep(1)
                self.finished.emit(True, "Your behavioral signature has been established successfully!")
            else:
                self.finished.emit(False, f"Upload failed: {response.text}")

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class TrainingDialog(QDialog):
    def __init__(self, token, user_id=None, parent=None):
        super().__init__(parent)
        self.token = token
        self.user_id = user_id
        
        self.setWindowTitle("SentinelX - Profile Training")
        self.setFixedSize(550, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

    def setup_ui(self):
        # Master Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Background Frame (Glassmorphism card styling consistent with Project)
        self.bg_frame = QFrame()
        self.bg_frame.setStyleSheet("""
            QFrame {
                background: #0B1643;
                border: 2px solid #0066ff;
                border-radius: 28px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 102, 255, 120))
        shadow.setOffset(0, 5)
        self.bg_frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(20)

        # Header Title
        self.title_lbl = QLabel("BEHAVIORAL PROFILE TRAINING")
        self.title_lbl.setFont(QFont("Orbitron", 16, QFont.Bold))
        self.title_lbl.setStyleSheet("color: white; border: none; background: transparent; letter-spacing: 2px;")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.title_lbl)

        # Separator Line
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066ff, stop:1 #00ccff); border: none;")
        frame_layout.addWidget(line)

        # Descriptive text
        self.desc_lbl = QLabel(
            "SentinelX needs to establish your secure behavioral signature by tracking your normal keyboard speed, rhythm, and mouse movement speed.\n\nPlease interact with your computer normally while training runs."
        )
        self.desc_lbl.setFont(QFont("Exo 2", 10))
        self.desc_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.75); border: none; background: transparent;")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.desc_lbl)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(16, 20, 40, 0.9);
                border: 1px solid rgba(0, 102, 255, 0.35);
                border-radius: 10px;
                color: white;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066ff, stop:1 #00ccff);
                border-radius: 9px;
            }
        """)
        frame_layout.addWidget(self.progress_bar)

        # Status text label
        self.status_lbl = QLabel("Status: Ready to start")
        self.status_lbl.setFont(QFont("Exo 2", 9, QFont.Bold))
        self.status_lbl.setStyleSheet("color: #00ccff; border: none; background: transparent;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.status_lbl)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        # Allow/Start Button
        self.start_btn = QPushButton("ALLOW TRAINING")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedHeight(45)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066ff, stop:1 #00ccff);
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Orbitron', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ccff, stop:1 #0066ff);
            }
            QPushButton:disabled {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.start_btn.clicked.connect(self.start_training)
        btn_layout.addWidget(self.start_btn)

        # Cancel Button
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 82, 82, 0.15);
                border: 1px solid #FF5252;
                border-radius: 12px;
                color: #FF5252;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Orbitron', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 82, 82, 0.3);
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_training)
        btn_layout.addWidget(self.cancel_btn)

        frame_layout.addLayout(btn_layout)
        layout.addWidget(self.bg_frame)

        self.thread = None

    def start_training(self):
        self.start_btn.setEnabled(False)
        self.cancel_btn.setText("STOP")
        
        self.thread = TrainingThread(self.token, self.user_id)
        self.thread.progress.connect(self.on_progress)
        self.thread.status.connect(self.on_status)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_progress(self, val):
        self.progress_bar.setValue(val)

    def on_status(self, msg):
        self.status_lbl.setText(f"Status: {msg}")

    def on_finished(self, success, message):
        if success:
            self.status_lbl.setText("Status: Completed!")
            self.progress_bar.setValue(100)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "SentinelX - Success", message)
            self.accept()
        else:
            self.status_lbl.setText("Status: Failed!")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "SentinelX - Training Error", message)
            self.start_btn.setEnabled(True)
            self.cancel_btn.setText("CANCEL")

    def cancel_training(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        self.reject()
