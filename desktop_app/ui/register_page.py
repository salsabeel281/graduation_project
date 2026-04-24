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
    QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen


class NeonBackground(QWidget):
    """Animated neon blue background with floating particles"""
    
    def _init_(self, parent=None):
        super()._init_(parent)
        self.particles = []
        self.glow_offset = 0
        self.init_particles()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # 30 FPS
    
    def init_particles(self):
        """Create floating particles with neon effect"""
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
        """Update all animations"""
        self.glow_offset = (self.glow_offset + 3) % 360
        
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
            # Wrap around
            if p['x'] > 100:
                p['x'] = 0
            elif p['x'] < 0:
                p['x'] = 100
            if p['y'] > 100:
                p['y'] = 0
            elif p['y'] < 0:
                p['y'] = 100
            
            # Pulse effect
            p['alpha'] = int(40 + 30 * math.sin(self.glow_offset * 0.02 * p['pulse']))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Neon blue gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(5, 20, 45))      # Deep dark blue
        gradient.setColorAt(0.3, QColor(10, 35, 65))   # Neon dark blue
        gradient.setColorAt(0.6, QColor(15, 45, 85))   # Bright neon blue
        gradient.setColorAt(1, QColor(8, 25, 55))      # Dark blue
        painter.fillRect(self.rect(), gradient)
        
        # Draw floating light orbs
        for i in range(5):
            alpha = 20 + 15 * math.sin((self.glow_offset + i * 72) * 0.02)
            x = 150 + 200 * math.sin((self.glow_offset + i) * 0.05)
            y = 150 + 150 * math.cos((self.glow_offset + i * 2) * 0.05)
            painter.setBrush(QBrush(QColor(0, 150, 255, int(alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x), int(y), 80, 80)
        
        # Draw particles
        for p in self.particles:
            color = QColor(0, 150, 255, p['alpha'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            x = int((p['x'] * self.width()) / 100)
            y = int((p['y'] * self.height()) / 100)
            painter.drawEllipse(x, y, p['size'], p['size'])
        
        # Draw neon glow lines
        
        
        # Draw corner glows
        corner_gradient = QLinearGradient(0, 0, 200, 200)
        corner_gradient.setColorAt(0, QColor(0, 150, 255, 30))
        corner_gradient.setColorAt(1, QColor(0, 150, 255, 0))
        painter.fillRect(0, 0, 300, 300, corner_gradient)
        painter.fillRect(self.width() - 300, self.height() - 300, 300, 300, corner_gradient)


class LiveDemoWidget(QWidget):
    """Live security monitoring demo"""
    
    def _init_(self, parent=None):
        super()._init_(parent)
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
        
        # Title
        title = QLabel("🔵 LIVE SECURITY MONITORING")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        layout.addWidget(title)
        
        # Terminal display
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 10, 20, 0.8);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 12px;
                color: #00FFAA;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                padding: 15px;
            }
        """)
        self.terminal.setMinimumHeight(250)
        layout.addWidget(self.terminal)
        
        # Status bar
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
        
        # Demo lines
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
    
    def _init_(self, placeholder="", parent=None):
        super()._init_(parent)
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
    
    def _init_(self, text, parent=None):
        super()._init_(text, parent)
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
    
    def _init_(self, login_page=None):
        super()._init_()
        self.setWindowTitle("SentinelX - Create Account")
        self.login_page = login_page
        self.setMinimumSize(1300, 1000)
        
        self.users_db = self.load_users()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_pos = None
        
        # Neon background
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
        
        # Left side
        left_widget = self.create_left_section()
        main_layout.addWidget(left_widget, 4)
        
        # Right side
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
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096FF, stop:1 #00C8FF); border-radius: 1px;")
        layout.addWidget(line)
        
        layout.addSpacing(10)
        
        # Demo title
        demo_title = QLabel(" Detect Insider Threats , protect your Data")
        demo_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        demo_title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        demo_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_title)
        
        # Live Demo
        self.live_demo = LiveDemoWidget()
        layout.addWidget(self.live_demo)
        
        # Stats
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
        
        # Badge
        badge = QFrame()
        badge.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 25px;
            }
        """)
       
        
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
        layout.setContentsMargins(35, 40, 35, 40)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("  Create Account  ")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel(" Build Your Own Digital Signature ")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        layout.addWidget(subtitle)
        
        layout.addSpacing(5)
        
        # Form fields
        self.name_input = ModernInput("Full name")
        layout.addWidget(self.name_input)
        
        self.email_input = ModernInput("Email address")
        layout.addWidget(self.email_input)
        
        self.password_input = ModernInput("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.confirm_input = ModernInput("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)
        
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
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name")
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
        
        self.users_db[email] = {
            "name": name,
            "password": password,
            "role": self.selected_role
        }
        self.save_users()
        
        role_text = "Administrator" if self.selected_role == "admin" else "Standard User"
        
        QMessageBox.information(
            self,
            "Welcome to SentinelX! 🎉",
            f"Account created successfully!\n\nName: {name}\nRole: {role_text}"
        )
        
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        
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


if __name__ == "_main_":
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