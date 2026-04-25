# ui/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar, QGridLayout,
    QSizePolicy, QPushButton, QSpacerItem, QLineEdit
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon
import pyqtgraph as pg
from datetime import datetime
import numpy as np
import os

from ui.sidebar import SideBar
from ui.profile_sidemenu import ProfileSideMenu
from ui.recent_activity_sidemenu import RecentActivitySideMenu
from ui.support_sidemenu import SupportSideMenu


class MetricWidget(QWidget):
    """بدون كروت - مجرد نص وقيمة"""
    def __init__(self, title, value, unit, subtitle="", progress_value=0, change=""):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            QLabel {
                background: transparent;
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
        """)
        title_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(title_lbl)

        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("""
            QLabel {
                background: transparent;
                color: rgba(255, 255, 255, 0.6);
                font-size: 32px;
                font-weight: 700;
            }
        """)
        value_lbl.setFont(QFont("Segoe UI", 32, QFont.Bold))
        value_layout.addWidget(value_lbl)
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("""
            QLabel {
                background: transparent;
                color: rgba(255, 255, 255, 0.4);
                font-size: 13px;
                font-weight: 500;
            }
        """)
        unit_lbl.setFont(QFont("Segoe UI", 13))
        value_layout.addWidget(unit_lbl)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)

        if progress_value > 0:
            progress_bar = QProgressBar()
            progress_bar.setValue(progress_value)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(2)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 1px;
                    border: none;
                }
                QProgressBar::chunk {
                    background: #4A6FFF;
                    border-radius: 1px;
                }
            """)
            layout.addWidget(progress_bar)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)
        
        if subtitle:
            subtitle_lbl = QLabel(subtitle)
            subtitle_lbl.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: rgba(255, 255, 255, 0.3);
                    font-size: 10px;
                    font-weight: 500;
                }
            """)
            subtitle_lbl.setFont(QFont("Segoe UI", 10))
            bottom_layout.addWidget(subtitle_lbl)
        
        bottom_layout.addStretch()
        
        if change:
            change_color = "#4CAF50" if "+" in change else "#F44336"
            arrow = "▲" if "+" in change else "▼"
            change_lbl = QLabel(f"{arrow} {change}")
            change_lbl.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    color: {change_color};
                    font-size: 10px;
                    font-weight: 600;
                }}
            """)
            change_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            bottom_layout.addWidget(change_lbl)
        
        layout.addLayout(bottom_layout)


