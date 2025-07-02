"""
Output Service - Handles all output management operations
"""

import os
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
from flask import send_file, jsonify

import sys
import os
# Add the parent directory to the path to import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.exceptions import FileOperationError
from utils.response_helpers import create_success_response, create_error_response
from utils.validators import validate_date_format, validate_filename


class OutputService:
    """Service class for managing output operations."""
    
    def __init__(self, output_manager, logger):
        """Initialize the output service.
        
        Args:
            output_manager: The output manager instance
            logger: The logger instance
        """
        self.output_manager = output_manager
        self.logger = logger
    
    def get_outputs(self, date: str = None, config_name: str = None) -> Dict[str, Any]:
        """Get outputs with optional filtering by date or config.
        
        Args:
            date: Optional date filter (YYYY-MM-DD format)
            config_name: Optional config name filter
            
        Returns:
            Dictionary containing outputs and metadata
        """
        try:
            # Get outputs for today by default
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            if config_name:
                # Get outputs for specific config
                outputs = self.output_manager.get_outputs_for_config(config_name)
            else:
                # Get outputs for specific date
                outputs = self.output_manager.get_outputs_for_date(date)
            
            # Format outputs for frontend
            formatted_outputs = []
            for output in outputs:
                formatted_output = {
                    'filename': output.get('filename', ''),
                    'filepath': output.get('filepath', ''),
                    'config_name': output.get('config_name', ''),
                    'prompt': output.get('prompt', ''),
                    'seed': output.get('seed', 0),
                    'created_at': output.get('generation_time', ''),
                    'date': output.get('date', ''),
                    'steps': output.get('steps', 20),
                    'sampler_name': output.get('sampler_name', ''),
                    'cfg_scale': output.get('cfg_scale', 7.0),
                    'width': output.get('width', 512),
                    'height': output.get('height', 512),
                    'model_name': output.get('model_name', ''),
                    'negative_prompt': output.get('negative_prompt', '')
                }
                formatted_outputs.append(formatted_output)
            
            self.logger.log_app_event("outputs_retrieved", {
                "date": date,
                "config_name": config_name,
                "output_count": len(formatted_outputs)
            })
            
            return create_success_response({
                'outputs': formatted_outputs,
                'date': date,
                'config_name': config_name
            })
            
        except Exception as e:
            self.logger.log_error(f"Error getting outputs: {e}")
            return create_error_response(str(e), 500)
    
    def get_output_statistics(self) -> Dict[str, Any]:
        """Get output statistics.
        
        Returns:
            Dictionary containing output statistics
        """
        try:
            stats = self.output_manager.get_output_statistics()
            
            self.logger.log_app_event("output_statistics_retrieved", stats)
            
            return create_success_response({'statistics': stats})
            
        except Exception as e:
            self.logger.log_error(f"Error getting output statistics: {e}")
            return create_error_response(str(e), 500)
    
    def get_output_dates(self) -> Dict[str, Any]:
        """Get all available output dates.
        
        Returns:
            Dictionary containing available dates
        """
        try:
            dates = []
            if os.path.exists(self.output_manager.base_output_dir):
                date_dirs = [d for d in os.listdir(self.output_manager.base_output_dir) 
                            if os.path.isdir(os.path.join(self.output_manager.base_output_dir, d)) and 
                            re.match(r'\d{4}-\d{2}-\d{2}', d)]
                dates = sorted(date_dirs, reverse=True)
            
            return create_success_response({'dates': dates})
            
        except Exception as e:
            self.logger.log_error(f"Error getting output dates: {e}")
            return create_error_response(str(e), 500)
    
    def serve_output_image(self, date: str, filename: str):
        """Serve output images from date-based folders.
        
        Args:
            date: Date in YYYY-MM-DD format
            filename: Image filename
            
        Returns:
            Flask response with image file or error
        """
        try:
            # Validate date format
            if not validate_date_format(date):
                return create_error_response('Invalid date format', 400)
            
            # Validate filename
            if not validate_filename(filename, '.png'):
                return create_error_response('Invalid file type', 400)
            
            # Construct file path
            file_path = os.path.join(self.output_manager.base_output_dir, date, filename)
            
            if not os.path.exists(file_path):
                return create_error_response('File not found', 404)
            
            # Serve the image file
            return send_file(file_path, mimetype='image/png')
            
        except Exception as e:
            self.logger.log_error(f"Error serving output image: {e}")
            return create_error_response(str(e), 500)
    
    def get_output_metadata(self, date: str, filename: str) -> Dict[str, Any]:
        """Get metadata for a specific output image.
        
        Args:
            date: Date in YYYY-MM-DD format
            filename: Image filename
            
        Returns:
            Dictionary containing metadata or error
        """
        try:
            # Validate date format
            if not validate_date_format(date):
                return create_error_response('Invalid date format', 400)
            
            # Validate filename
            if not validate_filename(filename, '.png'):
                return create_error_response('Invalid file type', 400)
            
            # Construct file path
            file_path = os.path.join(self.output_manager.base_output_dir, date, filename)
            
            if not os.path.exists(file_path):
                return create_error_response('File not found', 404)
            
            # Extract metadata from image
            metadata = self.output_manager.extract_metadata_from_image(file_path)
            
            if not metadata:
                return create_error_response('No metadata found', 404)
            
            return create_success_response({'metadata': metadata})
            
        except Exception as e:
            self.logger.log_error(f"Error getting output metadata: {e}")
            return create_error_response(str(e), 500)
    
    def get_output_directory(self, config_name: str) -> Dict[str, Any]:
        """Get the output directory path for a specific config.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Dictionary containing directory information
        """
        try:
            directory_path = self.output_manager.get_output_directory(config_name)
            return create_success_response({
                'config_name': config_name,
                'directory_path': directory_path,
                'exists': os.path.exists(directory_path)
            })
        except Exception as e:
            self.logger.log_error(f"Failed to get output directory for {config_name}: {e}")
            return create_error_response(str(e), 400)
    
    def get_latest_output_directory(self, config_name: str) -> Dict[str, Any]:
        """Get the most recent output directory for a specific config.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Dictionary containing latest directory information
        """
        try:
            directory_path = self.output_manager.get_latest_output_directory(config_name)
            return create_success_response({
                'config_name': config_name,
                'directory_path': directory_path,
                'exists': os.path.exists(directory_path)
            })
        except Exception as e:
            self.logger.log_error(f"Failed to get latest output directory for {config_name}: {e}")
            return create_error_response(str(e), 400)
    
    def open_output_folder(self, config_name: str) -> Dict[str, Any]:
        """Open the output folder for a specific configuration.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Dictionary containing operation result
        """
        try:
            self.logger.log_app_event("output_folder_opened", {"config_name": config_name})
            
            # Get the output directory for the configuration
            output_dir = self.output_manager.get_output_directory(config_name)
            
            if not output_dir or not os.path.exists(output_dir):
                # Create the directory if it doesn't exist
                output_dir = self.output_manager.create_output_directory(config_name)
                self.logger.info(f"Created output directory: {output_dir}")
            
            # Open the folder using the system's default file manager
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS and Linux
                if sys.platform == 'darwin':  # macOS
                    os.system(f'open "{output_dir}"')
                else:  # Linux
                    os.system(f'xdg-open "{output_dir}"')
            
            return create_success_response({
                'directory_path': output_dir,
                'message': f'Opened output folder for {config_name}'
            })
            
        except FileOperationError as e:
            self.logger.log_error(f"File operation error opening folder: {e}")
            return create_error_response(f'File operation error: {e}', 500)
        except Exception as e:
            self.logger.log_error(f"Unexpected error opening folder: {e}")
            return create_error_response(f'Unexpected error: {e}', 500) 