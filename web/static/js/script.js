// Main JavaScript for MoneyPrinterV2 Web UI

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize copy buttons
    initCopyButtons();
    
    // Initialize platform selection
    initPlatformSelection();
    
    // Initialize monetization type selection
    initMonetizationSelection();
    
    // Initialize charts if they exist
    initCharts();
});

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'tooltip';
            tooltipElement.textContent = tooltipText;
            
            document.body.appendChild(tooltipElement);
            
            const rect = this.getBoundingClientRect();
            tooltipElement.style.top = rect.top - tooltipElement.offsetHeight - 10 + 'px';
            tooltipElement.style.left = rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2) + 'px';
            
            tooltipElement.classList.add('show');
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltipElement = document.querySelector('.tooltip');
            if (tooltipElement) {
                tooltipElement.remove();
            }
        });
    });
}

// Initialize copy buttons
function initCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const textToCopy = targetElement.innerText;
            
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    // Show success feedback
                    this.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                    alert('Failed to copy text. Please try again.');
                });
        });
    });
}

// Initialize platform selection
function initPlatformSelection() {
    const platformSelect = document.getElementById('platform');
    
    if (platformSelect) {
        const youtubeOptions = document.querySelector('.youtube-options');
        const twitterOptions = document.querySelector('.twitter-options');
        const threadsOptions = document.querySelector('.threads-options');
        
        // Set initial state
        if (youtubeOptions && twitterOptions && threadsOptions) {
            youtubeOptions.style.display = 'block';
            twitterOptions.style.display = 'none';
            threadsOptions.style.display = 'none';
        }
        
        // Platform selection change handler
        platformSelect.addEventListener('change', function() {
            // Hide all platform options
            if (youtubeOptions) youtubeOptions.style.display = 'none';
            if (twitterOptions) twitterOptions.style.display = 'none';
            if (threadsOptions) threadsOptions.style.display = 'none';
            
            // Show selected platform options
            if (this.value === 'youtube' && youtubeOptions) {
                youtubeOptions.style.display = 'block';
            } else if (this.value === 'twitter' && twitterOptions) {
                twitterOptions.style.display = 'block';
            } else if (this.value === 'threads' && threadsOptions) {
                threadsOptions.style.display = 'block';
            }
        });
    }
}

// Initialize monetization type selection
function initMonetizationSelection() {
    const monetizationSelect = document.getElementById('monetization_type');
    
    if (monetizationSelect) {
        monetizationSelect.addEventListener('change', function() {
            // You can add specific behavior based on monetization type selection
            console.log('Monetization type selected:', this.value);
        });
    }
}

// Initialize charts
function initCharts() {
    // Check if Chart.js is available
    if (typeof Chart !== 'undefined') {
        // Revenue chart
        const revenueChartElement = document.getElementById('revenue-chart');
        if (revenueChartElement) {
            const revenueChart = new Chart(revenueChartElement, {
                type: 'bar',
                data: {
                    labels: ['Affiliate', 'Sponsorship', 'Digital Products', 'Subscription'],
                    datasets: [{
                        label: 'Estimated Revenue ($)',
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            'rgba(255, 153, 0, 0.7)',
                            'rgba(100, 65, 164, 0.7)',
                            'rgba(40, 167, 69, 0.7)',
                            'rgba(23, 162, 184, 0.7)'
                        ],
                        borderColor: [
                            'rgb(255, 153, 0)',
                            'rgb(100, 65, 164)',
                            'rgb(40, 167, 69)',
                            'rgb(23, 162, 184)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Content distribution chart
        const contentChartElement = document.getElementById('content-chart');
        if (contentChartElement) {
            const contentChart = new Chart(contentChartElement, {
                type: 'doughnut',
                data: {
                    labels: ['YouTube', 'X (Twitter)', 'Threads'],
                    datasets: [{
                        label: 'Content Distribution',
                        data: [0, 0, 0],
                        backgroundColor: [
                            'rgba(255, 0, 0, 0.7)',
                            'rgba(29, 161, 242, 0.7)',
                            'rgba(0, 0, 0, 0.7)'
                        ],
                        borderColor: [
                            'rgb(255, 0, 0)',
                            'rgb(29, 161, 242)',
                            'rgb(0, 0, 0)'
                        ],
                        borderWidth: 1
                    }]
                }
            });
        }
    }
}

// Generate random topic
function generateTopic() {
    fetch('/generate_topic', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.topic) {
            // Create a modal to display the topic
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>Generated Topic Idea</h3>
                    <p>${data.topic}</p>
                    <div class="modal-actions">
                        <a href="/generate?topic=${encodeURIComponent(data.topic)}" class="btn btn-primary">Use This Topic</a>
                        <button class="btn btn-secondary modal-close">Close</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Show the modal
            modal.style.display = 'flex';
            
            // Close button functionality
            const closeBtn = modal.querySelector('.close');
            const closeModalBtn = modal.querySelector('.modal-close');
            
            closeBtn.addEventListener('click', function() {
                modal.style.display = 'none';
                document.body.removeChild(modal);
            });
            
            closeModalBtn.addEventListener('click', function() {
                modal.style.display = 'none';
                document.body.removeChild(modal);
            });
            
            // Close when clicking outside the modal
            window.addEventListener('click', function(event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                    document.body.removeChild(modal);
                }
            });
        } else if (data.error) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to generate topic. Please try again.');
    });
}

// Initialize system
function initializeSystem() {
    fetch('/initialize', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Check initialization status
function checkInitStatus() {
    fetch('/status')
    .then(response => response.json())
    .then(data => {
        if (data.initialized || data.error) {
            location.reload();
        } else if (data.initializing) {
            setTimeout(checkInitStatus, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        setTimeout(checkInitStatus, 5000);
    });
}

// Toggle automation settings
function toggleAutomation(element) {
    const isChecked = element.checked;
    const automationType = element.getAttribute('data-automation');
    
    console.log(`${automationType} automation ${isChecked ? 'enabled' : 'disabled'}`);
    
    // In a real implementation, this would send a request to the server
    // to update the automation settings
}

// Update dashboard stats
function updateDashboardStats() {
    fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        // Update stats on the dashboard
        const revenueElement = document.getElementById('total-revenue');
        const contentElement = document.getElementById('content-count');
        const productsElement = document.getElementById('product-count');
        
        if (revenueElement) revenueElement.textContent = `$${data.revenue.total}`;
        if (contentElement) contentElement.textContent = data.content.total;
        if (productsElement) productsElement.textContent = data.products.total;
        
        // Update charts if they exist
        updateCharts(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Update charts with new data
function updateCharts(data) {
    if (typeof Chart !== 'undefined') {
        const revenueChart = Chart.getChart('revenue-chart');
        const contentChart = Chart.getChart('content-chart');
        
        if (revenueChart) {
            revenueChart.data.datasets[0].data = [
                data.revenue.affiliate,
                data.revenue.sponsorship,
                data.revenue.digital_products,
                data.revenue.subscription
            ];
            revenueChart.update();
        }
        
        if (contentChart) {
            contentChart.data.datasets[0].data = [
                data.content.youtube,
                data.content.twitter,
                data.content.threads
            ];
            contentChart.update();
        }
    }
}
