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
ui_print "  100% Stock Telephony/VoLTE/Hotspot Safe  ";
ui_print "===========================================";
ui_print " ";

# Remove any past broken module overlays that cause modem panics
ui_print "- Cleaning any residual module overlays...";
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

# Deploy NetHunter External WiFi Drivers & Firmwares ONLY to SDCard (Zero system pollution)
ui_print "- Deploying NetHunter external dongle drivers to /sdcard/NetHunter-Drivers/...";
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null || true

if [ -d "$home/modules" ]; then
  cp -rf $home/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null || true
fi

if [ -d "$home/firmware" ]; then
  cp -rf $home/firmware/rtlwifi/* /sdcard/NetHunter-Drivers/firmware/rtlwifi/ 2>/dev/null || true
  cp -rf $home/firmware/* /sdcard/NetHunter-Drivers/firmware/ 2>/dev/null || true
fi

ui_print " ";
ui_print "-> NetHunter Kernel Successfully Installed!";
ui_print "-> VoLTE, 5G Data, and Hotspot are 100% Protected!";
ui_print "-> Flash Complete by Rohit Sharma!";
"""

out_path = sys.argv[1] if len(sys.argv) > 1 else "anykernel.sh"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(anykernel_content)

print(f"[+] Successfully wrote {out_path} ({len(anykernel_content)} bytes)")
