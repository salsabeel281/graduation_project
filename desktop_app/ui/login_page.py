# ui/login_page.py
<<<<<<< HEAD
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QApplication,
    QDesktopWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QPen, QIcon, QPixmap, QPainterPath
import os
import json


class ModernLineEdit(QLineEdit):
    """Custom line edit with modern glassmorphism styling"""
    
    def _init_(self, placeholder="", parent=None):
        super()._init_(parent)
=======
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
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(55)
        self.setStyleSheet("""
            QLineEdit {
<<<<<<< HEAD
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.6);
                background: rgba(255, 255, 255, 0.2);
            }
            QLineEdit:hover {
                border: 1px solid rgba(255, 255, 255, 0.5);
                background: rgba(255, 255, 255, 0.18);
            }
        """)
        self.setFont(QFont("Segoe UI", 14))
    
    def focusInEvent(self, event):
        """Add animation effect on focus"""
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.6);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
        """)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Reset style on focus out"""
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
        """)
        super().focusOutEvent(event)


class GlassButton(QPushButton):
    """Custom glassmorphism button"""
    
    def _init_(self, text, parent=None):
        super()._init_(text, parent)
=======
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
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
<<<<<<< HEAD
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(255, 255, 255, 0.85));
                border: none;
                border-radius: 12px;
                color: #1A1A1A;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 1),
                    stop:1 rgba(255, 255, 255, 0.95));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.8),
                    stop:1 rgba(255, 255, 255, 0.7));
            }
        """)


