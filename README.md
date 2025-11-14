# Simple Smart Power - CircuitPython Project

CircuitPython project for controlling NeoPixel and LEDs via MQTT on QT Py ESP32-S2.

## Features

- 🌈 NeoPixel control via MQTT
- 💡 GPIO LED control (A2 pin)
- 📡 WiFi connectivity
- 🔌 MQTT integration for remote control
- 🔧 Complete VS Code development environment

## Prerequisites

- CircuitPython-compatible board (QT Py ESP32-S2 or similar)
- Python 3.11+ (conda environment recommended)
- `ampy` - for file transfers to device
- `circup` - for CircuitPython library management
- `screen` - for serial monitor (or use `minicom` as alternative)

## Quick Start

### 1. Setup Development Environment

```bash
# Create and activate conda environment
conda env create -f environmnet.yaml
conda activate usb-simplepower

# Initialize project settings
make setup
# OR
cp settings.toml.example settings.toml
```

Edit `settings.toml` with your credentials:
```toml
CIRCUITPY_WIFI_SSID = "your-wifi-name"
CIRCUITPY_WIFI_PASSWORD = "your-wifi-password"
CIRCUITPY_WEB_API_PASSWORD = "your-api-password"

MQTT_BROKER = "your-mqtt-broker-ip"
MQTT_PORT = 1883
MQTT_USER = "mqtt-username"
MQTT_PASSWORD = "mqtt-password"
```

### 2. Install CircuitPython Libraries

```bash
# Automatically detect and install required libraries
make libs
# OR
circup install --auto --auto-file code.py
```

### 3. Deploy to Device

**Option A: Using VS Code Tasks (Recommended)**

Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac) and select:
- **Deploy to CircuitPython** - Deploy only code.py
- **Deploy All Files** - Deploy code.py and settings.toml
- **Update Libraries** - Install required libraries
- **Show Serial Monitor** - View device output
- **List CircuitPython Files** - See what's on device

**Option B: Using Makefile**

```bash
make deploy              # Deploy code.py only
make deploy-all          # Deploy code.py and settings.toml
make monitor             # Open serial monitor
make list                # List files on device
make pull                # Backup code.py from device
```

**Option C: Manual Deployment**

```bash
# Deploy files
ampy --port /dev/ttyACM0 put code.py
ampy --port /dev/ttyACM0 put settings.toml

# Monitor output
screen /dev/ttyACM0 115200
```

## MQTT Control

Send messages to these topics to control your device:

### NeoPixel Control
**Topic:** `home/neopixel`

**Commands:**
- `"255,0,0"` - Set to red (R,G,B format)
- `"0,255,0"` - Set to green
- `"0,0,255"` - Set to blue
- `"255,128,0"` - Set to orange
- `"off"` - Turn off

### LED Control (A2 Pin)
**Topic:** `home/led_a2`

**Commands:**
- `"on"` - Turn LED on
- `"off"` - Turn LED off

## Development Workflow

### Typical Workflow

1. **Edit** `code.py` in VS Code
2. **Deploy** using `Ctrl+Shift+B` → "Deploy to CircuitPython"
3. **Monitor** using task "Show Serial Monitor" or `make monitor`
4. **Debug** by viewing serial output
5. **Iterate** - make changes and redeploy

### Adding New Libraries

1. Add library import to `code.py`:
   ```python
   import adafruit_newlibrary
   ```

2. Add to `requirements.txt`:
   ```
   adafruit-circuitpython-newlibrary
   ```

3. Install:
   ```bash
   make libs
   # OR
   circup install adafruit-circuitpython-newlibrary
   ```

### Troubleshooting

**Device not found:**
```bash
# Find your device port
ls /dev/tty* | grep -E "(ACM|USB)"

# Use custom port
make deploy PORT=/dev/ttyUSB0
```

**CircuitPython not responding:**
- Unplug and replug the device
- Press reset button twice quickly to enter bootloader mode
- Check if CIRCUITPY drive is mounted

**Libraries not working:**
- Ensure CircuitPython version matches library bundle
- Check `lib/` folder on device has required libraries
- Run `circup update --all` to update all libraries

**Serial monitor issues:**
```bash
# Exit screen: Press Ctrl+A then K
# Alternative to screen:
minicom -D /dev/ttyACM0 -b 115200
```

## Project Structure

```
simple-smart-power/
├── code.py                    # Main CircuitPython code
├── settings.toml.example      # Settings template
├── settings.toml              # Your credentials (gitignored)
├── requirements.txt           # Library dependencies
├── Makefile                   # Command-line shortcuts
├── environmnet.yaml           # Conda environment config
├── README.md                  # This file
├── .gitignore                 # Git exclusions
├── .vscode/
│   ├── settings.json          # VS Code workspace settings
│   └── tasks.json             # VS Code tasks (Ctrl+Shift+B)
└── ENV/                       # Python virtual environment (gitignored)
```

## VS Code Tasks Reference

Access tasks via `Ctrl+Shift+P` → "Tasks: Run Task" or `Ctrl+Shift+B` for build tasks:

| Task | Description | Shortcut |
|------|-------------|----------|
| Deploy to CircuitPython | Deploy code.py | `Ctrl+Shift+B` (default) |
| Deploy All Files | Deploy code.py + settings.toml | - |
| Update Libraries (circup) | Install required libraries | - |
| Show Serial Monitor | Open serial console | - |
| List CircuitPython Files | Show device files | - |
| Pull code.py from Device | Backup from device | - |

## Required CircuitPython Libraries

These are automatically installed when you run `make libs`:

- `adafruit_neopixel` - NeoPixel LED control
- `adafruit_minimqtt` - MQTT client for IoT communication

## Version Control

This project is configured for Git with appropriate `.gitignore` settings:

✅ **Tracked:** Source code, configuration templates, documentation  
❌ **Ignored:** Secrets, virtual environments, compiled files

```bash
# Commit your changes
git add code.py requirements.txt
git commit -m "Update NeoPixel control logic"
git push
```

**Important:** Never commit `settings.toml` - it contains secrets!

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
