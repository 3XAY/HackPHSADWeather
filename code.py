import board
import analogio
import time
import wifi
import socketpool
import adafruit_requests
import os

ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
server_ip = os.getenv("SERVER_IP")
connected = False

while not connected:
    try:
        wifi.radio.connect(ssid, password)
        print("Connected to WiFi")
        print("IP: " + str(wifi.radio.ipv4_address))
        connected = True
    except RuntimeError as e:
        print("Retrying")

redPin = analogio.AnalogIn(board.A0)
greenPin = analogio.AnalogIn(board.A1)
bluePin = analogio.AnalogIn(board.A3)
moisturePin = analogio.AnalogIn(board.A5)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

SERVER_URL = f"http://{server_ip}:5000/plant_data"

while True:
    red = redPin.value
    green = greenPin.value
    blue = bluePin.value
    moisture = moisturePin.value
    
    print(f"R:{red} G:{green} B:{blue} M:{moisture}")
    
    data = {
        "red": red,
        "green": green,
        "blue": blue,
        "moisture": moisture
    }
    
    try:
        response = requests.post(SERVER_URL, json=data)
        print(f"Server: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(60)
