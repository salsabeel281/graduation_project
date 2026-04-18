# ui/admin_dashboard.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar, QGridLayout,
    QScrollArea, QSizePolicy, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QSplitter,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QSlider, QSpinBox, QMessageBox, QMenu, QAction,
    QApplication, QDesktopWidget, QSpacerItem, QDialog
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize, QTimer, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon, QBrush, QLinearGradient
import pyqtgraph as pg
from datetime import datetime, timedelta
import numpy as np
import os
import random
import json


# ==================== Card Class ====================
class Card(QFrame):
    def __init__(self, title, value, subtitle="", progress_value=0, parent=None):
        super().__init__(parent)

        self.setObjectName("Card")
        
        self.setStyleSheet("""
            QFrame#Card {
                background: #FFFFFF;
                border-radius: 15px;
                padding: 25px;
                border: 1px solid #E0E0E0;
            }
            QFrame#Card:hover {
                background: #F8F9FA;
                border: 2px solid #4A6FFF;
            }
        """)
        self.setMinimumHeight(230)
        self.setMaximumHeight(230)
        self.setMinimumWidth(300)
        
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # TOP: Large value
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("""
            QLabel {
                background: transparent !important;
                color: #1A237E !important;
                font-size: 30px;
                font-weight: 800;
                margin-bottom: 5px;
            }
        """)
        value_lbl.setFont(QFont("Arial", 42, QFont.Black))
        value_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(value_lbl)

        # MIDDLE: Title
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("""
            QLabel {
                background: transparent !important;
                color: #424242 !important;
                font-size: 14px;
                letter-spacing: 1.2px;
                font-weight: 900;
                margin-bottom: 12px;
            }
        """)
        title_lbl.setFont(QFont("Arial", 12, QFont.Black))
        title_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(title_lbl)

        # BOTTOM: Progress section
        if subtitle or progress_value > 0:
            progress_container = QFrame()
            progress_container.setStyleSheet("""
                QFrame {
                    background: transparent !important;
                }
            """)
            progress_layout = QVBoxLayout(progress_container)
            progress_layout.setContentsMargins(0, 0, 0, 0)
            progress_layout.setSpacing(8)
            
            progress_row = QHBoxLayout()
            progress_row.setSpacing(10)
            
            if subtitle:
                subtitle_lbl = QLabel(subtitle)
                subtitle_lbl.setStyleSheet("""
                    QLabel {
                        background: transparent !important;
                        color: #616161 !important;
                        font-size: 13px;
                        font-weight: 700;
                    }
                """)
                subtitle_lbl.setFont(QFont("Arial", 11, QFont.Bold))
                progress_row.addWidget(subtitle_lbl)
                progress_row.addStretch()
            
            progress_layout.addLayout(progress_row)
            
            if progress_value > 0:
                progress_bar_layout = QHBoxLayout()
                progress_bar_layout.setSpacing(10)
                
                progress_bar = QProgressBar()
                progress_bar.setValue(progress_value)
                progress_bar.setTextVisible(False)
                progress_bar.setFixedHeight(8)
                progress_bar.setStyleSheet("""
                    QProgressBar {
                        background: #E0E0E0 !important;
                        border-radius: 4px;
                        border: none;
                    }
                    QProgressBar::chunk {
                        background: #4A6FFF !important;
                        border-radius: 4px;
                    }
                """)
                
                progress_percentage = QLabel(f"{progress_value}%")
                progress_percentage.setStyleSheet("""
                    QLabel {
                        background: transparent !important;
                        color: #1A237E !important;
                        font-size: 14px;
                        font-weight: 900;
                    }
                """)
                progress_percentage.setFont(QFont("Arial", 12, QFont.Black))
                
                progress_bar_layout.addWidget(progress_bar, 1)
                progress_bar_layout.addWidget(progress_percentage)
                
                progress_layout.addLayout(progress_bar_layout)
            
            layout.addWidget(progress_container)
        
        layout.addStretch()


# ==================== Status Bar ====================
class StatusBar(QFrame):
    """شريط الحالة العلوي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # ===== عنوان Dashboard =====
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        dashboard_title.setStyleSheet("color: white; background: transparent;")
        
        # ===== المسافة لدفع السيرش للنص =====
        layout.addWidget(dashboard_title)
        layout.addStretch(1)
        
        # ===== Search Box =====
        search_container = QFrame()
        search_container.setFixedWidth(450)
        search_container.setFixedHeight(45)
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                border: none;
            }
            QFrame:focus-within {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid #4A6FFF;
            }
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 15))
        search_icon.setStyleSheet("color: #8a9ab0; background: transparent;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: normal;
            }
            QLineEdit::placeholder {
                color: #5a6b7c;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_container)
        layout.addStretch(1)
        
        # ===== أيقونة النوتفيكشن =====
        notification_btn = QPushButton()
        notification_btn.setFixedSize(40, 40)
        notification_btn.setCursor(QCursor(Qt.PointingHandCursor))
        notification_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8a9ab0;
                font-size: 20px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
        notification_btn.setText("🔔")
        notification_btn.setFont(QFont("Segoe UI Emoji", 18))
        
        # ===== صورة المستخدم + الاسم =====
        user_container = QFrame()
        user_container.setCursor(QCursor(Qt.PointingHandCursor))
        user_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-radius: 25px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(8, 4, 12, 4)
        user_layout.setSpacing(10)
        
        # صورة المستخدم (دائرية) - IMPROVED: perfectly centered
        avatar_container = QFrame()
        avatar_container.setFixedSize(38, 38)
        avatar_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A6FFF,
                    stop:1 #6C8CFF
                );
                border-radius: 19px;
                border: 2px solid #FFFFFF;
            }
        """)
        
        # IMPROVED: Better centering for avatar text
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        # الحروف الأولى من الاسم - IMPROVED: perfectly centered text
        avatar_text = QLabel("CH")
        avatar_text.setFont(QFont("Segoe UI", 12, QFont.Bold))
        avatar_text.setAlignment(Qt.AlignCenter)
        avatar_text.setStyleSheet("color: white; background: transparent; padding: 0px; margin: 0px;")
        avatar_layout.addWidget(avatar_text, 0, Qt.AlignCenter)
        
        # اسم المستخدم
        self.user_name = QLabel("Courtney Henry")
        self.user_name.setFont(QFont("Segoe UI", 13, QFont.Medium))
        self.user_name.setStyleSheet("color: white; background: transparent;")
        
        # سهم للأسفل
        dropdown = QLabel("▼")
        dropdown.setFont(QFont("Segoe UI", 9))
        dropdown.setStyleSheet("color: #8a9ab0; background: transparent;")
        
        user_layout.addWidget(avatar_container)
        user_layout.addWidget(self.user_name)
        user_layout.addWidget(dropdown)
        
        layout.addWidget(notification_btn)
        layout.addWidget(user_container)
        layout.addSpacing(10)
    
    def set_user_name(self, name):
        self.user_name.setText(name)
        # تحديث الحروف الأولى
        parts = name.split()
        if len(parts) >= 2:
            initials = parts[0][0] + parts[1][0]
        else:
            initials = name[:2].upper()
        
        # البحث عن avatar container وتحديث النص
        user_container = self.layout().itemAt(self.layout().count()-2).widget()
        if user_container:
            avatar_container = user_container.layout().itemAt(0).widget()
            if avatar_container:
                avatar_text = avatar_container.layout().itemAt(0).widget()
                avatar_text.setText(initials.upper())


