#!/usr/bin/env python3
"""
OpenGrow-Box Sensor Client

This script runs on the Sensor Raspberry Pi to collect data from the
connected sensors and send it to the Dashboard Pi via MQTT.

Hardware connections:
- DHT22: GPIO4 (temperature/humidity)
- BH1750: I2C (SDA/SCL) (light intensity)
- Capacitive Soil Moisture: GPIO17
- Relay module for fan/light/water pump controls
"""

import os
import time
import json
import logging
import signal
import threading
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sensor_pi.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sensor_pi")

# Import sensor libraries
try:
    import RPi.GPIO as GPIO
    import Adafruit_DHT
    from smbus2 import SMBus
    import paho.mqtt.client as mqtt
    SIMULATION_MODE = False
    logger.info("Running in hardware mode with real sensors")
except ImportError as e:
    logger.warning(f"Error importing hardware libraries: {e}")
    logger.warning("Running in simulation mode with simulated sensor data")
    SIMULATION_MODE = True

# MQTT Configuration
MQTT_BROKER = os.environ.get("MQTT_BROKER", "192.168.10.36")  # Dashboard Pi IP
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", None)
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", None)
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "sensor_pi")

# MQTT Topics
TOPIC_SENSOR_DATA = "opengrow/sensors/data"
TOPIC_CONTROL_COMMAND = "opengrow/control/command"
TOPIC_CONTROL_STATUS = "opengrow/control/status"
TOPIC_SYSTEM_STATUS = "opengrow/system/status"

# GPIO Pin definitions based on user's equipment
# Sensor connections
DHT_SENSOR_PIN = 4  # DHT22 on GPIO4
# BH1750 uses I2C (SDA/SCL) - no specific GPIO pin needed
SOIL_MOISTURE_PIN = 17  # Capacitive soil moisture on GPIO17

# Actuator connections through relay module
FAN_PIN = 18  # Example relay pin for fan
LIGHT_PIN = 23  # Example relay pin for grow lights
WATER_PUMP_PIN = 24  # Example relay pin for water pump

# BH1750 I2C address
BH1750_ADDR = 0x23

# DHT sensor type
DHT_SENSOR_TYPE = Adafruit_DHT.DHT22 if not SIMULATION_MODE else None

# Global variables
mqtt_client = None
is_connected = False
running = True
control_state = {
    'fan': False,
    'light': False,
    'water_pump': False
}

def initialize_hardware():
    """Initialize GPIO and sensors"""
#CHANGED_LINE *******
    global SIMULATION_MODE
    if SIMULATION_MODE:
        logger.info("Initializing in simulation mode")
        return

    try:
        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup output pins for relays
        GPIO.setup(FAN_PIN, GPIO.OUT)
        GPIO.setup(LIGHT_PIN, GPIO.OUT)
        GPIO.setup(WATER_PUMP_PIN, GPIO.OUT)

        # Setup input pin for soil moisture
        GPIO.setup(SOIL_MOISTURE_PIN, GPIO.IN)

        # Initialize outputs to OFF
        GPIO.output(FAN_PIN, GPIO.LOW)
        GPIO.output(LIGHT_PIN, GPIO.LOW)
        GPIO.output(WATER_PUMP_PIN, GPIO.LOW)

        logger.info("Hardware initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing hardware: {e}")
        logger.warning("Falling back to simulation mode")

        SIMULATION_MODE = True

def cleanup():
    """Clean up GPIO and MQTT connections on exit"""
    logger.info("Cleaning up resources...")

    # Disconnect MQTT
    if mqtt_client:
        try:
            # Send offline status
            offline_payload = json.dumps({
                'status': 'offline',
                'timestamp': datetime.now().isoformat()
            })
            mqtt_client.publish(TOPIC_SYSTEM_STATUS, offline_payload, qos=1, retain=True)
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
        except Exception as e:
            logger.error(f"Error disconnecting MQTT: {e}")

    # Clean up GPIO
    if not SIMULATION_MODE:
        try:
            # Turn off all actuators
            GPIO.output(FAN_PIN, GPIO.LOW)
            GPIO.output(LIGHT_PIN, GPIO.LOW)
            GPIO.output(WATER_PUMP_PIN, GPIO.LOW)
            GPIO.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up GPIO: {e}")

    logger.info("Cleanup complete")

