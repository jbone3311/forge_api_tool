"""
Validation utilities for the Flask web dashboard.

This module provides validation functions for various input parameters
used throughout the application.
"""

import re
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.exceptions import ValidationError


def validate_config_name(config_name: str) -> None:
    """
    Validate configuration name.
    
    Args:
        config_name: Configuration name to validate
        
    Raises:
        ValidationError: If config name is invalid
    """
    if not config_name:
        raise ValidationError("Configuration name is required")
    
    if not isinstance(config_name, str):
        raise ValidationError("Configuration name must be a string")
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', config_name):
        raise ValidationError("Configuration name can only contain letters, numbers, hyphens, and underscores")
    
    # Check length
    if len(config_name) < 1 or len(config_name) > 100:
        raise ValidationError("Configuration name must be between 1 and 100 characters")


def validate_date_format(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        raise ValidationError("Date cannot be empty")
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValidationError("Date must be in YYYY-MM-DD format")
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Invalid date")
    
    return True


def validate_batch_parameters(batch_size: int, num_batches: int) -> None:
    """
    Validate batch generation parameters.
    
    Args:
        batch_size: Number of images per batch
        num_batches: Number of batches
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not isinstance(batch_size, int) or batch_size < 1:
        raise ValidationError("Batch size must be a positive integer")
    
    if not isinstance(num_batches, int) or num_batches < 1:
        raise ValidationError("Number of batches must be a positive integer")
    
    # Check reasonable limits
    if batch_size > 100:
        raise ValidationError("Batch size cannot exceed 100")
    
    if num_batches > 100:
        raise ValidationError("Number of batches cannot exceed 100")
    
    total_images = batch_size * num_batches
    if total_images > 1000:
        raise ValidationError("Total number of images cannot exceed 1,000")


def validate_generation_settings(settings: Dict[str, Any]) -> bool:
    """
    Validate image generation settings.
    
    Args:
        settings: Generation settings dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If settings are invalid
    """
    # Validate steps
    steps = settings.get('steps', 20)
    if not isinstance(steps, int) or steps < 1 or steps > 200:
        raise ValidationError("Steps must be an integer between 1 and 200")
    
    # Validate dimensions
    width = settings.get('width', 512)
    height = settings.get('height', 512)
    
    if not isinstance(width, int) or width < 64 or width > 2048:
        raise ValidationError("Width must be an integer between 64 and 2048")
    
    if not isinstance(height, int) or height < 64 or height > 2048:
        raise ValidationError("Height must be an integer between 64 and 2048")
    
    # Validate CFG scale
    cfg_scale = settings.get('cfg_scale', 7.0)
    if not isinstance(cfg_scale, (int, float)) or cfg_scale < 1.0 or cfg_scale > 30.0:
        raise ValidationError("CFG scale must be between 1.0 and 30.0")
    
    return True


def validate_prompt(prompt: str) -> None:
    """
    Validate prompt string.
    
    Args:
        prompt: Prompt string to validate
        
    Raises:
        ValidationError: If prompt is invalid
    """
    if not isinstance(prompt, str):
        raise ValidationError("Prompt must be a string")
    
    # Check length
    if len(prompt) > 10000:
        raise ValidationError("Prompt must be less than 10,000 characters")
    
    # Check for potentially dangerous content (basic check)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload=',
        r'onerror='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            raise ValidationError(f"Prompt contains potentially dangerous content: {pattern}")


def validate_file_path(file_path: str, must_exist: bool = False) -> bool:
    """
    Validate file path.
    
    Args:
        file_path: File path to validate
        must_exist: Whether the file must exist
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    # Check for path traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        raise ValidationError("Invalid file path")
    
    if must_exist and not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    return True


def validate_api_config(config: Dict[str, Any]) -> bool:
    """
    Validate API configuration.
    
    Args:
        config: API configuration dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If configuration is invalid
    """
    required_fields = ['url']
    for field in required_fields:
        if field not in config:
            raise ValidationError(f"Missing required field: {field}")
    
    url = config['url']
    if not url:
        raise ValidationError("URL cannot be empty")
    
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://")
    
    return True


def validate_rundiffusion_config(config: Dict[str, Any]) -> bool:
    """
    Validate RunDiffusion configuration.
    
    Args:
        config: RunDiffusion configuration dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If configuration is invalid
    """
    required_fields = ['url', 'username', 'password']
    for field in required_fields:
        if field not in config:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate URL
    url = config['url'].strip()
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://")
    
    # Validate credentials
    if not config['username']:
        raise ValidationError("Username cannot be empty")
    
    if not config['password']:
        raise ValidationError("Password cannot be empty")
    
    return True


def validate_log_cleanup_params(days_to_keep: int) -> bool:
    """
    Validate log cleanup parameters.
    
    Args:
        days_to_keep: Number of days to keep logs
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not isinstance(days_to_keep, int):
        raise ValidationError("days_to_keep must be an integer")
    
    if days_to_keep < 1:
        raise ValidationError("days_to_keep must be a positive integer")
    
    if days_to_keep > 365:
        raise ValidationError("days_to_keep cannot exceed 365 days")
    
    return True


def validate_settings_data(settings: Dict[str, Any], settings_type: str) -> bool:
    """
    Validate settings data based on type.
    
    Args:
        settings: Settings data dictionary
        settings_type: Type of settings ('api', 'output', 'logs', 'advanced')
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If settings are invalid
    """
    if settings_type == 'api':
        return validate_api_config(settings)
    elif settings_type == 'output':
        # Validate output settings
        if 'base_directory' in settings:
            validate_file_path(settings['base_directory'])
        if 'max_outputs_display' in settings:
            max_outputs = settings['max_outputs_display']
            if not isinstance(max_outputs, int) or max_outputs < 1 or max_outputs > 1000:
                raise ValidationError("max_outputs_display must be between 1 and 1000")
    elif settings_type == 'logs':
        if 'retention_days' in settings:
            validate_log_cleanup_params(settings['retention_days'])
    elif settings_type == 'advanced':
        # Validate advanced settings
        if 'max_concurrent_jobs' in settings:
            max_jobs = settings['max_concurrent_jobs']
            if not isinstance(max_jobs, int) or max_jobs < 1 or max_jobs > 10:
                raise ValidationError("max_concurrent_jobs must be between 1 and 10")
        if 'job_timeout' in settings:
            timeout = settings['job_timeout']
            if not isinstance(timeout, int) or timeout < 10 or timeout > 3600:
                raise ValidationError("job_timeout must be between 10 and 3600 seconds")
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed'
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def validate_image_data(image_data: str) -> bool:
    """
    Validate base64 image data.
    
    Args:
        image_data: Base64 encoded image data
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If image data is invalid
    """
    if not image_data:
        raise ValidationError("Image data cannot be empty")
    
    # Check if it looks like base64 data
    if not image_data.startswith('data:image/'):
        raise ValidationError("Invalid image data format")
    
    # Check reasonable size (max 10MB)
    if len(image_data) > 10 * 1024 * 1024:
        raise ValidationError("Image data too large (max 10MB)")
    
    return True


def validate_seed(seed: Optional[int]) -> None:
    """
    Validate seed value.
    
    Args:
        seed: Seed value to validate
        
    Raises:
        ValidationError: If seed is invalid
    """
    if seed is not None:
        if not isinstance(seed, int):
            raise ValidationError("Seed must be an integer")
        
        # Check reasonable range
        if seed < -1 or seed > 2**32 - 1:
            raise ValidationError("Seed must be between -1 and 4,294,967,295")


def validate_job_id(job_id: str) -> None:
    """
    Validate job ID.
    
    Args:
        job_id: Job ID to validate
        
    Raises:
        ValidationError: If job ID is invalid
    """
    if not job_id:
        raise ValidationError("Job ID is required")
    
    if not isinstance(job_id, str):
        raise ValidationError("Job ID must be a string")
    
    # Check for valid characters (alphanumeric, hyphens)
    if not re.match(r'^[a-zA-Z0-9-]+$', job_id):
        raise ValidationError("Job ID can only contain letters, numbers, and hyphens")
    
    # Check length
    if len(job_id) < 1 or len(job_id) > 50:
        raise ValidationError("Job ID must be between 1 and 50 characters")


def validate_date_format(date: str) -> None:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date: Date string to validate
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date:
        raise ValidationError("Date is required")
    
    if not isinstance(date, str):
        raise ValidationError("Date must be a string")
    
    # Check format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        raise ValidationError("Date must be in YYYY-MM-DD format")
    
    # Validate date components
    try:
        year, month, day = map(int, date.split('-'))
        if year < 1900 or year > 2100:
            raise ValidationError("Year must be between 1900 and 2100")
        if month < 1 or month > 12:
            raise ValidationError("Month must be between 1 and 12")
        if day < 1 or day > 31:
            raise ValidationError("Day must be between 1 and 31")
    except ValueError:
        raise ValidationError("Invalid date components")


def validate_filename(filename: str, required_extension: str = None) -> bool:
    """
    Validate filename.
    
    Args:
        filename: Filename to validate
        required_extension: Optional specific extension to require (e.g., '.png')
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If filename is invalid
    """
    if not filename:
        raise ValidationError("Filename is required")
    
    if not isinstance(filename, str):
        raise ValidationError("Filename must be a string")
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in filename:
            raise ValidationError(f"Filename cannot contain '{char}'")
    
    # Check length
    if len(filename) < 1 or len(filename) > 255:
        raise ValidationError("Filename must be between 1 and 255 characters")
    
    # Check for valid extension
    if '.' not in filename:
        raise ValidationError("Filename must have an extension")
    
    # Check for specific extension if required
    if required_extension:
        if not filename.lower().endswith(required_extension.lower()):
            raise ValidationError(f"Filename must end with {required_extension}")
        return True
    
    # Check for common image extensions
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    file_extension = filename.lower().split('.')[-1]
    if f'.{file_extension}' not in valid_extensions:
        raise ValidationError(f"File extension must be one of: {', '.join(valid_extensions)}")
    
    return True


def validate_url(url: str) -> None:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL is required")
    
    if not isinstance(url, str):
        raise ValidationError("URL must be a string")
    
    # Basic URL validation
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, url):
        raise ValidationError("URL must be a valid HTTP or HTTPS URL")
    
    # Check length
    if len(url) > 2048:
        raise ValidationError("URL must be less than 2048 characters")


def validate_username(username: str) -> None:
    """
    Validate username.
    
    Args:
        username: Username to validate
        
    Raises:
        ValidationError: If username is invalid
    """
    if not username:
        raise ValidationError("Username is required")
    
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    
    # Check length
    if len(username) < 1 or len(username) > 100:
        raise ValidationError("Username must be between 1 and 100 characters")
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")


def validate_password(password: str) -> None:
    """
    Validate password.
    
    Args:
        password: Password to validate
        
    Raises:
        ValidationError: If password is invalid
    """
    if not password:
        raise ValidationError("Password is required")
    
    if not isinstance(password, str):
        raise ValidationError("Password must be a string")
    
    # Check length
    if len(password) < 1 or len(password) > 100:
        raise ValidationError("Password must be between 1 and 100 characters") 