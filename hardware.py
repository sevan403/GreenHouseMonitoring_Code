import logging
import time
import threading
from models import ControlState, SensorReading
from app import db
import random

# Setup logging
logger = logging.getLogger(__name__)

# Flag to determine if running on actual hardware or in simulation mode
SIMULATION_MODE = True

# Define GPIO and Adafruit_DHT as None initially to avoid unbound errors
GPIO = None
Adafruit_DHT = None

# GPIO Pin definitions (used only when not in simulation mode)
FAN_PIN = 17
LIGHT_PIN = 18
WATER_PUMP_PIN = 27
DHT_SENSOR_PIN = 4
LIGHT_SENSOR_PIN = 23
SOIL_MOISTURE_PIN = 24

# DHT sensor type (DHT22 or DHT11) - only defined when hardware is available
DHT_SENSOR_TYPE = None

try:
    import RPi.GPIO as GPIO
    import Adafruit_DHT
    SIMULATION_MODE = False
    DHT_SENSOR_TYPE = Adafruit_DHT.DHT22
    logger.info("Hardware libraries loaded successfully")
except ImportError:
    logger.warning("RPi.GPIO or Adafruit_DHT not found. Running in simulation mode.")

# Current state of controls
control_state = {
    'fan': False,
    'light': False,
    'water_pump': False
}

# Sensor reading thread
sensor_thread = None
should_run = True

def initialize_hardware():
    """Initialize GPIO and sensor hardware"""
    if SIMULATION_MODE:
        logger.info("Initializing in simulation mode")
        return
    
    # Set GPIO mode
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup output pins
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.setup(LIGHT_PIN, GPIO.OUT)
    GPIO.setup(WATER_PUMP_PIN, GPIO.OUT)
    
    # Initialize outputs to OFF
    GPIO.output(FAN_PIN, GPIO.LOW)
    GPIO.output(LIGHT_PIN, GPIO.LOW)
    GPIO.output(WATER_PUMP_PIN, GPIO.LOW)
    
    # Start sensor reading thread
    start_sensor_thread()
    
    logger.info("Hardware initialized successfully")

def cleanup():
    """Cleanup GPIO pins on shutdown"""
    global should_run
    
    should_run = False
    
    if sensor_thread:
        sensor_thread.join()
    
    if not SIMULATION_MODE:
        GPIO.cleanup()
    
    logger.info("Hardware resources cleaned up")

def control_fan(state):
    """Control the fan state"""
    control_state['fan'] = state
    
    if not SIMULATION_MODE:
        GPIO.output(FAN_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    # Update database with new state
    update_control_state_db()
    
    logger.info(f"Fan set to: {'ON' if state else 'OFF'}")
    return state

def control_light(state):
    """Control the light state"""
    control_state['light'] = state
    
    if not SIMULATION_MODE:
        GPIO.output(LIGHT_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    # Update database with new state
    update_control_state_db()
    
    logger.info(f"Light set to: {'ON' if state else 'OFF'}")
    return state

def control_water_pump(state):
    """Control the water pump state"""
    control_state['water_pump'] = state
    
    if not SIMULATION_MODE:
        GPIO.output(WATER_PUMP_PIN, GPIO.HIGH if state else GPIO.LOW)
    
    # Update database with new state
    update_control_state_db()
    
    logger.info(f"Water pump set to: {'ON' if state else 'OFF'}")
    return state

def read_sensors():
    """Read sensor data and return as dict"""
    if SIMULATION_MODE:
        # Generate simulated sensor data
        temperature = round(random.uniform(18.0, 30.0), 1)
        humidity = round(random.uniform(30.0, 80.0), 1)
        light_level = round(random.uniform(0.0, 1000.0), 1)
        soil_moisture = round(random.uniform(0.0, 100.0), 1)
    else:
        # Read actual sensor data
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)
        
        # Read light sensor (analog would require ADC, here's a placeholder)
        # In real implementation, you would use an ADC like MCP3008
        light_level = random.uniform(0.0, 1000.0)  # Replace with actual reading
        
        # Read soil moisture (analog would require ADC, here's a placeholder)
        soil_moisture = random.uniform(0.0, 100.0)  # Replace with actual reading
    
    # Create sensor reading dict
    sensor_data = {
        'temperature': temperature,
        'humidity': humidity,
        'light_level': light_level,
        'soil_moisture': soil_moisture
    }
    
    logger.debug(f"Sensor reading: {sensor_data}")
    return sensor_data

def update_control_state_db():
    """Update control state in the database"""
    try:
        with db.app.app_context():
            # Get existing state or create new
            state = ControlState.query.first()
            if not state:
                state = ControlState()
                db.session.add(state)
            
            # Update state
            state.fan_state = control_state['fan']
            state.light_state = control_state['light']
            state.water_pump_state = control_state['water_pump']
            
            db.session.commit()
    except Exception as e:
        logger.error(f"Error updating control state in database: {e}")

def save_sensor_reading(sensor_data):
    """Save sensor reading to database"""
    try:
        with db.app.app_context():
            reading = SensorReading(
                temperature=sensor_data['temperature'],
                humidity=sensor_data['humidity'],
                light_level=sensor_data['light_level'],
                soil_moisture=sensor_data['soil_moisture']
            )
            db.session.add(reading)
            db.session.commit()
    except Exception as e:
        logger.error(f"Error saving sensor data to database: {e}")

def sensor_reading_thread():
    """Thread function to periodically read sensors and save to database"""
    global should_run
    
    while should_run:
        try:
            # Read sensors
            sensor_data = read_sensors()
            
            # Save to database
            save_sensor_reading(sensor_data)
            
            # Sleep for sensor reading interval (30 seconds)
            time.sleep(30)
        except Exception as e:
            logger.error(f"Error in sensor reading thread: {e}")
            time.sleep(5)  # Sleep on error to avoid spamming logs

def start_sensor_thread():
    """Start the sensor reading thread"""
    global sensor_thread, should_run
    
    should_run = True
    sensor_thread = threading.Thread(target=sensor_reading_thread)
    sensor_thread.daemon = True
    sensor_thread.start()
    
    logger.info("Sensor reading thread started")

def get_current_sensor_data():
    """Get the most recent sensor data"""
    sensor_data = read_sensors()
    return sensor_data

def get_current_control_state():
    """Get the current control state"""
    return control_state
