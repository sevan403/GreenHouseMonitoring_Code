import logging
from flask import Blueprint, jsonify, request
from app import app
from hardware import (
    control_fan, control_light, control_water_pump, 
    get_current_sensor_data, get_current_control_state
)
from sensor_data import (
    get_latest_reading, get_readings_time_range, 
    get_hourly_average, get_daily_min_max
)
from data_storage import (
    get_all_settings, get_setting, update_setting, 
    export_settings, import_settings
)

# Setup logging
logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

def register_api_routes(app):
    """Register API routes with the Flask app"""
    
    # Sensor data endpoints
    @api_bp.route('/sensors/current', methods=['GET'])
    def get_current_sensors():
        """Get current sensor readings"""
        latest = get_latest_reading()
        if not latest:
            return jsonify({'error': 'No sensor data available'}), 404
        return jsonify(latest)
    
    @api_bp.route('/sensors/history', methods=['GET'])
    def get_sensor_history():
        """Get historical sensor data"""
        hours = request.args.get('hours', '24')
        try:
            hours = int(hours)
            if hours < 1 or hours > 168:  # Max one week
                hours = 24
        except ValueError:
            hours = 24
        
        readings = get_readings_time_range(hours)
        return jsonify(readings)
    
    @api_bp.route('/sensors/hourly', methods=['GET'])
    def get_hourly_data():
        """Get hourly averaged sensor data"""
        hours = request.args.get('hours', '24')
        try:
            hours = int(hours)
            if hours < 1 or hours > 168:  # Max one week
                hours = 24
        except ValueError:
            hours = 24
        
        data = get_hourly_average(hours)
        return jsonify(data)
    
    @api_bp.route('/sensors/daily', methods=['GET'])
    def get_daily_data():
        """Get daily min/max sensor data"""
        days = request.args.get('days', '7')
        try:
            days = int(days)
            if days < 1 or days > 30:  # Max one month
                days = 7
        except ValueError:
            days = 7
        
        data = get_daily_min_max(days)
        return jsonify(data)
    
    # Control endpoints
    @api_bp.route('/controls/status', methods=['GET'])
    def get_control_status():
        """Get current status of all controls"""
        control_state = get_current_control_state()
        return jsonify(control_state)
    
    @api_bp.route('/controls/fan', methods=['POST'])
    def set_fan():
        """Control fan state"""
        data = request.get_json()
        if 'state' not in data:
            return jsonify({'error': 'Missing state parameter'}), 400
        
        state = data['state']
        if state not in [True, False, 'true', 'false']:
            return jsonify({'error': 'State must be true or false'}), 400
        
        # Convert string to boolean if needed
        if isinstance(state, str):
            state = state.lower() == 'true'
        
        result = control_fan(state)
        return jsonify({'success': True, 'fan_state': result})
    
    @api_bp.route('/controls/light', methods=['POST'])
    def set_light():
        """Control light state"""
        data = request.get_json()
        if 'state' not in data:
            return jsonify({'error': 'Missing state parameter'}), 400
        
        state = data['state']
        if state not in [True, False, 'true', 'false']:
            return jsonify({'error': 'State must be true or false'}), 400
        
        # Convert string to boolean if needed
        if isinstance(state, str):
            state = state.lower() == 'true'
        
        result = control_light(state)
        return jsonify({'success': True, 'light_state': result})
    
    @api_bp.route('/controls/water', methods=['POST'])
    def set_water_pump():
        """Control water pump state"""
        data = request.get_json()
        if 'state' not in data:
            return jsonify({'error': 'Missing state parameter'}), 400
        
        state = data['state']
        if state not in [True, False, 'true', 'false']:
            return jsonify({'error': 'State must be true or false'}), 400
        
        # Convert string to boolean if needed
        if isinstance(state, str):
            state = state.lower() == 'true'
        
        result = control_water_pump(state)
        return jsonify({'success': True, 'water_pump_state': result})
    
    # Settings endpoints
    @api_bp.route('/settings', methods=['GET'])
    def get_settings():
        """Get all settings"""
        settings = get_all_settings()
        return jsonify(settings)
    
    @api_bp.route('/settings/<name>', methods=['GET'])
    def get_setting_value(name):
        """Get specific setting by name"""
        value = get_setting(name)
        if value is None:
            return jsonify({'error': f'Setting not found: {name}'}), 404
        return jsonify({name: value})
    
    @api_bp.route('/settings/<name>', methods=['POST'])
    def update_setting_value(name):
        """Update specific setting by name"""
        data = request.get_json()
        if 'value' not in data:
            return jsonify({'error': 'Missing value parameter'}), 400
        
        result = update_setting(name, data['value'])
        if result:
            return jsonify({'success': True, name: data['value']})
        else:
            return jsonify({'error': f'Failed to update setting: {name}'}), 500
    
    @api_bp.route('/settings/export', methods=['GET'])
    def export_all_settings():
        """Export all settings as JSON"""
        settings_json = export_settings()
        return jsonify(settings_json)
    
    @api_bp.route('/settings/import', methods=['POST'])
    def import_all_settings():
        """Import settings from JSON"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No settings data provided'}), 400
        
        result = import_settings(data)
        if result:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to import settings'}), 500
    
    # Register the blueprint with the app
    app.register_blueprint(api_bp)
    
    logger.info("API routes registered successfully")
