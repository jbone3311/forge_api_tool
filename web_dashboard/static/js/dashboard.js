// Forge API Tool Dashboard JavaScript

// Global variables
let socket;
let statusUpdateInterval;
let currentBatchPreview = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    initializeSocket();
    initializeStatusUpdates();
    loadInitialData();
    setupEventListeners();
});

// Socket.IO initialization
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateNotification('Connected to server', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateNotification('Disconnected from server', 'warning');
    });
    
    socket.on('generation_progress', function(data) {
        updateGenerationProgress(data);
    });
    
    socket.on('status_update', function(data) {
        updateStatusIndicators(data);
    });
    
    socket.on('error', function(data) {
        updateNotification(data.message || 'An error occurred', 'error');
    });
}

// Initialize status updates
function initializeStatusUpdates() {
    // Update status every 15 seconds
    statusUpdateInterval = setInterval(function() {
        updateSystemStatus();
    }, 15000);
    
    // Initial status update
    updateSystemStatus();
}

// Load initial data
function loadInitialData() {
    loadOutputs();
    updateQueueStatus();
}

// Setup event listeners
function setupEventListeners() {
    // Template card clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.template-card')) {
            const configName = e.target.closest('.template-card').dataset.config;
            selectTemplate(configName);
        }
    });
    
    // Modal close on backdrop click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });
    
    // Escape key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
    
    // Seed input validation
    const seedInput = document.getElementById('seed-input');
    if (seedInput) {
        seedInput.addEventListener('input', function(e) {
            const value = e.target.value;
            if (value !== '' && value !== '-') {
                const num = parseInt(value);
                if (isNaN(num)) {
                    e.target.setCustomValidity('Please enter a valid number');
                } else {
                    e.target.setCustomValidity('');
                }
            } else {
                e.target.setCustomValidity('');
            }
        });
        
        // Add tooltip for seed input
        seedInput.addEventListener('focus', function() {
            if (this.value === '') {
                this.placeholder = 'Leave empty for random seed';
            }
        });
        
        seedInput.addEventListener('blur', function() {
            this.placeholder = 'Random';
        });
    }
}

// Update system status
function updateSystemStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicators(data);
            updateQueueStatus(data.queue);
            updateOutputStats(data.outputs);
            
            // Adaptive polling: faster updates when generation is active
            if (data.generation && data.generation.active) {
                // If generation is active, poll more frequently
                if (statusUpdateInterval) {
                    clearInterval(statusUpdateInterval);
                    statusUpdateInterval = setInterval(updateSystemStatus, 5000); // 5 seconds during generation
                }
            } else {
                // If idle, use normal polling interval
                if (statusUpdateInterval) {
                    clearInterval(statusUpdateInterval);
                    statusUpdateInterval = setInterval(updateSystemStatus, 15000); // 15 seconds when idle
                }
            }
        })
        .catch(error => {
            console.error('Failed to update status:', error);
            updateStatusIndicators({
                api: { connected: false, error: 'Failed to connect' },
                queue: { queue_size: 0 },
                generation: { active: false }
            });
        });
}

// Update status indicators
function updateStatusIndicators(data) {
    // API Status
    const apiStatus = document.getElementById('api-status');
    if (apiStatus) {
        const apiIcon = apiStatus.querySelector('.status-icon');
        const apiText = apiStatus.querySelector('.status-text');
        const apiConnectBtn = document.getElementById('api-connect-btn');
        
        if (data.api && data.api.connected) {
            apiIcon.className = 'fas fa-circle status-icon connected';
            apiText.textContent = `API: Connected (${data.api.server_url})`;
            if (apiConnectBtn) {
                apiConnectBtn.innerHTML = '<i class="fas fa-unplug"></i> Disconnect';
                apiConnectBtn.className = 'btn btn-sm btn-danger';
            }
        } else {
            apiIcon.className = 'fas fa-circle status-icon disconnected';
            apiText.textContent = `API: Disconnected`;
            if (apiConnectBtn) {
                apiConnectBtn.innerHTML = '<i class="fas fa-plug"></i> Connect';
                apiConnectBtn.className = 'btn btn-sm btn-primary';
            }
        }
    }
    
    // Generation Status
    const generationStatus = document.getElementById('generation-status');
    if (generationStatus) {
        const generationIcon = generationStatus.querySelector('.status-icon');
        const generationText = generationStatus.querySelector('.status-text');
        const stopBtn = document.getElementById('stop-generation-btn');
        
        if (data.generation && data.generation.active) {
            generationIcon.className = 'fas fa-spinner fa-spin status-icon processing';
            const progress = Math.round(data.generation.progress || 0);
            generationText.textContent = `Generation: ${progress}% (${data.generation.current_image}/${data.generation.total_images})`;
            if (stopBtn) stopBtn.style.display = 'inline-flex';
        } else {
            generationIcon.className = 'fas fa-circle status-icon idle';
            generationText.textContent = 'Generation: Idle';
            if (stopBtn) stopBtn.style.display = 'none';
        }
    }
    
    // Queue Status
    const queueStatus = document.getElementById('queue-status');
    if (queueStatus) {
        const queueIcon = queueStatus.querySelector('.status-icon');
        const queueText = queueStatus.querySelector('.status-text');
        
        const queueSize = data.queue ? data.queue.total_jobs : 0;
        queueText.textContent = `Queue: ${queueSize} jobs`;
        
        if (queueSize > 0) {
            queueIcon.className = 'fas fa-list status-icon processing';
        } else {
            queueIcon.className = 'fas fa-list status-icon idle';
        }
    }
}

