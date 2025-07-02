// Forge API Tool Dashboard JavaScript

// Global variables
let socket;
let statusUpdateInterval;
let currentBatchPreview = null;
let currentAnalysisResult = null;
let currentEditingConfig = null;
let analyzedImages = []; // Array to store multiple analyzed images
let selectedAnalysisIndex = 0; // Index of currently selected analysis
let serverInfo = {
    models: [],
    loras: [],
    vae: [],
    samplers: [],
    upscalers: []
};
let currentJob = null;
let progressInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    initializeSocket();
    initializeStatusUpdates();
    loadInitialData();
    setupEventListeners();
    loadCurrentAPIState();
    initializeImageDropZone();
    initializeResizableElements();
    initializeProgressTracking();
    initializeServerInfo();
    updateStatusIndicators();
    
    // Start periodic updates
    setInterval(updateStatusIndicators, 5000);
    setInterval(updateProgress, 1000);
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
    refreshQueue(); // Load detailed queue data
    loadSavedSettings(); // Load saved settings from localStorage
    
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
    // Template card clicks - improved event delegation
    document.addEventListener('click', function(e) {
        const templateCard = e.target.closest('.template-card');
        if (templateCard) {
            const configName = templateCard.dataset.config;
            if (configName) {
                selectTemplate(configName);
            }
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
    // Update header status
    const queueStatus = document.getElementById('queue-status');
    if (queueStatus) {
        const queueText = queueStatus.querySelector('.status-text');
        if (queueData && queueData.total_jobs !== undefined) {
            queueText.textContent = `Queue: ${queueData.total_jobs} jobs`;
        } else {
            queueText.textContent = 'Queue: 0 jobs';
        }
    }
    
    // Update compact queue display
    updateCompactQueue(queueData);
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
    fetch(`/api/configs/${configName}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                const config = data.config;
                
                // Basic
                document.getElementById('prompt-input').value = config.prompt_settings?.base_prompt || '';
                document.getElementById('negative-prompt-input').value = config.prompt_settings?.negative_prompt || '';
                document.getElementById('seed-input').value = config.generation_settings?.seed || '';
                document.getElementById('config-select').value = configName;
                
                // Image Settings
                document.getElementById('width-input').value = config.generation_settings?.width || 512;
                document.getElementById('height-input').value = config.generation_settings?.height || 512;
                document.getElementById('steps-input').value = config.generation_settings?.steps || 20;
                document.getElementById('cfg-scale-input').value = config.generation_settings?.cfg_scale || 7.0;
                document.getElementById('sampler-input').value = config.generation_settings?.sampler_name || 'Euler a';
                document.getElementById('batch-size-input').value = config.generation_settings?.batch_size || 1;
                document.getElementById('num-batches').value = config.generation_settings?.num_batches || 1;
                
                // Advanced Settings - handle boolean values properly
                const restoreFaces = config.generation_settings?.restore_faces;
                document.getElementById('restore-faces-input').value = restoreFaces === true ? 'true' : 'false';
                
                const tiling = config.generation_settings?.tiling;
                document.getElementById('tiling-input').value = tiling === true ? 'true' : 'false';
                
                document.getElementById('clip-skip-input').value = config.generation_settings?.clip_skip || 1;
                document.getElementById('denoising-strength-input').value = config.generation_settings?.denoising_strength || 0.7;
                
                // Hires Fix Settings - handle boolean values properly
                const hiresFix = config.generation_settings?.hires_fix;
                document.getElementById('hires-fix-input').value = hiresFix === true ? 'true' : 'false';
                
                document.getElementById('hires-upscaler-input').value = config.generation_settings?.hires_upscaler || 'Latent';
                document.getElementById('hires-steps-input').value = config.generation_settings?.hires_steps || 20;
                document.getElementById('hires-denoising-input').value = config.generation_settings?.hires_denoising || 0.7;
                
                updateNotification('Template loaded successfully!', 'success');
            } else {
                updateNotification('Failed to load template: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error loading template:', error);
            updateNotification('Error loading template: ' + error.message, 'error');
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
    fetch(`/api/configs/${configName}/settings`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                updateNotification(`Failed to load config: ${data.error}`, 'error');
                return;
            }
            
            loadConfigIntoEditor(data.settings);
            openModal('config-editor-modal');
        })
        .catch(error => {
            console.error('Error loading config:', error);
            updateNotification('Failed to load config', 'error');
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
    if (modal) {
        modal.style.display = 'none';
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
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

function loadCurrentAPIState() {
    fetch('/api/status/api')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                fetchServerInfo();
            }
        })
        .catch(error => {
            console.error('Failed to load current API state:', error);
        });
}

// Image Analysis and Config Management
function initializeImageDropZone() {
    const dropZone = document.getElementById('image-drop-zone');
    const fileInput = document.getElementById('image-file-input');
    
    if (!dropZone || !fileInput) return;
    
    // Click to select file
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleImageFile(file);
        }
    });
    
    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageFile(files[0]);
        }
    });
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        updateNotification('Please select an image file', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const imageData = e.target.result;
        analyzeImage(imageData);
    };
    reader.readAsDataURL(file);
}

function setButtonLoading(button, loading = true) {
    if (!button) return;
    
    if (loading) {
        button.classList.add('loading');
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    } else {
        button.classList.remove('loading');
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

// Progress Tracking
function initializeProgressTracking() {
    // Initialize progress section
    const progressSection = document.getElementById('progress-section');
    if (progressSection) {
        progressSection.style.display = 'none';
    }
}

function updateProgress() {
    if (!currentJob) return;
    
    fetch('/api/queue/jobs/' + currentJob.id)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateProgressDisplay(data.job);
            }
        })
        .catch(error => {
            console.error('Error updating progress:', error);
        });
}

function updateProgressDisplay(job) {
    const progressSection = document.getElementById('progress-section');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressConfig = document.getElementById('progress-config');
    const progressTime = document.getElementById('progress-time');
    const progressEta = document.getElementById('progress-eta');
    
    if (!progressSection || !job) return;
    
    const completed = job.completed || 0;
    const total = job.total || 1;
    const percentage = Math.round((completed / total) * 100);
    
    // Show progress section
    progressSection.style.display = 'block';
    
    // Update progress bar
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    // Update text
    if (progressText) {
        progressText.textContent = `${completed} of ${total} images`;
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${percentage}%`;
    }
    
    if (progressConfig) {
        progressConfig.textContent = job.config_name || 'Unknown Config';
    }
    
    // Update time info
    if (job.start_time) {
        const elapsed = Math.floor((Date.now() - new Date(job.start_time)) / 1000);
        if (progressTime) {
            progressTime.textContent = `Elapsed: ${formatTime(elapsed)}`;
        }
        
        // Calculate ETA
        if (completed > 0 && elapsed > 0) {
            const rate = completed / elapsed;
            const remaining = total - completed;
            const eta = Math.floor(remaining / rate);
            if (progressEta) {
                progressEta.textContent = `ETA: ${formatTime(eta)}`;
            }
        }
    }
    
    // Hide progress when complete
    if (completed >= total) {
        setTimeout(() => {
            progressSection.style.display = 'none';
            currentJob = null;
        }, 3000);
    }
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}m ${secs}s`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
}

// Server Info Management
function initializeServerInfo() {
    // Get server info on connection
    fetch('/api/status/api')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                fetchServerInfo();
            }
        })
        .catch(error => {
            console.error('Error checking API status:', error);
        });
}

function fetchServerInfo() {
    setButtonLoading(document.getElementById('api-connect-btn'), true);
    
    Promise.all([
        fetch('/api/models').then(r => r.json()),
        fetch('/api/samplers').then(r => r.json()),
        fetch('/api/options').then(r => r.json())
    ])
    .then(([modelsData, samplersData, optionsData]) => {
        if (modelsData.success) {
            serverInfo.models = modelsData.models || [];
        }
        if (samplersData.success) {
            serverInfo.samplers = samplersData.samplers || [];
        }
        if (optionsData.success) {
            serverInfo.vae = optionsData.vae || [];
            serverInfo.upscalers = optionsData.upscalers || [];
        }
        
        updateModelCompatibility();
        setButtonLoading(document.getElementById('api-connect-btn'), false);
    })
    .catch(error => {
        console.error('Error fetching server info:', error);
        setButtonLoading(document.getElementById('api-connect-btn'), false);
    });
}

function updateModelCompatibility() {
    // Check current config against available models
    const configSelect = document.getElementById('config-select');
    if (!configSelect || !configSelect.value) return;
    
    const configName = configSelect.value;
    fetch(`/api/configs/${configName}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                checkConfigCompatibility(data.config);
            }
        })
        .catch(error => {
            console.error('Error checking config compatibility:', error);
        });
}

