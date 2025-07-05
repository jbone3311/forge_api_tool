// Forge API Tool Dashboard - Bootstrap Version
// Modern JavaScript with Bootstrap 5 components and Socket.IO integration

class ForgeDashboard {
    constructor() {
        this.socket = null;
        this.currentJob = null;
        this.templates = {};
        this.outputs = [];
        this.settings = {};
        this.isGenerating = false;
        
        this.initializeSocket();
        this.initializeEventListeners();
        this.loadInitialData();
    }

    // Initialize Socket.IO connection
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.showToast('Connected to Forge API Tool', 'success');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.showToast('Disconnected from server', 'warning');
            this.updateConnectionStatus(false);
        });

        this.socket.on('status_update', (status) => {
            this.updateSystemStatus(status);
        });

        this.socket.on('job_progress', (data) => {
            this.updateJobProgress(data);
        });

        this.socket.on('job_completed', (data) => {
            this.handleJobCompleted(data);
        });

        this.socket.on('job_failed', (data) => {
            this.handleJobFailed(data);
        });
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Template selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.template-card')) {
                const card = e.target.closest('.template-card');
                this.selectTemplate(card.dataset.config);
            }
        });

        // Form submission prevention
        document.getElementById('generation-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
        });

        // Auto-save settings
        const settingsInputs = document.querySelectorAll('#generation-form input, #generation-form select, #generation-form textarea');
        settingsInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.autoSaveSettings();
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.generateImage();
                        break;
                    case 's':
                        e.preventDefault();
                        this.saveSettings();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshDashboard();
                        break;
                }
            }
        });
    }

    // Load initial data
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadTemplates(),
                this.loadSettings(),
                this.loadOutputs(),
                this.loadSystemStatus()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading data', 'error');
        }
    }

    // Load templates
    async loadTemplates() {
        try {
            const response = await fetch('/api/configs');
            const configs = await response.json();
            
            this.templates = configs;
            this.updateTemplatesDisplay();
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showToast('Error loading templates', 'error');
        }
    }

    // Update templates display
    updateTemplatesDisplay() {
        const container = document.getElementById('templates-container');
        if (!container) return;

        if (Object.keys(this.templates).length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-exclamation-triangle display-4 text-muted"></i>
                    <p class="mt-2">No templates found</p>
                    <small>Add configurations in the configs/ directory</small>
                </div>
            `;
            return;
        }

        const templatesHtml = Object.entries(this.templates).map(([name, config]) => `
            <div class="template-card card card-hover mb-3" data-config="${name}">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${config.name || name}</h6>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-secondary btn-sm" onclick="dashboard.editTemplate('${name}')" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="dashboard.deleteTemplate('${name}')" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <small class="text-muted">${config.description || 'No description'}</small>
                    </div>
                    
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <small class="text-muted">Model:</small><br>
                            <span class="badge bg-secondary">${(config.model_type || 'Unknown').toUpperCase()}</span>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Checkpoint:</small><br>
                            <span class="badge bg-info">${config.model_settings?.checkpoint || 'Unknown'}</span>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button class="btn btn-primary btn-sm" onclick="dashboard.generateSingle('${name}')">
                            <i class="bi bi-play"></i> Generate
                        </button>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-secondary" onclick="dashboard.startBatch('${name}')">
                                <i class="bi bi-collection"></i> Batch
                            </button>
                            <button class="btn btn-outline-info" onclick="dashboard.openOutputFolder('${name}')" title="Open Output Folder">
                                <i class="bi bi-folder"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="alert alert-info alert-sm" role="alert">
                <i class="bi bi-info-circle"></i> Found ${Object.keys(this.templates).length} template(s)
            </div>
            ${templatesHtml}
        `;
    }

    // Select template
    selectTemplate(configName) {
        // Remove previous selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked card
        const card = document.querySelector(`[data-config="${configName}"]`);
        if (card) {
            card.classList.add('selected');
        }

        // Update form
        document.getElementById('config-select').value = configName;
        
        // Load template settings
        const config = this.templates[configName];
        if (config) {
            this.loadTemplateSettings(config);
        }
    }

    // Load template settings into form
    loadTemplateSettings(config) {
        if (config.generation_settings) {
            const settings = config.generation_settings;
            document.getElementById('steps-input').value = settings.steps || 20;
            document.getElementById('cfg-scale-input').value = settings.cfg_scale || 7.0;
            document.getElementById('width-input').value = settings.width || 512;
            document.getElementById('height-input').value = settings.height || 512;
        }
    }

    // Generate single image
    async generateImage() {
        if (this.isGenerating) {
            this.showToast('Generation already in progress', 'warning');
            return;
        }

        const formData = this.getFormData();
        if (!formData.config_name) {
            this.showToast('Please select a template', 'warning');
            return;
        }

        if (!formData.prompt.trim()) {
            this.showToast('Please enter a prompt', 'warning');
            return;
        }

        try {
            this.isGenerating = true;
            this.showProgressSection(formData.config_name);
            this.updateGenerateButton(true);

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentJob = result.job_id;
                this.showToast('Generation started', 'success');
            } else {
                throw new Error(result.error || 'Generation failed');
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showToast(error.message, 'error');
            this.hideProgressSection();
        } finally {
            this.isGenerating = false;
            this.updateGenerateButton(false);
        }
    }

    // Generate single image from template
    async generateSingle(configName) {
        document.getElementById('config-select').value = configName;
        this.selectTemplate(configName);
        await this.generateImage();
    }

    // Start batch generation
    async startBatch(configName) {
        document.getElementById('config-select').value = configName;
        this.selectTemplate(configName);
        this.openBatchModal();
    }

    // Get form data
    getFormData() {
        return {
            prompt: document.getElementById('prompt-input').value,
            negative_prompt: document.getElementById('negative-prompt-input').value,
            config_name: document.getElementById('config-select').value,
            seed: parseInt(document.getElementById('seed-input').value) || -1,
            steps: parseInt(document.getElementById('steps-input').value) || 20,
            cfg_scale: parseFloat(document.getElementById('cfg-scale-input').value) || 7.0,
            width: parseInt(document.getElementById('width-input').value) || 512,
            height: parseInt(document.getElementById('height-input').value) || 512
        };
    }

    // Show progress section
    showProgressSection(configName) {
        const progressSection = document.getElementById('progress-section');
        const progressConfig = document.getElementById('progress-config');
        
        progressConfig.textContent = configName;
        progressSection.style.display = 'block';
        progressSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Hide progress section
    hideProgressSection() {
        document.getElementById('progress-section').style.display = 'none';
    }

    // Update job progress
    updateJobProgress(data) {
        if (data.job_id !== this.currentJob) return;

        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressTime = document.getElementById('progress-time');

        const percentage = Math.round(data.progress);
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${data.current_step} / ${data.total_steps} steps`;
        progressPercentage.textContent = `${percentage}%`;

        // Update time (mock)
        const elapsed = Math.floor(data.current_step * 0.1);
        progressTime.textContent = `Elapsed: ${elapsed}s`;
    }

    // Handle job completed
    handleJobCompleted(data) {
        if (data.job_id !== this.currentJob) return;

        this.showToast('Generation completed!', 'success');
        this.hideProgressSection();
        this.currentJob = null;
        
        // Refresh outputs
        this.loadOutputs();
    }

    // Handle job failed
    handleJobFailed(data) {
        if (data.job_id !== this.currentJob) return;

        this.showToast(`Generation failed: ${data.error}`, 'error');
        this.hideProgressSection();
        this.currentJob = null;
    }

    // Stop generation
    async stopGeneration() {
        if (!this.currentJob) return;

        try {
            const response = await fetch(`/api/queue/job/${this.currentJob}/cancel`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Generation stopped', 'info');
                this.hideProgressSection();
                this.currentJob = null;
            } else {
                throw new Error('Failed to stop generation');
            }
        } catch (error) {
            console.error('Stop generation error:', error);
            this.showToast('Error stopping generation', 'error');
        }
    }

    // Update generate button
    updateGenerateButton(loading) {
        const button = document.querySelector('button[onclick="generateImage()"]');
        if (!button) return;

        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    // Load settings
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            this.settings = await response.json();
            this.applySettings();
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    // Apply settings to form
    applySettings() {
        const generationSettings = this.settings.generation_settings || {};
        
        document.getElementById('steps-input').value = generationSettings.default_steps || 20;
        document.getElementById('cfg-scale-input').value = generationSettings.default_cfg_scale || 7.0;
        document.getElementById('width-input').value = generationSettings.default_width || 512;
        document.getElementById('height-input').value = generationSettings.default_height || 512;
    }

    // Save settings
    async saveSettings() {
        try {
            const formData = this.getFormData();
            const settings = {
                ...this.settings,
                generation_settings: {
                    default_steps: formData.steps,
                    default_cfg_scale: formData.cfg_scale,
                    default_width: formData.width,
                    default_height: formData.height
                }
            };

            const response = await fetch('/api/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                this.showToast('Settings saved', 'success');
                this.settings = settings;
            } else {
                throw new Error('Failed to save settings');
            }
        } catch (error) {
            console.error('Save settings error:', error);
            this.showToast('Error saving settings', 'error');
        }
    }

    // Auto-save settings
    autoSaveSettings() {
        // Debounce auto-save
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveSettings();
        }, 2000);
    }

    // Save settings from modal
    async saveSettingsModal(settings) {
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                this.showToast('Settings saved successfully', 'success');
                this.settings = settings;
                this.applySettings();
            } else {
                throw new Error('Failed to save settings');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showToast('Error saving settings', 'error');
        }
    }

    // Template management methods
    async exportTemplates() {
        try {
            const response = await fetch('/api/configs/export');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `templates_export_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showToast('Templates exported successfully', 'success');
        } catch (error) {
            console.error('Error exporting templates:', error);
            this.showToast('Error exporting templates', 'error');
        }
    }

    async importTemplates(files) {
        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/api/configs/import', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showToast('Templates imported successfully', 'success');
                await this.loadTemplates();
            } else {
                throw new Error('Failed to import templates');
            }
        } catch (error) {
            console.error('Error importing templates:', error);
            this.showToast('Error importing templates', 'error');
        }
    }

    async validateAllTemplates() {
        try {
            const response = await fetch('/api/configs/validate', {
                method: 'POST'
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast(`Validation complete: ${result.valid} valid, ${result.invalid} invalid`, 'success');
                return result;
            } else {
                throw new Error('Failed to validate templates');
            }
        } catch (error) {
            console.error('Error validating templates:', error);
            this.showToast('Error validating templates', 'error');
            throw error;
        }
    }

    async clearTemplateCache() {
        try {
            const response = await fetch('/api/configs/cache/clear', {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Template cache cleared successfully', 'success');
                await this.loadTemplates();
            } else {
                throw new Error('Failed to clear template cache');
            }
        } catch (error) {
            console.error('Error clearing template cache:', error);
            this.showToast('Error clearing template cache', 'error');
        }
    }

    // Log management methods
    async exportLogs() {
        try {
            const response = await fetch('/api/logs/export');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `logs_export_${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showToast('Logs exported successfully', 'success');
        } catch (error) {
            console.error('Error exporting logs:', error);
            this.showToast('Error exporting logs', 'error');
        }
    }

    async clearLogs() {
        try {
            const response = await fetch('/api/logs/clear', {
                method: 'POST'
            });

            if (response.ok) {
                this.showToast('Logs cleared successfully', 'success');
            } else {
                throw new Error('Failed to clear logs');
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
            this.showToast('Error clearing logs', 'error');
        }
    }

    // Load outputs
    async loadOutputs() {
        try {
            const response = await fetch('/api/outputs/list');
            this.outputs = await response.json();
            this.updateOutputsDisplay();
        } catch (error) {
            console.error('Error loading outputs:', error);
        }
    }

    // Update outputs display
    updateOutputsDisplay() {
        const container = document.getElementById('outputs-container');
        if (!container) return;

        // Filter to only show image files
        const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'svg'];
        const imageOutputs = this.outputs.filter(output => {
            const extension = output.name.split('.').pop().toLowerCase();
            return imageExtensions.includes(extension);
        });

        if (imageOutputs.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-4">
                    <i class="bi bi-images display-4"></i>
                    <p class="mt-2">No image outputs yet</p>
                    <small>Generated images will appear here</small>
                </div>
            `;
            return;
        }

        const outputsHtml = imageOutputs.slice(0, 6).map(output => `
            <div class="col-md-4 col-lg-3">
                <div class="card card-hover h-100">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <small class="text-muted">${output.name}</small>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="dashboard.downloadOutput('${output.path}')" title="Download">
                                    <i class="bi bi-download"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="dashboard.deleteOutput('${output.path}')" title="Delete">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                        <small class="text-muted d-block">${this.formatFileSize(output.size)}</small>
                        <small class="text-muted d-block">${this.formatDate(output.modified)}</small>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = outputsHtml;
    }

    // Load system status
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('Error loading system status:', error);
        }
    }

    // Update system status
    updateSystemStatus(status) {
        // Update connection status
        this.updateConnectionStatus(status.api_connected);
        
        // Update queue status
        const queueIndicator = document.getElementById('queue-status-indicator');
        const queueText = document.getElementById('queue-status-text');
        
        if (queueIndicator && queueText) {
            queueText.textContent = `Queue: ${status.queue_size}`;
            
            if (status.queue_size === 0) {
                queueIndicator.className = 'status-indicator status-online';
            } else if (status.queue_size < 5) {
                queueIndicator.className = 'status-indicator status-warning';
            } else {
                queueIndicator.className = 'status-indicator status-offline';
            }
        }
    }

    // Update connection status
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('api-status-indicator');
        const text = document.getElementById('api-status-text');
        
        if (indicator && text) {
            if (connected) {
                indicator.className = 'status-indicator status-online';
                text.textContent = 'API: Connected';
            } else {
                indicator.className = 'status-indicator status-offline';
                text.textContent = 'API: Disconnected';
            }
        }
    }

    // Process wildcards
    async processWildcards() {
        const prompt = document.getElementById('prompt-input').value;
        if (!prompt.trim()) {
            this.showToast('Please enter a prompt first', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/wildcards/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });

            const result = await response.json();
            
            if (response.ok) {
                document.getElementById('prompt-input').value = result.processed_prompt;
                this.showToast('Wildcards processed', 'success');
            } else {
                throw new Error(result.error || 'Failed to process wildcards');
            }
        } catch (error) {
            console.error('Process wildcards error:', error);
            this.showToast(error.message, 'error');
        }
    }

    // Analyze image
    async analyzeImage() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);

            try {
                const response = await fetch('/api/analyze-image', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (response.ok) {
                    this.showAnalysisResult(result);
                } else {
                    throw new Error(result.error || 'Analysis failed');
                }
            } catch (error) {
                console.error('Analyze image error:', error);
                this.showToast(error.message, 'error');
            }
        };

        input.click();
    }

    // Show analysis result
    showAnalysisResult(result) {
        // Create and show modal with analysis results
        const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
        const modalBody = document.getElementById('analysisModalBody');
        
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Image Information</h6>
                    <ul class="list-unstyled">
                        <li><strong>Filename:</strong> ${result.filename}</li>
                        <li><strong>Size:</strong> ${this.formatFileSize(result.size)}</li>
                        <li><strong>Dimensions:</strong> ${result.dimensions}</li>
                        <li><strong>Format:</strong> ${result.format}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Analysis Results</h6>
                    <ul class="list-unstyled">
                        <li><strong>Estimated Prompt:</strong> ${result.estimated_prompt}</li>
                        <li><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</li>
                        <li><strong>Tags:</strong> ${result.tags.join(', ')}</li>
                    </ul>
                </div>
            </div>
        `;
        
        modal.show();
    }

    // Download output
    async downloadOutput(filepath) {
        try {
            window.open(`/api/outputs/${filepath}`, '_blank');
        } catch (error) {
            console.error('Download error:', error);
            this.showToast('Error downloading file', 'error');
        }
    }

    // Delete output
    async deleteOutput(filepath) {
        if (!confirm('Are you sure you want to delete this file?')) return;

        try {
            const response = await fetch(`/api/outputs/delete/${filepath}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('File deleted', 'success');
                this.loadOutputs();
            } else {
                throw new Error('Failed to delete file');
            }
        } catch (error) {
            console.error('Delete output error:', error);
            this.showToast('Error deleting file', 'error');
        }
    }

    // Open output folder
    openOutputFolder(configName) {
        // This would typically open the file explorer
        this.showToast(`Opening output folder for ${configName}`, 'info');
    }

    // Edit template
    async editTemplate(configName) {
        try {
            // Load the template data
            const response = await fetch(`/api/configs/${configName}`);
            if (!response.ok) {
                throw new Error('Failed to load template');
            }
            
            const template = await response.json();
            
            // Populate the template modal with existing data
            this.populateTemplateModal(template, configName);
            
            // Open the template modal
            const modal = new bootstrap.Modal(document.getElementById('templateModal'));
            modal.show();
            
        } catch (error) {
            console.error('Edit template error:', error);
            this.showToast('Error loading template for editing', 'error');
        }
    }

    // Populate template modal with existing data
    populateTemplateModal(template, configName) {
        // Update modal title
        const modalTitle = document.getElementById('templateModalLabel');
        if (modalTitle) {
            modalTitle.innerHTML = '<i class="bi bi-pencil"></i> Edit Template';
        }
        
        // Populate form fields
        document.getElementById('template-name').value = configName;
        document.getElementById('template-type').value = template.model_type || 'stable_diffusion';
        document.getElementById('template-description').value = template.description || '';
        
        // Model settings
        if (template.model_settings) {
            document.getElementById('model-checkpoint').value = template.model_settings.checkpoint || '';
            document.getElementById('model-vae').value = template.model_settings.vae || '';
            document.getElementById('model-scheduler').value = template.model_settings.scheduler || 'ddim';
            document.getElementById('model-clip-skip').value = template.model_settings.clip_skip || 1;
        }
        
        // Generation settings
        if (template.generation_settings) {
            document.getElementById('gen-steps').value = template.generation_settings.steps || 20;
            document.getElementById('gen-cfg-scale').value = template.generation_settings.cfg_scale || 7.0;
            document.getElementById('gen-width').value = template.generation_settings.width || 512;
            document.getElementById('gen-height').value = template.generation_settings.height || 512;
            document.getElementById('advanced-sampler').value = template.generation_settings.sampler || 'euler';
            document.getElementById('advanced-restore-faces').value = template.generation_settings.restore_faces ? 'true' : 'false';
            document.getElementById('advanced-tiling').value = template.generation_settings.tiling ? 'true' : 'false';
            document.getElementById('advanced-hires-fix').value = template.generation_settings.hires_fix ? 'true' : 'false';
            document.getElementById('advanced-hires-steps').value = template.generation_settings.hires_steps || 20;
            document.getElementById('advanced-hires-upscaler').value = template.generation_settings.hires_upscaler || 'Latent';
        }
        
        // Prompt templates
        if (template.prompt_templates) {
            document.getElementById('default-prompt').value = template.prompt_templates.default_prompt || '';
            document.getElementById('default-negative-prompt').value = template.prompt_templates.default_negative_prompt || '';
        }
        
        // Store the original config name for updating
        document.getElementById('template-form').dataset.originalName = configName;
    }

    // Delete template
    async deleteTemplate(configName) {
        if (!confirm(`Are you sure you want to delete template "${configName}"?`)) return;

        try {
            const response = await fetch(`/api/configs/${configName}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Template deleted', 'success');
                this.loadTemplates();
            } else {
                throw new Error('Failed to delete template');
            }
        } catch (error) {
            console.error('Delete template error:', error);
            this.showToast('Error deleting template', 'error');
        }
    }

    // Refresh functions
    refreshTemplates() {
        this.loadTemplates();
        this.showToast('Templates refreshed', 'info');
    }

    refreshOutputs() {
        this.loadOutputs();
        this.showToast('Outputs refreshed', 'info');
    }

    refreshDashboard() {
        this.loadInitialData();
        this.showToast('Dashboard refreshed', 'info');
    }

    // Load default settings
    loadDefaultSettings() {
        this.applySettings();
        this.showToast('Settings reset to defaults', 'info');
    }

    // Save template
    async saveTemplate(templateData) {
        try {
            const response = await fetch('/api/configs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(templateData)
            });

            if (response.ok) {
                this.showToast('Template saved successfully', 'success');
                this.loadTemplates();
            } else {
                throw new Error('Failed to save template');
            }
        } catch (error) {
            console.error('Save template error:', error);
            this.showToast('Error saving template', 'error');
        }
    }

    // Update template
    async updateTemplate(originalName, templateData) {
        try {
            const response = await fetch(`/api/configs/${originalName}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(templateData)
            });

            if (response.ok) {
                this.showToast('Template updated successfully', 'success');
                this.loadTemplates();
            } else {
                throw new Error('Failed to update template');
            }
        } catch (error) {
            console.error('Update template error:', error);
            this.showToast('Error updating template', 'error');
        }
    }

    // Modal functions
    openSettingsModal() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
    }

    openBatchModal() {
        const modal = new bootstrap.Modal(document.getElementById('batchModal'));
        modal.show();
    }

    openStatusModal() {
        const modal = new bootstrap.Modal(document.getElementById('statusModal'));
        modal.show();
    }

    openCreateTemplateModal() {
        // Reset form and update title for new template
        document.getElementById('template-form').reset();
        document.getElementById('template-form').dataset.originalName = '';
        const modalTitle = document.getElementById('templateModalLabel');
        if (modalTitle) {
            modalTitle.innerHTML = '<i class="bi bi-plus-circle"></i> Create New Template';
        }
        
        const modal = new bootstrap.Modal(document.getElementById('templateModal'));
        modal.show();
    }

    openOutputsModal() {
        const modal = new bootstrap.Modal(document.getElementById('outputsModal'));
        modal.show();
    }

    // Utility functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    // Toast notification system
    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="bi bi-${this.getToastIcon(type)} me-2"></i>
                    <strong class="me-auto">${this.getToastTitle(type)}</strong>
                    <small>${new Date().toLocaleTimeString()}</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getToastTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };
        return titles[type] || 'Info';
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ForgeDashboard();
});

