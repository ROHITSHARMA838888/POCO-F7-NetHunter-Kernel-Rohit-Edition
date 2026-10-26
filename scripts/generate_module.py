#!/usr/bin/env python3
import sys
import os
import zipfile

def create_wifi_module(output_zip, modules_dir, firmware_dir):
    print(f"[*] Packaging NetHunter Wireless Drivers Module into {output_zip}...")
    
    zf = zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED)
    
    # 1. module.prop
    module_prop = """id=nethunter_wireless_drivers
name=Kali NetHunter WiFi Drivers (Archer T2U Plus + WN722N)
version=2.1
versionCode=21
author=Rohit Sharma
description=Plug-and-play wireless drivers for TP-Link Archer T2U Plus (8821au) and TP-Link TL-WN722N v2/v3 (8188eu) with packet injection and live logging.
"""
    zf.writestr("module.prop", module_prop)

    # 2. auto_mount
    zf.writestr("auto_mount", "")

    # 3. META-INF/com/google/android/updater-script
    zf.writestr("META-INF/com/google/android/updater-script", "#MAGISK\n")

    # 4. META-INF/com/google/android/update-binary
    update_binary = """#!/sbin/sh
OUTFD=$2
ZIPFILE=$3

ui_print() {
  echo "$1"
}

ui_print "**********************************************"
ui_print "   Kali NetHunter WiFi Drivers Module v2.1   "
ui_print "   By Rohit Sharma (POCO F7 / Onyx)          "
ui_print "   Supports: Archer T2U Plus & WN722N        "
ui_print "**********************************************"

MODPATH="/data/adb/modules/nethunter_wireless_drivers"
mkdir -p "$MODPATH"
unzip -o "$ZIPFILE" -x 'META-INF/*' -d "$MODPATH" >/dev/null

# Set permissions
chmod -R 755 "$MODPATH"
chmod 644 "$MODPATH/module.prop"
chmod 755 "$MODPATH/service.sh"
chmod 755 "$MODPATH/system/bin/nh-wifi-status" 2>/dev/null || true

# Copy backup drivers to sdcard for Kali Chroot accessibility
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null || true
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null || true
cp -rf "$MODPATH"/system/lib/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null || true
cp -rf "$MODPATH"/system/etc/firmware/rtlwifi/* /sdcard/NetHunter-Drivers/firmware/rtlwifi/ 2>/dev/null || true

ui_print "- Drivers and firmwares installed to /data/adb/modules/"
ui_print "- Backup drivers placed in /sdcard/NetHunter-Drivers/"
ui_print "- Live log enabled at /sdcard/nethunter_wifi_debug.log"
ui_print "- Status tool installed: run 'nh-wifi-status' in terminal"
ui_print " "
ui_print "-> Installation Complete! Reboot your phone."
exit 0
"""
    zf.writestr("META-INF/com/google/android/update-binary", update_binary)

    # 5. system/bin/nh-wifi-status
    nh_wifi_status = """#!/system/bin/sh
echo "============================================================"
echo "    Kali NetHunter WiFi Status Monitor - Rohit Sharma       "
echo "============================================================"
echo ""
echo "[+] Connected USB Devices (lsusb):"
lsusb 2>/dev/null || echo "lsusb tool not available"
echo ""
echo "[+] Loaded Realtek Wireless Drivers (lsmod):"
lsmod 2>/dev/null | grep -E "8821au|8188eu|8812au|rtl8xxxu|cfg80211|mac80211" || echo "[-] No external WiFi drivers loaded yet."
echo ""
echo "[+] Network Interfaces (ip link):"
ip link show | grep -E "wlan[0-9]|link/ether" || ifconfig -a
echo ""
echo "[+] Wireless Extensions (iwconfig):"
iwconfig 2>/dev/null | grep -E "wlan[0-9]|IEEE|Mode" || echo "[-] Legacy WEXT not active; use 'iw dev' or 'ip link'."
echo ""
echo "[+] Recent Activity Log (/sdcard/nethunter_wifi_debug.log):"
if [ -f /sdcard/nethunter_wifi_debug.log ]; then
  tail -n 12 /sdcard/nethunter_wifi_debug.log
else
  echo "[-] Log file not created yet."
fi
echo "============================================================"
"""
    zf.writestr("system/bin/nh-wifi-status", nh_wifi_status)

    # 6. system/etc/modprobe.d/realtek.conf
    realtek_conf = """blacklist rtl8xxxu
blacklist r8188eu
"""
    zf.writestr("system/etc/modprobe.d/realtek.conf", realtek_conf)

    # 7. service.sh
    service_sh = """#!/system/bin/sh
MODDIR=${0%/*}
LOGFILE="/sdcard/nethunter_wifi_debug.log"

log_msg() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

# Initialize Log File
echo "============================================================" > "$LOGFILE"
echo "Kali NetHunter Wireless Daemon v2.1 (Rohit Sharma Edition)" >> "$LOGFILE"
echo "Boot Date: $(date)" >> "$LOGFILE"
echo "Kernel: $(uname -r) ($(uname -m))" >> "$LOGFILE"
echo "Device: POCO F7 / Onyx (SM8735)" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"
log_msg "NetHunter Wireless Service started. Watching USB ports..."

# Copy backup drivers & firmwares to SDCard for Kali Chroot accessibility
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null
cp -rf "$MODDIR"/system/lib/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null
cp -rf "$MODDIR"/system/etc/firmware/rtlwifi/* /sdcard/NetHunter-Drivers/firmware/rtlwifi/ 2>/dev/null

# Unload in-tree conflicting driver if loaded
if lsmod 2>/dev/null | grep -q "rtl8xxxu"; then
  log_msg "Unloading conflicting in-tree driver rtl8xxxu..."
  rmmod rtl8xxxu 2>/dev/null || true
fi

# Background Watcher Loop
while true; do
  # 1. Check for TP-Link Archer T2U Plus (2357:0120) or RTL8811AU/RTL8821AU
  if lsusb 2>/dev/null | grep -qi "2357:0120" || lsusb 2>/dev/null | grep -qi "0bda:0811" || lsusb 2>/dev/null | grep -qi "0bda:0821" || [ -e /sys/bus/usb/devices/*2357:0120* ]; then
    if ! lsmod 2>/dev/null | grep -q "8821au"; then
      log_msg "[HOTPLUG] TP-Link Archer T2U Plus (2357:0120) detected!"
      log_msg "Loading 8821au.ko driver..."
      insmod "$MODDIR/system/lib/modules/8821au.ko" 2>>"$LOGFILE"
      RET=$?
      if [ $RET -eq 0 ]; then
        log_msg "[SUCCESS] 8821au.ko loaded cleanly!"
        sleep 1
        ip link set wlan1 up 2>/dev/null || ifconfig wlan1 up 2>/dev/null || true
        IFACE=$(ip link 2>/dev/null | grep -o 'wlan[0-9]*' | tail -n 1)
        log_msg "[READY] Wireless interface created: $IFACE. UP and ready for Monitor Mode in Kali Chroot!"
      else
        log_msg "[ERROR] Failed to insmod 8821au.ko (Exit code: $RET)."
      fi
    fi
  fi

  # 2. Check for TP-Link TL-WN722N v2/v3 (2357:010c) or RTL8188EUS
  if lsusb 2>/dev/null | grep -qi "2357:010c" || lsusb 2>/dev/null | grep -qi "0bda:8179" || [ -e /sys/bus/usb/devices/*2357:010c* ]; then
    if lsmod 2>/dev/null | grep -q "rtl8xxxu"; then
      rmmod rtl8xxxu 2>/dev/null || true
    fi
    if ! lsmod 2>/dev/null | grep -q "8188eu"; then
      log_msg "[HOTPLUG] TP-Link TL-WN722N v2/v3 (2357:010c) detected!"
      log_msg "Loading 8188eu.ko driver..."
      insmod "$MODDIR/system/lib/modules/8188eu.ko" 2>>"$LOGFILE"
      RET=$?
      if [ $RET -eq 0 ]; then
        log_msg "[SUCCESS] 8188eu.ko loaded cleanly!"
        sleep 1
        ip link set wlan1 up 2>/dev/null || ifconfig wlan1 up 2>/dev/null || true
        IFACE=$(ip link 2>/dev/null | grep -o 'wlan[0-9]*' | tail -n 1)
        log_msg "[READY] Wireless interface created: $IFACE. UP and ready for Monitor Mode in Kali Chroot!"
      else
        log_msg "[ERROR] Failed to insmod 8188eu.ko (Exit code: $RET)."
      fi
    fi
  fi

  # 3. Check for Realtek AC1200 / Alfa (0bda:8812 / 2357:012d)
  if lsusb 2>/dev/null | grep -qi "0bda:8812" || lsusb 2>/dev/null | grep -qi "2357:012d"; then
    if ! lsmod 2>/dev/null | grep -q "8812au"; then
      log_msg "[HOTPLUG] Realtek AC1200 / Alfa device detected! Loading 8812au.ko..."
      insmod "$MODDIR/system/lib/modules/8812au.ko" 2>>"$LOGFILE"
    fi
  fi

  sleep 3
done &
"""
    zf.writestr("service.sh", service_sh)

    # 8. Add modules
    if os.path.exists(modules_dir):
        for f in os.listdir(modules_dir):
            if f.endswith(".ko"):
                full_path = os.path.join(modules_dir, f)
                arc_name = f"system/lib/modules/{f}"
                zf.write(full_path, arc_name)
                print(f"[+] Included module: {arc_name} ({os.path.getsize(full_path)} bytes)")

    # 9. Add firmware
    if os.path.exists(firmware_dir):
        for root, _, files in os.walk(firmware_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, firmware_dir)
                arc_name = f"system/etc/firmware/{rel_path}".replace("\\", "/")
                zf.write(full_path, arc_name)
                print(f"[+] Included firmware: {arc_name}")

    zf.close()
    print(f"[+] Successfully generated standalone module: {output_zip} ({os.path.getsize(output_zip)} bytes)")

if __name__ == "__main__":
    out_zip = sys.argv[1] if len(sys.argv) > 1 else "NetHunter-Wireless-Drivers-Module.zip"
    mod_dir = sys.argv[2] if len(sys.argv) > 2 else "modules"
    fw_dir = sys.argv[3] if len(sys.argv) > 3 else "firmware"
    create_wifi_module(out_zip, mod_dir, fw_dir)
