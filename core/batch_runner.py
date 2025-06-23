import os
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import random

from config_handler import ConfigHandler
from wildcard_manager import WildcardManagerFactory
from prompt_builder import PromptBuilder
from forge_api import ForgeAPIClient
from job_queue import JobQueue, Job


class BatchRunner:
    """Orchestrates batch image generation using the job queue."""
    
    def __init__(self, config_dir: str = "configs", output_dir: str = "outputs"):
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.config_handler = ConfigHandler(config_dir)
        self.wildcard_factory = WildcardManagerFactory()
        self.prompt_builder = PromptBuilder(self.wildcard_factory)
        self.job_queue = JobQueue()
        self.forge_client = None
        self.running = False
        self.worker_thread = None
        self.progress_callback = None
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def set_forge_client(self, forge_client: ForgeAPIClient):
        """Set the Forge API client."""
        self.forge_client = forge_client
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set a callback for progress updates."""
        self.progress_callback = callback
    
    def add_job(self, config_name: str, batch_size: int = None, num_batches: int = None) -> Job:
        """Add a job to the queue."""
        return self.job_queue.add_job(config_name, batch_size, num_batches)
    
    def start_processing(self):
        """Start processing jobs in the queue."""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def stop_processing(self):
        """Stop processing jobs."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
    
    def cancel_current_job(self):
        """Cancel the currently running job."""
        self.job_queue.cancel_current_job()
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of the job queue."""
        return self.job_queue.get_queue_stats()
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific job."""
        job = self.job_queue.get_job(job_id)
        if job:
            return job.to_dict()
        return None
    
    def _process_queue(self):
        """Main processing loop for the job queue."""
        while self.running:
            try:
                # Get next job
                job = self.job_queue.start_next_job()
                if not job:
                    time.sleep(1)  # No jobs to process
                    continue
                
                # Process the job
                self._process_job(job)
                
            except Exception as e:
                print(f"Error in queue processing: {e}")
                if self.job_queue.current_job:
                    self.job_queue.fail_current_job(str(e))
                time.sleep(1)
    
    def _process_job(self, job: Job):
        """Process a single job."""
        try:
            # Load configuration
            config = self.config_handler.load_config(job.config_name)
            
            # Override batch settings if specified
            if job.batch_size:
                config['generation_settings']['batch_size'] = job.batch_size
            if job.num_batches:
                config['generation_settings']['num_batches'] = job.num_batches
            
            # Validate configuration
            if self.forge_client:
                is_valid, errors = self.forge_client.validate_config(config)
                if not is_valid:
                    raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
            
            # Calculate total images
            batch_size = config['generation_settings']['batch_size']
            num_batches = config['generation_settings']['num_batches']
            total_images = batch_size * num_batches
            
            job.total_images = total_images
            self.job_queue.save_queue()
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(
                self.output_dir,
                config['name'],
                timestamp
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # Process each batch
            for batch_num in range(num_batches):
                if not self.running or job.status.value == "cancelled":
                    break
                
                # Generate prompts for this batch
                prompts = self.prompt_builder.build_prompt_batch(config, batch_size)
                
                # Generate seeds if needed
                seeds = self._generate_seeds(config, batch_size)
                
                # Generate images
                if self.forge_client:
                    results = self.forge_client.generate_batch(config, prompts, seeds)
                else:
                    # Mock results for testing
                    results = [(True, "mock_image_data", {}) for _ in prompts]
                
                # Save images and update progress
                for i, (success, image_data, info) in enumerate(results):
                    if not self.running or job.status.value == "cancelled":
                        break
                    
                    current_image = batch_num * batch_size + i + 1
                    
                    if success and image_data:
                        # Save image
                        image_filename = f"image_{current_image:04d}.png"
                        image_path = os.path.join(output_dir, image_filename)
                        
                        if self.forge_client:
                            self.forge_client.save_image(image_data, image_path, info)
                        else:
                            # Mock save for testing
                            with open(image_path, 'w') as f:
                                f.write("mock_image")
                        
                        # Add to job outputs
                        self.job_queue.add_current_job_output(image_path)
                        
                        # Save prompt info
                        if config['output_settings'].get('save_prompts', True):
                            prompt_filename = f"prompt_{current_image:04d}.txt"
                            prompt_path = os.path.join(output_dir, prompt_filename)
                            with open(prompt_path, 'w', encoding='utf-8') as f:
                                f.write(f"Prompt: {prompts[i]}\n")
                                f.write(f"Seed: {seeds[i] if seeds else 'random'}\n")
                                f.write(f"Config: {job.config_name}\n")
                                f.write(f"Batch: {batch_num + 1}/{num_batches}\n")
                                f.write(f"Image: {i + 1}/{batch_size}\n")
                    else:
                        # Handle failed generation
                        error_msg = info.get('error', 'Unknown error')
                        self.job_queue.add_current_job_error(f"Image {current_image}: {error_msg}")
                        job.failed_images += 1
                    
                    # Update progress
                    self.job_queue.update_current_job_progress(
                        batch_num + 1, current_image, total_images
                    )
                    
                    # Call progress callback
                    if self.progress_callback:
                        progress_data = {
                            'job_id': job.id,
                            'config_name': job.config_name,
                            'current_batch': batch_num + 1,
                            'current_image': current_image,
                            'total_images': total_images,
                            'progress_percent': (current_image / total_images) * 100,
                            'status': 'running'
                        }
                        self.progress_callback(progress_data)
                
                # Small delay between batches
                time.sleep(0.5)
            
            # Mark job as completed
            self.job_queue.complete_current_job()
            
            # Call final progress callback
            if self.progress_callback:
                progress_data = {
                    'job_id': job.id,
                    'config_name': job.config_name,
                    'current_batch': num_batches,
                    'current_image': total_images,
                    'total_images': total_images,
                    'progress_percent': 100.0,
                    'status': 'completed'
                }
                self.progress_callback(progress_data)
                
        except Exception as e:
            error_msg = f"Job processing failed: {e}"
            print(error_msg)
            self.job_queue.fail_current_job(error_msg)
    
    def _generate_seeds(self, config: Dict[str, Any], count: int) -> List[int]:
        """Generate seeds for image generation."""
        seed_setting = config['generation_settings']['seed']
        
        if seed_setting == "random":
            return [random.randint(1, 2147483647) for _ in range(count)]
        elif isinstance(seed_setting, int):
            return [seed_setting + i for i in range(count)]
        else:
            return [random.randint(1, 2147483647) for _ in range(count)]
    
    def preview_job(self, config_name: str, count: int = 5) -> Dict[str, Any]:
        """Preview what a job would generate."""
        try:
            config = self.config_handler.load_config(config_name)
            prompts = self.prompt_builder.preview_prompts(config, count)
            
            return {
                'config_name': config_name,
                'prompts': prompts,
                'total_images': count,
                'config_summary': self.config_handler.get_config_summary(config)
            }
        except Exception as e:
            return {
                'error': str(e),
                'config_name': config_name
            }
    
    def get_wildcard_usage(self, config_name: str) -> Dict[str, Any]:
        """Get wildcard usage statistics for a config."""
        try:
            config = self.config_handler.load_config(config_name)
            return self.prompt_builder.get_wildcard_usage_info(config)
        except Exception as e:
            return {'error': str(e)}
    
    def reset_wildcards(self, config_name: str):
        """Reset wildcard usage for a config."""
        try:
            config = self.config_handler.load_config(config_name)
            self.prompt_builder.reset_wildcards(config)
        except Exception as e:
            print(f"Error resetting wildcards: {e}")
    
    def export_prompt_list(self, config_name: str, count: int) -> List[Dict[str, Any]]:
        """Export a list of prompts that would be generated."""
        try:
            config = self.config_handler.load_config(config_name)
            return self.prompt_builder.export_prompt_list(config, count)
        except Exception as e:
            print(f"Error exporting prompt list: {e}")
            return []
    
    def clear_completed_jobs(self):
        """Clear completed jobs from the queue."""
        self.job_queue.clear_completed_jobs()
    
    def clear_all_jobs(self):
        """Clear all jobs from the queue."""
        self.job_queue.clear_all_jobs() 