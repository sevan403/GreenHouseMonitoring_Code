# test_sensors.py

import time
import Adafruit_DHT
import smbus2
import RPi.GPIO as GPIO

# ---------- DHT22 (Temperature & Humidity) ----------
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin connected to the DHT22 data pin

# ---------- BH1750 (Light Sensor) ----------
BH1750_ADDR = 0x23
CONT_H_RES_MODE = 0x10

def read_light(bus):
    data = bus.read_i2c_block_data(BH1750_ADDR, CONT_H_RES_MODE, 2)
    light_level = (data[0] << 8) + data[1]
    return light_level / 1.2  # Convert to lux

# ---------- Soil Moisture Sensor ----------
SOIL_PIN = 17  # GPIO pin for digital soil moisture sensor

def read_soil():
    return GPIO.input(SOIL_PIN)  # 0 = Wet, 1 = Dry

# ---------- Setup ----------
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_PIN, GPIO.IN)
bus = smbus2.SMBus(1)

# ---------- Main Loop ----------
try:
    while True:
        # DHT22
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            print(f"DHT22 -> Temp: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
        else:
            print("DHT22 -> Failed to retrieve data")

        # BH1750
        try:
            light_level = read_light(bus)
            print(f"BH1750 -> Light Level: {light_level:.2f} lux")
        except Exception as e:
            print(f"BH1750 -> Error reading light: {e}")

        # Soil Moisture
        soil_status = read_soil()
        print(f"Soil Moisture -> {'Dry' if soil_status else 'Wet'}")

        print("-" * 40)
        time.sleep(2)

except KeyboardInterrupt:
    print("Test stopped by user.")
finally:
    GPIO.cleanup()
