/**
 * Main Dashboard Application
 * Modular dashboard that coordinates all functionality through separate modules.
 * Safari-compatible version.
 */

// Safari-compatible module loading - load modules sequentially
async function loadModules() {
    console.log('Loading modules for Safari compatibility...');
    
    try {
        // Load modules in dependency order with explicit await
        await import('./modules/notifications.js');
        console.log('✓ notifications loaded');
        
        await import('./modules/modals.js');
        console.log('✓ modals loaded');
        
        await import('./modules/templates.js');
        console.log('✓ templates loaded');
        
        await import('./modules/generation.js');
        console.log('✓ generation loaded');
        
        await import('./modules/queue.js');
        console.log('✓ queue loaded');
        
        await import('./modules/output.js');
        console.log('✓ output loaded');
        
        await import('./modules/settings.js');
        console.log('✓ settings loaded');
        
        await import('./modules/analysis.js');
        console.log('✓ analysis loaded');
        
        await import('./modules/utils.js');
        console.log('✓ utils loaded');
        
        console.log('All modules loaded successfully');
        return true;
    } catch (error) {
        console.error('Failed to load modules:', error);
        return false;
    }
}

class DashboardApp {
    constructor() {
        this.modules = {};
        this.init();
    }

    async init() {
        try {
            console.log('Initializing dashboard...');
            
            // Load modules first
            const modulesLoaded = await loadModules();
            if (!modulesLoaded) {
                throw new Error('Failed to load required modules');
            }
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.handleError(error);
        }
    }

    setup() {
        console.log('Setting up dashboard...');
        this.setupGlobalErrorHandling();
        this.setupEventListeners();
        this.initializeModules();
        this.startPeriodicUpdates();
        this.loadInitialData();
        console.log('Dashboard setup complete');
    }

