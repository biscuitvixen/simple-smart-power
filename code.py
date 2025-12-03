import json
import os
import time

import adafruit_minimqtt.adafruit_minimqtt as MQTT
import alarm
import board
import neopixel
import socketpool
import wifi
from pwmio import PWMOut

# Get credentials from settings.toml
try:
    WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
    WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    BOARD_ID = os.getenv("BOARD_ID")  # Unique identifier for this board
    # MQTT topics for JSON schema
    MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC") or f"home/light/{BOARD_ID}/set"
    MQTT_STATE_TOPIC = os.getenv("MQTT_STATE_TOPIC") or f"home/light/{BOARD_ID}/state"
    # Optional NeoPixel (defaults to True for backward compatibility)
    USE_NEOPIXEL = os.getenv("USE_NEOPIXEL", "true").lower() in ("true", "1", "yes")
except:
    print("Settings are kept in settings.toml, please add them there!")
    raise

# Initialize the NeoPixel on the QT Py ESP32-S2 (if enabled)
# The built-in NeoPixel is on pin NEOPIXEL
if USE_NEOPIXEL:
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)
else:
    pixel = None
    print("NeoPixel disabled in settings")

# Initialize LED on pin A2 with PWM for brightness control
led_a2 = PWMOut(board.A2, frequency=5000, duty_cycle=0)

# Light state
light_state = {
    "state": "ON",
    "brightness": 255,  # 0-255
}
last_brightness = 255  # Remember last non-zero brightness


def set_led_brightness(brightness):
    """Set LED brightness (0-255) using PWM."""
    global last_brightness
    if brightness > 0:
        # Convert 0-255 to 0-65535 (PWM duty cycle range)
        duty_cycle = int((brightness / 255) * 65535)
        led_a2.duty_cycle = duty_cycle
        light_state["brightness"] = brightness
        last_brightness = brightness  # Remember this brightness
    else:
        led_a2.duty_cycle = 0
        light_state["brightness"] = 0


def publish_state(client):
    """Publish current state to MQTT."""
    try:
        state_json = json.dumps(light_state)
        client.publish(MQTT_STATE_TOPIC, state_json)
        print(f"Published state: {state_json}")
    except Exception as e:
        print(f"Failed to publish state: {e}")


def publish_discovery(client):
    """Publish Home Assistant MQTT Discovery message."""
    try:
        discovery_topic = f"homeassistant/light/{BOARD_ID}/config"

        discovery_payload = {
            "name": "simple-smart-power-light",
            "unique_id": BOARD_ID,
            "command_topic": MQTT_COMMAND_TOPIC,
            "state_topic": MQTT_STATE_TOPIC,
            "schema": "json",
            "brightness": True,
            "brightness_scale": 255,
            "optimistic": False,
            "device": {
                "identifiers": [BOARD_ID],
                "name": f"Smart Power {BOARD_ID}",
                "model": "QT Py ESP32-S2",
                "manufacturer": "Adafruit",
            },
        }

        client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
        print(f"Published discovery to: {discovery_topic}")
    except Exception as e:
        print(f"Failed to publish discovery: {e}")


# Helper function for color wheel
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


# Stage 1: Initializing - Red
print("Stage 1: Initializing...")
if pixel:
    pixel[0] = (255, 0, 0)
    pixel.show()
time.sleep(0.5)

# Stage 2: Connecting to WiFi - Yellow
print(f"Stage 2: Connecting to {WIFI_SSID}...")
if pixel:
    pixel[0] = (255, 255, 0)
    pixel.show()
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID}!")
print(f"IP address: {wifi.radio.ipv4_address}")

# Stage 3: Setting up MQTT - Blue
print("Stage 3: Setting up MQTT...")
if pixel:
    pixel[0] = (0, 0, 255)
    pixel.show()

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)


# MQTT callback function
def message_received(client, topic, message):
    global last_brightness
    print(f"Topic: {topic}, Message: {message}")

    if topic == MQTT_COMMAND_TOPIC:
        try:
            # Parse JSON payload
            payload = json.loads(message)

            # Handle state
            if "state" in payload:
                if payload["state"] == "OFF":
                    led_a2.duty_cycle = 0
                    light_state["state"] = "OFF"
                    light_state["brightness"] = 0
                elif payload["state"] == "ON":
                    # Use brightness from payload, or restore last brightness
                    brightness = payload.get("brightness", last_brightness)
                    set_led_brightness(brightness)
                    light_state["state"] = "ON"

            # Handle brightness change (without explicit state)
            elif "brightness" in payload:
                brightness = int(payload["brightness"])
                set_led_brightness(brightness)
                light_state["state"] = "ON" if brightness > 0 else "OFF"

            # Publish updated state
            publish_state(client)

        except Exception as e:
            print(f"Error parsing message: {e}")


# Set up MQTT client
mqtt_client = MQTT.MQTT(broker=MQTT_BROKER, port=MQTT_PORT, socket_pool=pool)

# Set up callback
mqtt_client.on_message = message_received

# Connect to MQTT broker
print(f"Connecting to MQTT broker at {MQTT_BROKER}...")
mqtt_client.connect()

# Publish discovery message for Home Assistant
publish_discovery(mqtt_client)

# Subscribe to command topic
mqtt_client.subscribe(MQTT_COMMAND_TOPIC)
print(f"Subscribed to topic: {MQTT_COMMAND_TOPIC}")
print(f"Publishing state to: {MQTT_STATE_TOPIC}")
print(f"Listening for commands on: {MQTT_COMMAND_TOPIC}")

# Publish initial state
set_led_brightness(255)  # Start with LED on
publish_state(mqtt_client)

# Stage 4: Ready - Green
print("Stage 4: Ready!")
if pixel:
    print("Starting color wheel...")
    pixel[0] = (0, 255, 0)
    pixel.show()
time.sleep(1)

# Main loop - Color wheel with MQTT monitoring
color_position = 0
last_state_publish = time.monotonic()
STATE_PUBLISH_INTERVAL = 60  # Publish state every 60 seconds
SLEEP_DURATION = 10

while True:
    try:
        # Update color wheel (if NeoPixel enabled)
        if pixel:
            pixel[0] = wheel(color_position)
            pixel.show()
            color_position = (color_position + 1) % 256

        # Check for MQTT messages
        mqtt_client.loop()

        # Periodically publish state
        if time.monotonic() - last_state_publish > STATE_PUBLISH_INTERVAL:
            publish_state(mqtt_client)
            last_state_publish = time.monotonic()

        # Enter light sleep to save power
        print(f"Entering light sleep for {SLEEP_DURATION}s...")
        time_alarm = alarm.time.TimeAlarm(
            monotonic_time=time.monotonic() + SLEEP_DURATION
        )
        alarm.light_sleep_until_alarms(time_alarm)
        print("Woke from light sleep")

    except Exception as e:
        print(f"Error: {e}")
        if pixel:
            pixel[0] = (255, 0, 0)  # Red on error
            pixel.show()
        time.sleep(5)
        try:
            mqtt_client.reconnect()
            publish_state(mqtt_client)
        except Exception as e:
            print(f"Reconnect failed: {e}")
