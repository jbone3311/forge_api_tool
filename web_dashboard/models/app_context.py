#!/usr/bin/env python3
"""
Application Context

Manages application state and dependency injection for the web dashboard.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.unified_config_handler import UnifiedConfigHandler
from core.unified_prompt_builder import UnifiedPromptBuilder
from core.unified_api_client import UnifiedAPIClient
from core.output_manager import OutputManager
from core.centralized_logger import logger


class AppContext:
    """
    Application context that manages all dependencies and state.
    """
    
    def __init__(self, project_root: str = None):
        """
        Initialize the application context.
        
        Args:
            project_root: Root directory of the project (auto-detected if None)
        """
        if project_root is None:
            # Auto-detect project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
        
        self.project_root = project_root
        self._initialize_components()
        self._initialize_state()
        
        logger.log_app_event("app_context_initialized", {
            "project_root": self.project_root,
            "components": list(self._components.keys())
        })
    
    def _initialize_components(self):
        """Initialize all application components."""
        self._components = {}
        
        # Configuration handler
        config_dir = os.path.join(self.project_root, "configs")
        
        self._components['config_handler'] = UnifiedConfigHandler(
            config_dir=config_dir
        )
        
        # Prompt builder with auto-discovery
        wildcards_dir = os.path.join(self.project_root, "wildcards")
        usage_file = os.path.join(self.project_root, "wildcard_usage.json")
        
        self._components['prompt_builder'] = UnifiedPromptBuilder(
            wildcards_base_dir=wildcards_dir,
            usage_file=usage_file,
            auto_discover=True
        )
        
        # Output manager
        outputs_dir = os.path.join(self.project_root, "outputs")
        self._components['output_manager'] = OutputManager(outputs_dir)
        
        # API client (mock by default)
        self._components['api_client'] = UnifiedAPIClient(
            use_mock=True,
            mock_provider_name="Clean App Mock Provider"
        )
    
    def _initialize_state(self):
        """Initialize application state."""
        self.state = {
            'job_queue': {
                'jobs': [],
                'next_id': 1
            },
            'current_api_type': 'local',
            'active_connections': set(),
            'startup_time': datetime.now().isoformat()
        }
    
    def get_component(self, name: str) -> Any:
        """Get a component by name."""
        return self._components.get(name)
    
    def set_component(self, name: str, component: Any):
        """Set a component by name."""
        self._components[name] = component
    
    def get_config_handler(self) -> UnifiedConfigHandler:
        """Get the configuration handler."""
        return self._components['config_handler']
    
    def get_prompt_builder(self) -> UnifiedPromptBuilder:
        """Get the prompt builder."""
        return self._components['prompt_builder']
    
    def get_output_manager(self) -> OutputManager:
        """Get the output manager."""
        return self._components['output_manager']
    
    def get_api_client(self) -> UnifiedAPIClient:
        """Get the API client."""
        return self._components['api_client']
    
    def switch_api_provider(self, provider_type: str):
        """Switch API provider."""
        if provider_type == 'mock':
            self._components['api_client'].switch_to_mock(f"Mock {provider_type.title()} Provider")
        else:
            self._components['api_client'].switch_to_real()
        
        self.state['current_api_type'] = provider_type
        
        logger.log_app_event("api_provider_switched", {
            "new_provider": provider_type,
            "context": "app_context"
        })
    
    def get_job_queue(self) -> Dict[str, Any]:
        """Get the job queue."""
        return self.state['job_queue']
    
    def add_job(self, job_data: Dict[str, Any]) -> int:
        """Add a job to the queue and return job ID."""
        job_queue = self.state['job_queue']
        job_id = job_queue['next_id']
        job_queue['next_id'] += 1
        
        job = {
            'id': job_id,
            'config_name': job_data.get('config_name', 'default'),
            'prompt': job_data.get('prompt', ''),
            'negative_prompt': job_data.get('negative_prompt', ''),
            'steps': job_data.get('steps', 20),
            'cfg_scale': job_data.get('cfg_scale', 7.0),
            'width': job_data.get('width', 512),
            'height': job_data.get('height', 512),
            'seed': job_data.get('seed', -1),
            'batch_size': job_data.get('batch_size', 1),
            'batch_count': job_data.get('batch_count', 1),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'progress': 0,
            'api_provider': self.state['current_api_type']
        }
        
        job_queue['jobs'].append(job)
        
        logger.log_app_event("job_added", {
            "job_id": job_id,
            "config_name": job['config_name'],
            "batch_size": job['batch_size']
        })
        
        return job_id
    
    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a job by ID."""
        job_queue = self.state['job_queue']
        for job in job_queue['jobs']:
            if job['id'] == job_id:
                return job
        return None
    
    def update_job_status(self, job_id: int, status: str, progress: int = None, **kwargs):
        """Update job status and other fields."""
        job = self.get_job(job_id)
        if job:
            job['status'] = status
            if progress is not None:
                job['progress'] = progress
            
            # Update any additional fields
            for key, value in kwargs.items():
                job[key] = value
            
            logger.log_app_event("job_status_updated", {
                "job_id": job_id,
                "status": status,
                "progress": progress
            })
    
    def get_all_jobs(self) -> list:
        """Get all jobs."""
        return self.state['job_queue']['jobs']
    
    def get_active_jobs(self) -> list:
        """Get all active jobs."""
        return [job for job in self.state['job_queue']['jobs'] 
                if job['status'] in ['pending', 'running']]
    
    def add_connection(self, connection_id: str):
        """Add an active connection."""
        self.state['active_connections'].add(connection_id)
    
    def remove_connection(self, connection_id: str):
        """Remove a connection."""
        self.state['active_connections'].discard(connection_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.state['active_connections'])
    
    def get_app_info(self) -> Dict[str, Any]:
        """Get application information."""
        return {
            'project_root': self.project_root,
            'startup_time': self.state['startup_time'],
            'current_api_type': self.state['current_api_type'],
            'active_connections': self.get_connection_count(),
            'total_jobs': len(self.state['job_queue']['jobs']),
            'active_jobs': len(self.get_active_jobs()),
            'components': list(self._components.keys())
        }


