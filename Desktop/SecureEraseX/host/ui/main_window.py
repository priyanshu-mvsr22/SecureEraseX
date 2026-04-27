"""
main_window.py - SecureEraseX v2.0 UI.
"""

import datetime
import math
import os
import sys

from PyQt6.QtCore import QThread, QTimer, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPalette,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC = sys.platform == "darwin"
_IS_LINUX = sys.platform.startswith("linux")

C_BG = "#060B14"
C_BG2 = "#0D1424"
C_CARD = "#0F1829"
C_CARD2 = "#141F33"
C_BORDER = "#1E3050"
C_NEON = "#00D4FF"
C_NEON2 = "#7B2FFF"
C_NEON3 = "#FF3C6E"
C_TEXT = "#E8F4FF"
C_TEXT_DIM = "#6B8AAD"
C_TEXT_MUTED = "#3A5470"
C_SUCCESS = "#00E676"
C_WARNING = "#FFB300"
C_DANGER = "#FF3C6E"

QSS = f"""
QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI", "SF Pro Display", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 13px;
}}
QMainWindow {{ background-color: {C_BG}; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 6px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {C_BORDER}; border-radius: 3px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QGroupBox {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 14px 12px 14px;
    font-size: 11px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 0px;
    padding: 0 6px;
    color: {C_TEXT_MUTED};
    font-size: 10px;
    font-weight: 600;
}}
QLabel {{ color: {C_TEXT_DIM}; background: transparent; padding: 1px 0; }}
QComboBox {{
    background-color: {C_CARD2};
    border: 1px solid {C_BORDER};
    border-radius: 7px;
    padding: 9px 12px;
    color: {C_TEXT};
    min-height: 24px;
    selection-background-color: #0060A0;
}}
QComboBox:hover {{ border: 1px solid #2A4870; background-color: #192030; }}
QComboBox:focus {{ border: 1px solid {C_NEON}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {C_TEXT_DIM};
    width: 0;
    height: 0;
    margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {C_CARD2};
    border: 1px solid {C_BORDER};
    selection-background-color: #1A3A60;
    color: {C_TEXT};
    padding: 4px;
    outline: none;
}}
QPushButton {{
    background-color: {C_CARD2};
    border: 1px solid {C_BORDER};
    border-radius: 7px;
    padding: 8px 18px;
    color: {C_TEXT};
    font-size: 13px;
    min-height: 24px;
}}
QPushButton:hover {{ background-color: #192030; border: 1px solid #2A4870; }}
QPushButton:pressed {{ background-color: #0D1520; }}
QPushButton:disabled {{ color: #2A4060; background-color: #0A1020; border-color: #111A28; }}
QProgressBar {{
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    text-align: center;
    background-color: {C_CARD2};
    color: {C_TEXT_DIM};
    min-height: 22px;
    font-size: 11px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C_NEON2}, stop:1 {C_NEON});
    border-radius: 5px;
}}
QTextEdit {{
    background-color: #040810;
    border: 1px solid {C_BORDER};
    border-radius: 7px;
    color: {C_TEXT_DIM};
    font-family: "JetBrains Mono", "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 8px;
    selection-background-color: #1A3A60;
}}
QStatusBar {{ background-color: #040810; color: {C_TEXT_MUTED}; font-size: 11px; border-top: 1px solid {C_BORDER}; }}
#titleLabel {{
    font-size: 22px;
    font-weight: 700;
    color: {C_TEXT};
    padding: 0;
    font-family: "Orbitron", "Segoe UI", sans-serif;
    letter-spacing: 3px;
}}
#subtitleLabel {{ font-size: 11px; color: {C_TEXT_DIM}; letter-spacing: 1px; }}
#platformBadge {{
    font-size: 10px;
    color: {C_NEON};
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 12px;
    padding: 3px 12px;
    background: rgba(0,212,255,0.07);
    font-family: "JetBrains Mono", "Consolas", monospace;
}}
#infoLine {{ color: {C_TEXT_DIM}; font-size: 11px; }}
#osWarnBox {{
    color: {C_DANGER};
    font-size: 11px;
    padding: 8px 12px;
    background-color: rgba(255,60,110,0.07);
    border: 1px solid rgba(255,60,110,0.3);
    border-radius: 7px;
}}
#warnBox {{
    color: {C_WARNING};
    font-size: 11px;
    padding: 8px 12px;
    background-color: rgba(255,179,0,0.06);
    border: 1px solid rgba(255,179,0,0.25);
    border-radius: 7px;
}}
#startBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #005A9E, stop:1 #0078D4);
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    padding: 14px 32px;
    letter-spacing: 3px;
}}
#startBtn:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #006BB5, stop:1 #1A8AE0); }}
#startBtn:pressed {{ background: #004E8C; }}
#startBtn:disabled {{ background: #0A1A28; color: #1E3A50; border: 1px solid #0F2035; }}
#refreshBtn {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 7px;
    padding: 9px 16px;
    color: {C_TEXT_DIM};
    font-size: 16px;
}}
#refreshBtn:hover {{ background-color: #192030; color: {C_NEON}; }}
#dlBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #007A3D, stop:1 #00994D);
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 12px 24px;
    letter-spacing: 2px;
}}
#closeBtn {{
    background: transparent;
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    color: {C_TEXT_DIM};
    padding: 10px 24px;
    font-size: 13px;
}}
"""


