#!/usr/bin/env python3
import sys
import os

def patch_8821au(driver_dir):
    print(f"[*] Patching RTL8821AU in {driver_dir}...")
    usb_intf_path = os.path.join(driver_dir, "os_dep", "linux", "usb_intf.c")
    if os.path.exists(usb_intf_path):
        with open(usb_intf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        target = "dvobj = usb_dvobj_init(pusb_intf, pdid);"
        repl = "dvobj = usb_dvobj_init(pusb_intf, pdid);\n\tusb_disable_autosuspend(interface_to_usbdev(pusb_intf));"
        if target in content and "usb_disable_autosuspend" not in content:
            content = content.replace(target, repl, 1)
            with open(usb_intf_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("[+] Successfully added usb_disable_autosuspend to RTL8821AU usb_intf.c")
        else:
            print("[-] RTL8821AU usb_intf.c already patched or target not found.")

def patch_8188eu(driver_dir):
    print(f"[*] Patching RTL8188EUS in {driver_dir}...")
    
    # 1. Patch wifi_regd.c to completely remove regulatory crash/panic
    regd_path = os.path.join(driver_dir, "os_dep", "linux", "wifi_regd.c")
    if os.path.exists(regd_path):
        with open(regd_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        target = "static void _rtw_regd_init_wiphy(struct rtw_regulatory *reg, struct wiphy *wiphy)"
        idx = content.find(target)
        if idx != -1:
            end_marker = "int rtw_regd_init(struct wiphy *wiphy)"
            end_idx = content.find(end_marker, idx)
            if end_idx != -1:
                safe_regd_func = (
                    "static void _rtw_regd_init_wiphy(struct rtw_regulatory *reg, struct wiphy *wiphy)\n"
                    "{\n"
                    "\twiphy->reg_notifier = rtw_reg_notifier;\n"
                    "\twiphy->regulatory_flags &= ~REGULATORY_STRICT_REG;\n"
                    "\twiphy->regulatory_flags &= ~REGULATORY_DISABLE_BEACON_HINTS;\n"
                    "}\n\n"
                )
                content = content[:idx] + safe_regd_func + content[end_idx:]
                with open(regd_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("[+] Successfully replaced _rtw_regd_init_wiphy with safe non-crashing implementation in RTL8188EUS!")

    # 2. Patch usb_intf.c to disable autosuspend
    usb_intf_path = os.path.join(driver_dir, "os_dep", "linux", "usb_intf.c")
    if os.path.exists(usb_intf_path):
        with open(usb_intf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        target = "dvobj = usb_dvobj_init(pusb_intf, pdid);"
        repl = "dvobj = usb_dvobj_init(pusb_intf, pdid);\n\tusb_disable_autosuspend(interface_to_usbdev(pusb_intf));"
        if target in content and "usb_disable_autosuspend" not in content:
            content = content.replace(target, repl, 1)
            with open(usb_intf_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("[+] Successfully added usb_disable_autosuspend to RTL8188EUS usb_intf.c")

if __name__ == "__main__":
    driver_type = sys.argv[1] if len(sys.argv) > 1 else ""
    driver_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    if driver_type == "8821au":
        patch_8821au(driver_dir)
    elif driver_type == "8188eu":
        patch_8188eu(driver_dir)
    else:
        print("Usage: patch_drivers.py <8821au|8188eu> <driver_dir>")