// Update generation progress
function updateGenerationProgress(data) {
    const progressSection = document.getElementById('progress-section');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressConfig = document.getElementById('progress-config');
    const progressTime = document.getElementById('progress-time');
    
    if (data.active) {
        progressSection.style.display = 'block';
        progressFill.style.width = `${data.progress}%`;
        progressText.textContent = `${data.current} / ${data.total} images`;
        progressPercentage.textContent = `${Math.round(data.progress)}%`;
        progressConfig.textContent = data.config_name;
        
        // Update elapsed time
        if (data.elapsed_time) {
            const minutes = Math.floor(data.elapsed_time / 60);
            const seconds = Math.floor(data.elapsed_time % 60);
            progressTime.textContent = `Elapsed: ${minutes}m ${seconds}s`;
        }
    } else {
        progressSection.style.display = 'none';
    }
}

// Update queue status
function updateQueueStatus(queueData) {
    if (!queueData) return;
    
    const activeEl = document.getElementById('queue-active');
    const pendingEl = document.getElementById('queue-pending');
    const completedEl = document.getElementById('queue-completed');
    
    if (activeEl) activeEl.textContent = queueData.running_jobs || 0;
    if (pendingEl) pendingEl.textContent = queueData.pending_jobs || 0;
    if (completedEl) completedEl.textContent = queueData.completed_jobs || 0;
}

// Update output statistics
function updateOutputStats(outputData) {
    if (!outputData) return;
    
    const totalEl = document.getElementById('total-images');
    const todayEl = document.getElementById('today-images');
    const storageEl = document.getElementById('storage-used');
    
    if (totalEl) totalEl.textContent = outputData.total_outputs || 0;
    if (todayEl) todayEl.textContent = outputData.today_outputs || 0;
    if (storageEl) storageEl.textContent = outputData.storage_used || '0 MB';
}

// Template Management
function selectTemplate(configName) {
    const configSelect = document.getElementById('config-select');
    if (configSelect) configSelect.value = configName;
}

function refreshTemplates() {
    console.log('Refreshing templates...');
    // Show loading state
    const refreshBtn = document.querySelector('.sidebar-actions .btn-secondary');
    if (refreshBtn) {
        const originalContent = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        refreshBtn.disabled = true;
        
        // Reload the page to refresh templates
        setTimeout(() => {
            location.reload();
        }, 500);
    }
}

function showCreateTemplateModal() {
    const modal = document.getElementById('create-template-modal');
    if (modal) modal.style.display = 'block';
}

function editTemplate(configName) {
    console.log('Editing template:', configName);
    fetch(`/api/configs/${configName}`)
        .then(response => response.json())
        .then(data => {
            const nameEl = document.getElementById('edit-template-name');
            const configEl = document.getElementById('edit-template-config');
            const modal = document.getElementById('edit-template-modal');
            
            if (nameEl) nameEl.value = configName;
            if (configEl) configEl.value = JSON.stringify(data, null, 2);
            if (modal) modal.style.display = 'block';
        })
        .catch(error => {
            console.error('Failed to load template:', error);
            updateNotification('Failed to load template', 'error');
        });
}

