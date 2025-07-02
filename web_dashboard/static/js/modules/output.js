/**
 * Output Management Module
 * Handles output gallery, file operations, and output statistics
 */

class OutputManager {
    constructor() {
        this.outputs = [];
        this.outputStats = {
            total_outputs: 0,
            total_size: 0,
            recent_outputs: 0
        };
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.refreshOutputs();
        console.log('Output Manager initialized');
    }

    setupEventListeners() {
        // Listen for output-related events
        document.addEventListener('outputsUpdated', () => {
            this.refreshOutputs();
        });

        // Listen for generation completion
        document.addEventListener('generationCompleted', () => {
            this.refreshOutputs();
        });
    }

    async refreshOutputs() {
        try {
            const response = await fetch('/api/outputs/list');
            const data = await response.json();

            if (data.success) {
                this.outputs = data.data.outputs || [];
                this.outputStats = data.data.stats || this.outputStats;
                this.updateOutputDisplay();
                this.updateStatusIndicators();
            } else {
                console.error('Failed to refresh outputs:', data.error);
            }
        } catch (error) {
            console.error('Error refreshing outputs:', error);
        }
    }

    updateOutputDisplay() {
        // Update output gallery if it exists
        const galleryElement = document.getElementById('output-gallery');
        if (galleryElement) {
            this.updateGallery(galleryElement);
        }

        // Update output stats display
        const statsElements = document.querySelectorAll('.output-stats');
        statsElements.forEach(element => {
            this.updateStatsElement(element);
        });
    }

    updateGallery(galleryElement) {
        if (this.outputs.length === 0) {
            galleryElement.innerHTML = `
                <div class="no-outputs">
                    <i class="fas fa-images" style="font-size: 3rem; opacity: 0.3;"></i>
                    <p>No outputs yet</p>
                    <p class="text-muted">Generate some images to see them here</p>
                </div>
            `;
            return;
        }

        const galleryHTML = this.outputs.map(output => `
            <div class="output-item" data-output-id="${output.id}">
                <div class="output-image">
                    <img src="${output.thumbnail_url || output.url}" alt="Generated output" loading="lazy">
                    <div class="output-overlay">
                        <button class="btn btn-sm btn-primary" onclick="window.outputManager.openOutput('${output.id}')">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="window.outputManager.downloadOutput('${output.id}')">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="window.outputManager.deleteOutput('${output.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="output-info">
                    <div class="output-name">${output.filename}</div>
                    <div class="output-meta">
                        <span class="output-size">${this.formatFileSize(output.size)}</span>
                        <span class="output-date">${this.formatDate(output.created_at)}</span>
                    </div>
                    ${output.config_name ? `<div class="output-config">${output.config_name}</div>` : ''}
                </div>
            </div>
        `).join('');

        galleryElement.innerHTML = galleryHTML;
    }

    updateStatsElement(element) {
        const template = `
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-label">Total Outputs:</span>
                    <span class="stat-value">${this.outputStats.total_outputs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Size:</span>
                    <span class="stat-value">${this.formatFileSize(this.outputStats.total_size)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Recent (24h):</span>
                    <span class="stat-value">${this.outputStats.recent_outputs}</span>
                </div>
            </div>
        `;

        element.innerHTML = template;
    }

    updateStatusIndicators() {
        // Update any output-related status indicators
        const outputElements = document.querySelectorAll('.output-count');
        outputElements.forEach(element => {
            element.textContent = this.outputStats.total_outputs;
        });
    }

    async openOutput(outputId) {
        try {
            const response = await fetch(`/api/outputs/${outputId}/open`);
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Output opened successfully');
            } else {
                this.showError(data.error || 'Failed to open output');
            }
        } catch (error) {
            console.error('Error opening output:', error);
            this.showError('Failed to open output: ' + error.message);
        }
    }

    async downloadOutput(outputId) {
        try {
            const response = await fetch(`/api/outputs/${outputId}/download`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'output.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showSuccess('Output downloaded successfully');
            } else {
                const data = await response.json();
                this.showError(data.error || 'Failed to download output');
            }
        } catch (error) {
            console.error('Error downloading output:', error);
            this.showError('Failed to download output: ' + error.message);
        }
    }

    async deleteOutput(outputId) {
        if (!confirm('Are you sure you want to delete this output?')) {
            return;
        }

        try {
            const response = await fetch(`/api/outputs/${outputId}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Output deleted successfully');
                this.refreshOutputs();
            } else {
                this.showError(data.error || 'Failed to delete output');
            }
        } catch (error) {
            console.error('Error deleting output:', error);
            this.showError('Failed to delete output: ' + error.message);
        }
    }

    async openOutputFolder(configName = null) {
        try {
            const url = configName ? `/api/outputs/folder/${configName}` : '/api/outputs/folder';
            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Output folder opened successfully');
            } else {
                this.showError(data.error || 'Failed to open output folder');
            }
        } catch (error) {
            console.error('Error opening output folder:', error);
            this.showError('Failed to open output folder: ' + error.message);
        }
    }

    async clearAllOutputs() {
        if (!confirm('Are you sure you want to delete ALL outputs? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/outputs/clear', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('All outputs cleared successfully');
                this.refreshOutputs();
            } else {
                this.showError(data.error || 'Failed to clear outputs');
            }
        } catch (error) {
            console.error('Error clearing outputs:', error);
            this.showError('Failed to clear outputs: ' + error.message);
        }
    }

    async getOutputStatistics() {
        try {
            const response = await fetch('/api/outputs/stats');
            const data = await response.json();

            if (data.success) {
                return data.data;
            } else {
                console.error('Failed to get output statistics:', data.error);
                return this.outputStats;
            }
        } catch (error) {
            console.error('Error getting output statistics:', error);
            return this.outputStats;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    getOutputs() {
        return this.outputs;
    }

    getOutputStats() {
        return this.outputStats;
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

    startAutoRefresh(interval = 30000) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.refreshInterval = setInterval(() => {
            this.refreshOutputs();
        }, interval);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize and export
window.outputManager = new OutputManager();
export default window.outputManager; 