// Global functions for onclick handlers
function generateImage() {
    window.dashboard?.generateImage();
}

function generateSingle(configName) {
    window.dashboard?.generateSingle(configName);
}

function startBatch(configName) {
    window.dashboard?.startBatch(configName);
}

function openOutputFolder(configName) {
    window.dashboard?.openOutputFolder(configName);
}

function editTemplate(configName) {
    window.dashboard?.editTemplate(configName);
}

function deleteTemplate(configName) {
    window.dashboard?.deleteTemplate(configName);
}

function refreshTemplates() {
    window.dashboard?.refreshTemplates();
}

function refreshOutputs() {
    window.dashboard?.refreshOutputs();
}

function refreshDashboard() {
    window.dashboard?.refreshDashboard();
}

function loadDefaultSettings() {
    window.dashboard?.loadDefaultSettings();
}

function saveSettings() {
    window.dashboard?.saveSettings();
}

function processWildcards() {
    window.dashboard?.processWildcards();
}

function analyzeImage() {
    window.dashboard?.analyzeImage();
}

function stopGeneration() {
    window.dashboard?.stopGeneration();
}

function openSettingsModal() {
    window.dashboard?.openSettingsModal();
}

function openBatchModal() {
    window.dashboard?.openBatchModal();
}

function openStatusModal() {
    window.dashboard?.openStatusModal();
}

function openCreateTemplateModal() {
    window.dashboard?.openCreateTemplateModal();
}

function openOutputsModal() {
    window.dashboard?.openOutputsModal();
} 