import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from models import SensorReading
from app import db

# Setup logging
logger = logging.getLogger(__name__)

def get_latest_reading():
    """Get the latest sensor reading from the database"""
    try:
        reading = SensorReading.query.order_by(SensorReading.timestamp.desc()).first()
        return reading.to_dict() if reading else None
    except Exception as e:
        logger.error(f"Error retrieving latest sensor reading: {e}")
        return None

def get_readings_time_range(hours=24):
    """Get sensor readings for the specified time range"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        readings = SensorReading.query.filter(
            SensorReading.timestamp.between(start_time, end_time)
        ).order_by(SensorReading.timestamp.asc()).all()
        
        return [reading.to_dict() for reading in readings]
    except Exception as e:
        logger.error(f"Error retrieving sensor readings for time range: {e}")
        return []

def get_hourly_average(hours=24):
    """Get hourly averages for the specified time range"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # SQLite doesn't support complex date functions directly, so we'll use a simpler approach
        readings = SensorReading.query.filter(
            SensorReading.timestamp.between(start_time, end_time)
        ).all()
        
        # Group readings by hour
        hourly_data = {}
        for reading in readings:
            hour_key = reading.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    'temperature': [],
                    'humidity': [],
                    'light_level': [],
                    'soil_moisture': []
                }
            
            hourly_data[hour_key]['temperature'].append(reading.temperature)
            hourly_data[hour_key]['humidity'].append(reading.humidity)
            hourly_data[hour_key]['light_level'].append(reading.light_level)
            if reading.soil_moisture is not None:
                hourly_data[hour_key]['soil_moisture'].append(reading.soil_moisture)
        
        # Calculate averages
        result = []
        for hour, data in sorted(hourly_data.items()):
            result.append({
                'timestamp': hour.isoformat(),
                'temperature': sum(data['temperature']) / len(data['temperature']) if data['temperature'] else None,
                'humidity': sum(data['humidity']) / len(data['humidity']) if data['humidity'] else None,
                'light_level': sum(data['light_level']) / len(data['light_level']) if data['light_level'] else None,
                'soil_moisture': sum(data['soil_moisture']) / len(data['soil_moisture']) if data['soil_moisture'] else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error calculating hourly averages: {e}")
        return []

def get_daily_min_max(days=7):
    """Get daily minimum and maximum values for the specified time range"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Retrieve all readings within the time range
        readings = SensorReading.query.filter(
            SensorReading.timestamp.between(start_time, end_time)
        ).all()
        
        # Group readings by day
        daily_data = {}
        for reading in readings:
            day_key = reading.timestamp.date()
            
            if day_key not in daily_data:
                daily_data[day_key] = {
                    'temperature': [],
                    'humidity': [],
                    'light_level': [],
                    'soil_moisture': []
                }
            
            daily_data[day_key]['temperature'].append(reading.temperature)
            daily_data[day_key]['humidity'].append(reading.humidity)
            daily_data[day_key]['light_level'].append(reading.light_level)
            if reading.soil_moisture is not None:
                daily_data[day_key]['soil_moisture'].append(reading.soil_moisture)
        
        # Calculate min/max/avg for each day
        result = []
        for day, data in sorted(daily_data.items()):
            result.append({
                'date': day.isoformat(),
                'temperature': {
                    'min': min(data['temperature']) if data['temperature'] else None,
                    'max': max(data['temperature']) if data['temperature'] else None,
                    'avg': sum(data['temperature']) / len(data['temperature']) if data['temperature'] else None
                },
                'humidity': {
                    'min': min(data['humidity']) if data['humidity'] else None,
                    'max': max(data['humidity']) if data['humidity'] else None,
                    'avg': sum(data['humidity']) / len(data['humidity']) if data['humidity'] else None
                },
                'light_level': {
                    'min': min(data['light_level']) if data['light_level'] else None,
                    'max': max(data['light_level']) if data['light_level'] else None,
                    'avg': sum(data['light_level']) / len(data['light_level']) if data['light_level'] else None
                },
                'soil_moisture': {
                    'min': min(data['soil_moisture']) if data['soil_moisture'] else None,
                    'max': max(data['soil_moisture']) if data['soil_moisture'] else None,
                    'avg': sum(data['soil_moisture']) / len(data['soil_moisture']) if data['soil_moisture'] else None
                }
            })
        
        return result
    except Exception as e:
        logger.error(f"Error calculating daily min/max values: {e}")
        return []
