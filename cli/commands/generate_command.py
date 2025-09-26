#!/usr/bin/env python3
"""
Generate Command

Commands for image generation.
"""

import time
from typing import Dict, Any
from .base import BaseCommand


class GenerateSingleCommand(BaseCommand):
    """Command to generate a single image."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the generate single command."""
        try:
            config_name = args.get('config_name')
            prompt = args.get('prompt')
            seed = args.get('seed')
            
            if not config_name:
                print("❌ Configuration name required")
                return False
            
            if not self.context._ensure_api_client():
                print("❌ No API client configured")
                return False
            
            print(f"🎨 Generating single image with config: {config_name}")
            
            # Load configuration
            config = self.context.config_handler.load_config(config_name)
            
            # Build prompt
            if prompt:
                final_prompt = prompt
            else:
                final_prompt = self.context.prompt_builder.build_prompt(config)
            
            print(f"📝 Prompt: {final_prompt}")
            
            # Generate image
            generation_settings = config.get('generation_settings', {})
            result = self.context.forge_client.generate_image(
                prompt=final_prompt,
                negative_prompt=config.get('prompt_settings', {}).get('negative_prompt', ''),
                steps=generation_settings.get('steps', 20),
                cfg_scale=generation_settings.get('cfg_scale', 7.0),
                width=generation_settings.get('width', 512),
                height=generation_settings.get('height', 512),
                sampler=generation_settings.get('sampler', 'Euler a'),
                seed=seed if seed is not None else generation_settings.get('seed', -1)
            )
            
            if result['success']:
                # Save image
                image_info = {
                    'prompt': final_prompt,
                    'config_name': config_name,
                    'seed': seed,
                    'generation_info': result.get('info', {})
                }
                
                saved_path = self.context.output_manager.save_image(result['images'][0], image_info)
                print(f"✅ Image generated and saved to: {saved_path}")
                return True
            else:
                print("❌ Image generation failed")
                return False
            
        except Exception as e:
            print(f"❌ Error in single generation: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the generate single command."""
        return "Generate a single image using the specified configuration."


class GenerateBatchCommand(BaseCommand):
    """Command to generate a batch of images."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the generate batch command."""
        try:
            config_name = args.get('config_name')
            batch_size = args.get('batch_size', 4)
            num_batches = args.get('num_batches', 1)
            
            if not config_name:
                print("❌ Configuration name required")
                return False
            
            if not self.context._ensure_api_client():
                print("❌ No API client configured")
                return False
            
            print(f"🎨 Starting batch generation with config: {config_name}")
            print(f"📊 Batch size: {batch_size}, Number of batches: {num_batches}")
            print()
            
            # Initialize batch runner
            if not self.context.batch_runner:
                from core.batch_runner import BatchRunner
                self.context.batch_runner = BatchRunner()
                self.context.batch_runner.set_forge_client(self.context.forge_client)
            
            # Add job to queue
            job = self.context.batch_runner.add_job(config_name, batch_size, num_batches)
            print(f"📋 Job added to queue: {job.id}")
            
            # Start processing
            self.context.batch_runner.start_processing()
            
            # Monitor progress with timeout protection
            start_time = time.time()
            timeout = 300  # 5 minutes timeout
            batch_count = 0
            
            while self.context.batch_runner.running:
                time.sleep(1)
                elapsed = time.time() - start_time
                
                # Check for timeout
                if elapsed > timeout:
                    print(f"⏰ Timeout reached ({timeout}s), stopping batch processing")
                    self.context.batch_runner.stop_processing()
                    return False
                
                # Report progress every 10 seconds
                if int(elapsed) % 10 == 0 and elapsed > 0:
                    batch_count += 1
                    print(f"⏳ Processing... ({int(elapsed)}s elapsed)")
            
            print("✅ Batch generation completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error in batch generation: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the generate batch command."""
        return "Generate a batch of images using the specified configuration."