# ==================== Profile Sidebar ====================
class ProfileSideBar(QFrame):
    """شريط جانبي للملف الشخصي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(380)
        self.setMaximumHeight(1000)
        self.setMinimumHeight(800)
        
        # إخفاء الشريط في البداية
        self.hide()
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0B1643,
                    stop:0.7 #132456,
                    stop:1 #1A2A5A
                );
                border-radius: 35px;
                margin: 20px 20px 20px 0px;
                border: 2px solid #4A6FFF;
            }
        """)
        
        self.setup_ui()
        
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # ===== رأس الملف الشخصي =====
        header_layout = QHBoxLayout()
        
        title = QLabel("👤 PROFILE")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #4A6FFF; letter-spacing: 1px; background: transparent;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid #4A6FFF;
                border-radius: 17px;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FF5252;
                border-color: #FF5252;
            }
        """)
        close_btn.clicked.connect(self.hide)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # ===== صورة المستخدم - IMPROVED: perfect centering =====
        avatar_container = QFrame()
        avatar_container.setFixedSize(140, 140)
        avatar_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A6FFF,
                    stop:1 #6C8CFF
                );
                border-radius: 70px;
                border: 4px solid #FFFFFF;
            }
        """)
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        self.avatar_emoji = QLabel("👑")
        self.avatar_emoji.setFont(QFont("Segoe UI Emoji", 70))
        self.avatar_emoji.setAlignment(Qt.AlignCenter)
        self.avatar_emoji.setStyleSheet("color: white; background: transparent;")
        avatar_layout.addWidget(self.avatar_emoji, 0, Qt.AlignCenter)
        
        layout.addWidget(avatar_container, 0, Qt.AlignCenter)
        
        # ===== اسم المستخدم =====
        self.name_label = QLabel("Courtney Henry")
        self.name_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #FFFFFF; margin-top: 10px; background: transparent;")
        layout.addWidget(self.name_label)
        
        # ===== البريد الإلكتروني =====
        self.email_label = QLabel("courtney.henry@sentinelx.com")
        self.email_label.setFont(QFont("Segoe UI", 12))
        self.email_label.setAlignment(Qt.AlignCenter)
        self.email_label.setStyleSheet("color: #8A9AB0; margin-bottom: 10px; background: transparent;")
        layout.addWidget(self.email_label)
        
        # ===== Badge =====
        badge = QFrame()
        badge.setFixedSize(130, 35)
        badge.setStyleSheet("""
            QFrame {
                background: rgba(74, 111, 255, 0.2);
                border: 2px solid #4A6FFF;
                border-radius: 17px;
            }
        """)
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(10, 0, 10, 0)
        
        badge_text = QLabel("👑  ADMIN")
        badge_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        badge_text.setStyleSheet("color: #4A6FFF; background: transparent;")
        badge_text.setAlignment(Qt.AlignCenter)
        badge_layout.addWidget(badge_text)
        
        layout.addWidget(badge, 0, Qt.AlignCenter)
        
        # ===== خط فاصل =====
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet("background: rgba(74, 111, 255, 0.3); border-radius: 1px; margin: 15px 0px;")
        layout.addWidget(line)
        
        # ===== بطاقة المعلومات الشخصية =====
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                padding: 20px;
                border: 1px solid #4A6FFF;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(12)
        
        info_title = QLabel("📋 PERSONAL INFORMATION")
        info_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        info_title.setStyleSheet("color: #4A6FFF; margin-bottom: 5px; background: transparent;")
        info_layout.addWidget(info_title)
        
        # ID
        self.id_widget = self.create_info_row("🆔", "User ID", "ADM-2024-001")
        info_layout.addWidget(self.id_widget)
        
        # Department
        self.dept_widget = self.create_info_row("🏢", "Department", "Security Operations")
        info_layout.addWidget(self.dept_widget)
        
        # Role
        self.role_widget = self.create_info_row("👔", "Role", "Administrator")
        info_layout.addWidget(self.role_widget)
        
        # Member Since
        self.member_widget = self.create_info_row("📅", "Member Since", "Jan 2024")
        info_layout.addWidget(self.member_widget)
        
        layout.addWidget(info_card)
        
        # ===== بطاقة الإحصائيات =====
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                padding: 20px;
                border: 1px solid #4A6FFF;
                margin-top: 5px;
            }
        """)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(12)
        
        stats_title = QLabel("📊 ACTIVITY STATS")
        stats_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        stats_title.setStyleSheet("color: #4A6FFF; margin-bottom: 5px; background: transparent;")
        stats_layout.addWidget(stats_title)
        
        # Last Login
        self.last_login_widget = self.create_stat_row("⏱️", "Last Login", "Today 09:30 AM", "#4CAF50")
        stats_layout.addWidget(self.last_login_widget)
        
        # Active Sessions
        self.sessions_widget = self.create_stat_row("💻", "Active Sessions", "3", "#FFC107")
        stats_layout.addWidget(self.sessions_widget)
        
        # New Alerts
        self.alerts_widget = self.create_stat_row("🔔", "New Alerts", "2", "#FF5252")
        stats_layout.addWidget(self.alerts_widget)
        
        # Total Logins
        self.logins_widget = self.create_stat_row("📊", "Total Logins", "147", "#4A6FFF")
        stats_layout.addWidget(self.logins_widget)
        
        layout.addWidget(stats_card)
        
        layout.addStretch()
        
        logout_btn = QPushButton("🚪  LOGOUT")
        logout_btn.setCursor(QCursor(Qt.PointingHandCursor))
        logout_btn.setFixedHeight(55)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5252,
                    stop:1 #FF1744
                );
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF1744,
                    stop:1 #D50000
                );
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
    
    def create_info_row(self, icon, label_text, value_text):
        row = QFrame()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(5, 5, 5, 5)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setStyleSheet("color: #4A6FFF; background: transparent;")
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #8A9AB0; font-size: 12px; background: transparent;")
        
        value = QLabel(value_text)
        value.setObjectName("info_value")
        value.setStyleSheet("""
            QLabel#info_value {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 13px;
                background: rgba(74, 111, 255, 0.15);
                padding: 5px 12px;
                border-radius: 12px;
            }
        """)
        value.setAlignment(Qt.AlignRight)
        
        row_layout.addWidget(icon_label)
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value)
        
        return row
    
    def create_stat_row(self, icon, label_text, value_text, color):
        row = QFrame()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(5, 5, 5, 5)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setStyleSheet("color: #4A6FFF; background: transparent;")
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #8A9AB0; font-size: 12px; background: transparent;")
        
        value = QLabel(value_text)
        value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; background: transparent;")
        value.setAlignment(Qt.AlignRight)
        
        row_layout.addWidget(icon_label)
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value)
        
        return row
    
    def update_profile(self, admin_data):
        self.name_label.setText(admin_data.get('name', 'Courtney Henry'))
        self.email_label.setText(admin_data.get('email', 'courtney.henry@sentinelx.com'))
        
        self.id_widget.layout().itemAt(3).widget().setText(admin_data.get('id', 'ADM001'))
        self.dept_widget.layout().itemAt(3).widget().setText(admin_data.get('department', 'Administration'))
        self.role_widget.layout().itemAt(3).widget().setText(admin_data.get('role', 'Administrator'))
        self.member_widget.layout().itemAt(3).widget().setText(admin_data.get('member_since', 'Jan 2024'))
        
        self.last_login_widget.layout().itemAt(3).widget().setText(admin_data.get('last_login', 'Today 09:30 AM'))
        self.sessions_widget.layout().itemAt(3).widget().setText(str(admin_data.get('sessions', '3')))
        self.alerts_widget.layout().itemAt(3).widget().setText(str(admin_data.get('alerts', '2')))
        self.logins_widget.layout().itemAt(3).widget().setText(str(admin_data.get('total_logins', '147')))
    
    def toggle(self):
        if self.isVisible():
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(0)
            self.animation.finished.connect(self.hide)
            self.animation.start()
        else:
            self.show()
            self.animation.setStartValue(0)
            self.animation.setEndValue(380)
            self.animation.start()
    
    def logout(self):
        reply = QMessageBox.question(
            self, 
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.quit()


# ==================== AnimatedSideBar ====================
class AnimatedSideBar(QFrame):
    """شريط جانبي متحرك بنفس تصميم السايد بار الأصلي"""
    
    profile_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_expanded = True
        self.expanded_width = 90
        self.collapsed_width = 70
        
        self.setFixedWidth(self.expanded_width)
        self.setMaximumHeight(650)
        self.setMinimumHeight(450)

        # نفس التدرج اللوني والتصميم من السايد بار الأصلي
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:0, y2:1,
                    stop:0 #1768B3,
                    stop:1 #145CA8
                );
                border-radius: 25px;
                margin: 20px 0px 20px 20px;
                border: none;
            }
        """)

        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # حاوية للأيقونات في المنتصف
        icons_container = QWidget()
        icons_container.setStyleSheet("background: transparent;")
        
        icons_layout = QVBoxLayout(icons_container)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(15)
        
        # إضافة spacer في الأعلى لدفع الأيقونات لأسفل
        icons_layout.addStretch()
        
        # الأيقونات - نفس التصميم من السايد بار الأصلي
        icon_data = [
            {"name": "home", "text": "🏠", "action": "home", "is_active": True},
            {"name": "briefcase", "text": "💼", "action": "briefcase", "is_active": True},
            {"name": "clock", "text": "⏰", "action": "clock", "is_active": True},
            {"name": "chart", "text": "📊", "action": "chart", "is_active": True},
            {"name": "folder", "text": "📁", "action": "folder", "is_active": True}
        ]

        for icon_info in icon_data:
            # استخدام QPushButton مباشرة
            icon_btn = QPushButton()
            icon_btn.setFixedSize(60, 60)
            icon_btn.setCursor(QCursor(Qt.PointingHandCursor))
            
            # تحميل الصورة إذا وجدت
            icon_path = os.path.join("ui", "icon", f"{icon_info['name']}.svg")
            if os.path.exists(icon_path):
                try:
                    pixmap = QPixmap(icon_path)
                    if not pixmap.isNull():
                        # تلوين الصورة بالأبيض الناصع
                        pixmap = self.colorize_pixmap(pixmap, QColor(255, 255, 255))
                        pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        icon_btn.setIcon(QIcon(pixmap))
                        icon_btn.setIconSize(QSize(30, 30))
                    else:
                        icon_btn.setText(icon_info["text"])
                        icon_btn.setFont(QFont("Segoe UI Emoji", 22))
                except:
                    icon_btn.setText(icon_info["text"])
                    icon_btn.setFont(QFont("Segoe UI Emoji", 22))
            else:
                icon_btn.setText(icon_info["text"])
                icon_btn.setFont(QFont("Segoe UI Emoji", 22))
            
            # نفس الستايل لجميع الأيقونات - أبيض ناصع
            icon_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #FFFFFF;
                    font-size: 24px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 30px;
                }
            """)
            
            # ربط أيقونة الـ home بعرض الملف الشخصي
            if icon_info["action"] == "home":
                icon_btn.clicked.connect(self.profile_clicked.emit)
            
            icons_layout.addWidget(icon_btn, 0, Qt.AlignCenter)

        # إضافة spacer في الأسفل لموازنة المسافات
        icons_layout.addStretch()
        
        # إضافة حاوية الأيقونات في منتصف الـmain layout
        main_layout.addWidget(icons_container)
        
        # إضافة أيقونة الإعدادات في الأسفل
        main_layout.addStretch()
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(50, 50)
        settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                color: #FFFFFF;
            }
        """)
        settings_btn.setFont(QFont("Segoe UI Emoji", 18))
        
        # حاوية لتوسيط أيقونة الإعدادات
        settings_container = QWidget()
        settings_container.setStyleSheet("background: transparent;")
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.addWidget(settings_btn, 0, Qt.AlignCenter)
        
        main_layout.addWidget(settings_container)
        main_layout.addSpacing(20)
    
    def colorize_pixmap(self, pixmap, color):
        """تلوين pixmap بلون معين"""
        try:
            colored = QPixmap(pixmap.size())
            colored.fill(Qt.transparent)
            
            painter = QPainter(colored)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.drawPixmap(0, 0, pixmap)
            
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(colored.rect(), color)
            painter.end()
            
            return colored
        except:
            return pixmap


