# OpenGrow-Box Plant Monitoring System

A Python Flask-based plant growth monitoring and control system designed to run on Raspberry Pi devices. This system replaces the original React-based OpenGrow-Box project with a more maintainable tech stack using Flask for the backend and JavaScript/HTML/CSS for the frontend.

## System Overview

The OpenGrow-Box system consists of two Raspberry Pi devices:

1. **Dashboard Pi** - Hosts the web interface, database, and MQTT broker
2. **Sensor Pi** - Collects sensor data and controls hardware (fans, lights, water pump)

The two devices communicate using MQTT, allowing for a clean separation between the user interface and the hardware control.

## Hardware Requirements

### Dashboard Pi
- Raspberry Pi 4 or 5 running Raspberry Pi OS Lite
- Network connection (Wi-Fi or Ethernet)

### Sensor Pi
- Raspberry Pi (any model) running Raspberry Pi OS Lite
- DHT22 Temperature/Humidity Sensor (connected to GPIO4)
- BH1750 Light Intensity Sensor (connected to I2C - SDA/SCL)
- Capacitive Soil Moisture Sensor (connected to GPIO17)
- Relay module for controlling:
  - Fan (connected to GPIO18)
  - Grow Light (connected to GPIO23)
  - Water Pump (connected to GPIO24)

## Software Setup

### Dashboard Pi Setup

1. Install required software:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-flask mosquitto mosquitto-clients
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/opengrow-box.git
   cd opengrow-box
   ```

3. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Configure Mosquitto MQTT broker:
   ```bash
   sudo nano /etc/mosquitto/mosquitto.conf
   ```
   Add these lines:
   ```
   listener 1883
   allow_anonymous true
   ```

5. Start the MQTT broker:
   ```bash
   sudo systemctl start mosquitto
   sudo systemctl enable mosquitto
   ```

6. Run the application:
   ```bash
   python3 main.py
   ```

7. For production use, set up the application as a service with systemd.

### Sensor Pi Setup

1. Install required software:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-dev i2c-tools
   ```

2. Enable I2C interface:
   ```bash
   sudo raspi-config
   # Go to Interface Options > I2C > Enable
   ```

3. Install Python dependencies:
   ```bash
   pip3 install paho-mqtt Adafruit_DHT smbus2 RPi.GPIO
   ```

4. Copy the `sensor_client.py` file to the Sensor Pi.

5. Configure MQTT connection in `sensor_client.py` (set the MQTT_BROKER to Dashboard Pi's IP).

6. Run the sensor client:
   ```bash
   python3 sensor_client.py
   ```

7. For production use, set up the sensor client as a service with systemd.

## System Configuration

### Network Configuration
- Dashboard Pi IP: 192.168.1.100 (recommended static IP)
- Sensor Pi IP: 192.168.1.101 (recommended static IP)

### Environment Variables
- `MQTT_BROKER`: IP address of the MQTT broker (default: "localhost")
- `MQTT_PORT`: Port for MQTT broker (default: 1883)
- `MQTT_USERNAME`: Username for MQTT authentication (optional)
- `MQTT_PASSWORD`: Password for MQTT authentication (optional)
- `DATABASE_URL`: URL for database connection (default: SQLite database)

## Features

- Real-time temperature, humidity, light, and soil moisture monitoring
- Automated control of fan, lights, and water pump based on sensor readings
- Historical data logging and graphing
- Manual control options for all actuators
- Settings management for thresholds and schedules
- Mobile-friendly responsive web interface

## System Architecture

```
[Dashboard Pi] <--- MQTT ---> [Sensor Pi]
    |                             |
    |                             |
[Web Interface]            [Physical Sensors]
[Database]                 [Actuator Control]
```

## Development

### Environment Setup

For local development without Raspberry Pi hardware:

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run the application with `python main.py`

The system will run in simulation mode, generating random sensor data.

## License

This project is open source and available under the MIT License.