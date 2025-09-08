

// YouTube Layout JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeYouTubeLayout();
    initializeThemeToggle();
    initializeUserMenu();
    initializeSidebarToggle();
    initializeSearch();
});

function initializeYouTubeLayout() {
    // Initialize any layout-specific functionality
    console.log('YouTube layout initialized');
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        // Send theme preference to server if user is logged in
        if (window.currentUser) {
            fetch('/api/preferences/theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme: newTheme })
            }).catch(console.error);
        }
    });
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    const icon = themeToggle.querySelector('i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function initializeUserMenu() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (!userMenuBtn || !userDropdown) return;
    
    userMenuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        userDropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        userDropdown.classList.remove('show');
    });
    
    // Prevent dropdown from closing when clicking inside it
    userDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });
}

function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarToggleMobile = document.getElementById('sidebarToggleMobile');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
    
    if (sidebarToggleMobile) {
        sidebarToggleMobile.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Load saved sidebar state
    const savedCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (savedCollapsed) {
        sidebar.classList.add('collapsed');
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(e.target) && 
            !sidebarToggleMobile.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    });
}

function initializeSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (!searchForm || !searchInput) return;
    
    // Add search suggestions functionality
    searchInput.addEventListener('input', debounce(function(e) {
        const query = e.target.value.trim();
        if (query.length > 2) {
            fetchSearchSuggestions(query);
        } else {
            hideSearchSuggestions();
        }
    }, 300));
    
    // Handle search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            window.location.href = `/stories/search?q=${encodeURIComponent(query)}`;
        }
    });
}

function fetchSearchSuggestions(query) {
    // This would be implemented with an API endpoint
    // For now, we'll just show some mock suggestions
    const suggestions = [
        'Technology',
        'Science',
        'Entertainment',
        'Sports',
        'Politics'
    ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
    
    showSearchSuggestions(suggestions);
}

function showSearchSuggestions(suggestions) {
    // Remove existing suggestions
    hideSearchSuggestions();
    
    if (suggestions.length === 0) return;
    
    const searchForm = document.querySelector('.search-form');
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'search-suggestions';
    suggestionsDiv.innerHTML = suggestions.map(suggestion => 
        `<div class="suggestion-item" onclick="selectSearchSuggestion('${suggestion}')">
            <i class="fas fa-search"></i>
            <span>${suggestion}</span>
        </div>`
    ).join('');
    
    searchForm.appendChild(suggestionsDiv);
}

function hideSearchSuggestions() {
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
}

function selectSearchSuggestion(suggestion) {
    const searchInput = document.querySelector('.search-input');
    searchInput.value = suggestion;
    hideSearchSuggestions();
    searchInput.closest('form').submit();
}

// Utility function for debouncing
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

// Story card interactions
function initializeStoryCards() {
    const storyCards = document.querySelectorAll('.story-card');
    
    storyCards.forEach(card => {
        card.addEventListener('click', function() {
            const storyId = this.dataset.storyId;
            if (storyId) {
                window.location.href = `/stories/${storyId}`;
            }
        });
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Infinite scroll functionality
function initializeInfiniteScroll() {
    let isLoading = false;
    let hasMore = true;
    let currentPage = 1;
    
    window.addEventListener('scroll', debounce(function() {
        if (isLoading || !hasMore) return;
        
        const scrollPosition = window.innerHeight + window.scrollY;
        const threshold = document.body.offsetHeight - 1000;
        
        if (scrollPosition >= threshold) {
            loadMoreStories();
        }
    }, 200));
    
    function loadMoreStories() {
        isLoading = true;
        currentPage++;
        
        // Show loading indicator
        showLoadingIndicator();
        
        fetch(`/api/stories?page=${currentPage}`)
            .then(response => response.json())
            .then(data => {
                if (data.stories && data.stories.length > 0) {
                    appendStories(data.stories);
                } else {
                    hasMore = false;
                }
            })
            .catch(error => {
                console.error('Error loading more stories:', error);
                hasMore = false;
            })
            .finally(() => {
                isLoading = false;
                hideLoadingIndicator();
            });
    }
}

function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = '<div class="spinner"></div>';
    document.querySelector('.stories-grid').appendChild(loadingDiv);
}

function hideLoadingIndicator() {
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function appendStories(stories) {
    const grid = document.querySelector('.stories-grid');
    if (!grid) return;
    
    stories.forEach(story => {
        const storyCard = createStoryCard(story);
        grid.appendChild(storyCard);
    });
    
    // Re-initialize story card interactions
    initializeStoryCards();
}

function createStoryCard(story) {
    const card = document.createElement('div');
    card.className = 'story-card';
    card.dataset.storyId = story.id;
    
    card.innerHTML = `
        <img src="${story.image_url || '/static/img/placeholder.jpg'}" alt="${story.title}" class="story-card-image">
        <div class="story-card-content">
            <h3 class="story-card-title">${story.title}</h3>
            <div class="story-card-meta">
                <span class="story-card-category">${story.category || 'General'}</span>
                <span class="story-card-views">
                    <i class="fas fa-eye"></i>
                    ${formatNumber(story.views || 0)}
                </span>
            </div>
        </div>
    `;
    
    return card;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Analytics tracking
function trackStoryView(storyId) {
    fetch(`/api/analytics/track`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId,
            metric_type: 'view',
            metric_value: 1
        })
    }).catch(console.error);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Press '/' to focus search
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Press 'Escape' to close dropdowns and sidebars
    if (e.key === 'Escape') {
        document.querySelectorAll('.user-dropdown, .search-suggestions').forEach(el => {
            el.classList.remove('show');
        });
        document.getElementById('sidebar').classList.remove('show');
    }
});

// Export functions for use in other scripts
window.YouTubeLayout = {
    initializeStoryCards,
    initializeInfiniteScroll,
    trackStoryView,
    formatNumber
};

