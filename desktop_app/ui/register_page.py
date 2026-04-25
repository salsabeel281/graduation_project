# ui/register_page.py
"""
SentinelX - Registration Page with Neon Blue Animated Background
"""

import os
import json
import sys
import random
import math
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QApplication,
    QDesktopWidget, QMessageBox, QGraphicsDropShadowEffect,
<<<<<<< HEAD
    QFrame, QTextEdit
=======
    QFrame, QTextEdit, QComboBox
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen


class NeonBackground(QWidget):
    """Animated neon blue background with floating particles"""
    
<<<<<<< HEAD
    def _init_(self, parent=None):
        super()._init_(parent)
=======
    def __init__(self, parent=None):
        super().__init__(parent)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.particles = []
        self.glow_offset = 0
        self.init_particles()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
<<<<<<< HEAD
        self.timer.start(33)  # 30 FPS
    
    def init_particles(self):
        """Create floating particles with neon effect"""
=======
        self.timer.start(33)
    
    def init_particles(self):
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        for _ in range(60):
            self.particles.append({
                'x': random.randint(0, 100),
                'y': random.randint(0, 100),
                'size': random.randint(2, 6),
                'speed_x': random.uniform(-0.3, 0.3),
                'speed_y': random.uniform(-0.2, 0.5),
                'alpha': random.randint(30, 80),
                'pulse': random.uniform(0.5, 2)
            })
    
    def update_animation(self):
<<<<<<< HEAD
        """Update all animations"""
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.glow_offset = (self.glow_offset + 3) % 360
        
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
<<<<<<< HEAD
            # Wrap around
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
            if p['x'] > 100:
                p['x'] = 0
            elif p['x'] < 0:
                p['x'] = 100
            if p['y'] > 100:
                p['y'] = 0
            elif p['y'] < 0:
                p['y'] = 100
            
<<<<<<< HEAD
            # Pulse effect
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
            p['alpha'] = int(40 + 30 * math.sin(self.glow_offset * 0.02 * p['pulse']))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
<<<<<<< HEAD
        # Neon blue gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(5, 20, 45))      # Deep dark blue
        gradient.setColorAt(0.3, QColor(10, 35, 65))   # Neon dark blue
        gradient.setColorAt(0.6, QColor(15, 45, 85))   # Bright neon blue
        gradient.setColorAt(1, QColor(8, 25, 55))      # Dark blue
        painter.fillRect(self.rect(), gradient)
        
        # Draw floating light orbs
