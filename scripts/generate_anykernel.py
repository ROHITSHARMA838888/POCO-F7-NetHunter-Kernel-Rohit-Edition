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
ui_print "  Root: KernelSU-Next Integration          ";
ui_print "  USB: Permanent Autosuspend Fix Applied   ";
ui_print "  100% Stock Telephony/VoLTE/Hotspot Safe  ";
ui_print "===========================================";
ui_print " ";

# Clean any obsolete or broken module overlays from previous test runs
ui_print "- Cleaning legacy module overlays...";
rm -rf /data/adb/modules/nethunter_wifi 2>/dev/null || true
rm -rf /data/adb/modules/nethunter_rtl8188 2>/dev/null || true

# GKI Boot Install (POCO F7 has init_boot for ramdisk, boot for kernel)
ui_print "- Flashing GKI NetHunter Kernel into Boot partition...";
if [ -L "/dev/block/bootdevice/by-name/init_boot_a" -o -L "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot_a" -o -e "/dev/block/by-name/init_boot" ]; then
    split_boot;
    patch_cmdline "usbcore.autosuspend" "usbcore.autosuspend=-1";
    flash_boot;
else
    dump_boot;
    patch_cmdline "usbcore.autosuspend" "usbcore.autosuspend=-1";
    write_boot;
fi

# Ensure SDCard driver backup directory is ready
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null || true

ui_print " ";
ui_print "-> NetHunter Kernel Successfully Installed!";
ui_print "-> BadUSB HID Nodes (/dev/hidg0, hidg1) Ready!";
ui_print "-> Next: Flash NetHunter-Wireless-Drivers-Module in KernelSU!";
ui_print "-> 100% Stable Telephony, 5G Data, and Hotspot!";
ui_print "-> Flash Complete by Rohit Sharma!";
"""

out_path = sys.argv[1] if len(sys.argv) > 1 else "anykernel.sh"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(anykernel_content)

print(f"[+] Successfully wrote {out_path} ({len(anykernel_content)} bytes)")
