from datetime import datetime
from app import db

class SensorReading(db.Model):
    """Model for storing sensor readings"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    light_level = db.Column(db.Float, nullable=False)
    soil_moisture = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f"<SensorReading {self.timestamp}: Temp={self.temperature}°C, Humidity={self.humidity}%>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'light_level': self.light_level,
            'soil_moisture': self.soil_moisture
        }

class ControlState(db.Model):
    """Model for storing current state of control devices"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fan_state = db.Column(db.Boolean, default=False)
    light_state = db.Column(db.Boolean, default=False)
    water_pump_state = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<ControlState: Fan={self.fan_state}, Light={self.light_state}, Pump={self.water_pump_state}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'fan_state': self.fan_state,
            'light_state': self.light_state,
            'water_pump_state': self.water_pump_state
        }

class Settings(db.Model):
    """Model for storing system settings and thresholds"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f"<Setting {self.name}: {self.value}>"
