/**
 * Settings Management Module
 * Handles application settings, preferences, and configuration
 */

class SettingsManager {
    constructor() {
        this.settings = {};
        this.defaultSettings = {
            // Generation settings
            default_batch_size: 1,
            default_steps: 20,
            default_cfg_scale: 7.0,
            default_sampler: 'DPM++ 2M Karras',
            default_width: 512,
            default_height: 512,
            
            // Output settings
            auto_open_outputs: true,
            max_outputs_display: 50,
            output_naming_pattern: '{config}_{timestamp}_{seed}',
            
            // Queue settings
            max_concurrent_jobs: 2,
            job_timeout: 30,
            
            // UI settings
            auto_refresh_interval: 5,
            theme: 'light',
            sidebar_width: 300,
            
            // Logging settings
            log_retention_days: 30,
            auto_cleanup_logs: true,
            
            // Security settings
            enable_cors: true,
            max_upload_size: 10
        };
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.applySettings();
        console.log('Settings Manager initialized');
    }

    setupEventListeners() {
        // Listen for settings changes
        document.addEventListener('settingsChanged', (e) => {
            this.updateSetting(e.detail.key, e.detail.value);
        });

        // Listen for settings modal events
        document.addEventListener('settingsModalOpened', () => {
            this.populateSettingsForm();
        });

        document.addEventListener('settingsModalSaved', () => {
            this.saveSettingsFromForm();
        });
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();

            if (data.success) {
                this.settings = { ...this.defaultSettings, ...data.data };
            } else {
                console.warn('Failed to load settings, using defaults:', data.error);
                this.settings = { ...this.defaultSettings };
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.settings = { ...this.defaultSettings };
        }
    }

    async saveSettings() {
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.settings)
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Settings saved successfully');
                this.applySettings();
            } else {
                this.showError(data.error || 'Failed to save settings');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showError('Failed to save settings: ' + error.message);
        }
    }

    updateSetting(key, value) {
        this.settings[key] = value;
        this.applySetting(key, value);
    }

    applySettings() {
        Object.entries(this.settings).forEach(([key, value]) => {
            this.applySetting(key, value);
        });
    }

    applySetting(key, value) {
        switch (key) {
            case 'theme':
                this.applyTheme(value);
                break;
            case 'sidebar_width':
                this.applySidebarWidth(value);
                break;
            case 'auto_refresh_interval':
                this.applyRefreshInterval(value);
                break;
            case 'max_concurrent_jobs':
                this.applyConcurrentJobs(value);
                break;
            default:
                // Apply to form fields if they exist
                this.updateFormField(key, value);
        }
    }

    applyTheme(theme) {
        document.body.className = document.body.className.replace(/theme-\w+/, '');
        document.body.classList.add(`theme-${theme}`);
        localStorage.setItem('dashboard-theme', theme);
    }

    applySidebarWidth(width) {
        const sidebar = document.querySelector('.templates-sidebar');
        if (sidebar) {
            sidebar.style.width = `${width}px`;
        }
    }

    applyRefreshInterval(interval) {
        // Update refresh intervals in other modules
        if (window.queueManager) {
            window.queueManager.startAutoRefresh(interval * 1000);
        }
        if (window.outputManager) {
            window.outputManager.startAutoRefresh(interval * 2000);
        }
    }

    applyConcurrentJobs(maxJobs) {
        // This would be applied to the backend queue manager
        // For now, just log the change
        console.log(`Max concurrent jobs set to: ${maxJobs}`);
    }

    updateFormField(key, value) {
        const field = document.getElementById(key);
        if (field) {
            if (field.type === 'checkbox') {
                field.checked = value === true || value === 'true';
            } else {
                field.value = value;
            }
        }
    }

    populateSettingsForm() {
        Object.entries(this.settings).forEach(([key, value]) => {
            this.updateFormField(key, value);
        });
    }

    saveSettingsFromForm() {
        const formData = new FormData(document.getElementById('settings-form'));
        
        Object.keys(this.settings).forEach(key => {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'checkbox') {
                    this.settings[key] = field.checked;
                } else if (field.type === 'number') {
                    this.settings[key] = parseFloat(field.value) || 0;
                } else {
                    this.settings[key] = field.value;
                }
            }
        });

        this.saveSettings();
    }

    getSetting(key, defaultValue = null) {
        return this.settings[key] !== undefined ? this.settings[key] : defaultValue;
    }

    setSetting(key, value) {
        this.settings[key] = value;
        this.applySetting(key, value);
    }

    resetToDefaults() {
        this.settings = { ...this.defaultSettings };
        this.applySettings();
        this.populateSettingsForm();
        this.showSuccess('Settings reset to defaults');
    }

    async exportSettings() {
        try {
            const dataStr = JSON.stringify(this.settings, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = window.URL.createObjectURL(dataBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard-settings-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            this.showSuccess('Settings exported successfully');
        } catch (error) {
            console.error('Error exporting settings:', error);
            this.showError('Failed to export settings: ' + error.message);
        }
    }

    async importSettings(file) {
        try {
            const text = await file.text();
            const importedSettings = JSON.parse(text);
            
            // Validate imported settings
            const validSettings = {};
            Object.keys(this.defaultSettings).forEach(key => {
                if (importedSettings[key] !== undefined) {
                    validSettings[key] = importedSettings[key];
                }
            });

            this.settings = { ...this.defaultSettings, ...validSettings };
            this.applySettings();
            this.populateSettingsForm();
            this.showSuccess('Settings imported successfully');
        } catch (error) {
            console.error('Error importing settings:', error);
            this.showError('Failed to import settings: ' + error.message);
        }
    }

    async clearCache() {
        try {
            const response = await fetch('/api/settings/clear-cache', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Cache cleared successfully');
            } else {
                this.showError(data.error || 'Failed to clear cache');
            }
        } catch (error) {
            console.error('Error clearing cache:', error);
            this.showError('Failed to clear cache: ' + error.message);
        }
    }

    async viewLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();

            if (data.success) {
                // Populate logs modal
                const logsContent = document.getElementById('app-logs-content');
                if (logsContent) {
                    logsContent.textContent = data.data.logs || 'No logs available';
                }
                
                // Open logs modal
                if (window.modalManager) {
                    window.modalManager.open('logs-modal');
                }
            } else {
                this.showError(data.error || 'Failed to load logs');
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            this.showError('Failed to load logs: ' + error.message);
        }
    }

    async downloadLogs() {
        try {
            const response = await fetch('/api/logs/download');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `dashboard-logs-${new Date().toISOString().split('T')[0]}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showSuccess('Logs downloaded successfully');
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to download logs');
            }
        } catch (error) {
            console.error('Error downloading logs:', error);
            this.showError('Failed to download logs: ' + error.message);
        }
    }

    async clearLogs() {
        if (!confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/logs/clear', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Logs cleared successfully');
            } else {
                this.showError(data.error || 'Failed to clear logs');
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
            this.showError('Failed to clear logs: ' + error.message);
        }
    }

    getAllSettings() {
        return { ...this.settings };
    }

    getDefaultSettings() {
        return { ...this.defaultSettings };
    }

    showSuccess(message) {
        if (window.notificationManager) {
            window.notificationManager.success(message);
        } else {
            console.log('Success:', message);
        }
    }

    showError(message) {
        if (window.notificationManager) {
            window.notificationManager.error(message);
        } else {
            console.error('Error:', message);
        }
    }
}

// Initialize and export
window.settingsManager = new SettingsManager();
export default window.settingsManager; 