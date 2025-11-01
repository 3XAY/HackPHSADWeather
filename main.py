import os
import network
import time
import urequests
from machine import Pin, ADC
from dotenv import load_dotenv

load_dotenv() 

# --- CONFIGURATION ---
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
ip = os.getenv("SERVER_IP")

API_ENDPOINT = f"http://{ip}:{5000}/plant_data"

soil_moisture_adc = ADC(Pin(26))

def connect_to_wifi():
    """Connects the Pico W to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 15
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        print(f"Failed to connect to Wi-Fi: Status {wlan.status()}")
        return False
    else:
        print(f'Connected! Pico IP address: {wlan.ifconfig()[0]}')
        return True


def read_soil_moisture():
    """Reads the 16-bit analog soil moisture value (0 - 65535)."""
    return soil_moisture_adc.read_u16()

def send_data(moisture_value):
    """Sends the soil moisture reading to the server via HTTP POST."""

    try:
        response = urequests.post(API_ENDPOINT, json=moisture_value)
        if response.status_code == 200:
            print("Data sent successfully!")
        else:
            print(f"Server error: HTTP {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Failed to send data: {e}")

# --- MAIN LOOP ---
if connect_to_wifi():
    while True:
        moisture = read_soil_moisture()
        send_data(moisture)
        time.sleep(60)