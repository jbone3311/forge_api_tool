"""
Generation service for the Flask web dashboard.

This module provides business logic for image generation operations,
separating it from the HTTP route handlers.
"""

import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
# These will be passed as instances to the constructor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.prompt_builder import PromptBuilder
from core.wildcard_manager import WildcardManagerFactory
from core.exceptions import (
    ConfigurationError, GenerationError, ValidationError, 
    FileOperationError, JobQueueError
)
from web_dashboard.utils.validators import validate_config_name, validate_batch_parameters, validate_prompt


class GenerationService:
    """
    Service class for image generation operations.
    """
    
    def __init__(self, 
                 config_handler_instance,
                 forge_api_client_instance,
                 output_manager_instance,
                 job_queue_instance,
                 logger_instance,
                 socketio_instance=None):
        """
        Initialize the generation service.
        
        Args:
            config_handler_instance: Instance of config handler
            forge_api_client_instance: Instance of forge API client
            output_manager_instance: Instance of output manager
            job_queue_instance: Instance of job queue
            socketio_instance: Optional SocketIO instance for progress updates
        """
        self.config_handler = config_handler_instance
        self.forge_api_client = forge_api_client_instance
        self.output_manager = output_manager_instance
        self.job_queue = job_queue_instance
        self.logger = logger_instance
        self.socketio = socketio_instance
        
        # Global state for tracking current generation
        self.current_generation = {
            'active': False,
            'current_image': 0,
            'total_images': 0,
            'config_name': '',
            'start_time': None,
            'progress': 0.0
        }
    
    def generate_single_image(self, 
                            config_name: str, 
                            prompt: str = '', 
                            seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a single image.
        
        Args:
            config_name: Name of the configuration to use
            prompt: User-provided prompt (optional)
            seed: Seed value for generation (optional)
            
        Returns:
            Dictionary with generation result
            
        Raises:
            ConfigurationError: If config not found or invalid
            GenerationError: If generation fails
            ValidationError: If input is invalid
        """
        try:
            # Validate inputs
            validate_config_name(config_name)
            if prompt:
                validate_prompt(prompt)
            
            # Get configuration
            try:
                config = self.config_handler.get_config(config_name)
            except FileNotFoundError:
                raise ConfigurationError(f"Configuration '{config_name}' not found")
            
            # Use user-provided prompt or template prompt
            if not prompt:
                prompt = config['prompt_settings']['base_prompt']
            
            # Resolve wildcards if present
            if '__' in prompt:
                wildcard_factory = WildcardManagerFactory()
                prompt_builder = PromptBuilder(wildcard_factory)
                temp_config = {
                    **config, 
                    'prompt_settings': {
                        **config['prompt_settings'], 
                        'base_prompt': prompt
                    }
                }
                resolved_prompts = prompt_builder.preview_prompts(temp_config, 1)
                prompt = resolved_prompts[0] if resolved_prompts else prompt
            
            # Generate image
            success, image_data, info = self.forge_api_client.generate_image(config, prompt, seed)
            
            if success and image_data:
                # Extract seed from info, ensuring it's an integer
                api_seed = info.get('seed') if isinstance(info, dict) else None
                if api_seed is not None:
                    try:
                        final_seed = int(api_seed)
                    except (ValueError, TypeError):
                        final_seed = int(seed) if seed is not None else -1
                else:
                    final_seed = int(seed) if seed is not None else -1
                
                # Save image with embedded metadata
                filepath = self.output_manager.save_image(
                    image_data=image_data,
                    config_name=config_name,
                    prompt=prompt,
                    seed=final_seed,
                    generation_settings=config['generation_settings'],
                    model_settings=config['model_settings']
                )
                
                self.logger.log_app_event("image_generation", {
                    "config_name": config_name,
                    "prompt": prompt,
                    "seed": final_seed,
                    "success": True,
                    "output_path": filepath,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'message': 'Image generated successfully',
                    'filepath': filepath,
                    'info': info
                }
            else:
                error_msg = info.get('error', 'Unknown error') if isinstance(info, dict) and info else 'Generation failed'
                self.logger.log_app_event("image_generation", {
                    "config_name": config_name,
                    "prompt": prompt,
                    "seed": seed,
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
                
                raise GenerationError(error_msg)
                
        except (ConfigurationError, GenerationError, ValidationError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error generating image: {e}")
            raise GenerationError(f"Unexpected error: {e}")
    
    def start_batch_generation(self, 
                             config_name: str,
                             batch_size: int = 1,
                             num_batches: int = 1,
                             prompts: List[str] = None,
                             user_prompt: str = '') -> Dict[str, Any]:
        """
        Start a batch generation job.
        
        Args:
            config_name: Name of the configuration to use
            batch_size: Number of images per batch
            num_batches: Number of batches
            prompts: Pre-generated prompts from preview (optional)
            user_prompt: User-provided prompt (optional)
            
        Returns:
            Dictionary with batch job result
            
        Raises:
            ConfigurationError: If config not found
            ValidationError: If parameters are invalid
            JobQueueError: If job queue operation fails
        """
        try:
            # Validate inputs
            validate_config_name(config_name)
            validate_batch_parameters(batch_size, num_batches)
            if user_prompt:
                validate_prompt(user_prompt)
            
            # Get configuration
            try:
                config = self.config_handler.get_config(config_name)
            except FileNotFoundError:
                raise ConfigurationError(f"Configuration '{config_name}' not found")
            
            # Calculate total images
            total_images = batch_size * num_batches
            
            # If prompts were provided from preview, use them
            if prompts:
                resolved_prompts = prompts
                user_provided = False
                wildcards_resolved = True
            elif user_prompt:
                # Use user-provided prompt (may contain wildcards)
                if '__' in user_prompt:
                    # Resolve wildcards
                    wildcard_factory = WildcardManagerFactory()
                    prompt_builder = PromptBuilder(wildcard_factory)
                    temp_config = {
                        **config, 
                        'prompt_settings': {
                            **config['prompt_settings'], 
                            'base_prompt': user_prompt
                        }
                    }
                    resolved_prompts = prompt_builder.preview_prompts(temp_config, total_images)
                    wildcards_resolved = True
                else:
                    # No wildcards, repeat the same prompt
                    resolved_prompts = [user_prompt] * total_images
                    wildcards_resolved = False
                user_provided = True
            else:
                # Use template's base prompt
                template_prompt = config['prompt_settings']['base_prompt']
                if '__' in template_prompt:
                    # Resolve wildcards
                    wildcard_factory = WildcardManagerFactory()
                    prompt_builder = PromptBuilder(wildcard_factory)
                    resolved_prompts = prompt_builder.preview_prompts(config, total_images)
                    wildcards_resolved = True
                else:
                    # No wildcards, repeat the same prompt
                    resolved_prompts = [template_prompt] * total_images
                    wildcards_resolved = False
                user_provided = False
            
            # Update generation progress
            self.update_generation_progress(0, total_images, config_name)
            
            # Add job to queue with resolved prompts
            job_id = self.job_queue.add_job_with_prompts(config, resolved_prompts)
            
            self.logger.log_queue_operation("job_added", job_id, {
                "config_name": config_name,
                "batch_size": batch_size,
                "num_batches": num_batches,
                "total_images": total_images,
                "user_provided_prompt": user_provided,
                "wildcards_resolved": wildcards_resolved,
                "prompts_provided": len(prompts) > 0 if prompts else False
            })
            
            return {
                'success': True,
                'job_id': job_id,
                'message': f'Batch job {job_id} added to queue',
                'total_images': total_images,
                'wildcards_resolved': wildcards_resolved
            }
            
        except (ConfigurationError, ValidationError, JobQueueError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error starting batch: {e}")
            raise JobQueueError(f"Unexpected error: {e}")
    
    def preview_batch_prompts(self, 
                            config_name: str,
                            batch_size: int = 1,
                            num_batches: int = 1,
                            user_prompt: str = '') -> Dict[str, Any]:
        """
        Preview batch prompts without generating images.
        
        Args:
            config_name: Name of the configuration to use
            batch_size: Number of images per batch
            num_batches: Number of batches
            user_prompt: User-provided prompt (optional)
            
        Returns:
            Dictionary with preview result
            
        Raises:
            ConfigurationError: If config not found
            ValidationError: If parameters are invalid
        """
        try:
            # Validate inputs
            validate_config_name(config_name)
            validate_batch_parameters(batch_size, num_batches)
            if user_prompt:
                validate_prompt(user_prompt)
            
            # Get configuration
            try:
                config = self.config_handler.get_config(config_name)
            except FileNotFoundError:
                raise ConfigurationError(f"Configuration '{config_name}' not found")
            
            # Calculate total prompts needed
            total_prompts = batch_size * num_batches
            
            # If user provided a prompt, use it; otherwise use template's base prompt
            if user_prompt:
                template_prompt = user_prompt
                user_provided = True
            else:
                template_prompt = config['prompt_settings']['base_prompt']
                user_provided = False
            
            # Check if the prompt contains wildcards
            if '__' in template_prompt:
                # Resolve wildcards using PromptBuilder
                wildcard_factory = WildcardManagerFactory()
                prompt_builder = PromptBuilder(wildcard_factory)
                
                # Create a temporary config with the template prompt
                temp_config = {
                    **config, 
                    'prompt_settings': {
                        **config['prompt_settings'], 
                        'base_prompt': template_prompt
                    }
                }
                
                # Generate varied prompts with wildcard resolution
                prompts = prompt_builder.preview_prompts(temp_config, total_prompts)
                wildcards_resolved = True
            else:
                # No wildcards, just repeat the same prompt
                prompts = [template_prompt] * total_prompts
                wildcards_resolved = False
            
            self.logger.log_app_event("batch_preview_generated", {
                "config_name": config_name,
                "batch_size": batch_size,
                "num_batches": num_batches,
                "prompt_count": len(prompts),
                "user_provided_prompt": user_provided,
                "wildcards_resolved": wildcards_resolved,
                "template_used": not user_provided
            })
            
            return {
                'success': True,
                'prompts': prompts,
                'wildcards_resolved': wildcards_resolved,
                'template_used': not user_provided
            }
            
        except (ConfigurationError, ValidationError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error previewing batch: {e}")
            raise ValidationError(f"Unexpected error: {e}")
    
    def stop_generation(self) -> Dict[str, Any]:
        """
        Stop the current generation.
        
        Returns:
            Dictionary with stop result
            
        Raises:
            JobQueueError: If queue operation fails
        """
        try:
            # Stop current generation
            if self.current_generation['active']:
                self.current_generation['active'] = False
                self.current_generation['current_image'] = 0
                self.current_generation['total_images'] = 0
                self.current_generation['progress'] = 0.0
                self.current_generation['config_name'] = ''
                self.current_generation['start_time'] = None
                
                # Clear the job queue
                cleared_count = self.job_queue.clear_queue()
                
                self.logger.log_app_event("generation_stopped", {
                    "cleared_jobs": cleared_count
                })
                
                return {
                    'success': True,
                    'message': f'Generation stopped. {cleared_count} jobs cleared from queue.'
                }
            else:
                return {
                    'success': False,
                    'message': 'No active generation to stop'
                }
                
        except Exception as e:
            self.logger.log_error(f"Failed to stop generation: {e}")
            raise JobQueueError(f"Failed to stop generation: {e}")
    
    def update_generation_progress(self, 
                                 current: int, 
                                 total: int, 
                                 config_name: str = '') -> None:
        """
        Update the current generation progress.
        
        Args:
            current: Current image number
            total: Total number of images
            config_name: Name of the configuration
        """
        self.current_generation['current_image'] = current
        self.current_generation['total_images'] = total
        self.current_generation['config_name'] = config_name
        self.current_generation['progress'] = (current / total * 100) if total > 0 else 0
        
        if current == 1 and total > 0:
            self.current_generation['active'] = True
            self.current_generation['start_time'] = datetime.now()
        
        if current >= total:
            self.current_generation['active'] = False
        
        # Emit progress update via WebSocket if available
        if self.socketio:
            self.socketio.emit('generation_progress', {
                'current': current,
                'total': total,
                'progress': self.current_generation['progress'],
                'config_name': config_name,
                'active': self.current_generation['active']
            })
    
    def get_generation_status(self) -> Dict[str, Any]:
        """
        Get current generation status.
        
        Returns:
            Dictionary with generation status
        """
        try:
            # Get Forge progress if available
            forge_progress = {}
            try:
                forge_progress = self.forge_api_client.get_progress()
            except:
                pass
            
            status = {
                'active': self.current_generation['active'],
                'current_image': self.current_generation['current_image'],
                'total_images': self.current_generation['total_images'],
                'config_name': self.current_generation['config_name'],
                'progress': self.current_generation['progress'],
                'forge_progress': forge_progress,
                'start_time': self.current_generation['start_time'],
                'elapsed_time': None
            }
            
            # Calculate elapsed time
            if self.current_generation['start_time']:
                elapsed = datetime.now() - self.current_generation['start_time']
                status['elapsed_time'] = elapsed.total_seconds()
            
            return status
            
        except Exception as e:
            self.logger.log_error(f"Failed to get generation status: {e}")
            return {
                'active': False,
                'error': str(e)
            } 