"""
platform_utils.py – Cross-platform OS detection helpers.
Supports: Windows, Linux, macOS.
"""
import sys
import os


def is_windows() -> bool:
    return sys.platform == "win32"

def is_linux() -> bool:
    return sys.platform.startswith("linux")

def is_mac() -> bool:
    return sys.platform == "darwin"

def current_platform() -> str:
    if is_windows(): return "windows"
    if is_linux():   return "linux"
    if is_mac():     return "macos"
    return "unknown"

def platform_label() -> str:
    """Human-readable platform label for UI display."""
    if is_windows():
        try:
            import platform
            return f"Windows {platform.release()}"
        except Exception:
            return "Windows"
    if is_linux():
        try:
            import platform
            return f"Linux  ({platform.release()})"
        except Exception:
            return "Linux"
    if is_mac():
        try:
            import platform
            return f"macOS {platform.mac_ver()[0]}"
        except Exception:
            return "macOS"
    return sys.platform

def require_supported_platform():
    if current_platform() == "unknown":
        raise RuntimeError(f"Unsupported platform: {sys.platform!r}")
