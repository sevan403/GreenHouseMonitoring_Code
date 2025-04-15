import os
import json
import logging
import time
import threading
from datetime import datetime

import paho.mqtt.client as mqtt
from paho.mqtt.publish import multiple

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MQTT Configuration
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", None)
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", None)
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "dashboard-pi")

# MQTT Topics
TOPIC_SENSOR_DATA = "opengrow/sensors/data"
TOPIC_CONTROL_COMMAND = "opengrow/control/command"
TOPIC_CONTROL_STATUS = "opengrow/control/status"
TOPIC_SYSTEM_STATUS = "opengrow/system/status"

# Global MQTT client
mqtt_client = None
is_connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    """Called when the client connects to the broker"""
    global is_connected
    if rc == 0:
        logger.info("Connected to MQTT broker")
        is_connected = True
        
        # Subscribe to topics
        client.subscribe(TOPIC_SENSOR_DATA)
        client.subscribe(TOPIC_CONTROL_STATUS)
        client.subscribe(TOPIC_SYSTEM_STATUS)
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")
        is_connected = False

def on_disconnect(client, userdata, rc):
    """Called when the client disconnects from the broker"""
    global is_connected
    logger.warning(f"Disconnected from MQTT broker with code {rc}")
    is_connected = False

def on_message(client, userdata, msg):
    """Called when a message is received from the broker"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        logger.debug(f"Received message on topic {topic}: {payload}")
        
        if topic == TOPIC_SENSOR_DATA:
            # Process sensor data from the sensor Pi
            process_sensor_data(payload)
        elif topic == TOPIC_CONTROL_STATUS:
            # Process control status updates from the sensor Pi
            process_control_status(payload)
        elif topic == TOPIC_SYSTEM_STATUS:
            # Process system status updates
            process_system_status(payload)
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def process_sensor_data(data):
    """Process sensor data received from MQTT"""
    try:
        # Import here to avoid circular imports
        from hardware import save_sensor_reading
        
        # Format data for the database
        sensor_data = {
            'temperature': data.get('temperature', 0.0),
            'humidity': data.get('humidity', 0.0),
            'light_level': data.get('light_level', 0.0),
            'soil_moisture': data.get('soil_moisture', 0.0)
        }
        
        # Save to database
        save_sensor_reading(sensor_data)
        logger.info(f"Saved sensor data from MQTT: {sensor_data}")
    except Exception as e:
        logger.error(f"Error saving sensor data from MQTT: {e}")

def process_control_status(data):
    """Process control status updates received from MQTT"""
    try:
        # Import here to avoid circular imports
        from hardware import control_state, update_control_state_db
        
        # Update control state
        if 'fan' in data:
            control_state['fan'] = data['fan']
        if 'light' in data:
            control_state['light'] = data['light']
        if 'water_pump' in data:
            control_state['water_pump'] = data['water_pump']
        
        # Update database
        update_control_state_db()
        logger.info(f"Updated control state from MQTT: {control_state}")
    except Exception as e:
        logger.error(f"Error updating control state from MQTT: {e}")

def process_system_status(data):
    """Process system status updates"""
    try:
        # Log system status
        logger.info(f"System status update: {data}")
        
        # Could store in database for historical tracking
    except Exception as e:
        logger.error(f"Error processing system status: {e}")

def send_control_command(command, value):
    """Send a control command to the sensor Pi"""
    if not is_connected or mqtt_client is None:
        logger.error("Cannot send control command - not connected to MQTT broker")
        return False
    
    try:
        payload = json.dumps({
            'command': command,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        mqtt_client.publish(TOPIC_CONTROL_COMMAND, payload)
        logger.info(f"Sent control command: {command}={value}")
        return True
    except Exception as e:
        logger.error(f"Error sending control command: {e}")
        return False

def send_fan_command(state):
    """Send a command to control the fan"""
    return send_control_command('fan', state)

def send_light_command(state):
    """Send a command to control the light"""
    return send_control_command('light', state)

def send_water_pump_command(state):
    """Send a command to control the water pump"""
    return send_control_command('water_pump', state)

def connect_mqtt():
    """Connect to the MQTT broker"""
    global mqtt_client, is_connected
    
    try:
        # Create new MQTT client instance
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
            'status': 'offline',
            'timestamp': datetime.now().isoformat()
        })
        mqtt_client.will_set(TOPIC_SYSTEM_STATUS, will_payload, qos=1, retain=True)
        
        # Connect to broker
        mqtt_client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=60)
        
        # Start the client loop in a separate thread
        mqtt_client.loop_start()
        
        # Wait for connection to establish
        timeout = 5  # seconds
        start_time = time.time()
        while not is_connected and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if is_connected:
            # Publish online status
            online_payload = json.dumps({
                'status': 'online',
                'timestamp': datetime.now().isoformat()
            })
            mqtt_client.publish(TOPIC_SYSTEM_STATUS, online_payload, qos=1, retain=True)
            
            logger.info("MQTT client started successfully")
            return True
        else:
            logger.error("MQTT client failed to connect within timeout period")
            mqtt_client.loop_stop()
            return False
    except Exception as e:
        logger.error(f"Error connecting to MQTT broker: {e}")
        if mqtt_client:
            mqtt_client.loop_stop()
        return False

def disconnect_mqtt():
    """Disconnect from the MQTT broker"""
    global mqtt_client, is_connected
    
    if mqtt_client:
        try:
            # Publish offline status
            offline_payload = json.dumps({
                'status': 'offline',
                'timestamp': datetime.now().isoformat()
            })
            mqtt_client.publish(TOPIC_SYSTEM_STATUS, offline_payload, qos=1, retain=True)
            
            # Disconnect and stop loop
            mqtt_client.disconnect()
            mqtt_client.loop_stop()
            is_connected = False
            logger.info("MQTT client stopped")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")

def initialize_mqtt():
    """Initialize the MQTT client"""
    # Connect in a separate thread to avoid blocking
    threading.Thread(target=connect_mqtt, daemon=True).start()