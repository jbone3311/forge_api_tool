"""
Custom exception classes for the Forge API Tool.

This module provides specific exception classes to replace generic exception handling
and improve error reporting and debugging throughout the application.
"""

from typing import Optional, Dict, Any


class ForgeAPIError(Exception):
    """Base exception for all Forge API Tool errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConnectionError(ForgeAPIError):
    """Raised when API connection fails."""
    
    def __init__(self, message: str, url: Optional[str] = None, timeout: Optional[float] = None):
        details = {}
        if url:
            details['url'] = url
        if timeout:
            details['timeout'] = timeout
        super().__init__(f"Connection failed: {message}", details)


class ConfigurationError(ForgeAPIError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_name: Optional[str] = None, field: Optional[str] = None):
        details = {}
        if config_name:
            details['config_name'] = config_name
        if field:
            details['field'] = field
        super().__init__(f"Configuration error: {message}", details)


class JobQueueError(ForgeAPIError):
    """Raised when job queue operations fail."""
    
    def __init__(self, message: str, job_id: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if job_id:
            details['job_id'] = job_id
        if operation:
            details['operation'] = operation
        super().__init__(f"Job queue error: {message}", details)


class WildcardError(ForgeAPIError):
    """Raised when wildcard operations fail."""
    
    def __init__(self, message: str, wildcard_name: Optional[str] = None, file_path: Optional[str] = None):
        details = {}
        if wildcard_name:
            details['wildcard_name'] = wildcard_name
        if file_path:
            details['file_path'] = file_path
        super().__init__(f"Wildcard error: {message}", details)


class APIError(ForgeAPIError):
    """Raised when Forge API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None):
        details = {}
        if status_code:
            details['status_code'] = status_code
        if endpoint:
            details['endpoint'] = endpoint
        super().__init__(f"API error: {message}", details)


class ValidationError(ForgeAPIError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        super().__init__(f"Validation error: {message}", details)


class FileOperationError(ForgeAPIError):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        super().__init__(f"File operation error: {message}", details)


class GenerationError(ForgeAPIError):
    """Raised when image generation fails."""
    
    def __init__(self, message: str, config_name: Optional[str] = None, prompt: Optional[str] = None):
        details = {}
        if config_name:
            details['config_name'] = config_name
        if prompt:
            details['prompt'] = prompt[:100] + "..." if len(prompt) > 100 else prompt
        super().__init__(f"Generation error: {message}", details)


class LoggingError(ForgeAPIError):
    """Raised when logging operations fail."""
    
    def __init__(self, message: str, log_type: Optional[str] = None, log_file: Optional[str] = None):
        details = {}
        if log_type:
            details['log_type'] = log_type
        if log_file:
            details['log_file'] = log_file
        super().__init__(f"Logging error: {message}", details) 