    setupGlobalErrorHandling() {
        // Global JS error logging
        window.onerror = (message, source, lineno, colno, error) => {
            console.error('Global error:', { message, source, lineno, colno, error });
            this.logError('JavaScript Error', {
                message, source, lineno, colno, 
                stack: error?.stack
            });
        };

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.logError('Unhandled Promise Rejection', {
                message: event.reason?.message || 'Unknown error',
                stack: event.reason?.stack
            });
        });
    }

    async logError(type, errorData) {
        try {
            await fetch('/api/log-js-error', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type,
                    ...errorData,
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    userAgent: navigator.userAgent
                })
            });
        } catch (error) {
            console.error('Failed to log error:', error);
        }

        // Show user notification
        if (window.notificationManager) {
            window.notificationManager.error(`A ${type.toLowerCase()} occurred. Check the console for details.`);
        }
    }

    setupEventListeners() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to generate
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                if (window.generationManager) {
                    const configName = window.generationManager.getCurrentConfigName();
                    if (configName) {
                        window.generationManager.generateSingle(configName);
                    }
                }
            }

            // Ctrl/Cmd + Shift + Enter for batch
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Enter') {
                e.preventDefault();
                if (window.generationManager) {
                    const configName = window.generationManager.getCurrentConfigName();
                    if (configName) {
                        window.generationManager.startBatch(configName);
                    }
                }
            }

            // Ctrl/Cmd + , for settings
            if ((e.ctrlKey || e.metaKey) && e.key === ',') {
                e.preventDefault();
                if (window.modalManager) {
                    window.modalManager.open('settings-modal');
                }
            }
        });

        // Window resize handling
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });
    }

    initializeModules() {
        console.log('Initializing modules...');
        
        // Wait a bit for all modules to load
        setTimeout(() => {
            // Initialize modules in dependency order
            this.modules = {
                notifications: window.notificationManager,
                modals: window.modalManager,
                templates: window.templateManager,
                generation: window.generationManager,
                queue: window.queueManager,
                output: window.outputManager,
                settings: window.settingsManager,
                analysis: window.analysisManager,
                utils: window.utilsManager
            };

            // Verify all modules loaded
            const missingModules = Object.entries(this.modules)
                .filter(([name, module]) => !module)
                .map(([name]) => name);

            if (missingModules.length > 0) {
                console.error('Missing modules:', missingModules);
                this.logError('Module Loading Error', {
                    message: `Failed to load modules: ${missingModules.join(', ')}`
                });
            } else {
                console.log('All modules loaded successfully:', Object.keys(this.modules));
            }
        }, 100);
    }

    startPeriodicUpdates() {
        // Update status indicators every 5 seconds
        setInterval(() => {
            this.updateStatusIndicators();
        }, 5000);

        // Update queue status every 10 seconds
        setInterval(() => {
            if (this.modules.queue) {
                this.modules.queue.refreshQueue();
            }
        }, 10000);

        // Update outputs every 30 seconds
        setInterval(() => {
            if (this.modules.output) {
                this.modules.output.refreshOutputs();
            }
        }, 30000);
    }

    async loadInitialData() {
        try {
            // Load initial status
            await this.updateStatusIndicators();

            // Load initial queue
            if (this.modules.queue) {
                await this.modules.queue.refreshQueue();
            }

            // Load initial outputs
            if (this.modules.output) {
                await this.modules.output.refreshOutputs();
            }

            // Show welcome message if first visit
            if (!localStorage.getItem('dashboard-visited')) {
                this.showWelcomeMessage();
                localStorage.setItem('dashboard-visited', 'true');
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.logError('Initial Data Loading Error', { message: error.message });
        }
    }

    async updateStatusIndicators() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            this.updateApiStatus(data.api_connected);
            this.updateGenerationStatus(data.generation_status);
            this.updateQueueStatus(data.queue_size);
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    updateApiStatus(connected) {
        const statusItem = document.getElementById('api-status');
        const icon = statusItem?.querySelector('.status-icon');
        const text = statusItem?.querySelector('.status-text');
        
        if (statusItem && icon && text) {
            if (connected) {
                icon.className = 'fas fa-circle status-icon connected';
                text.textContent = 'API: Connected';
            } else {
                icon.className = 'fas fa-circle status-icon disconnected';
                text.textContent = 'API: Disconnected';
            }
        }
    }

    updateGenerationStatus(status) {
        const statusItem = document.getElementById('generation-status');
        if (statusItem) {
            statusItem.textContent = `Generation: ${status}`;
            statusItem.className = `status-indicator ${status.toLowerCase()}`;
        }
    }

    updateQueueStatus(queueSize) {
        const statusItem = document.getElementById('queue-status');
        if (statusItem) {
            statusItem.textContent = `Queue: ${queueSize}`;
        }
    }

    handleResize() {
        // Handle responsive layout adjustments
        const isMobile = window.innerWidth < 768;
        const isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
        
        document.body.classList.toggle('mobile', isMobile);
        document.body.classList.toggle('tablet', isTablet);
        document.body.classList.toggle('desktop', !isMobile && !isTablet);
    }

    handlePageHidden() {
        // Pause non-critical updates when page is hidden
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }
    }

    handlePageVisible() {
        // Resume updates when page becomes visible
        this.updateStatusIndicators();
        this.startPeriodicUpdates();
    }

    showWelcomeMessage() {
        if (this.modules.notifications) {
            this.modules.notifications.info(
                'Welcome to Forge API Tool! Use Ctrl+Enter to generate images quickly.',
                8000
            );
        }
    }

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
    }

    handleError(error) {
        console.error('Dashboard error:', error);
        this.logError('Dashboard Error', { message: error.message });
        
        if (this.modules.notifications) {
            this.modules.notifications.error('An error occurred. Please refresh the page.');
        }
    }

    // Public API for external access
    getModule(name) {
        return this.modules[name];
    }

    getAllModules() {
        return { ...this.modules };
    }

    // Utility method to check if dashboard is ready
    isReady() {
        return Object.values(this.modules).every(module => module && module.isReady && module.isReady());
    }
}

// Global functions for HTML button calls
window.checkWildcardEncoding = function() {
    if (window.settingsManager) {
        window.settingsManager.checkWildcardEncoding();
    } else {
        console.error('Settings manager not available');
    }
};

window.fixWildcardEncoding = function() {
    if (window.settingsManager) {
        window.settingsManager.fixWildcardEncoding();
    } else {
        console.error('Settings manager not available');
    }
};

window.fixWildcardEncodingDryRun = function() {
    if (window.settingsManager) {
        window.settingsManager.fixWildcardEncodingDryRun();
    } else {
        console.error('Settings manager not available');
    }
};

window.clearWildcardResults = function() {
    if (window.settingsManager) {
        window.settingsManager.clearWildcardResults();
    } else {
        console.error('Settings manager not available');
    }
};

// Initialize the dashboard
const dashboard = new DashboardApp();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardApp;
} 