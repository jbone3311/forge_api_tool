// Dashboard JavaScript
let socket = null;
let currentConfig = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    loadInitialData();
    setupEventListeners();
    setupConfigModalRefresh();
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
            const connectBtn = document.getElementById('connect-forge');
            const disconnectBtn = document.getElementById('disconnect-forge');
            
            if (data.connected) {
                statusElement.innerHTML = `
                    <span class="badge bg-success">
                        <i class="fas fa-check-circle"></i> Connected
                    </span>
                `;
                connectBtn.style.display = 'none';
                disconnectBtn.style.display = 'inline-block';
            } else {
                statusElement.innerHTML = `
                    <span class="badge bg-danger">
                        <i class="fas fa-times-circle"></i> Disconnected
                    </span>
                `;
                connectBtn.style.display = 'inline-block';
                disconnectBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error updating Forge status:', error);
            const statusElement = document.getElementById('forge-status');
            statusElement.innerHTML = `
                <span class="badge bg-secondary">
                    <i class="fas fa-question-circle"></i> Unknown
                </span>
            `;
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
}

// Show new config modal
function showNewConfigModal() {
    const modal = new bootstrap.Modal(document.getElementById('newConfigModal'));
    modal.show();
    loadConfigTemplates();
}

// Load configuration templates
function loadConfigTemplates() {
    fetch('/api/config/templates')
        .then(response => response.json())
        .then(templates => {
            const container = document.getElementById('config-templates');
            const templateHtml = templates.map(template => `
                <button type="button" class="list-group-item list-group-item-action" 
                        onclick="loadTemplate('${template.name}')">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${template.name}</h6>
                    </div>
                    <p class="mb-1">${template.description}</p>
                </button>
            `).join('');
            container.innerHTML = templateHtml;
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            document.getElementById('config-templates').innerHTML = 
                '<div class="alert alert-danger">Error loading templates</div>';
        });
}

// Load a template into the form
function loadTemplate(templateName) {
    fetch('/api/config/templates')
        .then(response => response.json())
        .then(templates => {
            const template = templates.find(t => t.name === templateName);
            if (template) {
                const config = template.template;
                
                // Fill form fields
                document.getElementById('config-name').value = config.name;
                document.getElementById('config-description').value = config.description;
                document.getElementById('config-model-type').value = config.model_type;
                document.getElementById('config-sampler').value = config.generation_settings.sampler;
                document.getElementById('config-steps').value = config.generation_settings.steps;
                document.getElementById('config-width').value = config.generation_settings.width;
                document.getElementById('config-height').value = config.generation_settings.height;
                document.getElementById('config-prompt').value = config.prompt_settings.base_prompt;
                document.getElementById('config-negative-prompt').value = config.prompt_settings.negative_prompt;
                
                // Convert wildcards to JSON string
                const wildcardsJson = JSON.stringify(config.wildcards, null, 2);
                document.getElementById('config-wildcards').value = wildcardsJson;
                
                showToast(`Loaded template: ${templateName}`, 'success');
            }
        })
        .catch(error => {
            console.error('Error loading template:', error);
            showToast('Error loading template', 'error');
        });
}

// Create new configuration
function createConfig() {
    const form = document.getElementById('new-config-form');
    const formData = new FormData(form);
    
    // Get form values
    const configData = {
        name: document.getElementById('config-name').value,
        description: document.getElementById('config-description').value,
        model_type: document.getElementById('config-model-type').value,
        prompt_settings: {
            base_prompt: document.getElementById('config-prompt').value,
            negative_prompt: document.getElementById('config-negative-prompt').value
        },
        wildcards: {},
        generation_settings: {
            steps: parseInt(document.getElementById('config-steps').value),
            width: parseInt(document.getElementById('config-width').value),
            height: parseInt(document.getElementById('config-height').value),
            batch_size: 1,
            sampler: document.getElementById('config-sampler').value,
            cfg_scale: 7.0,
            seed: "random"
        },
        model_settings: {
            checkpoint: "",
            vae: "",
            text_encoder: "",
            gpu_weight: 1.0,
            swap_method: "weight",
            swap_location: "cpu"
        },
        output_settings: {
            output_dir: `outputs/${document.getElementById('config-name').value.toLowerCase().replace(/\s+/g, '_')}`,
            filename_pattern: "{prompt_hash}_{seed}_{timestamp}",
            save_metadata: true,
            save_prompt_list: true
        },
        wildcard_settings: {
            randomization_mode: "smart_cycle",
            cycle_length: 10,
            shuffle_on_reset: true
        },
        alwayson_scripts: {}
    };
    
    // Parse wildcards JSON
    try {
        const wildcardsText = document.getElementById('config-wildcards').value;
        if (wildcardsText.trim()) {
            configData.wildcards = JSON.parse(wildcardsText);
        }
    } catch (e) {
        showToast('Invalid wildcards JSON format', 'error');
        return;
    }
    
    // Validate required fields
    if (!configData.name || !configData.prompt_settings.base_prompt) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Send request to create config
    fetch('/api/config/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('newConfigModal'));
            modal.hide();
            loadConfigs(); // Refresh config list
        } else {
            showToast(data.error || 'Failed to create configuration', 'error');
        }
    })
    .catch(error => {
        console.error('Error creating config:', error);
        showToast('Error creating configuration', 'error');
    });
}

// Show connect modal
function showConnectModal() {
    const modal = new bootstrap.Modal(document.getElementById('connectModal'));
    modal.show();
}

// Connect to Forge API
function connectForge() {
    const serverUrl = document.getElementById('server-url').value;
    
    if (!serverUrl) {
        showToast('Please enter a server URL', 'error');
        return;
    }
    
    fetch('/api/forge/connect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            server_url: serverUrl
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateForgeStatus();
            const modal = bootstrap.Modal.getInstance(document.getElementById('connectModal'));
            modal.hide();
        } else {
            showToast(data.error || 'Failed to connect', 'error');
        }
    })
    .catch(error => {
        console.error('Error connecting to Forge:', error);
        showToast('Error connecting to Forge API', 'error');
    });
}

// Disconnect from Forge API
function disconnectForge() {
    if (!confirm('Are you sure you want to disconnect from the Forge API?')) {
        return;
    }
    
    fetch('/api/forge/disconnect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateForgeStatus();
        } else {
            showToast(data.error || 'Failed to disconnect', 'error');
        }
    })
    .catch(error => {
        console.error('Error disconnecting from Forge:', error);
        showToast('Error disconnecting from Forge API', 'error');
    });
}

// Show shutdown confirmation modal
function shutdownApplication() {
    const modal = new bootstrap.Modal(document.getElementById('shutdownModal'));
    modal.show();
}

// Confirm and execute shutdown
function confirmShutdown() {
    fetch('/api/shutdown', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'info');
            // Show shutdown message and disable interface
            document.body.innerHTML = `
                <div class="container-fluid d-flex align-items-center justify-content-center" style="height: 100vh;">
                    <div class="text-center">
                        <i class="fas fa-power-off fa-3x text-muted mb-3"></i>
                        <h3>Application Shutting Down...</h3>
                        <p class="text-muted">The Forge API Tool is shutting down. You can close this window.</p>
                    </div>
                </div>
            `;
        } else {
            showToast(data.error || 'Failed to shutdown', 'error');
        }
    })
    .catch(error => {
        console.error('Error shutting down:', error);
        showToast('Error shutting down application', 'error');
    });
}

// Add event listener to refresh configs when New Config modal closes
function setupConfigModalRefresh() {
    const modal = document.getElementById('newConfigModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            loadConfigs();
        });
    }
} 