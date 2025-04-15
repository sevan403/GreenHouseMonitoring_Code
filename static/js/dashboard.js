// dashboard.js - Handles the dashboard page functionality

// Update sensor readings periodically
function updateSensorReadings() {
    fetch('/api/sensors/current')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch sensor data');
            }
            return response.json();
        })
        .then(data => {
            // Update temperature display
            const tempElement = document.getElementById('current-temperature');
            if (tempElement && data.temperature) {
                tempElement.textContent = data.temperature.toFixed(1) + '°C';
            }
            
            // Update humidity display
            const humidityElement = document.getElementById('current-humidity');
            if (humidityElement && data.humidity) {
                humidityElement.textContent = data.humidity.toFixed(1) + '%';
            }
            
            // Update light level display
            const lightElement = document.getElementById('current-light');
            if (lightElement && data.light_level) {
                lightElement.textContent = data.light_level.toFixed(1) + ' lux';
            }
            
            // Update soil moisture display
            const soilElement = document.getElementById('current-soil');
            if (soilElement && data.soil_moisture) {
                soilElement.textContent = data.soil_moisture.toFixed(1) + '%';
            }
            
            // Update timestamp
            const timestampElement = document.getElementById('reading-timestamp');
            if (timestampElement && data.timestamp) {
                const date = new Date(data.timestamp);
                timestampElement.textContent = date.toLocaleString();
            }
            
            // Update status indicators
            updateStatusIndicators(data);
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
        });
}

// Update control states periodically
function updateControlStates() {
    fetch('/api/controls/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch control status');
            }
            return response.json();
        })
        .then(data => {
            // Update fan status
            const fanElement = document.getElementById('fan-status');
            if (fanElement) {
                fanElement.textContent = data.fan ? 'ON' : 'OFF';
                fanElement.className = data.fan ? 'badge bg-success' : 'badge bg-danger';
            }
            
            // Update light status
            const lightElement = document.getElementById('light-status');
            if (lightElement) {
                lightElement.textContent = data.light ? 'ON' : 'OFF';
                lightElement.className = data.light ? 'badge bg-success' : 'badge bg-danger';
            }
            
            // Update water pump status
            const pumpElement = document.getElementById('pump-status');
            if (pumpElement) {
                lightElement.textContent = data.water_pump ? 'ON' : 'OFF';
                lightElement.className = data.water_pump ? 'badge bg-success' : 'badge bg-danger';
            }
        })
        .catch(error => {
            console.error('Error fetching control status:', error);
        });
}

// Update status indicators based on sensor readings
function updateStatusIndicators(data) {
    // Fetch settings to get thresholds
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            // Temperature status
            const tempStatus = document.getElementById('temperature-status');
            if (tempStatus && data.temperature) {
                const tempMin = parseFloat(settings.temperature_min);
                const tempMax = parseFloat(settings.temperature_max);
                
                if (data.temperature < tempMin) {
                    tempStatus.textContent = 'TOO LOW';
                    tempStatus.className = 'badge bg-info';
                } else if (data.temperature > tempMax) {
                    tempStatus.textContent = 'TOO HIGH';
                    tempStatus.className = 'badge bg-danger';
                } else {
                    tempStatus.textContent = 'GOOD';
                    tempStatus.className = 'badge bg-success';
                }
            }
            
            // Humidity status
            const humidityStatus = document.getElementById('humidity-status');
            if (humidityStatus && data.humidity) {
                const humidityMin = parseFloat(settings.humidity_min);
                const humidityMax = parseFloat(settings.humidity_max);
                
                if (data.humidity < humidityMin) {
                    humidityStatus.textContent = 'TOO LOW';
                    humidityStatus.className = 'badge bg-warning';
                } else if (data.humidity > humidityMax) {
                    humidityStatus.textContent = 'TOO HIGH';
                    humidityStatus.className = 'badge bg-info';
                } else {
                    humidityStatus.textContent = 'GOOD';
                    humidityStatus.className = 'badge bg-success';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching settings:', error);
        });
}

// Initialize dashboard charts
function initDashboardCharts() {
    // Fetch 24-hour data for charts
    fetch('/api/sensors/hourly?hours=24')
        .then(response => response.json())
        .then(data => {
            createTemperatureChart(data);
            createHumidityChart(data);
            createLightChart(data);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
}

// Create temperature chart
function createTemperatureChart(data) {
    const ctx = document.getElementById('temperature-chart');
    if (!ctx) return;
    
    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const temperatures = data.map(item => item.temperature);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temperatures,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Temperature (last 24 hours)'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

// Create humidity chart
function createHumidityChart(data) {
    const ctx = document.getElementById('humidity-chart');
    if (!ctx) return;
    
    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const humidities = data.map(item => item.humidity);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Humidity (%)',
                data: humidities,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Humidity (last 24 hours)'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Humidity (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

// Create light level chart
function createLightChart(data) {
    const ctx = document.getElementById('light-chart');
    if (!ctx) return;
    
    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const lightLevels = data.map(item => item.light_level);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Light Level (lux)',
                data: lightLevels,
                borderColor: 'rgba(255, 206, 86, 1)',
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Light Level (last 24 hours)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Light Level (lux)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initial updates
    updateSensorReadings();
    updateControlStates();
    initDashboardCharts();
    
    // Set intervals for updates
    setInterval(updateSensorReadings, 30000);  // Update every 30 seconds
    setInterval(updateControlStates, 10000);   // Update every 10 seconds
});
