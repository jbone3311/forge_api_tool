/**
 * Utilities Module
 * Common helper functions and utilities
 */

class UtilsManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupGlobalUtils();
        console.log('Utils Manager initialized');
    }

    setupGlobalUtils() {
        window.utils = {
            debounce: this.debounce.bind(this),
            formatFileSize: this.formatFileSize.bind(this),
            formatDate: this.formatDate.bind(this),
            generateId: this.generateId.bind(this),
            copyToClipboard: this.copyToClipboard.bind(this),
            showLoading: this.showLoading.bind(this),
            hideLoading: this.hideLoading.bind(this)
        };
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString() + ' ' + new Date(date).toLocaleTimeString();
    }

    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            return false;
        }
    }

    showLoading(element, message = 'Loading...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.add('loading');
            element.innerHTML = `<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> ${message}</div>`;
        }
    }

    hideLoading(element) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.classList.remove('loading');
        }
    }
}

window.utilsManager = new UtilsManager();
export default window.utilsManager; 