// Forge API Tool Dashboard JavaScript

// Global variables
let socket;
let statusUpdateInterval;
let currentBatchPreview = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    initializeSocket();
    initializeStatusUpdates();
    loadInitialData();
    setupEventListeners();
    loadCurrentAPIState();
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
    
    // Auto-load the first available template
    setTimeout(() => {
        const configSelect = document.getElementById('config-select');
        if (configSelect && configSelect.options.length > 1) { // More than just the placeholder
            const firstConfig = configSelect.options[1].value; // Skip the placeholder option
            if (firstConfig) {
                selectTemplate(firstConfig);
            }
        }
    }, 500); // Small delay to ensure DOM is ready
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
    
    // Config select dropdown change
    const configSelect = document.getElementById('config-select');
    if (configSelect) {
        configSelect.addEventListener('change', function(e) {
            const selectedConfig = e.target.value;
            if (selectedConfig) {
                selectTemplate(selectedConfig);
            }
        });
    }
    
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
    
    // Fetch the template's base prompt and populate the prompt input
    fetch(`/api/configs/${configName}`)
        .then(response => response.json())
        .then(data => {
            const promptInput = document.getElementById('prompt-input');
            if (promptInput && data.prompt_settings && data.prompt_settings.base_prompt) {
                promptInput.value = data.prompt_settings.base_prompt;
                console.log('Populated prompt with template base prompt:', data.prompt_settings.base_prompt);
                
                // Show helpful notification
                const hasWildcards = data.prompt_settings.base_prompt.includes('__');
                if (hasWildcards) {
                    updateNotification(`Template "${configName}" loaded with wildcards. Edit the prompt to customize or generate as-is.`, 'info');
                } else {
                    updateNotification(`Template "${configName}" loaded. You can edit the prompt or generate as-is.`, 'info');
                }
            }
        })
        .catch(error => {
            console.error('Failed to fetch template details:', error);
            updateNotification(`Failed to load template "${configName}" details`, 'error');
        });
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
    
    if (!configName) {
        updateNotification('Please select a template', 'warning');
        return;
    }
    
    console.log('Previewing batch with config:', configName);
    
    const data = {
        config_name: configName,
        batch_size: parseInt(batchSize) || 4,
        num_batches: parseInt(numBatches) || 1
    };
    
    // Only include prompt if user provided one
    if (prompt && prompt.trim()) {
        data.prompt = prompt;
    }
    
    fetch('/api/batch/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentBatchPreview = data.prompts;
            showBatchPreview(data.prompts, data);
        } else {
            updateNotification('Failed to preview batch', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to preview batch:', error);
        updateNotification('Failed to preview batch', 'error');
    });
}

