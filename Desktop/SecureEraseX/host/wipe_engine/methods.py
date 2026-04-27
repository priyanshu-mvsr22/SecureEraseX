"""methods.py – Wipe method enum shared across all platforms."""
from enum import Enum

class WipeMethod(Enum):
    CRYPTO       = "Fast – Crypto / Sanitize (SSD / NVMe)"
    USB_SANITIZE = "Fast – USB Sanitize (Format + Trim)"
    SINGLE       = "Standard – Single Pass  (1× zero overwrite)"
    MULTI        = "Secure   – Multi Pass   (3× DoD 5220.22-M overwrites)"
    RAW          = "Raw Disk Overwrite       (full disk, all sectors)"
