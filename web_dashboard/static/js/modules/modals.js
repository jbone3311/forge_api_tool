/**
 * Modals Module
 * Handles all modal operations including opening, closing, and managing modal states with proper event handling.
 */

class ModalManager {
    constructor() {
        this.activeModals = new Set();
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Close modals on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.close(e.target.id);
            }
        });

        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAll();
            }
        });

        // Prevent modal content clicks from closing the modal
        document.addEventListener('click', (e) => {
            if (e.target.closest('.modal-content')) {
                e.stopPropagation();
            }
        });
    }

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal with id '${modalId}' not found`);
            return false;
        }

        // Close any other active modals
        this.closeAll();

        // Show the modal
        modal.style.display = 'block';
        this.activeModals.add(modalId);

        // Add body scroll lock
        document.body.style.overflow = 'hidden';

        // Focus first input in modal
        const firstInput = modal.querySelector('input, textarea, select, button');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        // Trigger custom event
        modal.dispatchEvent(new CustomEvent('modal:opened', { detail: { modalId } }));

        return true;
    }

    close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal with id '${modalId}' not found`);
            return false;
        }

        // Hide the modal
        modal.style.display = 'none';
        this.activeModals.delete(modalId);

        // Remove body scroll lock if no modals are active
        if (this.activeModals.size === 0) {
            document.body.style.overflow = '';
        }

        // Trigger custom event
        modal.dispatchEvent(new CustomEvent('modal:closed', { detail: { modalId } }));

        return true;
    }

    closeAll() {
        this.activeModals.forEach(modalId => {
            this.close(modalId);
        });
    }

    isOpen(modalId) {
        return this.activeModals.has(modalId);
    }

    getActiveModals() {
        return Array.from(this.activeModals);
    }

    // Utility method to create a modal programmatically
    createModal(id, title, content, options = {}) {
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal';
        
        const sizeClass = options.size ? ` modal-${options.size}` : '';
        
        modal.innerHTML = `
            <div class="modal-content${sizeClass}">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="close-btn" onclick="modalManager.close('${id}')">&times;</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        return modal;
    }

    // Confirm dialog
    confirm(message, title = 'Confirm', options = {}) {
        return new Promise((resolve) => {
            const modalId = 'confirm-modal-' + Date.now();
            const content = `<p>${message}</p>`;
            const footer = `
                <button class="btn btn-secondary" onclick="modalManager.close('${modalId}'); window.confirmResult = false;">${options.cancelText || 'Cancel'}</button>
                <button class="btn btn-primary" onclick="modalManager.close('${modalId}'); window.confirmResult = true;">${options.confirmText || 'Confirm'}</button>
            `;
            
            const modal = this.createModal(modalId, title, content, { footer });
            
            // Listen for close event
            modal.addEventListener('modal:closed', () => {
                const result = window.confirmResult;
                delete window.confirmResult;
                document.body.removeChild(modal);
                resolve(result);
            });
            
            this.open(modalId);
        });
    }

    // Alert dialog
    alert(message, title = 'Alert', options = {}) {
        return new Promise((resolve) => {
            const modalId = 'alert-modal-' + Date.now();
            const content = `<p>${message}</p>`;
            const footer = `
                <button class="btn btn-primary" onclick="modalManager.close('${modalId}'); window.alertResult = true;">${options.okText || 'OK'}</button>
            `;
            
            const modal = this.createModal(modalId, title, content, { footer });
            
            // Listen for close event
            modal.addEventListener('modal:closed', () => {
                document.body.removeChild(modal);
                resolve();
            });
            
            this.open(modalId);
        });
    }

    // Prompt dialog
    prompt(message, defaultValue = '', title = 'Input', options = {}) {
        return new Promise((resolve) => {
            const modalId = 'prompt-modal-' + Date.now();
            const content = `
                <p>${message}</p>
                <input type="text" id="prompt-input-${modalId}" value="${defaultValue}" class="form-control" placeholder="${options.placeholder || ''}">
            `;
            const footer = `
                <button class="btn btn-secondary" onclick="modalManager.close('${modalId}'); window.promptResult = null;">${options.cancelText || 'Cancel'}</button>
                <button class="btn btn-primary" onclick="modalManager.close('${modalId}'); window.promptResult = document.getElementById('prompt-input-${modalId}').value;">${options.okText || 'OK'}</button>
            `;
            
            const modal = this.createModal(modalId, title, content, { footer });
            
            // Listen for close event
            modal.addEventListener('modal:closed', () => {
                const result = window.promptResult;
                delete window.promptResult;
                document.body.removeChild(modal);
                resolve(result);
            });
            
            this.open(modalId);
            
            // Focus input and handle enter key
            setTimeout(() => {
                const input = document.getElementById(`prompt-input-${modalId}`);
                if (input) {
                    input.focus();
                    input.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            window.promptResult = input.value;
                            this.close(modalId);
                        }
                    });
                }
            }, 100);
        });
    }
}

// Export for use in other modules
window.modalManager = new ModalManager();
export default window.modalManager; 