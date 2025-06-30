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
    initializeDropZone();
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
                
                // Advanced Settings
                document.getElementById('restore-faces-input').value = config.generation_settings?.restore_faces || false;
                document.getElementById('tiling-input').value = config.generation_settings?.tiling || false;
                document.getElementById('clip-skip-input').value = config.generation_settings?.clip_skip || 1;
                document.getElementById('denoising-strength-input').value = config.generation_settings?.denoising_strength || 0.7;
                
                // Hires Fix Settings
                document.getElementById('hires-fix-input').value = config.generation_settings?.hires_fix || false;
                document.getElementById('hires-upscaler-input').value = config.generation_settings?.hires_upscaler || 'Latent';
                document.getElementById('hires-steps-input').value = config.generation_settings?.hires_steps || 20;
                document.getElementById('hires-denoising-input').value = config.generation_settings?.hires_denoising || 0.7;
                
                showNotification('Template loaded successfully!', 'success');
            } else {
                showNotification('Failed to load template: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error loading template:', error);
            showNotification('Error loading template: ' + error.message, 'error');
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

function analyzeImage(imageData) {
    updateNotification('Analyzing image...', 'info');
    
    // Show loading state in the analysis results
    const resultsDiv = document.getElementById('analysis-results');
    if (resultsDiv) {
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = `
            <div class="analysis-header">
                <h4><i class="fas fa-chart-line"></i> Analysis Results</h4>
                <div class="analysis-actions">
                    <button class="btn btn-sm btn-secondary" onclick="clearImageAnalysis()">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
            <div class="analysis-content">
                <div class="analysis-image">
                    <img src="${imageData}" alt="Analyzing..." style="opacity: 0.7;">
                </div>
                <div class="analysis-details">
                    <div class="detail-group">
                        <h5>Analysis Status</h5>
                        <div class="detail-item">
                            <span class="detail-label">Status:</span>
                            <span class="detail-value">
                                <i class="fas fa-spinner fa-spin"></i> Analyzing image...
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    fetch('/api/analyze-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_data: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            updateNotification(`Analysis failed: ${data.error}`, 'error');
            // Restore the original analysis results structure
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div class="analysis-header">
                        <h4><i class="fas fa-chart-line"></i> Analysis Results</h4>
                        <div class="analysis-actions">
                            <select id="analysis-selector" onchange="selectAnalysis(parseInt(this.value))" style="margin-right: 0.5rem; padding: 0.25rem; border-radius: 4px; border: 1px solid #ddd;">
                                <option value="">No analyzed images</option>
                            </select>
                            <button class="btn btn-sm btn-danger" onclick="removeAnalysis(selectedAnalysisIndex)" title="Remove Current Analysis">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-sm btn-success" onclick="populateSettingsFromAnalysis()" title="Populate All Settings">
                                <i class="fas fa-magic"></i> Populate Settings
                            </button>
                            <button class="btn btn-sm btn-primary" onclick="createConfigFromAnalysis()">
                                <i class="fas fa-save"></i> Create Config
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="editAnalysisConfig()">
                                <i class="fas fa-edit"></i> Edit Settings
                            </button>
                        </div>
                    </div>
                    <div class="analysis-content resizable" id="analysis-content">
                        <div class="analysis-resizer" id="analysis-resizer"></div>
                        <div class="analysis-image">
                            <img id="analysis-image-preview" src="" alt="Analyzed Image">
                        </div>
                        <div class="analysis-details">
                            <!-- Analysis details will be populated here -->
                        </div>
                    </div>
                `;
            }
            return;
        }
        
        // Add timestamp and filename to the analysis result
        data.timestamp = new Date().toISOString();
        data.filename = `analyzed_image_${analyzedImages.length + 1}`;
        
        // Add to analyzed images array
        analyzedImages.push(data);
        selectedAnalysisIndex = analyzedImages.length - 1;
        currentAnalysisResult = data;
        
        displayAnalysisResults(data);
        updateAnalysisSelector();
        
        updateNotification(`Image analysis completed (${analyzedImages.length} total)`, 'success');
    })
    .catch(error => {
        console.error('Error analyzing image:', error);
        updateNotification('Failed to analyze image', 'error');
        // Restore the original analysis results structure on error
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="analysis-header">
                    <h4><i class="fas fa-chart-line"></i> Analysis Results</h4>
                    <div class="analysis-actions">
                        <select id="analysis-selector" onchange="selectAnalysis(parseInt(this.value))" style="margin-right: 0.5rem; padding: 0.25rem; border-radius: 4px; border: 1px solid #ddd;">
                            <option value="">No analyzed images</option>
                        </select>
                        <button class="btn btn-sm btn-danger" onclick="removeAnalysis(selectedAnalysisIndex)" title="Remove Current Analysis">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="populateSettingsFromAnalysis()" title="Populate All Settings">
                            <i class="fas fa-magic"></i> Populate Settings
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="createConfigFromAnalysis()">
                            <i class="fas fa-save"></i> Create Config
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="editAnalysisConfig()">
                            <i class="fas fa-edit"></i> Edit Settings
                        </button>
                    </div>
                </div>
                <div class="analysis-content resizable" id="analysis-content">
                    <div class="analysis-resizer" id="analysis-resizer"></div>
                    <div class="analysis-image">
                        <img id="analysis-image-preview" src="" alt="Analyzed Image">
                    </div>
                    <div class="analysis-details">
                        <!-- Analysis details will be populated here -->
                    </div>
                </div>
            `;
        }
    });
}

function displayAnalysisResults(data) {
    const resultsDiv = document.getElementById('analysis-results');
    const imagePreview = document.getElementById('analysis-image-preview');
    
    if (!resultsDiv || !imagePreview) return;
    
    // Show results section
    resultsDiv.style.display = 'block';
    
    // Set image preview
    imagePreview.src = data.image_data || '';
    
    // Update analysis details
    updateAnalysisDetail('analysis-dimensions', `${data.width} × ${data.height}`);
    updateAnalysisDetail('analysis-format', data.format || 'Unknown');
    
    // Extract and display parameters
    const params = data.parameters || {};
    const promptInfo = data.prompt_info || {};
    
    // Helper function to format values
    const formatValue = (value, defaultValue = 'Not found') => {
        if (value === null || value === undefined || value === '') {
            return defaultValue;
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        if (typeof value === 'number') {
            return value.toString();
        }
        return value.toString();
    };
    
    // Basic settings
    updateAnalysisDetail('analysis-prompt', formatValue(promptInfo.prompt || params.prompt, 'No prompt found'));
    updateAnalysisDetail('analysis-negative-prompt', formatValue(promptInfo.negative_prompt || params.negative_prompt, 'No negative prompt'));
    updateAnalysisDetail('analysis-steps', formatValue(params.steps));
    updateAnalysisDetail('analysis-cfg-scale', formatValue(params.cfg_scale));
    updateAnalysisDetail('analysis-sampler', formatValue(params.sampler));
    updateAnalysisDetail('analysis-seed', formatValue(params.seed));
    updateAnalysisDetail('analysis-denoising-strength', formatValue(params.denoising_strength));
    updateAnalysisDetail('analysis-clip-skip', formatValue(params.clip_skip));
    updateAnalysisDetail('analysis-restore-faces', formatValue(params.restore_faces));
    updateAnalysisDetail('analysis-tiling', formatValue(params.tiling));
    
    // Hires fix settings
    updateAnalysisDetail('analysis-hires-fix', formatValue(params.hires_fix));
    updateAnalysisDetail('analysis-hires-steps', formatValue(params.hires_steps));
    updateAnalysisDetail('analysis-hires-upscaler', formatValue(params.hires_upscaler));
    updateAnalysisDetail('analysis-hires-denoising', formatValue(params.hires_denoising));
    
    // Advanced settings
    updateAnalysisDetail('analysis-subseed', formatValue(params.subseed));
    updateAnalysisDetail('analysis-subseed-strength', formatValue(params.subseed_strength));
    updateAnalysisDetail('analysis-text-encoder', formatValue(params.text_encoder));
    updateAnalysisDetail('analysis-model-hash', formatValue(params.model_hash));
    updateAnalysisDetail('analysis-vae-hash', formatValue(params.vae_hash));
    updateAnalysisDetail('analysis-lora', formatValue(params.lora));
    updateAnalysisDetail('analysis-embedding', formatValue(params.embedding));
    
    // Model information
    updateAnalysisDetail('analysis-model', formatValue(params.model));
    updateAnalysisDetail('analysis-vae', formatValue(params.vae));
    
    // Update the analysis selector
    updateAnalysisSelector();
    
    // Show success notification
    updateNotification(`Image analysis completed successfully! Found ${Object.keys(params).length} parameters.`, 'success');
    
    // Scroll to the analysis results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateAnalysisDetail(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Determine the data type for color coding
        let dataType = 'text';
        if (elementId.includes('prompt')) {
            dataType = 'prompt';
        } else if (elementId.includes('model') || elementId.includes('vae') || elementId.includes('sampler') || elementId.includes('upscaler')) {
            dataType = 'model';
        } else if (elementId.includes('hash')) {
            dataType = 'hash';
        } else if (typeof value === 'boolean' || value === 'Yes' || value === 'No') {
            dataType = 'boolean';
        } else if (!isNaN(value) && value !== '') {
            dataType = 'number';
        }
        
        // Check if the value is long and needs expandable functionality
        if (value && value.length > 100) {
            element.textContent = value;
            element.classList.add('expandable');
            element.title = 'Click to expand/collapse';
            element.setAttribute('data-type', dataType);
            
            // Add click event listener for expandable text
            element.onclick = function() {
                if (this.classList.contains('expanded')) {
                    this.classList.remove('expanded');
                } else {
                    this.classList.add('expanded');
                }
            };
        } else {
            element.textContent = value;
            element.classList.remove('expandable', 'expanded');
            element.onclick = null;
            element.title = '';
            element.setAttribute('data-type', dataType);
        }
    }
}

function clearImageAnalysis() {
    const resultsDiv = document.getElementById('analysis-results');
    const fileInput = document.getElementById('image-file-input');
    
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
    
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Clear all analyzed images
    analyzedImages = [];
    selectedAnalysisIndex = 0;
    currentAnalysisResult = null;
    
    updateAnalysisSelector();
    updateNotification('All analyses cleared', 'info');
}

function createConfigFromAnalysis() {
    if (analyzedImages.length === 0) {
        updateNotification('No analyzed images available', 'error');
        return;
    }
    
    if (selectedAnalysisIndex < 0 || selectedAnalysisIndex >= analyzedImages.length) {
        updateNotification('Please select a valid analysis', 'error');
        return;
    }
    
    const selectedAnalysis = analyzedImages[selectedAnalysisIndex];
    
    // Populate the create config modal
    const summaryDiv = document.getElementById('create-config-summary');
    if (summaryDiv) {
        const params = selectedAnalysis.parameters || {};
        const promptInfo = selectedAnalysis.prompt_info || {};
        
        summaryDiv.innerHTML = `
            <div><strong>Selected Image:</strong> ${selectedAnalysis.filename}</div>
            <div><strong>Dimensions:</strong> ${selectedAnalysis.width} × ${selectedAnalysis.height}</div>
            <div><strong>Prompt:</strong> ${promptInfo.prompt || params.prompt || 'Not found'}</div>
            <div><strong>Steps:</strong> ${params.steps || 'Not found'}</div>
            <div><strong>CFG Scale:</strong> ${params.cfg_scale || 'Not found'}</div>
            <div><strong>Sampler:</strong> ${params.sampler || 'Not found'}</div>
            <div><strong>Model:</strong> ${params.model || 'Not found'}</div>
        `;
    }
    
    // Set default config name
    const configNameInput = document.getElementById('new-config-name');
    if (configNameInput) {
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        configNameInput.value = `extracted_config_${selectedAnalysis.filename}_${timestamp}`;
    }
    
    openModal('create-config-modal');
}

function confirmCreateConfig() {
    const configName = document.getElementById('new-config-name').value.trim();
    const description = document.getElementById('new-config-description').value.trim();
    
    if (!configName) {
        updateNotification('Please enter a config name', 'error');
        return;
    }
    
    if (analyzedImages.length === 0) {
        updateNotification('No analyzed images available', 'error');
        return;
    }
    
    if (selectedAnalysisIndex < 0 || selectedAnalysisIndex >= analyzedImages.length) {
        updateNotification('Please select a valid analysis', 'error');
        return;
    }
    
    const selectedAnalysis = analyzedImages[selectedAnalysisIndex];
    
    const data = {
        config_name: configName,
        analysis_result: selectedAnalysis,
        custom_settings: {
            name: configName,
            description: description || `Config created from image analysis - ${new Date().toLocaleString()}`
        }
    };
    
    fetch('/api/configs/create-from-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            updateNotification(`Failed to create config: ${data.error}`, 'error');
            return;
        }
        
        updateNotification(`Config '${configName}' created successfully`, 'success');
        closeModal('create-config-modal');
        
        // Refresh templates
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    })
    .catch(error => {
        console.error('Error creating config:', error);
        updateNotification('Failed to create config', 'error');
    });
}

function editAnalysisConfig() {
    if (analyzedImages.length === 0) {
        updateNotification('No analyzed images available', 'error');
        return;
    }
    
    if (selectedAnalysisIndex < 0 || selectedAnalysisIndex >= analyzedImages.length) {
        updateNotification('Please select a valid analysis', 'error');
        return;
    }
    
    const selectedAnalysis = analyzedImages[selectedAnalysisIndex];
    
    // Populate the config editor with the selected analysis
    loadConfigIntoEditor(selectedAnalysis);
    
    // Set the config name to indicate it's from analysis
    const configNameInput = document.getElementById('config-name');
    if (configNameInput) {
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        configNameInput.value = `extracted_config_${selectedAnalysis.filename}_${timestamp}`;
    }
    
    openModal('config-editor-modal');
}

function populateSettingsFromAnalysis() {
    if (analyzedImages.length === 0) {
        updateNotification('No analyzed images available', 'error');
        return;
    }
    
    if (selectedAnalysisIndex < 0 || selectedAnalysisIndex >= analyzedImages.length) {
        updateNotification('Please select a valid analysis', 'error');
        return;
    }
    
    const selectedAnalysis = analyzedImages[selectedAnalysisIndex];
    const params = selectedAnalysis.parameters || {};
    const promptInfo = selectedAnalysis.prompt_info || {};
    
    // Populate basic settings
    const promptInput = document.getElementById('prompt-input');
    const negativePromptInput = document.getElementById('negative-prompt-input');
    const seedInput = document.getElementById('seed-input');
    
    if (promptInput) {
        promptInput.value = promptInfo.prompt || params.prompt || '';
    }
    
    if (negativePromptInput) {
        negativePromptInput.value = promptInfo.negative_prompt || params.negative_prompt || '';
    }
    
    if (seedInput) {
        seedInput.value = params.seed || '';
    }
    
    // Populate image settings
    const widthInput = document.getElementById('width-input');
    const heightInput = document.getElementById('height-input');
    const stepsInput = document.getElementById('steps-input');
    const cfgScaleInput = document.getElementById('cfg-scale-input');
    const samplerInput = document.getElementById('sampler-input');
    const batchSizeInput = document.getElementById('batch-size-input');
    
    if (widthInput) {
        widthInput.value = selectedAnalysis.width || params.width || 512;
    }
    
    if (heightInput) {
        heightInput.value = selectedAnalysis.height || params.height || 512;
    }
    
    if (stepsInput) {
        stepsInput.value = params.steps || 20;
    }
    
    if (cfgScaleInput) {
        cfgScaleInput.value = params.cfg_scale || 7.0;
    }
    
    if (samplerInput) {
        samplerInput.value = params.sampler || 'Euler a';
    }
    
    if (batchSizeInput) {
        batchSizeInput.value = params.batch_size || 1;
    }
    
    // Populate number of batches
    const numBatchesInput = document.getElementById('num-batches');
    if (numBatchesInput) {
        numBatchesInput.value = params.num_batches || 1;
    }
    
    // Populate advanced settings
    const denoisingStrengthInput = document.getElementById('denoising-strength-input');
    const clipSkipInput = document.getElementById('clip-skip-input');
    const restoreFacesInput = document.getElementById('restore-faces-input');
    const tilingInput = document.getElementById('tiling-input');
    
    if (denoisingStrengthInput) {
        denoisingStrengthInput.value = params.denoising_strength || 0.7;
    }
    
    if (clipSkipInput) {
        clipSkipInput.value = params.clip_skip || 1;
    }
    
    if (restoreFacesInput) {
        restoreFacesInput.value = params.restore_faces ? 'true' : 'false';
    }
    
    if (tilingInput) {
        tilingInput.value = params.tiling ? 'true' : 'false';
    }
    
    // Populate hires fix settings
    const hiresFixInput = document.getElementById('hires-fix-input');
    const hiresStepsInput = document.getElementById('hires-steps-input');
    const hiresUpscalerInput = document.getElementById('hires-upscaler-input');
    const hiresDenoisingInput = document.getElementById('hires-denoising-input');
    
    if (hiresFixInput) {
        hiresFixInput.value = params.hires_fix ? 'true' : 'false';
    }
    
    if (hiresStepsInput) {
        hiresStepsInput.value = params.hires_steps || 20;
    }
    
    if (hiresUpscalerInput) {
        hiresUpscalerInput.value = params.hires_upscaler || 'Latent';
    }
    
    if (hiresDenoisingInput) {
        hiresDenoisingInput.value = params.hires_denoising || 0.5;
    }
    
    // Show success notification
    updateNotification(`Settings populated from analysis: ${selectedAnalysis.filename}`, 'success');
    
    // Scroll to the generation settings section
    const generationSettings = document.querySelector('.generation-settings');
    if (generationSettings) {
        generationSettings.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Config Editor Functions
function switchConfigTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.config-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(`config-tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    const clickedButton = event.target;
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
}

function loadConfigIntoEditor(config) {
    currentEditingConfig = config;
    
    // Load basic settings
    document.getElementById('config-name').value = config.name || '';
    document.getElementById('config-description').value = config.description || '';
    document.getElementById('config-model-type').value = config.model_type || 'sd';
    
    // Load prompt settings
    const promptSettings = config.prompt_settings || {};
    document.getElementById('config-base-prompt').value = promptSettings.base_prompt || '';
    document.getElementById('config-negative-prompt').value = promptSettings.negative_prompt || '';
    
    // Load generation settings
    const generationSettings = config.generation_settings || {};
    document.getElementById('config-steps').value = generationSettings.steps || 20;
    document.getElementById('config-cfg-scale').value = generationSettings.cfg_scale || 7.0;
    document.getElementById('config-width').value = generationSettings.width || 512;
    document.getElementById('config-height').value = generationSettings.height || 512;
    document.getElementById('config-batch-size').value = generationSettings.batch_size || 1;
    document.getElementById('config-sampler').value = generationSettings.sampler || 'Euler a';
    
    // Load model settings
    const modelSettings = config.model_settings || {};
    document.getElementById('config-checkpoint').value = modelSettings.checkpoint || '';
    document.getElementById('config-vae').value = modelSettings.vae || '';
    document.getElementById('config-text-encoder').value = modelSettings.text_encoder || '';
    document.getElementById('config-gpu-weight').value = modelSettings.gpu_weight || 1.0;
    document.getElementById('config-swap-method').value = modelSettings.swap_method || 'weight';
    document.getElementById('config-swap-location').value = modelSettings.swap_location || 'cpu';
    
    // Load output settings
    const outputSettings = config.output_settings || {};
    document.getElementById('config-output-dir').value = outputSettings.dir || 'outputs/{config_name}/{timestamp}/';
    document.getElementById('config-output-format').value = outputSettings.format || 'png';
    document.getElementById('config-save-metadata').checked = outputSettings.save_metadata !== false;
    document.getElementById('config-save-prompts').checked = outputSettings.save_prompts !== false;
    
    // Load raw JSON
    document.getElementById('config-json').value = JSON.stringify(config, null, 2);
}

function saveConfigFromEditor() {
    const configName = document.getElementById('config-name').value.trim();
    
    if (!configName) {
        updateNotification('Please enter a config name', 'error');
        return;
    }
    
    // Build config object from form
    const config = {
        name: configName,
        description: document.getElementById('config-description').value,
        model_type: document.getElementById('config-model-type').value,
        prompt_settings: {
            base_prompt: document.getElementById('config-base-prompt').value,
            negative_prompt: document.getElementById('config-negative-prompt').value
        },
        generation_settings: {
            steps: parseInt(document.getElementById('config-steps').value),
            cfg_scale: parseFloat(document.getElementById('config-cfg-scale').value),
            width: parseInt(document.getElementById('config-width').value),
            height: parseInt(document.getElementById('config-height').value),
            batch_size: parseInt(document.getElementById('config-batch-size').value),
            sampler: document.getElementById('config-sampler').value
        },
        model_settings: {
            checkpoint: document.getElementById('config-checkpoint').value,
            vae: document.getElementById('config-vae').value,
            text_encoder: document.getElementById('config-text-encoder').value,
            gpu_weight: parseFloat(document.getElementById('config-gpu-weight').value),
            swap_method: document.getElementById('config-swap-method').value,
            swap_location: document.getElementById('config-swap-location').value
        },
        output_settings: {
            dir: document.getElementById('config-output-dir').value,
            format: document.getElementById('config-output-format').value,
            save_metadata: document.getElementById('config-save-metadata').checked,
            save_prompts: document.getElementById('config-save-prompts').checked
        }
    };
    
    // Check if this is a new config or updating existing
    const isNewConfig = !currentEditingConfig || !currentEditingConfig.name;
    
    if (isNewConfig) {
        // Create new config
        fetch('/api/configs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: configName,
                config: config
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                updateNotification(`Failed to create config: ${data.error}`, 'error');
                return;
            }
            
            updateNotification(`Config "${configName}" created successfully`, 'success');
            closeModal('config-editor-modal');
            
            // Refresh the page to show the new config
            setTimeout(() => {
                location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error('Error creating config:', error);
            updateNotification('Failed to create config', 'error');
        });
    } else {
        // Update existing config
        fetch(`/api/configs/${configName}/settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                settings: config
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                updateNotification(`Failed to update config: ${data.error}`, 'error');
                return;
            }
            
            updateNotification(`Config "${configName}" updated successfully`, 'success');
            closeModal('config-editor-modal');
            
            // Refresh the page to show the updated config
            setTimeout(() => {
                location.reload();
            }, 1000);
        })
        .catch(error => {
            console.error('Error updating config:', error);
            updateNotification('Failed to update config', 'error');
        });
    }
}

// Enhanced template editing function
function editTemplate(configName) {
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

function updateAnalysisSelector() {
    const selector = document.getElementById('analysis-selector');
    if (!selector) return;
    
    // Clear existing options
    selector.innerHTML = '';
    
    if (analyzedImages.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No analyzed images';
        option.disabled = true;
        selector.appendChild(option);
        return;
    }
    
    // Add options for each analyzed image
    analyzedImages.forEach((analysis, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${analysis.filename} (${analysis.width}x${analysis.height}) - ${new Date(analysis.timestamp).toLocaleTimeString()}`;
        if (index === selectedAnalysisIndex) {
            option.selected = true;
        }
        selector.appendChild(option);
    });
}

function selectAnalysis(index) {
    if (index >= 0 && index < analyzedImages.length) {
        selectedAnalysisIndex = index;
        currentAnalysisResult = analyzedImages[index];
        displayAnalysisResults(currentAnalysisResult);
        updateNotification(`Selected analysis: ${currentAnalysisResult.filename}`, 'info');
    }
}

function removeAnalysis(index) {
    if (index >= 0 && index < analyzedImages.length) {
        const removedAnalysis = analyzedImages[index];
        analyzedImages.splice(index, 1);
        
        // Update selected index if needed
        if (analyzedImages.length === 0) {
            selectedAnalysisIndex = 0;
            currentAnalysisResult = null;
            const resultsDiv = document.getElementById('analysis-results');
            if (resultsDiv) {
                resultsDiv.style.display = 'none';
            }
        } else if (selectedAnalysisIndex >= analyzedImages.length) {
            selectedAnalysisIndex = analyzedImages.length - 1;
            currentAnalysisResult = analyzedImages[selectedAnalysisIndex];
            displayAnalysisResults(currentAnalysisResult);
        } else if (selectedAnalysisIndex === index) {
            currentAnalysisResult = analyzedImages[selectedAnalysisIndex];
            displayAnalysisResults(currentAnalysisResult);
        }
        
        updateAnalysisSelector();
        updateNotification(`Removed analysis: ${removedAnalysis.filename}`, 'info');
    }
}

function showAnalysisSummary() {
    if (analyzedImages.length === 0) {
        updateNotification('No analyzed images to show', 'info');
        return;
    }
    
    let summary = `Analysis Summary (${analyzedImages.length} images):\n\n`;
    
    analyzedImages.forEach((analysis, index) => {
        const params = analysis.parameters || {};
        const promptInfo = analysis.prompt_info || {};
        const timestamp = new Date(analysis.timestamp).toLocaleTimeString();
        
        summary += `${index + 1}. ${analysis.filename}\n`;
        summary += `   Time: ${timestamp}\n`;
        summary += `   Size: ${analysis.width}x${analysis.height}\n`;
        summary += `   Model: ${params.model || 'Unknown'}\n`;
        summary += `   Steps: ${params.steps || 'Unknown'}\n`;
        summary += `   Sampler: ${params.sampler || 'Unknown'}\n`;
        summary += `   Prompt: ${(promptInfo.prompt || params.prompt || 'None').substring(0, 50)}${(promptInfo.prompt || params.prompt || '').length > 50 ? '...' : ''}\n\n`;
    });
    
    // Create a modal to show the summary
    const modalId = 'analysis-summary-modal';
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Analysis Summary</h3>
                <button class="close-btn" onclick="closeModal('${modalId}')">&times;</button>
            </div>
            <div class="modal-body">
                <pre style="white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; max-height: 400px; overflow-y: auto;">${summary}</pre>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('${modalId}')">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    openModal(modalId);
}

// Initialize resizable elements
function initializeResizableElements() {
    initializeSidebarResizer();
    initializeAnalysisResizer();
}

// Initialize sidebar resizer
function initializeSidebarResizer() {
    const sidebar = document.querySelector('.sidebar.resizable');
    const resizer = document.getElementById('sidebar-resizer');
    
    if (!sidebar || !resizer) return;
    
    let isResizing = false;
    let startX, startWidth;
    
    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        startWidth = parseInt(getComputedStyle(sidebar).width, 10);
        
        resizer.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const width = startWidth + (e.clientX - startX);
        const minWidth = 300;
        const maxWidth = 800;
        
        if (width >= minWidth && width <= maxWidth) {
            sidebar.style.width = width + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            resizer.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            
            // Save the width to localStorage
            const width = parseInt(getComputedStyle(sidebar).width, 10);
            localStorage.setItem('sidebar-width', width);
        }
    });
    
    // Load saved width
    const savedWidth = localStorage.getItem('sidebar-width');
    if (savedWidth) {
        sidebar.style.width = savedWidth + 'px';
    }
}

