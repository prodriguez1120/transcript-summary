#!/usr/bin/env python3
"""
Test Script for Modular Prompt System

This script tests the functionality of the new modular prompt system
to ensure it works correctly with all prompt types.
"""

import json
import os
from prompt_config import PromptConfig, get_prompt_config

def test_prompt_config_loading():
    """Test that prompt configuration loads correctly."""
    print("Testing prompt configuration loading...")
    
    # Test default prompts
    config = PromptConfig()
    assert config.prompts is not None, "Default prompts should load"
    assert "system_messages" in config.prompts, "System messages should be present"
    assert "quote_ranking" in config.prompts, "Quote ranking should be present"
    
    print("✓ Prompt configuration loads correctly")

def test_prompt_formatting():
    """Test that prompt templates format correctly with variables."""
    print("Testing prompt formatting...")
    
    config = get_prompt_config()
    
    # Test quote ranking prompt
    formatted = config.format_prompt("quote_ranking",
                                   perspective_title="Market Analysis",
                                   perspective_description="Analysis of market position",
                                   focus_areas="Competition, Pricing, Strategy",
                                   quotes_list="Quote 1: Sample quote text")
    
    assert "Market Analysis" in formatted, "Template variables should be substituted"
    assert "Sample quote text" in formatted, "Quotes should be included"
    
    print("✓ Prompt formatting works correctly")

def test_system_messages():
    """Test that system messages are retrieved correctly."""
    print("Testing system message retrieval...")
    
    config = get_prompt_config()
    
    system_msg = config.get_system_message("quote_ranking")
    assert system_msg is not None, "System message should be retrieved"
    assert len(system_msg) > 0, "System message should not be empty"
    
    print("✓ System messages work correctly")

def test_prompt_parameters():
    """Test that OpenAI parameters are retrieved correctly."""
    print("Testing parameter retrieval...")
    
    config = get_prompt_config()
    
    params = config.get_prompt_parameters("quote_ranking")
    assert params is not None, "Parameters should be retrieved"
    assert "model" in params, "Model parameter should be present"
    assert "temperature" in params, "Temperature parameter should be present"
    
    print("✓ Parameter retrieval works correctly")

def test_prompt_validation():
    """Test that prompt validation works correctly."""
    print("Testing prompt validation...")
    
    config = get_prompt_config()
    
    # Test valid prompt
    assert config.validate_prompt("quote_ranking"), "Valid prompt should pass validation"
    
    # Test invalid prompt
    assert not config.validate_prompt("nonexistent"), "Invalid prompt should fail validation"
    
    print("✓ Prompt validation works correctly")

def test_prompt_updates():
    """Test that prompts can be updated and saved."""
    print("Testing prompt updates...")
    
    config = PromptConfig("test_prompts.json")
    
    # Test updating a prompt
    success = config.update_prompt("quote_ranking", 
                                 template="Test template",
                                 system_message="Test system message")
    assert success, "Prompt update should succeed"
    
    # Test saving configuration
    success = config.save_config()
    assert success, "Configuration save should succeed"
    
    # Clean up test file
    if os.path.exists("test_prompts.json"):
        os.remove("test_prompts.json")
    
    print("✓ Prompt updates work correctly")

def test_all_prompt_types():
    """Test that all prompt types are available and functional."""
    print("Testing all prompt types...")
    
    config = get_prompt_config()
    prompt_types = config.get_all_prompt_types()
    
    expected_types = [
        "quote_ranking",
        "theme_identification", 
        "transcript_analysis",
        "company_summary",
        "quote_scoring"
    ]
    
    for expected_type in expected_types:
        assert expected_type in prompt_types, f"Prompt type {expected_type} should be available"
        
        # Test that each type has required components
        template = config.get_prompt_template(expected_type)
        assert template is not None, f"Template for {expected_type} should be available"
        
        system_msg = config.get_system_message(expected_type)
        assert system_msg is not None, f"System message for {expected_type} should be available"
        
        params = config.get_prompt_parameters(expected_type)
        assert params is not None, f"Parameters for {expected_type} should be available"
    
    print(f"✓ All {len(expected_types)} prompt types are functional")

def test_template_variables():
    """Test that template variables are properly handled."""
    print("Testing template variables...")
    
    config = get_prompt_config()
    
    # Test with missing variables (should show warning but not crash)
    try:
        formatted = config.format_prompt("quote_ranking", 
                                       perspective_title="Test")
        # Should work with partial variables
        assert "Test" in formatted
        print("✓ Template handles partial variables gracefully")
    except Exception as e:
        print(f"✗ Template variable handling failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("  Testing Modular Prompt System")
    print("=" * 60)
    print()
    
    tests = [
        test_prompt_config_loading,
        test_prompt_formatting,
        test_system_messages,
        test_prompt_parameters,
        test_prompt_validation,
        test_prompt_updates,
        test_all_prompt_types,
        test_template_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular prompt system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
