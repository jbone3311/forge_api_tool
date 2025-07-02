"""
Image Analysis Service for analyzing images and extracting generation settings.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response
from core.image_analyzer import ImageAnalyzer
from core.centralized_logger import logger
from core.exceptions import ValidationError, FileOperationError


class ImageAnalysisService:
    """Service for analyzing images and extracting generation settings."""
    
    def __init__(self, analyzer_instance=None):
        """Initialize the image analysis service.
        
        Args:
            analyzer_instance: The image analyzer instance (defaults to new instance)
        """
        self.analyzer = analyzer_instance or ImageAnalyzer()
    
    def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze an uploaded image to extract generation settings.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dict containing analysis results or error response
        """
        try:
            if not image_data:
                return create_error_response('No image data provided', status_code=400)
            
            # Analyze the image
            result = self.analyzer.analyze_image(image_data)
            
            if not result.get('success', False):
                error_msg = result.get('error', 'Failed to analyze image')
                logger.log_error(f"Image analysis failed: {error_msg}")
                return create_error_response(error_msg, status_code=400)
            
            # Create suggested config from analysis if parameters are available
            if 'parameters' in result and 'prompt_info' in result:
                suggested_config = self._create_suggested_config_from_analysis(
                    result['parameters'], 
                    result['prompt_info']
                )
                result['suggested_config'] = suggested_config
            
            # Log successful analysis
            logger.log_app_event("image_analyzed", {
                "image_width": result.get('width', 0),
                "image_height": result.get('height', 0),
                "has_metadata": 'metadata' in result,
                "has_parameters": 'parameters' in result,
                "has_prompt": 'prompt' in result,
                "has_suggested_config": 'suggested_config' in result
            })
            
            return create_success_response(result)
            
        except (ValidationError, FileOperationError) as e:
            logger.log_error(f"Image analysis error: {e}")
            return create_error_response(str(e))
        except ValidationError as e:
            logger.log_error(f"Validation error in image analysis: {e}")
            return create_error_response(str(e))
        except Exception as e:
            logger.log_error(f"Unexpected error analyzing image: {e}")
            return create_error_response(f'Failed to analyze image: {str(e)}', status_code=500)
    
    def create_config_from_analysis(self, config_name: str, analysis_result: Dict[str, Any], 
                                   custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new configuration based on image analysis results.
        
        Args:
            config_name: Name for the new configuration
            analysis_result: Results from image analysis
            custom_settings: Optional custom settings to override defaults
            
        Returns:
            Dict containing success/error response
        """
        try:
            if not config_name:
                return create_error_response('Config name is required', status_code=400)
            
            if not analysis_result:
                return create_error_response('Analysis result is required', status_code=400)
            
            # Create base configuration from analysis
            base_config = self._create_base_config_from_analysis(config_name, analysis_result)
            
            # Override with custom settings if provided
            if custom_settings:
                base_config = self._merge_custom_settings(base_config, custom_settings)
            
            # Update name and description
            base_config['name'] = config_name
            if 'description' not in base_config:
                base_config['description'] = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            
            # Log successful config creation
            logger.log_app_event("config_created_from_image", {
                "config_name": config_name,
                "image_width": analysis_result.get('width', 0),
                "image_height": analysis_result.get('height', 0),
                "has_metadata": 'metadata' in analysis_result,
                "has_parameters": 'parameters' in analysis_result,
                "has_custom_settings": custom_settings is not None
            })
            
            return create_success_response({
                'message': f'Configuration {config_name} created successfully',
                'config_name': config_name,
                'config': base_config,
                'timestamp': datetime.now().isoformat()
            })
            
        except (ValidationError, FileOperationError) as e:
            logger.log_error(f"Image analysis error creating config: {e}")
            return create_error_response(str(e))
        except ValidationError as e:
            logger.log_error(f"Validation error creating config: {e}")
            return create_error_response(str(e))
        except Exception as e:
            logger.log_error(f"Unexpected error creating config from image: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    def extract_image_metadata(self, image_data: str) -> Dict[str, Any]:
        """Extract metadata from an image without full analysis.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dict containing metadata or error response
        """
        try:
            if not image_data:
                return create_error_response('No image data provided', status_code=400)
            
            # Extract basic metadata
            metadata = self.analyzer.extract_metadata(image_data)
            
            if not metadata:
                return create_error_response('No metadata found in image', status_code=404)
            
            logger.log_app_event("metadata_extracted", {
                "has_metadata": bool(metadata),
                "metadata_keys": list(metadata.keys()) if metadata else []
            })
            
            return create_success_response({
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.log_error(f"Error extracting metadata: {e}")
            return create_error_response(f'Failed to extract metadata: {str(e)}', status_code=500)
    
    def validate_image_format(self, image_data: str) -> Dict[str, Any]:
        """Validate image format and basic properties.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dict containing validation results or error response
        """
        try:
            if not image_data:
                return create_error_response('No image data provided', status_code=400)
            
            # Validate image format
            validation_result = self.analyzer.validate_image_format(image_data)
            
            logger.log_app_event("image_validated", {
                "is_valid": validation_result.get('valid', False),
                "format": validation_result.get('format', 'unknown'),
                "width": validation_result.get('width', 0),
                "height": validation_result.get('height', 0)
            })
            
            return create_success_response(validation_result)
            
        except Exception as e:
            logger.log_error(f"Error validating image: {e}")
            return create_error_response(f'Failed to validate image: {str(e)}', status_code=500)
    
    def _create_suggested_config_from_analysis(self, parameters: Dict[str, Any], 
                                             prompt_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a suggested configuration from analysis parameters and prompt info.
        
        Args:
            parameters: Generation parameters from analysis
            prompt_info: Prompt information from analysis
            
        Returns:
            Dict containing suggested configuration
        """
        try:
            return self.analyzer._create_suggested_config(parameters, prompt_info)
        except Exception as e:
            logger.log_error(f"Error creating suggested config: {e}")
            # Return a basic config if the analyzer method fails
            return self._create_basic_config_from_parameters(parameters, prompt_info)
    
    def _create_base_config_from_analysis(self, config_name: str, 
                                        analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a base configuration from image analysis results.
        
        Args:
            config_name: Name for the configuration
            analysis_result: Results from image analysis
            
        Returns:
            Dict containing base configuration
        """
        # Check if there's a suggested config in the analysis result
        if 'suggested_config' in analysis_result:
            suggested_config = analysis_result['suggested_config']
            
            # Handle case where suggested_config might be a string
            if isinstance(suggested_config, str):
                try:
                    # Try to parse as JSON
                    base_config = json.loads(suggested_config)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, use as description
                    base_config = self._create_basic_config_from_analysis(
                        config_name, analysis_result, suggested_config
                    )
            else:
                # It's already a dictionary
                base_config = suggested_config
        else:
            # Create basic config if no suggested config
            base_config = self._create_basic_config_from_analysis(config_name, analysis_result)
        
        return base_config
    
    def _create_basic_config_from_analysis(self, config_name: str, 
                                         analysis_result: Dict[str, Any], 
                                         description: Optional[str] = None) -> Dict[str, Any]:
        """Create a basic configuration from image analysis results.
        
        Args:
            config_name: Name for the configuration
            analysis_result: Results from image analysis
            description: Optional description
            
        Returns:
            Dict containing basic configuration
        """
        if description is None:
            description = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        return {
            'name': config_name,
            'description': description,
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': analysis_result.get('prompt', ''),
                'negative_prompt': analysis_result.get('negative_prompt', '')
            },
            'generation_settings': {
                'steps': analysis_result.get('steps', 20),
                'width': analysis_result.get('width', 512),
                'height': analysis_result.get('height', 512),
                'batch_size': analysis_result.get('batch_size', 1),
                'sampler': analysis_result.get('sampler', 'Euler a'),
                'cfg_scale': analysis_result.get('cfg_scale', 7.0)
            },
            'model_settings': {
                'checkpoint': analysis_result.get('checkpoint', ''),
                'vae': analysis_result.get('vae', ''),
                'text_encoder': analysis_result.get('text_encoder', ''),
                'gpu_weight': analysis_result.get('gpu_weight', 1.0),
                'swap_method': analysis_result.get('swap_method', 'weight'),
                'swap_location': analysis_result.get('swap_location', 'cpu')
            },
            'output_settings': {
                'dir': f'outputs/{config_name}/{{timestamp}}/',
                'format': analysis_result.get('format', 'png'),
                'save_metadata': True,
                'save_prompts': True
            }
        }
    
    def _create_basic_config_from_parameters(self, parameters: Dict[str, Any], 
                                           prompt_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic configuration from parameters and prompt info.
        
        Args:
            parameters: Generation parameters
            prompt_info: Prompt information
            
        Returns:
            Dict containing basic configuration
        """
        return {
            'name': f'config_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Config created from image analysis',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': prompt_info.get('prompt', ''),
                'negative_prompt': prompt_info.get('negative_prompt', '')
            },
            'generation_settings': {
                'steps': parameters.get('steps', 20),
                'width': parameters.get('width', 512),
                'height': parameters.get('height', 512),
                'batch_size': parameters.get('batch_size', 1),
                'sampler': parameters.get('sampler', 'Euler a'),
                'cfg_scale': parameters.get('cfg_scale', 7.0)
            },
            'model_settings': {
                'checkpoint': parameters.get('checkpoint', ''),
                'vae': parameters.get('vae', ''),
                'text_encoder': parameters.get('text_encoder', ''),
                'gpu_weight': parameters.get('gpu_weight', 1.0),
                'swap_method': parameters.get('swap_method', 'weight'),
                'swap_location': parameters.get('swap_location', 'cpu')
            },
            'output_settings': {
                'dir': f'outputs/config_{{timestamp}}/',
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            }
        }
    
    def _merge_custom_settings(self, base_config: Dict[str, Any], 
                             custom_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge custom settings with base configuration.
        
        Args:
            base_config: Base configuration
            custom_settings: Custom settings to merge
            
        Returns:
            Dict containing merged configuration
        """
        merged_config = base_config.copy()
        
        for section, settings in custom_settings.items():
            if section in merged_config:
                if isinstance(settings, dict) and isinstance(merged_config[section], dict):
                    # Merge dictionaries
                    merged_config[section].update(settings)
                else:
                    # Replace non-dict values
                    merged_config[section] = settings
            else:
                # Add new sections
                merged_config[section] = settings
        
        return merged_config 