// Initialize analysis resizer
function initializeAnalysisResizer() {
    const analysisContent = document.getElementById('analysis-content');
    const resizer = document.getElementById('analysis-resizer');
    
    if (!analysisContent || !resizer) return;
    
    let isResizing = false;
    let startX, startWidth;
    
    resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        startWidth = parseInt(getComputedStyle(analysisContent).getPropertyValue('--image-column-width') || '200');
        
        resizer.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        
        const width = startWidth + (e.clientX - startX);
        const minWidth = 150;
        const maxWidth = 400;
        
        if (width >= minWidth && width <= maxWidth) {
            analysisContent.style.setProperty('--image-column-width', width + 'px');
            resizer.style.left = width + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            resizer.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            
            // Save the width to localStorage
            const width = parseInt(getComputedStyle(analysisContent).getPropertyValue('--image-column-width') || '200');
            localStorage.setItem('analysis-image-width', width);
        }
    });
    
    // Load saved width
    const savedWidth = localStorage.getItem('analysis-image-width');
    if (savedWidth) {
        analysisContent.style.setProperty('--image-column-width', savedWidth + 'px');
        resizer.style.left = savedWidth + 'px';
    }
}

// Queue management functions
function refreshQueue() {
    loadQueueStats();
    loadQueueJobs();
}

