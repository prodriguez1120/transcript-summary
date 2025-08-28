#!/usr/bin/env python3
"""
Test runner for FlexXray Transcript Summarizer

This script runs all comprehensive unit tests including:
- Core Logic: quote_analysis_tool.py, fuzzy_matching.py, vector_database.py
- Validation & Error Handling: exceptions.py, validation.py, json_utils.py
- Perspective Analysis: perspective_analysis.py
- Quote Processing: quote extraction, filtering, and export
- System Integration: streamlined system and prompt management
- RAG Functionality: vector database semantic search and retrieval
- Modular Analysis: refactored perspective analysis components
- Ranking & Coverage: quote ranking and selection stage tracking
- Batch Processing: batch processing capabilities for quote ranking
- Quote Enrichment: quote enrichment and export functionality
- Formatting & Tools: code formatting and save detection tools
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
    print("🚀 RECOMMENDED Test Categories (Streamlined System):")
    print("  - Streamlined System: test_streamlined_system (RECOMMENDED)")
    print("  - Robust Metadata Filtering: test_robust_metadata_filtering")
    print("  - Complex Logic (Migrated): test_complex_logic (MIGRATED TO STREAMLINED)")
    print("  - Speaker Roles (Migrated): test_speaker_roles (MIGRATED TO STREAMLINED)")
    print("  - Quote Export: test_quote_export, test_quote_filtering")
    print("  - RAG Functionality: test_rag_functionality, test_main_rag_integration")
    print("  - Batch Processing (Migrated): test_batch_processing (MIGRATED TO STREAMLINED)")
    print("  - Quote Enrichment (Migrated): test_quote_enrichment (MIGRATED TO STREAMLINED)")
    print("  - Real Quotes Enrichment (Migrated): test_real_quotes_enrichment (MIGRATED TO STREAMLINED)")
    print("  - Main RAG Integration (Migrated): test_main_rag_integration (MIGRATED TO STREAMLINED)")
    print("  - Modular Perspective Analysis (Migrated): test_modular_perspective_analysis (MIGRATED TO STREAMLINED)")
    print("  - Ranking & Coverage (Migrated): test_ranking_coverage (MIGRATED TO STREAMLINED)")
    print("  - Diverse Quotes (Migrated): test_diverse_quotes (MIGRATED TO STREAMLINED)")
    print("")
    print("⚠️  DEPRECATED Test Categories (Comprehensive System):")
    print("  - Fuzzy Logic: test_fuzzy_logic, test_fuzzy_matching")
    print("  - Vector Database: test_vector_db_logic, test_vector_db_management")
    print("  - Quote Processing: test_quote_export, test_quote_filtering")
    print("  - Validation & Error Handling: test_error_handling, test_perspective_analysis")
    print("  - Refactored Modules: test_refactored_modules")
    print("  - Formatting & Tools: test_formatting, test_save_detection")
    print("")
    print("Examples:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py test_streamlined_system   # Run RECOMMENDED tests")
    print("  python run_tests.py test_robust_metadata_filtering   # Run metadata filtering tests")
    print("  python run_tests.py test_error_handling   # Run validation tests (DEPRECATED)")
    print("  python run_tests.py test_perspective_analysis   # Run perspective analysis tests (DEPRECATED)")
    print("  python run_tests.py test_fuzzy_logic   # Run specific test file (DEPRECATED)")
    print("  python run_tests.py test_rag_functionality   # Run RAG functionality tests (MIGRATED)")
    print("  python run_tests.py test_quote_enrichment   # Run quote enrichment tests (MIGRATED)")
    print("  python run_tests.py test_batch_processing   # Run batch processing tests (MIGRATED)")
    print("  python run_tests.py --help             # Show this help")
    print("")
    print("⚠️  NOTE: Tests marked as DEPRECATED use the old comprehensive system.")
    print("   Use test_streamlined_system for production testing.")


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