=======
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(5, 20, 45))
        gradient.setColorAt(0.3, QColor(10, 35, 65))
        gradient.setColorAt(0.6, QColor(15, 45, 85))
        gradient.setColorAt(1, QColor(8, 25, 55))
        painter.fillRect(self.rect(), gradient)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        for i in range(5):
            alpha = 20 + 15 * math.sin((self.glow_offset + i * 72) * 0.02)
            x = 150 + 200 * math.sin((self.glow_offset + i) * 0.05)
            y = 150 + 150 * math.cos((self.glow_offset + i * 2) * 0.05)
            painter.setBrush(QBrush(QColor(0, 150, 255, int(alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x), int(y), 80, 80)
        
<<<<<<< HEAD
        # Draw particles
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        for p in self.particles:
            color = QColor(0, 150, 255, p['alpha'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            x = int((p['x'] * self.width()) / 100)
            y = int((p['y'] * self.height()) / 100)
            painter.drawEllipse(x, y, p['size'], p['size'])
        
<<<<<<< HEAD
        # Draw neon glow lines
        
        
        # Draw corner glows
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        corner_gradient = QLinearGradient(0, 0, 200, 200)
        corner_gradient.setColorAt(0, QColor(0, 150, 255, 30))
        corner_gradient.setColorAt(1, QColor(0, 150, 255, 0))
        painter.fillRect(0, 0, 300, 300, corner_gradient)
        painter.fillRect(self.width() - 300, self.height() - 300, 300, 300, corner_gradient)


class LiveDemoWidget(QWidget):
    """Live security monitoring demo"""
    
<<<<<<< HEAD
    def _init_(self, parent=None):
        super()._init_(parent)
=======
    def __init__(self, parent=None):
        super().__init__(parent)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setMinimumHeight(550)
        self.setStyleSheet("""
            QWidget {
                background: rgba(0, 20, 40, 0.85);
                border-radius: 20px;
                border: 1px solid rgba(0, 150, 255, 0.4);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
<<<<<<< HEAD
        # Title
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        title = QLabel("🔵 LIVE SECURITY MONITORING")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        layout.addWidget(title)
        
<<<<<<< HEAD
        # Terminal display
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 10, 20, 0.8);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 12px;
                color: #00FFAA;
                font-family: 'Consolas', monospace;
<<<<<<< HEAD
                font-size: 13px;
=======
                font-size: 18px;
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
                padding: 15px;
            }
        """)
        self.terminal.setMinimumHeight(250)
        layout.addWidget(self.terminal)
        
<<<<<<< HEAD
        # Status bar
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 255, 0.08),
                    stop:1 rgba(0, 200, 255, 0.05));
                border-radius: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Segoe UI", 12))
        self.status_dot.setStyleSheet("color: #00FFAA;")
        
        self.status_text = QLabel("SYSTEM SECURE")
        self.status_text.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.status_text.setStyleSheet("color: #00FFAA;")
        
        self.threat_label = QLabel("THREAT LEVEL: LOW")
        self.threat_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.threat_label.setStyleSheet("color: #00FFAA;")
        
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        status_layout.addWidget(self.threat_label)
        
        layout.addWidget(status_bar)
        
<<<<<<< HEAD
        # Demo lines
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.demo_lines = [
            "> INITIALIZING SENTINELX SYSTEM...",
            "> LOADING USER PROFILES... [▓▓▓▓▓▓▓▓▓▓] 100%",
            "> MONITORING KEYSTROKE PATTERNS...",
            "> ANALYZING MOUSE MOVEMENT...",
            "> TRACKING APPLICATION USAGE...",
            "> DETECTING ANOMALIES...",
            "> THREAT LEVEL: LOW",
            "> SYSTEM STATUS: SECURE"
        ]
        
        self.line_index = 0
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.update_demo)
        self.demo_timer.start(700)
        
        self.threat_timer = QTimer()
        self.threat_timer.timeout.connect(self.update_threat_level)
        self.threat_timer.start(4000)
        
        self.terminal.setText("")
    
    def update_demo(self):
        if self.line_index < len(self.demo_lines):
            current_text = self.terminal.toPlainText()
            if current_text:
                current_text += "\n"
            current_text += self.demo_lines[self.line_index]
            self.terminal.setText(current_text)
            self.line_index += 1
            cursor = self.terminal.textCursor()
            cursor.movePosition(cursor.End)
            self.terminal.setTextCursor(cursor)
        else:
            text = self.terminal.toPlainText()
            lines = text.split('\n')
            if len(lines) > 9:
                lines = lines[-8:]
                self.terminal.setText('\n'.join(lines))
    
    def update_threat_level(self):
        threat_levels = ["LOW", "MEDIUM", "HIGH"]
        colors = ["#00FFAA", "#FFAA00", "#FF4444"]
        status_texts = ["SYSTEM SECURE", "SYSTEM ALERT", "THREAT DETECTED!"]
        
        current = random.choice(threat_levels)
        idx = threat_levels.index(current)
        
        self.threat_label.setText(f"THREAT LEVEL: {current}")
        self.threat_label.setStyleSheet(f"color: {colors[idx]};")
        self.status_text.setText(status_texts[idx])
        self.status_text.setStyleSheet(f"color: {colors[idx]};")
        self.status_dot.setStyleSheet(f"color: {colors[idx]};")


class ModernInput(QLineEdit):
    """Modern input field"""
    
<<<<<<< HEAD
    def _init_(self, placeholder="", parent=None):
        super()._init_(parent)
=======
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 150, 255, 0.05);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 14px;
                padding: 12px 18px;
                font-size: 14px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border: 1px solid #0096FF;
                background: rgba(0, 150, 255, 0.1);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """Modern button"""
    
