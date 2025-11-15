import json
import os
import time

import adafruit_minimqtt.adafruit_minimqtt as MQTT
import board
import neopixel
import socketpool
import wifi
from digitalio import DigitalInOut, Direction

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
except:
    print("Settings are kept in settings.toml, please add them there!")
    raise

# Initialize the NeoPixel on the QT Py ESP32-S2
# The built-in NeoPixel is on pin NEOPIXEL
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

# Initialize LED on pin A2
led_a2 = DigitalInOut(board.A2)
led_a2.direction = Direction.OUTPUT

# Light state
light_state = {
    "state": "ON",
    "brightness": 255,  # 0-255
}
last_brightness = 255  # Remember last non-zero brightness


def set_led_brightness(brightness):
    """Set LED brightness (0-255). For digital LED, treat as on/off threshold."""
    global last_brightness
    if brightness > 0:
        led_a2.value = True
        light_state["brightness"] = brightness
        last_brightness = brightness  # Remember this brightness
    else:
        led_a2.value = False
        light_state["brightness"] = 0


def publish_state(client):
    """Publish current state to MQTT."""
    try:
        state_json = json.dumps(light_state)
        client.publish(MQTT_STATE_TOPIC, state_json)
        print(f"Published state: {state_json}")
    except Exception as e:
        print(f"Failed to publish state: {e}")


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
pixel[0] = (255, 0, 0)
pixel.show()
time.sleep(0.5)

# Stage 2: Connecting to WiFi - Yellow
print(f"Stage 2: Connecting to {WIFI_SSID}...")
pixel[0] = (255, 255, 0)
pixel.show()
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID}!")
print(f"IP address: {wifi.radio.ipv4_address}")

# Stage 3: Setting up MQTT - Blue
print("Stage 3: Setting up MQTT...")
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
                    led_a2.value = False
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

# Subscribe to command topic
mqtt_client.subscribe(MQTT_COMMAND_TOPIC)
print(f"Subscribed to topic: {MQTT_COMMAND_TOPIC}")
print(f"Publishing state to: {MQTT_STATE_TOPIC}")
print(f"Listening for commands on: {MQTT_COMMAND_TOPIC}")

# Publish initial state
set_led_brightness(255)  # Start with LED on
publish_state(mqtt_client)

# Stage 4: Ready - Green
print("Stage 4: Ready! Starting color wheel...")
pixel[0] = (0, 255, 0)
pixel.show()
time.sleep(1)

# Main loop - Color wheel with MQTT monitoring
color_position = 0
last_state_publish = time.monotonic()
STATE_PUBLISH_INTERVAL = 60  # Publish state every 60 seconds

while True:
    try:
        # Update color wheel
        pixel[0] = wheel(color_position)
        pixel.show()
        color_position = (color_position + 1) % 256

        # Check for MQTT messages
        mqtt_client.loop()

        # Periodically publish state
        if time.monotonic() - last_state_publish > STATE_PUBLISH_INTERVAL:
            publish_state(mqtt_client)
            last_state_publish = time.monotonic()

        time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")
        pixel[0] = (255, 0, 0)  # Red on error
        pixel.show()
        time.sleep(5)
        try:
            mqtt_client.reconnect()
            publish_state(mqtt_client)
        except Exception as e:
            print(f"Reconnect failed: {e}")
