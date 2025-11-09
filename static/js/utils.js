/**
 * Utility functions for the Scratch Automation App
 */

// API helper functions
class APIClient {
  constructor() {
    this.baseURL = '';
  }

  getAuthHeaders() {
    const token = localStorage.getItem('scratch_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('scratch_token');
        localStorage.removeItem('scratch_user');
        window.location.href = '/';
        return;
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  async upload(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData
    });
  }
}

// Global API client instance
const api = new APIClient();

// Notification system
class NotificationManager {
  constructor() {
    this.container = this.createContainer();
  }

  createContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    `;
    document.body.appendChild(container);
    return container;
  }

  show(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
      padding: 1rem;
      border-radius: 0.5rem;
      font-weight: bold;
      max-width: 300px;
      word-wrap: break-word;
      animation: slideInRight 0.3s ease;
      cursor: pointer;
      border: 1px solid transparent;
      box-shadow: var(--shadow-lg);
    `;

    // Check if dark mode is active
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
                   (document.documentElement.getAttribute('data-theme') !== 'light' &&
                    window.matchMedia('(prefers-color-scheme: dark)').matches);

    const lightColors = {
      success: { bg: '#28a745', text: 'white' },
      error: { bg: '#dc3545', text: 'white' },
      warning: { bg: '#ffc107', text: 'white' },
      info: { bg: '#007bff', text: 'white' }
    };

    const darkColors = {
      success: { bg: 'rgba(16, 185, 129, 0.2)', text: '#34d399', border: '#059669' },
      error: { bg: 'rgba(239, 68, 68, 0.2)', text: '#f87171', border: '#dc2626' },
      warning: { bg: 'rgba(245, 158, 11, 0.2)', text: '#fbbf24', border: '#d97706' },
      info: { bg: 'rgba(59, 130, 246, 0.2)', text: '#60a5fa', border: '#2563eb' }
    };

    const colors = isDark ? darkColors : lightColors;
    const colorSet = colors[type] || colors.info;

    notification.style.background = colorSet.bg;
    notification.style.color = colorSet.text;
    if (colorSet.border) {
      notification.style.borderColor = colorSet.border;
    }

    notification.textContent = message;

    // Add close functionality
    notification.onclick = () => this.remove(notification);

    this.container.appendChild(notification);

    // Auto remove
    if (duration > 0) {
      setTimeout(() => this.remove(notification), duration);
    }

    return notification;
  }

  remove(notification) {
    if (notification && notification.parentNode) {
      notification.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }
  }

  success(message, duration) {
    return this.show(message, 'success', duration);
  }

  error(message, duration) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration) {
    return this.show(message, 'info', duration);
  }
}

// Global notification manager
const notifications = new NotificationManager();

// Loading overlay
class LoadingManager {
  constructor() {
    this.overlay = null;
    this.count = 0;
  }

  show(message = 'Loading...') {
    this.count++;
    
    if (!this.overlay) {
      this.overlay = document.createElement('div');
      this.overlay.className = 'loading-overlay';
      this.overlay.innerHTML = `
        <div style="text-align: center;">
          <div class="spinner"></div>
          <div style="margin-top: 1rem; font-weight: bold;">${message}</div>
        </div>
      `;
      document.body.appendChild(this.overlay);
    }
  }

  hide() {
    this.count = Math.max(0, this.count - 1);
    
    if (this.count === 0 && this.overlay) {
      this.overlay.remove();
      this.overlay = null;
    }
  }
}

// Global loading manager
const loading = new LoadingManager();

// Theme Management
class ThemeManager {
  constructor() {
    this.init();
  }

  // Get current theme (always dark)
  getCurrentTheme() {
    return 'dark';
  }

  // Set theme (always dark)
  setTheme(theme) {
    // Force dark mode only
    localStorage.setItem('theme', 'dark');
    this.applyTheme('dark');
    this.updateThemeToggle();
  }

  // Apply theme to document (always dark)
  applyTheme(theme) {
    const html = document.documentElement;
    // Always set dark theme
    html.setAttribute('data-theme', 'dark');
  }

  // Toggle between themes (disabled - always dark)
  toggleTheme() {
    // Do nothing - dark mode only
    return;
  }

  // Update theme toggle button (hide it since we only have dark mode)
  updateThemeToggle() {
    const toggleBtn = document.querySelector('.theme-toggle');
    if (!toggleBtn) return;

    // Hide the theme toggle since we only support dark mode
    toggleBtn.style.display = 'none';
  }

  // Create theme toggle button (disabled - dark mode only)
  createThemeToggle() {
    // Don't create theme toggle since we only support dark mode
    return;
  }

  // Initialize theme system (dark mode only)
  init() {
    // Always apply dark theme
    this.applyTheme('dark');
    localStorage.setItem('theme', 'dark');

    // Hide any existing theme toggles
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.updateThemeToggle();
      });
    } else {
      this.updateThemeToggle();
    }
  }
}

// Global theme manager
const themeManager = new ThemeManager();

// Utility functions
const utils = {
  // Format date for display
  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
  },

  // Format date for input fields
  formatDateForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  },

  // Truncate text by characters (legacy)
  truncate(text, length = 50) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  },

  // Truncate text by words
  truncateWords(text, wordCount = 30) {
    if (!text) return '';
    const words = text.trim().split(/\s+/);
    if (words.length <= wordCount) return text;
    return words.slice(0, wordCount).join(' ') + '...';
  },

  // Debounce function
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Copy to clipboard
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      notifications.success('Copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      notifications.error('Failed to copy to clipboard');
    }
  },

  // Download file
  downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  },

  // Validate email
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Get status icon
  getStatusIcon(status) {
    const icons = {
      pending: '⏳',
      in_progress: '🔄',
      completed: '✅',
      failed: '❌'
    };
    return icons[status] || '❓';
  },

  // Get status color
  getStatusColor(status) {
    const colors = {
      pending: '#ffc107',
      in_progress: '#007bff',
      completed: '#28a745',
      failed: '#dc3545'
    };
    return colors[status] || '#6c757d';
  }
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes slideOutRight {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(100%);
    }
  }
`;
document.head.appendChild(style);

// Export for use in other scripts
window.api = api;
window.notifications = notifications;
window.loading = loading;
window.utils = utils;
window.themeManager = themeManager;