<<<<<<< HEAD
    def _init_(self, text, parent=None):
        super()._init_(text, parent)
=======
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0096FF,
                    stop:1 #00C8FF);
                border: none;
                border-radius: 14px;
                color: white;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00C8FF,
                    stop:1 #0096FF);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 150, 255, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class RegisterPage(QMainWindow):
    """Main Registration Window"""
    
<<<<<<< HEAD
    def _init_(self, login_page=None):
        super()._init_()
=======
    def __init__(self, login_page=None):
        super().__init__()
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setWindowTitle("SentinelX - Create Account")
        self.login_page = login_page
        self.setMinimumSize(1300, 1000)
        
        self.users_db = self.load_users()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_pos = None
        
<<<<<<< HEAD
        # Neon background
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.central_widget = NeonBackground()
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()
        self.setup_controls()
    
    def load_users(self):
        if os.path.exists("sentinelx_users.json"):
            try:
                with open("sentinelx_users.json", 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        with open("sentinelx_users.json", 'w') as f:
            json.dump(self.users_db, f, indent=4)
    
    def setup_ui(self):
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(40)
        
<<<<<<< HEAD
        # Left side
        left_widget = self.create_left_section()
        main_layout.addWidget(left_widget, 4)
        
        # Right side
=======
        left_widget = self.create_left_section()
        main_layout.addWidget(left_widget, 4)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        right_widget = self.create_form_card()
        right_widget.setFixedWidth(550)
        main_layout.addWidget(right_widget, 5)
    
    def create_left_section(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)
        
<<<<<<< HEAD
        # Logo
        logo = QLabel("🔵 SENTINELX")
        logo.setFont(QFont("Segoe UI", 38, QFont.Bold))
        logo.setStyleSheet("color: #0096FF; letter-spacing: 4px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Welcome text
        welcome = QLabel("Welcome to SentinelX")
        welcome.setFont(QFont("Segoe UI", 26, QFont.Bold))
        welcome.setStyleSheet("color: white;")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        # Line
=======
        logo = QLabel("🫆 SENTINELX")
        logo.setFont(QFont("Segoe UI", 38, QFont.Bold))
        logo.setStyleSheet("color: #0096FF; letter-spacing: 4px;")
        logo.setAlignment(Qt.AlignLeft)
        layout.addWidget(logo)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096FF, stop:1 #00C8FF); border-radius: 1px;")
        layout.addWidget(line)
        
        layout.addSpacing(10)
        
<<<<<<< HEAD
        # Demo title
=======
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        demo_title = QLabel(" Detect Insider Threats , protect your Data")
        demo_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        demo_title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        demo_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_title)
        
<<<<<<< HEAD
        # Live Demo
        self.live_demo = LiveDemoWidget()
        layout.addWidget(self.live_demo)
        
        # Stats
=======
        self.live_demo = LiveDemoWidget()
        layout.addWidget(self.live_demo)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        stats_container = QFrame()
        stats_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 255, 0.06),
                    stop:1 rgba(0, 200, 255, 0.03));
                border-radius: 12px;
            }
        """)
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(15, 12, 15, 12)
        
        stat1 = QLabel("🎯 99.7% Accuracy")
        stat1.setFont(QFont("Segoe UI", 11))
        stat1.setStyleSheet("color: #00FFAA;")
        
        stat2 = QLabel("⚡ 0.2s Response")
        stat2.setFont(QFont("Segoe UI", 11))
        stat2.setStyleSheet("color: #0096FF;")
        
        stat3 = QLabel("🛡️ 24/7 Monitoring")
        stat3.setFont(QFont("Segoe UI", 11))
        stat3.setStyleSheet("color: #00C8FF;")
        
        stats_layout.addWidget(stat1)
        stats_layout.addWidget(stat2)
        stats_layout.addWidget(stat3)
        layout.addWidget(stats_container)
        
        layout.addStretch()
        
<<<<<<< HEAD
        # Badge
        badge = QFrame()
        badge.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 25px;
            }
        """)
       
