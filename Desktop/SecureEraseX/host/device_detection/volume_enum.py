"""
volume_enum.py – Cross-platform drive/partition enumeration.
Supports: Windows, Linux, macOS.

BUG FIXES applied in this version:
  - plistlib is NOT imported at module level (crashes Win/Linux).
  - Linux: enumerates partitions; 'disk' field = parent disk name.
  - Windows: per-partition IsBoot/IsSystem (not disk-level).
  - All platforms: list_volumes() returns sorted-by-letter results.

Volume dict keys:
  letter      str   "D:" | "/dev/sdb1" | "/dev/disk1s1"
  disk        any   disk_number (Win int) | "sdb" (Linux) | "disk1" (macOS)
  type        str   "HDD" | "SSD" | "USB"
  model       str   friendly model name
  size        int   size in GB
  is_internal bool
  is_system   bool  True ONLY if this partition is the OS root (/)
  mountpoint  str   mount point or ""
  filesystem  str   filesystem type or ""
"""

import subprocess
import json
import sys

_IS_WINDOWS = sys.platform == "win32"
_IS_MAC     = sys.platform == "darwin"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def list_volumes():
    """Return a list of volume dicts, sorted alphabetically by letter."""
    if _IS_WINDOWS:
        vols = _list_volumes_windows()
    elif _IS_MAC:
        vols = _list_volumes_macos()
    else:
        vols = _list_volumes_linux()

    # Sort alphabetically by device letter/path so the UI is consistent
    vols.sort(key=lambda v: v["letter"].upper())
    return vols


# ===========================================================================
# WINDOWS
# ===========================================================================

def _ps(cmd: str):
    """Run a PowerShell command; return parsed JSON list or []."""
    p = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
        capture_output=True, text=True
    )
    if p.returncode != 0 or not p.stdout.strip():
        return []
    try:
        data = json.loads(p.stdout)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def _classify_windows(media: str, bus: str, name: str,
                       spindle: int, size_gb: int, cim_media: str = "",
                       interface_type: str = "") -> str:
    """
    Classify a Windows disk as HDD | SSD | USB.

    USB-bus detection priority (handles Seagate BUP Slim + similar):
      1. Get-PhysicalDisk MediaType == "HDD"           -> HDD
      2. Get-PhysicalDisk SpindleSpeed > 0 (RPM)       -> HDD (rotational)
        3. CIM "External hard disk media"                -> HDD
        4. Size >= 500 GB + Unspecified (size heuristic) -> HDD
        5. Otherwise                                     -> USB flash
    """
    media = media.strip().upper()
    bus   = bus.strip().upper()
    name  = name.strip().upper()
    cim_media = cim_media.strip().upper()
    interface_type = interface_type.strip().upper()

    if bus == "USB":
        if media == "HDD":          return "HDD"
        if spindle > 0:             return "HDD"
        if "HARD DISK" in cim_media or "FIXED" in cim_media: return "HDD"
        if interface_type == "USB" and size_gb >= 500: return "HDD"
        if size_gb >= 500:          return "HDD"
        return "USB"

    if bus == "NVME" or "NVME" in name: return "SSD"
    if media == "SSD" or "SSD" in name: return "SSD"
    if media == "HDD":                  return "HDD"
    return "HDD"   # conservative fallback


