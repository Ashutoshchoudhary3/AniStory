


// Main JavaScript for ChronoStories
document.addEventListener('DOMContentLoaded', function() {
    console.log('ChronoStories loaded successfully!');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize notifications
    initializeNotifications();
    
    // Initialize auto-refresh for dashboard
    initializeAutoRefresh();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize scroll animations
function initializeAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up, .slide-in-left, .slide-in-right');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translate(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        if (el.classList.contains('slide-in-left')) {
            el.style.transform = 'translateX(-30px)';
        } else if (el.classList.contains('slide-in-right')) {
            el.style.transform = 'translateX(30px)';
        } else {
            el.style.transform = 'translateY(30px)';
        }
        
        observer.observe(el);
    });
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            } else {
                searchResults.style.display = 'none';
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

// Perform search
function performSearch(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Display search results
function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        searchResults.innerHTML = '<div class="dropdown-item text-muted">No results found</div>';
        searchResults.style.display = 'block';
        return;
    }
    
    const resultsHtml = results.map(result => `
        <a class="dropdown-item" href="${result.url}">
            <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                    <i class="fas fa-${result.type === 'story' ? 'book' : 'chart-line'}"></i>
                </div>
                <div class="flex-grow-1 ms-3">
                    <h6 class="mb-1">${result.title}</h6>
                    <small class="text-muted">${result.description}</small>
                </div>
            </div>
        </a>
    `).join('');
    
    searchResults.innerHTML = resultsHtml;
    searchResults.style.display = 'block';
}

// Initialize theme toggle
function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    if (themeToggle) {
        // Check for saved theme preference or default to light mode
        const currentTheme = localStorage.getItem('theme') || 'light';
        
        if (currentTheme === 'dark') {
            body.classList.add('dark-mode');
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
        
        themeToggle.addEventListener('click', function() {
            if (body.classList.contains('dark-mode')) {
                body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
        });
    }
}

// Initialize notifications
function initializeNotifications() {
    // Check for browser notification support
    if ('Notification' in window) {
        // Request permission if not already granted
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    // Initialize WebSocket connection for real-time updates
    initializeWebSocket();
}

// Initialize WebSocket connection
function initializeWebSocket() {
    if (window.location.protocol === 'https:') {
        var wsProtocol = 'wss:';
    } else {
        var wsProtocol = 'ws:';
    }
    
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/notifications`;
    
    try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {
            console.log('WebSocket connected');
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        ws.onclose = function() {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(initializeWebSocket, 5000);
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    } catch (error) {
        console.error('WebSocket connection failed:', error);
    }
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'new_story':
            showNotification('New Story Available!', data.title, data.url);
            updateDashboard();
            break;
        case 'story_update':
            showNotification('Story Updated', data.message);
            break;
        case 'system_status':
            updateSystemStatus(data.status);
            break;
    }
}

// Show browser notification
function showNotification(title, body, url = null) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: '/static/img/favicon.ico',
            badge: '/static/img/favicon.ico'
        });
        
        if (url) {
            notification.onclick = function() {
                window.open(url, '_blank');
                notification.close();
            };
        }
    }
}

// Update dashboard data
function updateDashboard() {
    // Refresh dashboard metrics
    fetch('/api/dashboard/metrics')
        .then(response => response.json())
        .then(data => {
            updateDashboardMetrics(data);
        })
        .catch(error => {
            console.error('Dashboard update error:', error);
        });
}

// Update dashboard metrics
function updateDashboardMetrics(data) {
    // Update story count
    const storyCountElement = document.getElementById('storyCount');
    if (storyCountElement) {
        animateNumber(storyCountElement, data.story_count);
    }
    
    // Update view count
    const viewCountElement = document.getElementById('viewCount');
    if (viewCountElement) {
        animateNumber(viewCountElement, data.view_count);
    }
    
    // Update recent activity
    const recentActivityElement = document.getElementById('recentActivity');
    if (recentActivityElement && data.recent_activity) {
        updateRecentActivity(recentActivityElement, data.recent_activity);
    }
}

// Animate number changes
function animateNumber(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const increment = (newValue - currentValue) / 20;
    let step = 0;
    
    const timer = setInterval(() => {
        step++;
        const value = Math.round(currentValue + (increment * step));
        element.textContent = value.toLocaleString();
        
        if (step >= 20) {
            element.textContent = newValue.toLocaleString();
            clearInterval(timer);
        }
    }, 50);
}

// Update recent activity
function updateRecentActivity(element, activities) {
    const activityHtml = activities.map(activity => `
        <div class="activity-item fade-in-up">
            <div class="activity-icon">
                <i class="fas fa-${activity.icon}"></i>
            </div>
            <div class="activity-content">
                <h6>${activity.title}</h6>
                <p class="mb-1">${activity.description}</p>
                <small class="text-muted">
                    <i class="fas fa-clock"></i> ${activity.time}
                </small>
            </div>
        </div>
    `).join('');
    
    element.innerHTML = activityHtml;
}

// Update system status
function updateSystemStatus(status) {
    const statusElement = document.getElementById('systemStatus');
    if (statusElement) {
        const statusClass = status === 'healthy' ? 'success' : 
                           status === 'warning' ? 'warning' : 'danger';
        
        statusElement.innerHTML = `
            <div class="alert alert-${statusClass} alert-anime">
                <div class="alert-icon">
                    <i class="fas fa-${status === 'healthy' ? 'check-circle' : 
                                     status === 'warning' ? 'exclamation-triangle' : 'times-circle'}"></i>
                </div>
                <div class="alert-content">
                    <strong>System Status:</strong> ${status.charAt(0).toUpperCase() + status.slice(1)}
                </div>
            </div>
        `;
    }
}

// Initialize auto-refresh for dashboard
function initializeAutoRefresh() {
    const dashboardElement = document.getElementById('dashboardContainer');
    if (dashboardElement) {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            if (!document.hidden) {
                updateDashboard();
            }
        }, 30000);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Loading overlay functions
function showLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner-large"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Error handling
function showError(message, duration = 5000) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-anime position-fixed top-0 end-0 m-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <div class="alert-icon">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="alert-content">
            <strong>Error:</strong> ${message}
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
}

function showSuccess(message, duration = 3000) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-anime position-fixed top-0 end-0 m-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <div class="alert-icon">
            <i class="fas fa-check-circle"></i>
        </div>
        <div class="alert-content">
            <strong>Success:</strong> ${message}
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, duration);
}

// Export functions for use in other scripts
window.ChronoStories = {
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    showNotification,
    updateDashboard,
    debounce,
    throttle
};


