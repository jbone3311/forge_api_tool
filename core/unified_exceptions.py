#!/usr/bin/env python3
"""
Unified Exception Hierarchy

Standardized exception classes for the Forge API Tool.
"""


class ForgeAPIError(Exception):
    """Base exception for all Forge API Tool errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(ForgeAPIError):
    """Configuration-related errors."""
    pass


class ValidationError(ForgeAPIError):
    """Validation-related errors."""
    pass


class APIError(ForgeAPIError):
    """API-related errors."""
    pass


class ConnectionError(ForgeAPIError):
    """Connection-related errors."""
    pass


class GenerationError(ForgeAPIError):
    """Image generation errors."""
    pass


class FileOperationError(ForgeAPIError):
    """File operation errors."""
    pass


class WildcardError(ForgeAPIError):
    """Wildcard-related errors."""
    pass


class OutputError(ForgeAPIError):
    """Output management errors."""
    pass


class CLIError(ForgeAPIError):
    """CLI-related errors."""
    pass


class ServiceError(ForgeAPIError):
    """Service layer errors."""
    pass
