// controls.js - Handles the manual controls page functionality

// Update control states
function updateControlStates() {
    fetch('/api/controls/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch control status');
            }
            return response.json();
        })
        .then(data => {
            // Update fan switch
            const fanSwitch = document.getElementById('fan-switch');
            if (fanSwitch) {
                fanSwitch.checked = data.fan;
            }
            
            // Update light switch
            const lightSwitch = document.getElementById('light-switch');
            if (lightSwitch) {
                lightSwitch.checked = data.light;
            }
            
            // Update water pump switch
            const pumpSwitch = document.getElementById('pump-switch');
            if (pumpSwitch) {
                pumpSwitch.checked = data.water_pump;
            }
            
            // Update status badges
            updateStatusBadges(data);
        })
        .catch(error => {
            console.error('Error fetching control status:', error);
        });
}

// Update status badges for controls
function updateStatusBadges(data) {
    // Fan status
    const fanStatus = document.getElementById('fan-status');
    if (fanStatus) {
        fanStatus.textContent = data.fan ? 'ON' : 'OFF';
        fanStatus.className = data.fan ? 'badge bg-success' : 'badge bg-secondary';
    }
    
    // Light status
    const lightStatus = document.getElementById('light-status');
    if (lightStatus) {
        lightStatus.textContent = data.light ? 'ON' : 'OFF';
        lightStatus.className = data.light ? 'badge bg-success' : 'badge bg-secondary';
    }
    
    // Water pump status
    const pumpStatus = document.getElementById('pump-status');
    if (pumpStatus) {
        pumpStatus.textContent = data.water_pump ? 'ON' : 'OFF';
        pumpStatus.className = data.water_pump ? 'badge bg-success' : 'badge bg-secondary';
    }
}

// Update auto control settings
function updateAutoSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            // Fan auto control
            const fanAuto = document.getElementById('fan-auto');
            if (fanAuto) {
                fanAuto.checked = settings.fan_auto === 'true';
            }
            
            // Light auto control
            const lightAuto = document.getElementById('light-auto');
            if (lightAuto) {
                lightAuto.checked = settings.light_auto === 'true';
            }
            
            // Water pump auto control
            const waterAuto = document.getElementById('water-auto');
            if (waterAuto) {
                waterAuto.checked = settings.water_auto === 'true';
            }
        })
        .catch(error => {
            console.error('Error fetching auto settings:', error);
        });
}

// Toggle fan state
function toggleFan(state) {
    fetch('/api/controls/fan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: state }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to control fan');
        }
        return response.json();
    })
    .then(data => {
        // Update UI after successful operation
        const fanStatus = document.getElementById('fan-status');
        if (fanStatus) {
            fanStatus.textContent = data.fan_state ? 'ON' : 'OFF';
            fanStatus.className = data.fan_state ? 'badge bg-success' : 'badge bg-secondary';
        }
    })
    .catch(error => {
        console.error('Error controlling fan:', error);
        // Reset switch state on error
        const fanSwitch = document.getElementById('fan-switch');
        if (fanSwitch) {
            fanSwitch.checked = !state;
        }
        
        // Show error message
        alert('Failed to control fan. Please try again.');
    });
}

// Toggle light state
function toggleLight(state) {
    fetch('/api/controls/light', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: state }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to control light');
        }
        return response.json();
    })
    .then(data => {
        // Update UI after successful operation
        const lightStatus = document.getElementById('light-status');
        if (lightStatus) {
            lightStatus.textContent = data.light_state ? 'ON' : 'OFF';
            lightStatus.className = data.light_state ? 'badge bg-success' : 'badge bg-secondary';
        }
    })
    .catch(error => {
        console.error('Error controlling light:', error);
        // Reset switch state on error
        const lightSwitch = document.getElementById('light-switch');
        if (lightSwitch) {
            lightSwitch.checked = !state;
        }
        
        // Show error message
        alert('Failed to control light. Please try again.');
    });
}

// Toggle water pump state
function toggleWaterPump(state) {
    fetch('/api/controls/water', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: state }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to control water pump');
        }
        return response.json();
    })
    .then(data => {
        // Update UI after successful operation
        const pumpStatus = document.getElementById('pump-status');
        if (pumpStatus) {
            pumpStatus.textContent = data.water_pump_state ? 'ON' : 'OFF';
            pumpStatus.className = data.water_pump_state ? 'badge bg-success' : 'badge bg-secondary';
        }
    })
    .catch(error => {
        console.error('Error controlling water pump:', error);
        // Reset switch state on error
        const pumpSwitch = document.getElementById('pump-switch');
        if (pumpSwitch) {
            pumpSwitch.checked = !state;
        }
        
        // Show error message
        alert('Failed to control water pump. Please try again.');
    });
}

// Toggle auto control settings
function toggleAutoControl(device, state) {
    const settingName = `${device}_auto`;
    
    fetch(`/api/settings/${settingName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ value: state ? 'true' : 'false' }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to update ${device} auto control setting`);
        }
        return response.json();
    })
    .then(data => {
        // Success notification
        const autoStatusEl = document.getElementById(`${device}-auto-status`);
        if (autoStatusEl) {
            autoStatusEl.textContent = state ? 'AUTO' : 'MANUAL';
            autoStatusEl.className = state ? 'badge bg-info' : 'badge bg-warning';
        }
    })
    .catch(error => {
        console.error(`Error updating ${device} auto control:`, error);
        // Reset switch state on error
        const autoSwitch = document.getElementById(`${device}-auto`);
        if (autoSwitch) {
            autoSwitch.checked = !state;
        }
        
        // Show error message
        alert(`Failed to update ${device} auto control. Please try again.`);
    });
}

// Initialize the controls page
document.addEventListener('DOMContentLoaded', function() {
    // Initial update of control states
    updateControlStates();
    updateAutoSettings();
    
    // Setup event listeners for fan control
    const fanSwitch = document.getElementById('fan-switch');
    if (fanSwitch) {
        fanSwitch.addEventListener('change', function() {
            toggleFan(this.checked);
        });
    }
    
    // Setup event listeners for light control
    const lightSwitch = document.getElementById('light-switch');
    if (lightSwitch) {
        lightSwitch.addEventListener('change', function() {
            toggleLight(this.checked);
        });
    }
    
    // Setup event listeners for water pump control
    const pumpSwitch = document.getElementById('pump-switch');
    if (pumpSwitch) {
        pumpSwitch.addEventListener('change', function() {
            toggleWaterPump(this.checked);
        });
    }
    
    // Setup event listeners for auto control toggles
    const fanAuto = document.getElementById('fan-auto');
    if (fanAuto) {
        fanAuto.addEventListener('change', function() {
            toggleAutoControl('fan', this.checked);
        });
    }
    
    const lightAuto = document.getElementById('light-auto');
    if (lightAuto) {
        lightAuto.addEventListener('change', function() {
            toggleAutoControl('light', this.checked);
        });
    }
    
    const waterAuto = document.getElementById('water-auto');
    if (waterAuto) {
        waterAuto.addEventListener('change', function() {
            toggleAutoControl('water', this.checked);
        });
    }
    
    // Set interval for periodic updates
    setInterval(updateControlStates, 5000);  // Update every 5 seconds
});
