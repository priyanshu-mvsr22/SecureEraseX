#!/usr/bin/env bash
# auto_wipe.sh
# Automated CLI wipe for use in bootable Linux environments.
# Usage:  sudo bash auto_wipe.sh /dev/sdX [method]
# method: zero | dod | nvme  (default: zero)

set -e

DEVICE="${1:?Usage: $0 /dev/sdX [zero|dod|nvme]}"
METHOD="${2:-zero}"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: must be run as root."
  exit 1
fi

if [ ! -b "$DEVICE" ]; then
  echo "ERROR: $DEVICE is not a block device."
  exit 1
fi

echo "=== SecureEraseX CLI Wipe ==="
echo "Device : $DEVICE"
echo "Method : $METHOD"
echo "WARNING: all data on $DEVICE will be destroyed!"
read -rp "Type YES to confirm: " CONFIRM
[ "$CONFIRM" = "YES" ] || { echo "Aborted."; exit 0; }

SIZE=$(blockdev --getsize64 "$DEVICE")
echo "Disk size: $((SIZE / 1024 / 1024 / 1024)) GB"

case "$METHOD" in
  zero)
    echo "[1/1] Zero pass..."
    dd if=/dev/zero of="$DEVICE" bs=4M conv=fdatasync status=progress
    ;;
  dod)
    echo "[1/3] Zero pass..."
    dd if=/dev/zero of="$DEVICE" bs=4M conv=fdatasync status=progress
    echo "[2/3] Shred passes (random x2)..."
    shred -n 2 -v "$DEVICE"
    echo "[3/3] Final zero pass..."
    dd if=/dev/zero of="$DEVICE" bs=4M conv=fdatasync status=progress
    ;;
  nvme)
    echo "[1/1] NVMe crypto format..."
    nvme format --ses=1 "$DEVICE" || blkdiscard "$DEVICE"
    ;;
  *)
    echo "Unknown method '$METHOD'. Use: zero | dod | nvme"
    exit 1
    ;;
esac

echo ""
echo "=== Wipe complete: $DEVICE ==="
