# ui/admin_dashboard.py
import requests
import json
import random
from datetime import datetime, timedelta
import numpy as np

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar, QGridLayout,
    QScrollArea, QSizePolicy, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QSplitter,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QSlider, QSpinBox, QMessageBox, QMenu, QAction,
    QApplication, QDesktopWidget, QSpacerItem, QDialog, QListWidget,
    QListWidgetItem, QTextEdit, QDateTimeEdit, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize, QTimer, QDateTime, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon, QBrush, QLinearGradient, QRadialGradient, QPen, QPainterPath
import pyqtgraph as pg

from backend.admin_dashboard_service import AdminDashboardService
from ui.profile_sidemenu import ProfileSideMenu


# ==================== Redesigned Card Class (Glassmorphic Gradients) ====================
class Card(QFrame):
    def __init__(self, title, value, unit="", subtitle="", progress_value=0, change="", bg_gradient=None):
        super().__init__()
        self.setMinimumHeight(120)
        
        if bg_gradient:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {bg_gradient};
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                }
            """)
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent; border: none;")
        layout.addWidget(title_lbl)
        
        value_layout = QHBoxLayout()
        value_layout.setSpacing(6)
        value_lbl = QLabel(str(value))
        value_lbl.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_lbl.setStyleSheet("color: white; background: transparent; border: none;")
        value_layout.addWidget(value_lbl)
        
        if unit:
            unit_lbl = QLabel(unit)
            unit_lbl.setFont(QFont("Segoe UI", 12))
            unit_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent; border: none;")
            value_layout.addWidget(unit_lbl)
            
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        if progress_value > 0:
            progress_bar = QProgressBar()
            progress_bar.setValue(progress_value)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(3)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 1.5px;
                    border: none;
                }
                QProgressBar::chunk {
                    background: white;
                    border-radius: 1.5px;
                }
              """)
            layout.addWidget(progress_bar)
            
        bottom_layout = QHBoxLayout()
        if subtitle:
            subtitle_lbl = QLabel(subtitle)
            subtitle_lbl.setFont(QFont("Segoe UI", 9))
            subtitle_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.7); background: transparent; border: none;")
            bottom_layout.addWidget(subtitle_lbl)
        bottom_layout.addStretch()
        
        if change:
            change_lbl = QLabel(f"▲ {change}" if "+" in change else f"▼ {change}")
            change_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
            change_lbl.setStyleSheet("color: white; background: transparent; border: none;")
            bottom_layout.addWidget(change_lbl)
            
        layout.addLayout(bottom_layout)


# ==================== Custom Donut Chart Widget ====================
class DonutChartWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data  # list of dicts: [{'label': 'Malware', 'value': 40, 'color': QColor('#FF5252')}, ...]
        self.setMinimumSize(220, 220)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 40
        cx = (rect.width() - size) // 2
        cy = (rect.height() - size) // 2
        
        draw_rect = QRect(cx, cy, size, size)
        total = sum(d['value'] for d in self.data)
        if total == 0:
            total = 1
            
        start_angle = 90 * 16  # Start at 12 o'clock
        for d in self.data:
            span_angle = int((d['value'] / total) * 360 * 16)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(d['color']))
            painter.drawPie(draw_rect, start_angle, -span_angle)
            start_angle -= span_angle
            
        # Draw center cutout
        inner_size = int(size * 0.6)
        icx = cx + (size - inner_size) // 2
        icy = cy + (size - inner_size) // 2
        inner_rect = QRect(icx, icy, inner_size, inner_size)
        painter.setBrush(QBrush(QColor('#0B1643')))  # matching background
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(inner_rect)
        
        # Center Text
        painter.setPen(QColor('white'))
        font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(inner_rect, Qt.AlignCenter, "Total\n100%")


# ==================== Custom Attack Map Widget ====================
class AttackMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 350)
        
        # Load map background
        self.map_pixmap = QPixmap("ui/cyber_world_map.png")
        
        # Coordinates mapped on an 800x500 original background size
        self.nodes = {
            "Egypt (HQ)": QPoint(475, 225),
            "Russia Node": QPoint(550, 120),
            "China Gateway": QPoint(640, 200),
            "Iran Hub": QPoint(510, 195),
            "Europe Gateway": QPoint(430, 160),
            "North America": QPoint(200, 180),
            "South America": QPoint(280, 350),
            "Australia Hub": QPoint(710, 390),
            "Africa Hub": QPoint(460, 320)
        }
        self.active_attacks = []
        self.anim_t = 0.0
        
        # Pulse variables
        self.pulse_radius = 5
        self.pulse_grow = True
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(40)
        
    def get_scaled_point(self, pt):
        # Maps 800x500 coordinate space to actual widget size
        scale_x = self.width() / 800.0
        scale_y = self.height() / 500.0
        return QPoint(int(pt.x() * scale_x), int(pt.y() * scale_y))
        
    def update_animation(self):
        self.anim_t += 0.015
        if self.anim_t > 1.0:
            self.anim_t = 0.0
            
        if self.pulse_grow:
            self.pulse_radius += 1
            if self.pulse_radius > 16:
                self.pulse_grow = False
        else:
            self.pulse_radius -= 1
            if self.pulse_radius < 5:
                self.pulse_grow = True
        self.update()
        
    def set_active_attacks(self, attacks):
        self.active_attacks = attacks  # list of tuples (source_node_name, target_node_name)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw scaled background image
        if not self.map_pixmap.isNull():
            scaled_pixmap = self.map_pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # Fallback to dark background grid
            painter.fillRect(self.rect(), QColor('#080a1a'))
            painter.setPen(QPen(QColor(255, 255, 255, 8), 1))
            for x in range(0, self.width(), 30):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 30):
                painter.drawLine(0, y, self.width(), y)
            
        # Draw Tech Nodes
        for name, pt in self.nodes.items():
            scaled_pt = self.get_scaled_point(pt)
            if "Egypt" in name:
                # Pulse target glow
                glow = QRadialGradient(scaled_pt.x(), scaled_pt.y(), self.pulse_radius * 2)
                glow.setColorAt(0, QColor(0, 229, 255, 120)) # Neon cyan pulse
                glow.setColorAt(1, QColor(0, 229, 255, 0))
                painter.setBrush(QBrush(glow))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(scaled_pt, self.pulse_radius * 2, self.pulse_radius * 2)
                
                # Core
                painter.setBrush(QBrush(QColor('#00E5FF')))
                painter.drawEllipse(scaled_pt, 6, 6)
            else:
                # Regular node
                painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(scaled_pt, 4, 4)
                
            # Label
            painter.setPen(QColor(255, 255, 255, 180))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(scaled_pt.x() + 8, scaled_pt.y() + 4, name)
            
        # Draw Attack Arcs
        for src, dest in self.active_attacks:
            if src in self.nodes and dest in self.nodes:
                p_src = self.get_scaled_point(self.nodes[src])
                p_dest = self.get_scaled_point(self.nodes[dest])
                
                # Source red pulse
                glow = QRadialGradient(p_src.x(), p_src.y(), 12)
                glow.setColorAt(0, QColor(255, 82, 82, 90))
                glow.setColorAt(1, QColor(255, 82, 82, 0))
                painter.setBrush(QBrush(glow))
                painter.drawEllipse(p_src, 10, 10)
                
                painter.setBrush(QBrush(QColor('#FF5252')))
                painter.drawEllipse(p_src, 3, 3)
                
                # Draw Curve
                path = QPainterPath()
                path.moveTo(p_src)
                mid_x = (p_src.x() + p_dest.x()) / 2
                mid_y = min(p_src.y(), p_dest.y()) - 40
                path.quadTo(QPoint(int(mid_x), int(mid_y)), p_dest)
                
                # Base dashed path
                painter.setPen(QPen(QColor(255, 82, 82, 100), 1.5, Qt.DashLine))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
                
                # Animated dash tracer
                pt_anim = path.pointAtPercent(self.anim_t)
                
                # Tracer Glow
                anim_glow = QRadialGradient(pt_anim.x(), pt_anim.y(), 8)
                anim_glow.setColorAt(0, QColor(255, 82, 82, 180))
                anim_glow.setColorAt(1, QColor(255, 82, 82, 0))
                painter.setBrush(QBrush(anim_glow))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(pt_anim, 6, 6)
                
                # White center
                painter.setBrush(QBrush(QColor('white')))
                painter.drawEllipse(pt_anim, 2, 2)


