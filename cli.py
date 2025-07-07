#!/usr/bin/env python3
"""
Forge API Tool - Command Line Interface

A comprehensive CLI for managing image generation, configurations, wildcards,
and all other features of the Forge API Tool.
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.config_handler import config_handler
from core.forge_api import ForgeAPIClient
from core.batch_runner import BatchRunner
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.image_analyzer import ImageAnalyzer
from core.job_queue import JobQueue
from core.api_config import api_config


class ForgeAPICLI:
    """Command Line Interface for Forge API Tool."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.forge_client = None
        self.batch_runner = None
        self.output_manager = OutputManager()
        self.wildcard_factory = WildcardManagerFactory()
        self.prompt_builder = PromptBuilder(self.wildcard_factory)
        self.image_analyzer = ImageAnalyzer()
        self.job_queue = JobQueue()
        
        # Initialize API client if configuration exists
        self._initialize_api_client()
    
    def _initialize_api_client(self):
        """Initialize the API client if configuration is available."""
        try:
            if api_config.base_url:
                self.forge_client = ForgeAPIClient()
                if self.batch_runner:
                    self.batch_runner.set_forge_client(self.forge_client)
        except Exception as e:
            logger.warning(f"Could not initialize API client: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to the API."""
        if not self.forge_client:
            print("❌ No API client configured")
            return False
        
        try:
            print("🔗 Testing API connection...")
            if self.forge_client.test_connection():
                print("✅ API connection successful")
                return True
            else:
                print("❌ API connection failed")
                return False
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
    
    def list_configs(self) -> None:
        """List all available configurations."""
        try:
            configs = config_handler.list_configs()
            if not configs:
                print("📋 No configurations found")
                return
            
            print(f"📋 Found {len(configs)} configurations:")
            print("-" * 50)
            
            for config_name in configs:
                try:
                    config = config_handler.load_config(config_name)
                    description = config.get('description', 'No description')
                    model_type = config.get('model_type', 'unknown')
                    print(f"📄 {config_name}")
                    print(f"   Model: {model_type}")
                    print(f"   Description: {description}")
                    print()
                except Exception as e:
                    print(f"📄 {config_name} (Error loading: {e})")
                    print()
        except Exception as e:
            print(f"❌ Error listing configurations: {e}")
    
    def show_config(self, config_name: str) -> None:
        """Show detailed information about a configuration."""
        try:
            config = config_handler.load_config(config_name)
            print(f"📄 Configuration: {config_name}")
            print("=" * 60)
            
            # Basic info
            print(f"Name: {config.get('name', 'N/A')}")
            print(f"Description: {config.get('description', 'N/A')}")
            print(f"Model Type: {config.get('model_type', 'N/A')}")
            print()
            
            # Generation settings
            if 'generation_settings' in config:
                print("🎨 Generation Settings:")
                for key, value in config['generation_settings'].items():
                    print(f"  {key}: {value}")
                print()
            
            # Prompt settings
            if 'prompt_settings' in config:
                print("💬 Prompt Settings:")
                print(f"  Base Prompt: {config['prompt_settings'].get('base_prompt', 'N/A')}")
                print(f"  Negative Prompt: {config['prompt_settings'].get('negative_prompt', 'N/A')}")
                print()
            
            # Output settings
            if 'output_settings' in config:
                print("📁 Output Settings:")
                for key, value in config['output_settings'].items():
                    print(f"  {key}: {value}")
                print()
                
        except Exception as e:
            print(f"❌ Error showing configuration: {e}")
    
    def generate_single(self, config_name: str, prompt: str, seed: Optional[int] = None) -> bool:
        """Generate a single image."""
        if not self.forge_client:
            print("❌ No API client configured")
            return False
        
        try:
            print(f"🎨 Generating image with config: {config_name}")
            print(f"💬 Prompt: {prompt}")
            if seed:
                print(f"🌱 Seed: {seed}")
            print()
            
            # Load configuration
            config = config_handler.load_config(config_name)
            
            # Generate image
            success, image_data, info = self.forge_client.generate_image(config, prompt, seed)
            
            if success:
                print("✅ Image generated successfully!")
                
                # Save image
                output_dir = self.output_manager.get_output_directory()
                filename = f"{config_name}_{int(time.time())}.png"
                output_path = os.path.join(output_dir, filename)
                
                if self.forge_client.save_image(image_data, output_path, info):
                    print(f"💾 Image saved to: {output_path}")
                    return True
                else:
                    print("❌ Failed to save image")
                    return False
            else:
                print("❌ Image generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return False
    
    def generate_batch(self, config_name: str, batch_size: int = 4, num_batches: int = 1) -> bool:
        """Generate a batch of images."""
        if not self.forge_client:
            print("❌ No API client configured")
            return False
        
        try:
            print(f"🎨 Starting batch generation with config: {config_name}")
            print(f"📊 Batch size: {batch_size}, Number of batches: {num_batches}")
            print()
            
            # Initialize batch runner
            if not self.batch_runner:
                self.batch_runner = BatchRunner()
                self.batch_runner.set_forge_client(self.forge_client)
            
            # Add job to queue
            job = self.batch_runner.add_job(config_name, batch_size, num_batches)
            print(f"📋 Job added to queue: {job.id}")
            
            # Start processing
            self.batch_runner.start_processing()
            
            # Monitor progress
            while self.batch_runner.running:
                time.sleep(1)
                # Could add progress reporting here
            
            print("✅ Batch generation completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error in batch generation: {e}")
            return False
    
    def list_outputs(self, date: Optional[str] = None, limit: int = 20) -> None:
        """List generated outputs."""
        try:
            output_dir = self.output_manager.get_output_directory(date)
            
            if not os.path.exists(output_dir):
                print(f"📁 No outputs found for date: {date or 'today'}")
                return
            
            files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
            
            if not files:
                print(f"📁 No image files found in: {output_dir}")
                return
            
            print(f"📁 Outputs ({len(files)} files):")
            print("-" * 60)
            
            for i, filename in enumerate(files[:limit]):
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                print(f"{i+1:2d}. {filename}")
                print(f"    Size: {size:,} bytes")
                print(f"    Created: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            
            if len(files) > limit:
                print(f"... and {len(files) - limit} more files")
                
        except Exception as e:
            print(f"❌ Error listing outputs: {e}")
    
    def analyze_image(self, image_path: str) -> None:
        """Analyze an image and extract generation parameters."""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return
            
            print(f"🔍 Analyzing image: {image_path}")
            print()
            
            # Analyze image
            analysis = self.image_analyzer.analyze_image(image_path)
            
            if analysis:
                print("📊 Analysis Results:")
                print("-" * 40)
                
                # Basic info
                if 'basic_info' in analysis:
                    info = analysis['basic_info']
                    print(f"Dimensions: {info.get('width', 'N/A')}x{info.get('height', 'N/A')}")
                    print(f"Format: {info.get('format', 'N/A')}")
                    print(f"Mode: {info.get('mode', 'N/A')}")
                    print()
                
                # Generation parameters
                if 'generation_params' in analysis:
                    params = analysis['generation_params']
                    print("🎨 Generation Parameters:")
                    for key, value in params.items():
                        print(f"  {key}: {value}")
                    print()
                
                # Prompt information
                if 'prompt_info' in analysis:
                    prompt_info = analysis['prompt_info']
                    print("💬 Prompt Information:")
                    print(f"  Prompt: {prompt_info.get('prompt', 'N/A')}")
                    print(f"  Negative Prompt: {prompt_info.get('negative_prompt', 'N/A')}")
                    if prompt_info.get('wildcards'):
                        print(f"  Wildcards: {', '.join(prompt_info['wildcards'])}")
                    print()
                
                # Suggested configuration
                if 'suggested_config' in analysis:
                    print("💡 Suggested Configuration:")
                    config = analysis['suggested_config']
                    print(f"  Model Type: {config.get('model_type', 'N/A')}")
                    print(f"  Steps: {config.get('generation_settings', {}).get('steps', 'N/A')}")
                    print(f"  Sampler: {config.get('generation_settings', {}).get('sampler', 'N/A')}")
                    print()
            else:
                print("❌ Could not analyze image")
                
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
    
    def list_wildcards(self) -> None:
        """List available wildcard files."""
        try:
            wildcard_dir = "wildcards"
            if not os.path.exists(wildcard_dir):
                print("📁 No wildcards directory found")
                return
            
            wildcard_files = []
            for root, dirs, files in os.walk(wildcard_dir):
                for file in files:
                    if file.endswith('.txt'):
                        rel_path = os.path.relpath(os.path.join(root, file), wildcard_dir)
                        wildcard_files.append(rel_path)
            
            if not wildcard_files:
                print("📁 No wildcard files found")
                return
            
            print(f"📁 Found {len(wildcard_files)} wildcard files:")
            print("-" * 40)
            
            for wildcard_file in sorted(wildcard_files):
                filepath = os.path.join(wildcard_dir, wildcard_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f if line.strip()]
                    print(f"📄 {wildcard_file} ({len(lines)} items)")
                except Exception as e:
                    print(f"📄 {wildcard_file} (Error reading: {e})")
            
            print()
            
        except Exception as e:
            print(f"❌ Error listing wildcards: {e}")
    
    def preview_wildcards(self, config_name: str, num_previews: int = 5) -> None:
        """Preview wildcard resolution for a configuration."""
        try:
            config = config_handler.load_config(config_name)
            template = config['prompt_settings']['base_prompt']
            
            print(f"🔍 Wildcard preview for config: {config_name}")
            print(f"💬 Template: {template}")
            print()
            
            # Generate previews
            prompts = []
            for i in range(num_previews):
                resolved_prompt = self.prompt_builder.build_prompt(config)
                prompts.append(resolved_prompt)
            
            print(f"📝 Generated {len(prompts)} previews:")
            print("-" * 50)
            
            for i, prompt in enumerate(prompts, 1):
                print(f"{i}. {prompt}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error previewing wildcards: {e}")
    
    def show_status(self) -> None:
        """Show system status."""
        try:
            print("📊 System Status")
            print("=" * 40)
            
            # API connection status
            if self.forge_client:
                print("🔗 API Connection: Configured")
                if self.test_connection():
                    print("   Status: ✅ Connected")
                else:
                    print("   Status: ❌ Disconnected")
            else:
                print("🔗 API Connection: ❌ Not configured")
            
            print()
            
            # Configuration count
            try:
                configs = config_handler.list_configs()
                print(f"📋 Configurations: {len(configs)} available")
            except Exception as e:
                print(f"📋 Configurations: Error ({e})")
            
            # Output count
            try:
                output_dir = self.output_manager.get_output_directory()
                if os.path.exists(output_dir):
                    files = [f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    print(f"📁 Outputs: {len(files)} files in today's directory")
                else:
                    print("📁 Outputs: No output directory")
            except Exception as e:
                print(f"📁 Outputs: Error ({e})")
            
            # Wildcard count
            try:
                wildcard_dir = "wildcards"
                if os.path.exists(wildcard_dir):
                    wildcard_files = []
                    for root, dirs, files in os.walk(wildcard_dir):
                        wildcard_files.extend([f for f in files if f.endswith('.txt')])
                    print(f"📄 Wildcards: {len(wildcard_files)} files available")
                else:
                    print("📄 Wildcards: No wildcards directory")
            except Exception as e:
                print(f"📄 Wildcards: Error ({e})")
            
            print()
            
        except Exception as e:
            print(f"❌ Error showing status: {e}")
    
    def export_config(self, config_name: str, output_file: str) -> bool:
        """Export a configuration to a file."""
        try:
            config = config_handler.load_config(config_name)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuration exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting configuration: {e}")
            return False
    
    def import_config(self, input_file: str, config_name: Optional[str] = None) -> bool:
        """Import a configuration from a file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not config_name:
                config_name = config.get('name', os.path.splitext(os.path.basename(input_file))[0])
            
            config_handler.save_config(config_name, config)
            print(f"✅ Configuration imported as: {config_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing configuration: {e}")
            return False

    def fix_wildcard_encoding(self, wildcards_dir: str = "wildcards", dry_run: bool = False) -> Dict[str, any]:
        """Fix encoding issues in all wildcard files."""
        try:
            # Import the wildcard encoding fix functions
            from scripts.fix_wildcard_encoding import fix_all_wildcard_encoding
            
            print("🔧 Fixing wildcard encoding issues...")
            
            # Run the comprehensive wildcard encoding fix
            results = fix_all_wildcard_encoding(wildcards_dir, dry_run)
            
            return results
                
        except Exception as e:
            print(f"❌ Error fixing wildcard encoding: {e}")
            return {
                "total_files": 0,
                "files_checked": 0,
                "files_fixed": 0,
                "files_with_errors": 1,
                "errors": [f"Script execution error: {e}"],
                "fixed_files": [],
                "skipped_files": [],
                "verification_errors": []
            }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Forge API Tool - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  forge-cli status                    # Show system status
  forge-cli configs list              # List all configurations
  forge-cli configs show my_config    # Show configuration details
  forge-cli generate single my_config "a beautiful landscape"  # Generate single image
  forge-cli generate batch my_config --batch-size 4 --batches 2  # Generate batch
  forge-cli outputs list              # List generated outputs
  forge-cli analyze image.png         # Analyze an image
  forge-cli wildcards list            # List wildcard files
  forge-cli wildcards preview my_config  # Preview wildcard resolution
  forge-cli wildcards fix-encoding --dry-run  # Check wildcard encoding issues
  forge-cli wildcards fix-encoding    # Fix wildcard encoding issues
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Configs commands
    configs_parser = subparsers.add_parser('configs', help='Configuration management')
    configs_subparsers = configs_parser.add_subparsers(dest='configs_command')
    
    configs_subparsers.add_parser('list', help='List all configurations')
    
    show_parser = configs_subparsers.add_parser('show', help='Show configuration details')
    show_parser.add_argument('config_name', help='Configuration name')
    
    export_parser = configs_subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('config_name', help='Configuration name')
    export_parser.add_argument('output_file', help='Output file path')
    
    import_parser = configs_subparsers.add_parser('import', help='Import configuration')
    import_parser.add_argument('input_file', help='Input file path')
    import_parser.add_argument('--name', help='Configuration name (optional)')
    
    # Generate commands
    generate_parser = subparsers.add_parser('generate', help='Image generation')
    generate_subparsers = generate_parser.add_subparsers(dest='generate_command')
    
    single_parser = generate_subparsers.add_parser('single', help='Generate single image')
    single_parser.add_argument('config_name', help='Configuration name')
    single_parser.add_argument('prompt', help='Generation prompt')
    single_parser.add_argument('--seed', type=int, help='Random seed')
    
    batch_parser = generate_subparsers.add_parser('batch', help='Generate batch of images')
    batch_parser.add_argument('config_name', help='Configuration name')
    batch_parser.add_argument('--batch-size', type=int, default=4, help='Images per batch')
    batch_parser.add_argument('--batches', type=int, default=1, help='Number of batches')
    
    # Outputs commands
    outputs_parser = subparsers.add_parser('outputs', help='Output management')
    outputs_subparsers = outputs_parser.add_subparsers(dest='outputs_command')
    
    outputs_subparsers.add_parser('list', help='List generated outputs')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Image analysis')
    analyze_parser.add_argument('image_path', help='Path to image file')
    
    # Wildcards commands
    wildcards_parser = subparsers.add_parser('wildcards', help='Wildcard management')
    wildcards_subparsers = wildcards_parser.add_subparsers(dest='wildcards_command')
    
    wildcards_subparsers.add_parser('list', help='List wildcard files')
    
    preview_parser = wildcards_subparsers.add_parser('preview', help='Preview wildcard resolution')
    preview_parser.add_argument('config_name', help='Configuration name')
    preview_parser.add_argument('--count', type=int, default=5, help='Number of previews')
    
    fix_parser = wildcards_subparsers.add_parser('fix-encoding', help='Fix encoding issues in wildcard files')
    fix_parser.add_argument('--wildcards-dir', default='wildcards', help='Wildcards directory (default: wildcards)')
    fix_parser.add_argument('--dry-run', action='store_true', help='Check files without making changes')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test API connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = ForgeAPICLI()
    
    try:
        # Execute commands
        if args.command == 'status':
            cli.show_status()
        
        elif args.command == 'configs':
            if args.configs_command == 'list':
                cli.list_configs()
            elif args.configs_command == 'show':
                cli.show_config(args.config_name)
            elif args.configs_command == 'export':
                cli.export_config(args.config_name, args.output_file)
            elif args.configs_command == 'import':
                cli.import_config(args.input_file, args.name)
        
        elif args.command == 'generate':
            if args.generate_command == 'single':
                cli.generate_single(args.config_name, args.prompt, args.seed)
            elif args.generate_command == 'batch':
                cli.generate_batch(args.config_name, args.batch_size, args.batches)
        
        elif args.command == 'outputs':
            if args.outputs_command == 'list':
                cli.list_outputs()
        
        elif args.command == 'analyze':
            cli.analyze_image(args.image_path)
        
        elif args.command == 'wildcards':
            if args.wildcards_command == 'list':
                cli.list_wildcards()
            elif args.wildcards_command == 'preview':
                cli.preview_wildcards(args.config_name, args.count)
            elif args.wildcards_command == 'fix-encoding':
                cli.fix_wildcard_encoding(args.wildcards_dir, args.dry_run)
        
        elif args.command == 'test':
            cli.test_connection()
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 