function checkConfigCompatibility(config) {
    const warnings = [];
    
    // Check model
    const modelName = config.model_settings?.checkpoint;
    if (modelName && !serverInfo.models.some(m => m.title === modelName)) {
        warnings.push(`Model "${modelName}" not available on server`);
    }
    
    // Check VAE
    const vaeName = config.model_settings?.vae;
    if (vaeName && !serverInfo.vae.some(v => v.title === vaeName)) {
        warnings.push(`VAE "${vaeName}" not available on server`);
    }
    
    // Display warnings
    displayModelWarnings(warnings);
}

function displayModelWarnings(warnings) {
    // Remove existing warnings
    const existingWarnings = document.querySelectorAll('.model-warning');
    existingWarnings.forEach(w => w.remove());
    
    // Add new warnings
    const settingsSection = document.querySelector('.generation-settings');
    if (settingsSection && warnings.length > 0) {
        warnings.forEach(warning => {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'model-warning';
            warningDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>${warning}</span>
            `;
            settingsSection.insertBefore(warningDiv, settingsSection.firstChild);
        });
    }
}

// Enhanced Image Analysis
function analyzeImage(imageData) {
    setButtonLoading(document.querySelector('.image-analysis-dropzone'), true);
    updateNotification('Analyzing image...', 'info');
    
    fetch('/api/analyze-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_data: imageData
        })
    })
    .then(response => response.json())
    .then(data => {
        setButtonLoading(document.querySelector('.image-analysis-dropzone'), false);
        
        if (data.success) {
            displayAnalysisResults(data.analysis);
            updateNotification('Image analyzed successfully!', 'success');
        } else {
            updateNotification(data.error || 'Analysis failed', 'error');
        }
    })
    .catch(error => {
        setButtonLoading(document.querySelector('.image-analysis-dropzone'), false);
        updateNotification('Analysis failed: ' + error.message, 'error');
    });
}

function displayAnalysisResults(analysis) {
    // Create analysis results display
    const resultsDisplay = document.createElement('div');
    resultsDisplay.className = 'analysis-results-display';
    resultsDisplay.innerHTML = `
        <div class="analysis-summary">
            <img src="${analysis.image_data}" alt="Analyzed Image" class="analysis-thumbnail">
            <div class="analysis-summary-info">
                <h4>Analysis Complete</h4>
                <p><strong>Dimensions:</strong> ${analysis.width} × ${analysis.height}</p>
                <p><strong>Model:</strong> ${analysis.parameters?.model || 'Unknown'}</p>
                <p><strong>Sampler:</strong> ${analysis.parameters?.sampler || 'Unknown'}</p>
            </div>
        </div>
        <div class="analysis-actions">
            <button class="analysis-action-btn success" onclick="populateSettingsFromAnalysis()">
                <i class="fas fa-magic"></i> Populate Settings
            </button>
            <button class="analysis-action-btn primary" onclick="createConfigFromAnalysis()">
                <i class="fas fa-save"></i> Create Config
            </button>
            <button class="analysis-action-btn secondary" onclick="clearAnalysisResults()">
                <i class="fas fa-times"></i> Clear
            </button>
        </div>
    `;
    
    // Insert after dropzone
    const dropzone = document.getElementById('image-analysis-dropzone');
    if (dropzone && dropzone.parentNode) {
        dropzone.parentNode.insertBefore(resultsDisplay, dropzone.nextSibling);
        
        // Show with animation
        setTimeout(() => {
            resultsDisplay.classList.add('show');
        }, 10);
    }
    
    // Store analysis data
    analyzedImages.push(analysis);
    selectedAnalysisIndex = analyzedImages.length - 1;
}

function clearAnalysisResults() {
    const resultsDisplay = document.querySelector('.analysis-results-display');
    if (resultsDisplay) {
        resultsDisplay.remove();
    }
    analyzedImages = [];
    selectedAnalysisIndex = -1;
}

// Enhanced populate settings function
function populateSettingsFromAnalysis() {
    if (analyzedImages.length === 0 || selectedAnalysisIndex < 0) {
        updateNotification('No analysis data available', 'error');
        return;
    }
    
    const analysis = analyzedImages[selectedAnalysisIndex];
    const params = analysis.parameters || {};
    
    // Populate all settings
    populateField('prompt-input', params.prompt || '');
    populateField('negative-prompt-input', params.negative_prompt || '');
    populateField('seed-input', params.seed || '');
    populateField('width-input', params.width || 512);
    populateField('height-input', params.height || 512);
    populateField('steps-input', params.steps || 20);
    populateField('cfg-scale-input', params.cfg_scale || 7.0);
    populateField('sampler-input', params.sampler || 'Euler a');
    populateField('batch-size-input', params.batch_size || 1);
    populateField('num-batches', params.num_batches || 1);
    populateField('denoising-strength-input', params.denoising_strength || 0.7);
    populateField('clip-skip-input', params.clip_skip || 1);
    populateField('restore-faces-input', params.restore_faces ? 'Yes' : 'No');
    populateField('tiling-input', params.tiling ? 'Yes' : 'No');
    populateField('hires-fix-input', params.hires_fix ? 'Yes' : 'No');
    populateField('hires-upscaler-input', params.hires_upscaler || 'Latent');
    populateField('hires-steps-input', params.hires_steps || 20);
    populateField('hires-denoising-input', params.hires_denoising || 0.7);
    
    updateNotification('Settings populated from analysis!', 'success');
    
    // Scroll to settings
    const settingsSection = document.querySelector('.generation-settings');
    if (settingsSection) {
        settingsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function populateField(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.value = value;
        // Trigger change event for any listeners
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

function createConfigFromAnalysis() {
    if (analyzedImages.length === 0 || selectedAnalysisIndex < 0) {
        updateNotification('No analysis data available', 'error');
        return;
    }
    
    const analysis = analyzedImages[selectedAnalysisIndex];
    const params = analysis.parameters || {};
    
    // Create config data
    const configData = {
        name: `Config from ${analysis.filename || 'Image'}`,
        description: `Generated from image analysis on ${new Date().toLocaleDateString()}`,
        model_type: 'sd',
        prompt_settings: {
            base_prompt: params.prompt || '',
            negative_prompt: params.negative_prompt || ''
        },
        generation_settings: {
            width: params.width || 512,
            height: params.height || 512,
            steps: params.steps || 20,
            cfg_scale: params.cfg_scale || 7.0,
            sampler: params.sampler || 'Euler a',
            batch_size: params.batch_size || 1,
            num_batches: params.num_batches || 1,
            denoising_strength: params.denoising_strength || 0.7,
            clip_skip: params.clip_skip || 1,
            restore_faces: params.restore_faces || false,
            tiling: params.tiling || false,
            hires_fix: params.hires_fix || false,
            hires_upscaler: params.hires_upscaler || 'Latent',
            hires_steps: params.hires_steps || 20,
            hires_denoising: params.hires_denoising || 0.7
        },
        model_settings: {
            checkpoint: params.model || '',
            vae: params.vae || ''
        },
        thumbnail: analysis.image_data // Add thumbnail
    };
    
    // Save config
    fetch('/api/configs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Config created successfully!', 'success');
            // Refresh templates
            location.reload();
        } else {
            updateNotification(data.error || 'Failed to create config', 'error');
        }
    })
    .catch(error => {
        updateNotification('Failed to create config: ' + error.message, 'error');
    });
}

// Enhanced generation functions with better feedback
function generateSingle(configName) {
    const button = event.target.closest('.btn');
    setButtonLoading(button, true);
    
    // Get current settings
    const settings = getCurrentSettings();
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            config_name: configName,
            ...settings
        })
    })
    .then(response => response.json())
    .then(data => {
        setButtonLoading(button, false);
        
        if (data.success) {
            updateNotification('Image generated successfully!', 'success');
            // Update outputs display
            updateOutputsDisplay();
        } else {
            updateNotification(data.error || 'Generation failed', 'error');
        }
    })
    .catch(error => {
        setButtonLoading(button, false);
        updateNotification('Generation failed: ' + error.message, 'error');
    });
}

function startBatch(configName) {
    const button = event.target.closest('.btn');
    setButtonLoading(button, true);
    
    // Get current settings
    const settings = getCurrentSettings();
    
    fetch('/api/batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            config_name: configName,
            ...settings
        })
    })
    .then(response => response.json())
    .then(data => {
        setButtonLoading(button, false);
        
        if (data.success) {
            currentJob = { id: data.job_id, config_name: configName };
            updateNotification(`Batch job started: ${data.total_images} images`, 'success');
            updateProgress();
        } else {
            updateNotification(data.error || 'Batch failed', 'error');
        }
    })
    .catch(error => {
        setButtonLoading(button, false);
        updateNotification('Batch failed: ' + error.message, 'error');
    });
}

function getCurrentSettings() {
    return {
        prompt: document.getElementById('prompt-input')?.value || '',
        negative_prompt: document.getElementById('negative-prompt-input')?.value || '',
        seed: document.getElementById('seed-input')?.value || '',
        width: parseInt(document.getElementById('width-input')?.value) || 512,
        height: parseInt(document.getElementById('height-input')?.value) || 512,
        steps: parseInt(document.getElementById('steps-input')?.value) || 20,
        cfg_scale: parseFloat(document.getElementById('cfg-scale-input')?.value) || 7.0,
        sampler: document.getElementById('sampler-input')?.value || 'Euler a',
        batch_size: parseInt(document.getElementById('batch-size-input')?.value) || 1,
        num_batches: parseInt(document.getElementById('num-batches')?.value) || 1
    };
}

function updateOutputsDisplay() {
    // Refresh outputs section
    fetch('/api/outputs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update outputs display (implement based on your UI)
                console.log('Outputs updated:', data.outputs);
            }
        })
        .catch(error => {
            console.error('Error updating outputs:', error);
        });
}

// ============================================================================
// SETTINGS MODAL FUNCTIONALITY
// ============================================================================

// Open settings modal
function openSettingsModal() {
    openModal('settings-modal');
    loadSettingsData();
}

// Load settings data
function loadSettingsData() {
    loadApiSettings();
    loadOutputSettings();
    loadLogSettings();
    loadAdvancedSettings();
    updateLogStats();
    updateCacheStats();
}

// Switch settings tabs
function switchSettingsTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.settings-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-settings-tab`).classList.add('active');
    
    // Add active class to selected tab button
    event.target.classList.add('active');
}

// API Settings
function loadApiSettings() {
    fetch('/api/settings/api')
        .then(response => response.json())
        .then(data => {
            // Set API type
            if (data.api_type === 'rundiffusion') {
                document.getElementById('api-rundiffusion').checked = true;
                document.getElementById('rundiffusion-api-settings').style.display = 'block';
                document.getElementById('local-api-settings').style.display = 'none';
            } else {
                document.getElementById('api-local').checked = true;
                document.getElementById('local-api-settings').style.display = 'block';
                document.getElementById('rundiffusion-api-settings').style.display = 'none';
            }
            
            // Load RunDiffusion settings
            if (data.rundiffusion_config) {
                document.getElementById('rundiffusion-url-settings').value = data.rundiffusion_config.url || '';
                document.getElementById('rundiffusion-username-settings').value = data.rundiffusion_config.username || '';
                document.getElementById('rundiffusion-password-settings').value = data.rundiffusion_config.password || '';
                document.getElementById('rundiffusion-timeout-settings').value = data.rundiffusion_config.timeout || 60;
            }
            
            // Load local API settings
            if (data.local_config) {
                document.getElementById('local-api-url').value = data.local_config.url || 'http://localhost:3000';
                document.getElementById('local-api-timeout').value = data.local_config.timeout || 30;
            }
        })
        .catch(error => {
            console.error('Failed to load API settings:', error);
            updateNotification('Failed to load API settings', 'error');
        });
}

function saveApiSettings() {
    const apiType = document.querySelector('input[name="api-type"]:checked').value;
    const settings = {
        api_type: apiType
    };
    
    if (apiType === 'rundiffusion') {
        settings.rundiffusion_config = {
            url: document.getElementById('rundiffusion-url-settings').value,
            username: document.getElementById('rundiffusion-username-settings').value,
            password: document.getElementById('rundiffusion-password-settings').value,
            timeout: parseInt(document.getElementById('rundiffusion-timeout-settings').value)
        };
    } else {
        settings.local_config = {
            url: document.getElementById('local-api-url').value,
            timeout: parseInt(document.getElementById('local-api-timeout').value)
        };
    }
    
    fetch('/api/settings/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('API settings saved successfully', 'success');
            loadCurrentAPIState(); // Reload current API state
        } else {
            updateNotification('Failed to save API settings', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to save API settings:', error);
        updateNotification('Failed to save API settings', 'error');
    });
}

function testApiConnection() {
    const apiType = document.querySelector('input[name="api-type"]:checked').value;
    const testButton = event.target;
    const originalText = testButton.innerHTML;
    
    setButtonLoading(testButton, true);
    
    fetch('/api/settings/test-connection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ api_type: apiType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Connection test successful', 'success');
        } else {
            updateNotification(`Connection test failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Connection test failed:', error);
        updateNotification('Connection test failed', 'error');
    })
    .finally(() => {
        setButtonLoading(testButton, false);
        testButton.innerHTML = originalText;
    });
}

// Output Settings
function loadOutputSettings() {
    fetch('/api/settings/output')
        .then(response => response.json())
        .then(data => {
            document.getElementById('output-base-directory').value = data.base_directory || '';
            document.getElementById('output-naming-pattern').value = data.naming_pattern || 'timestamp';
            document.getElementById('custom-naming-pattern').value = data.custom_pattern || '';
            document.getElementById('auto-open-outputs').value = data.auto_open_outputs ? 'true' : 'false';
            document.getElementById('max-outputs-display').value = data.max_outputs_display || 50;
            
            // Show/hide custom pattern input
            toggleCustomPatternInput();
        })
        .catch(error => {
            console.error('Failed to load output settings:', error);
        });
}

function saveOutputSettings() {
    const settings = {
        base_directory: document.getElementById('output-base-directory').value,
        naming_pattern: document.getElementById('output-naming-pattern').value,
        custom_pattern: document.getElementById('custom-naming-pattern').value,
        auto_open_outputs: document.getElementById('auto-open-outputs').value === 'true',
        max_outputs_display: parseInt(document.getElementById('max-outputs-display').value)
    };
    
    fetch('/api/settings/output', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Output settings saved successfully', 'success');
        } else {
            updateNotification('Failed to save output settings', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to save output settings:', error);
        updateNotification('Failed to save output settings', 'error');
    });
}

function selectOutputDirectory() {
    // This would typically open a file dialog
    // For now, we'll use a simple input dialog
    const directory = prompt('Enter output directory path:');
    if (directory) {
        document.getElementById('output-base-directory').value = directory;
    }
}

function toggleCustomPatternInput() {
    const pattern = document.getElementById('output-naming-pattern').value;
    const customGroup = document.getElementById('custom-pattern-group');
    
    if (pattern === 'custom') {
        customGroup.style.display = 'block';
    } else {
        customGroup.style.display = 'none';
    }
}

// Log Settings
function loadLogSettings() {
    fetch('/api/settings/logs')
        .then(response => response.json())
        .then(data => {
            document.getElementById('log-retention-days').value = data.retention_days || 30;
            document.getElementById('auto-cleanup-logs').value = data.auto_cleanup ? 'true' : 'false';
        })
        .catch(error => {
            console.error('Failed to load log settings:', error);
        });
}

function saveLogSettings() {
    const settings = {
        retention_days: parseInt(document.getElementById('log-retention-days').value),
        auto_cleanup: document.getElementById('auto-cleanup-logs').value === 'true'
    };
    
    fetch('/api/settings/logs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Log settings saved successfully', 'success');
        } else {
            updateNotification('Failed to save log settings', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to save log settings:', error);
        updateNotification('Failed to save log settings', 'error');
    });
}

function updateLogStats() {
    fetch('/api/logs/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('app-logs-size').textContent = formatBytes(data.app_logs_size || 0);
            document.getElementById('error-logs-size').textContent = formatBytes(data.error_logs_size || 0);
            document.getElementById('perf-logs-size').textContent = formatBytes(data.perf_logs_size || 0);
        })
        .catch(error => {
            console.error('Failed to load log stats:', error);
        });
}

function updateCacheStats() {
    fetch('/api/cache/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cache-size').textContent = formatBytes(data.size || 0);
            document.getElementById('cache-items').textContent = data.items || 0;
        })
        .catch(error => {
            console.error('Failed to load cache stats:', error);
        });
}

function clearCache() {
    if (confirm('Are you sure you want to clear the cache? This action cannot be undone.')) {
        fetch('/api/cache/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotification('Cache cleared successfully', 'success');
                updateCacheStats();
            } else {
                updateNotification('Failed to clear cache', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to clear cache:', error);
            updateNotification('Failed to clear cache', 'error');
        });
    }
}

// Advanced Settings
function loadAdvancedSettings() {
    fetch('/api/settings/advanced')
        .then(response => response.json())
        .then(data => {
            document.getElementById('max-concurrent-jobs').value = data.max_concurrent_jobs || 2;
            document.getElementById('job-timeout').value = data.job_timeout || 30;
            document.getElementById('auto-refresh-interval').value = data.auto_refresh_interval || 5;
            document.getElementById('enable-cors').value = data.enable_cors ? 'true' : 'false';
            document.getElementById('max-upload-size').value = data.max_upload_size || 10;
            document.getElementById('theme').value = data.theme || 'light';
            document.getElementById('sidebar-width').value = data.sidebar_width || 300;
        })
        .catch(error => {
            console.error('Failed to load advanced settings:', error);
        });
}

function saveAdvancedSettings() {
    const settings = {
        max_concurrent_jobs: parseInt(document.getElementById('max-concurrent-jobs').value),
        job_timeout: parseInt(document.getElementById('job-timeout').value),
        auto_refresh_interval: parseInt(document.getElementById('auto-refresh-interval').value),
        enable_cors: document.getElementById('enable-cors').value === 'true',
        max_upload_size: parseInt(document.getElementById('max-upload-size').value),
        theme: document.getElementById('theme').value,
        sidebar_width: parseInt(document.getElementById('sidebar-width').value)
    };
    
    fetch('/api/settings/advanced', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Advanced settings saved successfully', 'success');
            applyTheme(settings.theme);
        } else {
            updateNotification('Failed to save advanced settings', 'error');
        }
    })
    .catch(error => {
        console.error('Failed to save advanced settings:', error);
        updateNotification('Failed to save advanced settings', 'error');
    });
}

function applyTheme(theme) {
    // Apply theme changes
    document.body.className = `theme-${theme}`;
    localStorage.setItem('theme', theme);
}

// Save all settings
function saveAllSettings() {
    saveApiSettings();
    saveOutputSettings();
    saveLogSettings();
    saveAdvancedSettings();
    
    updateNotification('All settings saved successfully', 'success');
}

// Logs Modal
function switchLogsTab(tabName) {
    // Hide all log content
    document.querySelectorAll('.log-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.logs-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected content
    document.getElementById(`${tabName}-logs`).classList.add('active');
    
    // Add active class to selected tab button
    event.target.classList.add('active');
    
    // Load logs for the selected tab
    loadLogs(tabName);
}

function loadLogs(logType) {
    fetch(`/api/logs/${logType}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById(`${logType}-logs-content`).textContent = data;
        })
        .catch(error => {
            console.error(`Failed to load ${logType} logs:`, error);
            document.getElementById(`${logType}-logs-content`).textContent = `Failed to load logs: ${error.message}`;
        });
}

function refreshLogs() {
    const activeTab = document.querySelector('.logs-tabs .tab-btn.active');
    if (activeTab) {
        const tabName = activeTab.textContent.toLowerCase();
        loadLogs(tabName);
    }
}

function downloadLogs() {
    fetch('/api/logs/download')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `forge-api-logs-${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Failed to download logs:', error);
            updateNotification('Failed to download logs', 'error');
        });
}

// Event listeners for settings
document.addEventListener('DOMContentLoaded', function() {
    // API type radio button change
    document.querySelectorAll('input[name="api-type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const apiType = this.value;
            if (apiType === 'rundiffusion') {
                document.getElementById('rundiffusion-api-settings').style.display = 'block';
                document.getElementById('local-api-settings').style.display = 'none';
            } else {
                document.getElementById('local-api-settings').style.display = 'block';
                document.getElementById('rundiffusion-api-settings').style.display = 'none';
            }
        });
    });
    
    // Output naming pattern change
    const namingPattern = document.getElementById('output-naming-pattern');
    if (namingPattern) {
        namingPattern.addEventListener('change', toggleCustomPatternInput);
    }
});

// Global JS error logging
window.onerror = function(message, source, lineno, colno, error) {
  fetch('/api/log-js-error', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message, source, lineno, colno, stack: error && error.stack
    })
  });
  if (typeof updateNotification === 'function') {
    updateNotification('A JavaScript error occurred: ' + message, 'error');
  }
};
window.addEventListener('unhandledrejection', function(event) {
  fetch('/api/log-js-error', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: event.reason && event.reason.message,
      stack: event.reason && event.reason.stack
    })
  });
  if (typeof updateNotification === 'function') {
    updateNotification('A JavaScript promise error occurred: ' + (event.reason && event.reason.message), 'error');
  }
});