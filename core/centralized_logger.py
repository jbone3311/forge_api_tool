#!/usr/bin/env python3
"""
Centralized Logging System for Forge API Tool

This module consolidates all logging functionality into a single, comprehensive system
that handles application logs, output logs, and performance metrics in one place.
"""

import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback


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
    
    def __init__(self, log_dir: str = "outputs/logs"):
        """Initialize the centralized logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.error_dir = self.log_dir / "errors"
        self.performance_dir = self.log_dir / "performance"
        self.application_dir = self.log_dir / "application"
        self.sessions_dir = self.log_dir / "sessions"
        
        for directory in [self.error_dir, self.performance_dir, self.application_dir, self.sessions_dir]:
            directory.mkdir(exist_ok=True)
        
        # Configure main logger
        self.logger = logging.getLogger('forge_api_tool')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handlers
        self._setup_file_handlers()
        
        # Console handler
        self._setup_console_handler()
        
        # Log initialization
        self.log_app_event("centralized_logger_initialized", {
            "log_dir": str(self.log_dir),
            "subdirectories": {
                "errors": str(self.error_dir),
                "performance": str(self.performance_dir),
                "application": str(self.application_dir),
                "sessions": str(self.sessions_dir)
            }
        })
    
    def _setup_file_handlers(self):
        """Setup file handlers for different log types."""
        # Main application log
        app_handler = logging.FileHandler(self.log_dir / "app.log", encoding='utf-8')
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(self.formatter)
        self.logger.addHandler(app_handler)
        
        # Error log
        error_handler = logging.FileHandler(self.error_dir / "errors.log", encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_handler)
        
        # API log
        api_handler = logging.FileHandler(self.log_dir / "api.log", encoding='utf-8')
        api_handler.setLevel(logging.INFO)
        api_handler.setFormatter(self.formatter)
        self.logger.addHandler(api_handler)
        
        # Performance log
        perf_handler = logging.FileHandler(self.performance_dir / "performance.log", encoding='utf-8')
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(self.formatter)
        self.logger.addHandler(perf_handler)
        
        # Jobs log
        jobs_handler = logging.FileHandler(self.log_dir / "jobs.log", encoding='utf-8')
        jobs_handler.setLevel(logging.INFO)
        jobs_handler.setFormatter(self.formatter)
        self.logger.addHandler(jobs_handler)
    
    def _setup_console_handler(self):
        """Setup console handler for development."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def log_app_event(self, event_type: str, data: Dict[str, Any] = None):
        """Log application events with structured data."""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Log to application directory
        event_file = self.application_dir / f"{event_type}_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(event_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write event log: {e}")
        
        # Also log to main logger
        self.logger.info(f"APP_EVENT: {event_type} - {json.dumps(data or {}, ensure_ascii=False)}")
    
    def log_error(self, message: str, error: Exception = None, context: Dict[str, Any] = None):
        """Log errors with full context."""
        error_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__ if error else None,
            "error_message": str(error) if error else None,
            "traceback": traceback.format_exc() if error else None,
            "context": context or {}
        }
        
        # Log to error directory
        error_file = self.error_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")
        
        # Also log to main logger
        self.logger.error(f"ERROR: {message} - {str(error) if error else 'No exception'}")
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, response_time: float, data: Dict[str, Any] = None):
        """Log API calls with performance metrics."""
        api_data = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Log to API log
        self.logger.info(f"API_CALL: {method} {endpoint} - {status_code} ({api_data['response_time_ms']}ms)")
        
        # Also save to performance directory
        perf_file = self.performance_dir / f"api_performance_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(perf_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(api_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write performance log: {e}")
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Log API requests (alias for log_api_call for compatibility)."""
        self.log_api_call(endpoint, method, status_code, response_time)
    
    def log_api_error(self, endpoint: str, method: str, error: str, response_time: float):
        """Log API errors."""
        api_error_data = {
            "endpoint": endpoint,
            "method": method,
            "error": error,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log to API log
        self.logger.error(f"API_ERROR: {method} {endpoint} - {error} ({api_error_data['response_time_ms']}ms)")
        
        # Also save to error directory
        error_file = self.error_dir / f"api_errors_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(api_error_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write API error log: {e}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics."""
        perf_data = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Log to performance directory
        perf_file = self.performance_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(perf_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(perf_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write performance log: {e}")
        
        # Also log to main logger
        self.logger.info(f"PERFORMANCE: {operation} - {perf_data['duration_ms']}ms")
    
    def log_job_event(self, job_id: str, event_type: str, data: Dict[str, Any] = None):
        """Log job-related events."""
        job_data = {
            "job_id": job_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Log to jobs log
        self.logger.info(f"JOB_EVENT: {job_id} - {event_type} - {json.dumps(data or {}, ensure_ascii=False)}")
        
        # Also save to sessions directory
        session_file = self.sessions_dir / f"job_{job_id}_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(session_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(job_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write job log: {e}")
    
    def log_output_created(self, config_name: str, filepath: str, prompt: str, seed: int):
        """Log when an output is created."""
        output_data = {
            "config_name": config_name,
            "filepath": filepath,
            "prompt": prompt,
            "seed": seed,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_app_event("output_created", output_data)
    
    def log_session_start(self, session_id: str, config_name: str, settings: Dict[str, Any]):
        """Log when a session starts."""
        session_data = {
            "session_id": session_id,
            "config_name": config_name,
            "settings": settings,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_app_event("session_started", session_data)
    
    def log_session_end(self, session_id: str, results: Dict[str, Any]):
        """Log when a session ends."""
        session_data = {
            "session_id": session_id,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_app_event("session_ended", session_data)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about the logs."""
        stats = {
            "total_log_files": 0,
            "total_size_mb": 0,
            "log_types": {}
        }
        
        try:
            for log_type in ["app", "api", "errors", "performance", "jobs"]:
                log_file = self.log_dir / f"{log_type}.log"
                if log_file.exists():
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    stats["log_types"][log_type] = {
                        "size_mb": round(size_mb, 2),
                        "exists": True
                    }
                    stats["total_size_mb"] += size_mb
                    stats["total_log_files"] += 1
                else:
                    stats["log_types"][log_type] = {
                        "size_mb": 0,
                        "exists": False
                    }
            
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            
        except Exception as e:
            self.logger.error(f"Failed to get log stats: {e}")
        
        return stats
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            deleted_count = 0
            failed_deletions = []
            
            # Clean up .log files
            for log_file in self.log_dir.rglob("*.log"):
                try:
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old log file: {log_file}")
                except (OSError, PermissionError) as e:
                    failed_deletions.append(f"{log_file}: {str(e)}")
                    self.logger.warning(f"Failed to delete log file {log_file}: {e}")
            
            # Clean up .json files
            for json_file in self.log_dir.rglob("*.json"):
                try:
                    if json_file.stat().st_mtime < cutoff_date:
                        json_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old JSON file: {json_file}")
                except (OSError, PermissionError) as e:
                    failed_deletions.append(f"{json_file}: {str(e)}")
                    self.logger.warning(f"Failed to delete JSON file {json_file}: {e}")
            
            # Log the cleanup operation
            cleanup_data = {
                "deleted_count": deleted_count,
                "days_to_keep": days_to_keep,
                "failed_deletions": failed_deletions,
                "total_failures": len(failed_deletions)
            }
            
            self.log_app_event("logs_cleaned", cleanup_data)
            
            # If there were failures, log them as a warning
            if failed_deletions:
                self.logger.warning(f"Log cleanup completed with {len(failed_deletions)} failures: {failed_deletions}")
            
            return deleted_count
            
        except Exception as e:
            error_msg = f"Failed to cleanup old logs: {e}"
            self.log_error(error_msg, e)
            raise Exception(error_msg)
    
    def log_image_generation(self, config_name: str, prompt: str, seed: int, success: bool, output_path: str = None):
        """Log image generation events."""
        generation_data = {
            "config_name": config_name,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "seed": seed,
            "success": success,
            "output_path": output_path,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_app_event("image_generation", generation_data)
    
    def log_output_error(self, config_name: str, error: str, prompt: str = None):
        """Log output creation errors."""
        error_data = {
            "config_name": config_name,
            "error": error,
            "prompt": prompt[:100] + "..." if prompt and len(prompt) > 100 else prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_error(f"Output error for {config_name}: {error}", context=error_data)
    
    def log_output_export(self, config_name: str, export_path: str, file_count: int):
        """Log output export operations."""
        export_data = {
            "config_name": config_name,
            "export_path": export_path,
            "file_count": file_count,
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_app_event("output_export", export_data)
    
    def log_config_operation(self, operation: str, config_name: str, success: bool, details: Dict[str, Any] = None):
        """Log configuration operations."""
        config_data = {
            "operation": operation,
            "config_name": config_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Log to application directory
        config_file = self.application_dir / f"config_operations_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(config_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(config_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write config operation log: {e}")
        
        # Also log to main logger
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"CONFIG_OPERATION: {operation} {config_name} - {status}")
    
    def log_queue_operation(self, operation: str, job_id: Optional[str], details: Dict[str, Any] = None):
        """Log queue operations."""
        queue_data = {
            "operation": operation,
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Log to application directory
        queue_file = self.application_dir / f"queue_operations_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(queue_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(queue_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write queue operation log: {e}")
        
        # Also log to main logger
        self.logger.info(f"QUEUE_OPERATION: {operation} - Job ID: {job_id or 'N/A'}")
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(f"INFO: {message}")
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(f"DEBUG: {message}")
    
    def error(self, message: str, context: Dict[str, Any] = None):
        """Alias for log_error for compatibility."""
        self.log_error(message, context=context)
    
    def get_log_directory_structure(self) -> Dict[str, Any]:
        """Get information about the log directory structure."""
        try:
            structure = {
                "log_dir": str(self.log_dir),
                "subdirectories": {},
                "file_counts": {},
                "total_size_mb": 0
            }
            
            # Check each subdirectory
            for subdir_name, subdir_path in [
                ("errors", self.error_dir),
                ("performance", self.performance_dir),
                ("application", self.application_dir),
                ("sessions", self.sessions_dir)
            ]:
                if subdir_path.exists():
                    file_count = len(list(subdir_path.glob("*")))
                    size_mb = sum(f.stat().st_size for f in subdir_path.rglob("*") if f.is_file()) / (1024 * 1024)
                    
                    structure["subdirectories"][subdir_name] = {
                        "path": str(subdir_path),
                        "exists": True,
                        "file_count": file_count,
                        "size_mb": round(size_mb, 2)
                    }
                    structure["total_size_mb"] += size_mb
                else:
                    structure["subdirectories"][subdir_name] = {
                        "path": str(subdir_path),
                        "exists": False,
                        "file_count": 0,
                        "size_mb": 0
                    }
            
            # Check main log files
            main_log_files = ["app.log", "api.log", "jobs.log"]
            for log_file in main_log_files:
                file_path = self.log_dir / log_file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    structure["file_counts"][log_file] = {
                        "exists": True,
                        "size_mb": round(size_mb, 2)
                    }
                    structure["total_size_mb"] += size_mb
                else:
                    structure["file_counts"][log_file] = {
                        "exists": False,
                        "size_mb": 0
                    }
            
            structure["total_size_mb"] = round(structure["total_size_mb"], 2)
            return structure
            
        except Exception as e:
            self.log_error(f"Failed to get log directory structure: {e}", e)
            return {
                "error": str(e),
                "log_dir": str(self.log_dir)
            }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of recent session events."""
        try:
            recent_events = []
            
            # Get recent events from application directory
            for event_file in self.application_dir.glob("*.json"):
                try:
                    with open(event_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                event_data = json.loads(line.strip())
                                recent_events.append(event_data)
                except Exception as e:
                    self.logger.warning(f"Failed to read event file {event_file}: {e}")
            
            # Sort by timestamp and get the most recent 50
            recent_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            recent_events = recent_events[:50]
            
            return {
                "recent_events": recent_events,
                "total_events": len(recent_events)
            }
            
        except Exception as e:
            self.log_error(f"Failed to get session summary: {e}", e)
            return {"recent_events": [], "total_events": 0}


# Global logger instance
logger = CentralizedLogger() 