# ui/login_page.py
"""
SentinelX - Login Page with Advanced Cyber Background & Electron Particles
"""

import os
import json
import sys
import random
import math
from urllib import response
import requests
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QApplication,
    QDesktopWidget, QMessageBox, QGraphicsDropShadowEffect,
    QFrame, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen, QPixmap, QRadialGradient
from PyQt5.QtWidgets import QScrollArea

from ui.main_window import MainWindow
from ui.admin_dashboard import AdminDashboard

class ElectronParticle:
    """Electron particle class for advanced animations"""
    def __init__(self, x, y, size, speed_x, speed_y, color, orbit_center=None, orbit_radius=0):
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color
        self.alpha = random.randint(40, 100)
        self.pulse = random.uniform(0.5, 1.5)
        self.orbit_center = orbit_center
        self.orbit_radius = orbit_radius
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.trail = []  # Trail effect


class CyberBackground(QWidget):
    """Advanced animated cyber background with electron particles, grid, and glowing orbs"""
    
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.electrons = []
        self.particles = []
        self.glow_offset = 0
        self.grid_offset = 0
        self.init_electrons()
        self.init_particles()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)

        self.drag_position = None
        self.setMouseTracking(True)
    
    def init_electrons(self):
        """Create electron particles like in the header"""
        # Orbiting electrons around center
        for i in range(30):
            orbit_center = (random.randint(200, self.width() - 200), random.randint(150, self.height() - 150))
            electron = ElectronParticle(
                x=random.randint(0, 100),
                y=random.randint(0, 100),
                size=random.randint(3, 7),
                speed_x=random.uniform(-0.5, 0.5),
                speed_y=random.uniform(-0.5, 0.5),
                color=random.choice([0, 102, 204]),  # cyber-blue or neon-blue
                orbit_center=orbit_center,
                orbit_radius=random.randint(80, 200)
            )
            self.electrons.append(electron)
        
        # Fast moving electrons
        for i in range(20):
            electron = ElectronParticle(
                x=random.randint(0, 100),
                y=random.randint(0, 100),
                size=random.randint(2, 5),
                speed_x=random.uniform(-0.8, 0.8),
                speed_y=random.uniform(-0.8, 0.8),
                color=random.choice([102, 204]),  # lighter colors
                orbit_center=None,
                orbit_radius=0
            )
            self.electrons.append(electron)
    
    def init_particles(self):
        for _ in range(100):
            self.particles.append({
                'x': random.randint(0, 100),
                'y': random.randint(0, 100),
                'size': random.randint(2, 5),
                'speed_x': random.uniform(-0.2, 0.2),
                'speed_y': random.uniform(-0.2, 0.2),
                'alpha': random.randint(20, 80),
                'pulse': random.uniform(0.3, 1.7),
                'color': random.choice([0, 102, 204])
            })
    
    def update_animation(self):
        self.glow_offset = (self.glow_offset + 2) % 360
        self.grid_offset = (self.grid_offset + 1) % 50
        
        # Update electrons
        for e in self.electrons:
            if e.orbit_center and e.orbit_radius > 0:
                # Orbiting motion
                e.orbit_angle += 0.02
                center_x = e.orbit_center[0]
                center_y = e.orbit_center[1]
                e.x = center_x + e.orbit_radius * math.cos(e.orbit_angle)
                e.y = center_y + e.orbit_radius * math.sin(e.orbit_angle)
            else:
                # Free floating motion
                e.x += e.speed_x
                e.y += e.speed_y
                
                if e.x > self.width():
                    e.x = 0
                elif e.x < 0:
                    e.x = self.width()
                if e.y > self.height():
                    e.y = 0
                elif e.y < 0:
                    e.y = self.height()
            
            # Update alpha with pulse effect
            e.alpha = int(50 + 40 * math.sin(self.glow_offset * 0.03 * e.pulse))
        
        # Update particles
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
            
            p['alpha'] = int(30 + 30 * math.sin(self.glow_offset * 0.03 * p['pulse']))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dark gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(10, 20, 26))      # أزرق داكن فاتح
        gradient.setColorAt(0.5, QColor(30, 30, 40))    # أزرق متوسط نيون
        gradient.setColorAt(1, QColor(20, 40, 50))      # أزرق نيون فاتح

        painter.fillRect(self.rect(), gradient)
        
        # Animated glowing orbs (like in header)
        painter.setBrush(QBrush(QColor(0, 102, 255, 15)))
        painter.setPen(Qt.NoPen)
        
        orb_positions = [
            (self.width() * 0.2, self.height() * 0.3, 300),
            (self.width() * 0.8, self.height() * 0.7, 350),
            (self.width() * 0.5, self.height() * 0.1, 200),
            (self.width() * 0.1, self.height() * 0.8, 250),
            (self.width() * 0.9, self.height() * 0.2, 280)
        ]
        
        for i, (x, y, radius) in enumerate(orb_positions):
            offset_x = 40 * math.sin(self.glow_offset * 0.01 + i)
            offset_y = 30 * math.cos(self.glow_offset * 0.015 + i)
            painter.drawEllipse(int(x + offset_x), int(y + offset_y), radius, radius)
        
        # Draw electron particles with glow effect
        for e in self.electrons:
            # Glow effect
            glow = QRadialGradient(e.x, e.y, e.size * 3)
            glow.setColorAt(0, QColor(e.color, 150, 255, e.alpha))
            glow.setColorAt(1, QColor(e.color, 150, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(int(e.x - e.size * 1.5), int(e.y - e.size * 1.5), int(e.size * 3), int(e.size * 3))
            
            # Core electron
            painter.setBrush(QBrush(QColor(e.color, 150 + int(50 * math.sin(self.glow_offset * 0.02)), 255, e.alpha)))
            painter.drawEllipse(int(e.x - e.size / 2), int(e.y - e.size / 2), e.size, e.size)
        
        # Draw regular particles
        for p in self.particles:
            color_value = p['color']
            color = QColor(color_value, 150 + int(50 * math.sin(self.glow_offset * 0.02)), 255, p['alpha'])
            painter.setBrush(QBrush(color))
            x = int((p['x'] * self.width()) / 100)
            y = int((p['y'] * self.height()) / 100)
            painter.drawEllipse(x, y, p['size'], p['size'])
        
        # Corner glows (optional - can be added if desired)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(
                self.window().pos() + event.globalPos() - self.drag_position
            )
            self.drag_position = event.globalPos()
        
    def mouseReleaseEvent(self, event):
            self.drag_position = None


class GradientLineEdit(QLineEdit):
    """Professional input field with improved border-radius"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(55)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(16, 20, 40, 0.92);
                border: 1.5px solid rgba(0, 102, 255, 0.35);
                border-radius: 18px;
                font-size: 14px;
                color: white;
                font-family: 'Exo 2', sans-serif;
                padding: 0 20px;
            }
            QLineEdit:focus {
                border: 2px solid #0066ff;
                background: rgba(16, 20, 40, 0.98);
                border-radius: 18px;
            }
            QLineEdit:hover {
                border: 1.5px solid rgba(0, 102, 255, 0.7);
                border-radius: 18px;
                background: rgba(20, 25, 45, 0.95);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 102, 255, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        


class GradientButton(QPushButton):
    """Professional button with gradient and animations"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0066ff,
                    stop:1 #00ccff);
                border: none;
                border-radius: 18px;
                color: white;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Orbitron', sans-serif;
                letter-spacing: 1.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ccff,
                    stop:1 #0066ff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0055cc,
                    stop:1 #0099cc);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 102, 255, 100))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        self.animation.stop()
        geometry = self.geometry()
        self.animation.setEndValue(geometry.adjusted(-2, -2, 4, 4))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.stop()
        geometry = self.geometry()
        self.animation.setEndValue(geometry.adjusted(2, 2, -4, -4))
        self.animation.start()
        super().leaveEvent(event)


class SocialButton(QPushButton):
    """Social login button with hover effects"""
    
    def __init__(self, text, icon, parent=None):
        super().__init__(f"{icon}  {text}", parent)
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(16, 20, 40, 0.92);
                border: 1.5px solid rgba(0, 102, 255, 0.3);
                border-radius: 18px;
                color: white;
                font-size: 14px;
                font-family: 'Exo 2', sans-serif;
                text-align: center;
            }
            QPushButton:hover {
                background: rgba(0, 102, 255, 0.2);
                border: 1.5px solid rgba(0, 102, 255, 0.7);
                border-radius: 18px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 102, 255, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernCheckBox(QCheckBox):
    """Custom checkbox with cyber styling"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: rgba(255, 255, 255, 0.85);
                font-size: 13px;
                spacing: 12px;
                font-family: 'Exo 2', sans-serif;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 8px;
                border: 2px solid rgba(0, 102, 255, 0.5);
                background: rgba(16, 20, 40, 0.92);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #0066ff;
                background: rgba(0, 102, 255, 0.15);
                border-radius: 8px;
            }
            QCheckBox::indicator:checked {
                background: #0066ff;
                border: 2px solid #0066ff;
                border-radius: 8px;
            }
        """)


