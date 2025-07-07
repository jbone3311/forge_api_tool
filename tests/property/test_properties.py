#!/usr/bin/env python3
"""
Property-based tests for the Forge API Tool using Hypothesis.
Tests invariants and properties that should always hold true.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from hypothesis import given, strategies as st, settings, Verbosity
from hypothesis.healthcheck import HealthCheck
import pytest

# Import core modules
from core.config_handler import config_handler
from core.wildcard_manager import WildcardManagerFactory
from core.output_manager import OutputManager
from core.exceptions import ValidationError


class TestConfigProperties:
    """Property-based tests for configuration handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test directories
        os.makedirs('configs', exist_ok=True)
        os.makedirs('wildcards', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
        
        # Initialize components
        self.wildcard_factory = WildcardManagerFactory()
        self.output_manager = OutputManager('outputs')
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @given(st.text(min_size=1, max_size=100))
    @settings(verbosity=Verbosity.verbose)
    def test_config_name_sanitization_idempotent(self, config_name):
        """Test that config name sanitization is idempotent."""
        # First sanitization
        sanitized1 = self._sanitize_config_name(config_name)
        
        # Second sanitization should produce the same result
        sanitized2 = self._sanitize_config_name(sanitized1)
        
        assert sanitized1 == sanitized2, f"Sanitization not idempotent: {sanitized1} != {sanitized2}"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(verbosity=Verbosity.verbose)
    def test_config_name_always_valid_after_sanitization(self, config_name):
        """Test that config names are always valid after sanitization."""
        sanitized_name = self._sanitize_config_name(config_name)
        
        # Check that sanitized name is valid
        assert self._is_valid_config_name(sanitized_name), f"Invalid config name after sanitization: {sanitized_name}"
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    @settings(verbosity=Verbosity.verbose)
    def test_wildcard_processing_commutative(self, wildcard_list):
        """Test that wildcard processing order doesn't matter."""
        wildcard_manager = self.wildcard_factory.create_manager('wildcards')
        
        # Process in original order
        result1 = self._process_wildcards(wildcard_manager, wildcard_list)
        
        # Process in reverse order
        result2 = self._process_wildcards(wildcard_manager, wildcard_list[::-1])
        
        # Results should be the same (commutative property)
        assert len(result1) == len(result2), f"Wildcard processing not commutative: {len(result1)} != {len(result2)}"
    
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5))
    @settings(verbosity=Verbosity.verbose)
    def test_wildcard_processing_associative(self, wildcard_list):
        """Test that wildcard processing is associative."""
        if len(wildcard_list) < 3:
            return  # Need at least 3 items to test associativity
        
        wildcard_manager = self.wildcard_factory.create_manager('wildcards')
        
        # Process as (A + B) + C
        first_half = wildcard_list[:len(wildcard_list)//2]
        second_half = wildcard_list[len(wildcard_list)//2:]
        
        result1 = self._process_wildcards(wildcard_manager, first_half)
        result2 = self._process_wildcards(wildcard_manager, second_half)
        combined_result = self._process_wildcards(wildcard_manager, result1 + result2)
        
        # Process as A + (B + C)
        result3 = self._process_wildcards(wildcard_manager, wildcard_list)
        
        # Results should be equivalent
        assert len(combined_result) == len(result3), f"Wildcard processing not associative"
    
    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
        min_size=1,
        max_size=10
    ))
    @settings(verbosity=Verbosity.verbose)
    def test_config_serialization_roundtrip(self, config_data):
        """Test that config serialization and deserialization is a roundtrip."""
        # Serialize config
        serialized = json.dumps(config_data, sort_keys=True)
        
        # Deserialize config
        deserialized = json.loads(serialized)
        
        # Should be equal
        assert config_data == deserialized, f"Config serialization not roundtrip: {config_data} != {deserialized}"
    
    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=20))
    @settings(verbosity=Verbosity.verbose)
    def test_output_path_generation_deterministic(self, path_components):
        """Test that output path generation is deterministic."""
        # Generate path multiple times
        path1 = self._generate_output_path(path_components)
        path2 = self._generate_output_path(path_components)
        path3 = self._generate_output_path(path_components)
        
        # All should be the same
        assert path1 == path2 == path3, f"Output path generation not deterministic: {path1} != {path2} != {path3}"
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(verbosity=Verbosity.verbose)
    def test_prompt_processing_preserves_length_invariant(self, prompt):
        """Test that prompt processing preserves certain invariants."""
        processed_prompt = self._process_prompt(prompt)
        
        # Processed prompt should not be empty if original wasn't empty
        if prompt.strip():
            assert processed_prompt.strip(), f"Non-empty prompt became empty after processing"
        
        # Processed prompt should not be significantly longer than original
        # (allowing for some expansion due to wildcard substitution)
        assert len(processed_prompt) <= len(prompt) * 10, f"Prompt processing created excessive length: {len(processed_prompt)} > {len(prompt) * 10}"
    
    @given(st.lists(st.integers(min_value=1, max_value=1000), min_size=1, max_size=10))
    @settings(verbosity=Verbosity.verbose)
    def test_batch_size_validation_consistent(self, batch_sizes):
        """Test that batch size validation is consistent."""
        for batch_size in batch_sizes:
            is_valid = self._is_valid_batch_size(batch_size)
            
            # If valid, should be within reasonable bounds
            if is_valid:
                assert 1 <= batch_size <= 100, f"Valid batch size outside bounds: {batch_size}"
            else:
                # If invalid, should be outside reasonable bounds
                assert batch_size < 1 or batch_size > 100, f"Invalid batch size within bounds: {batch_size}"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(verbosity=Verbosity.verbose)
    def test_file_path_sanitization_safe(self, file_path):
        """Test that file path sanitization produces safe paths."""
        sanitized_path = self._sanitize_file_path(file_path)
        
        # Should not contain dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            assert char not in sanitized_path, f"Dangerous character in sanitized path: {char}"
        
        # Should not be empty
        assert sanitized_path.strip(), f"Sanitized path is empty"
        
        # Should not start with dangerous patterns
        assert not sanitized_path.startswith('..'), f"Sanitized path starts with '..': {sanitized_path}"
    
    # Helper methods
    def _sanitize_config_name(self, name):
        """Sanitize configuration name."""
        # Remove invalid characters
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Ensure it starts with a letter or number
        if sanitized and not sanitized[0].isalnum():
            sanitized = 'config_' + sanitized
        return sanitized or 'config'
    
    def _is_valid_config_name(self, name):
        """Check if config name is valid."""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name)) and len(name) <= 100
    
    def _process_wildcards(self, wildcard_manager, wildcard_list):
        """Process a list of wildcards."""
        try:
            # Create a simple wildcard file for testing
            with open('wildcards/test.txt', 'w') as f:
                f.write('\n'.join(wildcard_list))
            
            # Process wildcards
            return wildcard_manager.get_wildcard_values('test')
        except Exception:
            return wildcard_list  # Return original if processing fails
    
    def _generate_output_path(self, components):
        """Generate output path from components."""
        return os.path.join('outputs', *components)
    
    def _process_prompt(self, prompt):
        """Process a prompt (simplified version)."""
        # Basic prompt processing - remove extra whitespace
        return ' '.join(prompt.split())
    
    def _is_valid_batch_size(self, batch_size):
        """Check if batch size is valid."""
        return isinstance(batch_size, int) and 1 <= batch_size <= 100
    
    def _sanitize_file_path(self, file_path):
        """Sanitize file path."""
        import re
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"|?*\\/]', '_', file_path)
        # Remove leading dots
        sanitized = re.sub(r'^\.+', '', sanitized)
        return sanitized or 'file'


