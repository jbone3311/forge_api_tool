// Dashboard JavaScript
let socket = null;
let currentConfig = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    loadInitialData();
    setupEventListeners();
});

// Initialize WebSocket connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateForgeStatus();
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        showToast('Disconnected from server', 'warning');
    });
    
    socket.on('progress_update', function(data) {
        updateProgress(data);
    });
    
    socket.on('queue_status', function(data) {
        updateQueueStatus(data);
    });
    
    socket.on('status', function(data) {
        console.log('Status:', data.message);
    });
}

// Load initial data
function loadInitialData() {
    loadConfigs();
    loadQueueStatus();
    updateForgeStatus();
}

// Setup event listeners
function setupEventListeners() {
    // Refresh status button
    document.getElementById('refresh-status').addEventListener('click', function() {
        updateForgeStatus();
    });
    
    // Auto-refresh queue status every 5 seconds
    setInterval(loadQueueStatus, 5000);
}

// Load configurations
function loadConfigs() {
    fetch('/api/configs')
        .then(response => response.json())
        .then(configs => {
            displayConfigs(configs);
        })
        .catch(error => {
            console.error('Error loading configs:', error);
            showToast('Error loading configurations', 'error');
        });
}

// Display configurations
function displayConfigs(configs) {
    const container = document.getElementById('configs-container');
    
    if (configs.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-folder-open fa-3x mb-3"></i>
                <p>No configurations found</p>
                <p>Add JSON files to the configs/ directory</p>
            </div>
        `;
        return;
    }
    
    const configCards = configs.map(config => createConfigCard(config)).join('');
    container.innerHTML = configCards;
}

// Create configuration card
function createConfigCard(config) {
    const statusClass = config.error ? 'error' : 'success';
    const statusIcon = config.error ? 'fa-exclamation-triangle' : 'fa-check-circle';
    
    return `
        <div class="card config-card ${statusClass} mb-3 fade-in">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h5 class="card-title mb-1">
                            <i class="fas ${statusIcon} text-${config.error ? 'danger' : 'success'} me-2"></i>
                            ${config.name}
                        </h5>
                        ${config.description ? `<p class="text-muted mb-0">${config.description}</p>` : ''}
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="previewConfig('${config.name}')">
                            <i class="fas fa-eye"></i> Preview
                        </button>
                        <button class="btn btn-outline-info btn-sm" onclick="showWildcardUsage('${config.name}')">
                            <i class="fas fa-chart-bar"></i> Usage
                        </button>
                        <button class="btn btn-success btn-sm" onclick="addJobToQueue('${config.name}')">
                            <i class="fas fa-plus"></i> Add Job
                        </button>
                    </div>
                </div>
                
                <div class="config-info">
                    <div class="config-info-item">
                        <div class="config-info-label">Model</div>
                        <div class="config-info-value">${config.model_type.toUpperCase()}</div>
                    </div>
                    <div class="config-info-item">
                        <div class="config-info-label">Resolution</div>
                        <div class="config-info-value">${config.width}×${config.height}</div>
                    </div>
                    <div class="config-info-item">
                        <div class="config-info-label">Steps</div>
                        <div class="config-info-value">${config.steps}</div>
                    </div>
                    <div class="config-info-item">
                        <div class="config-info-label">Total Images</div>
                        <div class="config-info-value">${config.total_images}</div>
                    </div>
                </div>
                
                <div class="mb-2">
                    <strong>Prompt Template:</strong>
                    <div class="preview-prompt">${config.prompt_template}</div>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="wildcard-status ${config.wildcards.available > 0 ? 'available' : 'missing'}"></span>
                        <small class="text-muted">
                            ${config.wildcards.available} wildcards available
                            ${config.wildcards.missing > 0 ? `(${config.wildcards.missing} missing)` : ''}
                        </small>
                    </div>
                    <span class="badge bg-${config.error ? 'danger' : 'success'} status-badge">
                        ${config.error ? 'Error' : 'Ready'}
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Load queue status
function loadQueueStatus() {
    fetch('/api/queue/status')
        .then(response => response.json())
        .then(status => {
            updateQueueStatus(status);
        })
        .catch(error => {
            console.error('Error loading queue status:', error);
        });
}

// Update queue status display
function updateQueueStatus(status) {
    const container = document.getElementById('queue-status');
    
    const queueHtml = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">${status.total_jobs}</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${status.pending_jobs}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${status.completed_jobs}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${status.total_images}</div>
                <div class="stat-label">Total Images</div>
            </div>
        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6>Job Queue</h6>
            <div>
                <button class="btn btn-outline-secondary btn-sm" onclick="clearCompletedJobs()">
                    <i class="fas fa-trash"></i> Clear Completed
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="clearAllJobs()">
                    <i class="fas fa-trash-alt"></i> Clear All
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = queueHtml;
    
    // Update current job display
    updateCurrentJob(status.current_job);
    
    // Update start/stop buttons
    const startBtn = document.getElementById('start-queue');
    const stopBtn = document.getElementById('stop-queue');
    
    if (status.running_jobs > 0) {
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
    } else {
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
    }
}

// Update current job display
function updateCurrentJob(job) {
    const container = document.getElementById('current-job');
    
    if (!job) {
        container.innerHTML = '<p class="text-muted">No job running</p>';
        document.getElementById('progress-container').style.display = 'none';
        return;
    }
    
    const progressPercent = job.total_images > 0 ? (job.completed_images / job.total_images) * 100 : 0;
    
    container.innerHTML = `
        <div class="mb-2">
            <strong>${job.config_name}</strong>
            <span class="badge bg-${getStatusColor(job.status)} ms-2">${job.status}</span>
        </div>
        <div class="mb-2">
            <small class="text-muted">
                Batch ${job.current_batch} • Image ${job.completed_images}/${job.total_images}
            </small>
        </div>
        <div class="progress mb-2">
            <div class="progress-bar" style="width: ${progressPercent}%"></div>
        </div>
        <div class="d-flex justify-content-between">
            <small class="text-muted">${progressPercent.toFixed(1)}% complete</small>
            ${job.status === 'running' ? `
                <button class="btn btn-warning btn-sm" onclick="cancelCurrentJob()">
                    <i class="fas fa-stop"></i> Cancel
                </button>
            ` : ''}
        </div>
    `;
    
    if (job.status === 'running') {
        document.getElementById('progress-container').style.display = 'block';
        updateProgress({
            job_id: job.id,
            config_name: job.config_name,
            current_batch: job.current_batch,
            current_image: job.completed_images,
            total_images: job.total_images,
            progress_percent: progressPercent,
            status: job.status
        });
    } else {
        document.getElementById('progress-container').style.display = 'none';
    }
}

// Update progress display
function updateProgress(data) {
    const container = document.getElementById('progress-container');
    const title = document.getElementById('progress-title');
    const bar = document.getElementById('progress-bar');
    const text = document.getElementById('progress-text');
    
    title.textContent = `${data.config_name} - Generating image ${data.current_image}/${data.total_images}`;
    bar.style.width = `${data.progress_percent}%`;
    text.textContent = `${data.progress_percent.toFixed(1)}% complete`;
    
    if (data.status === 'completed') {
        setTimeout(() => {
            container.style.display = 'none';
        }, 3000);
    }
}

// Update Forge status
function updateForgeStatus() {
    fetch('/api/forge/status')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('forge-status');
            const badge = statusElement.querySelector('.badge');
            
            if (data.connected) {
                badge.className = 'badge bg-success';
                badge.textContent = 'Forge Connected';
            } else {
                badge.className = 'badge bg-danger';
                badge.textContent = 'Forge Disconnected';
            }
        })
        .catch(error => {
            console.error('Error checking Forge status:', error);
            const statusElement = document.getElementById('forge-status');
            const badge = statusElement.querySelector('.badge');
            badge.className = 'badge bg-danger';
            badge.textContent = 'Connection Error';
        });
}

