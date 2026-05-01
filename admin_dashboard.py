# ui/admin_dashboard.py
# Final version – profile page shows initials "CH" in a professional circle

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar, QGridLayout,
    QScrollArea, QSizePolicy, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QSplitter,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QSlider, QSpinBox, QMessageBox, QMenu, QAction,
    QApplication, QDesktopWidget, QSpacerItem, QDialog, QListWidget,
    QListWidgetItem, QTextEdit, QDateTimeEdit
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize, QTimer, QDateTime, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon, QBrush, QLinearGradient
import pyqtgraph as pg
from datetime import datetime, timedelta
import numpy as np
import random


# ==================== Card Class (Transparent) ====================
class Card(QFrame):
    def __init__(self, title, value, unit="", subtitle="", progress_value=0, change=""):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("QLabel { background: transparent; color: white; font-size: 18px; font-weight: 600; }")
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_lbl)

        value_layout = QHBoxLayout()
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("QLabel { background: transparent; color: rgba(255, 255, 255, 0.6); font-size: 28px; font-weight: 700; }")
        value_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        value_layout.addWidget(value_lbl)
        if unit:
            unit_lbl = QLabel(unit)
            unit_lbl.setStyleSheet("QLabel { background: transparent; color: rgba(255, 255, 255, 0.4); font-size: 12px; font-weight: 500; }")
            unit_lbl.setFont(QFont("Segoe UI", 12))
            value_layout.addWidget(unit_lbl)
        value_layout.addStretch()
        layout.addLayout(value_layout)

        if progress_value > 0:
            progress_bar = QProgressBar()
            progress_bar.setValue(progress_value)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(2)
            progress_bar.setStyleSheet("""
                QProgressBar { background: rgba(255, 255, 255, 0.15); border-radius: 1px; border: none; }
                QProgressBar::chunk { background: #4A6FFF; border-radius: 1px; }
            """)
            layout.addWidget(progress_bar)

        bottom_layout = QHBoxLayout()
        if subtitle:
            subtitle_lbl = QLabel(subtitle)
            subtitle_lbl.setStyleSheet("QLabel { background: transparent; color: rgba(255, 255, 255, 0.3); font-size: 9px; font-weight: 500; }")
            subtitle_lbl.setFont(QFont("Segoe UI", 9))
            bottom_layout.addWidget(subtitle_lbl)
        bottom_layout.addStretch()
        if change:
            change_color = "#4CAF50" if "+" in change else "#F44336"
            arrow = "▲" if "+" in change else "▼"
            change_lbl = QLabel(f"{arrow} {change}")
            change_lbl.setStyleSheet(f"QLabel {{ background: transparent; color: {change_color}; font-size: 9px; font-weight: 600; }}")
            change_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
            bottom_layout.addWidget(change_lbl)
        layout.addLayout(bottom_layout)