def _list_volumes_windows():
    volumes = []
    vols = _ps(r"""
$vols  = Get-Volume | Where-Object { $_.DriveLetter }
$parts = Get-Partition | Select-Object DriveLetter, DiskNumber, IsBoot, IsSystem
$disks = Get-Disk | Select-Object Number, FriendlyName, BusType
$pdisks = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, SpindleSpeed
$cimDisks = Get-CimInstance Win32_DiskDrive | Select-Object Index, Model, MediaType, InterfaceType

$rows = foreach ($v in $vols) {
    $p = $parts | Where-Object { $_.DriveLetter -eq $v.DriveLetter } | Select-Object -First 1
    if (-not $p) { continue }
    $d = $disks | Where-Object { $_.Number -eq $p.DiskNumber } | Select-Object -First 1
    if (-not $d) { continue }
    $pd = $pdisks | Where-Object { $_.FriendlyName -eq $d.FriendlyName } | Select-Object -First 1
    $cd = $cimDisks | Where-Object { $_.Index -eq $p.DiskNumber } | Select-Object -First 1

    [pscustomobject]@{
        DriveLetter   = $v.DriveLetter
        Size          = $v.Size
        FileSystem    = $v.FileSystem
        DiskNumber    = $p.DiskNumber
        IsBoot        = $p.IsBoot
        IsSystem      = $p.IsSystem
        FriendlyName  = $d.FriendlyName
        BusType       = $d.BusType
        MediaType     = if ($pd) { $pd.MediaType } else { $null }
        SpindleSpeed  = if ($pd) { $pd.SpindleSpeed } else { 0 }
        CimModel      = if ($cd) { $cd.Model } else { $null }
        CimMediaType  = if ($cd) { $cd.MediaType } else { $null }
        InterfaceType = if ($cd) { $cd.InterfaceType } else { $null }
    }
}

$rows | ConvertTo-Json -Compress
""")
    if not vols:
        return []

    # Fallback OS-drive detection via %SystemDrive%
    import os as _os
    sys_drive = _os.environ.get("SystemDrive", "C:").rstrip("\\").upper()

    for v in vols:
        dl = v["DriveLetter"]
        disk_num = v.get("DiskNumber")

        try:
            size_gb = round((v.get("Size") or 0) / (1024 ** 3))
        except Exception:
            size_gb = 0

        media = str(v.get("MediaType", "") or "")
        bus = str(v.get("BusType", "") or "")
        name = str(v.get("CimModel", "") or v.get("FriendlyName", "") or "")
        spindle = int(v.get("SpindleSpeed", 0) or 0)
        cim_media = str(v.get("CimMediaType", "") or "")
        interface_type = str(v.get("InterfaceType", "") or "")

        dtype = _classify_windows(media, bus, name, spindle, size_gb, cim_media, interface_type)
        is_internal = bus.strip().upper() != "USB"
        is_system   = (
            bool(v.get("IsBoot"))
            or bool(v.get("IsSystem"))
            or dl.upper() == sys_drive.upper()
        )

        volumes.append({
            "letter":      dl + ":",
            "disk":        disk_num,
            "type":        dtype,
            "model":       name or "Unknown",
            "size":        size_gb,
            "is_internal": is_internal,
            "is_system":   is_system,
            "mountpoint":  dl + ":\\",
            "filesystem":  str(v.get("FileSystem", "") or ""),
        })

    return volumes


# ===========================================================================
# LINUX
# ===========================================================================

def _to_bool(val) -> bool:
    if isinstance(val, bool): return val
    if isinstance(val, int):  return val != 0
    if isinstance(val, str):  return val.strip() not in ("0", "false", "False", "")
    return bool(val)


def _classify_linux(tran: str, rota: bool, name: str) -> str:
    if tran == "usb":
        return "HDD" if rota else "USB"
    if tran == "nvme" or "nvme" in name.lower():
        return "SSD"
    if rota:
        return "HDD"
    return "SSD"


def _list_volumes_linux():
    """
    Enumerate partitions on Linux using lsblk --json.
    'letter' = partition device (/dev/sdb1).
    'disk'   = parent disk name ('sdb') — used by dispatcher to get /dev/sdb.
    is_system is True ONLY if mountpoint == '/'.
    """
    try:
        raw = subprocess.check_output(
            ["lsblk", "-o",
             "NAME,TRAN,ROTA,SIZE,MODEL,HOTPLUG,TYPE,MOUNTPOINT,FSTYPE",
             "--json", "--bytes"],
            text=True, stderr=subprocess.DEVNULL
        )
        devices = json.loads(raw).get("blockdevices", [])
    except Exception:
        return []

    volumes = []
    _collect_linux_nodes(devices, volumes, parent=None)
    return volumes


def _collect_linux_nodes(nodes, volumes, parent):
    for node in nodes:
        ntype = node.get("type", "")
        if ntype == "disk":
            children = node.get("children", [])
            if children:
                _collect_linux_nodes(children, volumes, parent=node)
            else:
                # Whole disk with no partition table — treat as single volume
                _add_linux_volume(node, node, volumes)
        elif ntype == "part":
            disk_node = parent if parent else node
            _add_linux_volume(node, disk_node, volumes)