def read_dht22():
    """Read temperature and humidity from DHT22 sensor"""
    if SIMULATION_MODE:
        temperature = round(random.uniform(18.0, 30.0), 1)
        humidity = round(random.uniform(30.0, 80.0), 1)
        return humidity, temperature

    try:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)
        if humidity is None or temperature is None:
            logger.warning("Failed to read from DHT sensor")
            return None, None
        return round(humidity, 1), round(temperature, 1)
    except Exception as e:
        logger.error(f"Error reading DHT22: {e}")
        return None, None

def read_bh1750():
    """Read light intensity from BH1750 sensor"""
    if SIMULATION_MODE:
        return round(random.uniform(0.0, 1000.0), 1)

    try:
        with SMBus(1) as bus:  # 1 = Raspberry Pi's I2C bus
            # 0x20 = One time high resolution mode (1 lux resolution)
            bus.write_byte(BH1750_ADDR, 0x20)
            time.sleep(0.2)  # Wait for measurement
            data = bus.read_i2c_block_data(BH1750_ADDR, 0x20, 2)
            light_level = (data[0] << 8 | data[1]) / 1.2  # Convert to lux
            return round(light_level, 1)
    except Exception as e:
        logger.error(f"Error reading BH1750: {e}")
        return None

def read_soil_moisture():
    """Read soil moisture from capacitive sensor"""
    if SIMULATION_MODE:
        return round(random.uniform(0.0, 100.0), 1)

    try:
        # Digital read for capacitive sensor
        # Low = wet, High = dry
        moisture_digital = GPIO.input(SOIL_MOISTURE_PIN)

        # Convert to percentage (simplified)
        # In a real implementation, you might need to calibrate or use an ADC
        # for analog readings to get more precision
        moisture_percentage = 0.0 if moisture_digital else 100.0
        return moisture_percentage
    except Exception as e:
        logger.error(f"Error reading soil moisture: {e}")
        return None

def read_sensors():
    """Read all sensors and return data dict"""
    humidity, temperature = read_dht22()
    light_level = read_bh1750()
    soil_moisture = read_soil_moisture()

    # Build sensor data dictionary
    sensor_data = {
        'temperature': temperature if temperature is not None else 20.0,
        'humidity': humidity if humidity is not None else 50.0,
        'light_level': light_level if light_level is not None else 500.0,
        'soil_moisture': soil_moisture if soil_moisture is not None else 50.0,
        'timestamp': datetime.now().isoformat()
    }

    return sensor_data

def control_fan(state):
    """Control the fan relay"""
    control_state['fan'] = state
    logger.info(f"Setting fan to {'ON' if state else 'OFF'}")

    if not SIMULATION_MODE:
        try:
            GPIO.output(FAN_PIN, GPIO.HIGH if state else GPIO.LOW)
        except Exception as e:
            logger.error(f"Error controlling fan: {e}")

    # Send status update via MQTT
    send_control_status()
    return state

def control_light(state):
    """Control the light relay"""
    control_state['light'] = state
    logger.info(f"Setting light to {'ON' if state else 'OFF'}")

    if not SIMULATION_MODE:
        try:
            GPIO.output(LIGHT_PIN, GPIO.HIGH if state else GPIO.LOW)
        except Exception as e:
            logger.error(f"Error controlling light: {e}")

    # Send status update via MQTT
    send_control_status()
    return state

def control_water_pump(state):
    """Control the water pump relay"""
    control_state['water_pump'] = state
    logger.info(f"Setting water pump to {'ON' if state else 'OFF'}")

    if not SIMULATION_MODE:
        try:
            GPIO.output(WATER_PUMP_PIN, GPIO.HIGH if state else GPIO.LOW)
        except Exception as e:
            logger.error(f"Error controlling water pump: {e}")

    # Send status update via MQTT
    send_control_status()
    return state