class LoginPage(QMainWindow):
    """Professional Login Window with Cyber Background"""

    def open_dashboard(self, token):
        self.dashboard = MainWindow(token)
        self.dashboard.show()
        self.close()
    
    def __init__(self, register_page=None):
        super().__init__()
        self.setWindowTitle("SentinelX - Login")
        self.register_page = register_page
        self.setMinimumSize(1200, 800)
        
        self.users_db = self.load_users()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_pos = None
        
        # Create advanced cyber background with electrons
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.bg_widget = CyberBackground()
        self.scroll.setWidget(self.bg_widget)

        self.setCentralWidget(self.scroll)

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
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self.bg_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(25)
        
        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 30, 40, 0)
        
        # Logo container
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(15)
        
        logo_icon = QLabel("🫆")
        logo_icon.setFont(QFont("Segoe UI", 32))
        logo_icon.setStyleSheet("background: transparent;")
        
        logo_text = QLabel("SENTINELX")
        logo_text.setFont(QFont("Orbitron", 24, QFont.Bold))
        logo_text.setStyleSheet("color: #0066ff; letter-spacing: 3px; background: transparent;")
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        header_layout.addWidget(logo_container)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        line = QFrame()
        line.setFixedHeight(2)
        line.setFixedWidth(800)
        line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096FF, stop:1 #00C8FF); border-radius: 1px;")
        main_layout.addWidget(line)
        
        main_layout.addSpacing(10)
        # Center container
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.addStretch(1)
        
        # Login Card
        login_card = QFrame()
        login_card.setMinimumWidth(700)
        login_card.setMaximumWidth(800)
        login_card.setMinimumHeight(600)
        login_card.setMaximumHeight(700)
        login_card.setStyleSheet("""
            QFrame {
                background: rgba(10, 12, 25, 0.94);
                border-radius: 32px;
                border: 1px solid rgba(0, 102, 255, 0.35);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        login_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(45, 45, 45, 45)
        card_layout.setSpacing(25)
        
        # Title - Sign in (الصحيح)
        title_label = QLabel("Login to SentinelX")
        title_label.setFont(QFont("Orbitron", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        title_label.setMinimumHeight(70)
        title_label.setWordWrap(True)

        title_label.setStyleSheet("""
            color: white;
            background: transparent;
            padding: 12px;
            margin: 0px;
        """)

        card_layout.addWidget(title_label)
        
        # Description - Welcome Back!
        desc_label = QLabel("Welcome Back!")
        desc_label.setFont(QFont("Exo 2", 13))
        desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.65); background: transparent;border: none; padding: 0; margin: 0;;")
        desc_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc_label)
        
        card_layout.addSpacing(15)
        
        email_label = QLabel(" Enter Your email")
        email_label.setContentsMargins(0, 10, 0, 5)
        email_label.setFont(QFont("Exo 2", 10))
        email_label.setStyleSheet("color: rgba(255, 255, 255, 0.65);background: transparent; border: none; padding: 0; margin: 0;")
        card_layout.addWidget(email_label)

        self.email_input = GradientLineEdit("📧  kmdvj@exmaple.com")
        card_layout.addWidget(self.email_input)

        card_layout.addSpacing(10)

# Password Field - بدون أي styling
        password_label = QLabel(" Enter Your Password")
        password_label.setContentsMargins(0, 15, 0, 5)
        password_label.setFont(QFont("Exo 2", 10))
        password_label.setStyleSheet("color: rgba(255, 255, 255, 0.65);background: transparent; border: none; padding: 0; margin: 0;")
        card_layout.addWidget(password_label)

        self.password_input = GradientLineEdit("🛡️ّ •••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(10)


        card_layout.addSpacing(5)
        self.keep_signed_check = ModernCheckBox("Keep me signed in")
        card_layout.addWidget(self.keep_signed_check)
        card_layout.addSpacing(15)
        
        
        # Sign In Button
        self.login_btn = GradientButton("SIGN IN →")
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)
        
        card_layout.addSpacing(15)
        
        # Divider
        divider_container = QWidget()
        divider_layout = QHBoxLayout(divider_container)
        divider_layout.setContentsMargins(0, 5, 0, 5)
        
        line_left = QFrame()
        line_left.setFrameShape(QFrame.HLine)
        line_left.setStyleSheet("background: rgba(0, 102, 255, 0.3); max-height: 1px; border-radius: 1px;")
        divider_layout.addWidget(line_left, 1)
        
        or_label = QLabel("or")
        or_label.setFont(QFont("Exo 2", 11))
        or_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); padding: 0 15px; background: transparent;")
        or_label.setAlignment(Qt.AlignCenter)
        divider_layout.addWidget(or_label)
        
        line_right = QFrame()
        line_right.setFrameShape(QFrame.HLine)
        line_right.setStyleSheet("background: rgba(0, 102, 255, 0.3); max-height: 1px; border-radius: 1px;")
        divider_layout.addWidget(line_right, 1)
        
        card_layout.addWidget(divider_container)
        
        # Social Buttons
        self.google_btn = SocialButton("Sign in with Google", "🄶")
        self.google_btn.clicked.connect(self.login_with_google)
        card_layout.addWidget(self.google_btn)
        
        card_layout.addSpacing(15)
        
        # Bottom Links
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(10)
        
        links_widget = QWidget()
        links_layout = QHBoxLayout(links_widget)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setSpacing(8)
        
        forgot_btn = QPushButton("Forgot password?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0066ff;
                font-size: 12px;
                padding: 5px;
                font-family: 'Exo 2', sans-serif;
            }
            QPushButton:hover {
                color: #00ccff;
            }
        """)
        forgot_btn.clicked.connect(self.forgot_password)
        links_layout.addWidget(forgot_btn)
        
        
        
        contact_btn = QPushButton("Contact us")
        contact_btn.setCursor(Qt.PointingHandCursor)
        contact_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0066ff;
                font-size: 12px;
                padding: 5px;
                font-family: 'Exo 2', sans-serif;
            }
            QPushButton:hover {
                color: #00ccff;
            }
        """)
        contact_btn.clicked.connect(self.contact_us)
        links_layout.addWidget(contact_btn)
        
        bottom_layout.addWidget(links_widget)
        bottom_layout.addStretch()
        
        signup_widget = QWidget()
        signup_layout = QHBoxLayout(signup_widget)
        signup_layout.setContentsMargins(0, 0, 0, 0)
        signup_layout.setSpacing(8)
        
        no_account_label = QLabel("Don't have an account?")
        no_account_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 12px; font-family: 'Exo 2', sans-serif; background: transparent;border:0;")
        signup_layout.addWidget(no_account_label)
        
        self.signup_link = QPushButton("Create Account")
        self.signup_link.setCursor(Qt.PointingHandCursor)
        self.signup_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0066ff;
                font-size: 12px;
                font-weight: 600;
                padding: 5px;
                font-family: 'Exo 2', sans-serif;
            }
            QPushButton:hover {
                color: #00ccff;
            }
        """)
        self.signup_link.clicked.connect(self.handle_register)
        signup_layout.addWidget(self.signup_link)
        
        bottom_layout.addWidget(signup_widget)
        
        card_layout.addWidget(bottom_container)
        
        center_layout.addStretch()
        center_layout.addWidget(login_card, 0, Qt.AlignCenter)
        center_layout.addStretch()
        
        main_layout.addWidget(center_container, 1)
    
    def login_with_google(self):
        QMessageBox.information(self, "Google Login", "Google authentication will be integrated here.\n\nThis feature is coming soon!")
    
    def forgot_password(self):
        QMessageBox.information(self, "Reset Password", "Please contact your administrator to reset your password.")
    
    def contact_us(self):
        QMessageBox.information(self, "Contact Us", "📧 Email: support@sentinelx.com\n🌐 Website: www.sentinelx.com\n📞 Phone: +1 (555) 123-4567")
    
        
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter email and password")
            return

        try:
            response = requests.post(
                 "http://127.0.0.1:8000/login",
                json={
                    "email": email,
                    "password": password,
                    "remember_me": self.keep_signed_check.isChecked()
                }
           )

            if response.status_code == 200:
                print(response.status_code)
                print(response.text)
                
                print("STATUS:", response.status_code)
                print("TEXT:", response.text)
                data = response.json()
                
                        # 🔍 DEBUG - Print everything to see what's coming
                print("=== FULL RESPONSE ===")
                print(data)
                print("=====================")
                print(f"Token: {data.get('access_token')}")
                print(f"Role: {data.get('role')}")
                print(f"All keys: {data.keys()}")
        
        # ... rest of your code

                
                
                token = data["access_token"]
                role = data.get("role")  # 👈 الباك لازم يرجعه

                # 💾 نحفظ التوكن (مهم جدًا)
                with open("token.txt", "w") as f:
                    f.write(token)

                if role == "admin":
                    self.dashboard = AdminDashboard(token)
                else:
                    self.dashboard = MainWindow(token)
                
                self.dashboard.show()
                self.close()
            
            
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("detail", "Login failed")
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
            
    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
    
    def handle_register(self):
        if self.register_page:
            self.register_page.show()
            self.close()
        else:
            QMessageBox.information(self, "Info", "Please use the registration page to create an account")
    
    def setup_controls(self):
        controls = QWidget(self)
        controls.setFixedSize(130, 38)
        controls.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        btn_style = """
            QPushButton {
                background: rgba(16, 20, 40, 0.92);
                border-radius: 19px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0, 102, 255, 0.6); border-radius: 19px; }
        """
        
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(38, 38)
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.showMinimized)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(38, 38)
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(38, 38)
        self.close_btn.setStyleSheet(btn_style + "QPushButton:hover { background: #ff3366; border-radius: 19px; }")
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


if __name__ == "__main__":
    random.seed()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LoginPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - 1200) // 2
    y = (screen.height() - 850) // 2
    window.setGeometry(x, y, 1200, 850)
    
    window.show()
    sys.exit(app.exec_())