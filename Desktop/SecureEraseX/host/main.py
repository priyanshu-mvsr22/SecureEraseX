"""
main.py
Entry point for SecureEraseX.
Auto-detects the running OS (Windows / Linux / macOS) and launches
the appropriate UI and tools for that platform.
"""
import sys
import os

# Ensure the host directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from device_detection.platform_utils import require_supported_platform, current_platform
from utils.permissions import require_admin
from ui.main_window import launch_app

if __name__ == "__main__":
    require_supported_platform()
    require_admin()
    launch_app()
