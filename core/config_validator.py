#!/usr/bin/env python3
"""
Configuration Validator

Provides real-time validation for configuration parameters.
"""

from typing import Dict, List, Any, Optional, Tuple
import re


class ValidationResult:
    """Result of a validation check."""
    
    def __init__(self, is_valid: bool, message: str = "", warnings: List[str] = None):
        self.is_valid = is_valid
        self.message = message
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'message': self.message,
            'warnings': self.warnings
        }


class ConfigValidator:
    """Validates configuration parameters."""
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.validation_rules = self._get_default_validation_rules()
        self.api_provider_rules = self._get_api_provider_rules()
    
    def _get_default_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get default validation rules for common parameters."""
        return {
            'width': {
                'type': int,
                'min_value': 64,
                'max_value': 2048,
                'multiple_of': 8,
                'message': 'Width must be an integer between 64 and 2048, divisible by 8'
            },
            'height': {
                'type': int,
                'min_value': 64,
                'max_value': 2048,
                'multiple_of': 8,
                'message': 'Height must be an integer between 64 and 2048, divisible by 8'
            },
            'steps': {
                'type': int,
                'min_value': 1,
                'max_value': 150,
                'message': 'Steps must be an integer between 1 and 150'
            },
            'cfg_scale': {
                'type': (int, float),
                'min_value': 1.0,
                'max_value': 30.0,
                'message': 'CFG Scale must be a number between 1.0 and 30.0'
            },
            'seed': {
                'type': int,
                'min_value': -1,
                'max_value': 2**32 - 1,
                'message': 'Seed must be an integer between -1 and 4294967295'
            },
            'batch_size': {
                'type': int,
                'min_value': 1,
                'max_value': 8,
                'message': 'Batch size must be an integer between 1 and 8'
            },
            'batch_count': {
                'type': int,
                'min_value': 1,
                'max_value': 100,
                'message': 'Batch count must be an integer between 1 and 100'
            }
        }
    
    def _get_api_provider_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get validation rules specific to API providers."""
        return {
            'local': {
                'supported_samplers': [
                    'DPM++ 2M Karras', 'DPM++ SDE Karras', 'DPM++ 2M SDE Exponential',
                    'DPM++ 2M SDE Karras', 'Euler a', 'Euler', 'LMS', 'Heun', 'DPM2',
                    'DPM2 a', 'DPM++ 2S a', 'DPM++ 2M', 'DPM++ SDE', 'DPM++ 2M SDE',
                    'DPM++ 2M SDE Heun', 'DPM++ 2M SDE Heun Karras', 'DPM++ 2M SDE Heun Exponential',
                    'DPM++ 3M SDE', 'DPM++ 3M SDE Karras', 'DPM++ 3M SDE Exponential',
                    'DPM fast', 'DPM adaptive', 'LMS Karras', 'DPM2 Karras', 'DPM2 a Karras',
                    'DPM++ 2S a Karras', 'Restart', 'DDIM', 'PLMS', 'UniPC'
                ],
                'max_resolution': 2048,
                'max_steps': 150
            },
            'rundiffusion': {
                'supported_samplers': [
                    'DPM++ 2M Karras', 'DPM++ SDE Karras', 'Euler a', 'Euler', 'LMS',
                    'Heun', 'DPM2', 'DPM2 a', 'DPM++ 2S a', 'DPM++ 2M', 'DPM++ SDE',
                    'DPM fast', 'DPM adaptive', 'LMS Karras', 'DPM2 Karras', 'DDIM', 'PLMS'
                ],
                'max_resolution': 1024,
                'max_steps': 50
            },
            'pinokio': {
                'supported_samplers': [
                    'DPM++ 2M Karras', 'Euler a', 'Euler', 'LMS', 'Heun', 'DPM2',
                    'DPM++ 2M', 'DPM fast', 'DDIM', 'PLMS'
                ],
                'max_resolution': 1024,
                'max_steps': 30
            }
        }
    
    def validate_config(self, config: Dict[str, Any], api_provider: str = 'local') -> Dict[str, ValidationResult]:
        """Validate a complete configuration."""
        results = {}
        
        for param_name, value in config.items():
            if param_name in self.validation_rules:
                result = self.validate_parameter(param_name, value, api_provider)
                results[param_name] = result
        
        # Add provider-specific validations
        provider_results = self.validate_provider_specific(config, api_provider)
        results.update(provider_results)
        
        return results
    
    def validate_parameter(self, param_name: str, value: Any, api_provider: str = 'local') -> ValidationResult:
        """Validate a single parameter."""
        if param_name not in self.validation_rules:
            return ValidationResult(True, "No validation rules for this parameter")
        
        rules = self.validation_rules[param_name]
        warnings = []
        
        # Type validation
        if not isinstance(value, rules['type']):
            return ValidationResult(False, f"{param_name} must be of type {rules['type'].__name__}")
        
        # Range validation
        if 'min_value' in rules and value < rules['min_value']:
            return ValidationResult(False, f"{param_name} must be at least {rules['min_value']}")
        
        if 'max_value' in rules and value > rules['max_value']:
            return ValidationResult(False, f"{param_name} must be at most {rules['max_value']}")
        
        # Multiple of validation
        if 'multiple_of' in rules and value % rules['multiple_of'] != 0:
            return ValidationResult(False, f"{param_name} must be divisible by {rules['multiple_of']}")
        
        # Provider-specific validations
        if api_provider in self.api_provider_rules:
            provider_rules = self.api_provider_rules[api_provider]
            
            # Check max resolution for dimensions
            if param_name in ['width', 'height'] and 'max_resolution' in provider_rules:
                if value > provider_rules['max_resolution']:
                    warnings.append(f"Provider {api_provider} supports max resolution of {provider_rules['max_resolution']}")
            
            # Check max steps
            if param_name == 'steps' and 'max_steps' in provider_rules:
                if value > provider_rules['max_steps']:
                    warnings.append(f"Provider {api_provider} supports max steps of {provider_rules['max_steps']}")
        
        # Special validations
        if param_name == 'cfg_scale' and value > 20:
            warnings.append("High CFG Scale values (>20) may produce over-saturated results")
        
        if param_name in ['width', 'height'] and value > 1024:
            warnings.append("Large dimensions may require significant memory and processing time")
        
        if param_name == 'steps' and value > 50:
            warnings.append("High step counts may not provide significant quality improvements")
        
        return ValidationResult(True, "Parameter is valid", warnings)
    
    def validate_provider_specific(self, config: Dict[str, Any], api_provider: str) -> Dict[str, ValidationResult]:
        """Validate provider-specific parameters."""
        results = {}
        
        if api_provider not in self.api_provider_rules:
            return results
        
        provider_rules = self.api_provider_rules[api_provider]
        
        # Validate sampler
        if 'sampler_name' in config:
            sampler = config['sampler_name']
            supported_samplers = provider_rules.get('supported_samplers', [])
            
            if sampler not in supported_samplers:
                results['sampler_name'] = ValidationResult(
                    False, 
                    f"Sampler '{sampler}' is not supported by {api_provider}. "
                    f"Supported samplers: {', '.join(supported_samplers[:5])}..."
                )
            else:
                results['sampler_name'] = ValidationResult(True, "Sampler is supported")
        
        # Validate resolution constraints
        width = config.get('width', 512)
        height = config.get('height', 512)
        max_resolution = provider_rules.get('max_resolution', 2048)
        
        if width > max_resolution or height > max_resolution:
            results['resolution'] = ValidationResult(
                False,
                f"Resolution {width}x{height} exceeds {api_provider}'s max resolution of {max_resolution}"
            )
        
        # Validate aspect ratio warnings
        aspect_ratio = width / height
        if aspect_ratio > 2.0 or aspect_ratio < 0.5:
            results['aspect_ratio'] = ValidationResult(
                True,
                "Valid aspect ratio",
                [f"Extreme aspect ratio ({aspect_ratio:.2f}) may produce unexpected results"]
            )
        
        return results
    
    def get_parameter_suggestions(self, param_name: str, current_value: Any, api_provider: str = 'local') -> Dict[str, Any]:
        """Get suggestions for a parameter."""
        suggestions = {
            'current_value': current_value,
            'recommended_value': current_value,
            'alternatives': [],
            'tips': []
        }
        
        if param_name == 'steps':
            if api_provider == 'rundiffusion':
                suggestions['recommended_value'] = min(30, current_value)
                suggestions['tips'].append("RunDiffusion works best with 20-30 steps")
            elif api_provider == 'pinokio':
                suggestions['recommended_value'] = min(20, current_value)
                suggestions['tips'].append("PINOKIO works best with 15-25 steps")
            else:
                suggestions['recommended_value'] = min(50, current_value)
                suggestions['tips'].append("Local generation works well with 20-50 steps")
        
        elif param_name == 'cfg_scale':
            if current_value < 5:
                suggestions['recommended_value'] = 7.5
                suggestions['tips'].append("CFG Scale 7-8 provides good balance of quality and creativity")
            elif current_value > 15:
                suggestions['recommended_value'] = 12
                suggestions['tips'].append("High CFG Scale may produce over-saturated results")
        
        elif param_name in ['width', 'height']:
            if api_provider in ['rundiffusion', 'pinokio']:
                suggestions['recommended_value'] = min(1024, current_value)
                suggestions['tips'].append(f"{api_provider} supports up to 1024x1024")
            
            # Suggest common resolutions
            common_resolutions = [
                (512, 512), (768, 768), (1024, 1024),
                (512, 768), (768, 512), (1024, 768), (768, 1024)
            ]
            suggestions['alternatives'] = [
                f"{w}x{h}" for w, h in common_resolutions 
                if w <= 1024 and h <= 1024
            ]
        
        elif param_name == 'sampler_name':
            if api_provider in self.api_provider_rules:
                supported = self.api_provider_rules[api_provider].get('supported_samplers', [])
                suggestions['alternatives'] = supported[:10]  # Top 10 supported samplers
        
        return suggestions
    
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate a prompt."""
        warnings = []
        
        if not prompt or not prompt.strip():
            return ValidationResult(False, "Prompt cannot be empty")
        
        # Check for very long prompts
        if len(prompt) > 2000:
            warnings.append("Very long prompts may be truncated by some models")
        
        # Check for potentially problematic patterns
        if re.search(r'\{[^}]{50,}\}', prompt):
            warnings.append("Very long wildcard expansions may cause issues")
        
        # Check for balanced brackets
        open_brackets = prompt.count('{')
        close_brackets = prompt.count('}')
        if open_brackets != close_brackets:
            return ValidationResult(False, f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
        
        return ValidationResult(True, "Prompt is valid", warnings)
    
    def get_validation_summary(self, config: Dict[str, Any], api_provider: str = 'local') -> Dict[str, Any]:
        """Get a summary of configuration validation."""
        validation_results = self.validate_config(config, api_provider)
        
        total_params = len(validation_results)
        valid_params = sum(1 for result in validation_results.values() if result.is_valid)
        invalid_params = total_params - valid_params
        
        all_warnings = []
        for result in validation_results.values():
            all_warnings.extend(result.warnings)
        
        return {
            'overall_valid': invalid_params == 0,
            'total_parameters': total_params,
            'valid_parameters': valid_params,
            'invalid_parameters': invalid_params,
            'total_warnings': len(all_warnings),
            'warnings': all_warnings,
            'api_provider': api_provider,
            'parameter_results': {k: v.to_dict() for k, v in validation_results.items()}
        }


# Global validator instance
_validator = None


def get_config_validator() -> ConfigValidator:
    """Get the global config validator instance."""
    global _validator
    if _validator is None:
        _validator = ConfigValidator()
    return _validator

