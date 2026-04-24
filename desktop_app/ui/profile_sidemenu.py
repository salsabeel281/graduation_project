# ui/profile_sidemenu.py
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QMessageBox,
    QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QCursor
import os


class ProfileSideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProfileSideMenu")
        
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QFrame#ProfileSideMenu {
                background: #0a1628;
                border-right: 1px solid #1a2a4a;
            }
        """)
        
        self.user_data = {
            "name": "Ahmed Mohamed",
            "email": "ahmed@sentinelx.com",
            "department": "Security Operations",
            "job_title": "Security Analyst",
            "phone": "+20 123 456 789",
            "location": "Cairo, Egypt",
            "bio": "Senior Security Analyst with 5+ years of experience in threat detection"
        }
        
        self.profile_image_path = None
        self.is_editing = False
        self.fields = {}
        
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
        
        title = QLabel("Profile")
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
        content_layout.setContentsMargins(0, 24, 0, 24)
        content_layout.setSpacing(20)
        
        # Profile image
        self.image_container = QFrame()
        self.image_container.setFixedSize(80, 80)
        self.image_container.setStyleSheet("""
            QFrame {
                background: rgba(74, 158, 255, 0.1);
                border-radius: 40px;
                border: 2px solid #2a4a7a;
            }
        """)
        
        self.image_label = QLabel(self.image_container)
        self.image_label.setFixedSize(76, 76)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: transparent; border-radius: 38px;")
        self.image_label.move(2, 2)
        self.image_label.setPixmap(self.create_default_avatar(76))
        
        image_wrapper = QWidget()
        image_wrapper_layout = QHBoxLayout(image_wrapper)
        image_wrapper_layout.setAlignment(Qt.AlignCenter)
        image_wrapper_layout.addWidget(self.image_container)
        content_layout.addWidget(image_wrapper)
        
        change_img_btn = QPushButton("Change photo")
        change_img_btn.setCursor(QCursor(Qt.PointingHandCursor))
        change_img_btn.setFixedHeight(28)
        change_img_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #2a4a7a;
                border-radius: 6px;
                color: #6a9acc;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0d1a30;
                border-color: #3a5a8a;
                color: #ffffff;
            }
        """)
        change_img_btn.clicked.connect(self.change_profile_image)
        
        img_btn_wrapper = QWidget()
        img_btn_layout = QHBoxLayout(img_btn_wrapper)
        img_btn_layout.setAlignment(Qt.AlignCenter)
        img_btn_layout.addWidget(change_img_btn)
        content_layout.addWidget(img_btn_wrapper)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #1a2a4a; margin: 8px 24px;")
        content_layout.addWidget(separator)
        
        # Fields
        content_layout.addWidget(self.create_field("Full Name", self.user_data["name"], "name"))
        content_layout.addWidget(self.create_field("Email", self.user_data["email"], "email"))
        content_layout.addWidget(self.create_field("Department", self.user_data["department"], "department"))
        content_layout.addWidget(self.create_field("Job Title", self.user_data["job_title"], "job_title"))
        content_layout.addWidget(self.create_field("Phone", self.user_data["phone"], "phone"))
        content_layout.addWidget(self.create_field("Location", self.user_data["location"], "location"))
        content_layout.addWidget(self.create_field("Password", "••••••••", "password", is_password=True))
        content_layout.addWidget(self.create_field("Bio", self.user_data["bio"], "bio", is_multiline=True))
        
        # Edit button
        self.edit_btn = QPushButton("Edit profile")
        self.edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.edit_btn.setFixedHeight(44)
        self.edit_btn.setStyleSheet("""
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
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        content_layout.addWidget(self.edit_btn)
        
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #4aff6b; margin-top: 8px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_label)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_field(self, label_text, value, field_key, is_password=False, is_multiline=False):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                margin: 0px 20px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 10))
        label.setStyleSheet("color: #5a7a9a;")
        layout.addWidget(label)
        
        if is_multiline:
            display_label = QLabel(value)
            display_label.setWordWrap(True)
            display_label.setFont(QFont("Segoe UI", 11))
            display_label.setStyleSheet("""
                QLabel {
                    background: #0d1a30;
                    border-radius: 6px;
                    color: #e0e0e0;
                    padding: 10px 12px;
                }
            """)
        else:
            display_label = QLabel(value)
            display_label.setFont(QFont("Segoe UI", 11))
            display_label.setStyleSheet("""
                QLabel {
                    background: #0d1a30;
                    border-radius: 6px;
                    color: #e0e0e0;
                    padding: 10px 12px;
                }
            """)
        layout.addWidget(display_label)
        
        if is_password:
            edit_entry = QLineEdit()
            edit_entry.setEchoMode(QLineEdit.Password)
        else:
            edit_entry = QLineEdit()
        
        edit_entry.setText(value if not is_password else "")
        edit_entry.setPlaceholderText(f"Enter {label_text.lower()}")
        edit_entry.setFont(QFont("Segoe UI", 11))
        edit_entry.setStyleSheet("""
            QLineEdit {
                background: #0d1a30;
                border: 1px solid #2a4a7a;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 9px 11px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        edit_entry.hide()
        layout.addWidget(edit_entry)
        
        self.fields[field_key] = {
            'display': display_label,
            'edit': edit_entry,
            'is_password': is_password,
            'original': value
        }
        
        return container
    
    def create_default_avatar(self, size=76):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(74, 158, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(size//3, size//4, size//3, size//3)
        painter.end()
        return pixmap
    
    def change_profile_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(76, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                rounded = QPixmap(76, 76)
                rounded.fill(Qt.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QBrush(pixmap))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(0, 0, 76, 76)
                painter.end()
                self.image_label.setPixmap(rounded)
                self.profile_image_path = file_path
                self.status_label.setText("✓ Photo updated!")
                QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.edit_btn.setText("Save changes")
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2a4a7a;
                    border-radius: 8px;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: 500;
                    margin: 8px 20px 0 20px;
                }
                QPushButton:hover {
                    background: #3a5a8a;
                }
            """)
            for key, field in self.fields.items():
                field['display'].hide()
                field['edit'].show()
                if not field['is_password']:
                    field['edit'].setText(field['display'].text())
                else:
                    field['edit'].setText("")
        else:
            for key, field in self.fields.items():
                new_value = field['edit'].text()
                if new_value:
                    if field['is_password'] and new_value:
                        field['display'].setText("••••••••")
                        self.user_data[key] = new_value
                    elif not field['is_password']:
                        field['display'].setText(new_value)
                        self.user_data[key] = new_value
                field['display'].show()
                field['edit'].hide()
            
            self.edit_btn.setText("Edit profile")
            self.edit_btn.setStyleSheet("""
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
            self.status_label.setText("✓ Profile updated!")
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
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