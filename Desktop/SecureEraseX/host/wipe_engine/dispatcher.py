"""
dispatcher.py – Routes wipe requests to the correct implementation.

KEY FIX: On Linux/macOS, `device` from the UI is a PARTITION path
  (e.g. /dev/sdb1, /dev/disk1s1).  Wipe functions require the WHOLE DISK
  (e.g. /dev/sdb, /dev/disk1).  This module converts partition -> disk
  before calling any wipe function, then verifies on the newly created
  first partition after formatting.
"""

import sys
import re

from wipe_engine.methods      import WipeMethod
from wipe_engine.wipe_methods import crypto, usb_sanitize, single, multi, raw_overwrite_disk
from wipe_engine.verify       import verify_sampling
from reporting.report         import save_report
from utils.logging            import log_event

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"
_IS_LINUX   = sys.platform.startswith("linux")


# ---------------------------------------------------------------------------
# Device path helpers
# ---------------------------------------------------------------------------

def _partition_to_disk_linux(device: str) -> str:
    """
    /dev/sda1       -> /dev/sda
    /dev/sdb2       -> /dev/sdb
    /dev/nvme0n1p1  -> /dev/nvme0n1
    /dev/mmcblk0p1  -> /dev/mmcblk0
    If already a whole disk, return unchanged.
    """
    name = device.replace("/dev/", "")
    # NVMe / MMC use trailing 'p<N>'
    stripped = re.sub(r"p\d+$", "", name)
    if stripped != name:
        return f"/dev/{stripped}"
    # SCSI/SATA use trailing digits
    stripped = re.sub(r"\d+$", "", name)
    return f"/dev/{stripped}" if stripped != name else device


def _partition_to_disk_macos(device: str) -> str:
    """
    /dev/disk1s1   -> /dev/disk1
    /dev/disk0s2   -> /dev/disk0
    """
    name     = device.replace("/dev/", "")
    stripped = re.sub(r"s\d+$", "", name)
    return f"/dev/{stripped}" if stripped != name else device


def _first_partition_linux(disk_device: str) -> str:
    """Return the expected first partition after format_drive."""
    from wipe_engine.filesystem import _partition_node_linux
    return _partition_node_linux(disk_device)


# ---------------------------------------------------------------------------
# OS-drive safety guards
# ---------------------------------------------------------------------------

def _is_system_device_linux(device: str) -> bool:
    try:
        from device_detection.volume_enum import _find_system_disks_linux
        # Check both partition and parent disk
        name      = device.replace("/dev/", "")
        disk_name = re.sub(r"p?\d+$", "", name)
        sys_disks = _find_system_disks_linux()
        return name in sys_disks or disk_name in sys_disks
    except Exception:
        return False


def _is_system_device_macos(device: str) -> bool:
    try:
        import plistlib, subprocess
        raw  = subprocess.check_output(
            ["diskutil", "info", "-plist", device],
            stderr=subprocess.DEVNULL
        )
        return plistlib.loads(raw).get("MountPoint", "") == "/"
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main dispatch function
# ---------------------------------------------------------------------------

def dispatch(device: str, method: str, fs: str, disk_ref, progress_cb=None):
    """
    device     – "D:" (Win) | "/dev/sdb1" (Linux) | "/dev/disk1s1" (macOS)
    method     – WipeMethod enum .value string
    fs         – "NTFS" | "FAT32" | "exFAT" | "ext4" | "APFS" | "HFS+"
    disk_ref   – disk number (Win int) | disk name str (Linux/macOS)
    progress_cb – optional callable(int 0-100)
    """

    # ── 1. Safety guard – never wipe the OS drive ────────────────────────
    if _IS_WINDOWS:
        if device.upper().startswith("C"):
            raise RuntimeError("System drive (C:) cannot be wiped.")
    elif _IS_MAC:
        if _is_system_device_macos(device):
            raise RuntimeError(f"System device {device} cannot be wiped.")
    else:
        if _is_system_device_linux(device):
            raise RuntimeError(f"System device {device} cannot be wiped.")

    # ── 2. Resolve wipe device (whole disk for Linux/macOS) ──────────────
    if _IS_LINUX:
        # Use parent disk name from volume dict if available, else derive it
        if disk_ref and str(disk_ref) and not str(disk_ref).isdigit():
            wipe_device = f"/dev/{disk_ref}"
        else:
            wipe_device = _partition_to_disk_linux(device)
    elif _IS_MAC:
        if disk_ref and str(disk_ref):
            d = str(disk_ref)
            wipe_device = d if d.startswith("/dev/") else f"/dev/{d}"
        else:
            wipe_device = _partition_to_disk_macos(device)
    else:
        wipe_device = device   # Windows: use drive letter as-is

    # ── 3. Route to wipe implementation ──────────────────────────────────
    if method == WipeMethod.CRYPTO.value:
        crypto(wipe_device, fs, progress_cb)

    elif method == WipeMethod.USB_SANITIZE.value:
        usb_sanitize(wipe_device, fs, progress_cb)

    elif method == WipeMethod.SINGLE.value:
        single(wipe_device, fs, progress_cb)

    elif method == WipeMethod.MULTI.value:
        multi(wipe_device, fs, progress_cb)

    elif method == WipeMethod.RAW.value:
        if disk_ref is None:
            raise RuntimeError("Disk reference required for Raw Disk Overwrite.")
        # For raw, pass disk_ref directly (disk index / disk name / device path)
        raw_overwrite_disk(disk_ref, progress_cb)

    else:
        raise RuntimeError(f"Unknown wipe method: {method!r}")

    # ── 4. Post-wipe: verify + report ────────────────────────────────────
    # Determine the device to verify on
    if _IS_LINUX:
        verify_dev = _first_partition_linux(wipe_device)
    elif _IS_MAC:
        # diskutil creates disk2s1 after format; try wipe_device's first slice
        d = wipe_device.replace("/dev/", "")
        verify_dev = f"/dev/{d}s1"
    else:
        verify_dev = device   # Windows: drive letter

    verified = verify_sampling(verify_dev)
    report   = {
        "device":       device,
        "wipe_device":  wipe_device,
        "method":       method,
        "filesystem":   fs,
        "verification": "PASS" if verified else "WARN",
    }

    # Save report — always attempt even if verify raised
    try:
        save_report(report)
    except Exception as e:
        log_event("REPORT_SAVE_FAILED", {"error": str(e)})

    log_event("WIPE_COMPLETED", report)
