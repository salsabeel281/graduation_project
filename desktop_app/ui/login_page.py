# ui/login_page.py
"""
SentinelX - Login Page with Neon Blue Animated Background
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
    QFrame
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen, QPixmap


class NeonBackgroundLogin(QWidget):
    """Animated neon blue background with floating particles"""
    
    def __init__(self, parent=None, background_image=None):
        super().__init__(parent)
        self.particles = []
        self.glow_offset = 0
        self.background_image = background_image
        self.init_particles()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)
    
    def set_background_image(self, image_path):
        """Set custom background image"""
        self.background_image = image_path
        self.update()
    
    def init_particles(self):
        for _ in range(40):
            self.particles.append({
                'x': random.randint(0, 100),
                'y': random.randint(0, 100),
                'size': random.randint(2, 5),
                'speed_x': random.uniform(-0.2, 0.2),
                'speed_y': random.uniform(-0.1, 0.3),
                'alpha': random.randint(20, 60),
                'pulse': random.uniform(0.5, 1.5)
            })
    
    def update_animation(self):
        self.glow_offset = (self.glow_offset + 2) % 360
        
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
            
            p['alpha'] = int(30 + 20 * math.sin(self.glow_offset * 0.02 * p['pulse']))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background image from assets
        bg_image_path = "assets/download.jpg"
        if os.path.exists(bg_image_path):
            pixmap = QPixmap(bg_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(0, 0, scaled_pixmap)
                
                # Add dark overlay for better text visibility
                painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
                painter.setPen(Qt.NoPen)
                painter.drawRect(self.rect())
        elif self.background_image and os.path.exists(self.background_image):
            pixmap = QPixmap(self.background_image)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                painter.drawPixmap(0, 0, scaled_pixmap)
                
                # Add dark overlay
                painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
                painter.setPen(Qt.NoPen)
                painter.drawRect(self.rect())
        else:
            # Default neon gradient background if image not found
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(5, 20, 45))
            gradient.setColorAt(0.5, QColor(10, 35, 65))
            gradient.setColorAt(1, QColor(8, 25, 55))
            painter.fillRect(self.rect(), gradient)
        
        # Draw particles
        for p in self.particles:
            color = QColor(0, 150, 255, p['alpha'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            x = int((p['x'] * self.width()) / 100)
            y = int((p['y'] * self.height()) / 100)
            painter.drawEllipse(x, y, p['size'], p['size'])
        
        # Draw corner glows
        corner_gradient = QLinearGradient(0, 0, 200, 200)
        corner_gradient.setColorAt(0, QColor(0, 150, 255, 20))
        corner_gradient.setColorAt(1, QColor(0, 150, 255, 0))
        painter.fillRect(0, 0, 200, 200, corner_gradient)
        painter.fillRect(self.width() - 200, self.height() - 200, 200, 200, corner_gradient)


class ModernInputLogin(QLineEdit):
    """Modern input field with oval shape - very visible"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(55)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 150, 255, 0.15);
                font-size: 15px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                background: rgba(0, 150, 255, 0.25);
            }
            QLineEdit:hover {
                background: rgba(0, 150, 255, 0.2);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 150, 255, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButtonLogin(QPushButton):
    """Modern button with oval shape"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0096FF,
                    stop:1 #00C8FF);
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 16px;
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
                    stop:0 #0080CC,
                    stop:1 #00A0CC);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 150, 255, 100))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class LoginPage(QMainWindow):
    """Main Login Window"""
    
    def __init__(self, register_page=None):
        super().__init__()
        self.setWindowTitle("SentinelX - Login")
        self.register_page = register_page
        self.setMinimumSize(1300, 1000)
        
        self.users_db = self.load_users()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_pos = None
        
        # Create background with default image from assets
        self.background_image_path = "assets/download.jpg"
        self.central_widget = NeonBackgroundLogin(background_image=self.background_image_path)
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()
        self.setup_controls()
    
    def set_background_image(self, image_path):
        """Set custom background image"""
        self.background_image_path = image_path
        self.central_widget.set_background_image(image_path)
    
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
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with logo (top left)
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 30, 40, 0)
        
        # Logo outside the container - top left
        logo_label = QLabel("🛡️ SENTINELX")
        logo_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        logo_label.setStyleSheet("color: #0096FF; letter-spacing: 4px; background: transparent;")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # Center container - takes most of the space
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(100, 50, 100, 80)
        
        # Login Card - expanded to take more space
        login_card = QFrame()
        login_card.setMinimumWidth(600)
        login_card.setMaximumWidth(700)
        login_card.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 40, 0.92);
                border-radius: 45px;
                border: 1px solid rgba(0, 150, 255, 0.5);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        login_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(60, 60, 60, 60)
        card_layout.setSpacing(25)
        
        # Welcome Title
        welcome_label = QLabel("Welcome Back!")
        welcome_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        welcome_label.setStyleSheet("color: white;")
        welcome_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(welcome_label)
        
        subtitle_label = QLabel("Sign in to continue to your account")
        subtitle_label.setFont(QFont("Segoe UI", 13))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        subtitle_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle_label)
        
        card_layout.addSpacing(20)
        
        # Email input
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        email_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 5px;")
        card_layout.addWidget(email_label)
        
        self.email_input = ModernInputLogin("Enter your email")
        card_layout.addWidget(self.email_input)
        
        card_layout.addSpacing(10)
        
        # Password input
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        password_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 5px;")
        card_layout.addWidget(password_label)
        
        self.password_input = ModernInputLogin("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.password_input)
        
        # Options row
        options_container = QWidget()
        options_layout = QHBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        self.remember_check = QPushButton("□ Remember me")
        self.remember_check.setCursor(Qt.PointingHandCursor)
        self.remember_check.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.8);
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                color: #0096FF;
            }
        """)
        self.remember_check.clicked.connect(self.toggle_remember)
        self.remember_checked = False
        
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0096FF;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #00C8FF;
                text-decoration: underline;
            }
        """)
        forgot_btn.clicked.connect(self.forgot_password)
        
        options_layout.addWidget(self.remember_check)
        options_layout.addStretch()
        options_layout.addWidget(forgot_btn)
        card_layout.addWidget(options_container)
        
        card_layout.addSpacing(15)
        
        # Login button
        self.login_btn = ModernButtonLogin("Sign In →")
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background: rgba(0, 150, 255, 0.3); margin: 20px 0;")
        card_layout.addWidget(divider)
        
        # Demo account info
        demo_frame = QFrame()
        demo_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 150, 255, 0.15);
                border-radius: 25px;
                padding: 15px;
            }
        """)
        demo_layout = QVBoxLayout(demo_frame)
        
        demo_title = QLabel("🔐 Demo Account")
        demo_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        demo_title.setStyleSheet("color: #00C8FF;")
        demo_title.setAlignment(Qt.AlignCenter)
        demo_layout.addWidget(demo_title)
        
        demo_creds = QLabel("demo@sentinelx.com / demo123")
        demo_creds.setFont(QFont("Segoe UI", 11))
        demo_creds.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        demo_creds.setAlignment(Qt.AlignCenter)
        demo_layout.addWidget(demo_creds)
        
        card_layout.addWidget(demo_frame)
        
        # Sign up link
        signup_container = QWidget()
        signup_layout = QHBoxLayout(signup_container)
        signup_layout.setContentsMargins(0, 15, 0, 0)
        signup_layout.setAlignment(Qt.AlignCenter)
        
        signup_text = QLabel("Don't have an account?")
        signup_text.setFont(QFont("Segoe UI", 12))
        signup_text.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        
        self.signup_link = QPushButton("Create Account")
        self.signup_link.setCursor(Qt.PointingHandCursor)
        self.signup_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0096FF;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #00C8FF;
                text-decoration: underline;
            }
        """)
        self.signup_link.clicked.connect(self.handle_register)
        
        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(self.signup_link)
        card_layout.addWidget(signup_container)
        
        # Add to center layout
        center_layout.addWidget(login_card, 0, Qt.AlignCenter)
        main_layout.addWidget(center_container, 1)
    
    def toggle_remember(self):
        self.remember_checked = not self.remember_checked
        if self.remember_checked:
            self.remember_check.setText("☑ Remember me")
            self.remember_check.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #0096FF;
                    font-size: 13px;
                }
            """)
        else:
            self.remember_check.setText("□ Remember me")
            self.remember_check.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 13px;
                }
            """)
    
    def forgot_password(self):
        QMessageBox.information(
            self,
            "Reset Password",
            "Please contact your administrator to reset your password.\n\n"
            "Demo Account:\n"
            "Email: demo@sentinelx.com\n"
            "Password: demo123"
        )
    
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter email and password")
            return
        
        # Demo account
        if email == "demo@sentinelx.com" and password == "demo123":
            QMessageBox.information(
                self,
                "Welcome to SentinelX! 🎉",
                f"Demo login successful!\n\n"
                f"Welcome: Demo User\n"
                f"Role: Standard User"
            )
            self.clear_fields()
            return
        
        # Check in database
        if email in self.users_db and self.users_db[email]["password"] == password:
            user_data = self.users_db[email]
            role_text = "Administrator" if user_data.get("role") == "admin" else "Standard User"
            
            QMessageBox.information(
                self,
                "Welcome Back! 🎉",
                f"Login successful!\n\n"
                f"Welcome: {user_data.get('full_name', user_data.get('name', email))}\n"
                f"Role: {role_text}\n"
                f"Department: {user_data.get('department', 'N/A')}"
            )
            self.clear_fields()
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password")
    
    def clear_fields(self):
        self.email_input.clear()
        self.password_input.clear()
        if not self.remember_checked:
            self.remember_check.setText("□ Remember me")
            self.remember_checked = False
    
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
        
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(38, 38)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,0.5);
                border-radius: 19px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,0,0,0.7); }
        """)
        self.min_btn.clicked.connect(self.showMinimized)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(38, 38)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,0.5);
                border-radius: 19px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,0,0,0.7); }
        """)
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(38, 38)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,0.5);
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


if __name__ == "__main__":
    random.seed()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LoginPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - 1300) // 2
    y = (screen.height() - 1000) // 2
    window.setGeometry(x, y, 1300, 1000)
    
    window.show()
    sys.exit(app.exec_())