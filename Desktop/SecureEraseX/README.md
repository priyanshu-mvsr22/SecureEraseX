# SecureEraseX  –  Merged Production Build

Secure Drive Wipe Utility · Windows · Linux · macOS

---

## How to Run

### Windows (as Administrator)
```
pip install PyQt6
cd SecureEraseX\host
python main.py
```
Right-click `cmd` → "Run as administrator", or right-click `main.py` → "Run as administrator".

### Linux (as root)
```
# System dependencies:
sudo apt install util-linux parted ntfs-3g exfat-utils nvme-cli
# util-linux  -> lsblk, blkdiscard, wipefs
# parted      -> partition table management
# ntfs-3g     -> mkfs.ntfs
# exfat-utils -> mkfs.exfat
# nvme-cli    -> nvme format (NVMe SSD erase)

pip install PyQt6
cd SecureEraseX/host
sudo python3 main.py
```

### macOS (as root + Full Disk Access)
1. System Settings → Privacy & Security → Full Disk Access → enable Terminal
2. `pip3 install PyQt6`
3. `cd SecureEraseX/host && sudo python3 main.py`

---

## Bug Fixes in This Build

| Bug | Fix |
|-----|-----|
| Multi-pass stuck at 88% | Opaque operations (cipher /w, diskpart, shred, diskutil) now use an **indeterminate pulsing progress bar**. No more fake percentage that stalls. |
| Linux single-pass not working | Dispatcher now converts partition device (`/dev/sdb1`) to whole-disk device (`/dev/sdb`) before calling wipe functions. `parted` and `dd` receive the correct device. |
| Reporting not saved after failed wipe | Report save is now in a `try/except`; always attempted even if verification raises. |
| Drive list not sorted | `list_volumes()` sorts by letter; UI adds items in that order. |
| `plistlib` crash on Windows/Linux | `plistlib` is now imported **inside functions**, not at module level. |
| USB HDD detected as USB flash | Multi-signal classification: MediaType + SpindleSpeed + WMIC + size heuristic. |

---

## Drive Type Detection

### Windows
1. `Get-PhysicalDisk MediaType == "HDD"` → HDD
2. `Get-PhysicalDisk SpindleSpeed > 0` → HDD (rotational)
3. WMIC `"External hard disk media"` → HDD
4. Size ≥ 500 GB + USB bus + Unspecified → HDD (heuristic for Seagate BUP etc.)
5. Otherwise USB bus → USB flash
6. NVMe bus / NVMe in model → SSD

### Linux  (`lsblk`)
- USB transport + ROTA=1 → HDD
- USB transport + ROTA=0 → USB flash
- NVMe transport → SSD
- ROTA=1 → HDD   |   ROTA=0 → SSD

### macOS  (`diskutil info -plist`)
- USB protocol + not SolidState → USB
- NVMe / PCIe protocol → SSD
- SolidState=true → SSD
- Otherwise → HDD

---

## Wipe Methods

| Type | Method | Detail |
|------|--------|--------|
| SSD | Crypto / Sanitize | BitLocker key delete (Win) · nvme format --ses=1 / blkdiscard (Linux) · diskutil secureErase 0 (macOS) |
| USB | USB Sanitize | Format + TRIM pass |
| HDD | Single Pass | 1× zero fill — Windows zero-fill loop OR Linux `dd if=/dev/zero` |
| HDD | Multi Pass | 3× DoD 5220.22-M — Windows `cipher /w` · Linux `dd`+`shred -n 2` · macOS `diskutil secureErase 4` |
| HDD | Raw Disk Overwrite | Windows `diskpart clean all` · Linux/macOS `dd if=/dev/zero` full disk |

---

## Build Executable

**Windows:**
```
pip install pyinstaller
pyinstaller --onefile --noconsole --name SecureEraseX host\main.py
```

**Linux / macOS:**
```
pip install pyinstaller
pyinstaller --onefile --name SecureEraseX host/main.py
sudo ./dist/SecureEraseX
```

---

## CLI Bootable Mode (Linux)
```
sudo bash bootable/wipe/auto_wipe.sh /dev/sdX [zero|dod|nvme]
```
