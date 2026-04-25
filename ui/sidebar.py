# ui/sidebar.py
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtGui import QCursor, QFont, QIcon


class SideBar(QFrame):
    profile_clicked = pyqtSignal()
    activity_clicked = pyqtSignal()
    support_clicked = pyqtSignal()
    page_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(90)
        self.setMaximumHeight(650)
        self.setMinimumHeight(450)
        # ✅ الشكل الأصلي - border-radius من جميع الجوانب مع مسافة صغيرة
        self.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1768B3, stop:1 #145CA8);
            border-radius: 25px;
            margin: 20px 0px 20px 20px;
            border: none;
        }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        icons_container = QWidget()
        icons_container.setStyleSheet("background: transparent;")
        
        icons_layout = QVBoxLayout(icons_container)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(15)
        icons_layout.addStretch()
        
        # أيقونة Home
        self.home_btn = QPushButton()
        self.home_btn.setFixedSize(60, 60)
        self.home_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # استخدم صورة
        icon = QIcon("ui/icon/home2.svg")
        self.home_btn.setIcon(icon)
        self.home_btn.setIconSize(QSize(32, 32))
        self.home_btn.setFont(QFont("Segoe UI Emoji", 28))
        self.home_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 30px;
                color: #FFFFFF;
                font-size: 28px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border-radius: 30px;
            }
        """)
        self.home_btn.clicked.connect(lambda: self.page_changed.emit("dashboard"))
        icons_layout.addWidget(self.home_btn, 0, Qt.AlignCenter)
        
        icons_layout.addSpacing(10)
        
        # أيقونة Profile
        self.profile_btn = QPushButton()
        self.profile_btn.setFixedSize(60, 60)
        self.profile_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # استخدم صورة profile.svg (غيري اسم الملف حسب الموجود عندك)
        icon_profile = QIcon("ui/icon/profile.svg")
        self.profile_btn.setIcon(icon_profile)
        self.profile_btn.setIconSize(QSize(32, 32))
        self.profile_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
                color: #FFFFFF;
                font-size: 28px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 30px;
            }
        """)
        self.profile_btn.clicked.connect(self.profile_clicked.emit)
        icons_layout.addWidget(self.profile_btn, 0, Qt.AlignCenter)
        
        icons_layout.addSpacing(10)
        
        # أيقونة Recent Activity
        self.activity_btn = QPushButton()
        self.activity_btn.setFixedSize(60, 60)
        self.activity_btn.setCursor(QCursor(Qt.PointingHandCursor))
        icon_activity = QIcon("ui/icon/activity.svg")
        self.activity_btn.setIcon(icon_activity)
        self.activity_btn.setIconSize(QSize(32, 32))
        self.activity_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 30px;
            }
        """)
        self.activity_btn.clicked.connect(self.activity_clicked.emit)
        icons_layout.addWidget(self.activity_btn, 0, Qt.AlignCenter)
        
        icons_layout.addSpacing(10)
        
        # أيقونة Support
        self.support_btn = QPushButton()
        self.support_btn.setFixedSize(60, 60)
        self.support_btn.setCursor(QCursor(Qt.PointingHandCursor))
        icon_support = QIcon("ui/icon/support.svg")
        self.support_btn.setIcon(icon_support)
        self.support_btn.setIconSize(QSize(32, 32))
        self.support_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 30px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 30px;
            }
        """)
        self.support_btn.clicked.connect(self.support_clicked.emit)
        icons_layout.addWidget(self.support_btn, 0, Qt.AlignCenter)
        
        icons_layout.addSpacing(20)
        
        icons_layout.addStretch()
        main_layout.addWidget(icons_container)
        main_layout.addStretch()
        
        # زر الإعدادات
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
        settings_btn.clicked.connect(lambda: self.page_changed.emit("settings"))
        
        settings_container = QWidget()
        settings_container.setStyleSheet("background: transparent;")
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.addWidget(settings_btn, 0, Qt.AlignCenter)
        
        main_layout.addWidget(settings_container)
        main_layout.addSpacing(20)