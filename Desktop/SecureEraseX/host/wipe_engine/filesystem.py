"""
filesystem.py – Cross-platform filesystem formatting after a wipe.
Supports: Windows (drive letter), Linux (whole disk), macOS (whole disk).
"""
import subprocess
import sys
import time

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"


def format_drive(device: str, fs: str):
    if _IS_WINDOWS:
        _format_windows(device, fs)
    elif _IS_MAC:
        _format_macos(device, fs)
    else:
        _format_linux(device, fs)


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------

def _format_windows(drive: str, fs: str):
    subprocess.call(
        ["format", drive, f"/FS:{fs.upper()}", "/Q", "/Y"],
        shell=True
    )


# ---------------------------------------------------------------------------
# Linux – operates on a WHOLE DISK device (e.g. /dev/sdb)
# ---------------------------------------------------------------------------

def _format_linux(device: str, fs: str):
    """
    1. Wipe existing partition signatures
    2. Create fresh GPT partition table
    3. One primary partition spanning 100% of the disk
    4. Format that partition
    """
    fs = fs.upper()
    _run(["wipefs", "-a", device])
    time.sleep(0.4)
    _run(["parted", "-s", device, "mklabel", "gpt"])
    time.sleep(0.4)
    _run(["parted", "-s", device, "mkpart", "primary", "1MiB", "100%"])
    time.sleep(1.2)   # let kernel register new partition

    part = _partition_node_linux(device)

    if   fs == "NTFS":  _run(["mkfs.ntfs", "-f", part])
    elif fs == "FAT32": _run(["mkfs.vfat", "-F", "32", part])
    elif fs == "EXFAT": _run(["mkfs.exfat", part])
    else:               _run(["mkfs.ext4", "-F", part])   # default ext4


def _partition_node_linux(device: str) -> str:
    """Return first partition path: /dev/sdb -> /dev/sdb1, /dev/nvme0n1 -> /dev/nvme0n1p1"""
    if "nvme" in device.lower() or "mmcblk" in device.lower():
        return device + "p1"
    return device + "1"


# ---------------------------------------------------------------------------
# macOS – operates on a WHOLE DISK device (e.g. /dev/disk2)
# ---------------------------------------------------------------------------

_MACOS_FS = {
    "APFS":  "apfs",
    "HFS+":  "jhfs+",
    "FAT32": "fat32",
    "EXFAT": "exfat",
    "NTFS":  "ntfs",
}

def _format_macos(device: str, fs: str):
    """diskutil eraseDisk <format> Erased GPT <device>"""
    fs_code = _MACOS_FS.get(fs.upper(), "apfs")
    subprocess.call(
        ["diskutil", "eraseDisk", fs_code, "Erased", "GPT", device],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _run(cmd):
    subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
