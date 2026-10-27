#!/usr/bin/env python3
import sys
import os
import re

def patch_8821au(driver_dir):
    print(f"[*] Patching RTL8821AU in {driver_dir}...")
    
    # 1. Disable USB autosuspend in usb_intf.c
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

    # 2. Fix wiphy_register WARN_ON and WoWLAN sanity checks in ioctl_cfg80211.c
    cfg_path = os.path.join(driver_dir, "os_dep", "linux", "ioctl_cfg80211.c")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Replace wowlan assignment with NULL so wiphy_register does not check or fail on WoWLAN ops
        content = re.sub(r'wiphy->wowlan\s*=\s*&?wowlan_stub;', 'wiphy->wowlan = NULL;', content)
        
        # Ensure suspend/resume are hooked in rtw_cfg80211_ops unconditionally
        old_ops = """#if defined(CONFIG_PNO_SUPPORT) && (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 0, 0))
	.sched_scan_start = cfg80211_rtw_sched_scan_start,
	.sched_scan_stop = cfg80211_rtw_sched_scan_stop,
	.suspend = cfg80211_rtw_suspend,
	.resume = cfg80211_rtw_resume,
#endif /* CONFIG_PNO_SUPPORT */"""
        new_ops = """#if (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 0, 0))
	.suspend = cfg80211_rtw_suspend,
	.resume = cfg80211_rtw_resume,
#if defined(CONFIG_PNO_SUPPORT)
	.sched_scan_start = cfg80211_rtw_sched_scan_start,
	.sched_scan_stop = cfg80211_rtw_sched_scan_stop,
#endif
#endif"""
        if old_ops in content:
            content = content.replace(old_ops, new_ops)
            print("[+] Fixed rtw_cfg80211_ops suspend/resume hooks in RTL8821AU")

        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Successfully patched RTL8821AU ioctl_cfg80211.c (WoWLAN NULL + suspend/resume ops)")

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

    # 3. Patch ioctl_cfg80211.c for WoWLAN and suspend/resume
    cfg_path = os.path.join(driver_dir, "os_dep", "linux", "ioctl_cfg80211.c")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        content = re.sub(r'wiphy->wowlan\s*=\s*&?wowlan_stub;', 'wiphy->wowlan = NULL;', content)
        
        old_ops = """#if defined(CONFIG_PNO_SUPPORT) && (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 0, 0))
	.sched_scan_start = cfg80211_rtw_sched_scan_start,
	.sched_scan_stop = cfg80211_rtw_sched_scan_stop,
	.suspend = cfg80211_rtw_suspend,
	.resume = cfg80211_rtw_resume,
#endif /* CONFIG_PNO_SUPPORT */"""
        new_ops = """#if (LINUX_VERSION_CODE >= KERNEL_VERSION(3, 0, 0))
	.suspend = cfg80211_rtw_suspend,
	.resume = cfg80211_rtw_resume,
#if defined(CONFIG_PNO_SUPPORT)
	.sched_scan_start = cfg80211_rtw_sched_scan_start,
	.sched_scan_stop = cfg80211_rtw_sched_scan_stop,
#endif
#endif"""
        if old_ops in content:
            content = content.replace(old_ops, new_ops)
            print("[+] Fixed rtw_cfg80211_ops suspend/resume hooks in RTL8188EUS")

        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Successfully patched RTL8188EUS ioctl_cfg80211.c (WoWLAN NULL + suspend/resume ops)")

if __name__ == "__main__":
    driver_type = sys.argv[1] if len(sys.argv) > 1 else ""
    driver_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    if driver_type == "8821au":
        patch_8821au(driver_dir)
    elif driver_type == "8188eu":
        patch_8188eu(driver_dir)
    else:
        print("Usage: patch_drivers.py <8821au|8188eu> <driver_dir>")
