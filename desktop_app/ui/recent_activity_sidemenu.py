# ui/recent_activity_sidemenu.py
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QCursor
from datetime import datetime, timedelta


class RecentActivitySideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecentActivitySideMenu")
        
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QFrame#RecentActivitySideMenu {
                background: #0a1628;
                border-right: 1px solid #1a2a4a;
            }
        """)
        
        self.activities = self.generate_activities()
        self.init_ui()
        self.hide()
    
    def generate_activities(self):
        now = datetime.now()
        return [
            {"title": "Login", "desc": "New sign-in from Chrome on Windows", "time": now - timedelta(minutes=5), "type": "auth"},
            {"title": "Typing anomaly", "desc": "Unusual pattern detected", "time": now - timedelta(minutes=15), "type": "alert"},
            {"title": "File accessed", "desc": "report.pdf opened", "time": now - timedelta(minutes=45), "type": "file"},
            {"title": "Scan completed", "desc": "No threats found", "time": now - timedelta(hours=1), "type": "success"},
            {"title": "ML model updated", "desc": "Behavioral patterns retrained", "time": now - timedelta(hours=2), "type": "system"},
            {"title": "Threat blocked", "desc": "Malware quarantined", "time": now - timedelta(hours=3), "type": "alert"},
            {"title": "App launched", "desc": "Visual Studio Code", "time": now - timedelta(hours=4), "type": "app"},
            {"title": "Security level up", "desc": "Level 2 → Level 3", "time": now - timedelta(hours=5), "type": "auth"},
            {"title": "Weekly report", "desc": "Sent to admin", "time": now - timedelta(hours=6), "type": "system"}
        ]
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet("background: #0a1628; border-bottom: 1px solid #1a2a4a;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 20, 0)
        
        title = QLabel("Activity")
        title.setFont(QFont("Segoe UI", 16, QFont.DemiBold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border-radius: 6px;
                color: #5a7a9a;
                font-size: 13px;
                font-weight: normal;
            }
            QPushButton:hover {
                background: #1a2a4a;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.hide_menu)
        header_layout.addWidget(close_btn)
        main_layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #0a1628;
                border: none;
            }
            QScrollBar:vertical {
                background: #0d1a30;
                width: 4px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #2a4a7a;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a5a8a;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: #0a1628;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 16, 0, 24)
        content_layout.setSpacing(2)
        
        for activity in self.activities:
            content_layout.addWidget(self.create_activity_item(activity))
        
        content_layout.addStretch()
        
        # View all button
        view_all = QPushButton("View all")
        view_all.setCursor(QCursor(Qt.PointingHandCursor))
        view_all.setFixedHeight(40)
        view_all.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #1a3a5a;
                border-radius: 8px;
                color: #6a9acc;
                font-size: 12px;
                font-weight: 500;
                margin: 8px 20px 0 20px;
            }
            QPushButton:hover {
                background: #0d1a30;
                border-color: #2a5a8a;
                color: #ffffff;
            }
        """)
        content_layout.addWidget(view_all)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_activity_item(self, activity):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                border-radius: 8px;
                margin: 0px 12px;
            }
            QWidget:hover {
                background: #0d1a30;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)
        
        # Dot indicator based on type (instead of icons)
        dot = QLabel("●")
        dot.setFixedSize(8, 8)
        dot.setAlignment(Qt.AlignCenter)
        
        color_map = {
            "auth": "#4a9eff",
            "alert": "#ff6b4a",
            "file": "#4affb5",
            "success": "#4aff6b",
            "system": "#ffd64a",
            "app": "#ff6bcb"
        }
        dot_color = color_map.get(activity["type"], "#4a9eff")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 8px;")
        layout.addWidget(dot)
        layout.addSpacing(12)
        
        # Text content
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        # Title row with time
        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(8)
        
        title_label = QLabel(activity["title"])
        title_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        title_label.setStyleSheet("color: #e0e0e0;")
        title_row_layout.addWidget(title_label)
        title_row_layout.addStretch()
        
        time_label = QLabel(self.format_time(activity["time"]))
        time_label.setFont(QFont("Segoe UI", 10))
        time_label.setStyleSheet("color: #5a7a9a;")
        title_row_layout.addWidget(time_label)
        
        text_layout.addWidget(title_row)
        
        desc_label = QLabel(activity["desc"])
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #8a9aaa;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        layout.addWidget(text_widget, 1)
        
        return container
    
    def format_time(self, dt):
        now = datetime.now()
        diff = now - dt
        
        if diff.seconds < 60:
            return f"{diff.seconds}s ago"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        elif diff.days == 0:
            return f"{diff.seconds // 3600}h ago"
        else:
            return dt.strftime("%b %d")
    
    def show_menu(self):
        self.show()
        self.raise_()
        parent = self.parent()
        if parent:
            sidebar_width = 90
            self.animation = QPropertyAnimation(self, b"pos")
            self.animation.setDuration(280)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.setStartValue(QPoint(-self.width(), 0))
            self.animation.setEndValue(QPoint(sidebar_width, 0))
            self.animation.start()
    
    def hide_menu(self):
        parent = self.parent()
        if parent:
            sidebar_width = 90
            self.animation = QPropertyAnimation(self, b"pos")
            self.animation.setDuration(260)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.setStartValue(QPoint(sidebar_width, 0))
            self.animation.setEndValue(QPoint(-self.width(), 0))
            self.animation.finished.connect(self.hide)
            self.animation.start()
        else:
            self.hide()