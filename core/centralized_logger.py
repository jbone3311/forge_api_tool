#!/usr/bin/env python3
"""
Centralized Logging System for Forge API Tool

This module consolidates all logging functionality into a single, comprehensive system
that handles application logs, output logs, and performance metrics in one place.
"""

import logging
import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class CentralizedLogger:
    """
    Centralized logging system that handles all logging needs for the Forge API Tool.
    
    Features:
    - Single log directory with organized subdirectories
    - Structured logging with context
    - Performance tracking
    - Output-specific logging
    - Log rotation and cleanup
    - Session management
    """
    
    def __init__(self, base_log_dir: str = "logs", log_level: str = "INFO"):
        self.base_log_dir = Path(base_log_dir)
        self.log_level = getattr(logging, log_level.upper())
        
        # Create main log directory
        self.base_log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        self.app_log_dir = self.base_log_dir / "application"
        self.output_log_dir = self.base_log_dir / "outputs"
        self.performance_log_dir = self.base_log_dir / "performance"
        self.error_log_dir = self.base_log_dir / "errors"
        self.session_log_dir = self.base_log_dir / "sessions"
        
        for directory in [self.app_log_dir, self.output_log_dir, self.performance_log_dir, 
                         self.error_log_dir, self.session_log_dir]:
            directory.mkdir(exist_ok=True)
        
        # Initialize session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now()
        self.session_log_file = self.session_log_dir / f"session_{self.session_id}.log"
        
        # Set up loggers
        self._setup_loggers()
        
        # Track session statistics
        self.session_stats = {
            'total_events': 0,
            'successful_events': 0,
            'warning_events': 0,
            'error_events': 0,
            'performance_events': 0,
            'output_events': 0
        }
    
    def _setup_loggers(self):
        """Set up different loggers for different purposes."""
        # Main application logger
        self.app_logger = self._create_logger(
            'forge_api_tool',
            self.app_log_dir / 'app.log',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Job processing logger
        self.job_logger = self._create_logger(
            'job_processor',
            self.app_log_dir / 'jobs.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # API communication logger
        self.api_logger = self._create_logger(
            'forge_api',
            self.app_log_dir / 'api.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            'errors',
            self.error_log_dir / 'errors.log',
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Performance logger
        self.perf_logger = self._create_logger(
            'performance',
            self.performance_log_dir / 'performance.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Output logger
        self.output_logger = self._create_logger(
            'outputs',
            self.output_log_dir / 'outputs.log',
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Session logger
        self.session_logger = self._create_logger(
            'session',
            self.session_log_file,
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
        
        # Console handler (only for main app logger)
        if name == 'forge_api_tool':
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            formatter = logging.Formatter(format_string)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Formatter
        formatter = logging.Formatter(format_string)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        
        return logger
    
    def _update_session_stats(self, level: str, category: str = 'app'):
        """Update session statistics."""
        self.session_stats['total_events'] += 1
        
        if level == 'ERROR':
            self.session_stats['error_events'] += 1
        elif level == 'WARNING':
            self.session_stats['warning_events'] += 1
        else:
            self.session_stats['successful_events'] += 1
        
        if category == 'performance':
            self.session_stats['performance_events'] += 1
        elif category == 'output':
            self.session_stats['output_events'] += 1
    
    # Application Logging Methods
    def log_app_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log application events."""
        message = f"APP_EVENT: {event}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        self.app_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_job_start(self, job_id: str, config_name: str, batch_size: int, num_batches: int):
        """Log job start."""
        message = f"JOB_START: {job_id} - Config: {config_name}, Batch: {batch_size}x{num_batches}"
        self.job_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_job_progress(self, job_id: str, current_batch: int, current_image: int, total_images: int):
        """Log job progress."""
        progress = (current_image / total_images) * 100 if total_images > 0 else 0
        message = f"JOB_PROGRESS: {job_id} - Batch {current_batch}, Image {current_image}/{total_images} ({progress:.1f}%)"
        self.job_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_job_complete(self, job_id: str, success: bool, error: Optional[str] = None):
        """Log job completion."""
        if success:
            message = f"JOB_COMPLETE: {job_id} - Success"
            self.job_logger.info(message)
            self.session_logger.info(message)
            self._update_session_stats('INFO')
        else:
            message = f"JOB_FAILED: {job_id} - Error: {error}"
            self.job_logger.error(message)
            self.session_logger.error(message)
            self._update_session_stats('ERROR')
    
    # API Logging Methods
    def log_api_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Log API requests."""
        message = f"API_REQUEST: {method} {endpoint} - Status: {status_code}, Time: {response_time:.3f}s"
        self.api_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_api_error(self, endpoint: str, method: str, error: str, response_time: float):
        """Log API errors."""
        message = f"API_ERROR: {method} {endpoint} - Error: {error}, Time: {response_time:.3f}s"
        self.api_logger.error(message)
        self.session_logger.error(message)
        self._update_session_stats('ERROR')
    
    # Error Logging Methods
    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Log errors."""
        message = f"ERROR: {error}"
        if context:
            message += f" - Context: {json.dumps(context, default=str)}"
        self.error_logger.error(message)
        self.session_logger.error(message)
        self._update_session_stats('ERROR')
    
    def error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Alias for log_error for compatibility."""
        self.log_error(error, context)
    
    # General Logging Methods
    def info(self, message: str):
        """Log info message."""
        self.app_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def warning(self, message: str):
        """Log warning message."""
        self.app_logger.warning(message)
        self.session_logger.warning(message)
        self._update_session_stats('WARNING')
    
    def debug(self, message: str):
        """Log debug message."""
        self.app_logger.debug(message)
        self.session_logger.debug(message)
        self._update_session_stats('DEBUG')
    
    # Performance Logging Methods
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        message = f"PERF: {operation} - Duration: {duration:.3f}s"
        if details:
            message += f" - Details: {json.dumps(details, default=str)}"
        self.perf_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO', 'performance')
    
    # Output Logging Methods
    def log_output_created(self, config_name: str, output_path: str, prompt: str, seed: int):
        """Log when an output is created."""
        message = f"OUTPUT_CREATED: {config_name} - {output_path} - Seed: {seed}"
        self.output_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO', 'output')
    
    def log_output_error(self, config_name: str, error: str, prompt: str = None):
        """Log output creation errors."""
        message = f"OUTPUT_ERROR: {config_name} - {error}"
        if prompt:
            message += f" - Prompt: {prompt[:100]}..."
        self.output_logger.error(message)
        self.session_logger.error(message)
        self._update_session_stats('ERROR', 'output')
    
    def log_output_export(self, config_name: str, export_path: str, file_count: int):
        """Log output export operations."""
        message = f"OUTPUT_EXPORT: {config_name} - {export_path} - {file_count} files"
        self.output_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO', 'output')
    
    # Specialized Logging Methods
    def log_wildcard_usage(self, wildcard_name: str, item: str, usage_count: int):
        """Log wildcard usage."""
        message = f"WILDCARD_USAGE: {wildcard_name} - Item: {item}, Count: {usage_count}"
        self.app_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_config_operation(self, operation: str, config_name: str, success: bool, details: Optional[Dict[str, Any]] = None):
        """Log configuration operations."""
        status = "SUCCESS" if success else "FAILED"
        message = f"CONFIG_{operation.upper()}: {config_name} - {status}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        
        if success:
            self.app_logger.info(message)
            self.session_logger.info(message)
            self._update_session_stats('INFO')
        else:
            self.app_logger.error(message)
            self.session_logger.error(message)
            self._update_session_stats('ERROR')
    
    def log_queue_operation(self, operation: str, job_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log queue operations."""
        message = f"QUEUE_{operation.upper()}"
        if job_id:
            message += f": {job_id}"
        if details:
            message += f" - {json.dumps(details, default=str)}"
        self.app_logger.info(message)
        self.session_logger.info(message)
        self._update_session_stats('INFO')
    
    def log_image_generation(self, config_name: str, prompt: str, seed: int, success: bool, output_path: Optional[str] = None):
        """Log image generation."""
        status = "SUCCESS" if success else "FAILED"
        message = f"IMAGE_GENERATION: {config_name} - {status} - Seed: {seed}"
        if output_path:
            message += f" - Output: {output_path}"
        
        if success:
            self.app_logger.info(message)
            self.session_logger.info(message)
            self._update_session_stats('INFO')
        else:
            self.app_logger.error(message)
            self.session_logger.error(message)
            self._update_session_stats('ERROR')
    
    # Session Management Methods
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the current session."""
        try:
            # Parse log files to get statistics
            log_stats = self._parse_log_files()
            
            return {
                'session_id': self.session_id,
                'session_start': self.session_start_time.isoformat(),
                'total_events': self.session_stats['total_events'],
                'successful_events': self.session_stats['successful_events'],
                'warning_events': self.session_stats['warning_events'],
                'error_events': self.session_stats['error_events'],
                'performance_events': self.session_stats['performance_events'],
                'output_events': self.session_stats['output_events'],
                'recent_events': log_stats.get('recent_events', []),
                'log_directories': {
                    'application': str(self.app_log_dir),
                    'outputs': str(self.output_log_dir),
                    'performance': str(self.performance_log_dir),
                    'errors': str(self.error_log_dir),
                    'sessions': str(self.session_log_dir)
                }
            }
        except Exception as e:
            # Fallback to basic summary if parsing fails
            return {
                'session_id': self.session_id,
                'session_start': self.session_start_time.isoformat(),
                'total_events': self.session_stats['total_events'],
                'successful_events': self.session_stats['successful_events'],
                'warning_events': self.session_stats['warning_events'],
                'error_events': self.session_stats['error_events'],
                'performance_events': self.session_stats['performance_events'],
                'output_events': self.session_stats['output_events'],
                'recent_events': [],
                'error': f'Failed to parse logs: {str(e)}'
            }
    
    def _parse_log_files(self) -> Dict[str, Any]:
        """Parse log files to extract statistics."""
        all_events = []
        
        # Parse all log files in all subdirectories
        for log_dir in [self.app_log_dir, self.output_log_dir, self.performance_log_dir, 
                       self.error_log_dir, self.session_log_dir]:
            for log_file in log_dir.glob('*.log'):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            event = self._parse_log_line(line, log_file.name)
                            if event:
                                all_events.append(event)
                except Exception:
                    continue
        
        # Sort events by timestamp and get recent ones
        all_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'recent_events': all_events[:20]  # Last 20 events
        }
    
    def _parse_log_line(self, line: str, log_file: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line to extract event information."""
        try:
            if not line.strip():
                return None
            
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
                elif 'OUTPUT_' in message:
                    event_type = 'OUTPUT'
            
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
            return None
    
    # Cleanup Methods
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files from all directories."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        cleaned_files = []
        
        for log_dir in [self.app_log_dir, self.output_log_dir, self.performance_log_dir, 
                       self.error_log_dir, self.session_log_dir]:
            for log_file in log_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_date:
                    try:
                        log_file.unlink()
                        cleaned_files.append(str(log_file))
                        self.app_logger.info(f"Cleaned up old log file: {log_file}")
                    except Exception as e:
                        self.app_logger.error(f"Failed to clean up log file {log_file}: {e}")
        
        return cleaned_files
    
    def get_log_directory_structure(self) -> Dict[str, Any]:
        """Get information about the log directory structure."""
        structure = {}
        
        for log_dir in [self.app_log_dir, self.output_log_dir, self.performance_log_dir, 
                       self.error_log_dir, self.session_log_dir]:
            dir_name = log_dir.name
            structure[dir_name] = {
                'path': str(log_dir),
                'files': [],
                'total_size': 0
            }
            
            for log_file in log_dir.glob('*.log'):
                try:
                    size = log_file.stat().st_size
                    structure[dir_name]['files'].append({
                        'name': log_file.name,
                        'size': size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                    })
                    structure[dir_name]['total_size'] += size
                except Exception:
                    continue
        
        return structure


# Global centralized logger instance
centralized_logger = CentralizedLogger() 