function loadQueueStats() {
    fetch('/api/queue/status')
        .then(response => response.json())
        .then(data => {
            updateQueueStats(data);
        })
        .catch(error => {
            console.error('Failed to load queue stats:', error);
            updateNotification('Failed to load queue statistics', 'error');
        });
}

function updateQueueStats(data) {
    document.getElementById('pending-jobs').textContent = data.pending_jobs || 0;
    document.getElementById('running-jobs').textContent = data.running_jobs || 0;
    document.getElementById('completed-jobs').textContent = data.completed_jobs || 0;
    document.getElementById('failed-jobs').textContent = data.failed_jobs || 0;
    document.getElementById('retrying-jobs').textContent = data.retrying_jobs || 0;
    document.getElementById('total-jobs').textContent = data.total_jobs || 0;
}

function loadQueueJobs() {
    fetch('/api/queue/jobs')
        .then(response => response.json())
        .then(data => {
            displayQueueJobs(data.jobs || []);
        })
        .catch(error => {
            console.error('Failed to load queue jobs:', error);
            updateNotification('Failed to load queue jobs', 'error');
        });
}

function displayQueueJobs(jobs) {
    const container = document.getElementById('jobs-container');
    
    if (jobs.length === 0) {
        container.innerHTML = '<div class="text-center text-muted" style="padding: 2rem;">No jobs in queue</div>';
        return;
    }
    
    const jobsHtml = jobs.map(job => createJobItemHtml(job)).join('');
    container.innerHTML = jobsHtml;
}