# ==================== Notification Widget (clear emoji, actions) ====================
class NotificationWidget(QFrame):
    def __init__(self, notification_data, parent=None, on_read=None, on_delete=None):
        super().__init__(parent)
        self.notification_data = notification_data
        self.on_read = on_read
        self.on_delete = on_delete
        
        self.setStyleSheet("""
            QFrame {
                background: rgba(20, 30, 55, 0.6);
                border-radius: 16px;
                margin: 6px;
            }
            QFrame:hover {
                background: rgba(40, 50, 80, 0.8);
                border: 1px solid rgba(74,111,255,0.3);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # Icon with emoji font
        icon_map = {'alert': '⚠️', 'user': '👤', 'threat': '🔴', 'system': '⚙️', 'success': '✅'}
        icon = icon_map.get(notification_data.get('type', 'system'), '📢')
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setFixedWidth(50)
        icon_label.setAlignment(Qt.AlignTop)
        
        # Content
        content_layout = QVBoxLayout()
        title_label = QLabel(notification_data['title'])
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        message_label = QLabel(notification_data['message'])
        message_label.setFont(QFont("Segoe UI", 9))
        message_label.setStyleSheet("color: #c0c8dc;")
        message_label.setWordWrap(True)
        time_label = QLabel(notification_data['time'])
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: #7a8aa0;")
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        content_layout.addWidget(time_label)
        
        # Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        if not notification_data.get('read', False):
            read_btn = QPushButton("✓")
            read_btn.setFixedSize(32, 32)
            read_btn.setToolTip("Mark as read")
            read_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(74,111,255,0.5);
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover { background: #4A6FFF; }
            """)
            read_btn.setCursor(Qt.PointingHandCursor)
            read_btn.clicked.connect(self._mark_read)
            actions_layout.addWidget(read_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setToolTip("Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,80,80,0.5);
                border-radius: 16px;
                font-size: 14px;
            }
            QPushButton:hover { background: #FF5252; }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._delete)
        actions_layout.addWidget(delete_btn)
        
        # Unread badge (clear blue dot)
        if not notification_data.get('read', False):
            unread_badge = QLabel("●")
            unread_badge.setStyleSheet("color: #4A6FFF; font-size: 16px; font-weight: bold; background: transparent;")
            unread_badge.setFixedWidth(24)
            unread_badge.setAlignment(Qt.AlignCenter)
            layout.addWidget(unread_badge)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        layout.addLayout(actions_layout)
    
    def _mark_read(self):
        if not self.notification_data.get('read', False):
            self.notification_data['read'] = True
            if self.on_read:
                self.on_read()
    
    def _delete(self):
        if self.on_delete:
            self.on_delete()


# ==================== Status Bar (with clickable user circle) ====================
class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(60)
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        dashboard_title = QLabel("Admin Control Panel")
        dashboard_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        dashboard_title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(dashboard_title)
        layout.addStretch(1)
        
        # Back button
        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.back_btn.setFixedHeight(35)
        self.back_btn.setFixedWidth(160)
        self.back_btn.setVisible(False)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74, 111, 255, 0.2);
                border: 1px solid #4A6FFF;
                border-radius: 8px;
                color: #4A6FFF;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(74, 111, 255, 0.3);
            }
        """)
        self.back_btn.clicked.connect(lambda: parent.switch_page("dashboard") if parent else None)
        layout.addWidget(self.back_btn)
        
        # Search
        search_container = QFrame()
        search_container.setFixedWidth(350)
        search_container.setFixedHeight(40)
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                border: none;
            }
            QFrame:focus-within {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid #4A6FFF;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 14))
        search_icon.setStyleSheet("color: #8a9ab0; background: transparent;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setStyleSheet("background: transparent; border: none; color: white;")
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_container)
        
        # Notification bell with badge
        self.notif_container = QPushButton()
        self.notif_container.setFixedSize(40, 40)
        self.notif_container.setCursor(QCursor(Qt.PointingHandCursor))
        self.notif_container.setStyleSheet("""
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
        self.notif_container.setText("🔔")
        self.notif_container.setFont(QFont("Segoe UI Emoji", 16))
        self.notif_container.clicked.connect(lambda: parent.switch_page("notifications") if parent else None)
        
        self.unread_badge = QLabel("0")
        self.unread_badge.setAlignment(Qt.AlignCenter)
        self.unread_badge.setFixedSize(18, 18)
        self.unread_badge.setStyleSheet("""
            background: #FF5252;
            border-radius: 9px;
            color: white;
            font-size: 10px;
            font-weight: bold;
        """)
        self.unread_badge.move(28, 5)
        self.unread_badge.setParent(self.notif_container)
        layout.addWidget(self.notif_container)
        
        # User avatar and name (clickable to profile)
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
        user_container.mousePressEvent = lambda e: parent.switch_page("profile") if parent else None
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(5, 2, 10, 2)
        user_layout.setSpacing(8)
        
        avatar_container = QFrame()
        avatar_container.setFixedSize(34, 34)
        avatar_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4A6FFF, stop:1 #6C8CFF);
                border-radius: 17px;
                border: 2px solid #FFFFFF;
            }
        """)
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_text = QLabel("CH")
        avatar_text.setFont(QFont("Segoe UI", 11, QFont.Bold))
        avatar_text.setAlignment(Qt.AlignCenter)
        avatar_text.setStyleSheet("color: white; background: transparent;")
        avatar_layout.addWidget(avatar_text)
        
        self.user_name = QLabel("Courtney Henry")
        self.user_name.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.user_name.setStyleSheet("color: white; background: transparent;")
        
        user_layout.addWidget(avatar_container)
        user_layout.addWidget(self.user_name)
        layout.addWidget(user_container)
    
    def update_unread_count(self, count):
        if count > 0:
            self.unread_badge.setText(str(count) if count < 100 else "99+")
            self.unread_badge.show()
        else:
            self.unread_badge.hide()


# ==================== Freeze Reason Dialog ====================
class FreezeReasonDialog(QDialog):
    def __init__(self, user_name, parent=None):
        super().__init__(parent)
        self.user_name = user_name
        self.setWindowTitle(f"Freeze User - {user_name}")
        self.setFixedSize(450, 300)
        self.setStyleSheet("""
            QDialog {
                background: #0B1643;
                border: 2px solid #FF9800;
                border-radius: 15px;
            }
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QTextEdit {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #FF9800;
            }
            QPushButton {
                font-weight: bold;
            }
        """)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        title = QLabel(f"❄️ Freeze {self.user_name}")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #FF9800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(QLabel("📝 Reason for freezing:"))
        self.reason_text = QTextEdit()
        self.reason_text.setPlaceholderText("Enter the reason why this user is being frozen...")
        self.reason_text.setMaximumHeight(100)
        layout.addWidget(self.reason_text)
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("background: transparent; border: 2px solid #FF5252; border-radius: 8px; color: #FF5252;")
        cancel_btn.clicked.connect(self.reject)
        freeze_btn = QPushButton("❄️ Freeze User")
        freeze_btn.setCursor(QCursor(Qt.PointingHandCursor))
        freeze_btn.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #FF9800, stop:1 #e68900); border: none; border-radius: 8px; color: white;")
        freeze_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(freeze_btn)
        layout.addLayout(btn_layout)
    
    def get_reason(self):
        return self.reason_text.toPlainText().strip()


# ==================== Main Admin Dashboard ====================
class AdminDashboard(QMainWindow):
    def __init__(self, sidebar=None):
        super().__init__()
        self.setWindowTitle("SentinelX - Admin Control Panel")
        self.showMaximized()
        self.setStyleSheet("QMainWindow { background: #0B1643; }")
        
        self.external_sidebar = sidebar
        self.users_data = self._gen_users()
        self.frozen_users_data = self._gen_frozen()
        self.all_users_data = []
        self.notifications_data = self._gen_notifications()
        self.admin_logs = self._gen_logs()
        self.threats_data = self._gen_threats()
        self.refresh_all_users()
        
        self.system_settings = {
            'anomaly_threshold': 70,
            'alert_enabled': True,
            'auto_suspend': False,
            'notification_ttl': 7
        }
        self.current_filter = "all"
        self.setup_ui()
        
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_new_notifications)
        self.notification_timer.start(8000)
        self.current_page = "dashboard"
        self.update_unread_badge()
    
    # -------------------- Data generators --------------------
    def _gen_users(self):
        users = []
        deps = ["Engineering","Sales","Marketing","HR","Finance","IT","Operations"]
        first = ["John","Sarah","Michael","Emily","David","Lisa","James","Maria"]
        last = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller"]
        statuses = ["Active","Active","Active","Inactive","Suspended"]
        for i in range(1,26):
            users.append({
                'id': i,
                'name': f"{random.choice(first)} {random.choice(last)}",
                'email': f"user{i}@company.com",
                'department': random.choice(deps),
                'risk_score': random.randint(5,95),
                'threat_level': random.randint(0,100),
                'status': random.choice(statuses),
                'last_active': (datetime.now() - timedelta(minutes=random.randint(0,1440))).strftime("%Y-%m-%d %H:%M"),
                'alerts_count': random.randint(0,15)
            })
        return users
    
    def _gen_frozen(self):
        frozen = []
        names = ["Alex Johnson","Maria Garcia","Robert Miller","Lisa Davis"]
        reasons = ["Multiple security violations","Suspicious activity","Policy violation","Unauthorized access"]
        for i,name in enumerate(names,start=101):
            frozen.append({
                'id': i, 'name': name, 'email': f"frozen{i}@company.com",
                'department': random.choice(["Engineering","Sales","IT"]),
                'frozen_date': (datetime.now() - timedelta(days=random.randint(1,30))).strftime("%Y-%m-%d %H:%M"),
                'reason': random.choice(reasons)
            })
        return frozen
    
    def _gen_notifications(self):
        notifs = []
        templates = [
            ("New User Registered","A new user joined the platform","user"),
            ("High Risk Alert","User exceeded anomaly threshold","alert"),
            ("System Update","Security patch applied","system"),
            ("Threat Detected","Suspicious activity flagged","threat"),
            ("Report Ready","Weekly security report available","success")
        ]
        for i in range(1,21):
            t = random.choice(templates)
            notifs.append({
                'id': i, 'title': t[0], 'message': t[1], 'type': t[2],
                'time': (datetime.now() - timedelta(hours=random.randint(0,72))).strftime("%Y-%m-%d %H:%M:%S"),
                'read': random.choice([True,False]), 'recipient': "All Users"
            })
        return sorted(notifs, key=lambda x: x['time'], reverse=True)
    
    def _gen_logs(self):
        logs = []
        actions = ["User Created","User Suspended","User Frozen","User Unfrozen","Settings Updated","Notification Sent"]
        for i in range(1,31):
            logs.append({
                'id': i,
                'time': (datetime.now() - timedelta(hours=random.randint(0,168))).strftime("%Y-%m-%d %H:%M:%S"),
                'admin': random.choice(["Courtney Henry","Security Admin"]),
                'action': random.choice(actions),
                'details': f"Action performed on user #{random.randint(1,100)}"
            })
        return sorted(logs, key=lambda x: x['time'], reverse=True)
    
    def _gen_threats(self):
        threats = []
        types = ["Unusual Login","Multiple Failures","Suspicious File Access","Data Transfer","Privilege Escalation"]
        severities = ["Low","Medium","High"]
        statuses = ["Investigating","Resolved","False Positive"]
        for i in range(1,21):
            threats.append({
                'id': i,
                'time': (datetime.now() - timedelta(hours=random.randint(0,48))).strftime("%Y-%m-%d %H:%M:%S"),
                'user': random.choice([u['name'] for u in self.users_data]),
                'type': random.choice(types),
                'severity': random.choice(severities),
                'risk_score': random.randint(10,95),
                'status': random.choice(statuses)
            })
        return sorted(threats, key=lambda x: x['time'], reverse=True)
    
    def refresh_all_users(self):
        self.all_users_data = []
        for u in self.users_data:
            self.all_users_data.append({
                'id': u['id'], 'name': u['name'], 'email': u['email'],
                'department': u['department'], 'status': u['status'],
                'risk_score': u['risk_score'], 'threat_level': u['threat_level'],
                'type': 'Active'
            })
        for u in self.frozen_users_data:
            self.all_users_data.append({
                'id': u['id'], 'name': u['name'], 'email': u['email'],
                'department': u['department'], 'status': 'Frozen',
                'risk_score': 0, 'threat_level': 0, 'type': 'Frozen',
                'frozen_date': u['frozen_date'], 'reason': u['reason']
            })
        self.all_users_data.sort(key=lambda x: x['id'])
    
    # -------------------- UI Setup --------------------
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        if self.external_sidebar:
            main_layout.addWidget(self.external_sidebar)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: #0B1643;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5,5,5,5)
        self.content_layout.setSpacing(8)
        self.status_bar = StatusBar(self)
        self.content_layout.addWidget(self.status_bar)
        main_layout.addWidget(self.content_widget,1)
        self.switch_page("dashboard")
    
    def switch_page(self, page_name):
        self.current_page = page_name
        self.status_bar.back_btn.setVisible(page_name != "dashboard")
        # Clear content below status bar
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        # If leaving notifications page, invalidate the layout reference
        if page_name != "notifications" and hasattr(self, 'notif_layout'):
            self.notif_layout = None
        if page_name == "dashboard":
            self._setup_dashboard()
        elif page_name == "users":
            self._setup_users()
        elif page_name == "notifications":
            self._setup_notifications()
        elif page_name == "threats":
            self._setup_threats()
        elif page_name == "analytics":
            self._setup_analytics()
        elif page_name == "logs":
            self._setup_logs()
        elif page_name == "settings":
            self._setup_settings()
        elif page_name == "profile":
            self._setup_profile()
    
    # -------------------- Dashboard Page --------------------
    def _setup_dashboard(self):
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setSpacing(12)
        # Cards
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)
        total = len(self.all_users_data)
        active = len([u for u in self.users_data if u['status']=='Active'])
        total_threats = sum([u['threat_level'] for u in self.users_data])
        high_risk = len([u for u in self.users_data if u['risk_score']>70])
        cards_grid.addWidget(Card("Total Users", str(total), "", "All Users", 0),0,0)
        cards_grid.addWidget(Card("Active Users", str(active), "", f"{int(active/total*100) if total else 0}% Active", int(active/total*100) if total else 0),0,1)
        cards_grid.addWidget(Card("Total Threats", str(total_threats), "", "Detected", 0),1,0)
        cards_grid.addWidget(Card("High Risk", str(high_risk), "", "Needs Attention", int(high_risk/total*100) if total else 0),1,1)
        cards_layout.addLayout(cards_grid)
        
        # Table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        header = QHBoxLayout()
        header.addWidget(QLabel("RECENT USERS"))
        view_all = QPushButton("View All →")
        view_all.setCursor(QCursor(Qt.PointingHandCursor))
        view_all.clicked.connect(lambda: self.switch_page("users"))
        view_all.setStyleSheet("background: transparent; border: 1px solid #4A6FFF; border-radius: 6px; color: #4A6FFF;")
        view_all.setFixedSize(90,28)
        header.addStretch()
        header.addWidget(view_all)
        table_layout.addLayout(header)
        
        self.recent_users_table = QTableWidget()
        self.recent_users_table.setColumnCount(4)
        self.recent_users_table.setHorizontalHeaderLabels(["ID","Name","Risk Score","Status"])
        self.recent_users_table.horizontalHeader().setStretchLastSection(True)
        self.recent_users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_users_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                color: white;
                gridline-color: rgba(255,255,255,0.05);
            }
            QTableWidget::item {
                padding: 8px 6px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            QTableWidget::item:selected {
                background: #4A6FFF40;
            }
            QTableWidget::item:hover {
                background: rgba(74, 111, 255, 0.2);
            }
            QHeaderView::section {
                background: #1a2a4a;
                color: #8a9ab0;
                padding: 8px 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        self.recent_users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_users_table.verticalHeader().setVisible(False)
        self.recent_users_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recent_users_table.customContextMenuRequested.connect(self._recent_user_menu)
        table_layout.addWidget(self.recent_users_table)
        
        top_row_layout.addWidget(cards_container,1)
        top_row_layout.addWidget(table_container,1)
        self.content_layout.addWidget(top_row)
        
        # Chart
        self.content_layout.addWidget(QLabel("THREAT ANALYTICS"))
        plot = pg.PlotWidget()
        plot.setBackground('#0B1643')
        plot.showGrid(x=True,y=True,alpha=0.15)
        plot.setFixedHeight(350)
        days = np.arange(1,8)
        threats = np.random.randint(10,50,7)
        plot.plot(days, threats, pen=pg.mkPen("#4A6FFF", width=4), symbol='o', symbolSize=10, symbolBrush="#4A6FFF")
        plot.setLabel('bottom','Day')
        plot.setLabel('left','Threats')
        self.content_layout.addWidget(plot)
        self._refresh_recent_table()
    
    def _refresh_recent_table(self):
        self.refresh_all_users()
        recent = self.all_users_data[:5]
        self.recent_users_table.setRowCount(len(recent))
        for row,u in enumerate(recent):
            self.recent_users_table.setItem(row,0, QTableWidgetItem(str(u['id'])))
            self.recent_users_table.setItem(row,1, QTableWidgetItem(u['name']))
            risk = QTableWidgetItem("Frozen" if u['type']=='Frozen' else f"{u['risk_score']}%")
            color = "#FF9800" if u['type']=='Frozen' else ("#4CAF50" if u['risk_score']<30 else ("#FFC107" if u['risk_score']<60 else "#FF5252"))
            risk.setForeground(QBrush(QColor(color)))
            self.recent_users_table.setItem(row,2, risk)
            status = QTableWidgetItem(u['status'])
            status_color = "#4CAF50" if u['status']=='Active' else ("#FF9800" if u['status']=='Frozen' else "#FF5252")
            status.setForeground(QBrush(QColor(status_color)))
            self.recent_users_table.setItem(row,3, status)
        self.recent_users_table.resizeRowsToContents()
    
    def _recent_user_menu(self, pos):
        idx = self.recent_users_table.indexAt(pos)
        if not idx.isValid(): return
        row = idx.row()
        if row < len(self.all_users_data[:5]):
            user = self.all_users_data[row]
            menu = QMenu()
            menu.setStyleSheet("background: #1a2a4a; border: 1px solid #4A6FFF; color: white;")
            if user['type'] == 'Frozen':
                act = menu.addAction("🔓 Unfreeze User")
                act.triggered.connect(lambda: self._unfreeze_user(user))
            else:
                act = menu.addAction("❄️ Freeze User")
                act.triggered.connect(lambda: self._freeze_user(user))
            menu.exec_(self.recent_users_table.viewport().mapToGlobal(pos))
    
    # -------------------- Users Page --------------------
    def _setup_users(self):
        header = QHBoxLayout()
        header.addWidget(QLabel("USER MANAGEMENT"))
        add_btn = QPushButton("+ Add New User")
        add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        add_btn.clicked.connect(self._add_user_dialog)
        add_btn.setStyleSheet("background: #4A6FFF; border-radius: 8px;")
        add_btn.setFixedSize(140,35)
        header.addStretch()
        header.addWidget(add_btn)
        self.content_layout.addLayout(header)
        
        filter_bar = QHBoxLayout()
        self.user_search = QLineEdit()
        self.user_search.setPlaceholderText("Search...")
        self.user_search.setStyleSheet("background: rgba(255,255,255,0.08); border-radius: 8px; padding: 8px; color: white;")
        self.user_search.textChanged.connect(self._filter_users)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All","Active","Frozen","Inactive","Suspended"])
        self.status_filter.currentTextChanged.connect(self._filter_users)
        filter_bar.addWidget(self.user_search)
        filter_bar.addWidget(self.status_filter)
        filter_bar.addStretch()
        self.content_layout.addLayout(filter_bar)
        
        self.all_users_table = QTableWidget()
        self.all_users_table.setColumnCount(7)
        self.all_users_table.setHorizontalHeaderLabels(["ID","Name","Email","Department","Risk","Threats","Status"])
        self.all_users_table.horizontalHeader().setStretchLastSection(True)
        self.all_users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_users_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                color: white;
                gridline-color: rgba(255,255,255,0.05);
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            QTableWidget::item:selected {
                background: #4A6FFF40;
            }
            QTableWidget::item:hover {
                background: rgba(74, 111, 255, 0.2);
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
        self.all_users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.all_users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.all_users_table.verticalHeader().setVisible(False)
        self.all_users_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.all_users_table.customContextMenuRequested.connect(self._all_user_menu)
        self.content_layout.addWidget(self.all_users_table)
        self._filter_users()
    
    def _filter_users(self):
        search = self.user_search.text().lower()
        status = self.status_filter.currentText()
        filtered = [u for u in self.all_users_data if (search in u['name'].lower() or search in u['email'].lower())]
        if status != "All":
            filtered = [u for u in filtered if u['status'] == status]
        self.all_users_table.setRowCount(len(filtered))
        for row,u in enumerate(filtered):
            self.all_users_table.setItem(row,0, QTableWidgetItem(str(u['id'])))
            self.all_users_table.setItem(row,1, QTableWidgetItem(u['name']))
            self.all_users_table.setItem(row,2, QTableWidgetItem(u['email']))
            self.all_users_table.setItem(row,3, QTableWidgetItem(u['department']))
            if u['type'] == 'Frozen':
                risk = QTableWidgetItem("Frozen")
                threat = QTableWidgetItem("Frozen")
                risk.setForeground(QBrush(QColor("#FF9800")))
                threat.setForeground(QBrush(QColor("#FF9800")))
            else:
                risk = QTableWidgetItem(f"{u['risk_score']}%")
                risk_col = "#4CAF50" if u['risk_score']<30 else ("#FFC107" if u['risk_score']<60 else "#FF5252")
                risk.setForeground(QBrush(QColor(risk_col)))
                threat = QTableWidgetItem(str(u['threat_level']))
                threat_col = "#4CAF50" if u['threat_level']<30 else ("#FFC107" if u['threat_level']<60 else "#FF5252")
                threat.setForeground(QBrush(QColor(threat_col)))
            self.all_users_table.setItem(row,4, risk)
            self.all_users_table.setItem(row,5, threat)
            status_item = QTableWidgetItem(u['status'])
            status_col = "#4CAF50" if u['status']=='Active' else ("#FF9800" if u['status']=='Frozen' else "#FF5252")
            status_item.setForeground(QBrush(QColor(status_col)))
            self.all_users_table.setItem(row,6, status_item)
    
    def _all_user_menu(self, pos):
        idx = self.all_users_table.indexAt(pos)
        if not idx.isValid(): return
        row = idx.row()
        search = self.user_search.text().lower()
        status = self.status_filter.currentText()
        filtered = [u for u in self.all_users_data if (search in u['name'].lower() or search in u['email'].lower())]
        if status != "All":
            filtered = [u for u in filtered if u['status'] == status]
        if row < len(filtered):
            user = filtered[row]
            menu = QMenu()
            menu.setStyleSheet("background: #1a2a4a; border: 1px solid #4A6FFF; color: white;")
            if user['type'] == 'Frozen':
                act = menu.addAction("🔓 Unfreeze User")
                act.triggered.connect(lambda: self._unfreeze_user(user))
            else:
                act = menu.addAction("❄️ Freeze User")
                act.triggered.connect(lambda: self._freeze_user(user))
            menu.exec_(self.all_users_table.viewport().mapToGlobal(pos))
    
    def _freeze_user(self, user):
        dlg = FreezeReasonDialog(user['name'], self)
        if dlg.exec_() == QDialog.Accepted:
            reason = dlg.get_reason()
            if not reason:
                QMessageBox.warning(self,"Warning","Please enter a reason.")
                return
            self.users_data = [u for u in self.users_data if u['id'] != user['id']]
            self.frozen_users_data.append({
                'id': user['id'], 'name': user['name'], 'email': user['email'],
                'department': user['department'], 'frozen_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'reason': reason
            })
            self.admin_logs.insert(0, {'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'admin': 'Courtney Henry', 'action': 'User Frozen', 'details': f"{user['name']} - {reason}"})
            self._add_notification("User Frozen", f"{user['name']} frozen. Reason: {reason}", "alert")
            self.refresh_all_users()
            self._refresh_recent_table()
            self._filter_users()
            QMessageBox.information(self,"Success",f"{user['name']} frozen.")
    
    def _unfreeze_user(self, user):
        reply = QMessageBox.question(self,"Confirm Unfreeze",f"Unfreeze {user['name']}?",QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.frozen_users_data = [u for u in self.frozen_users_data if u['id'] != user['id']]
            exists = False
            for u in self.users_data:
                if u['id'] == user['id']:
                    u['status'] = 'Active'
                    exists = True
                    break
            if not exists:
                self.users_data.append({
                    'id': user['id'], 'name': user['name'], 'email': user['email'],
                    'department': user['department'], 'risk_score': 20, 'threat_level': 15,
                    'status': 'Active', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'alerts_count': 0
                })
            self.admin_logs.insert(0, {'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'admin': 'Courtney Henry', 'action': 'User Unfrozen', 'details': user['name']})
            self._add_notification("User Unfrozen", f"{user['name']} is active again.", "success")
            self.refresh_all_users()
            self._refresh_recent_table()
            self._filter_users()
            QMessageBox.information(self,"Success",f"{user['name']} unfrozen.")
    
    # -------------------- Add User Dialog (improved) --------------------
    def _add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setFixedSize(480, 580)
        dialog.setStyleSheet("""
            QDialog {
                background: #0B1643;
                border: 2px solid #4A6FFF;
                border-radius: 20px;
            }
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                margin-top: 5px;
            }
            QLineEdit, QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4A6FFF;
                background: rgba(74,111,255,0.1);
            }
            QPushButton {
                border-radius: 10px;
                font-weight: bold;
                padding: 10px;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("➕ Add New User")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #4A6FFF; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Full Name *"))
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter full name")
        layout.addWidget(name_edit)
        
        layout.addWidget(QLabel("Email Address *"))
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("user@example.com")
        layout.addWidget(email_edit)
        
        layout.addWidget(QLabel("Department"))
        dept_combo = QComboBox()
        dept_combo.addItems(["Engineering", "Sales", "Marketing", "HR", "Finance", "IT", "Operations"])
        layout.addWidget(dept_combo)
        
        layout.addWidget(QLabel("Role"))
        role_combo = QComboBox()
        role_combo.addItems(["User", "Manager", "Admin"])
        layout.addWidget(role_combo)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("background: transparent; border: 1px solid #FF5252; color: #FF5252;")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("✓ Save User")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet("background: #4CAF50; color: white; border: none;")
        save_btn.clicked.connect(lambda: self._save_new_user(dialog, name_edit.text(), email_edit.text(), dept_combo.currentText(), role_combo.currentText()))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def _save_new_user(self, dialog, name, email, dept, role):
        if not name or not email:
            QMessageBox.warning(dialog, "Missing Information", "Please enter both name and email.")
            return
        new_id = max([u['id'] for u in self.users_data] + [0]) + 1
        self.users_data.append({
            'id': new_id, 'name': name, 'email': email, 'department': dept,
            'role': role, 'risk_score': random.randint(10,50), 'threat_level': random.randint(5,40),
            'status': 'Active', 'last_active': datetime.now().strftime("%Y-%m-%d %H:%M"), 'alerts_count': 0
        })
        self.admin_logs.insert(0, {'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'admin': 'Courtney Henry', 'action': 'User Created', 'details': f"{name} ({role})"})
        self._add_notification("New User Added", f"{name} has been added as {role}", "user")
        self.refresh_all_users()
        self._refresh_recent_table()
        self._filter_users()
        dialog.accept()
        QMessageBox.information(self, "Success", f"✅ User {name} added successfully!")
    
    # -------------------- Notifications Page (No Send button, safe layout) --------------------
    def _setup_notifications(self):
        header = QHBoxLayout()
        header.addWidget(QLabel("NOTIFICATION CENTER"))
        
        # Filter buttons
        self.filter_all = QPushButton("All")
        self.filter_unread = QPushButton("Unread")
        self.filter_read = QPushButton("Read")
        for btn in (self.filter_all, self.filter_unread, self.filter_read):
            btn.setFixedSize(70,30)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("background: rgba(74,111,255,0.2); border-radius: 15px; color: white;")
            btn.clicked.connect(lambda checked, f=btn.text().lower(): self._set_filter(f))
        header.addStretch()
        header.addWidget(self.filter_all)
        header.addWidget(self.filter_unread)
        header.addWidget(self.filter_read)
        self.content_layout.addLayout(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        self.notif_layout = QVBoxLayout(container)
        self.notif_layout.setSpacing(10)
        scroll.setWidget(container)
        self.content_layout.addWidget(scroll)
        
        mark_all = QPushButton("✓ Mark All as Read")
        mark_all.setFixedSize(150,32)
        mark_all.setCursor(QCursor(Qt.PointingHandCursor))
        mark_all.setStyleSheet("background: rgba(74,111,255,0.2); border-radius: 10px; color: #4A6FFF;")
        mark_all.clicked.connect(self._mark_all_read)
        self.content_layout.addWidget(mark_all, 0, Qt.AlignRight)
        
        self._refresh_notifications()
    
    def _set_filter(self, f):
        if f == 'all':
            self.current_filter = 'all'
        elif f == 'unread':
            self.current_filter = 'unread'
        else:
            self.current_filter = 'read'
        self._refresh_notifications()
    
    def _refresh_notifications(self):
        if not hasattr(self, 'notif_layout') or self.notif_layout is None:
            return
        try:
            _ = self.notif_layout.count()
        except RuntimeError:
            self.notif_layout = None
            return
        while self.notif_layout.count():
            child = self.notif_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        filtered = []
        if self.current_filter == 'all':
            filtered = self.notifications_data[:]
        elif self.current_filter == 'unread':
            filtered = [n for n in self.notifications_data if not n.get('read', False)]
        else:
            filtered = [n for n in self.notifications_data if n.get('read', False)]
        for n in filtered:
            w = NotificationWidget(n, on_read=self._on_notification_changed, on_delete=lambda nid=n['id']: self._delete_notification(nid))
            self.notif_layout.addWidget(w)
        self.notif_layout.addStretch()
        self.update_unread_badge()
    
    def _on_notification_changed(self):
        self._refresh_notifications()
    
    def _delete_notification(self, nid):
        self.notifications_data = [n for n in self.notifications_data if n['id'] != nid]
        self._refresh_notifications()
    
    def _mark_all_read(self):
        for n in self.notifications_data:
            n['read'] = True
        self._refresh_notifications()
    
    def update_unread_badge(self):
        unread = sum(1 for n in self.notifications_data if not n.get('read', False))
        self.status_bar.update_unread_count(unread)
    
    # -------------------- Threats Page --------------------
    def _setup_threats(self):
        self.content_layout.addWidget(QLabel("THREAT MANAGEMENT"))
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Time","User","Type","Severity","Risk","Status"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                color: white;
                gridline-color: rgba(255,255,255,0.05);
            }
            QTableWidget::item { padding: 12px 8px; }
            QHeaderView::section {
                background: #1a2a4a;
                color: #8a9ab0;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
            }
        """)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(self.threats_data))
        for row,t in enumerate(self.threats_data):
            table.setItem(row,0, QTableWidgetItem(t['time']))
            table.setItem(row,1, QTableWidgetItem(t['user']))
            table.setItem(row,2, QTableWidgetItem(t['type']))
            sev = QTableWidgetItem(t['severity'])
            sev_color = {"Low":"#4CAF50","Medium":"#FFC107","High":"#FF5252"}[t['severity']]
            sev.setForeground(QBrush(QColor(sev_color)))
            table.setItem(row,3, sev)
            risk = QTableWidgetItem(f"{t['risk_score']}%")
            risk_color = "#4CAF50" if t['risk_score']<30 else ("#FFC107" if t['risk_score']<60 else "#FF5252")
            risk.setForeground(QBrush(QColor(risk_color)))
            table.setItem(row,4, risk)
            table.setItem(row,5, QTableWidgetItem(t['status']))
        self.content_layout.addWidget(table)
    
    # -------------------- Analytics Page --------------------
    def _setup_analytics(self):
        self.content_layout.addWidget(QLabel("ADVANCED ANALYTICS"))
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
            }
            QTabBar::tab {
                background: transparent;
                color: #8a9ab0;
                padding: 12px 25px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4A6FFF;
                color: white;
                border-radius: 8px;
            }
            QTabBar::tab:hover {
                background: rgba(74, 111, 255, 0.3);
            }
        """)
        # User Growth
        w1 = QWidget()
        l1 = QVBoxLayout(w1)
        p1 = pg.PlotWidget()
        p1.setBackground('#0B1643')
        p1.plot(np.arange(1,13), np.cumsum(np.random.randint(20,50,12)), pen=pg.mkPen("#4A6FFF", width=3), fillLevel=0, brush=pg.mkBrush(74,111,255,50))
        l1.addWidget(p1)
        tabs.addTab(w1, "User Growth")
        # Threat Trends
        w2 = QWidget()
        l2 = QVBoxLayout(w2)
        p2 = pg.PlotWidget()
        p2.setBackground('#0B1643')
        weeks = np.arange(1,13)
        p2.plot(weeks, np.random.randint(10,30,12), pen=pg.mkPen("#4CAF50"), name="Low Risk")
        p2.plot(weeks, np.random.randint(5,20,12), pen=pg.mkPen("#FFC107"), name="Medium Risk")
        p2.plot(weeks, np.random.randint(0,15,12), pen=pg.mkPen("#FF5252"), name="High Risk")
        p2.addLegend()
        l2.addWidget(p2)
        tabs.addTab(w2, "Threat Trends")
        # Department Stats
        w3 = QWidget()
        l3 = QVBoxLayout(w3)
        p3 = pg.PlotWidget()
        p3.setBackground('#0B1643')
        depts = ['Eng','Sales','Mkt','HR','Fin','IT']
        counts = [45,32,28,15,22,38]
        bg = pg.BarGraphItem(x=np.arange(len(depts)), height=counts, width=0.6, brush='#4A6FFF')
        p3.addItem(bg)
        p3.getAxis('bottom').setTicks([[(i,d) for i,d in enumerate(depts)]])
        l3.addWidget(p3)
        tabs.addTab(w3, "Department Stats")
        self.content_layout.addWidget(tabs)
    
    # -------------------- Logs Page --------------------
    def _setup_logs(self):
        self.content_layout.addWidget(QLabel("ADMIN ACTIVITY LOGS"))
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Time","Admin","Action","Details"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                color: white;
                gridline-color: rgba(255,255,255,0.05);
            }
            QTableWidget::item { padding: 12px 8px; }
            QHeaderView::section {
                background: #1a2a4a;
                color: #8a9ab0;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
            }
        """)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(self.admin_logs))
        for row,log in enumerate(self.admin_logs):
            table.setItem(row,0, QTableWidgetItem(log['time']))
            table.setItem(row,1, QTableWidgetItem(log['admin']))
            table.setItem(row,2, QTableWidgetItem(log['action']))
            table.setItem(row,3, QTableWidgetItem(log['details']))
        self.content_layout.addWidget(table)
    
    # -------------------- Settings Page --------------------
    def _setup_settings(self):
        self.content_layout.addWidget(QLabel("SYSTEM SETTINGS"))
        container = QFrame()
        container.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 15px; padding: 20px;")
        layout = QVBoxLayout(container)
        # Threshold
        thr_layout = QHBoxLayout()
        thr_layout.addWidget(QLabel("Anomaly Detection Threshold:"))
        self.thr_spin = QSpinBox()
        self.thr_spin.setRange(0,100)
        self.thr_spin.setValue(self.system_settings['anomaly_threshold'])
        thr_layout.addWidget(self.thr_spin)
        thr_layout.addStretch()
        layout.addLayout(thr_layout)
        # Alerts
        alert_layout = QHBoxLayout()
        alert_layout.addWidget(QLabel("Enable Real-time Alerts:"))
        self.alert_check = QCheckBox()
        self.alert_check.setChecked(self.system_settings['alert_enabled'])
        alert_layout.addWidget(self.alert_check)
        alert_layout.addStretch()
        layout.addLayout(alert_layout)
        # Auto suspend
        auto_layout = QHBoxLayout()
        auto_layout.addWidget(QLabel("Auto-suspend High Risk Users:"))
        self.auto_check = QCheckBox()
        self.auto_check.setChecked(self.system_settings['auto_suspend'])
        auto_layout.addWidget(self.auto_check)
        auto_layout.addStretch()
        layout.addLayout(auto_layout)
        # Notification Retention
        ret_layout = QHBoxLayout()
        ret_layout.addWidget(QLabel("Notification Retention (days):"))
        self.ret_spin = QSpinBox()
        self.ret_spin.setRange(1,90)
        self.ret_spin.setValue(self.system_settings['notification_ttl'])
        ret_layout.addWidget(self.ret_spin)
        ret_layout.addStretch()
        layout.addLayout(ret_layout)
        # Save
        save_btn = QPushButton("Save Settings")
        save_btn.setFixedSize(140,36)
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setStyleSheet("background: #4CAF50; border-radius: 8px;")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn, 0, Qt.AlignRight)
        self.content_layout.addWidget(container)
    
    def _save_settings(self):
        self.system_settings.update({
            'anomaly_threshold': self.thr_spin.value(),
            'alert_enabled': self.alert_check.isChecked(),
            'auto_suspend': self.auto_check.isChecked(),
            'notification_ttl': self.ret_spin.value()
        })
        self.admin_logs.insert(0, {'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'admin': 'Courtney Henry', 'action': 'Settings Updated', 'details': str(self.system_settings)})
        QMessageBox.information(self, "Saved", "Settings applied.")
    
    # -------------------- Professional Profile Page (initials in circle) --------------------
    def _setup_profile(self):
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(20,30,55,0.6), stop:1 rgba(30,40,65,0.6));
                border-radius: 28px;
                border: 1px solid rgba(74,111,255,0.3);
                padding: 30px;
            }
        """)
        layout = QVBoxLayout(profile_card)
        layout.setSpacing(20)
        
        # Avatar circle with initials "CH" (larger version of the top bar circle)
        avatar_frame = QFrame()
        avatar_frame.setFixedSize(100, 100)
        avatar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4A6FFF, stop:1 #6C8CFF);
                border-radius: 50px;
                border: 2px solid rgba(255,255,255,0.3);
            }
        """)
        avatar_layout = QVBoxLayout(avatar_frame)
        avatar_text = QLabel("CH")
        avatar_text.setFont(QFont("Segoe UI", 38, QFont.Bold))
        avatar_text.setAlignment(Qt.AlignCenter)
        avatar_text.setStyleSheet("color: white; background: transparent;")
        avatar_layout.addWidget(avatar_text)
        avatar_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar_frame, 0, Qt.AlignCenter)
        
        # Name
        name = QLabel("Courtney Henry")
        name.setFont(QFont("Segoe UI", 24, QFont.Bold))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: white;")
        layout.addWidget(name)
        
        # Role (subtle)
        role = QLabel("Security Administrator")
        role.setFont(QFont("Segoe UI", 13))
        role.setAlignment(Qt.AlignCenter)
        role.setStyleSheet("color: #4A6FFF; font-weight: 500;")
        layout.addWidget(role)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: rgba(255,255,255,0.1); max-height: 1px;")
        layout.addWidget(sep)
        
        # Info grid
        info_grid = QGridLayout()
        info_grid.setSpacing(15)
        info_grid.setColumnStretch(0, 1)
        info_grid.setColumnStretch(1, 2)
        
        details = [
            ("📧 Email", "courtney.henry@sentinelx.com"),
            ("🏢 Department", "Security Operations"),
            ("📅 Member Since", "January 2024"),
            ("🆔 User ID", "ADM-2024-001"),
            ("🖥️ Last Login", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("🔐 Active Sessions", "3")
        ]
        
        for i, (label, value) in enumerate(details):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 11))
            label_widget.setStyleSheet("color: #8a9ab0;")
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Segoe UI", 12, QFont.Medium))
            value_widget.setStyleSheet("color: white;")
            info_grid.addWidget(label_widget, i, 0)
            info_grid.addWidget(value_widget, i, 1)
        
        layout.addLayout(info_grid)
        
        self.content_layout.addWidget(profile_card)
    
    # -------------------- Helper Methods --------------------
    def _add_notification(self, title, msg, typ):
        self.notifications_data.insert(0, {
            'id': len(self.notifications_data)+1,
            'title': title,
            'message': msg,
            'type': typ,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'read': False,
            'recipient': "Admin"
        })
        if self.current_page == "notifications" and hasattr(self, 'notif_layout') and self.notif_layout is not None:
            try:
                _ = self.notif_layout.count()
                self._refresh_notifications()
            except RuntimeError:
                self.notif_layout = None
        else:
            self.update_unread_badge()
    
    def check_new_notifications(self):
        if random.randint(1, 15) == 1:
            self._add_notification(
                "⚠️ New Threat Detected",
                f"Suspicious behavior from user {random.choice([u['name'] for u in self.users_data])}",
                "alert"
            )


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())