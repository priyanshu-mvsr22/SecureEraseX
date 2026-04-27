"""
permissions.py
Cross-platform administrator / root privilege check.
Supports: Windows, Linux, macOS.
"""

import sys
import os

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"


def is_admin() -> bool:
    if _IS_WINDOWS:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    else:
        # Linux and macOS both use euid 0 for root
        return os.geteuid() == 0


def require_admin():
    if is_admin():
        return
    if _IS_WINDOWS:
        _prompt_windows()
    elif _IS_MAC:
        _prompt_macos()
    else:
        _prompt_linux()
    sys.exit(1)


def _prompt_windows():
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("Administrator Required")
        msg.setText(
            "SecureEraseX must be run as Administrator.\n\n"
            "Right-click the application and select 'Run as administrator'."
        )
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()
    except Exception:
        print("ERROR: Administrator privileges required. Run as Administrator.")


def _prompt_linux():
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("Root Required")
        msg.setText(
            "SecureEraseX requires root privileges to wipe drives.\n\n"
            "Please run with:  sudo python3 main.py"
        )
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()
    except Exception:
        print("ERROR: Root privileges required. Run with:  sudo python3 main.py")


def _prompt_macos():
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("Root & Full Disk Access Required")
        msg.setText(
            "SecureEraseX requires root and Full Disk Access to wipe drives.\n\n"
            "1. Grant Full Disk Access to Terminal:\n"
            "   System Settings → Privacy & Security\n"
            "   → Full Disk Access → enable Terminal\n\n"
            "2. Then run:\n"
            "   sudo python3 main.py"
        )
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()
    except Exception:
        print(
            "ERROR: Root + Full Disk Access required.\n"
            "Grant Full Disk Access to Terminal in System Settings, then:\n"
            "  sudo python3 main.py"
        )
