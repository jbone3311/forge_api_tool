"""
RunDiffusion Service for managing RunDiffusion API configuration and connection.
"""
import os
import json
from typing import Dict, Any
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response
from core.api_config import api_config
from core.forge_api import forge_api_client
from core.centralized_logger import logger

class RunDiffusionService:
    """Service for managing RunDiffusion API configuration and connection."""
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rundiffusion_config.json')
        else:
            self.config_path = config_path

    @handle_errors
    def get_config(self) -> Dict[str, Any]:
        """Get the current RunDiffusion configuration."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return create_success_response({'config': config})
        else:
            return create_success_response({'config': None})

    @handle_errors
    def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Save RunDiffusion configuration and switch to RunDiffusion API."""
        required_fields = ['url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return create_error_response(f'Missing required field: {field}')
        url = config['url'].strip()
        if not url.startswith(('http://', 'https://')):
            return create_error_response('URL must start with http:// or https://')
        # Switch to RunDiffusion API
        api_config.switch_to_rundiffusion(config)
        forge_api_client.refresh_configuration()
        logger.log_app_event("switched_to_rundiffusion", {"url": url, "username": config['username']})
        return create_success_response({'message': 'Switched to RunDiffusion API successfully'})

    @handle_errors
    def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test RunDiffusion API connection."""
        required_fields = ['url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return create_error_response(f'Missing required field: {field}')
        import requests
        from requests.auth import HTTPBasicAuth
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
                logger.log_app_event("rundiffusion_connection_successful", {"url": url})
                return create_success_response({'message': 'Connection successful'})
            else:
                error_msg = f'HTTP {response.status_code}: {response.text}'
                logger.log_error(f"RunDiffusion connection failed: {error_msg}")
                return create_error_response(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = 'Connection refused - server may not be running'
            logger.log_error(f"RunDiffusion connection error: {error_msg}")
            return create_error_response(error_msg)
        except requests.exceptions.Timeout:
            error_msg = 'Connection timeout'
            logger.log_error(f"RunDiffusion connection timeout: {error_msg}")
            return create_error_response(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f'Request error: {str(e)}'
            logger.log_error(f"RunDiffusion request error: {error_msg}")
            return create_error_response(error_msg)
        except Exception as e:
            logger.log_error(f"Error testing RunDiffusion connection: {e}")
            return create_error_response(str(e))

    @handle_errors
    def disable(self) -> Dict[str, Any]:
        """Disable RunDiffusion and switch back to local API."""
        try:
            api_config.switch_to_local()
            forge_api_client.refresh_configuration()
            logger.log_app_event("switched_to_local_api", {})
            return create_success_response({'message': 'Switched to local API'})
        except Exception as e:
            logger.log_error(f"Error switching to local API: {e}")
            return create_error_response(str(e)) 