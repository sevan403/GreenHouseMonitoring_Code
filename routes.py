import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from hardware import control_fan, control_light, control_water_pump, get_current_control_state
from sensor_data import get_latest_reading, get_readings_time_range, get_hourly_average, get_daily_min_max
from data_storage import get_all_settings, update_setting, export_settings, import_settings
from models import ControlState

# Setup logging
logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        # Get latest sensor data
        sensor_data = get_latest_reading()
        
        # Get current control states
        control_state = ControlState.query.first()
        if not control_state:
            control_state = {
                'fan_state': False,
                'light_state': False,
                'water_pump_state': False
            }
        else:
            control_state = control_state.to_dict()
        
        # Get settings
        settings = get_all_settings()
        
        return render_template('dashboard.html', 
                              sensor_data=sensor_data, 
                              control_state=control_state,
                              settings=settings)
    
    @app.route('/dashboard')
    def dashboard():
        """Alias for main dashboard page"""
        return redirect(url_for('index'))
    
    @app.route('/controls')
    def controls():
        """Controls page for manual control of hardware"""
        # Get current control states
        control_state = ControlState.query.first()
        if not control_state:
            control_state = {
                'fan_state': False,
                'light_state': False,
                'water_pump_state': False
            }
        else:
            control_state = control_state.to_dict()
        
        # Get latest sensor data
        sensor_data = get_latest_reading()
        
        # Get settings
        settings = get_all_settings()
        
        return render_template('controls.html', 
                              control_state=control_state,
                              sensor_data=sensor_data,
                              settings=settings)
    
    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        """Settings page for configuring the system"""
        if request.method == 'POST':
            # Update settings from form
            for key in request.form:
                update_setting(key, request.form[key])
            
            flash('Settings updated successfully', 'success')
            return redirect(url_for('settings'))
        
        # Get current settings
        current_settings = get_all_settings()
        
        return render_template('settings.html', settings=current_settings)
    
        @app.route('/history')
    def history():
        """History page for viewing historical sensor data"""
        latest = get_latest_reading()

        # Parse selected time range
        time_range = request.args.get('range', '24h')  # Default: 24 hours
        range_map = {
            '12h': 12,
            '24h': 24,
            '48h': 48,
            '7d': 168  # 7 days * 24 hours
        }
        hours = range_map.get(time_range, 24)  # fallback to 24h if invalid

        # Get data
        hourly_data = get_hourly_average(hours)
        daily_data = get_daily_min_max(7)

        return render_template('history.html',
                               latest=latest,
                               hourly_data=hourly_data,
                               daily_data=daily_data,
                               selected_range=time_range)

    
    @app.errorhandler(404)
    def page_not_found(e):
        """Custom 404 page"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Custom 500 page"""
        logger.error(f"Internal server error: {e}")
        return render_template('500.html'), 500
    
    logger.info("Routes registered successfully")
