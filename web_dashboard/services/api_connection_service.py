"""
API Connection Service for managing connections to the Forge API.
"""

from typing import Dict, Any, Optional
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response
from core.forge_api import forge_api_client
from core.centralized_logger import logger
from core.exceptions import ConnectionError, APIError


class APIConnectionService:
    """Service for managing API connections and status."""
    
    def __init__(self, api_client=None):
        """Initialize the API connection service.
        
        Args:
            api_client: The API client instance (defaults to global forge_api_client)
        """
        self.api_client = api_client or forge_api_client
        self._connection_status = {
            'connected': False,
            'server_url': None,
            'last_connection_attempt': None,
            'connection_error': None
        }
    
    @handle_errors
    def connect_to_api(self) -> Dict[str, Any]:
        """Connect to the Forge API.
        
        Returns:
            Dict containing connection result or error response
        """
        try:
            # Test connection
            connected = self.api_client.test_connection()
            
            if connected:
                # Update connection status
                self._connection_status.update({
                    'connected': True,
                    'server_url': self.api_client.base_url,
                    'last_connection_attempt': 'success',
                    'connection_error': None
                })
                
                logger.log_app_event("api_connected", {
                    "server_url": self.api_client.base_url,
                    "status": "success"
                })
                
                return create_success_response({
                    'message': 'Successfully connected to Forge API',
                    'server_url': self.api_client.base_url,
                    'connected': True
                })
            else:
                # Update connection status with error
                self._connection_status.update({
                    'connected': False,
                    'server_url': self.api_client.base_url,
                    'last_connection_attempt': 'failed',
                    'connection_error': 'Connection test failed'
                })
                
                logger.log_app_event("api_connection_failed", {
                    "server_url": self.api_client.base_url,
                    "status": "failed"
                })
                
                return create_error_response('Failed to connect to Forge API', status_code=400)
                
        except ConnectionError as e:
            # Update connection status with error
            self._connection_status.update({
                'connected': False,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'failed',
                'connection_error': str(e)
            })
            
            logger.log_error(f"API connection error: {e}")
            return create_error_response(f'Connection error: {str(e)}', status_code=400)
        except APIError as e:
            # Update connection status with error
            self._connection_status.update({
                'connected': False,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'failed',
                'connection_error': str(e)
            })
            
            logger.log_error(f"API error during connection: {e}")
            return create_error_response(f'API error: {str(e)}', status_code=400)
        except Exception as e:
            # Update connection status with error
            self._connection_status.update({
                'connected': False,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'failed',
                'connection_error': str(e)
            })
            
            logger.log_error(f"Unexpected API connection error: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    @handle_errors
    def disconnect_from_api(self) -> Dict[str, Any]:
        """Disconnect from the Forge API.
        
        Returns:
            Dict containing disconnection result or error response
        """
        try:
            # Update connection status
            self._connection_status.update({
                'connected': False,
                'last_connection_attempt': 'disconnected',
                'connection_error': None
            })
            
            # Log disconnection
            logger.log_app_event("api_disconnected", {
                "server_url": self.api_client.base_url
            })
            
            return create_success_response({
                'message': 'API disconnected',
                'server_url': self.api_client.base_url,
                'connected': False
            })
            
        except Exception as e:
            logger.log_error(f"API disconnection error: {e}")
            return create_error_response(f'Disconnection error: {str(e)}', status_code=400)
    
    @handle_errors
    def test_connection(self) -> Dict[str, Any]:
        """Test the current API connection.
        
        Returns:
            Dict containing connection test result or error response
        """
        try:
            # Test connection
            connected = self.api_client.test_connection()
            
            # Update connection status
            self._connection_status.update({
                'connected': connected,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'test',
                'connection_error': None if connected else 'Connection test failed'
            })
            
            logger.log_app_event("api_connection_tested", {
                "server_url": self.api_client.base_url,
                "connected": connected
            })
            
            return create_success_response({
                'connected': connected,
                'server_url': self.api_client.base_url,
                'message': 'Connection test completed'
            })
            
        except ConnectionError as e:
            # Update connection status with error
            self._connection_status.update({
                'connected': False,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'test_failed',
                'connection_error': str(e)
            })
            
            logger.log_error(f"API connection test error: {e}")
            return create_error_response(f'Connection test failed: {str(e)}', status_code=400)
        except Exception as e:
            # Update connection status with error
            self._connection_status.update({
                'connected': False,
                'server_url': self.api_client.base_url,
                'last_connection_attempt': 'test_failed',
                'connection_error': str(e)
            })
            
            logger.log_error(f"Unexpected API connection test error: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    @handle_errors
    def get_connection_status(self) -> Dict[str, Any]:
        """Get the current API connection status.
        
        Returns:
            Dict containing connection status information
        """
        try:
            # Get current connection status
            current_status = self._connection_status.copy()
            
            # Add additional status information
            status_info = {
                'connection_status': current_status,
                'api_client_configured': self.api_client is not None,
                'base_url_configured': bool(self.api_client.base_url) if self.api_client else False,
                'timestamp': 'current'
            }
            
            logger.log_app_event("api_status_retrieved", {
                "connected": current_status['connected'],
                "server_url": current_status['server_url']
            })
            
            return create_success_response(status_info)
            
        except Exception as e:
            logger.log_error(f"Error getting API connection status: {e}")
            return create_error_response(f'Failed to get connection status: {str(e)}', status_code=500)
    
    @handle_errors
    def update_api_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update API configuration settings.
        
        Args:
            config: Configuration settings to update
            
        Returns:
            Dict containing update result or error response
        """
        try:
            # Validate required fields
            if 'base_url' not in config:
                return create_error_response('base_url is required', status_code=400)
            
            # Update API client configuration
            if hasattr(self.api_client, 'update_config'):
                self.api_client.update_config(config)
            else:
                # Fallback: update base URL directly
                self.api_client.base_url = config['base_url']
            
            # Reset connection status
            self._connection_status.update({
                'connected': False,
                'server_url': config['base_url'],
                'last_connection_attempt': None,
                'connection_error': None
            })
            
            logger.log_app_event("api_config_updated", {
                "server_url": config['base_url'],
                "config_keys": list(config.keys())
            })
            
            return create_success_response({
                'message': 'API configuration updated successfully',
                'server_url': config['base_url']
            })
            
        except Exception as e:
            logger.log_error(f"Error updating API configuration: {e}")
            return create_error_response(f'Failed to update configuration: {str(e)}', status_code=500)
    
    @handle_errors
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and capabilities.
        
        Returns:
            Dict containing API information or error response
        """
        try:
            # Check if connected
            if not self._connection_status['connected']:
                return create_error_response('Not connected to API', status_code=400)
            
            # Get API information
            api_info = {
                'server_url': self.api_client.base_url,
                'connected': True,
                'capabilities': {}
            }
            
            # Try to get additional API information if available
            if hasattr(self.api_client, 'get_api_info'):
                try:
                    api_info['capabilities'] = self.api_client.get_api_info()
                except Exception as e:
                    logger.log_warning(f"Could not retrieve API capabilities: {e}")
                    api_info['capabilities'] = {'error': 'Could not retrieve capabilities'}
            
            logger.log_app_event("api_info_retrieved", {
                "server_url": self.api_client.base_url,
                "has_capabilities": bool(api_info['capabilities'])
            })
            
            return create_success_response(api_info)
            
        except Exception as e:
            logger.log_error(f"Error getting API information: {e}")
            return create_error_response(f'Failed to get API information: {str(e)}', status_code=500)
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to the API.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connection_status['connected']
    
    @property
    def connection_status(self) -> Dict[str, Any]:
        """Get the current connection status.
        
        Returns:
            Dict containing connection status
        """
        return self._connection_status.copy() 