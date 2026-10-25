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
ui_print "  Features: Packet Injection + HID + WiFi  ";
ui_print "  Universal GKI: Android 15 / 16 / 17      ";
ui_print "===========================================";
ui_print " ";

# GKI Boot Install (POCO F7 has init_boot for ramdisk, boot for kernel)
if [ -L "/dev/block/bootdevice/by-name/init_boot_a" -o -L "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot" ]; then
    split_boot;
    flash_boot;
else
    dump_boot;
    write_boot;
fi

# Deploy NetHunter WiFi Drivers & Firmwares
ui_print "- Deploying NetHunter WiFi drivers and firmwares...";
mkdir -p /data/adb/modules/nethunter_wifi/system/lib/modules 2>/dev/null || true
mkdir -p /data/adb/modules/nethunter_wifi/system/etc/firmware/rtlwifi 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null || true

if [ -d "$home/modules" ]; then
  cp -rf $home/modules/* /data/adb/modules/nethunter_wifi/system/lib/modules/ 2>/dev/null || true
  cp -rf $home/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null || true
fi

if [ -d "$home/firmware" ]; then
  cp -rf $home/firmware/rtlwifi/* /data/adb/modules/nethunter_wifi/system/etc/firmware/rtlwifi/ 2>/dev/null || true
  cp -rf $home/firmware/* /data/adb/modules/nethunter_wifi/system/etc/firmware/ 2>/dev/null || true
  cp -rf $home/firmware/* /sdcard/NetHunter-Drivers/firmware/ 2>/dev/null || true
fi

ui_print " ";
ui_print "-> NetHunter Kernel Successfully Installed!";
ui_print "-> Flash Complete by Rohit Sharma!";
"""

out_path = sys.argv[1] if len(sys.argv) > 1 else "anykernel.sh"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(anykernel_content)

print(f"[+] Successfully wrote {out_path} ({len(anykernel_content)} bytes)")
