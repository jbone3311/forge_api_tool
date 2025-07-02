"""
Status Service for managing system and API status information.
"""

import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from requests.auth import HTTPBasicAuth

from core.exceptions import ForgeAPIError, JobQueueError, FileOperationError
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response


class StatusService:
    """Service for managing system and API status information."""
    
    def __init__(self, forge_api_client, job_queue, output_manager, logger):
        """Initialize the status service.
        
        Args:
            forge_api_client: The Forge API client instance
            job_queue: The job queue instance
            output_manager: The output manager instance
            logger: The logger instance
        """
        self.forge_api_client = forge_api_client
        self.job_queue = job_queue
        self.output_manager = output_manager
        self.logger = logger
        self._api_status_cache = None
        self._api_status_cache_time = 0
        self._cache_duration = 30  # Cache API status for 30 seconds
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status.
        
        Returns:
            Dict containing system status information
        """
        # Get API connection status
        api_status = self.get_api_status()
        
        # Get queue status
        queue_status = self.job_queue.get_queue_stats()
        
        # Get current generation status
        generation_status = self._get_generation_status()
        
        # Get output statistics
        output_stats = self.output_manager.get_output_statistics()
        
        status = {
            'api': api_status,
            'queue': queue_status,
            'generation': generation_status,
            'outputs': output_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return status
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get Forge API connection status.
        
        Returns:
            Dict containing API status information
        """
        # Check if we have a cached result that's still valid
        current_time = time.time()
        if (self._api_status_cache is not None and 
            current_time - self._api_status_cache_time < self._cache_duration):
            return self._api_status_cache
        
        # Test connection to Forge API
        try:
            connected = self.forge_api_client.test_connection()
            
            if connected:
                # Get additional API info
                try:
                    progress = self.forge_api_client.get_progress()
                    options = self.forge_api_client.get_options()
                    
                    status = {
                        'connected': True,
                        'server_url': self.forge_api_client.base_url,
                        'progress': progress,
                        'options_count': len(options) if options else 0,
                        'last_check': datetime.now().isoformat()
                    }
                except Exception as e:
                    status = {
                        'connected': True,
                        'server_url': self.forge_api_client.base_url,
                        'error': f'Failed to get API details: {str(e)}',
                        'last_check': datetime.now().isoformat()
                    }
            else:
                status = {
                    'connected': False,
                    'server_url': self.forge_api_client.base_url,
                    'error': 'Cannot connect to Forge API',
                    'last_check': datetime.now().isoformat()
                }
        except Exception as e:
            # If connection test fails, return cached result if available, otherwise return error status
            if self._api_status_cache is not None:
                return self._api_status_cache
            
            status = {
                'connected': False,
                'server_url': self.forge_api_client.base_url,
                'error': f'Connection test failed: {str(e)}',
                'last_check': datetime.now().isoformat()
            }
        
        # Cache the result
        self._api_status_cache = status
        self._api_status_cache_time = current_time
        
        return status
    
    def get_current_api_status(self) -> Dict[str, Any]:
        """Get current API connection status.
        
        Returns:
            Dict containing current API status information
        """
        # Get current API preference
        api_preference_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api_preference.json')
        current_api = 'local'
        
        if os.path.exists(api_preference_file):
            try:
                with open(api_preference_file, 'r') as f:
                    preference = json.load(f)
                    current_api = preference.get('current_api', 'local')
            except Exception as e:
                self.logger.warning(f"Failed to read API preference: {e}")
        
        # Test connection based on current API
        if current_api == 'rundiffusion':
            try:
                # Test RunDiffusion connection
                response = self.forge_api_client.get_progress()
                connected = True
                response_time = response.get('response_time', 0)
            except Exception as e:
                connected = False
                response_time = 0
        else:
            try:
                # Test local Forge connection
                response = self.forge_api_client.get_progress()
                connected = True
                response_time = response.get('response_time', 0)
            except Exception as e:
                connected = False
                response_time = 0
        
        return {
            'current_api': current_api,
            'connected': connected,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_generation_status(self) -> Dict[str, Any]:
        """Get current generation status.
        
        Returns:
            Dict containing generation status information
        """
        try:
            # Get current progress
            progress = self.forge_api_client.get_progress()
            
            # Determine if generation is active
            is_generating = progress.get('state', {}).get('job', '') != ''
            
            status = {
                'is_generating': is_generating,
                'progress': progress,
                'timestamp': datetime.now().isoformat()
            }
            
            return status
        except Exception as e:
            self.logger.log_error(f"Error getting generation status: {e}")
            return {
                'is_generating': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_socketio_status(self) -> Dict[str, Any]:
        """Get status for SocketIO updates.
        
        Returns:
            Dict containing status for SocketIO emission
        """
        try:
            # Get comprehensive status
            api_status = self.get_api_status()
            queue_status = self.job_queue.get_queue_stats()
            generation_status = self._get_generation_status()
            output_stats = self.output_manager.get_output_statistics()
            
            return {
                'api': api_status,
                'queue': queue_status,
                'generation': generation_status,
                'outputs': output_stats,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.log_error(f"Failed to get SocketIO status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_rundiffusion_connection(self, config: Dict[str, str]) -> Dict[str, Any]:
        """Test RunDiffusion API connection.
        
        Args:
            config: RunDiffusion configuration containing url, username, password
            
        Returns:
            Dict containing connection test results
        """
        # Validate required fields
        required_fields = ['url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return create_error_response(f'Missing required field: {field}')
        
        # Test connection using requests
        url = config['url'].rstrip('/')
        test_url = f"{url}/sdapi/v1/progress"
        
        try:
            response = requests.get(
                test_url,
                auth=HTTPBasicAuth(config['username'], config['password']),
                timeout=10,
                verify=True
            )
            
            if response.status_code == 200:
                return create_success_response({
                    'message': 'RunDiffusion connection successful',
                    'response_time': response.elapsed.total_seconds()
                })
            else:
                return create_error_response(f'Connection failed with status {response.status_code}')
                
        except requests.exceptions.ConnectionError:
            return create_error_response('Cannot connect to RunDiffusion server')
        except requests.exceptions.Timeout:
            return create_error_response('Connection timeout')
        except requests.exceptions.RequestException as e:
            return create_error_response(f'Request error: {str(e)}')
        except Exception as e:
            return create_error_response(f'Unexpected error: {str(e)}')
    
    def start_background_processor(self) -> None:
        """Start the background job processor."""
        def processor():
            while True:
                try:
                    # Process jobs in queue
                    self.job_queue.process_next_job()
                    time.sleep(1)  # Check every second
                except Exception as e:
                    self.logger.log_error(f"Background processor error: {e}")
                    time.sleep(5)  # Wait longer on error
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()
        self.logger.log_app_event("background_processor_started") 