function createJobItemHtml(job) {
    const priorityNames = { 1: 'Low', 2: 'Normal', 3: 'High', 4: 'Urgent' };
    const priorityColors = { 1: '#6c757d', 2: '#007bff', 3: '#fd7e14', 4: '#dc3545' };
    
    const progress = job.total_images > 0 ? (job.completed_images / job.total_images) * 100 : 0;
    const elapsed = job.started_at ? formatElapsedTime(job.started_at) : '-';
    const created = formatDateTime(job.created_at);
    
    let actionsHtml = '';
    if (job.status === 'failed') {
        actionsHtml = `<button class="btn btn-sm btn-primary" onclick="retryJob('${job.id}')">
            <i class="fas fa-redo"></i> Retry
        </button>`;
    }
    if (job.status === 'pending' || job.status === 'running') {
        actionsHtml = `<button class="btn btn-sm btn-danger" onclick="cancelJob('${job.id}')">
            <i class="fas fa-times"></i> Cancel
        </button>`;
    }
    
    const errorHtml = job.last_error ? `<div class="job-error">${job.last_error}</div>` : '';
    
    return `
        <div class="job-item ${job.status}" data-job-id="${job.id}" data-status="${job.status}" data-priority="${job.priority}">
            <div class="job-header">
                <h5 class="job-title">${job.config_name}</h5>
                <div class="job-status ${job.status}">
                    <i class="fas fa-${getStatusIcon(job.status)}"></i>
                    ${job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </div>
            </div>
            
            <div class="job-details">
                <div class="job-detail">
                    <span class="job-detail-label">Priority:</span>
                    <span class="job-detail-value" style="color: ${priorityColors[job.priority]}">
                        ${priorityNames[job.priority]}
                    </span>
                </div>
                <div class="job-detail">
                    <span class="job-detail-label">Images:</span>
                    <span class="job-detail-value">${job.completed_images}/${job.total_images}</span>
                </div>
                <div class="job-detail">
                    <span class="job-detail-label">Created:</span>
                    <span class="job-detail-value">${created}</span>
                </div>
                <div class="job-detail">
                    <span class="job-detail-label">Elapsed:</span>
                    <span class="job-detail-value">${elapsed}</span>
                </div>
                ${job.retry_count > 0 ? `
                <div class="job-detail">
                    <span class="job-detail-label">Retries:</span>
                    <span class="job-detail-value">${job.retry_count}/${job.max_retries}</span>
                </div>
                ` : ''}
            </div>
            
            ${job.total_images > 0 ? `
            <div class="job-progress">
                <div class="progress-bar-small">
                    <div class="progress-fill-small" style="width: ${progress}%"></div>
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.25rem;">
                    ${progress.toFixed(1)}% complete
                </div>
            </div>
            ` : ''}
            
            ${errorHtml}
            
            <div class="job-actions">
                ${actionsHtml}
            </div>
        </div>
    `;
}