=======
        welcome = QLabel("Secure Your Digital Identity")
        welcome.setFont(QFont("Segoe UI", 11, QFont.Bold))
        welcome.setStyleSheet("color: white;")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        
        return widget
    
    def create_form_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.85);
                border-radius: 24px;
                border: 1px solid rgba(0, 150, 255, 0.3);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
<<<<<<< HEAD
        layout.setContentsMargins(35, 40, 35, 40)
        layout.setSpacing(15)
        
        # Header
=======
        layout.setContentsMargins(35, 35, 35, 40)
        layout.setSpacing(10)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        title = QLabel("  Create Account  ")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel(" Build Your Own Digital Signature ")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        layout.addWidget(subtitle)
        
<<<<<<< HEAD
        layout.addSpacing(5)
        
        # Form fields
        self.name_input = ModernInput("Full name")
        layout.addWidget(self.name_input)
        
        self.email_input = ModernInput("Email address")
        layout.addWidget(self.email_input)
        
=======
        layout.addSpacing(30)
        
        # First Name and Last Name in same row
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(18)
        
        self.first_name_input = ModernInput("First Name")
        self.last_name_input = ModernInput("Last Name")
        
        name_layout.addWidget(self.first_name_input)
        name_layout.addWidget(self.last_name_input)
        layout.addWidget(name_container)
        
        # Email
        self.email_input = ModernInput("Email address")
        layout.addWidget(self.email_input)
        
        # Password
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.password_input = ModernInput("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
<<<<<<< HEAD
=======
        # Confirm Password
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.confirm_input = ModernInput("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)
        
<<<<<<< HEAD
=======
        # Location
        self.location_input = ModernInput("Location (City, Country)")
        layout.addWidget(self.location_input)
        
        # Gender
        gender_label = QLabel("Gender")
        gender_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        gender_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        layout.addWidget(gender_label)
        
        gender_container = QWidget()
        gender_layout = QHBoxLayout(gender_container)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        gender_layout.setSpacing(10)
        
        self.male_btn = QPushButton("Male")
        self.male_btn.setCursor(Qt.PointingHandCursor)
        self.male_btn.setMinimumHeight(42)
        self.male_btn.setStyleSheet("""
            QPushButton {
                background: #0096FF;
                border: none;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-weight: 600;
                font-size: 12px;
            }
        """)
        self.male_btn.clicked.connect(lambda: self.select_gender("male"))
        
        self.female_btn = QPushButton("Female")
        self.female_btn.setCursor(Qt.PointingHandCursor)
        self.female_btn.setMinimumHeight(42)
        self.female_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.4);
                border-radius: 10px;
                padding: 10px;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 150, 255, 0.15);
            }
        """)
        self.female_btn.clicked.connect(lambda: self.select_gender("female"))
        
        self.other_btn = QPushButton("Other")
        self.other_btn.setCursor(Qt.PointingHandCursor)
        self.other_btn.setMinimumHeight(42)
        self.other_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.4);
                border-radius: 10px;
                padding: 10px;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 150, 255, 0.15);
            }
        """)
        self.other_btn.clicked.connect(lambda: self.select_gender("other"))
        
        gender_layout.addWidget(self.male_btn)
        gender_layout.addWidget(self.female_btn)
        gender_layout.addWidget(self.other_btn)
        layout.addWidget(gender_container)
        
        self.selected_gender = "male"
        
        # Department
        dept_label = QLabel("Department")
        dept_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dept_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        layout.addWidget(dept_label)
        
        self.department_combo = QComboBox()
        self.department_combo.setMinimumHeight(50)
        self.department_combo.setStyleSheet("""
            QComboBox {
                background: rgba(0, 150, 255, 0.05);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 14px;
                padding: 12px 18px;
                font-size: 14px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(10, 20, 40, 0.95);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 10px;
                color: white;
                padding: 5px;
            }
        """)
        
        departments = [
            "Information Technology",
            "Human Resources",
            "Finance & Accounting",
            "Sales & Marketing",
            "Operations",
            "Research & Development",
            "Customer Support",
            "Legal",
            "Administration"
        ]
        self.department_combo.addItems(departments)
        layout.addWidget(self.department_combo)
        
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        # Role selector
        role_label = QLabel("Select account type")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        role_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        layout.addWidget(role_label)
        
        role_container = QWidget()
        role_layout = QHBoxLayout(role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(10)
        
        self.user_btn = QPushButton("Standard User")
        self.user_btn.setCursor(Qt.PointingHandCursor)
        self.user_btn.setMinimumHeight(42)
        self.user_btn.setStyleSheet("""
            QPushButton {
                background: #0096FF;
                border: none;
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-weight: 600;
                font-size: 12px;
            }
        """)
        self.user_btn.clicked.connect(lambda: self.select_role("user"))
        
        self.admin_btn = QPushButton("Administrator")
        self.admin_btn.setCursor(Qt.PointingHandCursor)
        self.admin_btn.setMinimumHeight(42)
        self.admin_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.4);
                border-radius: 10px;
                padding: 10px;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 150, 255, 0.15);
            }
        """)
        self.admin_btn.clicked.connect(lambda: self.select_role("admin"))
        
        role_layout.addWidget(self.user_btn)
        role_layout.addWidget(self.admin_btn)
        layout.addWidget(role_container)
        
        self.selected_role = "user"
        
        layout.addSpacing(5)
        
        # Register button
        self.register_btn = ModernButton("Create Account →")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background: rgba(0, 150, 255, 0.2); margin: 8px 0;")
        layout.addWidget(divider)
        
        # Social login
        social_label = QLabel("Or continue with")
        social_label.setFont(QFont("Segoe UI", 10))
        social_label.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        social_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(social_label)
        
        social_buttons = QWidget()
        social_layout = QHBoxLayout(social_buttons)
        social_layout.setContentsMargins(0, 0, 0, 0)
        social_layout.setSpacing(10)
        
        google_btn = QPushButton("Google")
        google_btn.setMinimumHeight(38)
        google_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.12);
            }
        """)
        
        github_btn = QPushButton("GitHub")
        github_btn.setMinimumHeight(38)
        github_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                padding: 8px;
                color: white;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.12);
            }
        """)
        
        social_layout.addWidget(google_btn)
        social_layout.addWidget(github_btn)
        layout.addWidget(social_buttons)
        
        # Sign in link
        signin_container = QWidget()
        signin_layout = QHBoxLayout(signin_container)
        signin_layout.setContentsMargins(0, 5, 0, 0)
        signin_layout.setAlignment(Qt.AlignCenter)
        
        signin_text = QLabel("Already have an account?")
        signin_text.setFont(QFont("Segoe UI", 10))
        signin_text.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        
        self.signin_link = QPushButton("Sign in")
        self.signin_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0096FF;
                font-weight: 600;
                font-size: 10px;
            }
            QPushButton:hover {
                color: #00C8FF;
            }
        """)
        self.signin_link.setCursor(Qt.PointingHandCursor)
        self.signin_link.clicked.connect(self.handle_login)
        
        signin_layout.addWidget(signin_text)
        signin_layout.addWidget(self.signin_link)
        layout.addWidget(signin_container)
        
        return card
    
