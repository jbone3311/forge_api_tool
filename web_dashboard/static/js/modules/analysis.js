/**
 * Image Analysis Module
 * Handles image analysis, drag and drop, and metadata extraction
 */

class ImageAnalysisManager {
    constructor() {
        this.dropZones = [];
        this.analysisResults = {};
        this.init();
    }

    init() {
        this.setupDropZones();
        this.setupEventListeners();
        console.log('Image Analysis Manager initialized');
    }

    setupDropZones() {
        // Find all drop zones in the document
        this.dropZones = document.querySelectorAll('.image-analysis-dropzone, .dropzone');
        
        this.dropZones.forEach(dropZone => {
            this.setupDropZone(dropZone);
        });
    }

    setupDropZone(dropZone) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.highlight(dropZone), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => this.unhighlight(dropZone), false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => this.handleDrop(e, dropZone), false);

        // Handle click to select file
        dropZone.addEventListener('click', () => this.triggerFileSelect(dropZone), false);
    }

    setupEventListeners() {
        // Listen for new drop zones being added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const newDropZones = node.querySelectorAll('.image-analysis-dropzone, .dropzone');
                        newDropZones.forEach(dropZone => {
                            if (!this.dropZones.includes(dropZone)) {
                                this.dropZones.push(dropZone);
                                this.setupDropZone(dropZone);
                            }
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(elem) {
        elem.classList.add('drag-over');
    }

    unhighlight(elem) {
        elem.classList.remove('drag-over');
    }

    handleDrop(e, dropZone) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            this.handleFiles(files, dropZone);
        }
    }

    triggerFileSelect(dropZone) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.multiple = false;
        input.onchange = (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files, dropZone);
            }
        };
        input.click();
    }

    async handleFiles(files, dropZone) {
        const file = files[0];
        
        if (!file.type.startsWith('image/')) {
            this.showError('Please select an image file');
            return;
        }

        try {
            this.showLoading(dropZone);
            
            // Convert file to base64
            const imageData = await this.fileToBase64(file);
            
            // Analyze the image
            const result = await this.analyzeImage(imageData);
            
            if (result.success) {
                this.displayAnalysisResults(result, dropZone);
                this.showSuccess('Image analyzed successfully!');
            } else {
                this.showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Error handling file:', error);
            this.showError('Failed to analyze image: ' + error.message);
        } finally {
            this.hideLoading(dropZone);
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async analyzeImage(imageData) {
        try {
            const response = await fetch('/api/analyze-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: imageData
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error analyzing image:', error);
            return {
                success: false,
                error: 'Failed to analyze image: ' + error.message
            };
        }
    }

    displayAnalysisResults(result, dropZone) {
        // Store the analysis result
        this.analysisResults[dropZone.id || 'default'] = result;

        // Update the drop zone with analysis info
        this.updateDropZoneDisplay(dropZone, result);

        // Update form fields if they exist
        this.updateFormFields(result);

        // Trigger any custom events
        this.triggerAnalysisComplete(result, dropZone);
    }

    updateDropZoneDisplay(dropZone, result) {
        // Clear existing content
        dropZone.innerHTML = '';

        // Create analysis display
        const display = document.createElement('div');
        display.className = 'analysis-display';

        if (result.width && result.height) {
            display.innerHTML = `
                <div class="analysis-info">
                    <div class="analysis-item">
                        <strong>Size:</strong> ${result.width} × ${result.height}
                    </div>
                    ${result.format ? `<div class="analysis-item"><strong>Format:</strong> ${result.format}</div>` : ''}
                    ${result.parameters ? `<div class="analysis-item"><strong>Parameters:</strong> Found</div>` : ''}
                    ${result.prompt ? `<div class="analysis-item"><strong>Prompt:</strong> Found</div>` : ''}
                </div>
                <button class="btn btn-sm btn-primary" onclick="window.analysisManager.createConfigFromAnalysis('${dropZone.id || 'default'}')">
                    Create Config
                </button>
            `;
        } else {
            display.innerHTML = `
                <div class="analysis-info">
                    <div class="analysis-item text-muted">No analysis data available</div>
                </div>
            `;
        }

        dropZone.appendChild(display);
    }

    updateFormFields(result) {
        // Update prompt field if it exists
        const promptInput = document.getElementById('prompt-input');
        if (promptInput && result.prompt) {
            promptInput.value = result.prompt;
        }

        // Update negative prompt field if it exists
        const negativePromptInput = document.getElementById('negative-prompt-input');
        if (negativePromptInput && result.negative_prompt) {
            negativePromptInput.value = result.negative_prompt;
        }

        // Update other fields based on parameters
        if (result.parameters) {
            this.updateParameterFields(result.parameters);
        }
    }

    updateParameterFields(parameters) {
        // Update seed if available
        if (parameters.seed) {
            const seedInput = document.getElementById('seed-input');
            if (seedInput) {
                seedInput.value = parameters.seed;
            }
        }

        // Update other parameter fields as needed
        // This can be extended based on the UI structure
    }

    async createConfigFromAnalysis(dropZoneId) {
        const result = this.analysisResults[dropZoneId];
        if (!result) {
            this.showError('No analysis result available');
            return;
        }

        try {
            const configName = prompt('Enter a name for the new configuration:');
            if (!configName) return;

            const response = await fetch('/api/configs/create-from-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    config_name: configName,
                    analysis_result: result,
                    custom_settings: {}
                })
            });

            const responseData = await response.json();
            
            if (responseData.success) {
                this.showSuccess(`Configuration "${configName}" created successfully!`);
                // Refresh templates if template manager exists
                if (window.templateManager) {
                    window.templateManager.refreshTemplates();
                }
            } else {
                this.showError(responseData.error || 'Failed to create configuration');
            }
        } catch (error) {
            console.error('Error creating config:', error);
            this.showError('Failed to create configuration: ' + error.message);
        }
    }

    triggerAnalysisComplete(result, dropZone) {
        // Dispatch custom event
        const event = new CustomEvent('imageAnalysisComplete', {
            detail: { result, dropZone }
        });
        document.dispatchEvent(event);
    }

    showLoading(dropZone) {
        dropZone.classList.add('loading');
        dropZone.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Analyzing...</div>';
    }

    hideLoading(dropZone) {
        dropZone.classList.remove('loading');
    }

    showSuccess(message) {
        if (window.notificationManager) {
            window.notificationManager.success(message);
        } else {
            alert(message);
        }
    }

    showError(message) {
        if (window.notificationManager) {
            window.notificationManager.error(message);
        } else {
            alert('Error: ' + message);
        }
    }

    // Public API methods
    getAnalysisResult(dropZoneId = 'default') {
        return this.analysisResults[dropZoneId];
    }

    clearAnalysisResult(dropZoneId = 'default') {
        delete this.analysisResults[dropZoneId];
    }

    refreshDropZones() {
        this.setupDropZones();
    }
}

// Initialize and export
window.analysisManager = new ImageAnalysisManager();
export default window.analysisManager; 