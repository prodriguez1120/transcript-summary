#!/usr/bin/env python3
"""
Test runner for FlexXray Transcript Summarizer

This script runs all comprehensive unit tests including:
- Core Logic: quote_analysis_tool.py, fuzzy_matching.py, vector_database.py
- Validation & Error Handling: exceptions.py, validation.py, json_utils.py
- Perspective Analysis: perspective_analysis.py
- Quote Processing: quote extraction, filtering, and export
- System Integration: streamlined system and prompt management
"""

import unittest
import sys
import os
import importlib

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


def clear_module_cache():
    """Clear module cache to ensure test isolation."""
    # Clear modules that might have state
    modules_to_clear = [
        "fuzzy_matching",
        "quote_analysis_tool",
        "vector_database",
        "exceptions",
        "validation",
        "json_utils",
        "perspective_analysis",
    ]
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]


def show_help():
    """Show help information."""
    print("Usage: python run_tests.py [test_file]")
    print("")
    print("Options:")
    print("  test_file    Run tests from specific test file (without .py extension)")
    print("  --help       Show this help message")
    print("")
    print("Available Test Categories:")
    print("  - Core Logic: test_complex_logic, test_fuzzy_logic, test_fuzzy_matching")
    print("  - Vector Database: test_vector_db_logic, test_vector_db_management")
    print(
        "  - Quote Processing: test_quote_export, test_quote_filtering, test_speaker_roles"
    )
    print(
        "  - Validation & Error Handling: test_error_handling, test_perspective_analysis"
    )
    print("  - System Integration: test_streamlined_system, test_prompt_system")
    print("")
    print("Examples:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py test_error_handling   # Run validation tests")
    print(
        "  python run_tests.py test_perspective_analysis   # Run perspective analysis tests"
    )
    print("  python run_tests.py test_fuzzy_logic   # Run specific test file")
    print("  python run_tests.py --help             # Show this help")


def run_all_tests():
    """Run all test suites."""
    # Clear module cache for clean test isolation
    clear_module_cache()

    # Discover and run all tests in the current directory (tests/)
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with verbose output and buffering
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


def run_specific_test_suite(test_file):
    """Run tests from a specific test file."""
    # Clear module cache for clean test isolation
    clear_module_cache()

    # If test_file doesn't have .py extension, add it
    if not test_file.endswith(".py"):
        test_file = test_file + ".py"

    # Check if test_file exists in tests directory
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_file)
    if not os.path.exists(test_path):
        print(f"Test file not found: {test_file}")
        return 1

    # Use test discovery for specific file instead of loadTestsFromName
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    test_suite = loader.discover(start_dir, pattern=test_file)

    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--help", "-h", "help"]:
            show_help()
            exit_code = 0
        else:
            # Run specific test file
            exit_code = run_specific_test_suite(arg)
    else:
        # Run all tests
        exit_code = run_all_tests()

    sys.exit(exit_code)