function deleteTemplate(configName) {
    console.log('Deleting template:', configName);
    if (confirm(`Are you sure you want to delete the template "${configName}"?`)) {
        fetch(`/api/configs/${configName}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Template deleted successfully', 'success');
                    location.reload();
                } else {
                    updateNotification('Failed to delete template', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to delete template:', error);
                updateNotification('Failed to delete template', 'error');
            });
    }
}

function createTemplate() {
    const name = document.getElementById('template-name').value;
    const configText = document.getElementById('template-config').value;
    
    if (!name || !configText) {
        updateNotification('Please fill in all fields', 'warning');
        return;
    }
    
    try {
        const config = JSON.parse(configText);
        
        fetch('/api/configs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, config })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotification('Template created successfully', 'success');
                closeModal('create-template-modal');
                location.reload();
            } else {
                updateNotification('Failed to create template', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to create template:', error);
            updateNotification('Failed to create template', 'error');
        });
    } catch (error) {
        console.error('Invalid JSON configuration:', error);
        updateNotification('Invalid JSON configuration', 'error');
    }
}

function updateTemplate() {
    const name = document.getElementById('edit-template-name').value;
    const configText = document.getElementById('edit-template-config').value;
    
    try {
        const config = JSON.parse(configText);
        
        fetch(`/api/configs/${name}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotification('Template updated successfully', 'success');
                closeModal('edit-template-modal');
                location.reload();
            } else {
                updateNotification('Failed to update template', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to update template:', error);
            updateNotification('Failed to update template', 'error');
        });
    } catch (error) {
        console.error('Invalid JSON configuration:', error);
        updateNotification('Invalid JSON configuration', 'error');
    }
}

// Generation Functions
function generateImage() {
    const prompt = document.getElementById('prompt-input').value;
    const seedInput = document.getElementById('seed-input').value;
    const configName = document.getElementById('config-select').value;
    
    if (!prompt || !configName) {
        updateNotification('Please enter a prompt and select a template', 'warning');
        return;
    }
    
    console.log('Generating image with config:', configName, 'prompt:', prompt);
    
    // Handle seed properly - empty string or invalid input becomes null (random seed)
    let seed = null;
    if (seedInput.trim() !== '') {
        const seedNum = parseInt(seedInput);
        if (!isNaN(seedNum)) {
            seed = seedNum;
        }
    }
    
    const data = {
        config_name: configName,
        prompt: prompt,
        seed: seed
    };
    
    fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Image generated successfully', 'success');
            loadOutputs();
        } else {
            updateNotification('Failed to generate image', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to generate image:', error);
        updateNotification('Failed to generate image', 'error');
    });
}

function generateSingle(configName) {
    console.log('Generating single image with config:', configName);
    const prompt = document.getElementById('prompt-input').value;
    if (!prompt) {
        updateNotification('Please enter a prompt first', 'warning');
        return;
    }
    
    const seedInput = document.getElementById('seed-input').value;
    
    // Handle seed properly - empty string or invalid input becomes null (random seed)
    let seed = null;
    if (seedInput.trim() !== '') {
        const seedNum = parseInt(seedInput);
        if (!isNaN(seedNum)) {
            seed = seedNum;
        }
    }
    
    const data = {
        config_name: configName,
        prompt: prompt,
        seed: seed
    };
    
    fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Image generated successfully', 'success');
            loadOutputs();
        } else {
            updateNotification('Failed to generate image', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to generate image:', error);
        updateNotification('Failed to generate image', 'error');
    });
}

function startBatch(configName) {
    console.log('Starting batch with config:', configName);
    const batchSize = document.getElementById('batch-size').value;
    const numBatches = document.getElementById('num-batches').value;
    const prompt = document.getElementById('prompt-input').value;
    
    if (!prompt) {
        updateNotification('Please enter a prompt first', 'warning');
        return;
    }
    
    const data = {
        config_name: configName,
        prompt: prompt,
        batch_size: parseInt(batchSize) || 4,
        num_batches: parseInt(numBatches) || 1
    };
    
    fetch('/api/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Batch generation started', 'success');
            loadOutputs();
        } else {
            updateNotification('Failed to start batch generation', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to start batch generation:', error);
        updateNotification('Failed to start batch generation', 'error');
    });
}

