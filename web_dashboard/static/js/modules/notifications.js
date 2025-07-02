/**
 * Notifications Module
 * Handles all user notifications, error messages, and status updates with proper styling and auto-dismiss.
 */

class NotificationManager {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.setupStyles();
    }

    createContainer() {
        // Create notification container if it doesn't exist
        this.container = document.getElementById('notification-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        }
    }

    setupStyles() {
        // Add CSS styles if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                }
                
                .notification {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    padding: 16px;
                    margin-bottom: 10px;
                    border-left: 4px solid #007bff;
                    animation: notificationSlideIn 0.3s ease-out;
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                }
                
                .notification.success {
                    border-left-color: #28a745;
                }
                
                .notification.error {
                    border-left-color: #dc3545;
                }
                
                .notification.warning {
                    border-left-color: #ffc107;
                }
                
                .notification.info {
                    border-left-color: #17a2b8;
                }
                
                .notification-icon {
                    flex-shrink: 0;
                    font-size: 18px;
                }
                
                .notification.success .notification-icon {
                    color: #28a745;
                }
                
                .notification.error .notification-icon {
                    color: #dc3545;
                }
                
                .notification.warning .notification-icon {
                    color: #ffc107;
                }
                
                .notification.info .notification-icon {
                    color: #17a2b8;
                }
                
                .notification-content {
                    flex: 1;
                }
                
                .notification-message {
                    margin: 0;
                    font-size: 14px;
                    line-height: 1.4;
                    color: #333;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    font-size: 16px;
                    padding: 0;
                    margin-left: 8px;
                    flex-shrink: 0;
                }
                
                .notification-close:hover {
                    color: #666;
                }
                
                @keyframes notificationSlideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes notificationSlideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);
        
        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(notification);
            }, duration);
        }
        
        return notification;
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = this.getIconForType(type);
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-message">${this.escapeHtml(message)}</p>
            </div>
            <button class="notification-close" onclick="notificationManager.dismiss(this.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return notification;
    }

    getIconForType(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    dismiss(notification) {
        if (!notification) return;
        
        notification.style.animation = 'notificationSlideOut 0.3s ease-in';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    dismissAll() {
        const notifications = this.container.querySelectorAll('.notification');
        notifications.forEach(notification => this.dismiss(notification));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Convenience methods
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 8000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 4000) {
        return this.show(message, 'info', duration);
    }

    // For backward compatibility
    updateNotification(message, type = 'info') {
        return this.show(message, type);
    }
}

// Export for use in other modules
window.notificationManager = new NotificationManager();
export default window.notificationManager; 