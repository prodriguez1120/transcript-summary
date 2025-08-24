#!/usr/bin/env python3
"""
Test runner for FlexXray Transcript Summarizer

This script runs all unit tests from the tests/ directory.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests from the tests directory."""
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    run_tests_script = os.path.join(tests_dir, "run_tests.py")

    if not os.path.exists(run_tests_script):
        print(f"Error: Test runner not found at {run_tests_script}")
        return 1

    # Run the tests using the script in the tests directory
    result = subprocess.run(
        [sys.executable, run_tests_script] + sys.argv[1:], cwd=tests_dir
    )
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