def _add_linux_volume(part_node, disk_node, volumes):
    name    = part_node.get("name", "")
    device  = f"/dev/{name}"
    mp      = (part_node.get("mountpoint") or "").strip()
    fstype  = (part_node.get("fstype")     or "").strip()
    size_b  = int(part_node.get("size") or 0)
    size_gb = round(size_b / (1024 ** 3))

    tran      = (disk_node.get("tran")    or "").lower().strip()
    rota      = _to_bool(disk_node.get("rota"))
    model     = (disk_node.get("model")   or disk_node.get("name") or name).strip()
    hotplug   = _to_bool(disk_node.get("hotplug"))
    disk_name = disk_node.get("name", name)

    dtype       = _classify_linux(tran, rota, name)
    is_internal = (not hotplug) and (tran != "usb")
    is_system   = (mp == "/")   # FIX: only root mount = system drive

    volumes.append({
        "letter":      device,
        "disk":        disk_name,          # e.g. "sdb" (parent disk)
        "type":        dtype,
        "model":       model,
        "size":        size_gb,
        "is_internal": is_internal,
        "is_system":   is_system,
        "mountpoint":  mp,
        "filesystem":  fstype,
    })


def _find_system_disks_linux() -> set:
    """Return set of disk names whose partition is mounted at '/'."""
    system_disks = set()
    try:
        raw = subprocess.check_output(
            ["lsblk", "-o", "NAME,MOUNTPOINT,TYPE", "--json"],
            text=True, stderr=subprocess.DEVNULL
        )
        data = json.loads(raw)
        for bd in data.get("blockdevices", []):
            if _disk_contains_root(bd):
                system_disks.add(bd["name"])
    except Exception:
        pass
    return system_disks


def _disk_contains_root(node: dict) -> bool:
    if (node.get("mountpoint") or "").strip() == "/":
        return True
    for child in node.get("children", []):
        if _disk_contains_root(child):
            return True
    return False


# ===========================================================================
# macOS
# ===========================================================================

def _list_volumes_macos():
    """
    Enumerate partitions on macOS using diskutil list/info plist.
    'letter' = partition device (/dev/disk1s1).
    'disk'   = parent whole-disk name ('disk1').
    is_system = True ONLY if mountpoint == '/'.
    """
    # NOTE: plistlib imported here (not at module level) to avoid Win/Linux crash
    import plistlib

    try:
        raw = subprocess.check_output(
            ["diskutil", "list", "-plist"],
            stderr=subprocess.DEVNULL
        )
        top = plistlib.loads(raw)
    except Exception:
        return []

    all_disks   = top.get("AllDisks", [])
    whole_disks = top.get("WholeDisks", [])

    _cache = {}
    def get_info(dev):
        if dev not in _cache:
            try:
                r = subprocess.check_output(
                    ["diskutil", "info", "-plist", f"/dev/{dev}"],
                    stderr=subprocess.DEVNULL
                )
                _cache[dev] = plistlib.loads(r)
            except Exception:
                _cache[dev] = {}
        return _cache[dev]

    volumes = []
    for dev in all_disks:
        if dev in whole_disks:
            continue   # only partition-level entries

        info        = get_info(dev)
        parent_dev  = info.get("ParentWholeDisk", dev)
        parent_info = get_info(parent_dev)

        device   = f"/dev/{dev}"
        mp       = (info.get("MountPoint")  or "").strip()
        vol_name = (info.get("VolumeName")  or "").strip()
        content  = (info.get("Content")     or "").strip()
        size_b   = int(info.get("TotalSize") or 0)
        size_gb  = round(size_b / (1024 ** 3))

        model = (
            parent_info.get("MediaName")
            or parent_info.get("IORegistryEntryName")
            or parent_dev
        ).strip()

        removable   = bool(parent_info.get("RemovableMedia") or parent_info.get("Removable"))
        protocol    = (parent_info.get("BusProtocol") or "").lower()
        solid_state = bool(parent_info.get("SolidState"))

        if protocol == "usb":
            dtype = "USB"   # USB flash OR USB HDD treated as USB on macOS
        elif "nvme" in protocol or "pcie" in protocol:
            dtype = "SSD"
        elif solid_state:
            dtype = "SSD"
        else:
            dtype = "HDD"

        is_internal = not removable and protocol != "usb"
        is_system   = (mp == "/")

        if size_gb == 0 and not mp:
            continue   # skip zero-size utility partitions

        display = vol_name or content or dev
        if model and display and display.lower() != model.lower():
            model_str = f"{model}  ({display})"
        else:
            model_str = model or display or dev

        volumes.append({
            "letter":      device,
            "disk":        parent_dev,     # e.g. "disk1"
            "type":        dtype,
            "model":       model_str,
            "size":        size_gb,
            "is_internal": is_internal,
            "is_system":   is_system,
            "mountpoint":  mp,
            "filesystem":  content,
        })

    return volumes