function showBatchPreview(prompts, previewData) {
    const modal = document.getElementById('batch-preview-modal');
    const content = document.getElementById('batch-preview-content');
    
    if (!modal || !content) return;
    
    // Add preview information header
    let html = '<div class="preview-info">';
    if (previewData.template_used) {
        html += '<div class="preview-notice"><i class="fas fa-info-circle"></i> Using template\'s base prompt</div>';
    }
    if (previewData.wildcards_resolved) {
        html += '<div class="preview-notice"><i class="fas fa-magic"></i> Wildcards automatically resolved</div>';
    }
    html += '</div>';
    
    html += '<div class="batch-preview-grid">';
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
        // Use the new date-based path structure
        const imageUrl = `/outputs/${output.date}/${output.filename}`;
        
        html += `
            <div class="output-card">
                <div class="output-image">
                    <img src="${imageUrl}" alt="Generated image" loading="lazy">
                </div>
                <div class="output-info">
                    <div class="output-name">${output.filename}</div>
                    <div class="output-config">${output.config_name}</div>
                    <div class="output-date">${formatDate(output.created_at)}</div>
                    <div class="output-details">
                        <small>Seed: ${output.seed} | Steps: ${output.steps} | ${output.width}x${output.height}</small>
                    </div>
                </div>
                <div class="output-actions">
                    <button class="btn btn-sm btn-secondary" onclick="downloadImage('${output.date}', '${output.filename}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="viewMetadata('${output.date}', '${output.filename}')" title="View Metadata">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteOutput('${output.date}', '${output.filename}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
}

function loadOutputs(date = null, config = null) {
    let url = '/api/outputs';
    const params = new URLSearchParams();
    
    if (date) {
        params.append('date', date);
    }
    if (config) {
        params.append('config', config);
    }
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOutputs(data.outputs);
                updateOutputStats(data.outputs.length);
            } else {
                console.error('Failed to load outputs:', data.error);
                updateNotification('Failed to load outputs', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading outputs:', error);
            updateNotification('Error loading outputs', 'error');
        });
}

function loadOutputDates() {
    fetch('/api/outputs/dates')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDateSelector(data.dates);
            }
        })
        .catch(error => {
            console.error('Error loading output dates:', error);
        });
}

function updateDateSelector(dates) {
    const dateSelect = document.getElementById('output-date-select');
    if (!dateSelect) return;
    
    // Clear existing options
    dateSelect.innerHTML = '<option value="">Today</option>';
    
    // Add date options
    dates.forEach(date => {
        const option = document.createElement('option');
        option.value = date;
        option.textContent = formatDate(date);
        dateSelect.appendChild(option);
    });
}

function downloadImage(date, filename) {
    const imageUrl = `/outputs/${date}/${filename}`;
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function viewMetadata(date, filename) {
    console.log('Viewing metadata for:', date, filename);
    fetch(`/api/outputs/metadata/${date}/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMetadataModal(data.metadata);
            } else {
                updateNotification('Failed to load metadata', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to load metadata:', error);
            updateNotification('Failed to load metadata', 'error');
        });
}

function showMetadataModal(metadata) {
    // Create a simple modal to display metadata
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 8px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        position: relative;
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
    `;
    closeBtn.onclick = () => document.body.removeChild(modal);
    
    const title = document.createElement('h3');
    title.textContent = 'Image Metadata';
    title.style.marginBottom = '1rem';
    
    const metadataText = document.createElement('pre');
    metadataText.textContent = JSON.stringify(metadata, null, 2);
    metadataText.style.cssText = `
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 4px;
        font-size: 12px;
        overflow-x: auto;
    `;
    
    content.appendChild(closeBtn);
    content.appendChild(title);
    content.appendChild(metadataText);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close on background click
    modal.onclick = (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

function deleteOutput(date, filename) {
    if (!confirm('Are you sure you want to delete this image?')) {
        return;
    }
    
    fetch(`/api/outputs/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: date,
            filename: filename
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Image deleted successfully', 'success');
            loadOutputs(); // Reload outputs
        } else {
            updateNotification('Failed to delete image', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting output:', error);
        updateNotification('Error deleting image', 'error');
    });
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

// RunDiffusion API Configuration Functions
function toggleRunDiffusion() {
    const toggle = document.getElementById('rundiffusion-toggle');
    const config = document.getElementById('rundiffusion-config');
    
    if (toggle.checked) {
        config.style.display = 'block';
        // Load saved configuration if available
        loadRunDiffusionConfig();
    } else {
        config.style.display = 'none';
        // Switch back to local API
        switchToLocalAPI();
    }
}

function loadRunDiffusionConfig() {
    fetch('/api/rundiffusion/config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                document.getElementById('rundiffusion-url').value = data.config.url || 'https://your-instance.rundiffusion.com';
                document.getElementById('rundiffusion-username').value = data.config.username || 'rduser';
                document.getElementById('rundiffusion-password').value = data.config.password || 'rdpass';
                updateNotification('RunDiffusion configuration loaded', 'success');
            }
        })
        .catch(error => {
            console.error('Failed to load RunDiffusion config:', error);
            // Use default values if loading fails
        });
}