class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltip = None
        self.lines_info = []
        # تعطيل الزوم والتحريك
        self.setMouseEnabled(x=False, y=False)
        self.setMenuEnabled(False)
        
    def set_lines_info(self, lines_info):
        self.lines_info = lines_info
        
    def mouseMoveEvent(self, event):
        pos = event.pos()
        view_pos = self.plotItem.vb.mapSceneToView(pos)
        
        closest_line = None
        closest_point = None
        min_distance = float('inf')
        
        for line_info in self.lines_info:
            data = line_info['data']
            x_data = line_info['x_data']
            name = line_info['name']
            
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
                        background: rgba(0, 0, 0, 0.85);
                        color: white;
                        border-radius: 8px;
                        padding: 8px 14px;
                        font-size: 11px;
                        font-weight: 500;
                    }
                """)
                self.tooltip.setFont(QFont("Segoe UI", 10))
            
            hour = int(closest_point[0])
            time_str = f"{hour:02d}:00"
            self.tooltip.setText(f"{closest_line}\n{time_str} • {closest_point[1]:.1f}")
            self.tooltip.adjustSize()
            tooltip_pos = pos + QPoint(15, 15)
            self.tooltip.move(tooltip_pos)
            self.tooltip.show()
        elif self.tooltip:
            self.tooltip.hide()
        
        super().mouseMoveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelX - Behavioral Threat Detection")
        self.showMaximized()
        self.setStyleSheet("QMainWindow { background: #0B1643; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 15, 0)
        main_layout.setSpacing(0)
        main_layout.setStretch(0, 0)  # sidebar
        main_layout.setStretch(4, 1)  # content
        
        # ========= Sidebar =========
        self.sidebar = SideBar()
        self.sidebar.page_changed.connect(self.switch_page)
        self.sidebar.profile_clicked.connect(self.toggle_profile_menu)
        self.sidebar.activity_clicked.connect(self.toggle_activity_menu)
        self.sidebar.support_clicked.connect(self.toggle_support_menu)
        
        # ========= Side Menus =========
        self.profile_menu = ProfileSideMenu(self)
        self.profile_menu.hide()
        
        self.activity_menu = RecentActivitySideMenu(self)
        self.activity_menu.hide()
        
        self.support_menu = SupportSideMenu(self)
        self.support_menu.hide()
        
        # ========= Content Area (بدون سكرول) =========
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background: #0B1643;")
        
        # ========= Dashboard Content (بدون سكرول) =========
        self.dashboard_widget = QWidget()
        self.dashboard_widget.setStyleSheet("background: #0B1643;")
        
        dashboard_layout = QVBoxLayout(self.dashboard_widget)
        dashboard_layout.setContentsMargins(30, 20, 30, 20)
        dashboard_layout.setSpacing(20)

        # ========= Header =========
        status_bar = QFrame()
        status_bar.setFixedHeight(70)
        status_bar.setStyleSheet("background: transparent; border: none;")
        
        header_layout = QHBoxLayout(status_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        dashboard_title.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(dashboard_title)
        header_layout.addStretch(1)
        
        # ===== Search Box (مع أيقونة SVG) =====
        search_container = QFrame()
        search_container.setMinimumWidth(300)
        search_container.setMinimumWidth(600)
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
        
        # أيقونة البحث من SVG
        search_icon_path = os.path.join("ui", "icon", "search.svg")
        if os.path.exists(search_icon_path):
            search_icon_pixmap = QPixmap(search_icon_path)
            if not search_icon_pixmap.isNull():
                search_icon_pixmap = search_icon_pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                search_icon_label = QLabel()
                search_icon_label.setPixmap(search_icon_pixmap)
                search_icon_label.setStyleSheet("background: transparent;")
                search_layout.addWidget(search_icon_label)
            else:
                search_icon_label = QLabel("🔍")
                search_icon_label.setFont(QFont("Segoe UI Emoji", 15))
                search_icon_label.setStyleSheet("color: #8a9ab0; background: transparent;")
                search_layout.addWidget(search_icon_label)
        else:
            search_icon_label = QLabel("🔍")
            search_icon_label.setFont(QFont("Segoe UI Emoji", 15))
            search_icon_label.setStyleSheet("color: #8a9ab0; background: transparent;")
            search_layout.addWidget(search_icon_label)
        
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
        
        search_layout.addWidget(self.search_input)
        
        header_layout.addWidget(search_container)
        header_layout.addStretch(1)
        
        # ===== Notification Button (مع أيقونة SVG) =====
        notification_btn = QPushButton()
        notification_btn.setFixedSize(40, 40)
        notification_btn.setCursor(QCursor(Qt.PointingHandCursor))
        notification_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        # أيقونة النوتفيكشن من SVG
        notif_icon_path = os.path.join("ui", "icon", "notification.svg")
        if os.path.exists(notif_icon_path):
            notif_icon_pixmap = QPixmap(notif_icon_path)
            if not notif_icon_pixmap.isNull():
                notif_icon_pixmap = notif_icon_pixmap.scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                notif_icon = QIcon(notif_icon_pixmap)
                notification_btn.setIcon(notif_icon)
                notification_btn.setIconSize(QSize(22, 22))
                notification_btn.setText("")
            else:
                notification_btn.setText("🔔")
                notification_btn.setFont(QFont("Segoe UI Emoji", 18))
                notification_btn.setStyleSheet(notification_btn.styleSheet() + "color: #8a9ab0;")
        else:
            notification_btn.setText("🔔")
            notification_btn.setFont(QFont("Segoe UI Emoji", 18))
            notification_btn.setStyleSheet(notification_btn.styleSheet() + "color: #8a9ab0;")
        
        # User Profile Section
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
        
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        avatar_text = QLabel("CH")
        avatar_text.setFont(QFont("Segoe UI", 12, QFont.Bold))
        avatar_text.setAlignment(Qt.AlignCenter)
        avatar_text.setStyleSheet("color: white; background: transparent; padding: 0px; margin: 0px;")
        avatar_layout.addWidget(avatar_text, 0, Qt.AlignCenter)
        
        user_name = QLabel("Courtney Henry")
        user_name.setFont(QFont("Segoe UI", 13, QFont.Medium))
        user_name.setStyleSheet("color: white; background: transparent;")
        
        dropdown = QLabel("▼")
        dropdown.setFont(QFont("Segoe UI", 9))
        dropdown.setStyleSheet("color: #8a9ab0; background: transparent;")
        
        user_layout.addWidget(avatar_container)
        user_layout.addWidget(user_name)
        user_layout.addWidget(dropdown)
        
        header_layout.addWidget(notification_btn)
        header_layout.addWidget(user_container)
        header_layout.addSpacing(10)
        
        dashboard_layout.addWidget(status_bar)

        # ========= Section Title =========
        section_title = QLabel("BEHAVIORAL METRICS")
        section_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        section_title.setStyleSheet("color: rgba(255,255,255,0.6); letter-spacing: 1.5px; margin-top: 5px; margin-bottom: 10px;")
        dashboard_layout.addWidget(section_title)
       
        # ========= Row 1 =========
        row1 = QHBoxLayout()
        row1.setSpacing(18)
        row1.addWidget(MetricWidget("Typing Speed", "72", "WPM", "Words Per Minute", 85, "+2.3%"))
        row1.addWidget(MetricWidget("Mouse Speed", "4.2", "px/s", "Pixels/Second", 60, "-0.8%"))
        row1.addWidget(MetricWidget("Keystroke Rhythm", "92", "%", "Consistency Score", 92, "+1.5%"))
        row1.addWidget(MetricWidget("Click Frequency", "3.8", "c/m", "Clicks/Minute", 75, "-0.3%"))
        dashboard_layout.addLayout(row1)
        
        # ========= Row 2 =========
        row2 = QHBoxLayout()
        row2.setSpacing(18)
        row2.addWidget(MetricWidget("App Focus Time", "4.2", "hrs", "Hours/Day", 63, "+0.5%"))
        row2.addWidget(MetricWidget("Login Time", "08:30", "", "Avg. Morning Login", 0, ""))
        row2.addWidget(MetricWidget("Session Length", "6.5", "hrs", "Hours", 0, ""))
        row2.addWidget(MetricWidget("Anomaly Score", "15", "%", "Risk Level", 15, "-2.1%"))
        dashboard_layout.addLayout(row2)
        
        # ========= Row 3 =========
        row3 = QHBoxLayout()
        row3.setSpacing(18)
        row3.addWidget(MetricWidget("File Access Rate", "42", "files/h", "Files/Hour", 0, ""))
        row3.addWidget(MetricWidget("Network Traffic", "2.1", "MB/m", "MB/Minute", 0, ""))
        row3.addWidget(MetricWidget("Error Rate", "1.2", "%", "System Errors", 1, ""))
        row3.addWidget(MetricWidget("Threats Detected", "3", "", "Active Alerts", 0, ""))
        dashboard_layout.addLayout(row3)

        # ========= Chart Section =========
        chart_title = QLabel("PERFORMANCE ANALYSIS")
        chart_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        chart_title.setStyleSheet("color: rgba(255,255,255,0.6); letter-spacing: 1.5px; margin-top: 10px; margin-bottom: 10px;")
        dashboard_layout.addWidget(chart_title)

        # شارت
        chart_widget = self.create_chart()
        dashboard_layout.addWidget(chart_widget)
        
        # إضافة stretch في النهاية
        dashboard_layout.addStretch()

        # وضع المحتوى مباشرة (بدون سكرول)
        content_area_layout = QVBoxLayout(self.content_area)
        content_area_layout.setContentsMargins(0, 0, 0, 0)
        content_area_layout.addWidget(self.dashboard_widget)
        
        # ========= ترتيب الإضافة =========
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.profile_menu)
        main_layout.addWidget(self.activity_menu)
        main_layout.addWidget(self.support_menu)
        main_layout.addWidget(self.content_area)

    def toggle_profile_menu(self):
        if self.profile_menu.isVisible():
            self.profile_menu.hide_menu()
        else:
            if self.activity_menu.isVisible():
                self.activity_menu.hide_menu()
            if self.support_menu.isVisible():
                self.support_menu.hide_menu()
            self.profile_menu.show_menu()

    def toggle_activity_menu(self):
        if self.activity_menu.isVisible():
            self.activity_menu.hide_menu()
        else:
            if self.profile_menu.isVisible():
                self.profile_menu.hide_menu()
            if self.support_menu.isVisible():
                self.support_menu.hide_menu()
            self.activity_menu.show_menu()

    def toggle_support_menu(self):
        if self.support_menu.isVisible():
            self.support_menu.hide_menu()
        else:
            if self.profile_menu.isVisible():
                self.profile_menu.hide_menu()
            if self.activity_menu.isVisible():
                self.activity_menu.hide_menu()
            self.support_menu.show_menu()

    def switch_page(self, page_name):
        print(f"Switching to page: {page_name}")
        if self.profile_menu.isVisible():
            self.profile_menu.hide_menu()
        if self.activity_menu.isVisible():
            self.activity_menu.hide_menu()
        if self.support_menu.isVisible():
            self.support_menu.hide_menu()

    def create_chart(self):
        # شارت بدون خلفية (شفاف)
        chart_widget = QWidget()
        chart_widget.setStyleSheet("background: transparent;")
        chart_widget.setMinimumHeight(340)
        
        layout = QVBoxLayout(chart_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Behavioral Metrics Over Time")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        subtitle_label = QLabel("Last 24 Hours")
        subtitle_label.setFont(QFont("Segoe UI", 11))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.4);")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        chart = CustomPlotWidget()
        chart.setBackground(None)
        chart.showGrid(x=True, y=True, alpha=0.15)
        
        axis_bottom = chart.getAxis('bottom')
        axis_left = chart.getAxis('left')
        axis_bottom.setPen(pg.mkPen(color='white', width=1))
        axis_left.setPen(pg.mkPen(color='white', width=1))
        axis_bottom.setTextPen('white')
        axis_left.setTextPen('white')
        
        hours = np.arange(0, 24, 0.1)
        typing_speed = 65 + 20 * np.sin(hours/3) + 10 * np.cos(hours/2)
        mouse_speed = 3.5 + 1.5 * np.sin(hours/2.5) + 0.8 * np.cos(hours/1.8) * 10
        click_freq = 3.0 + 3 * np.sin(hours/2) + 2 * np.cos(hours/1.5) * 10
        
        chart.plot(hours, typing_speed, pen=pg.mkPen("#2ec4ff", width=2.5), name="Typing Speed")
        chart.plot(hours, mouse_speed, pen=pg.mkPen("#ffffff", width=2.5), name="Mouse Speed")
        chart.plot(hours, click_freq, pen=pg.mkPen("#ff6b6b", width=2.5), name="Click Frequency")
        
        chart.plot(hours, typing_speed, fillLevel=0, brush=pg.mkBrush(color=(46, 196, 255, 20)), pen=None)
        chart.plot(hours, mouse_speed, fillLevel=0, brush=pg.mkBrush(color=(255, 255, 255, 10)), pen=None)
        chart.plot(hours, click_freq, fillLevel=0, brush=pg.mkBrush(color=(255, 107, 107, 10)), pen=None)
        
        lines_info = [
            {'data': typing_speed, 'x_data': hours, 'name': 'Typing Speed'},
            {'data': mouse_speed, 'x_data': hours, 'name': 'Mouse Speed'},
            {'data': click_freq, 'x_data': hours, 'name': 'Click Frequency'}
        ]
        chart.set_lines_info(lines_info)
        
        chart.setXRange(0, 24)
        chart.setYRange(0, 100)
        axis_bottom.setTicks([[(i, f"{i:02d}:00") for i in range(0, 25, 4)]])
        
        legend = chart.addLegend()
        legend.brush = pg.mkBrush(color=(255, 255, 255, 30))
        legend.setPen(pg.mkPen(color='white', width=0.5))
        
        chart.setLabel('bottom', 'Hour', color='rgba(255,255,255,0.5)', size='10pt')
        chart.setLabel('left', 'Value', color='rgba(255,255,255,0.5)', size='10pt')
        
        layout.addWidget(chart)
        
        return chart_widget

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())