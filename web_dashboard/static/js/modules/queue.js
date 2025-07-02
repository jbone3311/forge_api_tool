/**
 * Queue Management Module
 * Handles job queue operations and status updates
 */

class QueueManager {
    constructor() {
        this.queueData = {
            total_jobs: 0,
            pending_jobs: 0,
            running_jobs: 0,
            completed_jobs: 0,
            failed_jobs: 0,
            total_images: 0,
            completed_images: 0,
            failed_images: 0,
            current_job: null
        };
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.refreshQueue();
        console.log('Queue Manager initialized');
    }

    setupEventListeners() {
        // Listen for queue-related events
        document.addEventListener('queueUpdated', () => {
            this.refreshQueue();
        });

        // Listen for generation events
        document.addEventListener('generationStarted', () => {
            this.refreshQueue();
        });

        document.addEventListener('generationCompleted', () => {
            this.refreshQueue();
        });
    }

    async refreshQueue() {
        try {
            const response = await fetch('/api/queue/status');
            const data = await response.json();

            if (data.success) {
                this.queueData = data.data;
                this.updateQueueDisplay();
                this.updateStatusIndicators();
            } else {
                console.error('Failed to refresh queue:', data.error);
            }
        } catch (error) {
            console.error('Error refreshing queue:', error);
        }
    }

    updateQueueDisplay() {
        // Update queue status indicator
        const queueStatusElement = document.getElementById('queue-status');
        if (queueStatusElement) {
            const textElement = queueStatusElement.querySelector('.status-text');
            if (textElement) {
                textElement.textContent = `Queue: ${this.queueData.total_jobs} jobs`;
            }
        }

        // Update any queue display elements
        const queueDisplayElements = document.querySelectorAll('.queue-display');
        queueDisplayElements.forEach(element => {
            this.updateQueueElement(element);
        });
    }

    updateQueueElement(element) {
        const template = `
            <div class="queue-stats">
                <div class="stat-item">
                    <span class="stat-label">Total Jobs:</span>
                    <span class="stat-value">${this.queueData.total_jobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Pending:</span>
                    <span class="stat-value">${this.queueData.pending_jobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Running:</span>
                    <span class="stat-value">${this.queueData.running_jobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Completed:</span>
                    <span class="stat-value">${this.queueData.completed_jobs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Failed:</span>
                    <span class="stat-value">${this.queueData.failed_jobs}</span>
                </div>
            </div>
            ${this.queueData.current_job ? `
                <div class="current-job">
                    <h4>Current Job</h4>
                    <div class="job-info">
                        <div><strong>Config:</strong> ${this.queueData.current_job.config_name || 'Unknown'}</div>
                        <div><strong>Progress:</strong> ${this.queueData.current_job.progress || 0}%</div>
                        <div><strong>Status:</strong> ${this.queueData.current_job.status || 'Unknown'}</div>
                    </div>
                </div>
            ` : ''}
        `;

        element.innerHTML = template;
    }

    updateStatusIndicators() {
        // Update queue status in header
        const queueStatusIndicator = document.getElementById('queue-status');
        if (queueStatusIndicator) {
            const icon = queueStatusIndicator.querySelector('.status-icon');
            const text = queueStatusIndicator.querySelector('.status-text');

            if (this.queueData.running_jobs > 0) {
                icon.className = 'fas fa-spinner fa-spin status-icon';
                text.textContent = `Queue: ${this.queueData.running_jobs} running`;
            } else if (this.queueData.pending_jobs > 0) {
                icon.className = 'fas fa-clock status-icon';
                text.textContent = `Queue: ${this.queueData.pending_jobs} pending`;
            } else {
                icon.className = 'fas fa-check-circle status-icon';
                text.textContent = `Queue: ${this.queueData.total_jobs} jobs`;
            }
        }
    }

    async clearQueue() {
        try {
            const response = await fetch('/api/queue/clear', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Queue cleared successfully');
                this.refreshQueue();
            } else {
                this.showError(data.error || 'Failed to clear queue');
            }
        } catch (error) {
            console.error('Error clearing queue:', error);
            this.showError('Failed to clear queue: ' + error.message);
        }
    }

    async pauseQueue() {
        try {
            const response = await fetch('/api/queue/pause', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Queue paused');
                this.refreshQueue();
            } else {
                this.showError(data.error || 'Failed to pause queue');
            }
        } catch (error) {
            console.error('Error pausing queue:', error);
            this.showError('Failed to pause queue: ' + error.message);
        }
    }

    async resumeQueue() {
        try {
            const response = await fetch('/api/queue/resume', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Queue resumed');
                this.refreshQueue();
            } else {
                this.showError(data.error || 'Failed to resume queue');
            }
        } catch (error) {
            console.error('Error resuming queue:', error);
            this.showError('Failed to resume queue: ' + error.message);
        }
    }

    async removeJob(jobId) {
        try {
            const response = await fetch(`/api/queue/jobs/${jobId}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Job removed from queue');
                this.refreshQueue();
            } else {
                this.showError(data.error || 'Failed to remove job');
            }
        } catch (error) {
            console.error('Error removing job:', error);
            this.showError('Failed to remove job: ' + error.message);
        }
    }

    async retryJob(jobId) {
        try {
            const response = await fetch(`/api/queue/jobs/${jobId}/retry`, {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('Job queued for retry');
                this.refreshQueue();
            } else {
                this.showError(data.error || 'Failed to retry job');
            }
        } catch (error) {
            console.error('Error retrying job:', error);
            this.showError('Failed to retry job: ' + error.message);
        }
    }

    getQueueStats() {
        return this.queueData;
    }

    isQueueEmpty() {
        return this.queueData.total_jobs === 0;
    }

    hasRunningJobs() {
        return this.queueData.running_jobs > 0;
    }

    hasPendingJobs() {
        return this.queueData.pending_jobs > 0;
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

    startAutoRefresh(interval = 10000) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.refreshInterval = setInterval(() => {
            this.refreshQueue();
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
window.queueManager = new QueueManager();
export default window.queueManager; 