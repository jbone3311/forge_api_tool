"""
Logging Service - Handles all logging management operations
"""

import os
import sys
import zipfile
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import send_file

# Add the parent directory to the path to import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.exceptions import LoggingError
from utils.response_helpers import create_success_response, create_error_response
from utils.validators import validate_log_cleanup_params


class LoggingService:
    """Service class for managing logging operations."""
    
    def __init__(self, logger_instance):
        """Initialize the logging service.
        
        Args:
            logger_instance: The logger instance
        """
        self.logger = logger_instance
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'logs')
    
    def get_logs_summary(self) -> Dict[str, Any]:
        """Get logging summary.
        
        Returns:
            Dictionary containing recent events
        """
        try:
            summary = self.logger.get_session_summary()
            # For live status, just return recent_events
            return create_success_response({'recent_events': summary.get('recent_events', [])})
        except Exception as e:
            self.logger.log_error(f"Error getting logs summary: {e}")
            return create_error_response(str(e), 400)
    
    def cleanup_logs(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up old log files.
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            Dictionary containing cleanup results
        """
        try:
            # Validate input
            if not validate_log_cleanup_params(days_to_keep):
                return create_error_response('days_to_keep must be a positive integer', 400)
            
            cleaned_files = self.logger.cleanup_old_logs(days_to_keep)
            
            self.logger.log_app_event("logs_cleaned", {
                "days_to_keep": days_to_keep,
                "cleaned_files": cleaned_files
            })
            
            return create_success_response({
                'message': f'Logs older than {days_to_keep} days cleaned up successfully',
                'cleaned_files': cleaned_files
            })
            
        except Exception as e:
            error_msg = f"Error during log cleanup: {str(e)}"
            self.logger.log_error(error_msg, e)
            return create_error_response(error_msg, 500)
    
    def get_logs_structure(self) -> Dict[str, Any]:
        """Get log directory structure information.
        
        Returns:
            Dictionary containing log directory structure
        """
        try:
            structure = self.logger.get_log_directory_structure()
            return create_success_response(structure)
        except Exception as e:
            self.logger.log_error(f"Error getting logs structure: {e}")
            return create_error_response(str(e), 400)
    
    def get_logs_stats(self) -> Dict[str, Any]:
        """Get log file statistics.
        
        Returns:
            Dictionary containing log statistics
        """
        try:
            stats = {
                'app_logs_size': 0,
                'error_logs_size': 0,
                'perf_logs_size': 0
            }
            
            if os.path.exists(self.logs_dir):
                # Calculate sizes for different log types
                for log_type in ['application', 'errors', 'performance']:
                    log_path = os.path.join(self.logs_dir, log_type)
                    if os.path.exists(log_path):
                        total_size = 0
                        for filename in os.listdir(log_path):
                            file_path = os.path.join(log_path, filename)
                            if os.path.isfile(file_path):
                                total_size += os.path.getsize(file_path)
                        
                        if log_type == 'application':
                            stats['app_logs_size'] = total_size
                        elif log_type == 'errors':
                            stats['error_logs_size'] = total_size
                        elif log_type == 'performance':
                            stats['perf_logs_size'] = total_size
            
            return create_success_response(stats)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get log stats: {e}")
            return create_error_response(str(e), 500)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
            
            stats = {
                'size': 0,
                'items': 0
            }
            
            if os.path.exists(cache_dir):
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        stats['size'] += os.path.getsize(file_path)
                        stats['items'] += 1
            
            return create_success_response(stats)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get cache stats: {e}")
            return create_error_response(str(e), 500)
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear the cache.
        
        Returns:
            Dictionary containing operation result
        """
        try:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
            
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            
            self.logger.log_app_event("cache_cleared", {})
            return create_success_response({'message': 'Cache cleared successfully'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to clear cache: {e}")
            return create_error_response(str(e), 500)
    
    def get_logs_by_type(self, log_type: str) -> str:
        """Get logs by type.
        
        Args:
            log_type: Type of logs to retrieve
            
        Returns:
            Log content as string
        """
        try:
            log_path = os.path.join(self.logs_dir, log_type)
            
            if not os.path.exists(log_path):
                raise LoggingError(f"No {log_type} logs found")
            
            # Get the most recent log file
            log_files = [f for f in os.listdir(log_path) if f.endswith('.log')]
            if not log_files:
                raise LoggingError(f"No {log_type} log files found")
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_path, x)), reverse=True)
            latest_log = os.path.join(log_path, log_files[0])
            
            # Read the log file
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            self.logger.log_error(f"Failed to get {log_type} logs: {e}")
            raise LoggingError(f"Failed to load logs: {str(e)}")
    
    def download_logs(self):
        """Download all logs as a zip file.
        
        Returns:
            Flask response with zip file
        """
        try:
            if not os.path.exists(self.logs_dir):
                raise LoggingError('No logs directory found')
            
            # Create a temporary zip file
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.logs_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, self.logs_dir)
                        zipf.write(file_path, arc_name)
            
            self.logger.log_app_event("logs_downloaded", {})
            return send_file(
                temp_zip.name, 
                as_attachment=True, 
                download_name=f'forge-api-logs-{datetime.now().strftime("%Y%m%d")}.zip'
            )
            
        except Exception as e:
            self.logger.log_error(f"Failed to download logs: {e}")
            raise LoggingError(str(e))
    
    def log_js_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log JavaScript errors.
        
        Args:
            error_data: JavaScript error data
            
        Returns:
            Dictionary containing operation result
        """
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '../logs')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, 'js_errors.log')
            
            with open(log_path, 'a') as f:
                f.write(f"JS ERROR: {error_data}\n")
            
            return create_success_response({'message': 'JavaScript error logged'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to log JavaScript error: {e}")
            return create_error_response(str(e), 500) 