<<<<<<< HEAD
=======
    def select_gender(self, gender):
        self.selected_gender = gender
        if gender == "male":
            self.male_btn.setStyleSheet("""
                QPushButton {
                    background: #0096FF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                }
            """)
            self.female_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
            self.other_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
        elif gender == "female":
            self.female_btn.setStyleSheet("""
                QPushButton {
                    background: #0096FF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                }
            """)
            self.male_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
            self.other_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
        else:
            self.other_btn.setStyleSheet("""
                QPushButton {
                    background: #0096FF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                }
            """)
            self.male_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
            self.female_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
    
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
    def select_role(self, role):
        self.selected_role = role
        if role == "user":
            self.user_btn.setStyleSheet("""
                QPushButton {
                    background: #0096FF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                }
            """)
            self.admin_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
        else:
            self.admin_btn.setStyleSheet("""
                QPushButton {
                    background: #0096FF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                }
            """)
            self.user_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(0, 150, 255, 0.4);
                    border-radius: 10px;
                    padding: 10px;
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                    font-size: 12px;
                }
            """)
    
    def handle_register(self):
<<<<<<< HEAD
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name")
=======
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        location = self.location_input.text().strip()
        gender = self.selected_gender
        department = self.department_combo.currentText()
        
        if not first_name or not last_name:
            QMessageBox.warning(self, "Error", "Please enter your first and last name")
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
            return
        
        if not email or '@' not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email")
            return
        
        if email in self.users_db:
            QMessageBox.warning(self, "Error", "Email already registered")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
<<<<<<< HEAD
        self.users_db[email] = {
            "name": name,
            "password": password,
            "role": self.selected_role
=======
        if not location:
            QMessageBox.warning(self, "Error", "Please enter your location")
            return
        
        full_name = f"{first_name} {last_name}"
        
        self.users_db[email] = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "password": password,
            "role": self.selected_role,
            "location": location,
            "gender": gender,
            "department": department,
            "signature_created": True
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        }
        self.save_users()
        
        role_text = "Administrator" if self.selected_role == "admin" else "Standard User"
        
        QMessageBox.information(
            self,
            "Welcome to SentinelX! 🎉",
<<<<<<< HEAD
            f"Account created successfully!\n\nName: {name}\nRole: {role_text}"
        )
        
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
=======
            f"Account created successfully!\n\n"
            f"Name: {full_name}\n"
            f"Email: {email}\n"
            f"Location: {location}\n"
            f"Department: {department}\n"
            f"Gender: {gender.capitalize()}\n"
            f"Role: {role_text}\n"
            f"Digital Signature: Generated"
        )
        
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.location_input.clear()
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        
        self.handle_login()
    
    def handle_login(self):
        if self.login_page:
            self.login_page.show()
            self.close()
        else:
            QMessageBox.information(self, "Info", "Please use the login page to sign in")
    
    def setup_controls(self):
        controls = QWidget(self)
        controls.setFixedSize(130, 38)
        controls.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(38, 38)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border-radius: 19px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); }
        """)
        self.min_btn.clicked.connect(self.showMinimized)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(38, 38)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border-radius: 19px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(255,255,255,0.2); }
        """)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(38, 38)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                border-radius: 19px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #E74C3C; }
        """)
        self.close_btn.clicked.connect(self.close)
        
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)
        
        controls.move(self.width() - 150, 18)
        self.controls = controls
    
    def toggle_maximize(self):
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.max_btn.setText("□")
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            screen = QDesktopWidget().screenGeometry()
            self.setGeometry(screen)
            self.max_btn.setText("❐")
            self.is_maximized = True
        self.update_controls_position()
    
    def update_controls_position(self):
        if hasattr(self, 'controls'):
            self.controls.move(self.width() - 150, 18)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_maximized:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.is_maximized and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_controls_position()


<<<<<<< HEAD
if __name__ == "_main_":
=======
if __name__ == "__main__":
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
    random.seed()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = RegisterPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - 1300) // 2
    y = (screen.height() - 850) // 2
    window.setGeometry(x, y, 1300, 850)
    
    window.show()
    sys.exit(app.exec_())