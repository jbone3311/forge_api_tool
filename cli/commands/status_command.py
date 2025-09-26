#!/usr/bin/env python3
"""
Status Command

Command for showing system status.
"""

from typing import Dict, Any
from .base import BaseCommand


class StatusCommand(BaseCommand):
    """Command to show system status."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the status command."""
        try:
            print("📊 System Status")
            print("=" * 40)
            
            # API connection status
            if self.context.forge_client:
                print("🔗 API Connection: Configured")
                if self.context._can_connect():
                    print("   Status: ✅ Connected")
                else:
                    print("   Status: ❌ Disconnected")
            else:
                print("🔗 API Connection: ❌ Not configured")
            
            # Configuration status
            try:
                configs = self.context.config_handler.list_configs()
                print(f"📋 Configurations: {len(configs)} available")
            except Exception:
                print("📋 Configurations: ❌ Error loading")
            
            # Output status
            try:
                stats = self.context.output_manager.get_output_statistics()
                print(f"📁 Outputs: {stats.get('today_count', 0)} files in today's directory")
            except Exception:
                print("📁 Outputs: ❌ Error loading")
            
            # Wildcard status
            try:
                wildcards = self.context.prompt_builder.get_available_wildcards()
                print(f"📄 Wildcards: {len(wildcards)} files available")
            except Exception:
                print("📄 Wildcards: ❌ Error loading")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the status command."""
        return "Show system status including API connection, configurations, outputs, and wildcards."