function saveRunDiffusionConfig() {
    const config = {
        url: document.getElementById('rundiffusion-url').value.trim(),
        username: document.getElementById('rundiffusion-username').value.trim(),
        password: document.getElementById('rundiffusion-password').value.trim()
    };
    
    // Validate configuration
    if (!config.url || config.url === 'https://your-instance.rundiffusion.com') {
        updateNotification('Please enter a valid RunDiffusion server URL', 'error');
        return;
    }
    
    if (!config.username || !config.password) {
        updateNotification('Please enter both username and password', 'error');
        return;
    }
    
    fetch('/api/rundiffusion/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Switched to RunDiffusion API successfully', 'success');
            // Test connection after saving
            testRunDiffusionConnection();
            // Update system status
            updateSystemStatus();
        } else {
            updateNotification('Failed to switch to RunDiffusion: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error switching to RunDiffusion:', error);
        updateNotification('Failed to switch to RunDiffusion', 'error');
    });
}

function testRunDiffusionConnection() {
    const url = document.getElementById('rundiffusion-url').value.trim();
    const username = document.getElementById('rundiffusion-username').value.trim();
    const password = document.getElementById('rundiffusion-password').value.trim();
    
    if (!url || !username || !password) {
        updateNotification('Please fill in all RunDiffusion configuration fields', 'error');
        return;
    }
    
    // Show testing status
    const configDiv = document.getElementById('rundiffusion-config');
    let statusDiv = configDiv.querySelector('.api-status');
    if (!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.className = 'api-status testing';
        configDiv.appendChild(statusDiv);
    }
    statusDiv.className = 'api-status testing';
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing connection...';
    
    fetch('/api/rundiffusion/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url, username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusDiv.className = 'api-status connected';
            statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Connection successful!';
            updateNotification('RunDiffusion connection test successful', 'success');
        } else {
            statusDiv.className = 'api-status disconnected';
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Connection failed: ' + data.error;
            updateNotification('RunDiffusion connection test failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error testing RunDiffusion connection:', error);
        statusDiv.className = 'api-status disconnected';
        statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> Connection failed: Network error';
        updateNotification('RunDiffusion connection test failed', 'error');
    });
}

function switchToLocalAPI() {
    fetch('/api/rundiffusion/disable', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Switched to local API', 'success');
            // Remove status indicator if it exists
            const configDiv = document.getElementById('rundiffusion-config');
            const statusDiv = configDiv.querySelector('.api-status');
            if (statusDiv) {
                statusDiv.remove();
            }
            // Update system status
            updateSystemStatus();
        } else {
            updateNotification('Failed to switch to local API: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error switching to local API:', error);
        updateNotification('Failed to switch to local API', 'error');
    });
}

function loadCurrentAPIState() {
    fetch('/api/status/current-api')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const toggle = document.getElementById('rundiffusion-toggle');
                const config = document.getElementById('rundiffusion-config');
                
                if (data.api_info.type === 'rundiffusion') {
                    // Enable RunDiffusion
                    toggle.checked = true;
                    config.style.display = 'block';
                    
                    // Load the configuration
                    if (data.api_info.url) {
                        document.getElementById('rundiffusion-url').value = data.api_info.url;
                    }
                    if (data.api_info.username) {
                        document.getElementById('rundiffusion-username').value = data.api_info.username;
                    }
                    
                    // Show connection status
                    let statusDiv = config.querySelector('.api-status');
                    if (!statusDiv) {
                        statusDiv = document.createElement('div');
                        statusDiv.className = 'api-status';
                        config.appendChild(statusDiv);
                    }
                    
                    if (data.connected) {
                        statusDiv.className = 'api-status connected';
                        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Connected to RunDiffusion';
                    } else {
                        statusDiv.className = 'api-status disconnected';
                        statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> RunDiffusion not connected';
                    }
                } else {
                    // Use local API
                    toggle.checked = false;
                    config.style.display = 'none';
                }
                
                console.log('Current API state loaded:', data.api_info);
            }
        })
        .catch(error => {
            console.error('Failed to load current API state:', error);
        });
} 