// Dashboard JavaScript for Criminal Data Visualization

// Global variables to store chart instances
let charts = {};

// Color schemes for charts
const colors = {
    primary: ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22'],
    secondary: ['#ecf0f1', '#bdc3c7', '#95a5a6', '#7f8c8d'],
    gradient: {
        red: 'rgba(231, 76, 60, 0.8)',
        blue: 'rgba(52, 152, 219, 0.8)',
        green: 'rgba(46, 204, 113, 0.8)',
        orange: 'rgba(243, 156, 18, 0.8)',
        purple: 'rgba(155, 89, 182, 0.8)'
    }
};

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// Load data and initialize charts
async function loadDashboardData() {
    try {
        showLoading();

        // Load data from JSON file
        const response = await fetch('dashboard_data.json');
        if (!response.ok) {
            throw new Error('Failed to load data');
        }

        const data = await response.json();

        // Update statistics
        updateStatistics(data.stats);

        // Create charts
        createCrimeTypesChart(data.crime_types);
        createMonthlyTrendsChart(data.monthly_trends);
        createNeighborhoodsChart(data.neighborhoods);
        createCategoryChart(data.categories);
        createCrimeDetails(data.crime_details);

        hideLoading();

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Erro ao carregar os dados. Verifique se o arquivo dashboard_data.json existe.');
        hideLoading();
    }
}

// Update statistics cards
function updateStatistics(stats) {
    document.getElementById('totalCrimes').textContent = stats.total_crimes.toLocaleString('pt-BR');
    document.getElementById('crimeTypes').textContent = stats.crime_types;
    document.getElementById('neighborhoods').textContent = stats.neighborhoods.toLocaleString('pt-BR');
}

// Create crime types horizontal bar chart
function createCrimeTypesChart(data) {
    const ctx = document.getElementById('crimeTypesChart').getContext('2d');

    charts.crimeTypes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels.slice(0, 10), // Top 10
            datasets: [{
                label: 'Número de Ocorrências',
                data: data.data.slice(0, 10),
                backgroundColor: colors.primary,
                borderColor: colors.primary.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.x.toLocaleString('pt-BR')} ocorrências`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('pt-BR');
                        }
                    }
                },
                y: {
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

// Create monthly trends line chart
function createMonthlyTrendsChart(data) {
    const ctx = document.getElementById('monthlyTrendsChart').getContext('2d');

    charts.monthlyTrends = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Ocorrências por Mês',
                data: data.data,
                borderColor: colors.gradient.blue,
                backgroundColor: colors.gradient.blue.replace('0.8', '0.2'),
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: colors.gradient.blue,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y.toLocaleString('pt-BR')} ocorrências`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('pt-BR');
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45
                    }
                }
            }
        }
    });
}

// Create neighborhoods chart
function createNeighborhoodsChart(data) {
    const ctx = document.getElementById('neighborhoodsChart').getContext('2d');

    charts.neighborhoods = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: colors.primary,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed.toLocaleString('pt-BR')} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create category pie chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');

    charts.categories = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    colors.gradient.red,
                    colors.gradient.blue,
                    colors.gradient.green,
                    colors.gradient.orange
                ],
                borderColor: '#fff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed.toLocaleString('pt-BR')} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create crime details section
function createCrimeDetails(details) {
    const container = document.getElementById('crimeDetails');
    container.innerHTML = '';

    details.slice(0, 12).forEach(crime => {
        const crimeItem = document.createElement('div');
        crimeItem.className = 'crime-item';

        crimeItem.innerHTML = `
            <h4>${crime.name}</h4>
            <p>
                <span class="crime-count">${crime.count.toLocaleString('pt-BR')}</span> ocorrências
                <br>
                <small>${crime.percentage}% do total</small>
            </p>
        `;

        container.appendChild(crimeItem);
    });
}

// Utility functions
function showLoading() {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(el => {
        if (el.id !== 'datePeriod') {
            el.innerHTML = '<div class="loading"></div>';
        }
    });
}

function hideLoading() {
    // Loading will be hidden when stats are updated
}

function showError(message) {
    const container = document.querySelector('.container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
}

// Responsive chart resize
window.addEventListener('resize', function() {
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.resize();
        }
    });
});

// Export functions for potential future use
window.dashboardUtils = {
    refreshData: loadDashboardData,
    getCharts: () => charts,
    updateChart: (chartName, newData) => {
        if (charts[chartName]) {
            charts[chartName].data = newData;
            charts[chartName].update();
        }
    }
};
