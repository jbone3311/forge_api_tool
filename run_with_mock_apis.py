#!/usr/bin/env python3
"""
Run Forge API Tool with Mock APIs
This script runs the main application but with simulated API backends.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config_handler import config_handler
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.mock_forge_api import create_forge_client, get_available_providers
from core.mock_api_provider import MockAPIProviderFactory


class MockForgeApplication:
    """Main application class that uses mock APIs."""
    
    def __init__(self, api_type: str = "local"):
        self.api_type = api_type
        self.api_client = create_forge_client(use_mock=True, api_type=api_type)
        self.output_manager = OutputManager()
        self.wildcard_factory = WildcardManagerFactory()
        self.prompt_builder = PromptBuilder(self.wildcard_factory)
        
        logger.info(f"Mock Forge Application initialized with {api_type} API provider")
    
    def switch_api_provider(self, api_type: str):
        """Switch to a different API provider."""
        self.api_type = api_type
        self.api_client.switch_api_provider(api_type)
        logger.info(f"Switched to {api_type} API provider")
    
    def test_connection(self) -> bool:
        """Test API connection."""
        return self.api_client.test_connection()
    
    def list_configurations(self) -> List[Dict[str, Any]]:
        """List available configurations."""
        return config_handler.list_configs()
    
    def load_configuration(self, config_name: str) -> Dict[str, Any]:
        """Load a specific configuration."""
        return config_handler.load_config(config_name)
    
    def generate_image(self, config_name: str, custom_prompt: str = None, 
                      custom_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a single image."""
        try:
            # Load configuration
            config = self.load_configuration(config_name)
            
            # Override prompt if provided
            if custom_prompt:
                config['prompt_settings']['base_prompt'] = custom_prompt
            
            # Override settings if provided
            if custom_settings:
                config['generation_settings'].update(custom_settings)
            
            # Process wildcards in prompt
            processed_prompt = self.prompt_builder.build_prompt(config)
            config['prompt_settings']['base_prompt'] = processed_prompt
            
            # Prepare payload
            payload = self.api_client._prepare_payload(config)
            
            # Generate image
            success, image_data, metadata = self.api_client.generate_image(payload)
            
            if success:
                # Save image
                output_path = self.output_manager.save_image(
                    image_data, config_name, processed_prompt, 
                    metadata.get('seed', -1), 
                    config['generation_settings'], 
                    config['model_settings']
                )
                
                result = {
                    'success': True,
                    'output_path': output_path,
                    'metadata': metadata,
                    'prompt': processed_prompt,
                    'config_name': config_name,
                    'api_provider': self.api_type
                }
                
                logger.info(f"Image generated successfully: {output_path}")
                return result
            else:
                return {
                    'success': False,
                    'error': 'Generation failed',
                    'api_provider': self.api_type
                }
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_provider': self.api_type
            }
    
    def generate_batch(self, config_name: str, count: int = 4, 
                      custom_prompt: str = None, 
                      custom_settings: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate multiple images in batch."""
        results = []
        
        try:
            # Load configuration
            config = self.load_configuration(config_name)
            
            # Override prompt if provided
            if custom_prompt:
                config['prompt_settings']['base_prompt'] = custom_prompt
            
            # Override settings if provided
            if custom_settings:
                config['generation_settings'].update(custom_settings)
            
            # Generate multiple prompts with wildcards
            prompts = self.prompt_builder.build_prompt_batch(config, count)
            
            for i, prompt in enumerate(prompts):
                # Create config copy for this image
                image_config = config.copy()
                image_config['prompt_settings']['base_prompt'] = prompt
                
                # Prepare payload
                payload = self.api_client._prepare_payload(image_config)
                
                # Generate image
                success, image_data, metadata = self.api_client.generate_image(payload)
                
                if success:
                    # Save image
                    output_path = self.output_manager.save_image(
                        image_data, config_name, prompt, 
                        metadata.get('seed', -1), 
                        config['generation_settings'], 
                        config['model_settings']
                    )
                    
                    results.append({
                        'success': True,
                        'output_path': output_path,
                        'metadata': metadata,
                        'prompt': prompt,
                        'config_name': config_name,
                        'api_provider': self.api_type,
                        'batch_index': i + 1,
                        'total_in_batch': count
                    })
                else:
                    results.append({
                        'success': False,
                        'error': 'Generation failed',
                        'api_provider': self.api_type,
                        'batch_index': i + 1,
                        'total_in_batch': count
                    })
            
            logger.info(f"Batch generation completed: {sum(1 for r in results if r['success'])}/{count} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            return [{
                'success': False,
                'error': str(e),
                'api_provider': self.api_type
            } for _ in range(count)]
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get information about the current API provider."""
        try:
            models = self.api_client.get_models()
            samplers = self.api_client.get_samplers()
            options = self.api_client.get_options()
            
            return {
                'api_type': self.api_type,
                'api_name': self.api_client.mock_provider.name if self.api_client.mock_provider else 'Unknown',
                'is_connected': self.test_connection(),
                'models': models,
                'samplers': samplers,
                'options': options,
                'available_providers': get_available_providers()
            }
        except Exception as e:
            logger.error(f"Error getting API info: {e}")
            return {
                'api_type': self.api_type,
                'error': str(e)
            }
    
    def get_outputs(self) -> Dict[str, Any]:
        """Get output statistics and recent files."""
        return self.output_manager.get_output_statistics()


def main():
    """Main function to run the mock application."""
    parser = argparse.ArgumentParser(description='Run Forge API Tool with Mock APIs')
    parser.add_argument('--api-type', choices=get_available_providers(), 
                       default='local', help='API provider to use')
    parser.add_argument('--config', default='Quick Start', 
                       help='Configuration to use')
    parser.add_argument('--prompt', help='Custom prompt to use')
    parser.add_argument('--batch', type=int, default=1, 
                       help='Number of images to generate')
    parser.add_argument('--list-configs', action='store_true', 
                       help='List available configurations')
    parser.add_argument('--api-info', action='store_true', 
                       help='Show API provider information')
    parser.add_argument('--test-connection', action='store_true', 
                       help='Test API connection')
    parser.add_argument('--outputs', action='store_true', 
                       help='Show output statistics')
    parser.add_argument('--interactive', action='store_true', 
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Initialize application
    app = MockForgeApplication(args.api_type)
    
    print(f"🎭 Forge API Tool - Mock Mode")
    print(f"📡 API Provider: {app.api_type}")
    print(f"🔗 Connected: {app.test_connection()}")
    print()
    
    # Handle command line arguments
    if args.list_configs:
        configs = app.list_configurations()
        print("📋 Available Configurations:")
        for config in configs:
            print(f"  • {config}")
        return
    
    if args.api_info:
        info = app.get_api_info()
        print("📡 API Provider Information:")
        print(f"  Type: {info['api_type']}")
        print(f"  Name: {info.get('api_name', 'Unknown')}")
        print(f"  Connected: {info.get('is_connected', False)}")
        print(f"  Models: {len(info.get('models', []))}")
        print(f"  Samplers: {len(info.get('samplers', []))}")
        print(f"  Available Providers: {', '.join(info.get('available_providers', []))}")
        return
    
    if args.test_connection:
        success = app.test_connection()
        print(f"🔗 Connection Test: {'✅ Success' if success else '❌ Failed'}")
        return
    
    if args.outputs:
        outputs = app.get_outputs()
        print("📁 Output Statistics:")
        print(f"  Total Outputs: {outputs.get('total_outputs', 0)}")
        print(f"  Total Size: {outputs.get('total_size_mb', 0):.2f} MB")
        print(f"  Configs with Outputs: {len(outputs.get('configs_with_outputs', []))}")
        return
    
    if args.interactive:
        run_interactive_mode(app)
        return
    
    # Generate images
    if args.batch > 1:
        print(f"🎨 Generating batch of {args.batch} images...")
        results = app.generate_batch(args.config, args.batch, args.prompt)
        
        print(f"\n📊 Batch Results:")
        successful = sum(1 for r in results if r['success'])
        print(f"  Successful: {successful}/{args.batch}")
        
        for i, result in enumerate(results):
            if result['success']:
                print(f"  {i+1}. ✅ {result['output_path']}")
            else:
                print(f"  {i+1}. ❌ {result.get('error', 'Unknown error')}")
    else:
        print(f"🎨 Generating single image...")
        result = app.generate_image(args.config, args.prompt)
        
        if result['success']:
            print(f"✅ Image generated: {result['output_path']}")
            print(f"📝 Prompt: {result['prompt'][:100]}...")
            print(f"🎯 Seed: {result['metadata'].get('seed', 'Random')}")
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")


def run_interactive_mode(app):
    """Run the application in interactive mode."""
    print("🎮 Interactive Mode - Type 'help' for commands")
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif command == 'help':
                print("""
📚 Available Commands:
  help              - Show this help
  status            - Show application status
  providers         - List available API providers
  switch <provider> - Switch API provider
  configs           - List configurations
  info              - Show API information
  test              - Test API connection
  outputs           - Show output statistics
  generate <config> [prompt] - Generate single image
  batch <config> <count> [prompt] - Generate batch
  exit/quit/q       - Exit application
""")
            
            elif command == 'status':
                connected = app.test_connection()
                outputs = app.get_outputs()
                print(f"🔗 API: {app.api_type} ({'✅ Connected' if connected else '❌ Disconnected'})")
                print(f"📁 Outputs: {outputs.get('total_outputs', 0)} files")
            
            elif command == 'providers':
                providers = get_available_providers()
                print(f"📡 Available Providers: {', '.join(providers)}")
            
            elif command.startswith('switch '):
                provider = command.split(' ', 1)[1]
                if provider in get_available_providers():
                    app.switch_api_provider(provider)
                    print(f"🔄 Switched to {provider} provider")
                else:
                    print(f"❌ Unknown provider: {provider}")
            
            elif command == 'configs':
                configs = app.list_configurations()
                print("📋 Available Configurations:")
                for config in configs:
                    print(f"  • {config}")
            
            elif command == 'info':
                info = app.get_api_info()
                print(f"📡 API: {info.get('api_name', 'Unknown')} ({info['api_type']})")
                print(f"🔗 Connected: {info.get('is_connected', False)}")
                print(f"🎨 Models: {len(info.get('models', []))}")
                print(f"⚙️  Samplers: {len(info.get('samplers', []))}")
            
            elif command == 'test':
                success = app.test_connection()
                print(f"🔗 Connection Test: {'✅ Success' if success else '❌ Failed'}")
            
            elif command == 'outputs':
                outputs = app.get_outputs()
                print(f"📁 Total Outputs: {outputs.get('total_outputs', 0)}")
                print(f"💾 Total Size: {outputs.get('total_size_mb', 0):.2f} MB")
            
            elif command.startswith('generate '):
                parts = command.split(' ', 2)
                if len(parts) >= 2:
                    config = parts[1]
                    prompt = parts[2] if len(parts) > 2 else None
                    
                    print(f"🎨 Generating image with {config}...")
                    result = app.generate_image(config, prompt)
                    
                    if result['success']:
                        print(f"✅ Generated: {result['output_path']}")
                    else:
                        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                else:
                    print("❌ Usage: generate <config> [prompt]")
            
            elif command.startswith('batch '):
                parts = command.split(' ', 3)
                if len(parts) >= 3:
                    config = parts[1]
                    count = int(parts[2])
                    prompt = parts[3] if len(parts) > 3 else None
                    
                    print(f"🎨 Generating batch of {count} images...")
                    results = app.generate_batch(config, count, prompt)
                    
                    successful = sum(1 for r in results if r['success'])
                    print(f"📊 Results: {successful}/{count} successful")
                else:
                    print("❌ Usage: batch <config> <count> [prompt]")
            
            else:
                print(f"❌ Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
