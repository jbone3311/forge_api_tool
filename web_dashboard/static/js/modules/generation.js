/**
 * Generation Module
 * Handles all image generation functionality including single generation, batch generation, and progress tracking.
 */

class GenerationManager {
    constructor() {
        this.currentJob = null;
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Generation buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.generate-btn, .generate-single-btn')) {
                const configName = this.getCurrentConfigName();
                if (configName) {
                    this.generateSingle(configName);
                }
            }
            
            if (e.target.matches('.batch-btn, .generate-batch-btn')) {
                const configName = this.getCurrentConfigName();
                if (configName) {
                    this.startBatch(configName);
                }
            }
        });

        // Stop generation button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.stop-generation-btn')) {
                this.stopGeneration();
            }
        });
    }

    getCurrentConfigName() {
        const configSelect = document.getElementById('config-select');
        return configSelect ? configSelect.value : null;
    }

    async generateSingle(configName) {
        if (this.isGenerating) {
            notificationManager.warning('Generation already in progress');
            return;
        }

        const prompt = document.getElementById('prompt-input')?.value;
        if (!prompt?.trim()) {
            notificationManager.warning('Please enter a prompt first');
            return;
        }

        const seedInput = document.getElementById('seed-input')?.value;
        let seed = null;
        if (seedInput?.trim()) {
            const seedNum = parseInt(seedInput);
            if (!isNaN(seedNum)) {
                seed = seedNum;
            }
        }

        const data = {
            config_name: configName,
            prompt: prompt.trim(),
            seed: seed
        };

        this.setGeneratingState(true);
        this.updateGenerationButton('Generating...', true);

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                notificationManager.success('Image generated successfully!');
                this.displayGeneratedImage(result.image_path, result.metadata);
                outputManager.refreshOutputs();
            } else {
                notificationManager.error('Generation failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Generation error:', error);
            notificationManager.error('Generation failed: ' + error.message);
        } finally {
            this.setGeneratingState(false);
            this.updateGenerationButton('Generate', false);
        }
    }

    async startBatch(configName) {
        if (this.isGenerating) {
            notificationManager.warning('Generation already in progress');
            return;
        }

        const prompt = document.getElementById('prompt-input')?.value;
        if (!prompt?.trim()) {
            notificationManager.warning('Please enter a prompt first');
            return;
        }

        const batchSize = parseInt(document.getElementById('batch-size')?.value) || 4;
        const numBatches = parseInt(document.getElementById('num-batches')?.value) || 1;

        const data = {
            config_name: configName,
            prompt: prompt.trim(),
            batch_size: batchSize,
            num_batches: numBatches
        };

        this.setGeneratingState(true);
        this.updateBatchButton('Starting Batch...', true);

        try {
            const response = await fetch('/api/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                notificationManager.success(`Batch generation started! ${batchSize * numBatches} images will be generated.`);
                this.currentJob = result.job_id;
                this.startProgressTracking();
                queueManager.refreshQueue();
            } else {
                notificationManager.error('Batch generation failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Batch generation error:', error);
            notificationManager.error('Batch generation failed: ' + error.message);
        } finally {
            this.setGeneratingState(false);
            this.updateBatchButton('Start Batch', false);
        }
    }

    async stopGeneration() {
        if (!this.currentJob) {
            notificationManager.warning('No active generation to stop');
            return;
        }

        try {
            const response = await fetch(`/api/stop-generation/${this.currentJob}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                notificationManager.info('Generation stopped');
                this.currentJob = null;
                this.stopProgressTracking();
            } else {
                notificationManager.error('Failed to stop generation: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error stopping generation:', error);
            notificationManager.error('Failed to stop generation: ' + error.message);
        }
    }

    setGeneratingState(generating) {
        this.isGenerating = generating;
        
        // Update UI elements
        const generateButtons = document.querySelectorAll('.generate-btn, .generate-single-btn, .batch-btn, .generate-batch-btn');
        const stopButton = document.querySelector('.stop-generation-btn');
        
        generateButtons.forEach(btn => {
            btn.disabled = generating;
        });
        
        if (stopButton) {
            stopButton.style.display = generating ? 'inline-block' : 'none';
        }

        // Update status indicators
        const statusIndicator = document.getElementById('generation-status');
        if (statusIndicator) {
            statusIndicator.textContent = generating ? 'Generating...' : 'Ready';
            statusIndicator.className = generating ? 'status-indicator generating' : 'status-indicator ready';
        }
    }

    updateGenerationButton(text, loading = false) {
        const buttons = document.querySelectorAll('.generate-btn, .generate-single-btn');
        buttons.forEach(btn => {
            btn.textContent = text;
            if (loading) {
                btn.classList.add('loading');
            } else {
                btn.classList.remove('loading');
            }
        });
    }

    updateBatchButton(text, loading = false) {
        const buttons = document.querySelectorAll('.batch-btn, .generate-batch-btn');
        buttons.forEach(btn => {
            btn.textContent = text;
            if (loading) {
                btn.classList.add('loading');
            } else {
                btn.classList.remove('loading');
            }
        });
    }

    displayGeneratedImage(imagePath, metadata) {
        const outputContainer = document.querySelector('.output-container');
        if (!outputContainer) return;

        const imageElement = document.createElement('div');
        imageElement.className = 'output-image';
        imageElement.innerHTML = `
            <img src="${imagePath}" alt="Generated Image" loading="lazy">
            <div class="image-info">
                <div class="image-metadata">
                    <span class="metadata-item">Seed: ${metadata?.seed || 'Random'}</span>
                    <span class="metadata-item">Steps: ${metadata?.steps || 'N/A'}</span>
                    <span class="metadata-item">CFG: ${metadata?.cfg_scale || 'N/A'}</span>
                </div>
                <div class="image-actions">
                    <button class="btn-icon" onclick="outputManager.downloadImage('${imagePath}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-icon" onclick="outputManager.openImageFolder('${imagePath}')" title="Open Folder">
                        <i class="fas fa-folder-open"></i>
                    </button>
                </div>
            </div>
        `;

        // Add to the beginning of the container
        outputContainer.insertBefore(imageElement, outputContainer.firstChild);
    }

    startProgressTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        this.progressInterval = setInterval(async () => {
            if (!this.currentJob) {
                this.stopProgressTracking();
                return;
            }

            try {
                const response = await fetch(`/api/job-status/${this.currentJob}`);
                const result = await response.json();

                if (result.success) {
                    this.updateProgress(result.progress);
                    
                    if (result.status === 'completed') {
                        notificationManager.success('Batch generation completed!');
                        this.currentJob = null;
                        this.stopProgressTracking();
                        outputManager.refreshOutputs();
                        queueManager.refreshQueue();
                    } else if (result.status === 'failed') {
                        notificationManager.error('Batch generation failed: ' + (result.error || 'Unknown error'));
                        this.currentJob = null;
                        this.stopProgressTracking();
                        queueManager.refreshQueue();
                    }
                }
            } catch (error) {
                console.error('Error tracking progress:', error);
            }
        }, 2000); // Check every 2 seconds
    }

    stopProgressTracking() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        this.updateProgress(null);
    }

    updateProgress(progress) {
        const progressBar = document.querySelector('.generation-progress');
        const progressText = document.querySelector('.progress-text');
        
        if (progressBar && progress !== null) {
            progressBar.style.width = `${progress}%`;
            progressBar.style.display = 'block';
        } else if (progressBar) {
            progressBar.style.display = 'none';
        }
        
        if (progressText && progress !== null) {
            progressText.textContent = `${Math.round(progress)}%`;
        }
    }

    // Utility methods for external use
    getCurrentJob() {
        return this.currentJob;
    }

    isCurrentlyGenerating() {
        return this.isGenerating;
    }
}

// Export for use in other modules
window.generationManager = new GenerationManager();
export default window.generationManager; 