function previewBatch() {
    const configName = document.getElementById('config-select').value;
    const batchSize = document.getElementById('batch-size').value;
    const numBatches = document.getElementById('num-batches').value;
    const prompt = document.getElementById('prompt-input').value;
    
    if (!prompt || !configName) {
        updateNotification('Please enter a prompt and select a template', 'warning');
        return;
    }
    
    console.log('Previewing batch with config:', configName);
    
    const data = {
        config_name: configName,
        prompt: prompt,
        batch_size: parseInt(batchSize) || 4,
        num_batches: parseInt(numBatches) || 1
    };
    
    fetch('/api/batch/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentBatchPreview = data.prompts;
            showBatchPreview(data.prompts);
        } else {
            updateNotification('Failed to preview batch', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to preview batch:', error);
        updateNotification('Failed to preview batch', 'error');
    });
}

function showBatchPreview(prompts) {
    const modal = document.getElementById('batch-preview-modal');
    const content = document.getElementById('batch-preview-content');
    
    if (!modal || !content) return;
    
    let html = '<div class="batch-preview-grid">';
    prompts.forEach((prompt, index) => {
        html += `
            <div class="preview-item">
                <div class="preview-number">${index + 1}</div>
                <div class="preview-prompt">${prompt}</div>
            </div>
        `;
    });
    html += '</div>';
    
    content.innerHTML = html;
    modal.style.display = 'block';
}

function startBatchGeneration() {
    if (!currentBatchPreview) {
        updateNotification('Please preview the batch first', 'warning');
        return;
    }
    
    const configName = document.getElementById('config-select').value;
    const data = {
        config_name: configName,
        prompts: currentBatchPreview
    };
    
    fetch('/api/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Batch generation started', 'success');
            closeModal('batch-preview-modal');
            loadOutputs();
        } else {
            updateNotification('Failed to start batch generation', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to start batch generation:', error);
        updateNotification('Failed to start batch generation', 'error');
    });
}

function confirmBatchGeneration() {
    startBatchGeneration();
}

function clearQueue() {
    console.log('Clearing queue...');
    if (confirm('Are you sure you want to clear the job queue?')) {
        fetch('/api/queue/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Queue cleared successfully', 'success');
                    updateQueueStatus({ running_jobs: 0, pending_jobs: 0, completed_jobs: 0 });
                } else {
                    updateNotification('Failed to clear queue', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to clear queue:', error);
                updateNotification('Failed to clear queue', 'error');
            });
    }
}

// Output Management
function loadOutputs() {
    fetch('/api/outputs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOutputs(data.outputs);
            } else {
                console.error('Failed to load outputs:', data.error);
            }
        })
        .catch(error => {
            console.error('Failed to load outputs:', error);
        });
}

