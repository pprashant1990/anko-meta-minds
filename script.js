// Chart instance
let budgetChart = null;

// Initialize chart on page load
window.onload = function() {
    const ctx = document.getElementById('chartCanvas').getContext('2d');

    // Initialize empty chart
    budgetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Income',
                    data: [],
                    backgroundColor: '#FFA726', // Light orange
                    borderColor: '#FB8C00',
                    borderWidth: 1
                },
                {
                    label: 'Expenses',
                    data: [],
                    backgroundColor: '#F57C00', // Dark orange
                    borderColor: '#E65100',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.parsed.y.toLocaleString();
                            return label;
                        }
                    }
                }
            }
        }
    });

    // Attach event listener to Update Chart button
    document.getElementById('updateChartBtn').addEventListener('click', updateChart);

    // Attach event listener to Download Chart button
    document.getElementById('downloadChartBtn').addEventListener('click', downloadChart);

    // Attach event listener for username form submission
    document.getElementById('usernameForm').addEventListener('submit', function(e) {
        e.preventDefault();
        validateUsername();
    });
    document.getElementById('usernameInput').addEventListener('input', clearUsernameValidation);
};

// Function to update chart with current data
function updateChart() {
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'];
    const monthCodes = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];

    const chartLabels = [];
    const incomeData = [];
    const expenseData = [];

    // Collect data from inputs, excluding empty months
    months.forEach((month, index) => {
        const incomeValue = parseFloat(document.getElementById('income-' + monthCodes[index]).value);
        const expenseValue = parseFloat(document.getElementById('expense-' + monthCodes[index]).value);

        // Only include months that have at least one value entered
        if (!isNaN(incomeValue) || !isNaN(expenseValue)) {
            chartLabels.push(month);
            incomeData.push(isNaN(incomeValue) ? 0 : incomeValue);
            expenseData.push(isNaN(expenseValue) ? 0 : expenseValue);
        }
    });

    // Update chart data
    budgetChart.data.labels = chartLabels;
    budgetChart.data.datasets[0].data = incomeData;
    budgetChart.data.datasets[1].data = expenseData;

    // Refresh chart
    budgetChart.update();
}

// Function to download chart as an image
function downloadChart() {
    // Get the canvas element
    const canvas = document.getElementById('chartCanvas');

    // Convert canvas to data URL (PNG format)
    const url = canvas.toDataURL('image/png');

    // Create a temporary link element
    const link = document.createElement('a');
    link.download = 'bucks2bar-budget-chart.png';
    link.href = url;

    // Trigger the download
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
}

// Function to validate username
function validateUsername() {
    const usernameInput = document.getElementById('usernameInput');
    const username = usernameInput.value;
    const errorDiv = document.getElementById('usernameError');
    const successDiv = document.getElementById('usernameSuccess');

    // Clear previous validation states
    usernameInput.classList.remove('is-invalid', 'is-valid');
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    // Validation patterns
    const hasUppercase = /[A-Z]/.test(username);
    const hasNumber = /[0-9]/.test(username);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;'`~]/.test(username);
    const hasMinLength = username.length >= 5;

    // Build error messages
    const errors = [];
    if (!hasMinLength) {
        errors.push('at least 5 characters');
    }
    if (!hasUppercase) {
        errors.push('at least 1 uppercase letter');
    }
    if (!hasNumber) {
        errors.push('at least 1 number');
    }
    if (!hasSpecialChar) {
        errors.push('at least 1 special character');
    }

    // Check if valid
    if (errors.length === 0) {
        usernameInput.classList.add('is-valid');
        successDiv.style.display = 'block';
        console.log('Username validated successfully:', username);
    } else {
        usernameInput.classList.add('is-invalid');
        errorDiv.textContent = 'Username must contain ' + errors.join(', ') + '.';
        errorDiv.style.display = 'block';
    }
}

// Function to clear username validation feedback
function clearUsernameValidation() {
    const usernameInput = document.getElementById('usernameInput');
    const errorDiv = document.getElementById('usernameError');
    const successDiv = document.getElementById('usernameSuccess');

    usernameInput.classList.remove('is-invalid', 'is-valid');
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
}
