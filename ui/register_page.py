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
    QFrame, QTextEdit, QComboBox
)
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QScrollArea

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen
import requests

class NeonBackground(QWidget):
    """Animated neon blue background with floating particles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.glow_offset = 0
        self.init_particles()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)
    
    def init_particles(self):
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
        self.glow_offset = (self.glow_offset + 3) % 360
        
        for p in self.particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
            if p['x'] > 100:
                p['x'] = 0
            elif p['x'] < 0:
                p['x'] = 100
            if p['y'] > 100:
                p['y'] = 0
            elif p['y'] < 0:
                p['y'] = 100
            
            p['alpha'] = int(40 + 30 * math.sin(self.glow_offset * 0.02 * p['pulse']))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(5, 20, 45))
        gradient.setColorAt(0.3, QColor(10, 35, 65))
        gradient.setColorAt(0.6, QColor(15, 45, 85))
        gradient.setColorAt(1, QColor(8, 25, 55))
        painter.fillRect(self.rect(), gradient)
        
        for i in range(5):
            alpha = 20 + 15 * math.sin((self.glow_offset + i * 72) * 0.02)
            x = 150 + 200 * math.sin((self.glow_offset + i) * 0.05)
            y = 150 + 150 * math.cos((self.glow_offset + i * 2) * 0.05)
            painter.setBrush(QBrush(QColor(0, 150, 255, int(alpha))))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x), int(y), 80, 80)
        
        for p in self.particles:
            color = QColor(0, 150, 255, p['alpha'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            x = int((p['x'] * self.width()) / 100)
            y = int((p['y'] * self.height()) / 100)
            painter.drawEllipse(x, y, p['size'], p['size'])
        
        corner_gradient = QLinearGradient(0, 0, 200, 200)
        corner_gradient.setColorAt(0, QColor(0, 150, 255, 30))
        corner_gradient.setColorAt(1, QColor(0, 150, 255, 0))
        painter.fillRect(0, 0, 300, 300, corner_gradient)
        painter.fillRect(self.width() - 300, self.height() - 300, 300, 300, corner_gradient)


class LiveDemoWidget(QWidget):
    """Live security monitoring demo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        
        title = QLabel("🔵 LIVE SECURITY MONITORING")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        layout.addWidget(title)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 10, 20, 0.8);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 12px;
                color: #00FFAA;
                font-family: 'Consolas', monospace;
                font-size: 18px;
                padding: 15px;
            }
        """)
        self.terminal.setMinimumHeight(250)
        layout.addWidget(self.terminal)
        
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
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setGraphicsEffect(None)

        self.setPlaceholderText(placeholder)

        self.setFixedHeight(50)

        self.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 150, 255, 0.05);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 14px;

                padding-left: 18px;
                padding-right: 18px;

                font-size: 14px;
                color: white;
                font-family: 'Segoe UI';
            }

            QLineEdit:focus {
                border: 1px solid #0096FF;
                background: rgba(0, 150, 255, 0.1);
            }
        """)
