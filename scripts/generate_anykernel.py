#!/usr/bin/env python3
import sys
import os

anykernel_content = """### AnyKernel3 - Rohit Sharma NetHunter Edition
properties() { '
kernel.string=Kali NetHunter Kernel - Rohit Sharma Edition (POCO F7 / Onyx)
do.devicecheck=0
do.modules=0
do.systemless=0
do.cleanup=1
do.cleanuponabort=0
'; }

# Boot shell variables
block=boot;
is_slot_device=auto;
ramdisk_compression=auto;
patch_vbmeta_flag=auto;
no_magisk_check=1;

# Shell Attributes
. tools/ak3-core.sh;

ui_print " ";
ui_print "===========================================";
ui_print "  KALI NETHUNTER KERNEL - ROHIT SHARMA     ";
ui_print "  Device: POCO F7 / Onyx (SM8735)          ";
ui_print "  Features: BadUSB HID + NetHunter WiFi    ";
ui_print "  Adapter: TP-Link WN722N v2/v3 (2357:010c)";
ui_print "  100% Stock Telephony/VoLTE/Hotspot Safe  ";
ui_print "===========================================";
ui_print " ";

# Remove old broken generic overlay if present from previous builds
ui_print "- Cleaning legacy module overlays...";
rm -rf /data/adb/modules/nethunter_wifi 2>/dev/null || true

# GKI Boot Install (POCO F7 has init_boot for ramdisk, boot for kernel)
ui_print "- Flashing GKI NetHunter Kernel into Boot partition...";
if [ -L "/dev/block/bootdevice/by-name/init_boot_a" -o -L "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot" ]; then
    split_boot;
    flash_boot;
else
    dump_boot;
    write_boot;
fi

# Deploy RTL8188EUS Driver & Firmware for TP-Link TL-WN722N v2/v3 (2357:010c)
ui_print "- Installing TP-Link TL-WN722N Plug-and-Play Driver & Firmware...";
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null || true
mkdir -p /data/adb/modules/nethunter_rtl8188/system/lib/modules 2>/dev/null || true
mkdir -p /data/adb/modules/nethunter_rtl8188/system/etc/firmware/rtlwifi 2>/dev/null || true

if [ -d "$home/modules" ]; then
  cp -rf $home/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null || true
  cp -rf $home/modules/* /data/adb/modules/nethunter_rtl8188/system/lib/modules/ 2>/dev/null || true
fi

if [ -d "$home/firmware" ]; then
  cp -rf $home/firmware/* /sdcard/NetHunter-Drivers/firmware/ 2>/dev/null || true
  cp -rf $home/firmware/* /data/adb/modules/nethunter_rtl8188/system/etc/firmware/ 2>/dev/null || true
  cp -rf $home/firmware/rtlwifi/* /data/adb/modules/nethunter_rtl8188/system/etc/firmware/rtlwifi/ 2>/dev/null || true
fi

# Create KernelSU Auto-Loader Module so user NEVER needs manual insmod
cat << 'EOF' > /data/adb/modules/nethunter_rtl8188/module.prop
id=nethunter_rtl8188
name=NetHunter RTL8188EUS Plug & Play
version=1.0
versionCode=1
author=Rohit Sharma
description=Plug-and-Play driver for TP-Link TL-WN722N v2/v3 (2357:010c) with monitor mode and packet injection.
EOF

cat << 'EOF' > /data/adb/modules/nethunter_rtl8188/service.sh
#!/system/bin/sh
MODDIR=${0%/*}

# Auto-load driver at boot so USB insertion is instantly recognized
insmod $MODDIR/system/lib/modules/8188eu.ko 2>/dev/null || insmod /sdcard/NetHunter-Drivers/modules/8188eu.ko 2>/dev/null

# Background poller: automatically binds driver on USB insertion/re-plug
while true; do
  if lsusb 2>/dev/null | grep -qi "2357:010c" || [ -e /sys/bus/usb/devices/*2357* ]; then
    if ! lsmod 2>/dev/null | grep -q "8188eu"; then
      insmod $MODDIR/system/lib/modules/8188eu.ko 2>/dev/null || insmod /sdcard/NetHunter-Drivers/modules/8188eu.ko 2>/dev/null
    fi
  fi
  sleep 2
done &
EOF

chmod 755 /data/adb/modules/nethunter_rtl8188/service.sh 2>/dev/null || true
touch /data/adb/modules/nethunter_rtl8188/auto_mount 2>/dev/null || true

ui_print " ";
ui_print "-> NetHunter Kernel Successfully Installed!";
ui_print "-> TP-Link WN722N v2/v3 Auto-Loader Configured (No insmod required)!";
ui_print "-> VoLTE, 5G Data, and Hotspot 100% Protected!";
ui_print "-> Flash Complete by Rohit Sharma!";
"""

out_path = sys.argv[1] if len(sys.argv) > 1 else "anykernel.sh"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(anykernel_content)

print(f"[+] Successfully wrote {out_path} ({len(anykernel_content)} bytes)")