function getStatusIcon(status) {
    const icons = {
        'pending': 'clock',
        'running': 'cog',
        'completed': 'check-circle',
        'failed': 'exclamation-triangle',
        'retrying': 'redo',
        'cancelled': 'times-circle'
    };
    return icons[status] || 'question-circle';
}

function formatElapsedTime(startTime) {
    if (!startTime) return '-';
    
    const start = new Date(startTime);
    const now = new Date();
    const elapsed = Math.floor((now - start) / 1000);
    
    if (elapsed < 60) return `${elapsed}s`;
    if (elapsed < 3600) return `${Math.floor(elapsed / 60)}m ${elapsed % 60}s`;
    return `${Math.floor(elapsed / 3600)}h ${Math.floor((elapsed % 3600) / 60)}m`;
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

function retryJob(jobId) {
    if (!confirm('Retry this failed job?')) return;
    
    fetch(`/api/queue/jobs/${jobId}/retry`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                updateNotification(data.message, 'success');
                refreshQueue();
            } else {
                updateNotification(data.error || 'Failed to retry job', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to retry job:', error);
            updateNotification('Failed to retry job', 'error');
        });
}

function cancelJob(jobId) {
    if (!confirm('Cancel this job?')) return;
    
    fetch(`/api/queue/jobs/${jobId}/cancel`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                updateNotification(data.message, 'success');
                refreshQueue();
            } else {
                updateNotification(data.error || 'Failed to cancel job', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to cancel job:', error);
            updateNotification('Failed to cancel job', 'error');
        });
}

function clearCompletedJobs() {
    if (!confirm('Clear all completed and failed jobs?')) return;
    
    fetch('/api/queue/clear-completed', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                updateNotification(data.message, 'success');
                refreshQueue();
            } else {
                updateNotification(data.error || 'Failed to clear completed jobs', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to clear completed jobs:', error);
            updateNotification('Failed to clear completed jobs', 'error');
        });
}

function clearAllJobs() {
    if (!confirm('Clear ALL jobs from the queue? This action cannot be undone.')) return;
    
    fetch('/api/queue/clear', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                updateNotification(data.message, 'success');
                refreshQueue();
            } else {
                updateNotification(data.error || 'Failed to clear queue', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to clear queue:', error);
            updateNotification('Failed to clear queue', 'error');
        });
}

function filterJobs() {
    const statusFilter = document.getElementById('status-filter').value;
    const priorityFilter = document.getElementById('priority-filter').value;
    
    const jobItems = document.querySelectorAll('.job-item');
    
    jobItems.forEach(item => {
        const status = item.dataset.status;
        const priority = item.dataset.priority;
        
        let show = true;
        
        if (statusFilter && status !== statusFilter) {
            show = false;
        }
        
        if (priorityFilter && priority !== priorityFilter) {
            show = false;
        }
        
        item.style.display = show ? 'block' : 'none';
    });
}

// Load default settings
function loadDefaultSettings() {
    // Reset all settings to default values
    document.getElementById('prompt-input').value = '';
    document.getElementById('negative-prompt-input').value = '';
    document.getElementById('config-select').value = '';
    document.getElementById('seed-input').value = '';
    document.getElementById('width-input').value = '512';
    document.getElementById('height-input').value = '512';
    document.getElementById('steps-input').value = '20';
    document.getElementById('cfg-scale-input').value = '7.0';
    document.getElementById('sampler-input').value = 'Euler a';
    document.getElementById('batch-size-input').value = '1';
    document.getElementById('restore-faces-input').value = 'false';
    document.getElementById('tiling-input').value = 'false';
    document.getElementById('clip-skip-input').value = '1';
    document.getElementById('denoising-strength-input').value = '0.7';
    document.getElementById('hires-fix-input').value = 'false';
    document.getElementById('hires-upscaler-input').value = 'Latent';
    document.getElementById('hires-steps-input').value = '20';
    document.getElementById('hires-denoising-input').value = '0.7';
    
    updateNotification('Settings reset to defaults', 'success');
}

// Save current settings
function saveSettings() {
    const settings = {
        prompt: document.getElementById('prompt-input').value,
        negative_prompt: document.getElementById('negative-prompt-input').value,
        config: document.getElementById('config-select').value,
        seed: document.getElementById('seed-input').value,
        width: parseInt(document.getElementById('width-input').value),
        height: parseInt(document.getElementById('height-input').value),
        steps: parseInt(document.getElementById('steps-input').value),
        cfg_scale: parseFloat(document.getElementById('cfg-scale-input').value),
        sampler: document.getElementById('sampler-input').value,
        batch_size: parseInt(document.getElementById('batch-size-input').value),
        restore_faces: document.getElementById('restore-faces-input').value === 'true',
        tiling: document.getElementById('tiling-input').value === 'true',
        clip_skip: parseInt(document.getElementById('clip-skip-input').value),
        denoising_strength: parseFloat(document.getElementById('denoising-strength-input').value),
        hires_fix: document.getElementById('hires-fix-input').value === 'true',
        hires_upscaler: document.getElementById('hires-upscaler-input').value,
        hires_steps: parseInt(document.getElementById('hires-steps-input').value),
        hires_denoising: parseFloat(document.getElementById('hires-denoising-input').value)
    };
    
    // Save to localStorage
    localStorage.setItem('forge_api_settings', JSON.stringify(settings));
    updateNotification('Settings saved', 'success');
}

// Load saved settings
function loadSavedSettings() {
    const saved = localStorage.getItem('forge_api_settings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            
            if (settings.prompt) document.getElementById('prompt-input').value = settings.prompt;
            if (settings.negative_prompt) document.getElementById('negative-prompt-input').value = settings.negative_prompt;
            if (settings.config) document.getElementById('config-select').value = settings.config;
            if (settings.seed !== undefined) document.getElementById('seed-input').value = settings.seed;
            if (settings.width) document.getElementById('width-input').value = settings.width;
            if (settings.height) document.getElementById('height-input').value = settings.height;
            if (settings.steps) document.getElementById('steps-input').value = settings.steps;
            if (settings.cfg_scale) document.getElementById('cfg-scale-input').value = settings.cfg_scale;
            if (settings.sampler) document.getElementById('sampler-input').value = settings.sampler;
            if (settings.batch_size) document.getElementById('batch-size-input').value = settings.batch_size;
            if (settings.restore_faces !== undefined) document.getElementById('restore-faces-input').value = settings.restore_faces.toString();
            if (settings.tiling !== undefined) document.getElementById('tiling-input').value = settings.tiling.toString();
            if (settings.clip_skip) document.getElementById('clip-skip-input').value = settings.clip_skip;
            if (settings.denoising_strength) document.getElementById('denoising-strength-input').value = settings.denoising_strength;
            if (settings.hires_fix !== undefined) document.getElementById('hires-fix-input').value = settings.hires_fix.toString();
            if (settings.hires_upscaler) document.getElementById('hires-upscaler-input').value = settings.hires_upscaler;
            if (settings.hires_steps) document.getElementById('hires-steps-input').value = settings.hires_steps;
            if (settings.hires_denoising) document.getElementById('hires-denoising-input').value = settings.hires_denoising;
            
            console.log('Settings loaded from localStorage');
        } catch (error) {
            console.error('Failed to load saved settings:', error);
        }
    }
}

