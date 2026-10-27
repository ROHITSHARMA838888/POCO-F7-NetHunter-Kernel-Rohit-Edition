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
version=2.2
versionCode=22
author=Rohit Sharma
description=Crash-free wireless drivers for TP-Link Archer T2U Plus (8821au) and TP-Link TL-WN722N v2/v3 (8188eu) with permanent USB autosuspend fix and zero polling overhead.
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
ui_print "   Kali NetHunter WiFi Drivers Module v2.2   "
ui_print "   By Rohit Sharma (POCO F7 / Onyx)          "
ui_print "   Supports: Archer T2U Plus & WN722N        "
ui_print "   Fixes: USB Autosuspend + Zero Crash       "
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
echo "[+] Kernel Version:"
uname -a
echo ""
echo "[+] USB Power Management (Autosuspend):"
echo -n "  Global setting: "
cat /sys/module/usbcore/parameters/autosuspend 2>/dev/null || echo "N/A"
echo ""
echo "[+] Connected USB Devices (sysfs):"
FOUND_USB=0
for d in /sys/bus/usb/devices/*; do
  if [ -f "$d/idVendor" ] && [ -f "$d/idProduct" ]; then
    vid=$(cat "$d/idVendor")
    pid=$(cat "$d/idProduct")
    mfr=$(cat "$d/manufacturer" 2>/dev/null)
    prod=$(cat "$d/product" 2>/dev/null)
    pwr=$(cat "$d/power/control" 2>/dev/null)
    echo "  -> Device [$vid:$pid] $mfr $prod (Power: $pwr)"
    FOUND_USB=1
  fi
done
[ $FOUND_USB -eq 0 ] && echo "  [-] No external USB devices detected right now."
echo ""
echo "[+] Loaded Realtek Wireless Drivers (lsmod):"
lsmod 2>/dev/null | grep -E "8821au|8188eu|8812au|cfg80211|mac80211" || echo "[-] No external WiFi drivers loaded."
echo ""
echo "[+] Network Interfaces (ip link):"
ip link show | grep -E "wlan[0-9]|link/ether" || ifconfig -a
echo ""
echo "[+] Wireless Extensions Details (iw dev):"
iw dev 2>/dev/null || iwconfig 2>/dev/null || echo "[-] iw/iwconfig not available in this shell."
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
options 8821au rtw_power_mgnt=0 rtw_ips_mode=0 rtw_enusbss=0
options 8188eu rtw_power_mgnt=0 rtw_ips_mode=0
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
echo "Kali NetHunter Wireless Daemon v2.2 (Rohit Sharma Edition)" >> "$LOGFILE"
echo "Boot Date: $(date)" >> "$LOGFILE"
echo "Kernel: $(uname -r) ($(uname -m))" >> "$LOGFILE"
echo "Device: POCO F7 / Onyx (SM8735)" >> "$LOGFILE"
echo "============================================================" >> "$LOGFILE"
log_msg "NetHunter Wireless Service started."

# 1. Permanently disable USB autosuspend on kernel and all connected USB devices
echo -1 > /sys/module/usbcore/parameters/autosuspend 2>/dev/null
for dev in /sys/bus/usb/devices/*; do
  [ -f "$dev/power/autosuspend" ] && echo -1 > "$dev/power/autosuspend" 2>/dev/null
  [ -f "$dev/power/autosuspend_delay_ms" ] && echo -1 > "$dev/power/autosuspend_delay_ms" 2>/dev/null
  [ -f "$dev/power/control" ] && echo "on" > "$dev/power/control" 2>/dev/null
done
log_msg "[USB] Disabled USB autosuspend globally (parameter set to -1)."

# 2. Copy backup drivers & firmwares to SDCard for Kali Chroot accessibility
mkdir -p /sdcard/NetHunter-Drivers/modules 2>/dev/null
mkdir -p /sdcard/NetHunter-Drivers/firmware/rtlwifi 2>/dev/null
cp -rf "$MODDIR"/system/lib/modules/* /sdcard/NetHunter-Drivers/modules/ 2>/dev/null
cp -rf "$MODDIR"/system/etc/firmware/rtlwifi/* /sdcard/NetHunter-Drivers/firmware/rtlwifi/ 2>/dev/null

# 3. Unload conflicting in-tree driver if present
if lsmod 2>/dev/null | grep -q "rtl8xxxu"; then
  log_msg "Unloading conflicting in-tree driver rtl8xxxu..."
  rmmod rtl8xxxu 2>/dev/null || true
fi

# 4. Pre-load Archer T2U Plus (8821au) driver with zero power-saving
if [ -f "$MODDIR/system/lib/modules/8821au.ko" ]; then
  if ! lsmod 2>/dev/null | grep -q "8821au"; then
    log_msg "Pre-loading 8821au.ko (rtw_power_mgnt=0 rtw_ips_mode=0 rtw_enusbss=0)..."
    insmod "$MODDIR/system/lib/modules/8821au.ko" rtw_power_mgnt=0 rtw_ips_mode=0 rtw_enusbss=0 2>>"$LOGFILE"
    if [ $? -eq 0 ]; then
      log_msg "[SUCCESS] 8821au.ko registered with USB core. Ready for Archer T2U Plus hotplug!"
    else
      log_msg "[ERROR] Failed to load 8821au.ko."
    fi
  fi
fi

# 5. Pre-load TP-Link WN722N (8188eu) driver with zero power-saving
if [ -f "$MODDIR/system/lib/modules/8188eu.ko" ]; then
  if ! lsmod 2>/dev/null | grep -q "8188eu"; then
    log_msg "Pre-loading 8188eu.ko (rtw_power_mgnt=0 rtw_ips_mode=0)..."
    insmod "$MODDIR/system/lib/modules/8188eu.ko" rtw_power_mgnt=0 rtw_ips_mode=0 2>>"$LOGFILE"
    if [ $? -eq 0 ]; then
      log_msg "[SUCCESS] 8188eu.ko registered with USB core. Ready for TL-WN722N hotplug!"
    else
      log_msg "[ERROR] Failed to load 8188eu.ko."
    fi
  fi
fi

# 6. Pre-load 8812au driver if present
if [ -f "$MODDIR/system/lib/modules/8812au.ko" ]; then
  if ! lsmod 2>/dev/null | grep -q "8812au"; then
    insmod "$MODDIR/system/lib/modules/8812au.ko" rtw_power_mgnt=0 2>>"$LOGFILE"
  fi
fi

# 7. Background Interface Watcher Loop (Pure sysfs, ZERO lsusb calls to prevent collision with Android UsbHostManager)
(
  while true; do
    # Keep autosuspend disabled for any newly plugged devices
    echo -1 > /sys/module/usbcore/parameters/autosuspend 2>/dev/null
    for p in /sys/bus/usb/devices/*/power/autosuspend; do
      [ -f "$p" ] && echo -1 > "$p" 2>/dev/null
    done
    for c in /sys/bus/usb/devices/*/power/control; do
      [ -f "$c" ] && echo "on" > "$c" 2>/dev/null
    done

    # Scan for external USB wireless interfaces
    for iface_path in /sys/class/net/*; do
      [ -d "$iface_path" ] || continue
      ifname=$(basename "$iface_path")

      # Skip internal interfaces
      case "$ifname" in
        lo|dummy*|ifb*|tun*|gre*|sit*|ip6*|rmnet*|wifi-aware*|p2p*|wlan0) continue ;;
      esac

      # Check if this interface is attached via USB
      if [ -e "$iface_path/device" ] && readlink "$iface_path/device" 2>/dev/null | grep -qi "usb"; then
        # Check flags (bit 0 is IFF_UP)
        flags=$(cat "$iface_path/flags" 2>/dev/null)
        if [ -n "$flags" ]; then
          if [ $((flags & 1)) -eq 0 ]; then
            log_msg "[HOTPLUG] USB Wireless interface $ifname detected! Bringing UP..."
            ip link set "$ifname" up 2>/dev/null || ifconfig "$ifname" up 2>/dev/null || true
            sleep 1
            log_msg "[READY] Interface $ifname is UP and ready for Monitor Mode in Kali Chroot!"
          fi
        fi
      fi
    done

    sleep 2
  done
) &
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
