# ui/support_sidemenu.py
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QScrollArea, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QCursor


class SupportSideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SupportSideMenu")
        
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QFrame#SupportSideMenu {
                background: #0a1628;
                border-right: 1px solid #1a2a4a;
            }
        """)
        
        self.init_ui()
        self.hide()
    
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
        
        title = QLabel("Support")
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
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #0a1628;
                border: none;
            }
            QScrollBar:vertical {
                background: #0d1a30;
                width: 4px;
                border-radius: 2px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2a4a7a;
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3a5a8a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: #0a1628;")
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 24, 0, 24)
        content_layout.setSpacing(16)
        
        # Contact methods - كل واحد في صف منفصل (عمودي)
        contact_items = [
            ("Email Support", "support@sentinelx.com"),
            ("Phone Support", "+1 (555) 123-4567"),
            ("Website", "www.sentinelx.com"),
            ("Live Chat", "Available 24/7"),
            ("Discord", "discord.gg/sentinelx"),
        ]
        
        for label, value in contact_items:
            content_layout.addWidget(self.create_contact_item(label, value))
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #1a2a4a; margin: 8px 20px;")
        content_layout.addWidget(separator)
        
        # Message section
        msg_title = QLabel("Send us a message")
        msg_title.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        msg_title.setStyleSheet("color: #e0e0e0; margin: 8px 20px 0 20px;")
        content_layout.addWidget(msg_title)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background: #0d1a30;
                border: 1px solid #2a4a7a;
                border-radius: 8px;
                color: #e0e0e0;
                font-size: 12px;
                padding: 10px;
                margin: 0px 20px;
            }
            QTextEdit:focus {
                border-color: #4a9eff;
            }
        """)
        content_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("Send message")
        send_btn.setCursor(QCursor(Qt.PointingHandCursor))
        send_btn.setFixedHeight(44)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #1a2a4a;
                border-radius: 8px;
                color: #6a9acc;
                font-size: 13px;
                font-weight: 500;
                margin: 8px 20px 0 20px;
            }
            QPushButton:hover {
                background: #2a3a5a;
                color: #ffffff;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        content_layout.addWidget(send_btn)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_contact_item(self, label, value):
        """كل عنصر يكون عمودي (العنوان فوق القيمة)"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #0d1a30;
                border-radius: 8px;
                margin: 0px 20px;
            }
            QWidget:hover {
                background: #122340;
            }
        """)
        
        container.setFixedHeight(70)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # العنوان
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        label_widget.setStyleSheet("color: #6a9acc;")
        layout.addWidget(label_widget)
        
        # القيمة
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Segoe UI", 12))
        value_widget.setStyleSheet("color: #e0e0e0;")
        value_widget.setWordWrap(True)
        layout.addWidget(value_widget)
        
        return container
    
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            print(f"Message sent: {message}")
            self.message_input.clear()
        else:
            print("Message is empty")
    
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