// Preview generation settings
function previewGeneration() {
    const settings = getCurrentSettings();
    
    let previewText = `Generation Preview:\n\n`;
    previewText += `Template: ${settings.config || 'None selected'}\n`;
    previewText += `Prompt: ${settings.prompt || 'None'}\n`;
    previewText += `Negative Prompt: ${settings.negative_prompt || 'None'}\n`;
    previewText += `Dimensions: ${settings.width}x${settings.height}\n`;
    previewText += `Steps: ${settings.steps}\n`;
    previewText += `CFG Scale: ${settings.cfg_scale}\n`;
    previewText += `Sampler: ${settings.sampler}\n`;
    previewText += `Batch Size: ${settings.batch_size}\n`;
    previewText += `Seed: ${settings.seed || 'Random'}\n`;
    previewText += `Restore Faces: ${settings.restore_faces ? 'Yes' : 'No'}\n`;
    previewText += `Tiling: ${settings.tiling ? 'Yes' : 'No'}\n`;
    previewText += `Clip Skip: ${settings.clip_skip}\n`;
    previewText += `Denoising Strength: ${settings.denoising_strength}\n`;
    previewText += `Hires Fix: ${settings.hires_fix ? 'Enabled' : 'Disabled'}\n`;
    
    if (settings.hires_fix) {
        previewText += `Hires Upscaler: ${settings.hires_upscaler}\n`;
        previewText += `Hires Steps: ${settings.hires_steps}\n`;
        previewText += `Hires Denoising: ${settings.hires_denoising}\n`;
    }
    
    alert(previewText);
}

