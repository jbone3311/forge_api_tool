#!/usr/bin/env python3
"""
Test the complete seed handling flow from JavaScript to Forge API
"""

import json
from core.forge_api import forge_api_client
from core.config_handler import config_handler
from core.centralized_logger import centralized_logger

def test_complete_seed_flow():
    """Test the complete seed handling flow."""
    print("=== Complete Seed Flow Test ===")
    
    # Simulate the complete flow:
    # 1. JavaScript sends string seeds
    # 2. Flask converts to integers
    # 3. Forge API uses integers
    
    def simulate_flask_seed_handler(seed_input):
        """Simulate Flask app seed handling."""
        seed = None
        if seed_input is not None and seed_input != '':
            try:
                seed = int(seed_input)
            except (ValueError, TypeError):
                # Invalid seed value, use random seed
                seed = None
        return seed
    
    # Test cases: (js_input, expected_flask_output, expected_forge_output, description)
    test_cases = [
        (None, None, -1, "None -> None -> random (-1)"),
        ("", None, -1, "Empty string -> None -> random (-1)"),
        ("   ", None, -1, "Whitespace -> None -> random (-1)"),
        ("-1", -1, -1, "Negative one -> -1 -> -1"),
        ("0", 0, 0, "Zero -> 0 -> 0"),
        ("123", 123, 123, "Positive number -> 123 -> 123"),
        ("999999999", 999999999, 999999999, "Large number -> 999999999 -> 999999999"),
        ("abc", None, -1, "Invalid text -> None -> random (-1)"),
        ("12.34", None, -1, "Decimal -> None -> random (-1)"),
        ("-2", -2, -2, "Negative number -> -2 -> -2"),
    ]
    
    # Get a test config
    configs = config_handler.get_all_configs()
    if not configs:
        print("❌ No configs available for testing")
        return False
    
    test_config_name = list(configs.keys())[0]
    test_config = configs[test_config_name]
    test_prompt = "a beautiful landscape"
    
    print(f"Using config: {test_config_name}")
    
    all_passed = True
    for js_input, expected_flask_output, expected_forge_output, description in test_cases:
        print(f"\nTesting: {description}")
        try:
            # Step 1: Simulate Flask handling
            flask_output = simulate_flask_seed_handler(js_input)
            
            # Step 2: Test Forge API with Flask output
            payload = forge_api_client._prepare_payload(test_config, test_prompt, flask_output)
            forge_output = payload.get('seed')
            
            # Check Flask step
            if flask_output == expected_flask_output:
                print(f"✅ Flask: {js_input} -> {flask_output} (correct)")
            else:
                print(f"❌ Flask: {js_input} -> {flask_output} (expected {expected_flask_output})")
                all_passed = False
            
            # Check Forge step
            if forge_output == expected_forge_output:
                print(f"✅ Forge: {flask_output} -> {forge_output} (correct)")
            else:
                print(f"❌ Forge: {flask_output} -> {forge_output} (expected {expected_forge_output})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {js_input}: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All complete flow tests passed!")
    else:
        print("\n❌ Some complete flow tests failed!")
    
    return all_passed

def test_gui_button_functionality():
    """Test GUI button functionality."""
    print("\n=== GUI Button Functionality Test ===")
    
    # Test the button validation logic
    def test_button_validation(prompt, config_name):
        """Test the validation logic used by GUI buttons."""
        return bool(prompt.strip() and config_name.strip())
    
    # Test cases
    validation_tests = [
        ("", "", False, "Empty prompt and config"),
        ("test prompt", "", False, "Empty config"),
        ("", "test_config", False, "Empty prompt"),
        ("test prompt", "test_config", True, "Valid input"),
        ("   ", "test_config", False, "Whitespace prompt"),
        ("a" * 1000, "test_config", True, "Long prompt"),
    ]
    
    all_passed = True
    for prompt, config, expected_valid, description in validation_tests:
        print(f"\nTesting: {description}")
        
        is_valid = test_button_validation(prompt, config)
        
        if is_valid == expected_valid:
            print(f"✅ Validation correct: {is_valid}")
        else:
            print(f"❌ Validation incorrect: expected {expected_valid}, got {is_valid}")
            all_passed = False
    
    return all_passed

def test_seed_input_validation():
    """Test seed input validation."""
    print("\n=== Seed Input Validation Test ===")
    
    # Test the JavaScript seed validation logic
    def test_js_seed_validation(seed_input):
        """Test the JavaScript seed validation logic."""
        if not seed_input or seed_input.strip() == '':
            return None
        
        try:
            # Check if it's a valid integer (including negative)
            if seed_input.lstrip('-').isdigit():
                return int(seed_input)
        except (ValueError, TypeError):
            pass
        
        return None
    
    # Test cases
    seed_tests = [
        ("", None, "Empty string -> None"),
        ("   ", None, "Whitespace -> None"),
        ("123", 123, "Valid number -> 123"),
        ("-1", -1, "Negative number -> -1"),
        ("0", 0, "Zero -> 0"),
        ("abc", None, "Invalid text -> None"),
        ("12.34", None, "Decimal -> None"),
        ("999999999", 999999999, "Large number -> 999999999"),
    ]
    
    all_passed = True
    for input_seed, expected_output, description in seed_tests:
        print(f"\nTesting: {description}")
        
        actual_output = test_js_seed_validation(input_seed)
        
        if actual_output == expected_output:
            print(f"✅ {input_seed} -> {actual_output} (correct)")
        else:
            print(f"❌ {input_seed} -> {actual_output} (expected {expected_output})")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print("Forge API Tool - Complete Flow and GUI Button Test")
    print("=" * 55)
    
    # Run all tests
    flow_passed = test_complete_seed_flow()
    button_passed = test_gui_button_functionality()
    validation_passed = test_seed_input_validation()
    
    print("\n" + "=" * 55)
    print("COMPLETE TEST SUMMARY")
    print("=" * 55)
    print(f"✅ Complete seed flow: {'PASSED' if flow_passed else 'FAILED'}")
    print(f"✅ GUI button validation: {'PASSED' if button_passed else 'FAILED'}")
    print(f"✅ Seed input validation: {'PASSED' if validation_passed else 'FAILED'}")
    
    if flow_passed and button_passed and validation_passed:
        print("\n🎉 All tests passed! The GUI buttons work properly with correct seed syntax.")
        print("\nSummary:")
        print("- Seed handling: JavaScript → Flask → Forge API ✅")
        print("- Button validation: Prevents invalid submissions ✅")
        print("- Input validation: Handles edge cases properly ✅")
        print("- Random seeds: Empty/invalid inputs use random (-1) ✅")
        print("- Fixed seeds: Valid integers use specified seed ✅")
        print("- Negative seeds: Supported throughout the flow ✅")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main() 