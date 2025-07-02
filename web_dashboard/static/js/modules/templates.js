/**
 * Templates Module
 * Handles all template-related functionality including loading, selecting, editing, and managing templates.
 */

class TemplateManager {
    constructor() {
        this.currentTemplate = null;
        this.templates = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTemplates();
    }

    setupEventListeners() {
        // Template card clicks
        document.addEventListener('click', (e) => {
            const templateCard = e.target.closest('.template-card');
            if (templateCard) {
                const configName = templateCard.dataset.config;
                if (configName) {
                    this.selectTemplate(configName);
                }
            }
        });

        // Config select dropdown change
        const configSelect = document.getElementById('config-select');
        if (configSelect) {
            configSelect.addEventListener('change', (e) => {
                const selectedConfig = e.target.value;
                if (selectedConfig) {
                    this.selectTemplate(selectedConfig);
                }
            });
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/configs');
            const data = await response.json();
            
            if (data.success) {
                // Extract configs from the response (they're at the top level, not in a configs field)
                const configs = {};
                for (const [key, value] of Object.entries(data)) {
                    if (key !== 'success' && key !== 'timestamp' && key !== 'message') {
                        configs[key] = value;
                    }
                }
                
                // Store as plain objects, not Map
                this.templates = configs;
                this.renderTemplates();
                this.updateConfigSelect();
            } else {
                console.error('Failed to load templates:', data.error);
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    renderTemplates() {
        const container = document.querySelector('.templates-container');
        if (!container) return;

        container.innerHTML = '';
        
        const templateCount = Object.keys(this.templates).length;
        if (templateCount === 0) {
            container.innerHTML = `
                <div class="no-templates">
                    <i class="fas fa-info-circle"></i>
                    <p>No templates found. Create your first template to get started.</p>
                </div>
            `;
            return;
        }

        Object.entries(this.templates).forEach(([configName, config]) => {
            const templateCard = this.createTemplateCard(configName, config);
            container.appendChild(templateCard);
        });
    }

    createTemplateCard(configName, config) {
        const card = document.createElement('div');
        card.className = 'template-card';
        card.dataset.config = configName;
        
        card.innerHTML = `
            <div class="template-header">
                <h3 class="template-name">${config.name || configName}</h3>
                <div class="template-actions">
                    <button class="btn-icon" onclick="templateManager.editTemplate('${configName}')" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" onclick="templateManager.deleteTemplate('${configName}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="template-info">
                <div class="template-field">
                    <span class="field-label">Description:</span>
                    <span class="field-value">${config.description || 'No description'}</span>
                </div>
                <div class="template-field">
                    <span class="field-label">Model:</span>
                    <span class="field-value">${(config.model_type || 'Unknown').toUpperCase()}</span>
                </div>
                <div class="template-field">
                    <span class="field-label">Checkpoint:</span>
                    <span class="field-value">${config.model_settings?.checkpoint || 'Unknown'}</span>
                </div>
            </div>
            <div class="template-actions-bar">
                <button class="btn btn-sm btn-primary" onclick="generationManager.generateSingle('${configName}')">
                    <i class="fas fa-play"></i> Generate
                </button>
                <button class="btn btn-sm btn-secondary" onclick="generationManager.startBatch('${configName}')">
                    <i class="fas fa-layer-group"></i> Batch
                </button>
                <button class="btn btn-sm btn-info" onclick="outputManager.openOutputFolder('${configName}')" title="Open Output Folder">
                    <i class="fas fa-folder-open"></i> Folder
                </button>
            </div>
        `;
        
        return card;
    }

    updateConfigSelect() {
        const configSelect = document.getElementById('config-select');
        if (!configSelect) return;

        // Clear existing options except the first one
        while (configSelect.children.length > 1) {
            configSelect.removeChild(configSelect.lastChild);
        }

        // Add template options
        Object.entries(this.templates).forEach(([configName, config]) => {
            const option = document.createElement('option');
            option.value = configName;
            option.textContent = config.name || configName;
            configSelect.appendChild(option);
        });
    }

    async selectTemplate(configName) {
        try {
            const response = await fetch(`/api/configs/${configName}`);
            const data = await response.json();
            
            if (data.success && data.config) {
                this.currentTemplate = configName;
                this.populateSettingsFromTemplate(data.config);
                notificationManager.show('Template loaded successfully!', 'success');
            } else {
                notificationManager.show('Failed to load template: ' + (data.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error loading template:', error);
            notificationManager.show('Error loading template: ' + error.message, 'error');
        }
    }

    populateSettingsFromTemplate(config) {
        // Basic settings
        this.setFieldValue('prompt-input', config.prompt_settings?.base_prompt || '');
        this.setFieldValue('negative-prompt-input', config.prompt_settings?.negative_prompt || '');
        this.setFieldValue('seed-input', config.generation_settings?.seed || '');
        this.setFieldValue('config-select', this.currentTemplate);
        
        // Image Settings
        this.setFieldValue('width-input', config.generation_settings?.width || 512);
        this.setFieldValue('height-input', config.generation_settings?.height || 512);
        this.setFieldValue('steps-input', config.generation_settings?.steps || 20);
        this.setFieldValue('cfg-scale-input', config.generation_settings?.cfg_scale || 7.0);
        this.setFieldValue('sampler-input', config.generation_settings?.sampler_name || 'Euler a');
        this.setFieldValue('batch-size-input', config.generation_settings?.batch_size || 1);
        this.setFieldValue('num-batches', config.generation_settings?.num_batches || 1);
        
        // Advanced Settings
        const restoreFaces = config.generation_settings?.restore_faces;
        this.setFieldValue('restore-faces-input', restoreFaces === true ? 'true' : 'false');
        
        const tiling = config.generation_settings?.tiling;
        this.setFieldValue('tiling-input', tiling === true ? 'true' : 'false');
        
        this.setFieldValue('clip-skip-input', config.generation_settings?.clip_skip || 1);
        this.setFieldValue('denoising-strength-input', config.generation_settings?.denoising_strength || 0.7);
        
        // Hires Fix Settings
        const hiresFix = config.generation_settings?.hires_fix;
        this.setFieldValue('hires-fix-input', hiresFix === true ? 'true' : 'false');
        
        this.setFieldValue('hires-upscaler-input', config.generation_settings?.hires_upscaler || 'Latent');
        this.setFieldValue('hires-steps-input', config.generation_settings?.hires_steps || 20);
        this.setFieldValue('hires-denoising-input', config.generation_settings?.hires_denoising || 0.7);
    }

    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
            // Trigger change event for any listeners
            field.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    async editTemplate(configName) {
        try {
            const response = await fetch(`/api/configs/${configName}/settings`);
            const data = await response.json();
            
            if (data.error) {
                notificationManager.show(`Failed to load config: ${data.error}`, 'error');
                return;
            }
            
            // Open template editor modal
            modalManager.open('edit-template-modal');
            // TODO: Populate editor with data.settings
        } catch (error) {
            console.error('Error loading config:', error);
            notificationManager.show('Failed to load config', 'error');
        }
    }

    async deleteTemplate(configName) {
        if (!confirm(`Are you sure you want to delete the template "${configName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/configs/${configName}`, { method: 'DELETE' });
            const data = await response.json();
            
            if (data.success) {
                notificationManager.show('Template deleted successfully', 'success');
                this.loadTemplates(); // Reload templates
            } else {
                notificationManager.show('Failed to delete template', 'error');
            }
        } catch (error) {
            console.error('Failed to delete template:', error);
            notificationManager.show('Failed to delete template', 'error');
        }
    }

    async createTemplate(name, config) {
        try {
            const response = await fetch('/api/configs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, config })
            });
            
            const data = await response.json();
            
            if (data.success) {
                notificationManager.show('Template created successfully', 'success');
                modalManager.close('create-template-modal');
                this.loadTemplates(); // Reload templates
            } else {
                notificationManager.show('Failed to create template', 'error');
            }
        } catch (error) {
            console.error('Failed to create template:', error);
            notificationManager.show('Failed to create template', 'error');
        }
    }

    async updateTemplate(name, config) {
        try {
            const response = await fetch(`/api/configs/${name}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config })
            });
            
            const data = await response.json();
            
            if (data.success) {
                notificationManager.show('Template updated successfully', 'success');
                modalManager.close('edit-template-modal');
                this.loadTemplates(); // Reload templates
            } else {
                notificationManager.show('Failed to update template', 'error');
            }
        } catch (error) {
            console.error('Failed to update template:', error);
            notificationManager.show('Failed to update template', 'error');
        }
    }

    refreshTemplates() {
        this.loadTemplates();
    }
}

// Export for use in other modules
window.templateManager = new TemplateManager();
export default window.templateManager; 