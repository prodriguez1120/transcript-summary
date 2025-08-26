#!/usr/bin/env python3
"""
Test file for formatting tools.
This file has intentionally poor formatting to test Black, isort, and flake8.
"""

import os
import sys
import unittest
from pathlib import Path


class TestFormatting(unittest.TestCase):
    """Test formatting functionality."""

    def test_badly_formatted_function(self):
        """Test that badly formatted function works correctly."""
        x = 1 + 2 * 3
        y = {"a": 1, "b": 2}
        z = [1, 2, 3, 4, 5]
        result = x, y, z
        
        self.assertEqual(x, 7)
        self.assertEqual(y, {"a": 1, "b": 2})
        self.assertEqual(z, [1, 2, 3, 4, 5])
        self.assertIsInstance(result, tuple)

    def test_badly_formatted_class(self):
        """Test that badly formatted class works correctly."""
        obj = BadlyFormattedClass("Test", 25)
        result = obj.get_info()
        
        self.assertEqual(obj.name, "Test")
        self.assertEqual(obj.age, 25)
        self.assertEqual(result, "Name: Test, Age: 25")

    def test_badly_formatted_line(self):
        """Test that badly formatted line works correctly."""
        badly_formatted_line = 123 + 456 * 789
        expected = 123 + (456 * 789)
        
        self.assertEqual(badly_formatted_line, expected)

    def test_import_structure(self):
        """Test that imports are properly structured."""
        # Test that required modules are available
        self.assertTrue(hasattr(os, 'path'))
        self.assertTrue(hasattr(sys, 'path'))
        self.assertTrue(hasattr(Path, '__init__'))

    def test_code_formatting_consistency(self):
        """Test that code formatting is consistent."""
        # Test various formatting scenarios
        test_dict = {"key1": "value1", "key2": "value2"}
        test_list = [1, 2, 3, 4, 5]
        test_string = "This is a test string"
        
        self.assertIsInstance(test_dict, dict)
        self.assertIsInstance(test_list, list)
        self.assertIsInstance(test_string, str)
        
        # Test mathematical operations formatting
        result1 = 10 + 20 * 30
        result2 = (10 + 20) * 30
        
        self.assertEqual(result1, 610)
        self.assertEqual(result2, 900)

    def test_function_definition_formatting(self):
        """Test function definition formatting."""
        def test_function():
            """This function tests formatting."""
            return "formatted"
        
        result = test_function()
        self.assertEqual(result, "formatted")

    def test_class_definition_formatting(self):
        """Test class definition formatting."""
        class TestClass:
            """Test class for formatting."""
            
            def __init__(self, value):
                self.value = value
            
            def get_value(self):
                return self.value
        
        obj = TestClass("test")
        self.assertEqual(obj.get_value(), "test")


class BadlyFormattedClass:
    """Test class with intentionally bad formatting."""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_info(self):
        return f"Name: {self.name}, Age: {self.age}"


def main():
    """Main test function."""
    print("🧪 Testing Code Formatting")
    print("=" * 40)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