def send_sensor_data(sensor_data):
    """Send sensor data to MQTT broker"""
    if not is_connected or mqtt_client is None:
        logger.warning("Cannot send sensor data - not connected to MQTT broker")
        return False

    try:
        payload = json.dumps(sensor_data)
        mqtt_client.publish(TOPIC_SENSOR_DATA, payload, qos=1)
        logger.debug(f"Sent sensor data: {sensor_data}")
        return True
    except Exception as e:
        logger.error(f"Error sending sensor data: {e}")
        return False

def send_control_status():
    """Send control states to MQTT broker"""
    if not is_connected or mqtt_client is None:
        logger.warning("Cannot send control status - not connected to MQTT broker")
        return False

    try:
        payload = json.dumps({
            **control_state,
            'timestamp': datetime.now().isoformat()
        })
        mqtt_client.publish(TOPIC_CONTROL_STATUS, payload, qos=1)
        logger.debug(f"Sent control status: {control_state}")
        return True
    except Exception as e:
        logger.error(f"Error sending control status: {e}")
        return False

def on_connect(client, userdata, flags, rc):
    """Called when connected to MQTT broker"""
    global is_connected
    if rc == 0:
        logger.info("Connected to MQTT broker")
        is_connected = True

        # Subscribe to control commands
        client.subscribe(TOPIC_CONTROL_COMMAND)

        # Send initial control status
        send_control_status()

        # Send online status
        online_payload = json.dumps({
            'device': 'sensor-pi',
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        })
        client.publish(TOPIC_SYSTEM_STATUS, online_payload, qos=1, retain=True)
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")
        is_connected = False

def on_disconnect(client, userdata, rc):
    """Called when disconnected from MQTT broker"""
    global is_connected
    logger.warning(f"Disconnected from MQTT broker with code {rc}")
    is_connected = False

def on_message(client, userdata, msg):
    """Called when a message is received from MQTT broker"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        logger.debug(f"Received message on topic {topic}: {payload}")

        if topic == TOPIC_CONTROL_COMMAND:
            process_control_command(payload)
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def process_control_command(payload):
    """Process control commands from MQTT"""
    try:
        command = payload.get('command')
        value = payload.get('value')

        if command == 'fan':
            control_fan(bool(value))
        elif command == 'light':
            control_light(bool(value))
        elif command == 'water_pump':
            control_water_pump(bool(value))
        else:
            logger.warning(f"Unknown command: {command}")
    except Exception as e:
        logger.error(f"Error processing control command: {e}")

def connect_mqtt():
    """Connect to MQTT broker"""
    global mqtt_client, is_connected

    try:
        # Create client
        mqtt_client = mqtt.Client(MQTT_CLIENT_ID)

        # Set callbacks
        mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.on_message = on_message

        # Set authentication if provided
        if MQTT_USERNAME and MQTT_PASSWORD:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Set will (testament) message
        will_payload = json.dumps({
            'device': 'sensor-pi',
            'status': 'offline',
            'timestamp': datetime.now().isoformat()
        })
        mqtt_client.will_set(TOPIC_SYSTEM_STATUS, will_payload, qos=1, retain=True)

        # Connect to broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

        # Start loop in background thread
        mqtt_client.loop_start()

        return True
    except Exception as e:
        logger.error(f"Error connecting to MQTT broker: {e}")
        return False

def sensor_loop():
    """Main sensor reading and reporting loop"""
    global running

    logger.info("Starting sensor loop")
    reading_interval = 30  # seconds

    while running:
        try:
            # Read sensors
            sensor_data = read_sensors()

            # Send data via MQTT
            if is_connected:
                send_sensor_data(sensor_data)
            else:
                logger.warning("Not connected to MQTT - skipping data transmission")

            # Sleep until next reading
            time.sleep(reading_interval)
        except Exception as e:
            logger.error(f"Error in sensor loop: {e}")
            time.sleep(5)  # Sleep shorter time on error

def signal_handler(sig, frame):
    """Handle termination signals"""
    global running
    logger.info("Received termination signal")
    running = False

def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize hardware
        initialize_hardware()

        # Connect to MQTT broker
        if not connect_mqtt():
            logger.error("Failed to connect to MQTT broker - continuing with local operation only")

        # Start sensor loop in main thread
        sensor_loop()
    except Exception as e:
        logger.error(f"Error in main function: {e}")
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main()
