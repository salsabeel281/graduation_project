# ui/splash_screen.py
from PyQt5.QtWidgets import (
    QSplashScreen, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt5.QtGui import (
    QFont, QPainter, QColor, QLinearGradient, QBrush,
    QPixmap, QPainterPath, QPen, QRadialGradient, QFontDatabase
)
import sys
import math


class ModernSplashScreen(QSplashScreen):
    """Modern splash screen with futuristic cybersecurity theme"""
    
    def __init__(self):
        # Create a pixmap for the splash screen
        self.width = 600
        self.height = 500
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.transparent)
        
        super().__init__(pixmap)
        
        # Set window flags for frameless window
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.SplashScreen
        )
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation properties
        self.glow_intensity = 0
        self.glow_direction = 1
        self.progress_value = 0
        
        # Start animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS for glow animation
        
        # Store custom font
        self.custom_font = None
        
    def update_animation(self):
        """Update glow animation"""
        # Update glow intensity (pulsing effect)
        self.glow_intensity += 0.05 * self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.glow_direction = 1
            
        # Update progress bar if it exists
        if hasattr(self, 'progress_bar') and self.progress_bar:
            if self.progress_value < 100:
                self.progress_value += 1
                self.progress_bar.setValue(self.progress_value)
        
        # Trigger repaint
        self.repaint()
        
    def drawContents(self, painter):
        """Custom drawing for the splash screen"""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Draw main background with gradient
        self.draw_background(painter)
        
        # Draw outer glow effect
        self.draw_outer_glow(painter)
        
        # Draw app icon container
        self.draw_icon_container(painter)
        
        # Draw icon symbol (shield with lock)
        self.draw_icon_symbol(painter)
        
        # Draw app name
        self.draw_app_name(painter)
        
        # Draw tagline
        self.draw_tagline(painter)
        
        # Draw loading section
        self.draw_loading_section(painter)
        
        # Draw version info
        self.draw_version_info(painter)
        
    def draw_background(self, painter):
        """Draw dark blue gradient background"""
        # Main gradient
        gradient = QLinearGradient(0, 0, self.width, self.height)
        gradient.setColorAt(0, QColor(11, 22, 67))      # #0B1643
        gradient.setColorAt(0.5, QColor(16, 28, 78))    # #101C4E
        gradient.setColorAt(1, QColor(8, 18, 58))       # #08123A
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width, self.height, 25, 25)
        
        # Add subtle grid pattern
        painter.setPen(QPen(QColor(74, 111, 255, 30), 1))
        for i in range(0, self.width, 30):
            painter.drawLine(i, 0, i, self.height)
        for i in range(0, self.height, 30):
            painter.drawLine(0, i, self.width, i)
        
        # Add subtle corner accents
        self.draw_corner_accents(painter)
        
    def draw_corner_accents(self, painter):
        """Draw decorative corner accents"""
        accent_color = QColor(74, 111, 255, 80)
        painter.setPen(QPen(accent_color, 2))
        
        # Top-left corner
        painter.drawLine(30, 15, 60, 15)
        painter.drawLine(15, 30, 15, 60)
        
        # Top-right corner
        painter.drawLine(self.width - 30, 15, self.width - 60, 15)
        painter.drawLine(self.width - 15, 30, self.width - 15, 60)
        
        # Bottom-left corner
        painter.drawLine(30, self.height - 15, 60, self.height - 15)
        painter.drawLine(15, self.height - 30, 15, self.height - 60)
        
        # Bottom-right corner
        painter.drawLine(self.width - 30, self.height - 15, self.width - 60, self.height - 15)
        painter.drawLine(self.width - 15, self.height - 30, self.width - 15, self.height - 60)
        
    def draw_outer_glow(self, painter):
        """Draw outer glow effect behind the icon"""
        center_x = self.width // 2
        center_y = 180
        
        # Create radial gradient for glow
        glow_gradient = QRadialGradient(center_x, center_y, 120)
        glow_gradient.setColorAt(0, QColor(74, 111, 255, 60))
        glow_gradient.setColorAt(0.5, QColor(74, 111, 255, 20))
        glow_gradient.setColorAt(1, QColor(74, 111, 255, 0))
        
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 120, center_y - 120, 240, 240)
        
        # Pulsing glow effect
        pulse_size = 100 + (self.glow_intensity * 30)
        pulse_gradient = QRadialGradient(center_x, center_y, pulse_size)
        pulse_gradient.setColorAt(0, QColor(74, 111, 255, int(40 * self.glow_intensity)))
        pulse_gradient.setColorAt(1, QColor(74, 111, 255, 0))
        
        painter.setBrush(QBrush(pulse_gradient))
        painter.drawEllipse(center_x - pulse_size, center_y - pulse_size, pulse_size * 2, pulse_size * 2)
        
    def draw_icon_container(self, painter):
        """Draw the app icon container with rounded corners"""
        center_x = self.width // 2
        center_y = 180
        icon_size = 120
        
        # Container rectangle
        icon_rect = QRect(center_x - icon_size//2, center_y - icon_size//2, icon_size, icon_size)
        
        # Create rounded rectangle path
        path = QPainterPath()
        radius = 25
        path.addRoundedRect(icon_rect, radius, radius)
        
        # Draw gradient background
        gradient = QLinearGradient(icon_rect.topLeft(), icon_rect.bottomRight())
        gradient.setColorAt(0, QColor(30, 45, 100))
        gradient.setColorAt(0.5, QColor(20, 35, 85))
        gradient.setColorAt(1, QColor(15, 25, 70))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(74, 111, 255, 150), 2))
        painter.drawPath(path)
        
        # Add inner border glow
        inner_path = QPainterPath()
        inner_rect = icon_rect.adjusted(3, 3, -3, -3)
        inner_path.addRoundedRect(inner_rect, radius - 3, radius - 3)
        painter.setPen(QPen(QColor(74, 111, 255, 100), 1))
        painter.drawPath(inner_path)
        
    def draw_icon_symbol(self, painter):
        """Draw the security symbol (shield with lock and eye)"""
        center_x = self.width // 2
        center_y = 180
        icon_size = 120
        
        # Draw shield shape
        shield_width = 60
        shield_height = 70
        shield_x = center_x - shield_width // 2
        shield_y = center_y - shield_height // 2 + 5
        
        # Create shield path
        shield_path = QPainterPath()
        shield_path.moveTo(shield_x + shield_width//2, shield_y)
        shield_path.lineTo(shield_x + shield_width - 10, shield_y + 15)
        shield_path.lineTo(shield_x + shield_width - 10, shield_y + shield_height - 20)
        shield_path.lineTo(shield_x + shield_width//2, shield_y + shield_height)
        shield_path.lineTo(shield_x + 10, shield_y + shield_height - 20)
        shield_path.lineTo(shield_x + 10, shield_y + 15)
        shield_path.closeSubpath()
        
        # Fill shield with gradient
        shield_gradient = QLinearGradient(shield_x, shield_y, shield_x + shield_width, shield_y + shield_height)
        shield_gradient.setColorAt(0, QColor(74, 111, 255, 230))
        shield_gradient.setColorAt(1, QColor(44, 81, 205, 230))
        
        painter.setBrush(QBrush(shield_gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
        painter.drawPath(shield_path)
        
        # Draw lock inside shield
        lock_width = 24
        lock_height = 28
        lock_x = center_x - lock_width // 2
        lock_y = center_y - lock_height // 2 + 5
        
        # Lock body
        lock_body = QPainterPath()
        lock_body.addRoundedRect(lock_x, lock_y + 8, lock_width, lock_height - 8, 4, 4)
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(lock_body)
        
        # Lock shackle
        shackle_path = QPainterPath()
        shackle_path.arcMoveTo(lock_x + 6, lock_y - 2, 12, 14, 0)
        shackle_path.arcTo(lock_x + 6, lock_y - 2, 12, 14, 0, 180)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 3))
        painter.drawPath(shackle_path)
        
        # Draw eye symbol in the center of lock
        eye_x = center_x
        eye_y = center_y + 8
        
        # Eye outline
        painter.setPen(QPen(QColor(74, 111, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255, 50)))
        painter.drawEllipse(eye_x - 8, eye_y - 4, 16, 10)
        
        # Eye pupil
        painter.setBrush(QBrush(QColor(74, 111, 255, 200)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(eye_x - 2, eye_y - 2, 4, 4)
        
        # Eye highlight
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawEllipse(eye_x - 1, eye_y - 3, 2, 2)
        
    def draw_app_name(self, painter):
        """Draw the application name with glow effect"""
        center_x = self.width // 2
        app_name = "sentinail_x"
        
        # Load custom font or use default
        font = QFont("Segoe UI", 32, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        painter.setFont(font)
        
        # Calculate text position
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.width(app_name)
        text_x = center_x - text_width // 2
        text_y = 290
        
        # Draw text shadow/glow layers for neon effect
        glow_color = QColor(74, 111, 255, int(100 * self.glow_intensity))
        
        for offset in range(5, 0, -1):
            painter.setPen(QPen(glow_color, 1))
            painter.drawText(text_x - offset, text_y, app_name)
            painter.drawText(text_x + offset, text_y, app_name)
            painter.drawText(text_x, text_y - offset, app_name)
            painter.drawText(text_x, text_y + offset, app_name)
        
        # Draw main text with gradient
        text_gradient = QLinearGradient(text_x, text_y - 20, text_x + text_width, text_y)
        text_gradient.setColorAt(0, QColor(255, 255, 255))
        text_gradient.setColorAt(0.5, QColor(200, 220, 255))
        text_gradient.setColorAt(1, QColor(74, 111, 255))
        
        painter.setPen(QPen(QBrush(text_gradient), 1))
        painter.drawText(text_x, text_y, app_name)
        
        # Draw underline accent
        underline_y = text_y + 5
        painter.setPen(QPen(QColor(74, 111, 255, 200), 2))
        painter.drawLine(text_x + 20, underline_y, text_x + text_width - 20, underline_y)
        
    def draw_tagline(self, painter):
        """Draw the tagline text"""
        center_x = self.width // 2
        tagline = "Advanced Cybersecurity Protection"
        
        font = QFont("Segoe UI", 11)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        painter.setFont(font)
        
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.width(tagline)
        text_x = center_x - text_width // 2
        
        painter.setPen(QPen(QColor(140, 160, 200), 1))
        painter.drawText(text_x, 330, tagline)
        
    def draw_loading_section(self, painter):
        """Draw the loading progress bar"""
        center_x = self.width // 2
        bar_width = 300
        bar_height = 3
        bar_x = center_x - bar_width // 2
        bar_y = 380
        
        # Draw background track
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(40, 50, 90)))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 2, 2)
        
        # Draw progress
        progress_width = int((self.progress_value / 100) * bar_width)
        if progress_width > 0:
            # Gradient for progress bar
            progress_gradient = QLinearGradient(bar_x, bar_y, bar_x + bar_width, bar_y)
            progress_gradient.setColorAt(0, QColor(74, 111, 255))
            progress_gradient.setColorAt(1, QColor(100, 150, 255))
            
            painter.setBrush(QBrush(progress_gradient))
            painter.drawRoundedRect(bar_x, bar_y, progress_width, bar_height, 2, 2)
            
            # Add glowing effect to progress
            if progress_width > 10:
                glow_gradient = QLinearGradient(bar_x + progress_width - 20, bar_y, bar_x + progress_width, bar_y)
                glow_gradient.setColorAt(0, QColor(74, 111, 255, 100))
                glow_gradient.setColorAt(1, QColor(74, 111, 255, 0))
                painter.setBrush(QBrush(glow_gradient))
                painter.drawRoundedRect(bar_x + progress_width - 20, bar_y - 2, 20, bar_height + 4, 4, 4)
        
        # Draw percentage text
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.setPen(QPen(QColor(140, 160, 200), 1))
        painter.drawText(center_x - 20, bar_y - 10, f"{self.progress_value}%")
        
        # Draw loading dots animation
        dots = "." * (int(self.progress_value / 10) % 4)
        painter.drawText(center_x + 20, bar_y - 10, f"Loading{dots}")
        
    def draw_version_info(self, painter):
        """Draw version information at the bottom"""
        version_text = "Version 2.0.0 | © 2024 SentinelX Security"
        
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.width(version_text)
        
        painter.setPen(QPen(QColor(100, 120, 160), 1))
        painter.drawText(self.width - text_width - 20, self.height - 20, version_text)
        
    def showEvent(self, event):
        """Override show event to center the splash screen"""
        super().showEvent(event)
        
        # Center on screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width) // 2
        y = (screen_geometry.height() - self.height) // 2
        self.move(x, y)
        
    def finish_splash(self, main_window):
        """Finish splash screen with fade out effect"""
        # Stop animation timer
        self.animation_timer.stop()
        
        # Create fade out animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.finished.connect(lambda: super().finish(main_window))
        self.fade_animation.start()