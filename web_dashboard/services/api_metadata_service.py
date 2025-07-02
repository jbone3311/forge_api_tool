"""
API Metadata Service for managing API metadata like models, samplers, and options.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response
from core.forge_api import forge_api_client
from core.centralized_logger import logger
from core.exceptions import APIError, ConnectionError


class APIMetadataService:
    """Service for managing API metadata and caching."""
    
    def __init__(self, api_client=None):
        """Initialize the API metadata service.
        
        Args:
            api_client: The API client instance (defaults to global forge_api_client)
        """
        self.api_client = api_client or forge_api_client
        self._metadata_cache = {
            'models': {
                'data': None,
                'last_updated': None,
                'cache_duration': timedelta(minutes=30)  # 30 minutes cache
            },
            'samplers': {
                'data': None,
                'last_updated': None,
                'cache_duration': timedelta(hours=1)  # 1 hour cache
            },
            'options': {
                'data': None,
                'last_updated': None,
                'cache_duration': timedelta(hours=1)  # 1 hour cache
            }
        }
    
    @handle_errors
    def get_models(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get available models from the API.
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            Dict containing models data or error response
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid('models'):
                logger.log_app_event("models_retrieved_from_cache", {
                    "cache_age_minutes": self._get_cache_age_minutes('models')
                })
                return create_success_response({
                    'models': self._metadata_cache['models']['data'],
                    'cached': True,
                    'last_updated': self._metadata_cache['models']['last_updated'].isoformat()
                })
            
            # Fetch fresh data from API
            models = self.api_client.get_models()
            
            # Update cache
            self._update_cache('models', models)
            
            logger.log_app_event("models_retrieved", {
                "count": len(models) if models else 0,
                "cached": False
            })
            
            return create_success_response({
                'models': models,
                'cached': False,
                'last_updated': datetime.now().isoformat()
            })
            
        except ConnectionError as e:
            logger.log_error(f"Connection error getting models: {e}")
            return create_error_response(f'Connection error: {str(e)}', status_code=400)
        except APIError as e:
            logger.log_error(f"API error getting models: {e}")
            return create_error_response(f'API error: {str(e)}', status_code=400)
        except Exception as e:
            logger.log_error(f"Unexpected error getting models: {e}")
            return create_error_response(f'Failed to get models: {str(e)}', status_code=500)
    
    @handle_errors
    def get_samplers(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get available samplers from the API.
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            Dict containing samplers data or error response
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid('samplers'):
                logger.log_app_event("samplers_retrieved_from_cache", {
                    "cache_age_minutes": self._get_cache_age_minutes('samplers')
                })
                return create_success_response({
                    'samplers': self._metadata_cache['samplers']['data'],
                    'cached': True,
                    'last_updated': self._metadata_cache['samplers']['last_updated'].isoformat()
                })
            
            # Fetch fresh data from API
            samplers = self.api_client.get_samplers()
            
            # Update cache
            self._update_cache('samplers', samplers)
            
            logger.log_app_event("samplers_retrieved", {
                "count": len(samplers) if samplers else 0,
                "cached": False
            })
            
            return create_success_response({
                'samplers': samplers,
                'cached': False,
                'last_updated': datetime.now().isoformat()
            })
            
        except ConnectionError as e:
            logger.log_error(f"Connection error getting samplers: {e}")
            return create_error_response(f'Connection error: {str(e)}', status_code=400)
        except APIError as e:
            logger.log_error(f"API error getting samplers: {e}")
            return create_error_response(f'API error: {str(e)}', status_code=400)
        except Exception as e:
            logger.log_error(f"Unexpected error getting samplers: {e}")
            return create_error_response(f'Failed to get samplers: {str(e)}', status_code=500)
    
    @handle_errors
    def get_options(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get available options from the API.
        
        Args:
            force_refresh: Force refresh of cached data
            
        Returns:
            Dict containing options data or error response
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid('options'):
                logger.log_app_event("options_retrieved_from_cache", {
                    "cache_age_minutes": self._get_cache_age_minutes('options')
                })
                return create_success_response({
                    'options': self._metadata_cache['options']['data'],
                    'cached': True,
                    'last_updated': self._metadata_cache['options']['last_updated'].isoformat()
                })
            
            # Fetch fresh data from API
            options = self.api_client.get_options()
            
            # Update cache
            self._update_cache('options', options)
            
            logger.log_app_event("options_retrieved", {
                "count": len(options) if options else 0,
                "cached": False
            })
            
            return create_success_response({
                'options': options,
                'cached': False,
                'last_updated': datetime.now().isoformat()
            })
            
        except ConnectionError as e:
            logger.log_error(f"Connection error getting options: {e}")
            return create_error_response(f'Connection error: {str(e)}', status_code=400)
        except APIError as e:
            logger.log_error(f"API error getting options: {e}")
            return create_error_response(f'API error: {str(e)}', status_code=400)
        except Exception as e:
            logger.log_error(f"Unexpected error getting options: {e}")
            return create_error_response(f'Failed to get options: {str(e)}', status_code=500)
    
    @handle_errors
    def refresh_all_metadata(self) -> Dict[str, Any]:
        """Refresh all metadata from the API.
        
        Returns:
            Dict containing refresh result or error response
        """
        try:
            refresh_results = {}
            
            # Refresh models
            models_result = self.get_models(force_refresh=True)
            if models_result.get('success'):
                refresh_results['models'] = {
                    'success': True,
                    'count': len(models_result.get('data', {}).get('models', []))
                }
            else:
                refresh_results['models'] = {
                    'success': False,
                    'error': models_result.get('error', 'Unknown error')
                }
            
            # Refresh samplers
            samplers_result = self.get_samplers(force_refresh=True)
            if samplers_result.get('success'):
                refresh_results['samplers'] = {
                    'success': True,
                    'count': len(samplers_result.get('data', {}).get('samplers', []))
                }
            else:
                refresh_results['samplers'] = {
                    'success': False,
                    'error': samplers_result.get('error', 'Unknown error')
                }
            
            # Refresh options
            options_result = self.get_options(force_refresh=True)
            if options_result.get('success'):
                refresh_results['options'] = {
                    'success': True,
                    'count': len(options_result.get('data', {}).get('options', []))
                }
            else:
                refresh_results['options'] = {
                    'success': False,
                    'error': options_result.get('error', 'Unknown error')
                }
            
            # Check overall success
            all_successful = all(result.get('success', False) for result in refresh_results.values())
            
            logger.log_app_event("metadata_refreshed", {
                "all_successful": all_successful,
                "models_success": refresh_results['models']['success'],
                "samplers_success": refresh_results['samplers']['success'],
                "options_success": refresh_results['options']['success']
            })
            
            return create_success_response({
                'message': 'Metadata refresh completed',
                'all_successful': all_successful,
                'results': refresh_results,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.log_error(f"Error refreshing metadata: {e}")
            return create_error_response(f'Failed to refresh metadata: {str(e)}', status_code=500)
    
    @handle_errors
    def get_metadata_status(self) -> Dict[str, Any]:
        """Get the current status of metadata cache.
        
        Returns:
            Dict containing cache status information
        """
        try:
            status = {}
            
            for metadata_type, cache_info in self._metadata_cache.items():
                status[metadata_type] = {
                    'has_data': cache_info['data'] is not None,
                    'last_updated': cache_info['last_updated'].isoformat() if cache_info['last_updated'] else None,
                    'cache_age_minutes': self._get_cache_age_minutes(metadata_type),
                    'is_valid': self._is_cache_valid(metadata_type),
                    'cache_duration_minutes': int(cache_info['cache_duration'].total_seconds() / 60)
                }
            
            logger.log_app_event("metadata_status_retrieved", {
                "models_valid": status['models']['is_valid'],
                "samplers_valid": status['samplers']['is_valid'],
                "options_valid": status['options']['is_valid']
            })
            
            return create_success_response({
                'cache_status': status,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.log_error(f"Error getting metadata status: {e}")
            return create_error_response(f'Failed to get metadata status: {str(e)}', status_code=500)
    
    @handle_errors
    def clear_cache(self, metadata_type: Optional[str] = None) -> Dict[str, Any]:
        """Clear metadata cache.
        
        Args:
            metadata_type: Specific metadata type to clear (models, samplers, options) or None for all
            
        Returns:
            Dict containing clear result or error response
        """
        try:
            if metadata_type:
                if metadata_type not in self._metadata_cache:
                    return create_error_response(f'Invalid metadata type: {metadata_type}', status_code=400)
                
                # Clear specific cache
                self._metadata_cache[metadata_type]['data'] = None
                self._metadata_cache[metadata_type]['last_updated'] = None
                
                logger.log_app_event("metadata_cache_cleared", {
                    "metadata_type": metadata_type
                })
                
                return create_success_response({
                    'message': f'{metadata_type} cache cleared successfully',
                    'cleared_type': metadata_type
                })
            else:
                # Clear all caches
                for cache_type in self._metadata_cache:
                    self._metadata_cache[cache_type]['data'] = None
                    self._metadata_cache[cache_type]['last_updated'] = None
                
                logger.log_app_event("metadata_cache_cleared", {
                    "metadata_type": "all"
                })
                
                return create_success_response({
                    'message': 'All metadata caches cleared successfully',
                    'cleared_type': 'all'
                })
                
        except Exception as e:
            logger.log_error(f"Error clearing metadata cache: {e}")
            return create_error_response(f'Failed to clear cache: {str(e)}', status_code=500)
    
    def _is_cache_valid(self, metadata_type: str) -> bool:
        """Check if cache is valid for the given metadata type.
        
        Args:
            metadata_type: Type of metadata to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if metadata_type not in self._metadata_cache:
            return False
        
        cache_info = self._metadata_cache[metadata_type]
        
        # Check if we have data and it's not expired
        if cache_info['data'] is None or cache_info['last_updated'] is None:
            return False
        
        # Check if cache has expired
        age = datetime.now() - cache_info['last_updated']
        return age < cache_info['cache_duration']
    
    def _get_cache_age_minutes(self, metadata_type: str) -> Optional[int]:
        """Get the age of cache in minutes for the given metadata type.
        
        Args:
            metadata_type: Type of metadata to check
            
        Returns:
            Age in minutes or None if no cache
        """
        if metadata_type not in self._metadata_cache:
            return None
        
        cache_info = self._metadata_cache[metadata_type]
        
        if cache_info['last_updated'] is None:
            return None
        
        age = datetime.now() - cache_info['last_updated']
        return int(age.total_seconds() / 60)
    
    def _update_cache(self, metadata_type: str, data: Any) -> None:
        """Update cache for the given metadata type.
        
        Args:
            metadata_type: Type of metadata to update
            data: Data to cache
        """
        if metadata_type in self._metadata_cache:
            self._metadata_cache[metadata_type]['data'] = data
            self._metadata_cache[metadata_type]['last_updated'] = datetime.now() 