// Get current settings from form
function getCurrentSettings() {
    return {
        prompt: document.getElementById('prompt-input').value,
        negative_prompt: document.getElementById('negative-prompt-input').value,
        config: document.getElementById('config-select').value,
        seed: document.getElementById('seed-input').value,
        width: parseInt(document.getElementById('width-input').value),
        height: parseInt(document.getElementById('height-input').value),
        steps: parseInt(document.getElementById('steps-input').value),
        cfg_scale: parseFloat(document.getElementById('cfg-scale-input').value),
        sampler: document.getElementById('sampler-input').value,
        batch_size: parseInt(document.getElementById('batch-size-input').value),
        restore_faces: document.getElementById('restore-faces-input').value === 'true',
        tiling: document.getElementById('tiling-input').value === 'true',
        clip_skip: parseInt(document.getElementById('clip-skip-input').value),
        denoising_strength: parseFloat(document.getElementById('denoising-strength-input').value),
        hires_fix: document.getElementById('hires-fix-input').value === 'true',
        hires_upscaler: document.getElementById('hires-upscaler-input').value,
        hires_steps: parseInt(document.getElementById('hires-steps-input').value),
        hires_denoising: parseFloat(document.getElementById('hires-denoising-input').value)
    };
}

// Update compact queue display
function updateCompactQueue(queueData) {
    if (!queueData) return;
    
    // Update compact stats
    const pendingEl = document.getElementById('queue-pending-compact');
    const runningEl = document.getElementById('queue-running-compact');
    const completedEl = document.getElementById('queue-completed-compact');
    const failedEl = document.getElementById('queue-failed-compact');
    
    if (pendingEl) pendingEl.textContent = queueData.pending_jobs || 0;
    if (runningEl) runningEl.textContent = queueData.running_jobs || 0;
    if (completedEl) completedEl.textContent = queueData.completed_jobs || 0;
    if (failedEl) failedEl.textContent = queueData.failed_jobs || 0;
    
    // Update compact job list
    const jobListCompact = document.getElementById('job-list-compact');
    if (jobListCompact && queueData.jobs) {
        jobListCompact.innerHTML = '';
        
        queueData.jobs.slice(0, 5).forEach(job => { // Show only first 5 jobs
            const jobItem = document.createElement('div');
            jobItem.className = 'job-item';
            jobItem.innerHTML = `
                <div class="job-title">${job.config_name || 'Unknown'}</div>
                <span class="job-status ${job.status}">${job.status}</span>
            `;
            jobListCompact.appendChild(jobItem);
        });
        
        if (queueData.jobs.length === 0) {
            jobListCompact.innerHTML = '<div class="job-item">No jobs in queue</div>';
        } else if (queueData.jobs.length > 5) {
            const moreItem = document.createElement('div');
            moreItem.className = 'job-item';
            moreItem.innerHTML = `<em>... and ${queueData.jobs.length - 5} more</em>`;
            jobListCompact.appendChild(moreItem);
        }
    }
}

