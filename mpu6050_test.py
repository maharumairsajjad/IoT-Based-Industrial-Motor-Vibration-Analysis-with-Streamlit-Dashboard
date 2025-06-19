import network
import urequests
import json
from mpu6050 import MPU6050  # Ensure mpu6050.py is uploaded to ESP32
from time import sleep

# Wi-Fi credentials
SSID = "ssss" # Add your wifi name 
PASSWORD = "12345678"

# Firebase credentials
FIREBASE_URL = " " # Add your Firebase URL from firebase
WEB_API_KEY = " "  # Add your web api key from firebase

# Connect to Wi-Fi
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    while not wifi.isconnected():
        pass
    print("Connected to Wi-Fi")

# Send data to Firebase
def send_data_to_firebase(data):
    url = f"{FIREBASE_URL}/sensor_data.json?auth={WEB_API_KEY}"
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.put(url, headers=headers, data=json.dumps(data))
        print("Data sent to Firebase:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

# Initialize MPU6050
connect_wifi()
sensor = MPU6050()

while True:
    try:
        accel_data = sensor.read_accel_data()
        gyro_data = sensor.read_gyro_data()
        temperature = sensor.read_temperature()
        
        # Prepare data for Firebase
        sensor_data = {
            "acceleration": accel_data,
            "gyroscope": gyro_data,
            "temperature": temperature
        }
        
        send_data_to_firebase(sensor_data)

        # Print sensor readings
        print("Accel:", accel_data, "Gyro:", gyro_data, "Temp:", temperature)
        sleep(1)  # Delay of 1 second for smooth updates

    except Exception as e:
        print("Error:", e)
        sleep(5)
