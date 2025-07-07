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

    // Wildcard Encoding Fix Methods
    async checkWildcardEncoding() {
        try {
            this.showInfo('Checking wildcard encoding...');
            
            const response = await fetch('/api/check-wildcard-encoding');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayWildcardResults(data.results, 'check');
                this.updateWildcardStats(data.results);
                this.showSuccess(data.message);
            } else {
                this.showError(data.message || 'Failed to check wildcard encoding');
            }
        } catch (error) {
            console.error('Error checking wildcard encoding:', error);
            this.showError('Failed to check wildcard encoding: ' + error.message);
        }
    }

    async fixWildcardEncoding() {
        try {
            this.showInfo('Fixing wildcard encoding...');
            
            const response = await fetch('/api/fix-wildcard-encoding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wildcards_dir: 'wildcards',
                    dry_run: false
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayWildcardResults(data.results, 'fix');
                this.updateWildcardStats(data.results);
                this.showSuccess(data.message);
            } else {
                this.showError(data.message || 'Failed to fix wildcard encoding');
            }
        } catch (error) {
            console.error('Error fixing wildcard encoding:', error);
            this.showError('Failed to fix wildcard encoding: ' + error.message);
        }
    }

    async fixWildcardEncodingDryRun() {
        try {
            this.showInfo('Running wildcard encoding fix (dry run)...');
            
            const response = await fetch('/api/fix-wildcard-encoding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wildcards_dir: 'wildcards',
                    dry_run: true
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayWildcardResults(data.results, 'dry-run');
                this.updateWildcardStats(data.results);
                this.showSuccess(data.message);
            } else {
                this.showError(data.message || 'Failed to run wildcard encoding dry run');
            }
        } catch (error) {
            console.error('Error running wildcard encoding dry run:', error);
            this.showError('Failed to run wildcard encoding dry run: ' + error.message);
        }
    }

    displayWildcardResults(results, operation) {
        const resultsContainer = document.getElementById('wildcard-results');
        const resultsContent = document.getElementById('wildcard-results-content');
        
        if (!resultsContainer || !resultsContent) {
            console.error('Wildcard results containers not found');
            return;
        }
        
        let html = `
            <div class="results-summary">
                <div class="summary-item">
                    <span class="summary-label">Operation:</span>
                    <span class="summary-value">${operation === 'check' ? 'Check' : operation === 'fix' ? 'Fix' : 'Dry Run'}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Total Files:</span>
                    <span class="summary-value">${results.total_files}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Files Checked:</span>
                    <span class="summary-value">${results.files_checked}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Files Fixed:</span>
                    <span class="summary-value">${results.files_fixed}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Files Skipped:</span>
                    <span class="summary-value">${results.skipped_files.length}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Errors:</span>
                    <span class="summary-value">${results.errors.length}</span>
                </div>
            </div>
        `;
        
        if (results.fixed_files && results.fixed_files.length > 0) {
            html += `
                <div class="results-section">
                    <h6><i class="fas fa-wrench"></i> Fixed Files:</h6>
                    <ul class="results-list">
                        ${results.fixed_files.map(file => `<li><i class="fas fa-check text-success"></i> ${file}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (results.skipped_files && results.skipped_files.length > 0) {
            html += `
                <div class="results-section">
                    <h6><i class="fas fa-check-circle"></i> Skipped Files (Already UTF-8):</h6>
                    <ul class="results-list">
                        ${results.skipped_files.slice(0, 10).map(file => `<li><i class="fas fa-info text-info"></i> ${file}</li>`).join('')}
                        ${results.skipped_files.length > 10 ? `<li><i class="fas fa-ellipsis-h text-muted"></i> ... and ${results.skipped_files.length - 10} more</li>` : ''}
                    </ul>
                </div>
            `;
        }
        
        if (results.errors && results.errors.length > 0) {
            html += `
                <div class="results-section">
                    <h6><i class="fas fa-exclamation-triangle"></i> Errors:</h6>
                    <ul class="results-list">
                        ${results.errors.map(error => `<li><i class="fas fa-times text-danger"></i> ${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (results.verification_errors && results.verification_errors.length > 0) {
            html += `
                <div class="results-section">
                    <h6><i class="fas fa-exclamation-circle"></i> Verification Errors:</h6>
                    <ul class="results-list">
                        ${results.verification_errors.map(error => `<li><i class="fas fa-times text-warning"></i> ${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultsContent.innerHTML = html;
        resultsContainer.style.display = 'block';
    }

    updateWildcardStats(results) {
        const filesCountElement = document.getElementById('wildcard-files-count');
        const encodingStatusElement = document.getElementById('wildcard-encoding-status');
        
        if (filesCountElement) {
            filesCountElement.textContent = results.total_files || '--';
        }
        
        if (encodingStatusElement) {
            if (results.files_fixed > 0) {
                encodingStatusElement.textContent = `${results.files_fixed} fixed`;
                encodingStatusElement.className = 'stat-value text-warning';
            } else if (results.errors.length > 0) {
                encodingStatusElement.textContent = `${results.errors.length} errors`;
                encodingStatusElement.className = 'stat-value text-danger';
            } else {
                encodingStatusElement.textContent = 'All OK';
                encodingStatusElement.className = 'stat-value text-success';
            }
        }
    }

    clearWildcardResults() {
        const resultsContainer = document.getElementById('wildcard-results');
        const resultsContent = document.getElementById('wildcard-results-content');
        
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        if (resultsContent) {
            resultsContent.innerHTML = '';
        }
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

    showInfo(message) {
        if (window.notificationManager) {
            window.notificationManager.info(message);
        } else {
            console.info('Info:', message);
        }
    }
}

// Initialize and export
window.settingsManager = new SettingsManager();
export default window.settingsManager; 