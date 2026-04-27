"""
wipe_methods.py – Cross-platform wipe implementations.
Supports: Windows, Linux, macOS.

IMPORTANT: On Linux/macOS every function receives the WHOLE DISK device
  (e.g. /dev/sdb, /dev/disk2), NOT a partition path.
  The dispatcher is responsible for converting partition -> disk before calling here.

progress_cb: optional callable(int 0-100).
  Methods that genuinely report progress:
    single()  – Windows (zero-fill loop) + Linux/macOS (dd status=progress)
    raw_overwrite_disk() – Linux/macOS (dd status=progress)
    usb_sanitize() – Linux/macOS (dd)
  Methods that are OPAQUE (no real progress):
    multi()   – cipher /w (Win) / shred (Linux) / diskutil (macOS)
    crypto()  – format + defrag/blkdiscard/diskutil
  The UI shows an indeterminate progress bar for opaque methods.
"""

import subprocess
import os
import sys
import time
import re

from wipe_engine.filesystem import format_drive, _partition_node_linux

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"
_IS_LINUX   = sys.platform.startswith("linux")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _disk_size_bytes(device: str) -> int:
    if _IS_MAC:
        try:
            import plistlib
            raw = subprocess.check_output(
                ["diskutil", "info", "-plist", device],
                stderr=subprocess.DEVNULL
            )
            return int(plistlib.loads(raw).get("TotalSize", 0))
        except Exception:
            pass
    try:
        return int(subprocess.check_output(
            ["blockdev", "--getsize64", device],
            text=True, stderr=subprocess.DEVNULL
        ).strip())
    except Exception:
        return 0


def _run_silent(cmd):
    subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _progress(cb, value: int):
    if cb:
        try:
            cb(min(max(int(value), 0), 100))
        except Exception:
            pass


# ===========================================================================
# SSD / NVMe — Crypto Erase
# ===========================================================================

def crypto(device: str, fs: str, progress_cb=None):
    """
    Windows: BitLocker key delete (instant), or format + TRIM (defrag /L).
    Linux:   nvme format --ses=1 (NVMe), or blkdiscard (SATA SSD), or hdparm.
    macOS:   diskutil secureErase 0 (zero fill).
    Opaque: no real progress emitted.
    """
    _progress(progress_cb, 5)
    if   _IS_WINDOWS: _crypto_windows(device, fs, progress_cb)
    elif _IS_MAC:     _crypto_macos(device, fs, progress_cb)
    else:             _crypto_linux(device, fs, progress_cb)
    _progress(progress_cb, 100)


def _crypto_windows(drive, fs, progress_cb):
    bitlocker_on = False
    try:
        status = subprocess.check_output(
            ["manage-bde", "-status", drive], shell=True, stderr=subprocess.STDOUT
        ).decode().lower()
        bitlocker_on = "protection on" in status
    except Exception:
        pass
    _progress(progress_cb, 30)
    if bitlocker_on:
        subprocess.call(["manage-bde", "-protectors", "-delete", drive], shell=True)
    else:
        format_drive(drive, fs)
        subprocess.call(["defrag", drive, "/L"], shell=True)
    _progress(progress_cb, 90)


