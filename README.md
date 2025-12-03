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

The device uses JSON schema for MQTT communication with Home Assistant.

### LED Control (A2 Pin)
**Command Topic:** `home/light/{BOARD_ID}/set`  
**State Topic:** `home/light/{BOARD_ID}/state`

**Commands (JSON):**
```json
{"state": "ON"}                    // Turn on
{"state": "OFF"}                   // Turn off
{"state": "ON", "brightness": 128} // Turn on with brightness
{"brightness": 200}                // Set brightness (auto-turns on)
```

**State Updates:**
The device publishes its current state:
```json
{"state": "ON", "brightness": 255}
```

### Home Assistant Configuration

Add to your `configuration.yaml`:

```yaml
mqtt:
  light:
    - name: "Smart Power Light"
      unique_id: "smart_power_light_1"
      command_topic: "home/light/YOUR_BOARD_ID/set"
      state_topic: "home/light/YOUR_BOARD_ID/state"
      schema: json
      brightness: true
      optimistic: false
```

Replace `YOUR_BOARD_ID` with the value from your `settings.toml`.

### Testing with MQTT Client

```bash
# Turn on
mosquitto_pub -h YOUR_BROKER -t "home/light/YOUR_BOARD_ID/set" -m '{"state":"ON"}'

# Turn off
mosquitto_pub -h YOUR_BROKER -t "home/light/YOUR_BOARD_ID/set" -m '{"state":"OFF"}'

# Set brightness
mosquitto_pub -h YOUR_BROKER -t "home/light/YOUR_BOARD_ID/set" -m '{"brightness":128}'

# Subscribe to state updates
mosquitto_sub -h YOUR_BROKER -t "home/light/YOUR_BOARD_ID/state"
```

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

**CIRCUITPY drive not mounting:**
- If the CIRCUITPY USB drive isn't appearing, you can still deploy via serial (see below).
- Alternatively, enable Web Workflow in `settings.toml` and use the device's IP address with `circup --host <IP>`.

### Deploy Libraries over Serial (ampy)

If CIRCUITPY is not mounting, you can push files via serial. ampy doesn't handle directories recursively, so use a helper script to upload everything under `lib/`.

**Windows (PowerShell):**
```pwsh
# Set your COM port
$PORT = "COM5"

# Upload code and settings
ampy --port $PORT put .\code.py
ampy --port $PORT put .\settings.toml

# Upload libraries from lib/ recursively
Get-ChildItem -Recurse -File .\lib | ForEach-Object {
  $rel = $_.FullName.Substring((Resolve-Path ".").Path.Length + 1)
  $relPosix = $rel -replace '\\','/'
  ampy --port $PORT put $_.FullName $relPosix
}

# Verify on device
ampy --port $PORT ls
ampy --port $PORT ls /lib
```

**Linux:**
```bash
PORT=/dev/ttyACM0

# Upload code and settings
ampy --port "$PORT" put ./code.py
ampy --port "$PORT" put ./settings.toml

# Upload libraries recursively
find ./lib -type f -print0 | while IFS= read -r -d '' f; do
  rel="${f#./}"
  ampy --port "$PORT" put "$f" "$rel"
done

# Verify on device
ampy --port "$PORT" ls
ampy --port "$PORT" ls /lib
```

**Tips:**
- Ensure the board is running CircuitPython (REPL accessible).
- If uploads fail intermittently, press reset once and retry.
- Large transfers are more reliable via CIRCUITPY drive or Web Workflow.
- For faster/bulk library management, prefer `circup` when CIRCUITPY or Web Workflow is available.

## Device Ports & Firmware Flashing

### Find Device Ports

- Windows (PowerShell):
   ```pwsh
   # List all serial ports
   Get-CimInstance Win32_SerialPort | Select-Object Name, DeviceID

   # Quick view of COM ports only
   Get-ChildItem HKLM:\HARDWARE\DEVICEMAP\SERIALCOMM | Select-Object -ExpandProperty Property
   Get-ChildItem HKLM:\HARDWARE\DEVICEMAP\SERIALCOMM | ForEach-Object { $_.GetValue('') }
   ```

- Linux:
   ```bash
   ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
   dmesg | grep -Ei "(ttyACM|ttyUSB)"
   ```

Use the detected port (e.g., `COM5` on Windows or `/dev/ttyACM0` on Linux) in tasks and commands.

### Erase & Flash Firmware (esptool)

For QT Py ESP32-S2 (or similar ESP32-S2 boards). Make sure you have `esptool` installed and know your serial port.

- Install `esptool`:
   ```pwsh
   # Windows (PowerShell)
   python -m pip install esptool
   ```
   ```bash
   # Linux
   python3 -m pip install esptool
   ```

- Put board in bootloader mode: hold BOOT (or 0) while pressing RESET, then release RESET first.

- Erase flash:
   ```pwsh
   # Windows
   esptool.py --chip esp32s2 --port COM5 erase-flash
   ```
   ```bash
   # Linux
   esptool.py --chip esp32s2 --port /dev/ttyACM0 erase-flash
   ```

- Flash CircuitPython firmware (.bin): download the ESP32-S2 "combined" `.bin` from CircuitPython releases, then:
   ```pwsh
   # Windows
   esptool.py --chip esp32s2 --port COM5 --baud 460800 write-flash -z 0x0000 path\to\firmware.bin
   ```
   ```bash
   # Linux
   esptool.py --chip esp32s2 --port /dev/ttyACM0 --baud 460800 write-flash -z 0x0000 /path/to/firmware.bin
   ```

- After flashing, press RESET. The `CIRCUITPY` drive should mount; then deploy `code.py` and `settings.toml`.

Notes:
- Replace `COM5` or `/dev/ttyACM0` with your actual port.
- If flashing fails, try lowering baud (e.g., `115200`) or unplug/replug the device.
- For other ESP32 variants, adjust `--chip` accordingly (e.g., `esp32`, `esp32s3`).

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
