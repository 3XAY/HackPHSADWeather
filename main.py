import os
import time
import requests
from gpiozero import MCP3008
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
SERVER_IP = os.getenv("SERVER_IP")  # IP of Device 2's Pi
DEVICE_ID = "sensor_node_1"

API_ENDPOINT = f"http://{SERVER_IP}:5000/plant_data"

# --- SENSOR SETUP ---
soil_moisture_adc = MCP3008(channel=0)  # Screw probes
red_light_adc = MCP3008(channel=1)      # Red light sensor (photodiode)
blue_light_adc = MCP3008(channel=2)     # Blue light sensor
green_light_adc = MCP3008(channel=3)    # Green light sensor


def read_sensors():
    """Read all sensor values"""
    moisture = int(soil_moisture_adc.value * 65535)
    red_light = int(red_light_adc.value * 65535)
    blue_light = int(blue_light_adc.value * 65535)
    green_light = int(green_light_adc.value * 65535)
    return moisture, red_light, blue_light, green_light


def send_data(moisture, red, blue, green):
    """Send data to server"""
    data = {
        "device_id": DEVICE_ID,
        "moisture": moisture,
        "red_light": red,      # Red light intensity
        "blue_light": blue,    # Blue light intensity
        "green_light": green   # Green light intensity
    }

    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
        if response.status_code == 200:
            print("✓ Data sent successfully!")
            return True
        else:
            print(f"✗ Server error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to send data: {e}")
        return False


# --- MAIN LOOP ---
print(f"Starting sensor node: {DEVICE_ID}")
print("Sensors: Soil Moisture + RGB Light Detection")

while True:
    try:
        moisture, red, blue, green = read_sensors()
        
        print(f"\n--- Sensor Reading ---")
        print(f"Soil Moisture: {moisture}")
        print(f"Red Light:     {red}")
        print(f"Green Light:   {green}")
        print(f"Blue Light:    {blue}")
        
        send_data(moisture, red, blue, green)
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(60)  # Send every 60 seconds