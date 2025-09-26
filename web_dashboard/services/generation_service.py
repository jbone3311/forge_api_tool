#!/usr/bin/env python3
"""
Generation Service

Handles image generation business logic.
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.centralized_logger import logger


class GenerationService:
    """Service for handling image generation."""
    
    def __init__(self, app_context):
        """
        Initialize the generation service.
        
        Args:
            app_context: Application context containing dependencies
        """
        self.context = app_context
        self._running_jobs = {}
        
        logger.log_app_event("generation_service_initialized", {
            "service": "GenerationService"
        })
    
    def create_generation_job(self, job_data: Dict[str, Any]) -> int:
        """
        Create a new generation job.
        
        Args:
            job_data: Job configuration data
            
        Returns:
            Job ID
        """
        job_id = self.context.add_job(job_data)
        
        # Start processing the job in background
        thread = threading.Thread(
            target=self._process_job,
            args=(job_id,),
            daemon=True
        )
        thread.start()
        
        return job_id
    
    def _process_job(self, job_id: int):
        """Process a generation job in the background."""
        job = self.context.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        try:
            # Update job status
            self.context.update_job_status(job_id, 'running', 0)
            
            # Load configuration
            config_handler = self.context.get_config_handler()
            settings_info = config_handler.get_setting(job['config_name'])
            
            if not settings_info:
                raise Exception(f"Settings '{job['config_name']}' not found")
            
            config = settings_info['config']
            
            # Build prompts
            prompt_builder = self.context.get_prompt_builder()
            api_client = self.context.get_api_client()
            output_manager = self.context.get_output_manager()
            
            total_images = job['batch_size'] * job['batch_count']
            generated_images = 0
            
            for batch_num in range(job['batch_count']):
                # Build prompt for this batch
                prompt = prompt_builder.build_prompt(config)
                negative_prompt = config.get('prompt_settings', {}).get('negative_prompt', '')
                
                # Override with job-specific values if provided
                if job['prompt']:
                    prompt = job['prompt']
                if job['negative_prompt']:
                    negative_prompt = job['negative_prompt']
                
                # Generate batch
                generation_settings = config.get('generation_settings', {})
                results = api_client.generate_batch(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    steps=job.get('steps', generation_settings.get('steps', 20)),
                    cfg_scale=job.get('cfg_scale', generation_settings.get('cfg_scale', 7.0)),
                    width=job.get('width', generation_settings.get('width', 512)),
                    height=job.get('height', generation_settings.get('height', 512)),
                    sampler=generation_settings.get('sampler', 'Euler a'),
                    seed=job.get('seed', generation_settings.get('seed', -1)),
                    batch_size=job['batch_size']
                )
                
                # Save images
                for result in results:
                    if result['success']:
                        for image_data in result['images']:
                            # Save image
                            image_info = {
                                'prompt': prompt,
                                'negative_prompt': negative_prompt,
                                'config_name': job['config_name'],
                                'job_id': job_id,
                                'batch_index': result.get('batch_index', 0),
                                'provider': result.get('provider', 'unknown'),
                                'generation_info': result.get('info', {})
                            }
                            
                            saved_path = output_manager.save_image(
                                image_data, 
                                image_info
                            )
                            
                            generated_images += 1
                            
                            # Update progress
                            progress = int((generated_images / total_images) * 100)
                            self.context.update_job_status(job_id, 'running', progress)
                            
                            logger.info(f"Generated image {generated_images}/{total_images} for job {job_id}")
                
                # Small delay between batches
                if batch_num < job['batch_count'] - 1:
                    time.sleep(1)
            
            # Mark job as completed
            self.context.update_job_status(
                job_id, 
                'completed', 
                100,
                completed_at=datetime.now().isoformat(),
                total_images=generated_images
            )
            
            logger.log_app_event("job_completed", {
                "job_id": job_id,
                "total_images": generated_images,
                "config_name": job['config_name']
            })
            
        except Exception as e:
            # Mark job as failed
            self.context.update_job_status(
                job_id,
                'failed',
                error=str(e),
                failed_at=datetime.now().isoformat()
            )
            
            logger.error(f"Job {job_id} failed: {e}")
    
    def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get the status of a job."""
        return self.context.get_job(job_id)
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs."""
        return self.context.get_all_jobs()
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all active jobs."""
        return self.context.get_active_jobs()
    
    def cancel_job(self, job_id: int) -> bool:
        """Cancel a job (if possible)."""
        job = self.context.get_job(job_id)
        if not job:
            return False
        
        if job['status'] in ['pending', 'running']:
            self.context.update_job_status(
                job_id,
                'cancelled',
                cancelled_at=datetime.now().isoformat()
            )
            return True
        
        return False
    
    def preview_prompt(self, config_name: str, count: int = 5) -> List[str]:
        """Preview prompts for a configuration."""
        try:
            config_handler = self.context.get_config_handler()
            settings_info = config_handler.get_setting(config_name)
            
            if not settings_info:
                return []
            
            config = settings_info['config']
            prompt_builder = self.context.get_prompt_builder()
            
            return prompt_builder.preview_prompts(config, count)
            
        except Exception as e:
            logger.error(f"Error previewing prompts for {config_name}: {e}")
            return []
    
    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """Validate a configuration."""
        try:
            config_handler = self.context.get_config_handler()
            settings_info = config_handler.get_setting(config_name)
            
            if not settings_info:
                return {
                    'valid': False,
                    'error': f"Configuration '{config_name}' not found"
                }
            
            config = settings_info['config']
            prompt_builder = self.context.get_prompt_builder()
            
            # Validate prompt
            validation_result = prompt_builder.validate_config_prompt(config)
            
            return {
                'valid': validation_result['validation_passed'],
                'wildcard_info': validation_result,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error validating config {config_name}: {e}")
            return {
                'valid': False,
                'error': str(e)
            }