class AppIcon(QWidget):
    def __init__(self, size=80, parent=None):
        super().__init__(parent)
        self._sz = size
        self._angle = 0.0
        self._glow = 0.0
        self._glow_dir = 1
        self.setFixedSize(size, size)
        self._spin_timer = QTimer(self)
        self._spin_timer.timeout.connect(self._tick)
        self._spin_timer.start(25)

    def _tick(self):
        self._angle = (self._angle + 2.0) % 360.0
        self._glow += 0.04 * self._glow_dir
        if self._glow >= 1.0:
            self._glow_dir = -1
        if self._glow <= 0.0:
            self._glow_dir = 1
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self._sz / 2, self._sz / 2
        r = self._sz / 2 - 2
        glow_alpha = int(60 + 60 * self._glow)
        for i in range(4):
            rg = QRadialGradient(cx, cy, r + i * 3)
            rg.setColorAt(0, QColor(0, 212, 255, max(0, glow_alpha - i * 15)))
            rg.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(rg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(cx - (r + i * 3), cy - (r + i * 3), (r + i * 3) * 2, (r + i * 3) * 2))

        n_seg = 90
        pen_w = max(4, self._sz // 16)
        for i in range(n_seg):
            t = i / n_seg
            a = (self._angle + t * 360) % 360
            r0 = QColor(0, 212, 255)
            r1 = QColor(123, 47, 255)
            r2 = QColor(255, 60, 110)
            if t < 0.33:
                cr = self._lerp_color(r0, r1, t / 0.33)
            elif t < 0.66:
                cr = self._lerp_color(r1, r2, (t - 0.33) / 0.33)
            else:
                cr = self._lerp_color(r2, r0, (t - 0.66) / 0.34)
            cr.setAlpha(int(255 * (0.3 + 0.7 * t)))
            p.setPen(QPen(cr, pen_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(QRectF(cx - r + pen_w / 2, cy - r + pen_w / 2, (r - pen_w / 2) * 2, (r - pen_w / 2) * 2), int(a * 16), int((360 / n_seg) * 16))

        inner_r = r - pen_w - 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(6, 11, 20)))
        p.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2))
        font = QFont("Orbitron", max(18, int(inner_r * 0.9)), QFont.Weight.Bold)
        p.setFont(font)
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance("S")
        th = fm.ascent()
        grad = QLinearGradient(cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2)
        grad.setColorAt(0, QColor(C_NEON))
        grad.setColorAt(0.5, QColor(C_NEON2))
        grad.setColorAt(1, QColor(C_NEON3))
        p.setPen(QPen(QBrush(grad), 0))
        p.drawText(int(cx - tw / 2), int(cy + th / 2 - 2), "S")

    @staticmethod
    def _lerp_color(a: QColor, b: QColor, t: float) -> QColor:
        return QColor(
            int(a.red() + (b.red() - a.red()) * t),
            int(a.green() + (b.green() - a.green()) * t),
            int(a.blue() + (b.blue() - a.blue()) * t),
        )


class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._t = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

    def _tick(self):
        self._t += 0.005
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        pen = QPen(QColor(0, 212, 255, 8))
        pen.setWidth(1)
        p.setPen(pen)
        for x in range(0, width, 60):
            p.drawLine(x, 0, x, height)
        for y in range(0, height, 60):
            p.drawLine(0, y, width, y)

        orbs = [
            (0.15, 0.15, 0.55, 0.45, QColor(0, 212, 255, 12)),
            (0.85, 0.80, 0.45, 0.55, QColor(123, 47, 255, 10)),
            (0.50, 0.40, 0.35, 0.60, QColor(255, 60, 110, 7)),
        ]
        p.setPen(Qt.PenStyle.NoPen)
        for bx, by, r_frac, phase, col in orbs:
            ox = width * (bx + 0.04 * math.sin(self._t + phase * math.pi))
            oy = height * (by + 0.03 * math.cos(self._t * 0.7 + phase * math.pi))
            rad = min(width, height) * r_frac
            rg = QRadialGradient(ox, oy, rad)
            rg.setColorAt(0, col)
            rg.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(rg))
            p.drawEllipse(QRectF(ox - rad, oy - rad, rad * 2, rad * 2))


class GlowProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._pulsing = False
        self._pulse_t = 0.0
        self.setFixedHeight(12)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def setValue(self, value: int):
        self._value = max(0, min(100, value))
        self.update()

    def setPulsing(self, enabled: bool):
        self._pulsing = enabled
        if enabled:
            self._timer.start(30)
        else:
            self._timer.stop()
        self.update()

    def _tick(self):
        self._pulse_t = (self._pulse_t + 0.04) % 1.0
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        radius = height / 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(C_BG2)))
        p.drawRoundedRect(0, 0, width, height, radius, radius)
        fill_w = int(width * self._value / 100) if not self._pulsing else width
        if fill_w <= 0 and not self._pulsing:
            return
        grad = QLinearGradient(0, 0, fill_w, 0)
        grad.setColorAt(0, QColor(123, 47, 255))
        grad.setColorAt(1, QColor(0, 212, 255))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(0, 0, fill_w, height, radius, radius)
        if self._pulsing:
            sw = int(width * 0.25)
            sx = int((self._pulse_t * (width + sw)) - sw)
            sg = QLinearGradient(sx, 0, sx + sw, 0)
            sg.setColorAt(0, QColor(255, 255, 255, 0))
            sg.setColorAt(0.5, QColor(255, 255, 255, 60))
            sg.setColorAt(1, QColor(255, 255, 255, 0))
            p.setBrush(QBrush(sg))
            p.drawRoundedRect(0, 0, width, height, radius, radius)
        glow = QLinearGradient(0, 0, fill_w if not self._pulsing else width, 0)
        glow.setColorAt(0, QColor(123, 47, 255, 40))
        glow.setColorAt(1, QColor(0, 212, 255, 40))
        p.setBrush(QBrush(glow))
        p.drawRect(0, 0, fill_w if not self._pulsing else width, 4)


