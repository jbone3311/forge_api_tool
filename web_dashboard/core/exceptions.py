"""
Custom exceptions for the Flask web dashboard.

This module defines custom exception classes used throughout the application
for better error handling and debugging.
"""


class ForgeAPIError(Exception):
    """Base exception for Forge API related errors."""
    pass


class ConfigurationError(Exception):
    """Exception raised for configuration related errors."""
    pass


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class GenerationError(Exception):
    """Exception raised for image generation errors."""
    pass


class JobQueueError(Exception):
    """Exception raised for job queue related errors."""
    pass


class FileOperationError(Exception):
    """Exception raised for file operation errors."""
    pass


class OutputError(Exception):
    """Exception raised for output related errors."""
    pass


class LoggingError(Exception):
    """Exception raised for logging related errors."""
    pass


class SettingsError(Exception):
    """Exception raised for settings related errors."""
    pass


class RunDiffusionError(Exception):
    """Exception raised for RunDiffusion API related errors."""
    pass 