def _crypto_linux(device, fs, progress_cb):
    name = os.path.basename(device)
    if "nvme" in name:
        ret = subprocess.call(
            ["nvme", "format", "--ses=1", device],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if ret != 0:
            _run_silent(["blkdiscard", device])
    else:
        ret = subprocess.call(
            ["blkdiscard", device],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if ret != 0:
            _hdparm_secure_erase(device)
    _progress(progress_cb, 60)
    format_drive(device, fs)
    _progress(progress_cb, 90)


def _crypto_macos(device, fs, progress_cb):
    import plistlib
    try:
        raw  = subprocess.check_output(
            ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
        )
        parent = plistlib.loads(raw).get("ParentWholeDisk",
                                          device.replace("/dev/", ""))
        disk_dev = f"/dev/{parent}"
    except Exception:
        disk_dev = device
    _progress(progress_cb, 20)
    _run_silent(["diskutil", "secureErase", "0", disk_dev])
    _progress(progress_cb, 80)
    format_drive(disk_dev, fs)
    _progress(progress_cb, 90)


def _hdparm_secure_erase(device):
    try:
        tmp = "SEX_TMP_PASS"
        subprocess.call(["hdparm", "--security-set-pass", tmp, device],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        subprocess.call(["hdparm", "--security-erase-enhanced", tmp, device],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ===========================================================================
# USB Flash — Sanitize
# ===========================================================================

def usb_sanitize(device: str, fs: str, progress_cb=None):
    """
    Windows: format + TRIM (defrag /L). Opaque.
    Linux:   dd zero pass then format. Real progress.
    macOS:   diskutil secureErase 0 then format. Opaque.
    """
    _progress(progress_cb, 5)
    if   _IS_WINDOWS: _usb_sanitize_windows(device, fs, progress_cb)
    elif _IS_MAC:     _usb_sanitize_macos(device, fs, progress_cb)
    else:             _usb_sanitize_linux(device, fs, progress_cb)
    _progress(progress_cb, 100)


def _usb_sanitize_windows(drive, fs, progress_cb):
    format_drive(drive, fs)
    _progress(progress_cb, 50)
    try:
        subprocess.call(["defrag", drive, "/L"], shell=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    _progress(progress_cb, 90)


def _usb_sanitize_linux(device, fs, progress_cb):
    _dd_zero(device, progress_cb, start_pct=10, end_pct=75)
    format_drive(device, fs)
    _progress(progress_cb, 90)


def _usb_sanitize_macos(device, fs, progress_cb):
    import plistlib
    try:
        raw  = subprocess.check_output(
            ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
        )
        parent   = plistlib.loads(raw).get("ParentWholeDisk",
                                            device.replace("/dev/", ""))
        disk_dev = f"/dev/{parent}"
    except Exception:
        disk_dev = device
    _progress(progress_cb, 20)
    _run_silent(["diskutil", "secureErase", "0", disk_dev])
    _progress(progress_cb, 75)
    format_drive(disk_dev, fs)
    _progress(progress_cb, 90)


# ===========================================================================
# HDD — Single Pass (1× zero overwrite)
# ===========================================================================

def single(device: str, fs: str, progress_cb=None):
    """
    Windows: format then fill free space with zeros (real progress via our loop).
    Linux:   dd if=/dev/zero (real progress via dd status=progress).
    macOS:   diskutil secureErase 0 then format (opaque).
    """
    _progress(progress_cb, 5)
    if   _IS_WINDOWS: _single_windows(device, fs, progress_cb)
    elif _IS_MAC:     _single_macos(device, fs, progress_cb)
    else:             _single_linux(device, fs, progress_cb)
    _progress(progress_cb, 100)


def _single_windows(drive, fs, progress_cb):
    format_drive(drive, fs)
    _progress(progress_cb, 20)

    filler = os.path.join(drive + "\\", "wipe_single.bin")
    try:
        out = subprocess.check_output(
            f"fsutil volume diskfree {drive}", shell=True
        ).decode()
        free_bytes = 0
        for line in out.splitlines():
            if "Total # of free bytes" in line:
                free_bytes = int(line.split(":")[1].strip())
    except Exception:
        free_bytes = 0

    chunk = b"\x00" * (1024 * 1024)
    written = 0
    try:
        with open(filler, "wb") as f:
            while written < free_bytes:
                f.write(chunk)
                written += len(chunk)
                if free_bytes > 0:
                    pct = 20 + int(written * 70 / free_bytes)
                    _progress(progress_cb, min(pct, 90))
    except OSError:
        pass   # disk full = wipe complete
    finally:
        try:
            os.remove(filler)
        except Exception:
            pass
    _progress(progress_cb, 90)


def _single_linux(device, fs, progress_cb):
    # dd writes zeros to the WHOLE DISK (device = /dev/sdb etc.)
    _dd_zero(device, progress_cb, start_pct=5, end_pct=80)
    format_drive(device, fs)
    _progress(progress_cb, 90)


def _single_macos(device, fs, progress_cb):
    import plistlib
    try:
        raw  = subprocess.check_output(
            ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
        )
        parent   = plistlib.loads(raw).get("ParentWholeDisk",
                                            device.replace("/dev/", ""))
        disk_dev = f"/dev/{parent}"
    except Exception:
        disk_dev = device
    _progress(progress_cb, 10)
    _run_silent(["diskutil", "secureErase", "0", disk_dev])
    _progress(progress_cb, 80)
    format_drive(disk_dev, fs)
    _progress(progress_cb, 90)


# ===========================================================================
# HDD — Multi Pass (DoD 5220.22-M · 3 passes)
# ===========================================================================

def multi(device: str, fs: str, progress_cb=None):
    """
    Windows: format + cipher /w (3 passes: 0x00, 0xFF, random). OPAQUE.
    Linux:   dd zero pass + shred -n 2 (2 random passes). Partial progress.
    macOS:   diskutil secureErase 4 (7-pass DoD). OPAQUE.
    """
    _progress(progress_cb, 3)
    if   _IS_WINDOWS: _multi_windows(device, fs, progress_cb)
    elif _IS_MAC:     _multi_macos(device, fs, progress_cb)
    else:             _multi_linux(device, fs, progress_cb)
    _progress(progress_cb, 100)


def _multi_windows(drive, fs, progress_cb):
    format_drive(drive, fs)
    _progress(progress_cb, 15)
    # cipher /w: 3 passes (0x00, 0xFF, random) – completely silent/opaque
    subprocess.call(["cipher", f"/w:{drive}"], shell=True)
    _progress(progress_cb, 90)


def _multi_linux(device, fs, progress_cb):
    # Pass 1: zeros via dd (has real progress)
    _dd_zero(device, progress_cb, start_pct=5, end_pct=33)
    _progress(progress_cb, 33)
    # Passes 2+3: shred (opaque but fast on Linux for 2 random passes)
    subprocess.call(
        ["shred", "-n", "2", "--verbose", device],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    _progress(progress_cb, 80)
    format_drive(device, fs)
    _progress(progress_cb, 90)


def _multi_macos(device, fs, progress_cb):
    import plistlib
    try:
        raw  = subprocess.check_output(
            ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
        )
        parent   = plistlib.loads(raw).get("ParentWholeDisk",
                                            device.replace("/dev/", ""))
        disk_dev = f"/dev/{parent}"
    except Exception:
        disk_dev = device
    _progress(progress_cb, 10)
    # Level 4 = 7-pass DoD; fallback to level 2 = 3-pass random
    ret = subprocess.call(
        ["diskutil", "secureErase", "4", disk_dev],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if ret != 0:
        _run_silent(["diskutil", "secureErase", "2", disk_dev])
    _progress(progress_cb, 80)
    format_drive(disk_dev, fs)
    _progress(progress_cb, 90)


# ===========================================================================
# HDD — Raw Disk Overwrite (full physical disk)
# ===========================================================================

def raw_overwrite_disk(disk_ref, progress_cb=None):
    """
    Windows: diskpart clean all (zeroes every sector). OPAQUE.
    Linux:   dd if=/dev/zero of=<device> (real progress via dd status=progress).
    macOS:   dd if=/dev/zero of=/dev/rdiskX (real progress).

    disk_ref:
      Windows -> int   disk number (from Get-Disk)
      Linux   -> str   disk device  ("/dev/sdb")
      macOS   -> str   disk name    ("disk2")
    """
    _progress(progress_cb, 3)
    if   _IS_WINDOWS: _raw_windows(disk_ref, progress_cb)
    elif _IS_MAC:     _raw_macos(str(disk_ref), progress_cb)
    else:             _raw_linux(str(disk_ref), progress_cb)
    _progress(progress_cb, 100)


def _raw_windows(disk_index, progress_cb):
    script = f"select disk {disk_index}\nclean all\nexit\n"
    subprocess.run(["diskpart"], input=script.encode(), shell=True)
    _progress(progress_cb, 90)


def _raw_linux(device, progress_cb):
    # device here is already the whole-disk path (e.g. /dev/sdb)
    _dd_zero(device, progress_cb, start_pct=5, end_pct=90)


def _raw_macos(disk_id, progress_cb):
    # Use /dev/rdiskX (raw device, no buffering = much faster)
    if disk_id.startswith("/dev/"):
        disk_id = disk_id[5:]
    raw_dev  = f"/dev/r{disk_id}"
    size     = _disk_size_bytes(f"/dev/{disk_id}")
    _progress(progress_cb, 5)
    proc = subprocess.Popen(
        ["dd", "if=/dev/zero", f"of={raw_dev}", "bs=1m"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
    )
    for line in proc.stderr:
        m = re.search(r"(\d+)\s+bytes", line)
        if m and size > 0:
            pct = 5 + int(int(m.group(1)) * 85 / size)
            _progress(progress_cb, min(pct, 89))
    proc.wait()
    _progress(progress_cb, 90)


# ===========================================================================
# Linux/macOS dd helpers
# ===========================================================================

def _dd_zero(device: str, progress_cb, start_pct: int, end_pct: int):
    _dd_source("/dev/zero", device, progress_cb, start_pct, end_pct)


def _dd_source(src: str, device: str, progress_cb, start_pct: int, end_pct: int):
    """dd with status=progress; parses stderr and calls progress_cb."""
    total = _disk_size_bytes(device)
    proc  = subprocess.Popen(
        ["dd", f"if={src}", f"of={device}", "bs=4M",
         "conv=fdatasync", "status=progress"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    for line in proc.stderr:
        m = re.match(r"(\d+)\s+bytes", line.strip())
        if m and total > 0:
            done = int(m.group(1))
            pct  = start_pct + int(done * (end_pct - start_pct) / total)
            _progress(progress_cb, min(pct, end_pct - 1))
    proc.wait()
    _progress(progress_cb, end_pct)