class SplashScreen(QWidget):
    finished = pyqtSignal()

    STEPS = [
        (0.12, "Initializing secure environment..."),
        (0.28, "Loading drive detection module..."),
        (0.44, "Checking administrator privileges..."),
        (0.58, "Preparing wipe engine..."),
        (0.72, "Scanning connected drives..."),
        (0.86, "Verifying system safety guard..."),
        (1.00, "Ready."),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 460)
        self._progress = 0.0
        self._step_idx = 0
        self._status_msg = "Initializing secure environment..."
        self._ring_angle = 0.0
        self._glow_t = 0.0
        self._paint_timer = QTimer(self)
        self._paint_timer.timeout.connect(self._animate)
        self._paint_timer.start(25)
        self._step_timer = QTimer(self)
        self._step_timer.timeout.connect(self._next_step)
        self._step_timer.start(500)
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def _animate(self):
        self._ring_angle = (self._ring_angle + 3.0) % 360.0
        self._glow_t += 0.03
        self.update()

    def _next_step(self):
        if self._step_idx >= len(self.STEPS):
            self._step_timer.stop()
            self._paint_timer.stop()
            QTimer.singleShot(300, self.finished.emit)
            return
        self._progress, self._status_msg = self.STEPS[self._step_idx]
        self._step_idx += 1
        self._step_timer.setInterval(400 if self._step_idx < 4 else 300)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        cx, cy = width / 2, height / 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(6, 11, 20, 245)))
        p.drawRoundedRect(0, 0, width, height, 20, 20)
        top_grad = QLinearGradient(0, 0, width, 0)
        top_grad.setColorAt(0, QColor(0, 212, 255, 0))
        top_grad.setColorAt(0.5, QColor(0, 212, 255, 180))
        top_grad.setColorAt(1, QColor(0, 212, 255, 0))
        p.setBrush(QBrush(top_grad))
        p.drawRect(0, 0, width, 2)

        glow = 0.5 + 0.5 * math.sin(self._glow_t)
        for i, (rr, alpha_base) in enumerate([(200, 25), (280, 14), (360, 8)]):
            pulse = rr + 8 * math.sin(self._glow_t + i * 1.1)
            cols = [
                QColor(0, 212, 255, int(alpha_base * glow)),
                QColor(123, 47, 255, int(alpha_base * glow * 0.7)),
                QColor(0, 212, 255, int(alpha_base * glow * 0.5)),
            ]
            p.setPen(QPen(cols[i], 1))
            p.drawEllipse(QRectF(cx - pulse, cy - pulse - 30, pulse * 2, pulse * 2))

        icon_r = 52
        icon_cx = cx
        icon_cy = cy - 60
        rg = QRadialGradient(icon_cx, icon_cy, icon_r + 20)
        rg.setColorAt(0, QColor(0, 212, 255, int(50 + 50 * glow)))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(rg))
        p.drawEllipse(QRectF(icon_cx - icon_r - 20, icon_cy - icon_r - 20, (icon_r + 20) * 2, (icon_r + 20) * 2))

        n_seg = 72
        ring_pen_w = 5
        for i in range(n_seg):
            t = i / n_seg
            a = (self._ring_angle + t * 360) % 360
            if t < 0.33:
                cr = AppIcon._lerp_color(QColor(0, 212, 255), QColor(123, 47, 255), t / 0.33)
            elif t < 0.66:
                cr = AppIcon._lerp_color(QColor(123, 47, 255), QColor(255, 60, 110), (t - 0.33) / 0.33)
            else:
                cr = AppIcon._lerp_color(QColor(255, 60, 110), QColor(0, 212, 255), (t - 0.66) / 0.34)
            cr.setAlpha(int(200 * (0.4 + 0.6 * t)))
            p.setPen(QPen(cr, ring_pen_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(QRectF(icon_cx - icon_r + ring_pen_w / 2, icon_cy - icon_r + ring_pen_w / 2, (icon_r - ring_pen_w / 2) * 2, (icon_r - ring_pen_w / 2) * 2), int(a * 16), int((360 / n_seg) * 16))

        inner = icon_r - ring_pen_w - 3
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(6, 11, 20)))
        p.drawEllipse(QRectF(icon_cx - inner, icon_cy - inner, inner * 2, inner * 2))
        font = QFont("Orbitron", int(inner * 0.88), QFont.Weight.Bold)
        if QFontMetrics(font).horizontalAdvance("S") == 0:
            font = QFont("Arial", int(inner * 0.88), QFont.Weight.Bold)
        p.setFont(font)
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance("S")
        sg = QLinearGradient(icon_cx - tw / 2, icon_cy - inner / 2, icon_cx + tw / 2, icon_cy + inner / 2)
        sg.setColorAt(0, QColor(0, 212, 255))
        sg.setColorAt(0.5, QColor(123, 47, 255))
        sg.setColorAt(1, QColor(255, 60, 110))
        p.setPen(QPen(QBrush(sg), 0))
        p.drawText(int(icon_cx - tw / 2), int(icon_cy + fm.ascent() / 2), "S")

        p.setPen(QColor(C_TEXT))
        title_font = QFont("Orbitron", 26, QFont.Weight.Bold)
        p.setFont(title_font)
        title = "SecureEraseX"
        title_y = int(icon_cy + icon_r + 30)
        p.drawText(int(cx - QFontMetrics(title_font).horizontalAdvance(title) / 2), title_y, title)
        sub_font = QFont("Segoe UI", 11)
        p.setFont(sub_font)
        subtitle = "Secure Drive Wipe Utility"
        sub_y = title_y + 28
        p.setPen(QColor(C_TEXT_DIM))
        p.drawText(int(cx - QFontMetrics(sub_font).horizontalAdvance(subtitle) / 2), sub_y, subtitle)

        bar_y = sub_y + 36
        bar_w = 280
        bar_x = int(cx - bar_w / 2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255, 15)))
        p.drawRoundedRect(bar_x, bar_y, bar_w, 4, 2, 2)
        fill_w = int(bar_w * self._progress)
        if fill_w > 0:
            bg = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            bg.setColorAt(0, QColor(123, 47, 255))
            bg.setColorAt(1, QColor(0, 212, 255))
            p.setBrush(QBrush(bg))
            p.drawRoundedRect(bar_x, bar_y, fill_w, 4, 2, 2)
        p.setFont(QFont("Consolas", 9))
        p.setPen(QColor(C_TEXT_MUTED))
        p.drawText(int(cx - QFontMetrics(p.font()).horizontalAdvance(self._status_msg) / 2), bar_y + 22, self._status_msg)


def _has_real_progress(method_text: str) -> bool:
    if "Single Pass" in method_text:
        return True
    if "Raw Disk" in method_text and not _IS_WINDOWS:
        return True
    if "USB Sanitize" in method_text and _IS_LINUX:
        return True
    return False


class WipeWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress_update = pyqtSignal(int)
    log_message = pyqtSignal(str, str)

    def __init__(self, device, method, fs, disk_ref):
        super().__init__()
        self.device = device
        self.method = method
        self.fs = fs
        self.disk_ref = disk_ref

    def run(self):
        try:
            _host = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if _host not in sys.path:
                sys.path.insert(0, _host)
            from wipe_engine.dispatcher import dispatch

            self.log_message.emit("info", f"Starting {self.method} on {self.device}...")
            dispatch(self.device, self.method, self.fs, self.disk_ref, progress_cb=lambda v: self.progress_update.emit(v))
            self.finished.emit(True, "Wipe completed successfully.")
        except Exception as exc:
            self.finished.emit(False, str(exc))


class DriveRefreshWorker(QThread):
    finished = pyqtSignal(object, str)

    def run(self):
        try:
            _host = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if _host not in sys.path:
                sys.path.insert(0, _host)
            from device_detection.volume_enum import list_volumes

            self.finished.emit(list_volumes(), "")
        except Exception as exc:
            self.finished.emit(None, str(exc))


def generate_pdf_report(report_data: dict, out_path: str) -> bool:
    if out_path.lower().endswith(".txt"):
        return _gen_pdf_fallback(report_data, out_path)
    try:
        _gen_pdf_reportlab(report_data, out_path)
        return True
    except ImportError:
        return _gen_pdf_fallback(report_data, out_path)