class ImageBackgroundWidget(QWidget):
    """Custom widget that draws background image from assets folder"""
    
    def _init_(self, parent=None):
        super()._init_(parent)
        self.background_image = None
        self.load_background_image()
    
    def load_background_image(self):
        """Load the background image from assets folder"""
        # الحصول على المسار الحالي
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # قائمة بأسماء الملفات الممكنة
        image_names = ["bg.png", "background.png", "bg.jpg", "background.jpg"]
        
        # البحث في المسارات المختلفة
        search_paths = [
            os.path.join(parent_dir, "assets"),      # ../assets/
            os.path.join(current_dir, "assets"),     # ./ui/assets/
            os.path.join(os.getcwd(), "assets"),     # assets/ من المجلد الحالي
            parent_dir,                               # ../ (المجلد الرئيسي)
            current_dir,                              # ./ui/
            os.getcwd(),                              # المجلد الحالي
        ]
        
        for search_path in search_paths:
            for image_name in image_names:
                image_path = os.path.join(search_path, image_name)
                if os.path.exists(image_path):
                    self.background_image = QPixmap(image_path)
                    print(f"✅ Background image loaded from: {image_path}")
                    return
        
        # إذا لم يتم العثور على الصورة
        print(f"❌ Background image not found in assets folder")
        print(f"   Searched in: {search_paths}")
    
    def paintEvent(self, event):
        """Draw the background image fully visible"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        if self.background_image and not self.background_image.isNull():
            # Scale image to fit window while maintaining aspect ratio
            scaled_image = self.background_image.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            # Center the image
            x = (self.width() - scaled_image.width()) // 2
            y = (self.height() - scaled_image.height()) // 2
            
            painter.drawPixmap(x, y, scaled_image)
        else:
            # Fallback gradient if no image found
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(26, 26, 46))
            gradient.setColorAt(0.5, QColor(22, 33, 62))
            gradient.setColorAt(1, QColor(15, 52, 96))
            painter.fillRect(self.rect(), QBrush(gradient))
        
        super().paintEvent(event)


class LoginPage(QMainWindow):
    """Modern login page with glassmorphism design"""
    
    def _init_(self, register_page=None):
        super()._init_()
        self.setWindowTitle("Login - Exclusive Membership")
        self.register_page = register_page
        
        # User database
        self.users_db = self.load_users()
        
        # Allow window to be resizable
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Track window state
        self.is_maximized = False
        self.normal_geometry = None
        self.drag_position = None
        
        # Setup main widget with background image
        self.central_widget = ImageBackgroundWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Create form container
        self.form_container = self.create_form_container()
        main_layout.addWidget(self.form_container)
        
        # Add window controls
        self.setup_window_controls()
        
    def load_users(self):
        """Load users from JSON file or create default users"""
        users_file = "users.json"
        
        # Default users
        default_users = {
            "admin@example.com": {
                "name": "Administrator",
                "password": "admin123",
                "role": "admin"
            },
            "user@example.com": {
                "name": "Regular User",
                "password": "user123",
                "role": "user"
            }
        }
        
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_users
        else:
            # Save default users
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=4, ensure_ascii=False)
            return default_users
    
    def save_users(self):
        """Save users to JSON file"""
        with open("users.json", 'w', encoding='utf-8') as f:
            json.dump(self.users_db, f, indent=4, ensure_ascii=False)
    
    def create_form_container(self):
        """Create the main login form with glassmorphism effect"""
        container = QWidget()
        container.setFixedWidth(580)
        
        container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== Header Section =====
        brand_label = QLabel("✨ EXCLUSIVE CLUB")
        brand_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        brand_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            letter-spacing: 2px;
            margin-bottom: 16px;
        """)
        brand_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(brand_label)
        
        heading = QLabel("Welcome Back")
        heading.setFont(QFont("Georgia", 44, QFont.Bold))
        heading.setStyleSheet("""
            color: #FFFFFF;
            margin-bottom: 12px;
        """)
        heading.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(heading)
        
        subheading = QLabel(
            "Sign in to access your exclusive benefits"
        )
        subheading.setFont(QFont("Segoe UI", 14))
        subheading.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.4;
            margin-bottom: 32px;
        """)
        subheading.setWordWrap(True)
        subheading.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subheading)
        
        # ===== Form Fields =====
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)
        
        # Email field
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        email_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 6px;")
        form_layout.addWidget(email_label)
        
        self.email_input = ModernLineEdit("hello@example.com")
        form_layout.addWidget(self.email_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        password_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin-bottom: 6px;")
        form_layout.addWidget(password_label)
        
        self.password_input = ModernLineEdit("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)
        
        # Remember me and Forgot password
        options_container = QWidget()
        options_layout = QHBoxLayout(options_container)
        options_layout.setContentsMargins(0, 8, 0, 8)
        
        # Remember me checkbox
        self.remember_checkbox = QPushButton("☐")
        self.remember_checkbox.setFixedSize(20, 20)
        self.remember_checkbox.setCursor(Qt.PointingHandCursor)
        self.remember_checkbox.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
            }
        """)
        self.remember_checkbox.clicked.connect(self.toggle_remember)
        self.remember_checked = False
        
        remember_label = QLabel("Remember me")
        remember_label.setFont(QFont("Segoe UI", 12))
        remember_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setFont(QFont("Segoe UI", 12))
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        self.forgot_btn.setCursor(Qt.PointingHandCursor)
        self.forgot_btn.clicked.connect(self.handle_forgot_password)
        
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addWidget(remember_label)
        options_layout.addStretch()
        options_layout.addWidget(self.forgot_btn)
        
        form_layout.addWidget(options_container)
        
        main_layout.addWidget(form_widget)
        main_layout.addSpacing(24)
        
        # Login Button
        self.login_btn = GlassButton("Sign In →")
        self.login_btn.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_btn)
        
        # Divider
        divider_container = QWidget()
        divider_layout = QHBoxLayout(divider_container)
        divider_layout.setContentsMargins(0, 24, 0, 24)
        
        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setStyleSheet("background: rgba(255, 255, 255, 0.2); max-height: 1px;")
        
        or_label = QLabel("or continue with")
        or_label.setFont(QFont("Segoe UI", 12))
        or_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); padding: 0 20px;")
        or_label.setAlignment(Qt.AlignCenter)
        
        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setStyleSheet("background: rgba(255, 255, 255, 0.2); max-height: 1px;")
        
        divider_layout.addWidget(left_line, 1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(right_line, 1)
        
        main_layout.addWidget(divider_container)
        
        # Social Buttons
        social_container = QWidget()
        social_layout = QHBoxLayout(social_container)
        social_layout.setContentsMargins(0, 0, 0, 0)
        social_layout.setSpacing(16)
        
        # Google button
        self.google_btn = QPushButton("G")
        self.google_btn.setFixedSize(52, 52)
        self.google_btn.setCursor(Qt.PointingHandCursor)
        self.google_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 26px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Apple button
        self.apple_btn = QPushButton("")
        self.apple_btn.setFixedSize(52, 52)
        self.apple_btn.setCursor(Qt.PointingHandCursor)
        self.apple_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 26px;
                color: white;
                font-size: 26px;
                font-weight: normal;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        
        social_layout.addStretch()
        social_layout.addWidget(self.google_btn)
        social_layout.addWidget(self.apple_btn)
        social_layout.addStretch()
        
        main_layout.addWidget(social_container)
        main_layout.addSpacing(24)
        
        # Register Link
        register_container = QWidget()
        register_layout = QHBoxLayout(register_container)
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setAlignment(Qt.AlignCenter)
        
        register_text = QLabel("Don't have an account?")
        register_text.setFont(QFont("Segoe UI", 13))
        register_text.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        
        self.register_link = QPushButton("Create Account")
        self.register_link.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.register_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #FFFFFF;
                padding: 4px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 0.8);
            }
        """)
        self.register_link.setCursor(Qt.PointingHandCursor)
        self.register_link.clicked.connect(self.handle_register)
        
        register_layout.addWidget(register_text)
        register_layout.addWidget(self.register_link)
        
        main_layout.addWidget(register_container)
        
        # Demo credentials hint
        demo_label = QLabel("💡 Demo Credentials: admin@example.com / admin123  |  user@example.com / user123")
        demo_label.setFont(QFont("Segoe UI", 10))
        demo_label.setStyleSheet("color: rgba(255, 255, 255, 0.4); margin-top: 20px;")
        demo_label.setWordWrap(True)
        demo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(demo_label)
        
        return container
    
    def toggle_remember(self):
        """Toggle remember me checkbox"""
        self.remember_checked = not self.remember_checked
        if self.remember_checked:
            self.remember_checkbox.setText("☑")
            self.remember_checkbox.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.25);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 4px;
                    color: white;
                    font-size: 12px;
                }
            """)
        else:
            self.remember_checkbox.setText("☐")
            self.remember_checkbox.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                    color: white;
                    font-size: 12px;
                }
            """)
    
    def setup_window_controls(self):
        """Add custom window controls"""
        controls_container = QWidget(self)
        controls_container.setFixedSize(140, 34)
        controls_container.move(self.width() - 150, 20)
        controls_container.setStyleSheet("background: transparent;")
        
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minimize button
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(34, 34)
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: 17px;
                color: white;
                font-size: 18px;
                font-weight: normal;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        # Maximize/Restore button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(34, 34)
        self.maximize_btn.setCursor(Qt.PointingHandCursor)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: 17px;
                color: white;
                font-size: 18px;
                font-weight: normal;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: 17px;
                color: white;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background: #E81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.maximize_btn)
        controls_layout.addWidget(self.close_btn)
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.is_maximized:
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.maximize_btn.setText("□")
=======
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
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            screen = QDesktopWidget().screenGeometry()
            self.setGeometry(screen)
<<<<<<< HEAD
            self.maximize_btn.setText("❐")
            self.is_maximized = True
        
        self.update_controls_position()
    
    def update_controls_position(self):
        """Update window controls position after resize"""
        if hasattr(self, 'minimize_btn') and self.minimize_btn.parent():
            self.minimize_btn.parent().move(self.width() - 150, 20)
    
    def handle_login(self):
        """Handle login button click"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if email == "hello@example.com":
            email = ""
        
        if not email:
            QMessageBox.warning(self, "Validation Error", "Please enter your email address.")
            return
        
        if not password:
            QMessageBox.warning(self, "Validation Error", "Please enter your password.")
            return
        
        # Check credentials
        if email in self.users_db and self.users_db[email]["password"] == password:
            user_info = self.users_db[email]
            role = user_info["role"]
            name = user_info["name"]
            
            # Show success message based on role
            if role == "admin":
                QMessageBox.information(
                    self,
                    "Admin Access Granted 🛡️",
                    f"Welcome back, {name}!\n\nYou have logged in as ADMINISTRATOR.\n\nYou have full access to all system features."
                )
                print(f"✅ ADMIN LOGIN - Name: {name}, Email: {email}")
            else:
                QMessageBox.information(
                    self,
                    "Welcome Back! 🎉",
                    f"Welcome back, {name}!\n\nYou have successfully logged in as a regular user.\n\nEnjoy your exclusive benefits!"
                )
                print(f"✅ USER LOGIN - Name: {name}, Email: {email}")
            
            if self.remember_checked:
                print(f"📝 Remember me enabled for: {email}")
            
            self.email_input.clear()
            self.password_input.clear()
            self.email_input.setPlaceholderText("hello@example.com")
            
        else:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid email or password.\n\nPlease check your credentials and try again."
            )
    
    def handle_register(self):
        """Navigate to registration page"""
        if self.register_page:
            self.register_page.show()
            self.close()
        else:
            from ui.register_page import RegisterPage
            self.register_page = RegisterPage(login_page=self)
            self.register_page.show()
            self.close()
    
    def handle_forgot_password(self):
        """Handle forgot password"""
        QMessageBox.information(
            self,
            "Reset Password",
            "Password reset link has been sent to your email address.\n\nPlease check your inbox and follow the instructions."
        )
    
    def mousePressEvent(self, event):
        """Handle window dragging"""
        if event.button() == Qt.LeftButton and not self.is_maximized:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.LeftButton and not self.is_maximized and hasattr(self, 'drag_position') and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def resizeEvent(self, event):
        """Update window controls position when window is resized"""
=======
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
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
        super().resizeEvent(event)
        self.update_controls_position()


<<<<<<< HEAD
if __name__ == "_main_":
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = LoginPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)
=======
if __name__ == "__main__":
    random.seed()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LoginPage()
    
    screen = QDesktopWidget().screenGeometry()
    x = (screen.width() - 1300) // 2
    y = (screen.height() - 1000) // 2
    window.setGeometry(x, y, 1300, 1000)
>>>>>>> a2582d3c71e7f17c6c3dd5f953a5cc89f69372b9
    
    window.show()
    sys.exit(app.exec_())