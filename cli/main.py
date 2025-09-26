#!/usr/bin/env python3
"""
Refactored CLI Main

Command-line interface using the command pattern for better organization.
"""

import argparse
import sys
from typing import Dict, Any, List

from cli.commands.base import CLIContext
from cli.commands.status_command import StatusCommand
from cli.commands.configs_command import (
    ConfigsListCommand, ConfigsShowCommand, 
    ConfigsExportCommand, ConfigsImportCommand
)
from cli.commands.generate_command import GenerateSingleCommand, GenerateBatchCommand
from cli.commands.api_command import APITestCommand, APISwitchCommand, APIStatusCommand
from core.centralized_logger import logger


class CLIManager:
    """Main CLI manager that handles command routing and execution."""
    
    def __init__(self):
        """Initialize the CLI manager."""
        self.context = CLIContext()
        self.commands = {}
        self._register_commands()
    
    def _register_commands(self):
        """Register all available commands."""
        # Status commands
        self.commands['status'] = StatusCommand(self.context)
        
        # Config commands
        self.commands['configs:list'] = ConfigsListCommand(self.context)
        self.commands['configs:show'] = ConfigsShowCommand(self.context)
        self.commands['configs:export'] = ConfigsExportCommand(self.context)
        self.commands['configs:import'] = ConfigsImportCommand(self.context)
        
        # Generate commands
        self.commands['generate:single'] = GenerateSingleCommand(self.context)
        self.commands['generate:batch'] = GenerateBatchCommand(self.context)
        
        # API commands
        self.commands['api:test'] = APITestCommand(self.context)
        self.commands['api:switch'] = APISwitchCommand(self.context)
        self.commands['api:status'] = APIStatusCommand(self.context)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            description='Forge API Tool - Command Line Interface',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s status
  %(prog)s configs list
  %(prog)s configs show "Quick Start"
  %(prog)s generate single "Quick Start" --prompt "A beautiful landscape"
  %(prog)s generate batch "Quick Start" --batch-size 4 --batches 2
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        
        # Configs commands
        configs_parser = subparsers.add_parser('configs', help='Configuration management')
        configs_subparsers = configs_parser.add_subparsers(dest='configs_command', help='Config commands')
        
        configs_subparsers.add_parser('list', help='List all configurations')
        
        show_parser = configs_subparsers.add_parser('show', help='Show configuration details')
        show_parser.add_argument('config_name', help='Configuration name')
        
        export_parser = configs_subparsers.add_parser('export', help='Export configuration')
        export_parser.add_argument('config_name', help='Configuration name')
        export_parser.add_argument('output_file', help='Output file path')
        
        import_parser = configs_subparsers.add_parser('import', help='Import configuration')
        import_parser.add_argument('input_file', help='Input file path')
        import_parser.add_argument('name', help='Configuration name')
        
        # Generate commands
        generate_parser = subparsers.add_parser('generate', help='Image generation')
        generate_subparsers = generate_parser.add_subparsers(dest='generate_command', help='Generate commands')
        
        single_parser = generate_subparsers.add_parser('single', help='Generate single image')
        single_parser.add_argument('config_name', help='Configuration name')
        single_parser.add_argument('--prompt', help='Custom prompt (overrides config)')
        single_parser.add_argument('--seed', type=int, help='Seed value')
        
        batch_parser = generate_subparsers.add_parser('batch', help='Generate batch of images')
        batch_parser.add_argument('config_name', help='Configuration name')
        batch_parser.add_argument('--batch-size', type=int, default=4, help='Images per batch')
        batch_parser.add_argument('--batches', type=int, default=1, help='Number of batches')
        
        # API commands
        api_parser = subparsers.add_parser('api', help='API management')
        api_subparsers = api_parser.add_subparsers(dest='api_command', help='API commands')
        
        api_subparsers.add_parser('status', help='Show API status')
        api_subparsers.add_parser('test', help='Test API connection')
        
        switch_parser = api_subparsers.add_parser('switch', help='Switch API provider')
        switch_parser.add_argument('provider', choices=['local', 'rundiffusion', 'pinokio', 'mock'], 
                                 help='API provider to switch to')
        
        return parser
    
    def execute_command(self, command_key: str, args: Dict[str, Any]) -> bool:
        """Execute a command by key."""
        if command_key not in self.commands:
            print(f"❌ Unknown command: {command_key}")
            return False
        
        command = self.commands[command_key]
        return command.execute(args)
    
    def run(self, argv: List[str] = None) -> int:
        """Run the CLI with the given arguments."""
        try:
            # Initialize components
            self.context.initialize_components()
            
            # Parse arguments
            parser = self.create_parser()
            args = parser.parse_args(argv)
            
            if not args.command:
                parser.print_help()
                return 1
            
            # Route to appropriate command
            success = False
            
            if args.command == 'status':
                success = self.execute_command('status', {})
            
            elif args.command == 'configs':
                if not args.configs_command:
                    print("❌ Configs subcommand required")
                    return 1
                
                if args.configs_command == 'list':
                    success = self.execute_command('configs:list', {})
                elif args.configs_command == 'show':
                    success = self.execute_command('configs:show', {
                        'config_name': args.config_name
                    })
                elif args.configs_command == 'export':
                    success = self.execute_command('configs:export', {
                        'config_name': args.config_name,
                        'output_file': args.output_file
                    })
                elif args.configs_command == 'import':
                    success = self.execute_command('configs:import', {
                        'input_file': args.input_file,
                        'name': args.name
                    })
                else:
                    print("❌ Invalid configs subcommand")
                    return 1
            
            elif args.command == 'generate':
                if not args.generate_command:
                    print("❌ Generate subcommand required")
                    return 1
                
                if args.generate_command == 'single':
                    success = self.execute_command('generate:single', {
                        'config_name': args.config_name,
                        'prompt': args.prompt,
                        'seed': args.seed
                    })
                elif args.generate_command == 'batch':
                    success = self.execute_command('generate:batch', {
                        'config_name': args.config_name,
                        'batch_size': args.batch_size,
                        'num_batches': args.batches
                    })
                else:
                    print("❌ Invalid generate subcommand")
                    return 1
            
            elif args.command == 'api':
                if not args.api_command:
                    print("❌ API subcommand required")
                    return 1
                
                if args.api_command == 'status':
                    success = self.execute_command('api:status', {})
                elif args.api_command == 'test':
                    success = self.execute_command('api:test', {})
                elif args.api_command == 'switch':
                    success = self.execute_command('api:switch', {
                        'provider': args.provider
                    })
                else:
                    print("❌ Invalid API subcommand")
                    return 1
            
            else:
                print(f"❌ Unknown command: {args.command}")
                return 1
            
            return 0 if success else 1
            
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"❌ CLI error: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = CLIManager()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())


