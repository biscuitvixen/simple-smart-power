import time
import board
import neopixel
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from digitalio import DigitalInOut, Direction
import os

# Get credentials from settings.toml
try:
    WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
    WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
except:
    print("Settings are kept in settings.toml, please add them there!")
    raise

# MQTT topics
MQTT_TOPIC_NEOPIXEL = "home/neopixel"
MQTT_TOPIC_A2 = "home/led_a2"

# Initialize the NeoPixel on the QT Py ESP32-S2
# The built-in NeoPixel is on pin NEOPIXEL
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

# Initialize LED on pin A2
led_a2 = DigitalInOut(board.A2)
led_a2.direction = Direction.OUTPUT

# Connect to WiFi
print(f"Connecting to {WIFI_SSID}...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID}!")
print(f"IP address: {wifi.radio.ipv4_address}")

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# MQTT callback function
def message_received(client, topic, message):
    print(f"Topic: {topic}, Message: {message}")
    
    if topic == MQTT_TOPIC_NEOPIXEL:
        # Expected format: "R,G,B" or "off"
        if message.lower() == "off":
            pixel[0] = (0, 0, 0)
        else:
            try:
                r, g, b = map(int, message.split(","))
                pixel[0] = (r, g, b)
            except:
                print("Invalid NeoPixel color format")
        pixel.show()
    
    elif topic == MQTT_TOPIC_A2:
        # Expected format: "on" or "off"
        if message.lower() == "on":
            led_a2.value = True
        elif message.lower() == "off":
            led_a2.value = False

# Set up MQTT client
mqtt_client = MQTT.MQTT(
    broker=MQTT_BROKER,
    port=MQTT_PORT,
    socket_pool=pool
)

# Set up callback
mqtt_client.on_message = message_received

# Connect to MQTT broker
print(f"Connecting to MQTT broker at {MQTT_BROKER}...")
mqtt_client.connect()

# Subscribe to topics
mqtt_client.subscribe(MQTT_TOPIC_NEOPIXEL)
mqtt_client.subscribe(MQTT_TOPIC_A2)
print("Subscribed to MQTT topics")

# Main loop
while True:
    try:
        mqtt_client.loop()
        time.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
        try:
            mqtt_client.reconnect()
        except:
            pass