class ModernButton(QPushButton):
    """Modern button"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
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
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078D4,
                    stop:1 #00B4E6);
            }
            QPushButton:focus {
                border: 2px solid #00FFFF;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 150, 255, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class RegisterPage(QMainWindow):
    """Main Registration Window"""
    
    def __init__(self, login_page=None):
        super().__init__()
        self.setWindowTitle("SentinelX - Create Account")
        self.login_page = login_page
        self.setMinimumSize(1100, 720)
        self.users_db = self.load_users()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_pos = None
        
        self.central_widget = NeonBackground()
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()
        self.setup_controls()

        # Stylesheet for custom properties of option buttons (Gender & Role)
        self.setStyleSheet("""
            QPushButton[optionBtn="true"] {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(0, 150, 255, 0.4);
                border-radius: 10px;
                padding: 10px;
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton[optionBtn="true"]:hover {
                background: rgba(0, 150, 255, 0.15);
                color: white;
            }
            QPushButton[optionBtn="true"][selected="true"] {
                background: #0096FF;
                border: none;
                color: white;
                font-weight: 600;
            }
        """)

        self.center_window()
        QTimer.singleShot(100, self.fix_focus)

    def fix_focus(self):
        self.raise_()
        self.activateWindow()
        self.first_name_input.setFocus()
    
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
        main_layout.setContentsMargins(50, 70, 50, 50)
        main_layout.setSpacing(40)

        left_widget = self.create_left_section()
        main_layout.addWidget(left_widget, 3)

        right_widget = self.create_form_card()
        right_widget.setMinimumWidth(450)
        right_widget.setMaximumWidth(700)

        main_layout.addWidget(right_widget, 4)
    def create_left_section(self):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)
        
        logo = QLabel("SENTINELX")
        logo.setFont(QFont("Segoe UI", 32, QFont.Bold))
        logo.setStyleSheet("color: #0096FF; letter-spacing: 4px;")
        logo.setAlignment(Qt.AlignLeft)
        layout.addWidget(logo)
        
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096FF, stop:1 #00C8FF); border-radius: 1px;")
        layout.addWidget(line)
        
        layout.addSpacing(10)
        
        demo_title = QLabel(" Detect Insider Threats , protect your Data")
        demo_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        demo_title.setStyleSheet("color: #0096FF; letter-spacing: 2px;")
        demo_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_title)
        
        self.live_demo = LiveDemoWidget()
        layout.addWidget(self.live_demo)
        
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
        
        return widget
        
    def create_form_card(self):
        card = QFrame()
        card.setObjectName("formCard")
        card.setStyleSheet("""
            QFrame#formCard {
                background: rgba(10, 20, 40, 0.85);
                border-radius: 24px;
                border: 1px solid rgba(0, 150, 255, 0.3);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 25)
        card_layout.setSpacing(5)
        
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: white; border: none; background: transparent;")
        card_layout.addWidget(title)
        
        subtitle = QLabel("Build Your Own Digital Signature")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.6); border: none; background: transparent;")
        card_layout.addWidget(subtitle)
        
        card_layout.addSpacing(15)
        
        # Scroll area for form responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 10, 20, 0.3);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 150, 255, 0.4);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 150, 255, 0.7);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 10, 5)
        scroll_layout.setSpacing(12)
        
        # First Name and Last Name
        name_container = QWidget()
        name_container.setFixedHeight(50)
        name_container.setStyleSheet("background: transparent;")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(15)
        
        self.first_name_input = ModernInput("First Name")
        self.last_name_input = ModernInput("Last Name")
        self.first_name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.last_name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        name_layout.addWidget(self.first_name_input)
        name_layout.addWidget(self.last_name_input)
        scroll_layout.addWidget(name_container)
        
        # Email
        self.email_input = ModernInput("Email address")
        scroll_layout.addWidget(self.email_input)
        
        # Password
        self.password_input = ModernInput("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        scroll_layout.addWidget(self.password_input)
        
        # Confirm Password
        self.confirm_input = ModernInput("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        scroll_layout.addWidget(self.confirm_input)
        
        # Location
        self.location_input = ModernInput("Location (City, Country)")
        scroll_layout.addWidget(self.location_input)
        
        # Gender
        gender_label = QLabel("Gender")
        gender_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        gender_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        scroll_layout.addWidget(gender_label)
        
        gender_container = QWidget()
        gender_container.setStyleSheet("background: transparent;")
        gender_layout = QHBoxLayout(gender_container)
        gender_layout.setContentsMargins(0, 0, 0, 0)
        gender_layout.setSpacing(12)
        
        self.male_btn = QPushButton("Male")
        self.female_btn = QPushButton("Female")
        self.other_btn = QPushButton("Other")
        
        for btn in [self.male_btn, self.female_btn, self.other_btn]:
            btn.setProperty("optionBtn", "true")
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            gender_layout.addWidget(btn)
            
        self.male_btn.clicked.connect(lambda: self.select_gender("male"))
        self.female_btn.clicked.connect(lambda: self.select_gender("female"))
        self.other_btn.clicked.connect(lambda: self.select_gender("other"))
        
        scroll_layout.addWidget(gender_container)
        self.selected_gender = "male"
        
        # Department
        dept_label = QLabel("Department")
        dept_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dept_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        scroll_layout.addWidget(dept_label)
        
        self.department_combo = QComboBox()
        self.department_combo.setFixedHeight(50)
        self.department_combo.setStyleSheet("""
            QComboBox {
                background: rgba(0, 150, 255, 0.05);
                border: 1px solid rgba(0, 150, 255, 0.3);
                border-radius: 14px;
                padding: 10px 14px;
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
        scroll_layout.addWidget(self.department_combo)
        
        # Role selector
        role_label = QLabel("Select account type")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        role_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); margin-top: 5px;")
        scroll_layout.addWidget(role_label)
        
        role_container = QWidget()
        role_container.setStyleSheet("background: transparent;")
        role_layout = QHBoxLayout(role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(12)
        
        self.user_btn = QPushButton("Standard User")
        self.admin_btn = QPushButton("Administrator")
        
        for btn in [self.user_btn, self.admin_btn]:
            btn.setProperty("optionBtn", "true")
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            role_layout.addWidget(btn)
            
        self.user_btn.clicked.connect(lambda: self.select_role("user"))
        self.admin_btn.clicked.connect(lambda: self.select_role("admin"))
        
        scroll_layout.addWidget(role_container)
        self.selected_role = "user"
        
        scroll_layout.addSpacing(10)
        
        # Register button (Centered & Proportional)
        self.register_btn = ModernButton("Create Account →")
        self.register_btn.clicked.connect(self.handle_register)
        
        register_btn_container = QWidget()
        register_btn_container.setStyleSheet("background: transparent;")
        register_btn_layout = QHBoxLayout(register_btn_container)
        register_btn_layout.setContentsMargins(0, 0, 0, 0)
        register_btn_layout.setAlignment(Qt.AlignCenter)
        
        self.register_btn.setFixedWidth(320)
        register_btn_layout.addWidget(self.register_btn)
        scroll_layout.addWidget(register_btn_container)
        
        # Sign-in link
        signin_container = QWidget()
        signin_container.setStyleSheet("background: transparent;")
        signin_layout = QHBoxLayout(signin_container)
        signin_layout.setContentsMargins(0, 0, 0, 0)
        signin_layout.setSpacing(5)
        signin_layout.setAlignment(Qt.AlignCenter)
        
        signin_text = QLabel("Already have an account?")
        signin_text.setFont(QFont("Segoe UI", 10))
        signin_text.setStyleSheet("color: rgba(255, 255, 255, 0.6); background: transparent;")
        
        self.signin_link = QPushButton("Sign in")
        self.signin_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0096FF;
                font-weight: 600;
                font-size: 11px;
                padding: 0px;
            }
            QPushButton:hover {
                color: #00C8FF;
            }
        """)
        self.signin_link.setCursor(Qt.PointingHandCursor)
        self.signin_link.clicked.connect(self.handle_login)
        
        signin_layout.addWidget(signin_text)
        signin_layout.addWidget(self.signin_link)
        scroll_layout.addWidget(signin_container)
        
        scroll_area.setWidget(scroll_content)
        card_layout.addWidget(scroll_area)
        
        self.update_option_button_styles()
        
        return card
        
    def select_gender(self, gender):
        self.selected_gender = gender
        self.update_option_button_styles()
    
    def select_role(self, role):
        self.selected_role = role
        self.update_option_button_styles()
        
    def update_option_button_styles(self):
        # Update gender buttons
        self.male_btn.setProperty("selected", self.selected_gender == "male")
        self.female_btn.setProperty("selected", self.selected_gender == "female")
        self.other_btn.setProperty("selected", self.selected_gender == "other")
        
        # Update role buttons
        self.user_btn.setProperty("selected", self.selected_role == "user")
        self.admin_btn.setProperty("selected", self.selected_role == "admin")
        
        # Refresh styling
        for btn in [self.male_btn, self.female_btn, self.other_btn, self.user_btn, self.admin_btn]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def handle_register(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        location = self.location_input.text().strip()
        gender = self.selected_gender
        department = self.department_combo.currentText()

        parts = [p.strip() for p in location.split(",")]

        city = parts[0] if len(parts) > 0 else ""
        country = parts[1] if len(parts) > 1 else ""

        url = "http://127.0.0.1:8000/register"

        role_text = "Administrator" if self.selected_role == "admin" else "Standard User"

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "confirm_password": confirm,
            "city": city,
            "country": country,
            "gender": gender,
            "department": department,
            "account_type": role_text
        }

        try:
            response = requests.post(url, json=data)

            if response.status_code != 200:
                QMessageBox.warning(self, "Error", response.text)
                return

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        
        
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.location_input.clear()
        
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


    def handle_google_login(self):
        try:
            url = "http://127.0.0.1:8000/auth/google/login"
            response = requests.get(url)

            auth_url = response.json().get("url")

            import webbrowser
            webbrowser.open(auth_url)

            # هنا بس نستنى التوكن بطريقة بسيطة
            self.check_token()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def handle_github_login(self):
        try:
            url = "http://127.0.0.1:8000/auth/github/login"
            response = requests.get(url)

            if response.status_code == 200:
                auth_url = response.json().get("url")
                import webbrowser
                webbrowser.open(auth_url)
            else:
                QMessageBox.warning(self, "Error", "Failed to start GitHub login")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def check_token(self):
        import time
        import requests

        for _ in range(30):
            try:
                res = requests.get("http://127.0.0.1:8000/send-token")
                token = res.json().get("token")

                if token:
                    self.open_dashboard(token)
                    return

            except:
                pass

            time.sleep(1)

        QMessageBox.warning(self, "Error", "Login failed or timeout")

    def open_dashboard(self, token):
        QMessageBox.information(self, "Success", "Logged in successfully 🎉")
        print("JWT TOKEN:", token)
        # هنا بعدين نفتح الداشبورد


if __name__ == "__main__":
    random.seed()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = RegisterPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - 1300) // 2
    y = (screen.height() - 1000) // 2
    window.showMaximized()
    
   
    sys.exit(app.exec_())

    