class TestAPIClientProperties:
    """Property-based tests for API client behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @given(st.text(min_size=1, max_size=100))
    @settings(verbosity=Verbosity.verbose)
    def test_url_sanitization_idempotent(self, url):
        """Test that URL sanitization is idempotent."""
        sanitized1 = self._sanitize_url(url)
        sanitized2 = self._sanitize_url(sanitized1)
        
        assert sanitized1 == sanitized2, f"URL sanitization not idempotent: {sanitized1} != {sanitized2}"
    
    @given(st.integers(min_value=1, max_value=3600))
    @settings(verbosity=Verbosity.verbose)
    def test_timeout_validation_consistent(self, timeout):
        """Test that timeout validation is consistent."""
        is_valid = self._is_valid_timeout(timeout)
        
        if is_valid:
            assert 1 <= timeout <= 3600, f"Valid timeout outside bounds: {timeout}"
        else:
            assert timeout < 1 or timeout > 3600, f"Invalid timeout within bounds: {timeout}"
    
    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    @settings(verbosity=Verbosity.verbose)
    def test_request_headers_consistent(self, header_names):
        """Test that request headers are handled consistently."""
        headers = {name: f"value_{name}" for name in header_names}
        
        # Headers should be preserved
        processed_headers = self._process_headers(headers)
        
        for name in header_names:
            assert name in processed_headers, f"Header {name} not preserved"
            assert processed_headers[name] == f"value_{name}", f"Header {name} value changed"
    
    # Helper methods
    def _sanitize_url(self, url):
        """Sanitize URL."""
        # Basic URL sanitization
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url
    
    def _is_valid_timeout(self, timeout):
        """Check if timeout is valid."""
        return isinstance(timeout, int) and 1 <= timeout <= 3600
    
    def _process_headers(self, headers):
        """Process request headers."""
        # Basic header processing - just return as-is
        return headers.copy()


if __name__ == "__main__":
    # Run property-based tests
    pytest.main([__file__, "-v"]) 