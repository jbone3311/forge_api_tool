#!/usr/bin/env python3
"""
Base Command Classes

Base classes for implementing the command pattern in the CLI.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.centralized_logger import logger


class BaseCommand(ABC):
    """Abstract base class for CLI commands."""
    
    def __init__(self, context: 'CLIContext'):
        """
        Initialize the command.
        
        Args:
            context: CLI context containing dependencies
        """
        self.context = context
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> bool:
        """
        Execute the command.
        
        Args:
            args: Command arguments
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """
        Get help text for the command.
        
        Returns:
            Help text string
        """
        pass


class CLIContext:
    """Context object that holds all CLI dependencies."""
    
    def __init__(self):
        """Initialize the CLI context."""
        self.project_root = None
        self.forge_client = None
        self.batch_runner = None
        self.output_manager = None
        self.wildcard_factory = None
        self.prompt_builder = None
        self.image_analyzer = None
        self.job_queue = None
        
        logger.log_app_event("cli_context_initialized", {
            "context": "CLIContext"
        })
    
    def initialize_components(self):
        """Initialize all CLI components."""
        try:
            from pathlib import Path
            import sys
            
            # Set project root - go up from cli/commands/base.py to project root
            self.project_root = Path(__file__).resolve().parent.parent.parent
            sys.path.insert(0, str(self.project_root))
            
            # Import and initialize components
            from core.unified_config_handler import UnifiedConfigHandler
            from core.unified_prompt_builder import UnifiedPromptBuilder
            from core.unified_api_client import UnifiedAPIClient
            from core.output_manager import OutputManager
            from core.batch_runner import BatchRunner
            from core.image_analyzer import ImageAnalyzer
            from core.job_queue import JobQueue
            from core.api_config import api_config
            
            # Initialize components
            self.config_handler = UnifiedConfigHandler()
            self.output_manager = OutputManager()
            self.prompt_builder = UnifiedPromptBuilder(auto_discover=True)
            self.image_analyzer = ImageAnalyzer()
            self.job_queue = JobQueue()
            
            # Initialize API client if configuration exists
            self._initialize_api_client()
            
            logger.log_app_event("cli_components_initialized", {
                "components": [
                    "config_handler", "output_manager", "prompt_builder",
                    "image_analyzer", "job_queue"
                ]
            })
            
        except Exception as e:
            logger.error(f"Error initializing CLI components: {e}")
            raise
    
    def _initialize_api_client(self):
        """Initialize the API client if configuration is available."""
        try:
            from core.unified_api_client import UnifiedAPIClient
            from core.api_config import api_config
            
            if api_config.base_url:
                self.forge_client = UnifiedAPIClient(use_mock=False)
                if self.batch_runner:
                    self.batch_runner.set_forge_client(self.forge_client)
        except Exception as e:
            logger.warning(f"Could not initialize API client: {e}")
    
    def _ensure_api_client(self):
        """Ensure API client is initialized, re-initializing if needed."""
        if self.forge_client is None:
            from core.api_config import api_config
            if api_config.base_url:
                self._initialize_api_client()
        return self.forge_client is not None
    
    def _can_connect(self) -> bool:
        """Check if API connection is available (silent)."""
        if not self.forge_client:
            return False
        try:
            return bool(self.forge_client.test_connection(silent=True))
        except Exception:
            return False


