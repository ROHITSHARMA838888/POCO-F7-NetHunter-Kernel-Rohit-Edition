# POCO F7 (onyx) Kali NetHunter Kernel - Rohit Sharma Edition

Official Kali NetHunter Kernel build pipeline for **POCO F7 / Redmi Turbo 4 Pro (`onyx` / SM8735)** on Android 15 / 16 / 17 (InfinityOS, HyperOS, AOSP, PixelOS).

## Key Features
- **Linux Kernel 6.6 Generic Kernel Image (GKI)**
- **Packet / Frame Injection Support** (802.11 monitor mode + packet injection)
- **USB HID Gadget Support** (BadUSB / DuckHunter keyboard emulation via ConfigFS)
- **Built-in / Out-of-tree WiFi Drivers:**
  - TP-Link TL-WN722N v2/v3 (`rtl8188eus` / `rtl8xxxu`)
  - TP-Link Archer T2U Plus (`rtl8821au`)
  - Alfa AWUS036NHA / TP-Link TL-WN722N v1 (`ath9k_htc`)
  - Ralink RT3070 / RT5370 (`rt2800usb`)
- **KernelSU-Next + SUSFS Integration** (Full root & stealth capabilities)
- **Zero Stability Conflicts:**
  - Baseband-guard partition write interception REMOVED (No lockscreen shutdown)
  - Unstable GPU hacks REMOVED (No SurfaceFlinger crash)
  - Pure GKI KMI compatibility preserved for all ROM vendor modules.

## Author & Maintainer
- **Build Owner:** Rohit Sharma (`ROHITSHARMA838888`)
- **Edition:** Rohit Sharma Ultimate NetHunter Edition