function displayOutputs(outputs) {
    const grid = document.getElementById('outputs-grid');
    if (!grid) return;
    
    if (!outputs || outputs.length === 0) {
        grid.innerHTML = `
            <div class="text-center text-muted" style="grid-column: 1 / -1; padding: 2rem;">
                <i class="fas fa-images" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                <div>No outputs found</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem;">Generate some images to see them here</div>
            </div>
        `;
        return;
    }
    
    let html = '';
    outputs.forEach(output => {
        const imageUrl = `/outputs/images/${output.filename}`;
        const metadataUrl = `/outputs/metadata/${output.filename.replace('.png', '.json')}`;
        
        html += `
            <div class="output-card">
                <div class="output-image">
                    <img src="${imageUrl}" alt="Generated image" loading="lazy">
                </div>
                <div class="output-info">
                    <div class="output-name">${output.filename}</div>
                    <div class="output-config">${output.config_name}</div>
                    <div class="output-date">${formatDate(output.created_at)}</div>
                </div>
                <div class="output-actions">
                    <button class="btn btn-sm btn-secondary" onclick="downloadImage('${output.filename}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="viewMetadata('${output.filename}')" title="View Metadata">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteOutput('${output.filename}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
}

function refreshOutputs() {
    console.log('Refreshing outputs...');
    loadOutputs();
}

function exportOutputs() {
    console.log('Exporting outputs...');
    // Implementation for exporting outputs
    updateNotification('Export feature not yet implemented', 'info');
}

function viewLogs() {
    console.log('Viewing logs...');
    fetch('/api/logs/summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayLogs(data.logs);
            } else {
                updateNotification('Failed to load logs', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to load logs:', error);
            updateNotification('Failed to load logs', 'error');
        });
}

function displayLogs(logData) {
    const modal = document.getElementById('logs-modal');
    const content = document.getElementById('logs-content');
    
    if (!modal || !content) return;
    
    let html = '<div class="logs-container">';
    if (logData && logData.length > 0) {
        logData.forEach(log => {
            html += `
                <div class="log-entry">
                    <div class="log-timestamp">${log.timestamp}</div>
                    <div class="log-level">${log.level}</div>
                    <div class="log-message">${log.message}</div>
                </div>
            `;
        });
    } else {
        html += '<div class="text-center text-muted">No logs available</div>';
    }
    html += '</div>';
    
    content.innerHTML = html;
    modal.style.display = 'block';
}

function clearLogs() {
    console.log('Clearing logs...');
    if (confirm('Are you sure you want to clear all logs?')) {
        fetch('/api/logs/cleanup', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Logs cleared successfully', 'success');
                } else {
                    updateNotification('Failed to clear logs', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to clear logs:', error);
                updateNotification('Failed to clear logs', 'error');
            });
    }
}

// Modal Management
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}

// Utility Functions
function updateNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Live Status Modal
function openLiveStatusModal() {
    const modal = document.getElementById('live-status-modal');
    if (modal) {
        modal.style.display = 'block';
        startLiveStatusPolling();
    }
}

function closeLiveStatusModal() {
    const modal = document.getElementById('live-status-modal');
    if (modal) {
        modal.style.display = 'none';
        stopLiveStatusPolling();
    }
}

function startLiveStatusPolling() {
    fetchAndDisplayLiveStatus();
    // Poll every 2 seconds
    setInterval(fetchAndDisplayLiveStatus, 2000);
}

function stopLiveStatusPolling() {
    // Clear any polling intervals
}

function fetchAndDisplayLiveStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const content = document.getElementById('live-status-content');
            if (content) {
                content.innerHTML = `
                    <div class="status-section">
                        <h4>API Status</h4>
                        <pre>${JSON.stringify(data.api, null, 2)}</pre>
                    </div>
                    <div class="status-section">
                        <h4>Queue Status</h4>
                        <pre>${JSON.stringify(data.queue, null, 2)}</pre>
                    </div>
                    <div class="status-section">
                        <h4>Generation Status</h4>
                        <pre>${JSON.stringify(data.generation, null, 2)}</pre>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Failed to fetch live status:', error);
        });
}

// API Connection
function toggleApiConnection() {
    const btn = document.getElementById('api-connect-btn');
    if (btn && btn.textContent.includes('Connect')) {
        // Connect
        fetch('/api/connect', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Connected to API', 'success');
                    updateSystemStatus();
                } else {
                    updateNotification('Failed to connect to API', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to connect to API:', error);
                updateNotification('Failed to connect to API', 'error');
            });
    } else {
        // Disconnect
        fetch('/api/disconnect', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Disconnected from API', 'success');
                    updateSystemStatus();
                } else {
                    updateNotification('Failed to disconnect from API', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to disconnect from API:', error);
                updateNotification('Failed to disconnect from API', 'error');
            });
    }
}

function stopGeneration() {
    console.log('Stopping generation...');
    fetch('/api/generation/stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotification('Generation stopped', 'success');
                updateSystemStatus();
            } else {
                updateNotification('Failed to stop generation', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to stop generation:', error);
            updateNotification('Failed to stop generation', 'error');
        });
}

// Output actions
function downloadImage(filename) {
    console.log('Downloading image:', filename);
    const link = document.createElement('a');
    link.href = `/outputs/images/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function viewMetadata(filename) {
    console.log('Viewing metadata for:', filename);
    const metadataFile = filename.replace('.png', '.json');
    fetch(`/outputs/metadata/${metadataFile}`)
        .then(response => response.json())
        .then(data => {
            alert(JSON.stringify(data, null, 2));
        })
        .catch(error => {
            console.error('Failed to load metadata:', error);
            updateNotification('Failed to load metadata', 'error');
        });
}

function deleteOutput(filename) {
    console.log('Deleting output:', filename);
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
        fetch(`/api/outputs/delete/${filename}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateNotification('Output deleted successfully', 'success');
                    loadOutputs();
                } else {
                    updateNotification('Failed to delete output', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to delete output:', error);
                updateNotification('Failed to delete output', 'error');
            });
    }
} 