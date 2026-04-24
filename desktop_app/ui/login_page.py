# ui/login_page.py
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
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(55)
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
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
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
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            screen = QDesktopWidget().screenGeometry()
            self.setGeometry(screen)
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
        super().resizeEvent(event)
        self.update_controls_position()


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
    
    window.show()
    sys.exit(app.exec_())