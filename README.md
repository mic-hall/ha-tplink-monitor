# TP-Link Switch Bandwidth Monitor (Home Assistant Integration)
A Home Assistant integration to monitor bandwidth usage on TP-Link Easy Smart Switches.

## Features
✔ Real-time bandwidth monitoring (RX/TX Mbps)  
✔ Works with TP-Link TL-SG1016DE, TL-SG108E, and similar models  
✔ Configurable polling interval & MTU  
✔ Home Assistant UI-based setup (no YAML required!)  

## Installation via HACS
1. Go to **HACS → Integrations → Custom Repositories**  
2. Add `https://github.com/bairnhard/ha-tplink-monitor` as an **Integration**  
3. Search for **"TP-Link Switch Bandwidth Monitor"** and install it  
4. Restart Home Assistant  
5. Add the integration from **Settings → Integrations**  

## Manual Installation
1. Copy `tplink_monitor/` to `/config/custom_components/`
2. Restart Home Assistant  
3. Add the integration via **Settings → Integrations**  

## Supported Switches
**TP-Link Easy Smart Switches:**
- TL-SG1016DE
- TL-SG108E
- TL-SG105E
- TL-SG1024DE  

## Notes
- **Your switch must have a static IP!**
- **Tested on Home Assistant 2023.1+**
