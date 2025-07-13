// Initialize all charts on the page
document.addEventListener('DOMContentLoaded', function() {
    // Find all chart containers
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        const chartId = container.id;
        const chartType = container.dataset.chartType || 'line';
        const chartData = JSON.parse(container.dataset.chartData);
        
        initializeChart(chartId, chartType, chartData);
    });
});

// Chart initialization function
function initializeChart(chartId, chartType, chartData) {
    const ctx = document.getElementById(chartId).getContext('2d');
    
    // Common chart options
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false,
            },
            legend: {
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    
    // Create the chart
    new Chart(ctx, {
        type: chartType,
        data: chartData,
        options: options
    });
}

// Update chart data dynamically
function updateChart(chartId, newData) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        chart.data = newData;
        chart.update();
    }
}