// Preview configuration
function previewConfig(configName) {
    fetch(`/api/config/${configName}/preview?count=5`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
                return;
            }
            
            const content = document.getElementById('preview-content');
            content.innerHTML = `
                <div class="mb-3">
                    <h6>Configuration Summary</h6>
                    <div class="config-info">
                        <div class="config-info-item">
                            <div class="config-info-label">Model</div>
                            <div class="config-info-value">${data.config_summary.model_type.toUpperCase()}</div>
                        </div>
                        <div class="config-info-item">
                            <div class="config-info-label">Resolution</div>
                            <div class="config-info-value">${data.config_summary.width}×${data.config_summary.height}</div>
                        </div>
                        <div class="config-info-item">
                            <div class="config-info-label">Total Images</div>
                            <div class="config-info-value">${data.total_images}</div>
                        </div>
                    </div>
                </div>
                
                <h6>Sample Prompts (${data.prompts.length})</h6>
                ${data.prompts.map((prompt, index) => `
                    <div class="preview-prompt">
                        <strong>${index + 1}.</strong> ${prompt}
                    </div>
                `).join('')}
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error previewing config:', error);
            showToast('Error previewing configuration', 'error');
        });
}

// Show wildcard usage
function showWildcardUsage(configName) {
    currentConfig = configName;
    
    fetch(`/api/config/${configName}/wildcard-usage`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
                return;
            }
            
            const content = document.getElementById('usage-content');
            let usageHtml = '';
            
            for (const [wildcardName, usage] of Object.entries(data)) {
                usageHtml += `
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0">${wildcardName}</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-2">
                                <strong>Total Uses:</strong> ${usage.total_uses}
                            </div>
                            <div class="mb-2">
                                <strong>Least Used Items:</strong>
                                <div class="mt-1">
                                    ${usage.least_used.map(item => `
                                        <span class="badge bg-light text-dark me-1">${item}</span>
                                    `).join('')}
                                </div>
                            </div>
                            <div>
                                <strong>Usage Breakdown:</strong>
                                ${Object.entries(usage.items).map(([item, stats]) => `
                                    <div class="usage-item">
                                        <span>${item}</span>
                                        <span class="usage-percentage ${stats.status}">
                                            ${stats.count} uses (${stats.percentage.toFixed(1)}%)
                                        </span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }
            
            content.innerHTML = usageHtml || '<p class="text-muted">No usage data available</p>';
            
            const modal = new bootstrap.Modal(document.getElementById('usageModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading wildcard usage:', error);
            showToast('Error loading wildcard usage', 'error');
        });
}

// Reset wildcards
function resetWildcards() {
    if (!currentConfig) return;
    
    fetch(`/api/config/${currentConfig}/reset-wildcards`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Wildcard usage reset successfully', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('usageModal'));
                modal.hide();
                showWildcardUsage(currentConfig);
            } else {
                showToast('Error resetting wildcard usage', 'error');
            }
        })
        .catch(error => {
            console.error('Error resetting wildcards:', error);
            showToast('Error resetting wildcard usage', 'error');
        });
}

// Add job to queue
function addJobToQueue(configName) {
    // Populate config select
    const configSelect = document.getElementById('config-select');
    configSelect.innerHTML = `<option value="${configName}">${configName}</option>`;
    configSelect.value = configName;
    
    const modal = new bootstrap.Modal(document.getElementById('addJobModal'));
    modal.show();
}

// Add job
function addJob() {
    const configName = document.getElementById('config-select').value;
    const batchSize = document.getElementById('batch-size').value;
    const numBatches = document.getElementById('num-batches').value;
    
    if (!configName) {
        showToast('Please select a configuration', 'warning');
        return;
    }
    
    const jobData = {
        config_name: configName,
        batch_size: batchSize ? parseInt(batchSize) : null,
        num_batches: numBatches ? parseInt(numBatches) : null
    };
    
    fetch('/api/queue/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jobData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                showToast('Job added to queue successfully', 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addJobModal'));
                modal.hide();
                loadQueueStatus();
            }
        })
        .catch(error => {
            console.error('Error adding job:', error);
            showToast('Error adding job to queue', 'error');
        });
}

// Queue control functions
function startQueue() {
    fetch('/api/queue/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Queue processing started', 'success');
                loadQueueStatus();
            } else {
                showToast(data.error || 'Error starting queue', 'error');
            }
        })
        .catch(error => {
            console.error('Error starting queue:', error);
            showToast('Error starting queue', 'error');
        });
}

function stopQueue() {
    fetch('/api/queue/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Queue processing stopped', 'success');
                loadQueueStatus();
            } else {
                showToast(data.error || 'Error stopping queue', 'error');
            }
        })
        .catch(error => {
            console.error('Error stopping queue:', error);
            showToast('Error stopping queue', 'error');
        });
}

function cancelCurrentJob() {
    fetch('/api/queue/cancel', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Current job cancelled', 'success');
                loadQueueStatus();
            } else {
                showToast(data.error || 'Error cancelling job', 'error');
            }
        })
        .catch(error => {
            console.error('Error cancelling job:', error);
            showToast('Error cancelling job', 'error');
        });
}

function clearCompletedJobs() {
    fetch('/api/queue/clear-completed', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Completed jobs cleared', 'success');
                loadQueueStatus();
            } else {
                showToast(data.error || 'Error clearing jobs', 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing jobs:', error);
            showToast('Error clearing jobs', 'error');
        });
}

function clearAllJobs() {
    if (!confirm('Are you sure you want to clear all jobs?')) return;
    
    fetch('/api/queue/clear-all', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('All jobs cleared', 'success');
                loadQueueStatus();
            } else {
                showToast(data.error || 'Error clearing jobs', 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing jobs:', error);
            showToast('Error clearing jobs', 'error');
        });
}

// Utility functions
function getStatusColor(status) {
    switch (status) {
        case 'pending': return 'secondary';
        case 'running': return 'primary';
        case 'completed': return 'success';
        case 'failed': return 'danger';
        case 'cancelled': return 'warning';
        default: return 'secondary';
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'} text-white`;
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function refreshConfigs() {
    loadConfigs();
    showToast('Configurations refreshed', 'success');
}

function showNewConfigModal() {
    showToast('New config feature coming soon!', 'info');
} 