# ==================== CustomPlotWidget ====================
class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltip = None
        self.lines_info = []
        
    def set_lines_info(self, lines_info):
        self.lines_info = lines_info
        
    def mouseMoveEvent(self, event):
        pos = event.pos()
        view_pos = self.plotItem.vb.mapSceneToView(pos)
        
        closest_line = None
        closest_point = None
        min_distance = float('inf')
        
        for line_info in self.lines_info:
            line = line_info['line']
            data = line_info['data']
            x_data = line_info['x_data']
            name = line_info['name']
            color = line_info['color']
            
            for i in range(len(x_data)):
                point_distance = abs(view_pos.x() - x_data[i]) + abs(view_pos.y() - data[i])
                if point_distance < min_distance:
                    min_distance = point_distance
                    closest_line = name
                    closest_point = (x_data[i], data[i])
        
        if closest_line and min_distance < 0.5:
            if not self.tooltip:
                self.tooltip = QLabel(self)
                self.tooltip.setStyleSheet("""
                    QLabel {
                        background: rgba(11, 22, 67, 0.95);
                        border: 2px solid #4A6FFF;
                        border-radius: 8px;
                        padding: 10px 15px;
                        font-size: 12px;
                        font-weight: bold;
                        color: #FFFFFF;
                    }
                """)
                self.tooltip.setFont(QFont("Segoe UI", 11, QFont.Bold))
            
            hour = int(closest_point[0])
            time_str = f"{hour:02d}:00"
            
            self.tooltip.setText(f"📊 {closest_line}\n⏰ {time_str}\n📈 {closest_point[1]:.1f}")
            self.tooltip.adjustSize()
            
            tooltip_pos = pos + QPoint(20, 20)
            self.tooltip.move(tooltip_pos)
            self.tooltip.show()
        elif self.tooltip:
            self.tooltip.hide()
        
        super().mouseMoveEvent(event)