// Enhanced generateImage function with new settings
function generateImage() {
    const settings = getCurrentSettings();
    
    if (!settings.config) {
        updateNotification('Please select a template', 'error');
        return;
    }
    
    if (!settings.prompt.trim()) {
        updateNotification('Please enter a prompt', 'error');
        return;
    }
    
    const payload = {
        config_name: settings.config,
        prompt: settings.prompt,
        negative_prompt: settings.negative_prompt,
        seed: settings.seed || -1,
        width: settings.width,
        height: settings.height,
        steps: settings.steps,
        cfg_scale: settings.cfg_scale,
        sampler: settings.sampler,
        batch_size: settings.batch_size,
        restore_faces: settings.restore_faces,
        tiling: settings.tiling,
        clip_skip: settings.clip_skip,
        denoising_strength: settings.denoising_strength,
        hires_fix: settings.hires_fix,
        hires_upscaler: settings.hires_upscaler,
        hires_steps: settings.hires_steps,
        hires_denoising: settings.hires_denoising
    };
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification('Image generation started', 'success');
            updateSystemStatus();
        } else {
            updateNotification(data.error || 'Failed to start generation', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        updateNotification('Failed to start generation', 'error');
    });
}

// Enhanced startBatchGeneration function
function startBatchGeneration() {
    const settings = getCurrentSettings();
    
    if (!settings.config) {
        updateNotification('Please select a template', 'error');
        return;
    }
    
    if (!settings.prompt.trim()) {
        updateNotification('Please enter a prompt', 'error');
        return;
    }
    
    const batchSize = parseInt(document.getElementById('batch-size-input').value);
    const numBatches = parseInt(document.getElementById('num-batches').value) || 1;
    
    const payload = {
        config_name: settings.config,
        prompt: settings.prompt,
        negative_prompt: settings.negative_prompt,
        seed: settings.seed || -1,
        width: settings.width,
        height: settings.height,
        steps: settings.steps,
        cfg_scale: settings.cfg_scale,
        sampler: settings.sampler,
        batch_size: batchSize,
        num_batches: numBatches,
        restore_faces: settings.restore_faces,
        tiling: settings.tiling,
        clip_skip: settings.clip_skip,
        denoising_strength: settings.denoising_strength,
        hires_fix: settings.hires_fix,
        hires_upscaler: settings.hires_upscaler,
        hires_steps: settings.hires_steps,
        hires_denoising: settings.hires_denoising
    };
    
    fetch('/api/batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotification(`Batch generation started: ${data.total_images} images`, 'success');
            updateSystemStatus();
        } else {
            updateNotification(data.error || 'Failed to start batch generation', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        updateNotification('Failed to start batch generation', 'error');
    });
}

// Image Analysis Drop Zone
function initializeDropZone() {
    const dropzone = document.getElementById('image-analysis-dropzone');
    const fileInput = document.getElementById('image-analysis-input');
    
    if (!dropzone || !fileInput) return;
    
    // Click to select file
    dropzone.addEventListener('click', () => {
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
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleImageFile(files[0]);
        } else {
            updateNotification('Please drop an image file', 'error');
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

// Enhanced Button Feedback
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

// Status Indicators
function updateStatusIndicators() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateApiStatus(data.api_connected);
            updateGenerationStatus(data.generation_status);
            updateQueueStatus(data.queue_size);
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
}

function updateApiStatus(connected) {
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

function updateGenerationStatus(status) {
    const statusItem = document.getElementById('generation-status');
    const icon = statusItem?.querySelector('.status-icon');
    const text = statusItem?.querySelector('.status-text');
    
    if (statusItem && icon && text) {
        if (status === 'generating') {
            icon.className = 'fas fa-spinner fa-spin status-icon processing';
            text.textContent = 'Generation: Active';
        } else {
            icon.className = 'fas fa-check-circle status-icon connected';
            text.textContent = 'Generation: Idle';
        }
    }
}

function updateQueueStatus(queueSize) {
    const statusItem = document.getElementById('queue-status');
    const text = statusItem?.querySelector('.status-text');
    
    if (statusItem && text) {
        text.textContent = `Queue: ${queueSize} jobs`;
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
    populateField('hires-denoising-input', params.hires_denoising || 0.5);
    
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
            hires_denoising: params.hires_denoising || 0.5
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