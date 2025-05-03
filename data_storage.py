import os
import json
import logging
from datetime import datetime
from models import Settings
from app import db

# Setup logging
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    'temperature_min': '18.0',
    'temperature_max': '30.0',
    'humidity_min': '40.0',
    'humidity_max': '80.0',
    'light_hours_start': '6',  # 6 AM
    'light_hours_end': '18',   # 6 PM
    'water_schedule': 'off',   # off, daily, custom
    'water_time': '8',         # 8 AM
    'water_duration': '30',    # seconds
    'fan_auto': 'true',        # true/false
    'light_auto': 'true',      # true/false
    'water_auto': 'true'       # true/false
}

def initialize_settings():
    """Initialize settings with default values if they don't exist"""
    try:
        for key, value in DEFAULT_SETTINGS.items():
            setting = Settings.query.filter_by(name=key).first()
            if not setting:
                setting = Settings(name=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        logger.info("Settings initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing settings: {e}")

def get_all_settings():
    """Get all settings as a dictionary"""
    try:
        settings = {}

        all_settings = Settings.query.all()
        for setting in all_settings:
            settings[setting.name] = setting.value
        
        return settings
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        return DEFAULT_SETTINGS

def get_setting(name, default=None):
    """Get a specific setting by name"""
    try:
        setting = Settings.query.filter_by(name=name).first()
        if setting:
            return setting.value
        return default
    except Exception as e:
        logger.error(f"Error retrieving setting '{name}': {e}")
        return default

def update_setting(name, value):
    """Update a setting value"""
    try:
        setting = Settings.query.filter_by(name=name).first()
        if setting:
            setting.value = value
        else:
            setting = Settings(name=name, value=value)
            db.session.add(setting)
        
        db.session.commit()
        logger.info(f"Setting '{name}' updated to '{value}'")
        return True
    except Exception as e:
        logger.error(f"Error updating setting '{name}': {e}")
        return False

def export_settings():
    """Export all settings to a JSON string"""
    settings = get_all_settings()
    return json.dumps(settings, indent=2)

def import_settings(settings_json):
    """Import settings from a JSON string"""
    try:

        settings = json.loads(settings_json)
        for name, value in settings.items():
            update_setting(name, value)
        return True
    except Exception as e:
        logger.error(f"Error importing settings: {e}")
        return False

def should_fan_be_on():
    """Determine if fan should be on based on settings and current conditions"""
    from hardware import get_current_sensor_data
    
    # If auto control is disabled, don't change state
    if get_setting('fan_auto', 'true') != 'true':
        return None
    
    # Get current sensor data
    sensor_data = get_current_sensor_data()
    if not sensor_data:
        return None
    
    # Get temperature thresholds
    temp_max = float(get_setting('temperature_max', '30.0'))
    
    # Turn on fan if temperature is too high
    if sensor_data['temperature'] > temp_max:
        return True
    
    # If temperature is more than 2 degrees below max, turn off fan
    if sensor_data['temperature'] < (temp_max - 2.0):
        return False
    
    # Otherwise maintain current state
    return None

def should_light_be_on():
    """Determine if light should be on based on settings and time of day"""
    # If auto control is disabled, don't change state
    if get_setting('light_auto', 'true') != 'true':
        return None
    
    # Get light hours settings
    light_start = int(get_setting('light_hours_start', '6'))
    light_end = int(get_setting('light_hours_end', '18'))
    
    # Get current hour
    current_hour = datetime.now().hour
    
    # Check if current hour is within light hours
    if light_start <= current_hour < light_end:
        return True
    else:
        return False

def should_water_pump_be_on():
    """Determine if water pump should be on based on settings and schedule"""
    # If auto control is disabled, don't change state
    if get_setting('water_auto', 'true') != 'true':
        return None
    
    # Get watering schedule
    schedule = get_setting('water_schedule', 'off')
    
    # If schedule is off, pump should be off
    if schedule == 'off':
        return False
    
    # Get current time
    now = datetime.now()
    water_time = int(get_setting('water_time', '8'))
    water_duration = int(get_setting('water_duration', '30'))
    
    # If schedule is daily, check if it's watering time
    if schedule == 'daily':
        # Check if it's water_time hour and within the first water_duration seconds of the hour
        if now.hour == water_time and now.minute == 0 and now.second < water_duration:
            return True
        else:
            return False
    
    # For custom schedule, we would need more logic here
    # ...
    
    return False