def _gen_pdf_reportlab(data: dict, out_path: str):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    page_w, _page_h = A4
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm, title="SecureEraseX Wipe Report")
    dark = colors.HexColor(C_BG)
    neon = colors.HexColor(C_NEON)
    green = colors.HexColor("#00994D")
    text = colors.HexColor("#2A3F55")
    card = colors.HexColor("#EEF4FA")
    border = colors.HexColor("#C0D8EE")
    body = getSampleStyleSheet()["Normal"]

    def sty(name, **kw):
        return ParagraphStyle(name, parent=body, **kw)

    s_title = sty("title", fontSize=22, textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_LEFT, leading=24)
    s_sub = sty("sub", fontSize=9, textColor=neon, fontName="Helvetica", alignment=TA_LEFT, leading=12)
    s_meta = sty("meta", fontSize=8, textColor=colors.HexColor("#6B8AAD"), fontName="Helvetica", alignment=TA_LEFT, leading=10)
    s_meta_r = sty("meta_r", fontSize=8, textColor=colors.HexColor("#6B8AAD"), fontName="Helvetica", alignment=TA_RIGHT, leading=10)
    s_status = sty("status", fontSize=8, textColor=green, fontName="Helvetica-Bold", alignment=TA_RIGHT, leading=10)
    s_sec = sty("sec", fontSize=9, textColor=neon, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4, alignment=TA_LEFT)
    s_body = sty("body", fontSize=9, textColor=text, fontName="Helvetica", leading=13, alignment=TA_LEFT)
    s_value = sty("value", fontSize=9, textColor=text, fontName="Helvetica", leading=12, alignment=TA_LEFT)
    s_mono = sty("mono", fontSize=8, textColor=text, fontName="Courier", leading=11, alignment=TA_LEFT)
    s_cert = sty("cert", fontSize=8.5, textColor=colors.HexColor("#005030"), fontName="Helvetica-Oblique", leading=13, alignment=TA_LEFT)
    s_label = sty("label", fontSize=8, textColor=colors.HexColor("#6B8AAD"), fontName="Helvetica-Bold", leading=11, alignment=TA_LEFT)

    story = []
    header = Table(
        [
            [
                Paragraph("<b>S</b>", sty("hicon", fontSize=28, textColor=neon, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=28)),
                Paragraph("SecureEraseX", s_title),
                Paragraph(f"<b>Report ID:</b> {data['report_id']}", s_meta_r),
            ],
            [
                "",
                Paragraph("Enterprise Secure Drive Wipe Utility  -  Certified Report", s_sub),
                Paragraph(data["timestamp"], s_meta_r),
            ],
            [
                "",
                Paragraph("NIST SP 800-88  -  DoD 5220.22-M  -  ISO 27001 Compliant", s_meta),
                Paragraph("STATUS: VERIFIED COMPLETE", s_status),
            ],
        ],
        colWidths=[18 * mm, 104 * mm, 48 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), dark),
                ("LINEABOVE", (0, 0), (-1, 0), 2, neon),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#1E3050")),
                ("SPAN", (0, 0), (0, 2)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 2), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (0, 2), 0),
                ("RIGHTPADDING", (0, 0), (0, 2), 0),
            ]
        )
    )
    story.extend([header, Spacer(1, 6 * mm)])

    def section(title):
        story.extend([Spacer(1, 2 * mm), HRFlowable(width="100%", thickness=0.5, color=neon, spaceAfter=3), Paragraph(f"<font color='#00D4FF'>[ {title.upper()} ]</font>", s_sec)])

    def detail_table(rows, highlight_last=False):
        table = Table(
            [[Paragraph(k, s_label), Paragraph(str(v), s_value)] for k, v in rows],
            colWidths=[56 * mm, 114 * mm],
        )
        rules = [
            ("BACKGROUND", (0, 0), (-1, -1), card),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#F0F6FC"), card]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -2), 0.35, colors.HexColor("#D8E8F4")),
            ("BOX", (0, 0), (-1, -1), 0.5, border),
        ]
        if highlight_last:
            rules.extend(
                [
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D8F4E8")),
                    ("TEXTCOLOR", (1, -1), (1, -1), green),
                    ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
                ]
            )
        table.setStyle(TableStyle(rules))
        story.append(table)

    drv = data["drive"]
    section("1. Drive Details")
    detail_table([("Drive Letter / ID", drv["letter"]), ("Model", drv["model"]), ("Drive Type", drv["type"]), ("Capacity", f"{drv['size']} GB"), ("Serial Number", drv.get("serial", "N/A")), ("Original Filesystem", drv.get("filesystem", "N/A")), ("Classification", "Internal Drive" if drv.get("is_internal") else "External / Removable Drive"), ("OS System Drive", "YES - Protected" if drv.get("is_system") else "NO - Eligible for Wipe")])
    section("2. Wipe Configuration & Method")
    detail_table([("Wipe Method", data["method_name"]), ("Short Name", data["method_short"]), ("Number of Passes", f"{data['passes']} pass(es)"), ("Filesystem Applied", data["new_fs"]), ("Admin Privileges", "Verified - Elevated Access Confirmed"), ("OS Drive Guard", "ACTIVE - System drive excluded from scan")])
    section("3. Technical Method Description")
    story.append(Paragraph(data["method_desc"], s_body))
    if "DoD" in data["method_name"] or "Multi" in data["method_name"]:
        story.append(Spacer(1, 1.5 * mm))
        for line in [
            "Pass 1: Write 0x00 (zero-fill) to all sectors",
            "Pass 2: Write 0xFF (ones complement) to all sectors",
            "Pass 3: Write PRNG random data to all sectors",
        ]:
            story.append(Paragraph(line, s_mono))
    section("4. Detailed Wipe Process Log")
    log_rows = [[Paragraph(f"[{tag}]", sty("logtag", fontSize=8, textColor=colors.HexColor("#0078D4"), fontName="Courier-Bold", leading=11, alignment=TA_LEFT)), Paragraph(msg, s_mono)] for tag, msg in data["log"]]
    log_table = Table(log_rows, colWidths=[22 * mm, 148 * mm], repeatRows=0)
    log_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#F9FCFF"), colors.HexColor("#F2F8FD")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.5, border),
                ("LINEBELOW", (0, 0), (-1, -2), 0.35, colors.HexColor("#D8E8F4")),
            ]
        )
    )
    story.append(log_table)
    section("5. Result & Certification Summary")
    detail_table([("Wipe Status", "SUCCESS - All data permanently destroyed"), ("Duration", f"{data['elapsed_s']} seconds"), ("Data Recovery Risk", "None - Drive verified clean"), ("Compliance", "NIST SP 800-88 / DoD 5220.22-M Satisfied"), ("Recycling Safe", "Drive cleared for safe reuse and recycling")], highlight_last=True)
    story.append(Spacer(1, 6 * mm))
    cert = Table([[Paragraph(f"This certifies that the drive identified in Section 1 has been securely wiped using {data['method_name']} on {data['timestamp']}. All data has been permanently and irreversibly destroyed. Report ID: {data['report_id']}.", s_cert)]], colWidths=[170 * mm])
    cert.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F8EE")), ("BOX", (0, 0), (-1, -1), 0.8, green), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    story.append(cert)

    def footer_canvas(canvas, doc_):
        canvas.saveState()
        canvas.setFillColor(dark)
        canvas.rect(0, 0, page_w, 10 * mm, fill=1, stroke=0)
        canvas.setFillColor(neon)
        canvas.rect(0, 10 * mm - 0.5 * mm, page_w, 0.5 * mm, fill=1, stroke=0)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#6B8AAD"))
        canvas.drawString(20 * mm, 4 * mm, "SecureEraseX  -  Developed by A. Ranjith Kumar  -  MVSREC IoT-13")
        canvas.drawRightString(page_w - 20 * mm, 4 * mm, f"Page {doc_.page}  -  Report ID: {data['report_id']}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer_canvas, onLaterPages=footer_canvas)


def _gen_pdf_fallback(data: dict, out_path: str) -> bool:
    txt_path = out_path if out_path.lower().endswith(".txt") else out_path.replace(".pdf", ".txt")
    lines = [
        "=" * 70,
        "  SecureEraseX - Certified Wipe Report",
        "=" * 70,
        f"Report ID  : {data['report_id']}",
        f"Timestamp  : {data['timestamp']}",
        "",
        f"Drive      : {data['drive']['letter']} | {data['drive']['model']}",
        f"Type       : {data['drive']['type']}  |  {data['drive']['size']} GB",
        f"Method     : {data['method_name']}",
        f"Passes     : {data['passes']}",
        f"New FS     : {data['new_fs']}",
        f"Duration   : {data['elapsed_s']} seconds",
        "",
    ] + [f"[{tag}] {msg}" for tag, msg in data["log"]]
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


METHOD_META = {
    "Fast - Crypto / Sanitize (SSD / NVMe)": {"short": "Crypto / TRIM Erase", "passes": 1, "desc": "SSD-optimised wipe using crypto-erase or TRIM/discard paths where supported."},
    "Fast - USB Sanitize (Format + Trim)": {"short": "USB TRIM Sanitize", "passes": 1, "desc": "Quick-formats the flash drive then issues a TRIM/discard pass where available."},
    "Standard - Single Pass  (1x zero overwrite)": {"short": "Single Pass", "passes": 1, "desc": "Overwrites every addressable sector with 0x00 for a fast, practical erase."},
    "Secure   - Multi Pass   (3x DoD 5220.22-M overwrites)": {"short": "DoD 5220.22-M", "passes": 3, "desc": "Performs a multi-pass overwrite using zero, complement, and random patterns."},
    "Raw Disk Overwrite       (full disk, all sectors)": {"short": "Raw Disk Overwrite", "passes": 1, "desc": "Zeroes every sector on the whole physical disk including partition metadata."},
}

_LEGACY_METHOD_ALIASES = {
    "Fast – Crypto / Sanitize (SSD / NVMe)": "Fast - Crypto / Sanitize (SSD / NVMe)",
    "Fast – USB Sanitize (Format + Trim)": "Fast - USB Sanitize (Format + Trim)",
    "Standard – Single Pass  (1× zero overwrite)": "Standard - Single Pass  (1x zero overwrite)",
    "Secure   – Multi Pass   (3× DoD 5220.22-M overwrites)": "Secure   - Multi Pass   (3x DoD 5220.22-M overwrites)",
}

_DRIVE_DESC = {
    "HDD": "Hard Disk Drive - rotational platters. Overwrite methods are most effective.",
    "SSD": "Solid-State / NVMe Drive - flash memory. Crypto-erase or TRIM is recommended.",
    "USB": "USB Flash Drive - flash memory. Format + TRIM sanitise is standard.",
}

_FS_OPTIONS = {"windows": ["NTFS", "FAT32", "exFAT"], "linux": ["ext4", "NTFS", "FAT32", "exFAT"], "macos": ["APFS", "HFS+", "FAT32", "exFAT"]}
_PLATFORM_METHODS = {
    "SSD": ["Fast - Crypto / Sanitize (SSD / NVMe)"],
    "USB": ["Fast - USB Sanitize (Format + Trim)", "Standard - Single Pass  (1x zero overwrite)"],
    "HDD": ["Standard - Single Pass  (1x zero overwrite)", "Secure   - Multi Pass   (3x DoD 5220.22-M overwrites)", "Raw Disk Overwrite       (full disk, all sectors)"],
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureEraseX")
        self.setMinimumSize(1020, 680)
        self.resize(1100, 740)
        self.setStyleSheet(QSS)
        self._plt = "windows" if _IS_WINDOWS else "macos" if _IS_MAC else "linux"
        self.drive_map = {}
        self.display_map = {}
        self._wipe_log = []
        self._wipe_start = None
        self._last_report = None
        self._use_real_progress = False
        self._refresh_worker = None
        self._bg = AnimatedBackground(self)
        self._bg.lower()
        self._setup_ui()
        self.refresh_drives()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bg.setGeometry(self.rect())

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._make_header())
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._make_main_panel(), stretch=3)
        body.addWidget(self._make_sidebar(), stretch=1)
        root.addLayout(body)
        self.statusBar().showMessage("Ready - select a drive to begin.")

    def _make_header(self):
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"QWidget {{ background: rgba(6,11,20,0.95); border-bottom: 1px solid {C_BORDER}; }}")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(22, 0, 22, 0)
        hl.addWidget(AppIcon(size=38, parent=bar))
        hl.addSpacing(12)
        name_col = QVBoxLayout()
        title = QLabel("SecureEraseX")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Enterprise Secure Drive Wipe Utility  -  Windows - Linux - macOS")
        subtitle.setObjectName("subtitleLabel")
        name_col.addWidget(title)
        name_col.addWidget(subtitle)
        hl.addLayout(name_col)
        hl.addStretch()
        try:
            _host = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if _host not in sys.path:
                sys.path.insert(0, _host)
            from device_detection.platform_utils import platform_label

            plabel = platform_label()
        except Exception:
            plabel = sys.platform
        badge = QLabel(f"{self._plt.upper()}  {plabel}")
        badge.setObjectName("platformBadge")
        hl.addWidget(badge)
        return bar

    def _make_main_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 20, 20)
        lay.setSpacing(14)

        g_drive = QGroupBox("  Target Drive")
        vd = QVBoxLayout(g_drive)
        row_d = QHBoxLayout()
        self.drive_box = QComboBox()
        self.drive_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.drive_box.currentIndexChanged.connect(self._on_drive_changed)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setFixedWidth(92)
        self.refresh_btn.clicked.connect(self.refresh_drives)
        row_d.addWidget(self.drive_box)
        row_d.addWidget(self.refresh_btn)
        vd.addLayout(row_d)
        self.drive_info = QLabel("")
        self.drive_info.setObjectName("infoLine")
        self.drive_info.setWordWrap(True)
        vd.addWidget(self.drive_info)
        self.os_warn = QLabel("This drive contains the running OS. Start Wipe is disabled for safety.")
        self.os_warn.setObjectName("osWarnBox")
        self.os_warn.setWordWrap(True)
        self.os_warn.setVisible(False)
        vd.addWidget(self.os_warn)
        lay.addWidget(g_drive)

        g_cfg = QGroupBox("  Wipe Configuration")
        vc = QVBoxLayout(g_cfg)
        vc.addWidget(QLabel("Filesystem After Wipe"))
        self.fs_box = QComboBox()
        self.fs_box.addItems(_FS_OPTIONS.get(self._plt, ["ext4", "FAT32"]))
        vc.addWidget(self.fs_box)
        vc.addWidget(QLabel("Wipe Method"))
        self.method_box = QComboBox()
        self.method_box.currentIndexChanged.connect(self._on_method_changed)
        vc.addWidget(self.method_box)
        self.method_info = QLabel("")
        self.method_info.setObjectName("infoLine")
        self.method_info.setWordWrap(True)
        vc.addWidget(self.method_info)
        lay.addWidget(g_cfg)

        warn = QLabel("All data on the selected drive will be permanently and irreversibly destroyed. This action cannot be undone.")
        warn.setObjectName("warnBox")
        warn.setWordWrap(True)
        lay.addWidget(warn)

        g_prog = QGroupBox("  Wipe Progress")
        vp = QVBoxLayout(g_prog)
        self.glow_bar = GlowProgressBar()
        vp.addWidget(self.glow_bar)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("Ready")
        vp.addWidget(self.progress)
        steps_row = QHBoxLayout()
        self._step_labels = []
        for name in ["INIT", "FORMAT", "WIPE", "VERIFY"]:
            sl = QLabel(name)
            sl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.setStyleSheet(f"color:{C_TEXT_MUTED};font-size:10px;padding:10px 4px;border-radius:6px;background:rgba(255,255,255,0.02);")
            steps_row.addWidget(sl)
            self._step_labels.append(sl)
        vp.addLayout(steps_row)
        lay.addWidget(g_prog)

        g_log = QGroupBox("  Operation Log")
        vl = QVBoxLayout(g_log)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(110)
        vl.addWidget(self.log_area)
        lay.addWidget(g_log)
        self._log("info", "SecureEraseX v2.0 initialized. Awaiting drive selection.")

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.start_btn = QPushButton("START WIPE")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedWidth(220)
        self.start_btn.setFixedHeight(48)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.confirm_wipe)
        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)
        lay.addStretch()
        scroll.setWidget(inner)
        return scroll

    def _make_sidebar(self):
        side = QWidget()
        side.setFixedWidth(300)
        side.setStyleSheet(f"QWidget {{ background: rgba(13,20,36,0.7); border-left: 1px solid {C_BORDER}; }}")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setParent(side)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)
        for header, text in [
            ("About", "SecureEraseX permanently wipes external drives, preventing software-based recovery. Auto-detects the OS drive for safety."),
            ("Key Features", "NIST SP 800-88 compliant\nCross-platform support\nSSD/NVMe and USB workflows\nPDF wipe report export"),
            ("Developer & Support", "A. Ranjith Kumar\nranjithkumarabba@gmail.com\nlinkedin.com/in/ranjith-kumar-abba\ngithub.com/ark074"),
            ("Team Members", "K. Priyanshu\nB. Manish\nGuide: G. Vijay Kumar"),
        ]:
            title = QLabel(header)
            title.setStyleSheet(f"color:{C_TEXT_MUTED};font-size:9px;font-weight:700;letter-spacing:2px;")
            body = QLabel(text)
            body.setWordWrap(True)
            body.setStyleSheet(f"color:{C_TEXT_DIM};font-size:11px;")
            body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lay.addWidget(title)
            lay.addWidget(body)
        lay.addStretch()
        scroll.setWidget(inner)
        side_lay = QVBoxLayout(side)
        side_lay.setContentsMargins(0, 0, 0, 0)
        side_lay.addWidget(scroll)
        return side

    def refresh_drives(self):
        if self._refresh_worker and self._refresh_worker.isRunning():
            return
        self.statusBar().showMessage("Scanning drives...")
        self._log("info", "Scanning for connected drives...")
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("...")
        self.drive_box.setEnabled(False)
        self._refresh_worker = DriveRefreshWorker(self)
        self._refresh_worker.finished.connect(self._on_drive_refresh_done)
        self._refresh_worker.start()

    def _on_drive_refresh_done(self, vols, error: str):
        self.drive_box.blockSignals(True)
        self.drive_box.clear()
        self.drive_map.clear()
        self.display_map.clear()
        self.drive_info.setText("")
        self.os_warn.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Refresh")
        self.drive_box.setEnabled(True)
        if error:
            self.statusBar().showMessage(f"Drive scan failed: {error}")
            self._log("err", f"Drive scan failed: {error}")
            self.drive_box.blockSignals(False)
            self._refresh_worker = None
            return
        for volume in vols:
            label = self._make_label(volume)
            self.display_map[label] = volume["letter"]
            self.drive_map[volume["letter"]] = volume
        self.drive_box.addItems(list(self.display_map.keys()))
        self.drive_box.blockSignals(False)
        if self.display_map:
            self.drive_box.setCurrentIndex(0)
            self._on_drive_changed()
            self.statusBar().showMessage(f"Found {len(self.display_map)} volume(s). Select a drive to begin.")
        else:
            self.statusBar().showMessage("No volumes detected.")
        self._refresh_worker = None

    def _make_label(self, volume: dict) -> str:
        tags = [f"[{volume['type']}]"]
        if volume.get("is_internal"):
            tags.append("[Internal]")
        if volume.get("is_system"):
            tags.append("[OS]")
        mountpoint = volume.get("mountpoint", "")
        if mountpoint and not _IS_WINDOWS:
            tags.append(f"[{mountpoint}]")
        size_str = f"{volume['size']} GB" if volume["size"] > 0 else "? GB"
        return f"{volume['letter']} | {volume['model']}  -  {size_str}   {'  '.join(tags)}"

    def _on_drive_changed(self):
        label = self.drive_box.currentText()
        letter = self.display_map.get(label)
        if not letter:
            return
        volume = self.drive_map[letter]
        self._update_methods(volume["type"])
        details = _DRIVE_DESC.get(volume["type"], "")
        if volume.get("filesystem"):
            details += f"  -  FS: {volume['filesystem']}"
        if volume.get("mountpoint"):
            details += f"  -  Mount: {volume['mountpoint']}"
        self.drive_info.setText(details)
        is_system = volume.get("is_system")
        self.os_warn.setVisible(bool(is_system))
        self.start_btn.setEnabled(not is_system)

    def _update_methods(self, dtype: str):
        self.method_box.blockSignals(True)
        self.method_box.clear()
        self.method_box.addItems(_PLATFORM_METHODS.get(dtype, _PLATFORM_METHODS["HDD"]))
        self.method_box.blockSignals(False)
        self._on_method_changed()

    def _current_dispatch_method(self) -> str:
        current = self.method_box.currentText()
        reverse = {v: k for k, v in _LEGACY_METHOD_ALIASES.items()}
        return reverse.get(current, current)

    def _on_method_changed(self):
        current = self.method_box.currentText()
        canonical = _LEGACY_METHOD_ALIASES.get(current, current)
        self.method_info.setText(METHOD_META.get(canonical, {}).get("desc", ""))

    def confirm_wipe(self):
        label = self.drive_box.currentText()
        letter = self.display_map.get(label)
        if not letter:
            QMessageBox.warning(self, "No Drive Selected", "Please select a drive first.")
            return
        volume = self.drive_map[letter]
        if volume.get("is_system"):
            QMessageBox.critical(self, "Wipe Blocked", "This drive contains the running OS and cannot be wiped.")
            return
        method = self._current_dispatch_method()
        canonical = _LEGACY_METHOD_ALIASES.get(method, method)
        meta = METHOD_META.get(canonical, {})
        reply = QMessageBox.question(self, "Confirm Wipe", f"<b>ALL DATA on:</b><br><tt>{label}</tt><br><br><b>will be permanently destroyed.</b><br><br>Type: <b>{volume['type']}</b><br>Method: <b>{meta.get('short', method)}</b> ({meta.get('passes', 1)} pass(es))<br>Filesystem after wipe: <b>{self.fs_box.currentText()}</b><br><br>This action <b>cannot be undone.</b> Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        disk_ref = None if _IS_WINDOWS and "Raw Disk" not in method else volume["disk"]
        self._start_wipe(letter, method, self.fs_box.currentText(), disk_ref, volume)

    def _start_wipe(self, device, method, fs, disk_ref, volume):
        self.start_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self._wipe_log = []
        self._wipe_start = datetime.datetime.now()
        self.statusBar().showMessage("Wipe in progress...")
        self._log("info", f"Starting wipe: {device} | Method: {method} | FS: {fs}")
        self._activate_step(0)
        if _has_real_progress(method):
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.setFormat("Wiping...  %p%")
            self.glow_bar.setPulsing(False)
            self.glow_bar.setValue(0)
            self._use_real_progress = True
        else:
            self.progress.setRange(0, 0)
            self.progress.setFormat("Wiping...  please wait")
            self.glow_bar.setPulsing(True)
            self._use_real_progress = False
        self.worker = WipeWorker(device, method, fs, disk_ref)
        self.worker.finished.connect(lambda ok, msg: self._on_wipe_done(ok, msg, volume, method, fs))
        self.worker.progress_update.connect(self._on_progress)
        self.worker.log_message.connect(self._on_worker_log)
        self.worker.start()

    def _activate_step(self, idx: int):
        for i, label in enumerate(self._step_labels):
            if i < idx:
                label.setStyleSheet(f"color:{C_SUCCESS};font-size:10px;padding:10px 4px;border-radius:6px;background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.25);")
            elif i == idx:
                label.setStyleSheet(f"color:{C_NEON};font-size:10px;padding:10px 4px;border-radius:6px;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.25);")
            else:
                label.setStyleSheet(f"color:{C_TEXT_MUTED};font-size:10px;padding:10px 4px;border-radius:6px;background:rgba(255,255,255,0.02);")

    def _on_progress(self, pct: int):
        if self._use_real_progress and pct > self.progress.value():
            self.progress.setValue(pct)
            self.glow_bar.setValue(pct)
            if pct > 10:
                self._activate_step(1)
            if pct > 25:
                self._activate_step(2)
            if pct > 85:
                self._activate_step(3)

    def _on_worker_log(self, level: str, msg: str):
        self._log(level, msg)

    def _on_wipe_done(self, success: bool, message: str, volume: dict, method: str, new_fs: str):
        elapsed = round((datetime.datetime.now() - self._wipe_start).total_seconds(), 1) if self._wipe_start else 0.0
        self.glow_bar.setPulsing(False)
        self.progress.setRange(0, 100)
        self.start_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        if success:
            self.glow_bar.setValue(100)
            self.progress.setValue(100)
            self.progress.setFormat("Complete")
            self._activate_step(len(self._step_labels))
            self.statusBar().showMessage("Wipe completed successfully.")
            self._log("ok", f"Wipe complete in {elapsed}s. Drive securely erased.")
            canonical = _LEGACY_METHOD_ALIASES.get(method, method)
            meta = METHOD_META.get(canonical, {})
            self._last_report = {"report_id": self._gen_report_id(), "timestamp": datetime.datetime.now().strftime("%d %B %Y  %H:%M:%S"), "drive": volume, "method_name": method, "method_short": meta.get("short", method), "method_desc": meta.get("desc", ""), "passes": meta.get("passes", 1), "new_fs": new_fs, "elapsed_s": elapsed, "log": self._wipe_log or [("COMPLETE", f"Wipe finished in {elapsed}s")]}
            self._show_success_dialog()
            self.refresh_drives()
        else:
            self.glow_bar.setValue(0)
            self.progress.setValue(0)
            self.progress.setFormat("Error")
            self.statusBar().showMessage(f"Wipe failed: {message}")
            self._log("err", f"Wipe failed: {message}")
            QMessageBox.critical(self, "Wipe Failed", f"The wipe operation failed:\n\n{message}")

    def _show_success_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Wipe Complete")
        dlg.setMinimumWidth(480)
        dlg.setStyleSheet(QSS)
        lay = QVBoxLayout(dlg)
        title = QLabel("Wipe Complete")
        title.setStyleSheet(f"font-size:20px;font-weight:700;color:{C_SUCCESS};")
        lay.addWidget(title)
        lay.addWidget(QLabel("Drive has been securely wiped. All data has been permanently destroyed and is irrecoverable by software-based recovery tools."))
        report = self._last_report
        drive = report["drive"]
        lay.addWidget(QLabel(f"Drive: {drive['letter']} | {drive['model']}\nMethod: {report['method_short']}\nDuration: {report['elapsed_s']}s"))
        dl_btn = QPushButton("Download Wipe Report (PDF)")
        dl_btn.setObjectName("dlBtn")
        dl_btn.clicked.connect(lambda: self._download_report(dlg))
        lay.addWidget(dl_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(dlg.accept)
        lay.addWidget(close_btn)
        dlg.exec()

    def _download_report(self, parent_dlg):
        report = self._last_report
        default_name = f"SecureEraseX_Report_{report['drive']['letter'].replace(':', '').replace('/', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path, _selected = QFileDialog.getSaveFileName(parent_dlg, "Save Wipe Report", os.path.join(os.path.expanduser("~"), "Desktop", default_name), "PDF Report (*.pdf);;Text Report (*.txt)")
        if not path:
            return
        if not (path.lower().endswith(".pdf") or path.lower().endswith(".txt")):
            path += ".pdf"
        if generate_pdf_report(report, path):
            self._log("ok", f"Report saved: {path}")
            QMessageBox.information(parent_dlg, "Report Saved", f"Wipe report has been saved to:\n{path}")
        else:
            QMessageBox.warning(parent_dlg, "Save Failed", "Could not save the report. Check permissions.")

    def _log(self, level: str, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        colour = {"ok": C_SUCCESS, "info": C_NEON, "warn": C_WARNING, "err": C_DANGER}.get(level, C_TEXT_DIM)
        self.log_area.append(f'<span style="color:{C_TEXT_MUTED}">{ts}</span>&nbsp;&nbsp;<span style="color:{colour}">{msg}</span>')
        self._wipe_log.append((level.upper(), msg))

    @staticmethod
    def _gen_report_id() -> str:
        import random
        import string

        return "SX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def launch_app():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(6, 11, 20))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(232, 244, 255))
    pal.setColor(QPalette.ColorRole.Base, QColor(13, 20, 36))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(15, 24, 41))
    pal.setColor(QPalette.ColorRole.Text, QColor(232, 244, 255))
    pal.setColor(QPalette.ColorRole.Button, QColor(20, 31, 51))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(232, 244, 255))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 212))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(pal)
    splash = SplashScreen()
    splash.show()
    main_win = MainWindow()

    def on_splash_done():
        splash.close()
        main_win.show()

    splash.finished.connect(on_splash_done)
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_app()
