#!/usr/bin/env python3
"""
Configs Command

Commands for managing configurations.
"""

from typing import Dict, Any, List
from .base import BaseCommand


class ConfigsListCommand(BaseCommand):
    """Command to list all configurations."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the configs list command."""
        try:
            configs = self.context.config_handler.list_configs()
            
            if not configs:
                print("📋 No configurations found")
                return False
            
            print(f"📋 Found {len(configs)} configurations:")
            print("-" * 50)
            
            for config in configs:
                print(f"📄 {config['name']}")
                print(f"   Model: {config['model']}")
                print(f"   Description: {config['description']}")
                if config.get('has_issues'):
                    print("   ⚠️  Has validation issues")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error listing configurations: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the configs list command."""
        return "List all available configurations."


class ConfigsShowCommand(BaseCommand):
    """Command to show a specific configuration."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the configs show command."""
        try:
            config_name = args.get('config_name')
            if not config_name:
                print("❌ Configuration name required")
                return False
            
            config = self.context.config_handler.load_config(config_name)
            
            print(f"📄 Configuration: {config_name}")
            print("=" * 50)
            
            # Basic info
            print(f"Model: {config.get('model', 'unknown')}")
            print(f"Description: {config.get('description', 'No description')}")
            
            # Prompt settings
            prompt_settings = config.get('prompt_settings', {})
            print(f"\nPrompt Settings:")
            print(f"  Base Prompt: {prompt_settings.get('base_prompt', 'Not set')}")
            print(f"  Negative Prompt: {prompt_settings.get('negative_prompt', 'Not set')}")
            
            # Generation settings
            gen_settings = config.get('generation_settings', {})
            print(f"\nGeneration Settings:")
            print(f"  Steps: {gen_settings.get('steps', 'Not set')}")
            print(f"  CFG Scale: {gen_settings.get('cfg_scale', 'Not set')}")
            print(f"  Width: {gen_settings.get('width', 'Not set')}")
            print(f"  Height: {gen_settings.get('height', 'Not set')}")
            print(f"  Sampler: {gen_settings.get('sampler', 'Not set')}")
            
            # Batch settings
            batch_settings = config.get('batch_settings', {})
            print(f"\nBatch Settings:")
            print(f"  Batch Size: {batch_settings.get('batch_size', 'Not set')}")
            print(f"  Batch Count: {batch_settings.get('batch_count', 'Not set')}")
            
            # Wildcard validation
            if 'missing_wildcards' in config:
                missing = config['missing_wildcards']
                if missing:
                    print(f"\n⚠️  Missing Wildcards:")
                    for wildcard in missing:
                        print(f"    {wildcard}")
                else:
                    print(f"\n✅ All wildcards available")
            
            return True
            
        except Exception as e:
            print(f"❌ Error showing configuration: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the configs show command."""
        return "Show detailed information about a specific configuration."


class ConfigsExportCommand(BaseCommand):
    """Command to export a configuration."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the configs export command."""
        try:
            config_name = args.get('config_name')
            output_file = args.get('output_file')
            
            if not config_name or not output_file:
                print("❌ Configuration name and output file required")
                return False
            
            success = self.context.config_handler.export_config(config_name, output_file)
            
            if success:
                print(f"✅ Configuration '{config_name}' exported to '{output_file}'")
                return True
            else:
                print(f"❌ Failed to export configuration '{config_name}'")
                return False
            
        except Exception as e:
            print(f"❌ Error exporting configuration: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the configs export command."""
        return "Export a configuration to a file."


class ConfigsImportCommand(BaseCommand):
    """Command to import a configuration."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the configs import command."""
        try:
            input_file = args.get('input_file')
            config_name = args.get('name')
            
            if not input_file or not config_name:
                print("❌ Input file and configuration name required")
                return False
            
            success = self.context.config_handler.import_config(input_file, config_name)
            
            if success:
                print(f"✅ Configuration '{config_name}' imported from '{input_file}'")
                return True
            else:
                print(f"❌ Failed to import configuration '{config_name}'")
                return False
            
        except Exception as e:
            print(f"❌ Error importing configuration: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the configs import command."""
        return "Import a configuration from a file."