# ==================== Attack Alert Dialog Popup ====================
class AttackAlertPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, 310)
        
        self.glow_val = 0
        self.glow_dir = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_glow)
        self.timer.start(25)
        
        self.setup_ui()
        
    def update_glow(self):
        self.glow_val += self.glow_dir * 4
        if self.glow_val >= 100 or self.glow_val <= 0:
            self.glow_dir *= -1
        self.update()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.card = QFrame()
        self.card.setObjectName("AlertCard")
        self.card.setStyleSheet("""
            QFrame#AlertCard {
                background: #090b16;
                border: 2px solid #FF5252;
                border-radius: 16px;
            }
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Close button top-right
        close_lay = QHBoxLayout()
        close_lay.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8a9ab0;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { color: #FF5252; }
        """)
        close_btn.clicked.connect(self.close)
        close_lay.addWidget(close_btn)
        card_layout.addLayout(close_lay)
        
        # Icon
        icon_lbl = QLabel("🛡️")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 46))
        icon_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_lbl)
        
        # Header
        title = QLabel("ATTACK ALERT")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #FF5252; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Message
        msg = QLabel("A network attack is currently in progress.\nPlease follow security protocols immediately.")
        msg.setFont(QFont("Segoe UI", 10))
        msg.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        card_layout.addWidget(msg)
        
        # Acknowledge Button
        btn = QPushButton("Acknowledge")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: #FF5252;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background: #FF6666; }
        """)
        btn.clicked.connect(self.close)
        card_layout.addWidget(btn)
        
        layout.addWidget(self.card)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        glow_color = QColor(255, 82, 82, 30 + int(self.glow_val * 0.45))
        pen = QPen(glow_color, 4)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(10, 10, self.width() - 20, self.height() - 20, 16, 16)


# ==================== Custom Admin Sidebar Widget ====================
class AdminSideBar(QFrame):
    page_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QFrame {
                background: #080a1a;
                border-right: 1px solid rgba(255, 255, 255, 0.04);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(8)
        
        # Brand
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        logo_lbl = QLabel("🛡️")
        logo_lbl.setFont(QFont("Segoe UI Emoji", 22))
        logo_lbl.setStyleSheet("background: transparent;")
        
        # Split brand label into SENTINEL (white) and X (neon blue/cyan)
        brand_container = QWidget()
        brand_container.setStyleSheet("background: transparent;")
        brand_lay = QHBoxLayout(brand_container)
        brand_lay.setContentsMargins(0, 0, 0, 0)
        brand_lay.setSpacing(0)
        
        brand_lbl1 = QLabel("SENTINEL")
        brand_lbl1.setFont(QFont("Orbitron", 15, QFont.Bold))
        brand_lbl1.setStyleSheet("color: white; letter-spacing: 1.5px; background: transparent;")
        
        brand_lbl2 = QLabel("X")
        brand_lbl2.setFont(QFont("Orbitron", 15, QFont.Bold))
        brand_lbl2.setStyleSheet("color: #00E5FF; background: transparent;") # Neon Cyan X
        
        brand_lay.addWidget(brand_lbl1)
        brand_lay.addWidget(brand_lbl2)
        
        brand_layout.addWidget(logo_lbl)
        brand_layout.addWidget(brand_container)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)
        
        layout.addSpacing(25)
        
        # Menu items
        self.menu_buttons = {}
        items = [
            ("dashboard", "📊  Dashboard"),
            ("logs", "📑  Logs"),
            ("alerts", "⚠️  Alerts"),
            ("incidents", "🚨  Incidents"),
            ("attack_map", "🌐  Attack Map"),
            ("endpoints", "🖥️  Endpoints"),
            ("threat_intel", "🔍  Threat Intelligence")
        ]
        
        for page_id, label in items:
            btn = QPushButton(label)
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border-radius: 10px;
                    color: #8a9ab0;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(74, 111, 255, 0.08);
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, pid=page_id: self.select_page(pid))
            layout.addWidget(btn)
            self.menu_buttons[page_id] = btn
            
        layout.addStretch()
        
        # Settings
        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.setFixedHeight(45)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setFont(QFont("Segoe UI", 11))
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border-radius: 10px;
                color: #8a9ab0;
                text-align: left;
                padding-left: 15px;
                border: none;
            }
            QPushButton:hover {
                background: rgba(74, 111, 255, 0.08);
                color: white;
            }
        """)
        self.settings_btn.clicked.connect(lambda: self.select_page("settings"))
        layout.addWidget(self.settings_btn)
        self.menu_buttons["settings"] = self.settings_btn
        
        self.active_page = None
        self.select_page("dashboard")
        
    def select_page(self, page_id):
        if self.active_page == page_id:
            return
            
        if self.active_page in self.menu_buttons:
            self.menu_buttons[self.active_page].setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border-radius: 10px;
                    color: #8a9ab0;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(74, 111, 255, 0.08);
                    color: white;
                }
            """)
            
        self.active_page = page_id
        if page_id in self.menu_buttons:
            self.menu_buttons[page_id].setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A6FFF, stop:1 #6C8CFF);
                    border-radius: 10px;
                    color: white;
                    text-align: left;
                    padding-left: 15px;
                    font-weight: bold;
                    border: none;
                }
            """)
            
        self.page_changed.emit(page_id)