# ==================== AdminDashboard ====================
class AdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelX - Admin Control Panel")
        self.resize(1600, 1000)

        self.setStyleSheet("""
            QMainWindow {
                background: #0B1643;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ========= Sidebar متحرك =========
        self.sidebar = AnimatedSideBar(self)
        self.sidebar.profile_clicked.connect(self.toggle_profile_sidebar)
        main_layout.addWidget(self.sidebar)
        
        # ========= Profile Sidebar =========
        self.profile_sidebar = ProfileSideBar(self)
        main_layout.addWidget(self.profile_sidebar)

        # ========= Content with Scroll =========
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: #0B1643;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #4A6FFF;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar:horizontal {
                background: rgba(255, 255, 255, 0.1);
                height: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background: #4A6FFF;
                border-radius: 7px;
                min-width: 30px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: #0B1643;")
        scroll_area.setWidget(content_widget)
        
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)

        # ========= Status Bar =========
        self.status_bar = StatusBar()
        self.content_layout.addWidget(self.status_bar)
        
        # ========= Stats Cards =========
        self.setup_stats_cards()
        
        # ========= Users Table =========
        self.setup_users_section()
        
        # ========= Charts Section =========
        self.setup_charts_section()

        main_layout.addWidget(scroll_area)

        # Generate data
        self.users_data = self.generate_users_data()
        self.behavior_data = self.generate_behavior_data()
        
        # بيانات الأدمن
        self.admin_data = {
            'name': 'Courtney Henry',
            'email': 'courtney.henry@sentinelx.com',
            'id': 'ADM-2024-001',
            'department': 'Security Operations',
            'role': 'Administrator',
            'member_since': 'Jan 2024',
            'last_login': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'sessions': 3,
            'alerts': 2,
            'total_logins': 147
        }
        
        # تحديث الملف الشخصي
        self.profile_sidebar.update_profile(self.admin_data)
        self.status_bar.set_user_name("Courtney Henry")
        
        # ملء الجدول بالبيانات
        self.refresh_users_table()
    
    def toggle_profile_sidebar(self):
        """تبديل ظهور شريط الملف الشخصي"""
        self.profile_sidebar.toggle()

    def setup_stats_cards(self):
        """كروت الإحصائيات"""
        stats_label = QLabel("📊 SYSTEM OVERVIEW")
        stats_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        stats_label.setStyleSheet("color: white; margin-bottom: 20px;")
        self.content_layout.addWidget(stats_label)
       
        cards_container = QWidget()
        cards_container.setStyleSheet("background: transparent;")
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(20)
        
        # Row 1
        card1 = Card("Total Users", "1,284", "Active: 847", 72, self)
        card2 = Card("Active Sessions", "847", "Peak: 1,024", 68, self)
        card3 = Card("Threats Blocked", "2,391", "Last 24h", 84, self)
        card4 = Card("Avg Risk Score", "23.4", "Low Risk", 23, self)
        
        cards_layout.addWidget(card1, 0, 0)
        cards_layout.addWidget(card2, 0, 1)
        cards_layout.addWidget(card3, 0, 2)
        cards_layout.addWidget(card4, 0, 3)
        
        # Row 2
        card5 = Card("Database Server", "99.9%", "Uptime", 99, self)
        card6 = Card("ML Engine", "95%", "Performance", 95, self)
        card7 = Card("Alert System", "98.5%", "Reliability", 98, self)
        card8 = Card("Storage", "87%", "Capacity", 87, self)
        
        cards_layout.addWidget(card5, 1, 0)
        cards_layout.addWidget(card6, 1, 1)
        cards_layout.addWidget(card7, 1, 2)
        cards_layout.addWidget(card8, 1, 3)
        
        self.content_layout.addWidget(cards_container)

    def setup_users_section(self):
        """قسم المستخدمين"""
        section_title = QWidget()
        title_layout = QHBoxLayout(section_title)
        title_layout.setContentsMargins(0, 20, 0, 15)
        
        title = QLabel("👥 USER MANAGEMENT")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        # عداد المستخدمين
        count_badge = QFrame()
        count_badge.setFixedSize(45, 45)
        count_badge.setStyleSheet("""
            QFrame {
                background: #4A6FFF;
                border-radius: 22px;
            }
        """)
        count_layout = QVBoxLayout(count_badge)
        self.count_label = QLabel("21")
        self.count_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.count_label.setStyleSheet("color: white;")
        self.count_label.setAlignment(Qt.AlignCenter)
        count_layout.addWidget(self.count_label)
        
        # Label للنتائج
        self.results_label = QLabel("📊 Showing all 21 users")
        self.results_label.setFont(QFont("Segoe UI", 11))
        self.results_label.setStyleSheet("color: #8a9ab0; margin-left: 20px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(count_badge)
        title_layout.addWidget(self.results_label)
        title_layout.addStretch()
        
        self.content_layout.addWidget(section_title)
        
        # Toolbar
        self.setup_toolbar()
        
        # Table
        self.setup_users_table()

    def setup_toolbar(self):
        """شريط الأدوات للبحث والفلترة"""
        toolbar = QFrame()
        toolbar.setFixedHeight(70)
        toolbar.setStyleSheet("""
            QFrame {
                background: transparent;
                margin-bottom: 20px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # ===== مربع البحث - NOW EXACTLY MATCHING StatusBar =====
        search_container = QFrame()
        search_container.setFixedWidth(450)  # نفس عرض الـ Status Bar
        search_container.setFixedHeight(45)   # نفس ارتفاع الـ Status Bar
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                border: none;
            }
            QFrame:focus-within {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid #4A6FFF;
            }
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 15))
        search_icon.setStyleSheet("color: #8a9ab0; background: transparent;")
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by name, department...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: normal;
            }
            QLineEdit::placeholder {
                color: #5a6b7c;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.search_box.textChanged.connect(self.filter_users)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_box)
        
        # ===== قائمة الفلتر =====
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Users", "Active", "Suspended", "High Risk"])
        self.filter_combo.setFixedHeight(40)
        self.filter_combo.setMinimumWidth(130)
        self.filter_combo.setMaximumWidth(160)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                color: white;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8a9ab0;
                margin-right: 5px;
            }
            QComboBox:hover {
                background: rgba(255, 255, 255, 0.12);
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_users)
        
        # ===== زر الإضافة =====
        self.add_btn = QPushButton("➕ Add User")
        self.add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_btn.setFixedHeight(40)
        self.add_btn.setMinimumWidth(110)
        self.add_btn.setMaximumWidth(130)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #4A6FFF;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #5A7FFF;
            }
        """)
        self.add_btn.clicked.connect(self.show_add_user_dialog)
        
        # IMPORTANT: نفس الترتيب والتباعد
        layout.addWidget(search_container)  # العرض ثابت 450px
        layout.addWidget(self.filter_combo)
        layout.addStretch()  # دفع الباقي لليمين
        layout.addWidget(self.add_btn)
        
        self.content_layout.addWidget(toolbar)

    def setup_users_table(self):
        """جدول المستخدمين"""
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Department", "Risk Score", 
            "Threat Level", "Status", "Last Active", "Actions"
        ])
        
        self.users_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.users_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid #2a3a5a;
                border-radius: 15px;
                color: white;
                gridline-color: #2a3a5a;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #2a3a5a;
            }
            QTableWidget::item:selected {
                background: #4A6FFF40;
            }
            QHeaderView::section {
                background: #1a2a4a;
                color: #8a9ab0;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.verticalHeader().setVisible(False)
        
        self.users_table.setFixedHeight(400)
        
        self.users_table.cellClicked.connect(self.on_user_selected)
        
        self.content_layout.addWidget(self.users_table)

    def setup_charts_section(self):
        """قسم الشارتات"""
        charts_label = QLabel("📈 BEHAVIORAL ANALYTICS")
        charts_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        charts_label.setStyleSheet("color: white; margin-top: 30px; margin-bottom: 20px;")
        self.content_layout.addWidget(charts_label)

        self.chart_tabs = QTabWidget()
        self.chart_tabs.setStyleSheet("""
            QTabWidget::pane {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid #2a3a5a;
                border-radius: 15px;
                padding: 20px;
            }
            QTabBar::tab {
                background: transparent;
                color: #8a9ab0;
                padding: 15px 30px;
                margin-right: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4A6FFF;
                color: white;
                border-radius: 8px;
            }
            QTabBar::tab:hover {
                background: rgba(74, 111, 255, 0.3);
                color: white;
            }
        """)

        main_chart_tab = self.create_main_chart()
        self.chart_tabs.addTab(main_chart_tab, "📊 All Users Behavior")

        risk_tab = self.create_risk_chart()
        self.chart_tabs.addTab(risk_tab, "⚠️ Risk Analysis")

        activity_tab = self.create_activity_chart()
        self.chart_tabs.addTab(activity_tab, "📅 Activity Heatmap")

        self.content_layout.addWidget(self.chart_tabs)

    def create_main_chart(self):
        """الشارت الرئيسي"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("User Behavioral Metrics Over Time (Last 24 Hours)")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 15px;")
        layout.addWidget(title)
        
        chart = CustomPlotWidget()
        chart.setMinimumHeight(450)
        chart.setBackground('#0B1643')
        chart.showGrid(x=True, y=True, alpha=0.2)
        
        axis_bottom = chart.getAxis('bottom')
        axis_left = chart.getAxis('left')
        axis_bottom.setPen(pg.mkPen(color='white', width=2))
        axis_left.setPen(pg.mkPen(color='white', width=2))
        axis_bottom.setTextPen('white')
        axis_left.setTextPen('white')
        axis_bottom.setStyle(tickFont=QFont("Segoe UI", 11))
        axis_left.setStyle(tickFont=QFont("Segoe UI", 11))
        
        hours = np.arange(0, 24, 0.1)
        typing_speed = 65 + 20 * np.sin(hours/3) + 10 * np.cos(hours/2)
        mouse_speed = 3.5 + 1.5 * np.sin(hours/2.5) + 0.8 * np.cos(hours/1.8) * 10
        click_freq = 3.0 + 3 * np.sin(hours/2) + 2 * np.cos(hours/1.5) * 10
        
        line1 = chart.plot(hours, typing_speed, pen=pg.mkPen("#4A6FFF", width=4), name="Typing Speed (WPM)")
        line2 = chart.plot(hours, mouse_speed, pen=pg.mkPen("#4CAF50", width=4), name="Mouse Speed (px/s)")
        line3 = chart.plot(hours, click_freq, pen=pg.mkPen("#FF5252", width=4), name="Click Frequency")
        
        lines_info = [
            {'line': line1, 'data': typing_speed, 'x_data': hours, 'name': 'Typing Speed', 'color': '#4A6FFF'},
            {'line': line2, 'data': mouse_speed, 'x_data': hours, 'name': 'Mouse Speed', 'color': '#4CAF50'},
            {'line': line3, 'data': click_freq, 'x_data': hours, 'name': 'Click Frequency', 'color': '#FF5252'}
        ]
        
        chart.set_lines_info(lines_info)
        chart.setXRange(-1, 24)
        chart.setYRange(0, 100)
        axis_bottom.setTicks([[(i, f"{i}:00") for i in range(0, 24, 2)]])
        
        legend = chart.addLegend()
        legend.brush = pg.mkBrush(color=(11, 22, 67, 200))
        legend.setPen(pg.mkPen(color='white', width=1))
        legend.setLabelTextColor('white')
        
        chart.setLabel('bottom', 'Hour of Day', color='white', **{'font-size': '12pt'})
        chart.setLabel('left', 'Value', color='white', **{'font-size': '12pt'})
        
        avg_line = pg.InfiniteLine(pos=50, angle=0, pen=pg.mkPen(color='white', style=Qt.DashLine, width=2))
        chart.addItem(avg_line)
        
        layout.addWidget(chart)
        
        info_text = QLabel("Hover over lines to see exact values • Average line (dashed) at 50%")
        info_text.setFont(QFont("Segoe UI", 11))
        info_text.setStyleSheet("color: #8a9ab0; margin-top: 10px;")
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        
        return tab

    def create_risk_chart(self):
        """تحليل المخاطر"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Threat Analysis - Last 30 Days")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 15px;")
        layout.addWidget(title)
        
        chart = pg.PlotWidget()
        chart.setMinimumHeight(400)
        chart.setBackground('#0B1643')
        
        days = np.arange(1, 31)
        low_risk = np.random.randint(20, 40, 30)
        medium_risk = np.random.randint(10, 25, 30)
        high_risk = np.random.randint(0, 15, 30)
        
        bg1 = pg.BarGraphItem(x=days, height=low_risk, width=0.6, brush='#4CAF50', name="Low Risk")
        bg2 = pg.BarGraphItem(x=days, height=medium_risk, width=0.6, brush='#FFC107', name="Medium Risk", bottom=low_risk)
        bg3 = pg.BarGraphItem(x=days, height=high_risk, width=0.6, brush='#FF5252', name="High Risk", bottom=low_risk+medium_risk)
        
        chart.addItem(bg1)
        chart.addItem(bg2)
        chart.addItem(bg3)
        
        chart.getAxis('bottom').setPen(pg.mkPen(color='white', width=2))
        chart.getAxis('left').setPen(pg.mkPen(color='white', width=2))
        chart.getAxis('bottom').setTextPen('white')
        chart.getAxis('left').setTextPen('white')
        chart.getAxis('bottom').setStyle(tickFont=QFont("Segoe UI", 10))
        chart.getAxis('left').setStyle(tickFont=QFont("Segoe UI", 10))
        
        chart.setLabel('bottom', 'Day of Month', color='white', **{'font-size': '11pt'})
        chart.setLabel('left', 'Number of Threats', color='white', **{'font-size': '11pt'})
        
        legend = chart.addLegend()
        legend.brush = pg.mkBrush(color=(11, 22, 67, 200))
        legend.setPen(pg.mkPen(color='white', width=1))
        legend.setLabelTextColor('white')
        
        layout.addWidget(chart)
        return tab

    def create_activity_chart(self):
        """خريطة النشاط"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Weekly Activity Heatmap")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 15px;")
        layout.addWidget(title)
        
        chart = pg.PlotWidget()
        chart.setMinimumHeight(400)
        chart.setBackground('#0B1643')
        
        activity = np.random.randint(0, 100, (24, 7))
        
        img = pg.ImageItem()
        img.setImage(activity.T)
        img.setRect(0, 0, 24, 7)
        
        colors = [
            (0, 0, 0, 0),
            (0, 255, 0, 150),
            (255, 255, 0, 200),
            (255, 0, 0, 250)
        ]
        cmap = pg.ColorMap(np.linspace(0, 1, 4), colors)
        img.setLookupTable(cmap.getLookupTable())
        
        chart.addItem(img)
        
        chart.getAxis('bottom').setPen(pg.mkPen(color='white', width=2))
        chart.getAxis('left').setPen(pg.mkPen(color='white', width=2))
        chart.getAxis('bottom').setTextPen('white')
        chart.getAxis('left').setTextPen('white')
        chart.getAxis('bottom').setStyle(tickFont=QFont("Segoe UI", 11))
        chart.getAxis('left').setStyle(tickFont=QFont("Segoe UI", 11))
        
        chart.setLabel('bottom', 'Hour of Day', color='white', **{'font-size': '12pt'})
        chart.setLabel('left', 'Day of Week', color='white', **{'font-size': '12pt'})
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        axis_left = chart.getAxis('left')
        axis_left.setTicks([[(i, days[i]) for i in range(7)]])
        
        axis_bottom = chart.getAxis('bottom')
        axis_bottom.setTicks([[(i, f"{i}:00") for i in range(0, 24, 2)]])
        
        layout.addWidget(chart)
        
        legend_widget = QFrame()
        legend_widget.setFixedHeight(40)
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setContentsMargins(0, 10, 0, 0)
        
        for color, text in [("#4CAF50", "Low"), ("#FFC107", "Medium"), ("#FF5252", "High")]:
            item = QFrame()
            item.setFixedSize(20, 20)
            item.setStyleSheet(f"background: {color}; border-radius: 3px;")
            
            label = QLabel(text)
            label.setStyleSheet("color: white; font-size: 11px;")
            
            legend_layout.addWidget(item)
            legend_layout.addWidget(label)
            legend_layout.addSpacing(15)
        
        legend_layout.addStretch()
        layout.addWidget(legend_widget)
        
        return tab

    # ==================== دوال المستخدمين ====================

    def filter_users(self):
        """تصفية المستخدمين حسب البحث والفلتر"""
        # التحقق من وجود search_box
        if not hasattr(self, 'search_box'):
            return
            
        search_text = self.search_box.text().lower().strip()
        filter_type = self.filter_combo.currentText()
        
        visible_count = 0
        for row in range(self.users_table.rowCount()):
            show_row = True
            
            username = self.users_table.item(row, 1).text().lower()
            department = self.users_table.item(row, 2).text().lower()
            
            # فلتر البحث
            if search_text:
                if search_text not in username and search_text not in department:
                    show_row = False
            
            # فلتر الحالة
            if show_row and filter_type != "All Users":
                status = self.users_table.item(row, 5).text()
                if filter_type == "Active" and status != "Active":
                    show_row = False
                elif filter_type == "Suspended" and status != "Suspended":
                    show_row = False
                elif filter_type == "High Risk":
                    risk_text = self.users_table.item(row, 3).text()
                    risk = int(risk_text.replace('%', ''))
                    if risk < 70:
                        show_row = False
            
            self.users_table.setRowHidden(row, not show_row)
            if show_row:
                visible_count += 1
        
        # تحديث ارتفاع الجدول
        if visible_count > 0:
            row_height = self.users_table.rowHeight(0)
            new_height = (visible_count * row_height) + 50
            self.users_table.setFixedHeight(min(new_height, 600))
        else:
            self.users_table.setFixedHeight(100)
        
        self.update_results_count(visible_count)

    def update_results_count(self, count):
        """تحديث عداد النتائج"""
        total = self.users_table.rowCount()
        search_text = self.search_box.text() if hasattr(self, 'search_box') else ""
        
        if search_text:
            self.results_label.setText(f"📊 Found {count} users matching '{search_text}'")
        else:
            filter_type = self.filter_combo.currentText()
            if filter_type == "All Users":
                self.results_label.setText(f"📊 Showing all {total} users")
            else:
                self.results_label.setText(f"📊 Showing {count} {filter_type} users")

    def show_add_user_dialog(self):
        """نافذة إضافة مستخدم جديد - IMPROVED: consistent spacing and alignment"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setFixedSize(600, 750)
        
        dialog.setStyleSheet("""
            QDialog {
                background: #0B1643;
                border: 2px solid #4A6FFF;
                border-radius: 25px;
            }
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            QLineEdit, QComboBox {
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid #3a4a6a;
                border-radius: 12px;
                padding: 12px 16px;
                color: white;
                font-size: 14px;
                min-height: 44px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4A6FFF;
                background: rgba(74, 111, 255, 0.1);
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 10px;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                min-height: 48px;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)  # Consistent vertical spacing
        
        title = QLabel("➕ ADD NEW USER")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4A6FFF; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.dialog_inputs = {}
        
        # Organized field definitions with consistent styling
        fields = [
            ("👤 Full Name", "text", "Enter full name"),
            ("📧 Email Address", "text", "Enter email address"),
            ("🏢 Department", "combo", ""),
            ("👔 Role", "combo", ""),
            ("🔑 Password", "password", "Enter password (min 6 characters)"),
            ("🔒 Confirm Password", "password", "Confirm your password")
        ]
        
        combo_options = {
            "🏢 Department": ["Engineering", "Sales", "Marketing", "HR", "Finance", "IT", "Operations"],
            "👔 Role": ["User", "Manager", "Admin", "Viewer"]
        }
        
        for label_text, field_type, placeholder in fields:
            # Better label spacing
            label = QLabel(label_text)
            label.setFont(QFont("Segoe UI", 13, QFont.Bold))
            label.setStyleSheet("margin-top: 5px;")
            layout.addWidget(label)
            
            if field_type == "combo":
                combo = QComboBox()
                combo.addItems(combo_options[label_text])
                combo.setMinimumHeight(44)
                self.dialog_inputs[label_text] = combo
                layout.addWidget(combo)
            else:
                line_edit = QLineEdit()
                if field_type == "password":
                    line_edit.setEchoMode(QLineEdit.Password)
                if placeholder:
                    line_edit.setPlaceholderText(placeholder)
                line_edit.setMinimumHeight(44)
                self.dialog_inputs[label_text] = line_edit
                layout.addWidget(line_edit)
        
        layout.addSpacing(20)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #FF5252;
                color: #FF5252;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FF5252;
                color: white;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Save User")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setMinimumHeight(48)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border: none;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_new_user(dialog))
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.center_dialog(dialog)
        dialog.exec_()

    def save_new_user(self, dialog):
        """حفظ المستخدم الجديد"""
        name = self.dialog_inputs["👤 Full Name"].text().strip()
        email = self.dialog_inputs["📧 Email Address"].text().strip()
        password = self.dialog_inputs["🔑 Password"].text()
        confirm = self.dialog_inputs["🔒 Confirm Password"].text()
        
        if not name:
            QMessageBox.warning(dialog, "Error", "Please enter full name")
            return
        
        if not email or '@' not in email:
            QMessageBox.warning(dialog, "Error", "Please enter valid email")
            return
        
        if password != confirm:
            QMessageBox.warning(dialog, "Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(dialog, "Error", "Password must be at least 6 characters")
            return
        
        new_user = {
            'id': len(self.users_data) + 1,
            'name': name,
            'email': email,
            'department': self.dialog_inputs["🏢 Department"].currentText(),
            'role': self.dialog_inputs["👔 Role"].currentText(),
            'risk_score': random.randint(5, 30),
            'threat_level': random.randint(0, 20),
            'status': 'Active',
            'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'alerts_count': 0
        }
        
        self.users_data.append(new_user)
        self.refresh_users_table()
        
        QMessageBox.information(dialog, "Success", f"User {name} added successfully!")
        dialog.accept()

    def refresh_users_table(self):
        """تحديث جدول المستخدمين"""
        self.users_table.setRowCount(0)
        self.users_table.setRowCount(len(self.users_data))
        
        for row, user in enumerate(self.users_data):
            id_item = QTableWidgetItem(str(user['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            
            name_item = QTableWidgetItem(user['name'])
            name_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            
            dept_item = QTableWidgetItem(user['department'])
            
            risk = user['risk_score']
            risk_item = QTableWidgetItem(f"{risk}%")
            risk_item.setTextAlignment(Qt.AlignCenter)
            risk_color = "#4CAF50" if risk < 30 else "#FFC107" if risk < 60 else "#FF5252"
            risk_item.setForeground(QBrush(QColor(risk_color)))
            
            threat = user['threat_level']
            threat_item = QTableWidgetItem(f"{threat}%")
            threat_item.setTextAlignment(Qt.AlignCenter)
            threat_color = "#4CAF50" if threat < 30 else "#FFC107" if threat < 60 else "#FF5252"
            threat_item.setForeground(QBrush(QColor(threat_color)))
            
            status_item = QTableWidgetItem(user['status'])
            status_color = "#4CAF50" if user['status'] == "Active" else "#FF5252" if user['status'] == "Suspended" else "#FFC107"
            status_item.setForeground(QBrush(QColor(status_color)))
            
            last_active_item = QTableWidgetItem(user['last_active'])
            
            actions_item = QTableWidgetItem("⚙️ Manage")
            actions_item.setForeground(QBrush(QColor("#4A6FFF")))
            
            self.users_table.setItem(row, 0, id_item)
            self.users_table.setItem(row, 1, name_item)
            self.users_table.setItem(row, 2, dept_item)
            self.users_table.setItem(row, 3, risk_item)
            self.users_table.setItem(row, 4, threat_item)
            self.users_table.setItem(row, 5, status_item)
            self.users_table.setItem(row, 6, last_active_item)
            self.users_table.setItem(row, 7, actions_item)
        
        self.users_table.resizeColumnsToContents()
        
        row_height = self.users_table.rowHeight(0) if self.users_table.rowCount() > 0 else 30
        total_height = (self.users_table.rowCount() * row_height) + 50
        self.users_table.setFixedHeight(min(total_height, 600))
        
        self.count_label.setText(str(len(self.users_data)))
        self.update_results_count(len(self.users_data))

    def on_user_selected(self, row, column):
        """عند اختيار مستخدم"""
        if column == 7:  # Actions column
            user_name = self.users_table.item(row, 1).text()
            user_id = self.users_table.item(row, 0).text()
            user_dept = self.users_table.item(row, 2).text()
            user_risk = self.users_table.item(row, 3).text()
            user_status = self.users_table.item(row, 5).text()
            
            QMessageBox.information(
                self, 
                "👤 User Details",
                f"📋 User Information:\n\n"
                f"🆔 ID: {user_id}\n"
                f"👤 Name: {user_name}\n"
                f"🏢 Department: {user_dept}\n"
                f"📊 Risk Score: {user_risk}\n"
                f"🔴 Status: {user_status}"
            )

    def generate_users_data(self):
        """توليد بيانات تجريبية"""
        users = []
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "IT", "Operations"]
        first_names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "James", "Maria", "Robert", "Jennifer"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        for i in range(1, 21):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            status = random.choice(["Active", "Active", "Active", "Inactive", "Suspended"])
            
            users.append({
                'id': i,
                'name': name,
                'email': f"{name.lower().replace(' ', '.')}@company.com",
                'department': random.choice(departments),
                'risk_score': random.randint(5, 95),
                'threat_level': random.randint(0, 100),
                'status': status,
                'last_active': (datetime.now() - timedelta(minutes=random.randint(0, 1440))).strftime("%Y-%m-%d %H:%M"),
                'alerts_count': random.randint(0, 10)
            })
        
        # إضافة John Garcia للاختبار
        users.append({
            'id': len(users) + 1,
            'name': "John Garcia",
            'email': "john.garcia@company.com",
            'department': "Engineering",
            'risk_score': 45,
            'threat_level': 30,
            'status': "Active",
            'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'alerts_count': 2
        })
        
        return users

    def generate_behavior_data(self):
        """توليد بيانات سلوك"""
        hours = np.arange(0, 24, 0.5)
        return {
            'hours': hours.tolist(),
            'typing': (65 + 20 * np.sin(hours/3) + 10 * np.cos(hours/2)).tolist(),
            'mouse': (3.5 + 1.5 * np.sin(hours/2.5) + 0.8 * np.cos(hours/1.8)).tolist(),
            'clicks': (3.0 + 3 * np.sin(hours/2) + 2 * np.cos(hours/1.5)).tolist()
        }

    def center_dialog(self, dialog):
        """توسيط نافذة الحوار"""
        parent_geo = self.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog.height()) // 2
        dialog.move(x, y)


# if __name__ == "__main__":
#     import sys
#     app = QApplication(sys.argv)
#     window = AdminDashboard()
    
#     screen = QDesktopWidget().screenGeometry()
#     x = (screen.width() - window.width()) // 2
#     y = (screen.height() - window.height()) // 2
#     window.move(x, y)
    
#     window.show()
#     sys.exit(app.exec_())
