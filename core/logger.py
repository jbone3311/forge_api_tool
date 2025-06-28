import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ForgeAPILogger:
    """Comprehensive logging system for Forge API Tool."""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up different loggers
        self._setup_loggers()
        
        # Initialize session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now()
        self.session_log = self.log_dir / f"session_{self.session_id}.log"
        
    def _setup_loggers(self):
        """Set up different loggers for different purposes."""
        # Main application logger
        self.app_logger = self._create_logger(
            'forge_api_tool',
            self.log_dir / 'app.log',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Job processing logger
        self.job_logger = self._create_logger(
            'job_processor',
            self.log_dir / 'jobs.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # API communication logger
        self.api_logger = self._create_logger(
            'forge_api',
            self.log_dir / 'api.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            'errors',
            self.log_dir / 'errors.log',
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Performance logger
        self.perf_logger = self._create_logger(
            'performance',
            self.log_dir / 'performance.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _create_logger(self, name: str, log_file: Path, format_string: str) -> logging.Logger:
        """Create a logger with file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Formatter
        formatter = logging.Formatter(format_string)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_app_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log application events."""
        message = f"APP_EVENT: {event}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        self.app_logger.info(message)
    
    def log_job_start(self, job_id: str, config_name: str, batch_size: int, num_batches: int):
        """Log job start."""
        self.job_logger.info(f"JOB_START: {job_id} - Config: {config_name}, Batch: {batch_size}x{num_batches}")
    
    def log_job_progress(self, job_id: str, current_batch: int, current_image: int, total_images: int):
        """Log job progress."""
        progress = (current_image / total_images) * 100 if total_images > 0 else 0
        self.job_logger.info(f"JOB_PROGRESS: {job_id} - Batch {current_batch}, Image {current_image}/{total_images} ({progress:.1f}%)")
    
    def log_job_complete(self, job_id: str, success: bool, error: Optional[str] = None):
        """Log job completion."""
        if success:
            self.job_logger.info(f"JOB_COMPLETE: {job_id} - Success")
        else:
            self.job_logger.error(f"JOB_FAILED: {job_id} - Error: {error}")
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Log API requests."""
        self.api_logger.info(f"API_REQUEST: {method} {endpoint} - Status: {status_code}, Time: {response_time:.3f}s")
    
    def log_api_error(self, endpoint: str, method: str, error: str, response_time: float):
        """Log API errors."""
        self.api_logger.error(f"API_ERROR: {method} {endpoint} - Error: {error}, Time: {response_time:.3f}s")
    
    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Log errors."""
        message = f"ERROR: {error}"
        if context:
            message += f" - Context: {json.dumps(context, default=str)}"
        self.error_logger.error(message)
    
    def error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Alias for log_error for compatibility."""
        self.log_error(error, context)
    
    def info(self, message: str):
        """Log info message."""
        self.app_logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.app_logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.app_logger.debug(message)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        message = f"PERF: {operation} - Duration: {duration:.3f}s"
        if details:
            message += f" - Details: {json.dumps(details, default=str)}"
        self.perf_logger.info(message)
    
    def log_wildcard_usage(self, wildcard_name: str, item: str, usage_count: int):
        """Log wildcard usage."""
        self.app_logger.info(f"WILDCARD_USAGE: {wildcard_name} - Item: {item}, Count: {usage_count}")
    
    def log_config_operation(self, operation: str, config_name: str, success: bool, details: Optional[Dict[str, Any]] = None):
        """Log configuration operations."""
        status = "SUCCESS" if success else "FAILED"
        message = f"CONFIG_{operation.upper()}: {config_name} - {status}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        
        if success:
            self.app_logger.info(message)
        else:
            self.app_logger.error(message)
    
    def log_queue_operation(self, operation: str, job_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log queue operations."""
        message = f"QUEUE_{operation.upper()}"
        if job_id:
            message += f": {job_id}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        self.app_logger.info(message)
    
    def log_image_generation(self, config_name: str, prompt: str, seed: int, success: bool, output_path: Optional[str] = None):
        """Log image generation."""
        status = "SUCCESS" if success else "FAILED"
        message = f"IMAGE_GENERATION: {config_name} - {status} - Seed: {seed}"
        if output_path:
            message += f" - Output: {output_path}"
        
        if success:
            self.app_logger.info(message)
        else:
            self.app_logger.error(message)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the current session."""
        try:
            # Parse log files to get statistics
            log_stats = self._parse_log_files()
            
            return {
                'session_id': self.session_id,
                'session_start': self.session_start_time.isoformat() if hasattr(self, 'session_start_time') else datetime.now().isoformat(),
                'total_events': log_stats.get('total_events', 0),
                'successful_events': log_stats.get('successful_events', 0),
                'warning_events': log_stats.get('warning_events', 0),
                'error_events': log_stats.get('error_events', 0),
                'recent_events': log_stats.get('recent_events', []),
                'log_files': {
                    'app': str(self.log_dir / 'app.log'),
                    'jobs': str(self.log_dir / 'jobs.log'),
                    'api': str(self.log_dir / 'api.log'),
                    'errors': str(self.log_dir / 'errors.log'),
                    'performance': str(self.log_dir / 'performance.log')
                }
            }
        except Exception as e:
            # Fallback to basic summary if parsing fails
            return {
                'session_id': self.session_id,
                'session_start': datetime.now().isoformat(),
                'total_events': 0,
                'successful_events': 0,
                'warning_events': 0,
                'error_events': 0,
                'recent_events': [],
                'error': f'Failed to parse logs: {str(e)}'
            }
    
    def _parse_log_files(self) -> Dict[str, Any]:
        """Parse log files to extract statistics."""
        stats = {
            'total_events': 0,
            'successful_events': 0,
            'warning_events': 0,
            'error_events': 0,
            'recent_events': []
        }
        
        # Track recent events across all log files
        all_events = []
        
        # Parse each log file
        for log_file in self.log_dir.glob('*.log'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Parse log line
                        event = self._parse_log_line(line, log_file.name)
                        if event:
                            all_events.append(event)
                            
                            # Count by level
                            stats['total_events'] += 1
                            if event['level'] == 'ERROR':
                                stats['error_events'] += 1
                            elif event['level'] == 'WARNING':
                                stats['warning_events'] += 1
                            else:
                                stats['successful_events'] += 1
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Sort events by timestamp and get recent ones
        all_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        stats['recent_events'] = all_events[:20]  # Last 20 events
        
        return stats
    
    def _parse_log_line(self, line: str, log_file: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line to extract event information."""
        try:
            # Skip empty lines
            if not line.strip():
                return None
            
            # Try to parse timestamp and level
            parts = line.split(' - ', 2)
            if len(parts) < 2:
                return None
            
            timestamp_str = parts[0].strip()
            level_part = parts[1].strip()
            
            # Extract level
            level = 'INFO'
            if 'ERROR' in level_part:
                level = 'ERROR'
            elif 'WARNING' in level_part:
                level = 'WARNING'
            elif 'DEBUG' in level_part:
                level = 'DEBUG'
            
            # Extract event type and message
            event_type = 'LOG'
            message = level_part
            
            if len(parts) > 2:
                message = parts[2].strip()
                
                # Try to extract event type from common patterns
                if 'APP_EVENT:' in message:
                    event_type = 'APP_EVENT'
                elif 'JOB_' in message:
                    event_type = 'JOB'
                elif 'API_' in message:
                    event_type = 'API'
                elif 'PERF:' in message:
                    event_type = 'PERFORMANCE'
                elif 'CONFIG_' in message:
                    event_type = 'CONFIG'
                elif 'QUEUE_' in message:
                    event_type = 'QUEUE'
                elif 'IMAGE_GENERATION:' in message:
                    event_type = 'IMAGE_GENERATION'
            
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
            except:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp.isoformat(),
                'level': level,
                'event_type': event_type,
                'message': message[:100] + '...' if len(message) > 100 else message,
                'log_file': log_file
            }
            
        except Exception:
            # Return None if parsing fails
            return None
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob('*.log'):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    self.app_logger.info(f"Cleaned up old log file: {log_file}")
                except Exception as e:
                    self.app_logger.error(f"Failed to clean up log file {log_file}: {e}")


# Global logger instance
logger = ForgeAPILogger() 