# ==================== Redesigned Status Bar Widget ====================
class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(70)
        self.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.title_label = QLabel("Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        
        # Search Container
        search_container = QFrame()
        search_container.setFixedWidth(400)
        search_container.setFixedHeight(42)
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.06);
                border-radius: 10px;
                border: none;
            }
            QFrame:focus-within {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid #4A6FFF;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 14))
        search_icon.setStyleSheet("color: #8a9ab0; background: transparent;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search here...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
            }
            QLineEdit::placeholder { color: #5a6b7c; }
        """)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_container)
        
        # Notifications button
        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFont(QFont("Segoe UI Emoji", 16))
        self.notif_btn.setFixedSize(42, 42)
        self.notif_btn.setCursor(Qt.PointingHandCursor)
        self.notif_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                border: none;
                border-radius: 10px;
                color: #8a9ab0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
        self.notif_btn.clicked.connect(lambda: parent.sidebar.select_page("alerts") if parent else None)
        
        self.unread_badge = QLabel("0", self.notif_btn)
        self.unread_badge.setAlignment(Qt.AlignCenter)
        self.unread_badge.setFixedSize(16, 16)
        self.unread_badge.setStyleSheet("""
            background: #FF5252;
            border-radius: 8px;
            color: white;
            font-size: 9px;
            font-weight: bold;
        """)
        self.unread_badge.move(26, 4)
        self.unread_badge.hide()
        layout.addWidget(self.notif_btn)
        
        # Admin Profile avatar
        user_container = QFrame()
        user_container.setCursor(Qt.PointingHandCursor)
        user_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)
        user_container.mousePressEvent = lambda e: parent.toggle_profile_menu() if parent else None
        
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(6, 4, 12, 4)
        user_layout.setSpacing(8)
        
        avatar_frame = QFrame()
        avatar_frame.setFixedSize(36, 36)
        avatar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A6FFF, stop:1 #6C8CFF);
                border-radius: 18px;
                border: 2px solid #FFFFFF;
            }
        """)
        avatar_layout = QVBoxLayout(avatar_frame)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        self.avatar_text = QLabel("AD")
        self.avatar_text.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.avatar_text.setAlignment(Qt.AlignCenter)
        self.avatar_text.setStyleSheet("color: white; background: transparent;")
        avatar_layout.addWidget(self.avatar_text)
        
        self.user_name = QLabel("Administrator")
        self.user_name.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.user_name.setStyleSheet("color: white; background: transparent;")
        
        arrow = QLabel("▼")
        arrow.setFont(QFont("Segoe UI", 8))
        arrow.setStyleSheet("color: #8a9ab0; background: transparent;")
        
        user_layout.addWidget(avatar_frame)
        user_layout.addWidget(self.user_name)
        user_layout.addWidget(arrow)
        layout.addWidget(user_container)
        
    def set_admin_info(self, full_name):
        self.user_name.setText(full_name)
        parts = full_name.strip().split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else full_name[:2].upper()
        self.avatar_text.setText(initials)
        
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
        self.setFixedSize(420, 270)
        self.setStyleSheet("""
            QDialog {
                background: #0B1643;
                border: 2px solid #FF9800;
                border-radius: 12px;
            }
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QTextEdit {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QTextEdit:focus { border: 1px solid #FF9800; }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel(f"❄️ Freeze {self.user_name}")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #FF9800;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Reason for Freezing:"))
        self.reason_text = QTextEdit()
        self.reason_text.setPlaceholderText("Describe the security violation or threat activity...")
        layout.addWidget(self.reason_text)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #FF5252;
                border-radius: 6px;
                color: #FF5252;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover { background: rgba(255, 82, 82, 0.15); }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        freeze_btn = QPushButton("Freeze Account")
        freeze_btn.setCursor(Qt.PointingHandCursor)
        freeze_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
            }
            QPushButton:hover { background: #e68900; }
        """)
        freeze_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(freeze_btn)
        layout.addLayout(btn_layout)
        
    def get_reason(self):
        return self.reason_text.toPlainText().strip()


# ==================== Main Admin Dashboard QMainWindow ====================
class AdminDashboard(QMainWindow):
    def __init__(self, token=None, sidebar=None):
        super().__init__()
        self.token = token
        self.sidebar_width = 260
        self.setWindowTitle("SentinelX - Admin Control Panel")
        self.showMaximized()
        self.setStyleSheet("QMainWindow { background: #0B1643; }")
        
        # Load API Services
        self.service = AdminDashboardService(token) if token else None
        self.admin_profile = self.service.get_profile() if self.service else None
        
        self.users_data = []
        self.frozen_users_data = []
        self.threats_data = []
        
        self._load_backend_users()
        self._load_backend_threats()
        
        # Mock Logs
        self.admin_logs = [
            {'time': '10:01', 'ip': '185.23.44.10', 'event': 'Failed Login', 'status': 'Failed'},
            {'time': '10:05', 'ip': '192.168.1.8', 'event': 'Successful Login', 'status': 'Success'},
            {'time': '10:12', 'ip': '77.55.22.1', 'event': 'Malware Detected', 'status': 'Blocked'},
            {'time': '10:20', 'ip': '192.168.1.20', 'event': 'USB Connected', 'status': 'Info'},
            {'time': '10:31', 'ip': '91.210.44.3', 'event': 'Brute Force Attempt', 'status': 'Active'}
        ]
        self.filtered_logs = self.admin_logs[:]
        
        # Map Animation setup
        self.map_animation_data = [
            ("Russia Node", "Egypt (HQ)", "🇷🇺 Russia", "HIGH RISK", "APT28 / Fancy Bear", "95.105.24.12", "DDoS / Flooding"),
            ("China Gateway", "Egypt (HQ)", "🇨🇳 China", "HIGH RISK", "APT41 / Double Dragon", "180.76.15.22", "SQL Injection"),
            ("Iran Hub", "Egypt (HQ)", "🇮🇷 Iran", "HIGH RISK", "OilRig", "185.220.101.45", "Credential Stuffing"),
            ("North Korea", "Egypt (HQ)", "🇰🇵 North Korea", "HIGH RISK", "Lazarus Group", "175.45.176.10", "Spear Phishing")
        ]
        self.map_index = 0
        
        self.system_settings = {
            'anomaly_threshold': 70,
            'alert_enabled': True,
            'auto_suspend': False,
            'notification_ttl': 7
        }
        
        self.setup_ui()
        
        # ✅ Create map timer but do NOT start it yet
        self.map_timer = QTimer(self)
        self.map_timer.timeout.connect(self.rotate_map_attack)
        # No self.map_timer.start() here
        
        # Pull notifications periodically
        self.notif_timer = QTimer(self)
        self.notif_timer.timeout.connect(self.check_threat_alerts)
        self.notif_timer.start(6000)
        
    def _load_backend_users(self):
        self.users_data = []
        self.frozen_users_data = []
        if not self.service:
            return
        users = self.service.get_all_users()
        frozen = self.service.get_frozen_users()
        frozen_ids = {str(u.get('id')) for u in frozen}
        
        for u in users:
            uid = str(u.get('id', ''))
            name = f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "Unknown User"
            email = u.get('email', '')
            dept = u.get('department', 'N/A')
            risk = 15 if not u.get('is_trained') else random.randint(5, 45)
            
            if uid in frozen_ids or u.get('is_frozen'):
                self.frozen_users_data.append({
                    'id': uid,
                    'name': name,
                    'email': email,
                    'department': dept,
                    'frozen_date': u.get('last_login') or 'N/A',
                    'reason': 'High risk behavioral anomaly detected'
                })
            else:
                self.users_data.append({
                    'id': uid,
                    'name': name,
                    'email': email,
                    'department': dept,
                    'risk_score': risk,
                    'status': 'Suspended' if u.get('risk_state') == 'suspended' else 'Active',
                    'last_active': u.get('last_login') or 'N/A'
                })
                
    def _load_backend_threats(self):
        self.threats_data = []
        if not self.service:
            return
        threats = self.service.get_latest_threats()
        for t in threats:
            self.threats_data.append({
                'time': str(t.get('timestamp', 'N/A'))[:16] if t.get('timestamp') else 'N/A',
                'user_id': t.get('user_id', 'Unknown'),
                'first_name': t.get('first_name', 'Unknown'),
                'last_name': t.get('last_name', 'User'),
                'email': t.get('email', 'Unknown'),
                'dept': t.get('department', 'N/A'),
                'type': t.get('alerts', 'Unusual behavior pattern'),
                'severity': t.get('status', 'Medium'),
                'risk': t.get('risk_score', 50),
                'city': t.get('city', 'Unknown'),
                'country': t.get('country', 'Unknown'),
                'ip': t.get('ip_address', 'Unknown')
            })

    def _load_backend_logs(self):
        if not self.service:
            self.filtered_logs = self.admin_logs[:]
            return
        db_logs = self.service.get_all_logs()
        if db_logs:
            self.admin_logs = []
            for log in db_logs:
                time_str = 'N/A'
                if log.get('timestamp'):
                    try:
                        time_str = str(log.get('timestamp'))[:16].replace('T', ' ')
                    except:
                        pass
                
                self.admin_logs.append({
                    'time': time_str,
                    'user': log.get('user_name', 'System'),
                    'email': log.get('email', 'N/A'),
                    'ip': '127.0.0.1',
                    'event': log.get('action', 'Info'),
                    'status': 'Success' if 'SUCCESS' in log.get('action', '').upper() or 'MONITOR' in log.get('action', '').upper() else 'Active'
                })
            self.filtered_logs = self.admin_logs[:]
        else:
            self.filtered_logs = self.admin_logs[:]
            
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = AdminSideBar()
        self.sidebar.page_changed.connect(self.switch_page)
        main_layout.addWidget(self.sidebar)
        
        # Content Container
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background: #0B1643;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(25, 20, 25, 20)
        self.content_layout.setSpacing(15)
        
        self.status_bar = StatusBar(self)
        self.content_layout.addWidget(self.status_bar)
        
        # Main layout stacking
        main_layout.addWidget(self.content_area, 1)
        
        # Profile Drawer
        self.profile_menu = ProfileSideMenu(self)
        self.profile_menu.hide()
        if self.admin_profile:
            self.profile_menu.set_user_data(self.admin_profile)
            full_name = f"{self.admin_profile.get('first_name','')} {self.admin_profile.get('last_name','')}".strip()
            if full_name:
                self.status_bar.set_admin_info(full_name)
                
        self.switch_page("dashboard")
        
    def toggle_profile_menu(self):
        if self.profile_menu.isVisible():
            self.profile_menu.hide_menu()
        else:
            data = self.profile_menu.load_user_profile(self.token)
            self.profile_menu.set_user_data(data)
            self.profile_menu.show_menu()
            
    def switch_page(self, page_name):
        # Update status bar title
        title_map = {
            "dashboard": "Dashboard Overview",
            "logs": "System Logs",
            "alerts": "Alert Notifications",
            "incidents": "Incident Responses",
            "attack_map": "Live Threat Map",
            "endpoints": "Endpoint Monitoring",
            "threat_intel": "Threat Intelligence Hub",
            "settings": "System Config"
        }
        self.status_bar.title_label.setText(title_map.get(page_name, "Control Panel"))
        
        if self.profile_menu.isVisible():
            self.profile_menu.hide_menu()
            
        # ✅ Stop map timer if it is running (to avoid accessing deleted widgets)
        if hasattr(self, 'map_timer') and self.map_timer.isActive():
            self.map_timer.stop()
        
        # Clean previous page content
        while self.content_layout.count() > 1:
            child = self.content_layout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
                
        # Populate Page
        if page_name == "dashboard":
            self.render_dashboard()
        elif page_name == "logs":
            self.render_logs()
        elif page_name == "alerts":
            self.render_alerts()
        elif page_name == "incidents":
            self.render_incidents()
        elif page_name == "attack_map":
            self.render_attack_map()
            # ✅ Start map timer only after the map page is fully rendered
            self.map_timer.start(5000)
        elif page_name == "endpoints":
            self.render_endpoints()
        elif page_name == "threat_intel":
            self.render_threat_intel()
        elif page_name == "settings":
            self.render_settings()
            
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                
    # ==================== Render Pages Methods ====================
    
    # 1. Dashboard Page
    def render_dashboard(self):
        # Stats defaults
        total_alerts = 33
        medium_alerts = 24
        high_alerts = 6
        critical_alerts = 3
        
        # Load dynamic stats from backend
        if self.service:
            try:
                sys_dash = self.service.get_system_dashboard()
                if sys_dash:
                    total = sys_dash.get("total_risks_detected", 0)
                    if total > 0:
                        total_alerts = total
                        medium_alerts = sys_dash.get("medium_risk_events", 0)
                        high_alerts = sys_dash.get("high_risk_events", 0)
                        critical_alerts = max(1, high_alerts // 2) if high_alerts > 0 else 0
            except Exception as e:
                print("Error loading system dashboard stats:", e)

        # Stats Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        total_alert_card = Card("Total Alerts", str(total_alerts), "", "Across 7 days", 0, "+12%", "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5E35B1, stop:1 #3949AB)")
        medium_card = Card("Medium Risk", str(medium_alerts), "", "Needs monitoring", 60, "+8%", "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00B0FF, stop:1 #00E5FF)")
        high_card = Card("High Risk", str(high_alerts), "", "Requires action", 85, "+2%", "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F50057, stop:1 #FF4081)")
        critical_card = Card("Critical Alerts", str(critical_alerts), "", "Active attack response", 100, "-1%", "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7B1FA2, stop:1 #9C27B0)")
        
        cards_layout.addWidget(total_alert_card)
        cards_layout.addWidget(medium_card)
        cards_layout.addWidget(high_card)
        cards_layout.addWidget(critical_card)
        
        self.content_layout.addLayout(cards_layout)
        
        # Charts Row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Bar Chart container
        bar_container = QFrame()
        bar_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
            }
        """)
        bar_layout = QVBoxLayout(bar_container)
        bar_layout.setContentsMargins(15, 15, 15, 15)
        
        bar_title = QLabel("Alerts Analysis (Monthly Trend)")
        bar_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        bar_title.setStyleSheet("color: white; border: none;")
        bar_layout.addWidget(bar_title)
        
        plot = pg.PlotWidget()
        plot.setBackground(None)
        plot.showGrid(x=True, y=True, alpha=0.1)
        
        # Plot multi bar graph (Cyber style: cyan & purple) for 12 months
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        x = np.arange(1, 13)
        cyan_heights = [15, 24, 18, 35, 28, 22, 40, 33, 25, 30, 20, 15]
        purple_heights = [8, 14, 10, 20, 18, 12, 25, 20, 15, 18, 12, 8]
        
        bg_cyan = pg.BarGraphItem(x=x - 0.2, height=cyan_heights, width=0.35, brush='#00E5FF', pen=None)
        bg_purple = pg.BarGraphItem(x=x + 0.2, height=purple_heights, width=0.35, brush='#8C33FF', pen=None)
        plot.addItem(bg_cyan)
        plot.addItem(bg_purple)
        
        plot.getAxis('bottom').setPen('white')
        plot.getAxis('left').setPen('white')
        plot.getAxis('bottom').setTextPen(QColor(255, 255, 255, 150))
        plot.getAxis('left').setTextPen(QColor(255, 255, 255, 150))
        
        # Set monthly labels
        x_axis = plot.getAxis('bottom')
        x_ticks = [(i, month) for i, month in zip(x, months)]
        x_axis.setTicks([x_ticks])
        
        bar_layout.addWidget(plot)
        
        # Donut Chart container
        donut_container = QFrame()
        donut_container.setFixedWidth(300)
        donut_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
            }
        """)
        donut_layout = QVBoxLayout(donut_container)
        donut_layout.setContentsMargins(15, 15, 15, 15)
        
        donut_title = QLabel("Threat Vectors")
        donut_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        donut_title.setStyleSheet("color: white; border: none;")
        donut_layout.addWidget(donut_title)
        
        donut_data = [
            {'label': 'Malware', 'value': 40, 'color': QColor('#FF5252')},
            {'label': 'Phishing', 'value': 25, 'color': QColor('#FF9800')},
            {'label': 'Network Attacks', 'value': 20, 'color': QColor('#00E5FF')},
            {'label': 'Data Exfiltration', 'value': 15, 'color': QColor('#3F51B5')}
        ]
        
        donut_chart = DonutChartWidget(donut_data)
        donut_layout.addWidget(donut_chart, 0, Qt.AlignCenter)
        
        # Legend
        legend_grid = QGridLayout()
        legend_grid.setContentsMargins(10, 0, 10, 0)
        legend_grid.setSpacing(8)
        for i, item in enumerate(donut_data):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {item['color'].name()}; font-size: 14px; background: transparent; border: none;")
            lbl = QLabel(f"{item['label']} ({item['value']}%)")
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet("color: #8a9ab0; background: transparent; border: none;")
            legend_grid.addWidget(dot, i // 2, (i % 2) * 2)
            legend_grid.addWidget(lbl, i // 2, (i % 2) * 2 + 1)
        donut_layout.addLayout(legend_grid)
        
        charts_layout.addWidget(bar_container, 2)
        charts_layout.addWidget(donut_container, 1)
        
        self.content_layout.addLayout(charts_layout)
        self.content_layout.addStretch()
        
    # 2. System Logs Page
    def render_logs(self):
        # Header Controls
        ctrls = QHBoxLayout()
        ctrls.setSpacing(15)
        
        sub_lbl = QLabel("REAL-TIME SYSTEM SECURITY LOGS")
        sub_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sub_lbl.setStyleSheet("color: white;")
        ctrls.addWidget(sub_lbl)
        ctrls.addStretch()
        
        self.event_filter_combo = QComboBox()
        self.event_filter_combo.setFixedWidth(200)
        self.event_filter_combo.addItems(["All Events", "Successful Login", "Failed Login", "Malware Detected", "USB Connected", "Brute Force Attempt", "FREEZE_RISK_TRIGGER", "SUSPENDED_RISK_TRIGGER"])
        self.event_filter_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 6px 12px;
                color: white;
                min-width: 150px;
            }
            QComboBox:focus { border: 1px solid #4A6FFF; }
        """)
        self.event_filter_combo.currentTextChanged.connect(self.filter_logs_by_event)
        ctrls.addWidget(self.event_filter_combo)
        
        reset_btn = QPushButton("Reset Filters")
        reset_btn.setFixedSize(110, 36)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74, 111, 255, 0.2);
                border: 1.5px solid #4A6FFF;
                border-radius: 8px;
                color: #4A6FFF;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(74, 111, 255, 0.35); }
        """)
        reset_btn.clicked.connect(self.reset_logs_filters)
        ctrls.addWidget(reset_btn)
        
        self.content_layout.addLayout(ctrls)
        
        # Table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(6)
        self.logs_table.setHorizontalHeaderLabels(["Time", "User Name", "Email", "Source IP", "Event Type", "Status"])
        self.logs_table.horizontalHeader().setStretchLastSection(True)
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.logs_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
                gridline-color: rgba(255,255,255,0.04);
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
            }
            QHeaderView::section {
                background: #080a1a;
                color: #8a9ab0;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
        """)
        self.content_layout.addWidget(self.logs_table)
        self._load_backend_logs()
        self.refresh_logs_table()
        
    def refresh_logs_table(self):
        self.logs_table.setRowCount(len(self.filtered_logs))
        for r_idx, log in enumerate(self.filtered_logs):
            self.logs_table.setItem(r_idx, 0, QTableWidgetItem(log.get('time', 'N/A')))
            self.logs_table.setItem(r_idx, 1, QTableWidgetItem(log.get('user', 'System')))
            self.logs_table.setItem(r_idx, 2, QTableWidgetItem(log.get('email', 'N/A')))
            self.logs_table.setItem(r_idx, 3, QTableWidgetItem(log.get('ip', '127.0.0.1')))
            self.logs_table.setItem(r_idx, 4, QTableWidgetItem(log.get('event', 'Info')))
            
            status_val = log.get('status', 'Success')
            status_item = QTableWidgetItem(status_val)
            color_map = {
                'Success': '#4CAF50',
                'Failed': '#FF5252',
                'Blocked': '#FF5252',
                'Info': '#2196F3',
                'Active': '#FF9800'
            }
            status_item.setForeground(QBrush(QColor(color_map.get(status_val, 'white'))))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.logs_table.setItem(r_idx, 5, status_item)
            
    def filter_logs_by_event(self, text):
        if text == "All Events":
            self.filtered_logs = self.admin_logs[:]
        else:
            self.filtered_logs = [log for log in self.admin_logs if log['event'] == text or text in log['event']]
        self.refresh_logs_table()
        
    def reset_logs_filters(self):
        self.event_filter_combo.setCurrentIndex(0)
        self.filtered_logs = self.admin_logs[:]
        self.refresh_logs_table()
        
    # 3. Alerts Page
    def render_alerts(self):
        # Header with Simulation button
        hdr = QHBoxLayout()
        sub_lbl = QLabel("CRITICAL CYBER THREAT ALERTS")
        sub_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sub_lbl.setStyleSheet("color: white;")
        hdr.addWidget(sub_lbl)
        hdr.addStretch()
        
        sim_btn = QPushButton("🚨 Simulate Attack Alert")
        sim_btn.setFixedHeight(40)
        sim_btn.setFixedWidth(200)
        sim_btn.setCursor(Qt.PointingHandCursor)
        sim_btn.setStyleSheet("""
            QPushButton {
                background: #FF5252;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background: #FF6666; }
        """)
        sim_btn.clicked.connect(self.trigger_critical_popup)
        hdr.addWidget(sim_btn)
        
        self.content_layout.addLayout(hdr)
        
        # Table of Alerts
        alerts_table = QTableWidget()
        alerts_table.setColumnCount(6)
        alerts_table.setHorizontalHeaderLabels(["Time", "User Info", "Department", "Threat Vectors", "Risk Score", "Severity"])
        alerts_table.horizontalHeader().setStretchLastSection(True)
        alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        alerts_table.verticalHeader().setVisible(False)
        alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        alerts_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 12px; border: none; font-weight: bold; }
        """)
        
        self._load_backend_threats()
        alerts_table.setRowCount(len(self.threats_data))
        for r_idx, t in enumerate(self.threats_data):
            alerts_table.setItem(r_idx, 0, QTableWidgetItem(t['time']))
            
            user_info = f"{t['first_name']} {t['last_name']} ({t['email']})"
            alerts_table.setItem(r_idx, 1, QTableWidgetItem(user_info))
            alerts_table.setItem(r_idx, 2, QTableWidgetItem(t['dept']))
            alerts_table.setItem(r_idx, 3, QTableWidgetItem(t['type']))
            
            risk_item = QTableWidgetItem(f"{t['risk']}%")
            risk_color = '#FF5252' if t['risk'] >= 70 else ('#FF9800' if t['risk'] >= 40 else '#4CAF50')
            risk_item.setForeground(QBrush(QColor(risk_color)))
            risk_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            alerts_table.setItem(r_idx, 4, risk_item)
            
            sev_item = QTableWidgetItem(t['severity'])
            sev_item.setForeground(QBrush(QColor(risk_color)))
            sev_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            alerts_table.setItem(r_idx, 5, sev_item)
            
        self.content_layout.addWidget(alerts_table)
        
    def trigger_critical_popup(self):
        popup = AttackAlertPopup(self)
        popup.exec_()
        
    # 4. Incidents Page
    def render_incidents(self):
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255, 255, 255, 0.05); height: 2px; }")
        
        self._load_backend_users()
        
        # 4a. Active Users List Panel
        active_panel = QFrame()
        active_lay = QVBoxLayout(active_panel)
        active_lay.setContentsMargins(0, 0, 0, 10)
        
        lbl_active = QLabel("ACTIVE & SUSPENDED ACCOUNTS MONITOR")
        lbl_active.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_active.setStyleSheet("color: white;")
        active_lay.addWidget(lbl_active)
        
        active_table = QTableWidget()
        active_table.setColumnCount(7)
        active_table.setHorizontalHeaderLabels(["ID", "User Name", "Email", "Department", "Risk Score", "Status", "Action"])
        active_table.horizontalHeader().setStretchLastSection(True)
        active_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        active_table.verticalHeader().setVisible(False)
        active_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 10px; border: none; font-weight: bold; }
        """)
        
        active_table.setRowCount(len(self.users_data))
        for r_idx, u in enumerate(self.users_data):
            active_table.setItem(r_idx, 0, QTableWidgetItem(u['id']))
            active_table.setItem(r_idx, 1, QTableWidgetItem(u['name']))
            active_table.setItem(r_idx, 2, QTableWidgetItem(u['email']))
            active_table.setItem(r_idx, 3, QTableWidgetItem(u['department']))
            
            risk_item = QTableWidgetItem(f"{u['risk_score']}%")
            risk_color = '#4CAF50' if u['risk_score'] < 30 else ('#FF9800' if u['risk_score'] < 70 else '#FF5252')
            risk_item.setForeground(QBrush(QColor(risk_color)))
            risk_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            active_table.setItem(r_idx, 4, risk_item)
            
            status_item = QTableWidgetItem(u['status'])
            status_item.setForeground(QBrush(QColor(risk_color)))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            active_table.setItem(r_idx, 5, status_item)
            
            # Action button
            freeze_btn = QPushButton("❄️ Freeze User")
            freeze_btn.setCursor(Qt.PointingHandCursor)
            freeze_btn.setStyleSheet("""
                QPushButton {
                    background: #FF9800;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                    border: none;
                    font-size: 11px;
                }
                QPushButton:hover { background: #e68900; }
            """)
            freeze_btn.clicked.connect(lambda checked, user=u: self.manual_freeze_action(user))
            active_table.setCellWidget(r_idx, 6, freeze_btn)
            
        active_lay.addWidget(active_table)
        splitter.addWidget(active_panel)
        
        # 4b. Frozen Users List Panel
        frozen_panel = QFrame()
        frozen_lay = QVBoxLayout(frozen_panel)
        frozen_lay.setContentsMargins(0, 10, 0, 0)
        
        lbl_frozen = QLabel("FROZEN / LOCKED ACCOUNTS")
        lbl_frozen.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_frozen.setStyleSheet("color: #FF5252;")
        frozen_lay.addWidget(lbl_frozen)
        
        frozen_table = QTableWidget()
        frozen_table.setColumnCount(7)
        frozen_table.setHorizontalHeaderLabels(["ID", "User Name", "Email", "Department", "Frozen Date", "Freeze Reason", "Action"])
        frozen_table.horizontalHeader().setStretchLastSection(True)
        frozen_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        frozen_table.verticalHeader().setVisible(False)
        frozen_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 10px; border: none; font-weight: bold; }
        """)
        
        frozen_table.setRowCount(len(self.frozen_users_data))
        for r_idx, u in enumerate(self.frozen_users_data):
            frozen_table.setItem(r_idx, 0, QTableWidgetItem(u['id']))
            frozen_table.setItem(r_idx, 1, QTableWidgetItem(u['name']))
            frozen_table.setItem(r_idx, 2, QTableWidgetItem(u['email']))
            frozen_table.setItem(r_idx, 3, QTableWidgetItem(u['department']))
            frozen_table.setItem(r_idx, 4, QTableWidgetItem(str(u['frozen_date'])[:16]))
            frozen_table.setItem(r_idx, 5, QTableWidgetItem(u['reason']))
            
            # Action button
            unfreeze_btn = QPushButton("🔥 Unfreeze User")
            unfreeze_btn.setCursor(Qt.PointingHandCursor)
            unfreeze_btn.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                    border: none;
                    font-size: 11px;
                }
                QPushButton:hover { background: #45a049; }
            """)
            unfreeze_btn.clicked.connect(lambda checked, user=u: self.manual_unfreeze_action(user))
            frozen_table.setCellWidget(r_idx, 6, unfreeze_btn)
            
        frozen_lay.addWidget(frozen_table)
        splitter.addWidget(frozen_panel)
        
        self.content_layout.addWidget(splitter)
        
    def manual_freeze_action(self, user):
        dlg = FreezeReasonDialog(user['name'], self)
        if dlg.exec_() == QDialog.Accepted:
            reason = dlg.get_reason()
            if not reason:
                QMessageBox.warning(self, "Warning", "Reason is required to freeze account.")
                return
                
            success = False
            if self.service:
                success = self.service.freeze_user(user['id'])
                
            if success:
                QMessageBox.information(self, "Frozen", f"✅ User {user['name']} has been frozen successfully.")
                self._load_backend_users()
                self.switch_page("incidents")
            else:
                QMessageBox.warning(self, "Error", "Failed to contact database backend to freeze user.")
                
    def manual_unfreeze_action(self, user):
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            f"Are you sure you want to unfreeze user {user['name']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = False
            if self.service:
                success = self.service.unfreeze_user(user['id'])
                
            if success:
                QMessageBox.information(self, "Unfrozen", f"✅ User {user['name']} has been unfrozen successfully.")
                self._load_backend_users()
                self.switch_page("incidents")
            else:
                QMessageBox.warning(self, "Error", "Failed to contact database backend to unfreeze user.")
                
    # 5. Live Attack Map Page
    def render_attack_map(self):
        # ✅ Stop any previous map timer to avoid conflicts
        if hasattr(self, 'map_timer') and self.map_timer.isActive():
            self.map_timer.stop()
            
        map_layout = QHBoxLayout()
        map_layout.setSpacing(20)
        
        # Left side - Map Canvas
        map_box = QFrame()
        map_box.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
            }
        """)
        box_lay = QVBoxLayout(map_box)
        box_lay.setContentsMargins(15, 15, 15, 15)
        
        map_title = QLabel("Global Cybersecurity Threat Map")
        map_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        map_title.setStyleSheet("color: white; border: none;")
        box_lay.addWidget(map_title)
        
        self.map_widget = AttackMapWidget()
        box_lay.addWidget(self.map_widget, 1)
        
        map_layout.addWidget(map_box, 2)
        
        # Right side - Active Threat Intelligence Panel
        self.threat_intel_panel = QFrame()
        self.threat_intel_panel.setFixedWidth(320)
        self.threat_intel_panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
            }
        """)
        panel_lay = QVBoxLayout(self.threat_intel_panel)
        panel_lay.setContentsMargins(20, 20, 20, 20)
        panel_lay.setSpacing(15)
        
        panel_title = QLabel("Active Threat Intelligence")
        panel_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        panel_title.setStyleSheet("color: white; border: none;")
        panel_lay.addWidget(panel_title)
        
        # Active Attacker Info
        self.attacker_flag_lbl = QLabel("🇷🇺 Russia")
        self.attacker_flag_lbl.setFont(QFont("Segoe UI Emoji", 18, QFont.Bold))
        self.attacker_flag_lbl.setStyleSheet("color: white; border: none; background: transparent;")
        panel_lay.addWidget(self.attacker_flag_lbl)
        
        # Risk Badge
        self.risk_badge = QLabel("HIGH RISK")
        self.risk_badge.setAlignment(Qt.AlignCenter)
        self.risk_badge.setFixedHeight(30)
        self.risk_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.risk_badge.setStyleSheet("""
            background: rgba(255, 82, 82, 0.2);
            color: #FF5252;
            border: 1px solid #FF5252;
            border-radius: 6px;
        """)
        panel_lay.addWidget(self.risk_badge)
        
        # Details grid
        details_grid = QGridLayout()
        details_grid.setSpacing(10)
        
        lbl_apt = QLabel("Targeted User")
        lbl_apt.setStyleSheet("color: #8a9ab0; border: none; background: transparent;")
        self.val_apt = QLabel("Jane Doe (jane@ex.com)")
        self.val_apt.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        lbl_ip = QLabel("Source IP")
        lbl_ip.setStyleSheet("color: #8a9ab0; border: none; background: transparent;")
        self.val_ip = QLabel("95.105.24.12")
        self.val_ip.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        lbl_type = QLabel("Attack Vector")
        lbl_type.setStyleSheet("color: #8a9ab0; border: none; background: transparent;")
        self.val_type = QLabel("DDoS / Flooding")
        self.val_type.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        details_grid.addWidget(lbl_apt, 0, 0)
        details_grid.addWidget(self.val_apt, 0, 1)
        details_grid.addWidget(lbl_ip, 1, 0)
        details_grid.addWidget(self.val_ip, 1, 1)
        details_grid.addWidget(lbl_type, 2, 0)
        details_grid.addWidget(self.val_type, 2, 1)
        
        panel_lay.addLayout(details_grid)
        panel_lay.addStretch()
        
        map_layout.addWidget(self.threat_intel_panel, 1)
        self.content_layout.addLayout(map_layout)
        
        # Call initial rotation to set data
        self.rotate_map_attack()
        
    def rotate_map_attack(self):
        # ✅ Safety checks: if widgets have been deleted, do nothing
        if not hasattr(self, 'map_widget') or self.map_widget is None:
            return
        if not hasattr(self, 'attacker_flag_lbl') or self.attacker_flag_lbl is None:
            return
        if not hasattr(self, 'val_apt') or self.val_apt is None:
            return
        if not hasattr(self, 'val_ip') or self.val_ip is None:
            return
        if not hasattr(self, 'val_type') or self.val_type is None:
            return
        if not hasattr(self, 'risk_badge') or self.risk_badge is None:
            return
            
        self._load_backend_threats()
        
        country_to_node = {
            "russia": "Russia Node",
            "china": "China Gateway",
            "iran": "Iran Hub",
            "egypt": "Egypt (HQ)",
            "united states": "North America",
            "usa": "North America",
            "germany": "Europe Gateway",
            "france": "Europe Gateway",
            "united kingdom": "Europe Gateway",
            "uk": "Europe Gateway",
            "brazil": "South America",
            "australia": "Australia Hub",
            "south africa": "Africa Hub",
            "canada": "North America",
            "japan": "China Gateway"
        }
        
        flags = {
            "russia": "🇷🇺",
            "china": "🇨🇳",
            "iran": "🇮🇷",
            "egypt": "🇪🇬",
            "united states": "🇺🇸",
            "usa": "🇺🇸",
            "germany": "🇩🇪",
            "france": "🇫🇷",
            "united kingdom": "🇬🇧",
            "uk": "🇬🇧",
            "brazil": "🇧🇷",
            "australia": "🇦🇺",
            "south africa": "🇿🇦",
            "canada": "🇨🇦",
            "japan": "🇯🇵"
        }
        
        if self.threats_data:
            t = self.threats_data[self.map_index % len(self.threats_data)]
            country = t.get('country', 'Unknown')
            city = t.get('city', 'Unknown')
            ip = t.get('ip', 'Unknown')
            user_fullname = f"{t.get('first_name')} {t.get('last_name')}"
            email = t.get('email', '')
            vector = t.get('type', 'Anomalous behavior')
            risk = t.get('risk', 50)
            sev = t.get('severity', 'Medium')
            
            src_node = country_to_node.get(country.lower(), "Russia Node")
            dest_node = "Egypt (HQ)"
            
            # Only update if map_widget exists
            if hasattr(self, 'map_widget') and self.map_widget is not None:
                self.map_widget.set_active_attacks([(src_node, dest_node)])
            
            flag_emoji = flags.get(country.lower(), "🌐")
            if hasattr(self, 'attacker_flag_lbl') and self.attacker_flag_lbl is not None:
                self.attacker_flag_lbl.setText(f"{flag_emoji} {country} ({city})")
            if hasattr(self, 'val_apt') and self.val_apt is not None:
                self.val_apt.setText(f"{user_fullname} ({email})")
            if hasattr(self, 'val_ip') and self.val_ip is not None:
                self.val_ip.setText(ip)
            if hasattr(self, 'val_type') and self.val_type is not None:
                self.val_type.setText(vector)
                
            # Update risk badge color
            badge_bg = "rgba(255, 82, 82, 0.2)" if risk >= 70 else ("rgba(255, 152, 0, 0.2)" if risk >= 40 else "rgba(76, 175, 80, 0.2)")
            badge_color = "#FF5252" if risk >= 70 else ("#FF9800" if risk >= 40 else "#4CAF50")
            if hasattr(self, 'risk_badge') and self.risk_badge is not None:
                self.risk_badge.setText(f"{risk}% RISK ({sev.upper()})")
                self.risk_badge.setStyleSheet(f"""
                    background: {badge_bg};
                    color: {badge_color};
                    border: 1px solid {badge_color};
                    border-radius: 6px;
                """)
            
            self.map_index = (self.map_index + 1) % len(self.threats_data)
        else:
            # Fallback simulation if no threats in backend database
            if not self.map_animation_data:
                return
            data = self.map_animation_data[self.map_index % len(self.map_animation_data)]
            src_node, dest_node, flag_name, risk_text, apt_name, ip_addr, attack_name = data
            
            if hasattr(self, 'map_widget') and self.map_widget is not None:
                self.map_widget.set_active_attacks([(src_node, dest_node)])
            
            if hasattr(self, 'attacker_flag_lbl') and self.attacker_flag_lbl is not None:
                self.attacker_flag_lbl.setText(flag_name)
            if hasattr(self, 'val_apt') and self.val_apt is not None:
                self.val_apt.setText(apt_name)
            if hasattr(self, 'val_ip') and self.val_ip is not None:
                self.val_ip.setText(ip_addr)
            if hasattr(self, 'val_type') and self.val_type is not None:
                self.val_type.setText(attack_name)
                
            if hasattr(self, 'risk_badge') and self.risk_badge is not None:
                self.risk_badge.setText(risk_text)
                self.risk_badge.setStyleSheet("""
                    background: rgba(255, 82, 82, 0.2);
                    color: #FF5252;
                    border: 1px solid #FF5252;
                    border-radius: 6px;
                """)
                
            self.map_index = (self.map_index + 1) % len(self.map_animation_data)
            
    # 6. Endpoint Monitoring Page
    def render_endpoints(self):
        self.content_layout.addWidget(QLabel("ENDPOINT CONNECTION STATUS MONITOR"))
        
        endpoints_table = QTableWidget()
        endpoints_table.setColumnCount(8)
        endpoints_table.setHorizontalHeaderLabels(["Hostname", "IP Address", "User Owner", "Email", "Operating System", "Last Seen", "Status", "Risk Score"])
        endpoints_table.horizontalHeader().setStretchLastSection(True)
        endpoints_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        endpoints_table.verticalHeader().setVisible(False)
        endpoints_table.setEditTriggers(QTableWidget.NoEditTriggers)
        endpoints_table.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 12px; border: none; font-weight: bold; }
        """)
        
        self._load_backend_users()
        endpoints = []
        os_options = ["Windows 11 Pro", "Windows 10 Enterprise", "Ubuntu Desktop 22.04", "macOS Sequoia"]
        
        # Combine active and frozen database users
        all_db_users = self.users_data + self.frozen_users_data
        for u in all_db_users:
            email_prefix = u['email'].split('@')[0].upper()
            hostname = f"{email_prefix}-PC"
            
            is_frozen = 'frozen_date' in u
            status = 'OFFLINE' if is_frozen else 'ONLINE'
            risk = 0 if is_frozen else u['risk_score']
            
            # Simulated OS and IP based on ID
            try:
                ip_id = int(u['id']) % 254
            except:
                ip_id = 12
            ip = f"192.168.10.{10 + ip_id}"
            try:
                os_name = os_options[ip_id % len(os_options)]
            except:
                os_name = os_options[0]
            last_seen = "10 mins ago" if is_frozen else "Just now"
            
            endpoints.append({
                'hostname': hostname,
                'ip': ip,
                'owner': u['name'],
                'email': u['email'],
                'os': os_name,
                'last_seen': last_seen,
                'status': status,
                'risk': risk
            })
            
        endpoints_table.setRowCount(len(endpoints))
        for r_idx, ep in enumerate(endpoints):
            endpoints_table.setItem(r_idx, 0, QTableWidgetItem(ep['hostname']))
            endpoints_table.setItem(r_idx, 1, QTableWidgetItem(ep['ip']))
            endpoints_table.setItem(r_idx, 2, QTableWidgetItem(ep['owner']))
            endpoints_table.setItem(r_idx, 3, QTableWidgetItem(ep['email']))
            endpoints_table.setItem(r_idx, 4, QTableWidgetItem(ep['os']))
            endpoints_table.setItem(r_idx, 5, QTableWidgetItem(ep['last_seen']))
            
            status_item = QTableWidgetItem(ep['status'])
            status_color = '#4CAF50' if ep['status'] == 'ONLINE' else '#FF5252'
            status_item.setForeground(QBrush(QColor(status_color)))
            status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            endpoints_table.setItem(r_idx, 6, status_item)
            
            risk_item = QTableWidgetItem(f"{ep['risk']}%")
            risk_color = '#4CAF50' if ep['risk'] < 30 else ('#FF9800' if ep['risk'] < 70 else '#FF5252')
            risk_item.setForeground(QBrush(QColor(risk_color)))
            risk_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            endpoints_table.setItem(r_idx, 7, risk_item)
            
        self.content_layout.addWidget(endpoints_table)
        
    # 7. Threat Intelligence Page
    def render_threat_intel(self):
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(255, 255, 255, 0.05); height: 2px; }")
        
        # Grid 1: Malicious IPs
        g1 = QFrame()
        l1 = QVBoxLayout(g1)
        l1.addWidget(QLabel("KNOWN MALICIOUS IP SOURCES"))
        
        t1 = QTableWidget()
        t1.setColumnCount(5)
        t1.setHorizontalHeaderLabels(["IP Address", "Attribution", "Threat Vector", "Confidence", "Last Seen"])
        t1.horizontalHeader().setStretchLastSection(True)
        t1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t1.verticalHeader().setVisible(False)
        t1.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 10px; border: none; font-weight: bold; }
        """)
        
        malicious_ips = [
            ("45.89.201.33", "🇷🇺 Russia", "Botnet C2 Node", "High", "10 mins ago"),
            ("103.77.192.11", "🇨🇳 China", "SSH Brute Forcer", "Medium", "25 mins ago"),
            ("185.244.25.90", "🇮🇷 Iran", "Credential Phishing Host", "High", "1 hour ago"),
            ("175.45.176.15", "🇰🇵 North Korea", "Active Spear-phishing Server", "High", "3 hours ago")
        ]
        t1.setRowCount(len(malicious_ips))
        for r_idx, ip in enumerate(malicious_ips):
            t1.setItem(r_idx, 0, QTableWidgetItem(ip[0]))
            t1.setItem(r_idx, 1, QTableWidgetItem(ip[1]))
            t1.setItem(r_idx, 2, QTableWidgetItem(ip[2]))
            
            conf_item = QTableWidgetItem(ip[3])
            conf_color = '#FF5252' if ip[3] == 'High' else '#FF9800'
            conf_item.setForeground(QBrush(QColor(conf_color)))
            conf_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            t1.setItem(r_idx, 3, conf_item)
            
            t1.setItem(r_idx, 4, QTableWidgetItem(ip[4]))
        l1.addWidget(t1)
        splitter.addWidget(g1)
        
        # Grid 2: Malware Hashes
        g2 = QFrame()
        l2 = QVBoxLayout(g2)
        l2.addWidget(QLabel("KNOWN MALWARE FILE SIGNATURES"))
        
        t2 = QTableWidget()
        t2.setColumnCount(4)
        t2.setHorizontalHeaderLabels(["Hash (SHA-256)", "Malware Family", "Threat Severity", "First Observed"])
        t2.horizontalHeader().setStretchLastSection(True)
        t2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t2.verticalHeader().setVisible(False)
        t2.setStyleSheet("""
            QTableWidget {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px;
                color: white;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.04); }
            QHeaderView::section { background: #080a1a; color: #8a9ab0; padding: 10px; border: none; font-weight: bold; }
        """)
        
        malware_hashes = [
            ("9f86d081884c7d659a2fea0c55ad015a3e5a1b327b8893d56f5c6e2a2a22cc4a", "Emotet Loader", "Critical", "Today"),
            ("5d41402abc7b2a76b9719d11017c592bb83a71b268b8e0a16d8a7a27a00f2e0f", "AgentTesla Infostealer", "High", "Yesterday"),
            ("2a7b82f0aa984c7d0d0a517cf2e0988cc2e198aa7b8bb5c7d0f5c62aa3b82df1", "TrickBot Trojan", "High", "2 days ago")
        ]
        t2.setRowCount(len(malware_hashes))
        for r_idx, h in enumerate(malware_hashes):
            t2.setItem(r_idx, 0, QTableWidgetItem(h[0]))
            t2.setItem(r_idx, 1, QTableWidgetItem(h[1]))
            
            sev_item = QTableWidgetItem(h[2])
            sev_color = '#FF5252' if h[2] == 'Critical' else '#FF9800'
            sev_item.setForeground(QBrush(QColor(sev_color)))
            sev_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            t2.setItem(r_idx, 2, sev_item)
            
            t2.setItem(r_idx, 3, QTableWidgetItem(h[3]))
        l2.addWidget(t2)
        splitter.addWidget(g2)
        
        self.content_layout.addWidget(splitter)
        
    # 8. Settings Page
    def render_settings(self):
        container = QFrame()
        container.setStyleSheet("background: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 20px;")
        layout = QVBoxLayout(container)
        
        thr_layout = QHBoxLayout()
        thr_layout.addWidget(QLabel("Anomaly Detection Threshold:"))
        self.thr_spin = QSpinBox()
        self.thr_spin.setRange(0, 100)
        self.thr_spin.setValue(self.system_settings['anomaly_threshold'])
        self.thr_spin.setStyleSheet("background: rgba(255,255,255,0.06); padding: 5px; color: white;")
        thr_layout.addWidget(self.thr_spin)
        thr_layout.addStretch()
        layout.addLayout(thr_layout)
        
        alert_layout = QHBoxLayout()
        alert_layout.addWidget(QLabel("Enable Cyber Alerts:"))
        self.alert_check = QCheckBox()
        self.alert_check.setChecked(self.system_settings['alert_enabled'])
        alert_layout.addWidget(self.alert_check)
        alert_layout.addStretch()
        layout.addLayout(alert_layout)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setFixedSize(140, 36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background: #45a049; }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn, 0, Qt.AlignRight)
        
        self.content_layout.addWidget(container)
        self.content_layout.addStretch()
        
    def save_settings(self):
        self.system_settings['anomaly_threshold'] = self.thr_spin.value()
        self.system_settings['alert_enabled'] = self.alert_check.isChecked()
        QMessageBox.information(self, "Saved", "Settings successfully saved.")
        
    # Check Alerts periodically from server
    def check_threat_alerts(self):
        if not self.service:
            return
        threats = self.service.get_latest_threats()
        unread_count = 0
        for t in threats:
            if t.get('risk_score', 0) >= 70:
                unread_count += 1
        self.status_bar.update_unread_count(unread_count)
        
        # Randomly trigger alert dialog popup if threat is critical
        if unread_count > 0 and random.randint(1, 10) == 1:
            self.trigger_critical_popup()
            
    def closeEvent(self, event):
        # Ensure map timer stops when window closes
        if hasattr(self, 'map_timer') and self.map_timer.isActive():
            self.map_timer.stop()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())

