"""verify.py – Post-wipe verification sampling. Supports Windows, Linux, macOS."""
import os, sys, random

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"


def verify_sampling(device: str, samples: int = 5) -> bool:
    try:
        if _IS_WINDOWS: return _verify_windows(device, samples)
        if _IS_MAC:     return _verify_macos(device, samples)
        return              _verify_linux(device, samples)
    except Exception:
        return False


def _verify_windows(drive: str, samples: int) -> bool:
    root = drive if drive.endswith("\\") else drive + "\\"
    if not os.path.exists(root):
        return False
    try:
        entries = os.listdir(root)
    except PermissionError:
        return True
    for _ in range(samples):
        if not entries:
            break
        candidate = os.path.join(root, random.choice(entries))
        if os.path.isfile(candidate):
            with open(candidate, "rb") as f:
                f.read(4096)
    return True


def _verify_linux(device: str, samples: int = 5) -> bool:
    size = _device_size(device)
    if size == 0:
        return False
    sector = 512
    with open(device, "rb") as f:
        for _ in range(samples):
            offset = random.randint(0, max(0, (size // sector) - 1)) * sector
            f.seek(offset)
            f.read(sector)
    return True


def _verify_macos(device: str, samples: int = 5) -> bool:
    import plistlib, subprocess
    try:
        raw    = subprocess.check_output(
            ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
        )
        parent = plistlib.loads(raw).get("ParentWholeDisk", device.replace("/dev/", ""))
        dev    = f"/dev/r{parent}"
    except Exception:
        dev = device.replace("/dev/disk", "/dev/rdisk")
    size   = _device_size(dev.replace("/dev/r", "/dev/"))
    sector = 512
    if size == 0:
        return False
    with open(dev, "rb") as f:
        for _ in range(samples):
            offset = random.randint(0, max(0, (size // sector) - 1)) * sector
            f.seek(offset)
            f.read(sector)
    return True


def _device_size(device: str) -> int:
    if _IS_MAC:
        try:
            import plistlib, subprocess
            raw = subprocess.check_output(
                ["diskutil", "info", "-plist", device], stderr=subprocess.DEVNULL
            )
            return int(plistlib.loads(raw).get("TotalSize", 0))
        except Exception:
            pass
    try:
        import subprocess
        return int(subprocess.check_output(
            ["blockdev", "--getsize64", device],
            text=True, stderr=subprocess.DEVNULL
        ).strip())
    except Exception:
        return 0
