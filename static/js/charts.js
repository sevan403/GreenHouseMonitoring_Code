// charts.js - Functions for creating and updating charts for history page

// Create temperature chart with daily and hourly data
function createTemperatureChart(hourlyData, dailyData, container) {
    const ctx = document.getElementById(container);
    if (!ctx) return null;
    
    // Format hourly data
    const hourlyLabels = hourlyData.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const hourlyTemps = hourlyData.map(item => item.temperature);
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyLabels,
            datasets: [{
                label: 'Temperature (°C)',
                data: hourlyTemps,
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
                    text: 'Temperature History'
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
    
    return chart;
}

// Create humidity chart with daily and hourly data
function createHumidityChart(hourlyData, dailyData, container) {
    const ctx = document.getElementById(container);
    if (!ctx) return null;
    
    // Format hourly data
    const hourlyLabels = hourlyData.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const hourlyHumidity = hourlyData.map(item => item.humidity);
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyLabels,
            datasets: [{
                label: 'Humidity (%)',
                data: hourlyHumidity,
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
                    text: 'Humidity History'
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
    
    return chart;
}

// Create light level chart with daily and hourly data
function createLightChart(hourlyData, dailyData, container) {
    const ctx = document.getElementById(container);
    if (!ctx) return null;
    
    // Format hourly data
    const hourlyLabels = hourlyData.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const hourlyLight = hourlyData.map(item => item.light_level);
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyLabels,
            datasets: [{
                label: 'Light Level (lux)',
                data: hourlyLight,
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
                    text: 'Light Level History'
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
    
    return chart;
}

// Create soil moisture chart with daily and hourly data
function createSoilMoistureChart(hourlyData, dailyData, container) {
    const ctx = document.getElementById(container);
    if (!ctx) return null;
    
    // Format hourly data
    const hourlyLabels = hourlyData.map(item => {
        const date = new Date(item.timestamp);
        return date.getHours() + ':00';
    });
    
    const hourlySoil = hourlyData.map(item => item.soil_moisture);
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hourlyLabels,
            datasets: [{
                label: 'Soil Moisture (%)',
                data: hourlySoil,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
                    text: 'Soil Moisture History'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Soil Moisture (%)'
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
    
    return chart;
}

// Create min/max/avg chart for any data type
function createMinMaxChart(dailyData, dataType, container, label, color) {
    const ctx = document.getElementById(container);
    if (!ctx) return null;
    
    // Format data
    const labels = dailyData.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const minValues = dailyData.map(item => item[dataType].min);
    const maxValues = dailyData.map(item => item[dataType].max);
    const avgValues = dailyData.map(item => item[dataType].avg);
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `Min ${label}`,
                    data: minValues,
                    borderColor: color.min,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 3
                },
                {
                    label: `Avg ${label}`,
                    data: avgValues,
                    borderColor: color.avg,
                    backgroundColor: color.avgFill,
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: `Max ${label}`,
                    data: maxValues,
                    borderColor: color.max,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: `Daily ${label} (Min/Avg/Max)`
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: label
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
    
    return chart;
}

// Fetch chart data with specified time range
function fetchChartData(timeRange) {
    // Convert time range to hours for API call
    let hours = 24;
    switch (timeRange) {
        case '12h':
            hours = 12;
            break;
        case '24h':
            hours = 24;
            break;
        case '48h':
            hours = 48;
            break;
        case '7d':
            hours = 168;  // 7 days
            break;
        default:
            hours = 24;
    }
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('chart-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
    
    // Fetch hourly data
    fetch(`/api/sensors/hourly?hours=${hours}`)
        .then(response => response.json())
        .then(hourlyData => {
            // Fetch daily data for min/max charts
            fetch('/api/sensors/daily?days=7')
                .then(response => response.json())
                .then(dailyData => {
                    // Initialize charts
                    initializeCharts(hourlyData, dailyData);
                    
                    // Hide loading indicator
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching daily data:', error);
                    if (loadingIndicator) {
                        loadingIndicator.style.display = 'none';
                    }
                });
        })
        .catch(error => {
            console.error('Error fetching hourly data:', error);
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        });
}

// Initialize all charts with fetched data
function initializeCharts(hourlyData, dailyData) {
    // Clear existing charts if needed
    if (window.growBoxCharts) {
        window.growBoxCharts.forEach(chart => chart.destroy());
    }
    
    // Create a collection for charts
    window.growBoxCharts = [];
    
    // Create temperature chart
    const tempChart = createTemperatureChart(hourlyData, dailyData, 'temperature-chart');
    if (tempChart) window.growBoxCharts.push(tempChart);
    
    // Create humidity chart
    const humidityChart = createHumidityChart(hourlyData, dailyData, 'humidity-chart');
    if (humidityChart) window.growBoxCharts.push(humidityChart);
    
    // Create light chart
    const lightChart = createLightChart(hourlyData, dailyData, 'light-chart');
    if (lightChart) window.growBoxCharts.push(lightChart);
    
    // Create soil moisture chart
    const soilChart = createSoilMoistureChart(hourlyData, dailyData, 'soil-moisture-chart');
    if (soilChart) window.growBoxCharts.push(soilChart);
    
    // Create min/max charts if containers exist
    const tempMinMaxChart = createMinMaxChart(
        dailyData, 
        'temperature', 
        'temperature-minmax-chart',
        'Temperature (°C)',
        {
            min: 'rgba(255, 99, 132, 0.7)',
            avg: 'rgba(255, 99, 132, 1)',
            max: 'rgba(255, 99, 132, 0.7)',
            avgFill: 'rgba(255, 99, 132, 0.2)'
        }
    );
    if (tempMinMaxChart) window.growBoxCharts.push(tempMinMaxChart);
    
    const humidityMinMaxChart = createMinMaxChart(
        dailyData,
        'humidity',
        'humidity-minmax-chart',
        'Humidity (%)',
        {
            min: 'rgba(54, 162, 235, 0.7)',
            avg: 'rgba(54, 162, 235, 1)',
            max: 'rgba(54, 162, 235, 0.7)',
            avgFill: 'rgba(54, 162, 235, 0.2)'
        }
    );
    if (humidityMinMaxChart) window.growBoxCharts.push(humidityMinMaxChart);
}

// Initialize history page
document.addEventListener('DOMContentLoaded', function() {
    // Get initial time range (default is 24h)
    const timeRangeSelect = document.getElementById('time-range-select');
    let selectedRange = '24h';
    if (timeRangeSelect) {
        selectedRange = timeRangeSelect.value;
    }
    
    // Fetch initial data and create charts
    fetchChartData(selectedRange);
    
    // Set up event listener for time range changes
    if (timeRangeSelect) {
        timeRangeSelect.addEventListener('change', function() {
            fetchChartData(this.value);
        });
    }
    
    // Set up export data button if it exists
    const exportBtn = document.getElementById('export-data-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            // Get currently selected time range
            const timeRange = document.getElementById('time-range-select').value;
            let hours = 24;
            switch (timeRange) {
                case '12h': hours = 12; break;
                case '24h': hours = 24; break;
                case '48h': hours = 48; break;
                case '7d': hours = 168; break;
            }
            
            // Fetch data for export
            fetch(`/api/sensors/history?hours=${hours}`)
                .then(response => response.json())
                .then(data => {
                    // Convert to CSV
                    const csv = convertToCSV(data);
                    
                    // Create download link
                    const blob = new Blob([csv], { type: 'text/csv' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    
                    // Generate filename with current date
                    const date = new Date();
                    const filename = `grow_box_data_${date.toISOString().split('T')[0]}.csv`;
                    
                    a.href = url;
                    a.download = filename;
                    a.click();
                    
                    // Clean up
                    URL.revokeObjectURL(url);
                })
                .catch(error => {
                    console.error('Error exporting data:', error);
                    alert('Failed to export data. Please try again.');
                });
        });
    }
});

// Helper function to convert data to CSV format
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    // Get headers from first object
    const headers = Object.keys(data[0]).join(',');
    
    // Create rows
    const rows = data.map(item => {
        return Object.values(item).map(value => {
            // Handle strings with commas by quoting
            if (typeof value === 'string' && value.includes(',')) {
                return `"${value}"`;
            }
            return value;
        }).join(',');
    });
    
    // Combine headers and rows
    return [headers, ...rows].join('\n');
}
