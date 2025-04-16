
import os
import logging
from flask import Flask
from models import db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///growbox.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Import and register routes after app initialization to avoid circular imports
with app.app_context():
    from routes import register_routes
    from api import register_api_routes
    
    # Register route blueprints
    register_routes(app)
    register_api_routes(app)
    
    # Create tables
    db.create_all()
    
    # Initialize hardware (if available)
    try:
        from hardware import initialize_hardware
        initialize_hardware()
        logger.info("Hardware initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize hardware: {e}")
        logger.warning("Running in simulation mode - hardware controls will be simulated")
    
    # Initialize MQTT client for communication with Sensor Pi
    try:
        from mqtt_client import initialize_mqtt
        initialize_mqtt()
        logger.info("MQTT client initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize MQTT client: {e}")
        logger.warning("Running without MQTT - using local sensors only")

logger.info("Application initialized successfully")
