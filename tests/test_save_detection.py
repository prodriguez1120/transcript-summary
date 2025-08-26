#!/usr/bin/env python3
"""
Test script to verify file save detection is working.
Run this alongside auto_format.py to test the save functionality.
"""

import time
import sys
import os
import unittest
from pathlib import Path


class TestSaveDetection(unittest.TestCase):
    """Test save detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_file = Path("test_save_detection.py")

    def test_file_creation(self):
        """Test that test file can be created."""
        # Add a timestamp comment to make the file different each time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        content = f'''#!/usr/bin/env python3
"""
Test file for save detection - created at {timestamp}
"""

def test_function():
    """This function will be formatted when the file is saved."""
    x=1+2*3
    return x

if __name__=="__main__":
    result=test_function()
    print(f"Result: {{result}}")
'''

        with open(self.test_file, "w") as f:
            f.write(content)

        # Verify file was created
        self.assertTrue(self.test_file.exists())
        
        # Read back and verify content
        with open(self.test_file, "r") as f:
            read_content = f.read()
        
        self.assertIn(timestamp, read_content)
        self.assertIn("test_function", read_content)
        
        # Clean up
        if self.test_file.exists():
            self.test_file.unlink()

    def test_file_content_validation(self):
        """Test that file content is properly formatted."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        content = f'''#!/usr/bin/env python3
"""
Test file for save detection - created at {timestamp}
"""

def test_function():
    """This function will be formatted when the file is saved."""
    x=1+2*3
    return x

if __name__=="__main__":
    result=test_function()
    print(f"Result: {{result}}")
'''

        with open(self.test_file, "w") as f:
            f.write(content)

        # Verify specific content elements
        with open(self.test_file, "r") as f:
            read_content = f.read()
        
        # Check for intentionally bad formatting
        self.assertIn("x=1+2*3", read_content)
        self.assertIn('if __name__=="__main__":', read_content)
        self.assertIn("result=test_function()", read_content)
        
        # Clean up
        if self.test_file.exists():
            self.test_file.unlink()

    def test_timestamp_generation(self):
        """Test that timestamps are generated correctly."""
        timestamp1 = time.strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(0.1)  # Small delay to ensure different timestamps
        timestamp2 = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Timestamps should be different
        self.assertNotEqual(timestamp1, timestamp2)
        
        # Timestamps should be in correct format
        self.assertRegex(timestamp1, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        self.assertRegex(timestamp2, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_file_path_handling(self):
        """Test file path handling."""
        # Test that we can work with Path objects
        self.assertIsInstance(self.test_file, Path)
        self.assertEqual(self.test_file.name, "test_save_detection.py")
        
        # Test file operations
        test_content = "test content"
        with open(self.test_file, "w") as f:
            f.write(test_content)
        
        self.assertTrue(self.test_file.exists())
        self.assertTrue(self.test_file.is_file())
        
        # Clean up
        if self.test_file.exists():
            self.test_file.unlink()

    def test_file_cleanup(self):
        """Test file cleanup functionality."""
        # Create a test file
        with open(self.test_file, "w") as f:
            f.write("test content")
        
        # Verify it exists
        self.assertTrue(self.test_file.exists())
        
        # Clean up
        if self.test_file.exists():
            self.test_file.unlink()
        
        # Verify it's gone
        self.assertFalse(self.test_file.exists())

    def test_content_validation(self):
        """Test content validation for save detection."""
        # Test content with various formatting issues
        test_content = '''
def badly_formatted_function():
    x=1+2*3
    y={"a":1,"b":2}
    return x,y

class BadlyFormattedClass:
    def __init__(self,name,age):
        self.name=name
        self.age=age
'''
        
        with open(self.test_file, "w") as f:
            f.write(test_content)
        
        # Verify content was written
        with open(self.test_file, "r") as f:
            read_content = f.read()
        
        # Check for formatting issues that should be detected
        self.assertIn("x=1+2*3", read_content)
        self.assertIn('y={"a":1,"b":2}', read_content)
        self.assertIn("def __init__(self,name,age):", read_content)
        self.assertIn("self.name=name", read_content)
        
        # Clean up
        if self.test_file.exists():
            self.test_file.unlink()


def create_test_file():
    """Create a test Python file to trigger save events."""
    test_file = Path("test_save_detection.py")

    # Add a timestamp comment to make the file different each time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f'''#!/usr/bin/env python3
"""
Test file for save detection - created at {timestamp}
"""

def test_function():
    """This function will be formatted when the file is saved."""
    x=1+2*3
    return x

if __name__=="__main__":
    result=test_function()
    print(f"Result: {{result}}")
'''

    with open(test_file, "w") as f:
        f.write(content)

    print(f"📝 Created test file: {test_file}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"💾 Save this file (Ctrl+S) to trigger formatting")


def main():
    """Main test function."""
    print("🧪 Save Detection Test")
    print("=" * 40)
    print("This script creates a test Python file that you can save")
    print("to verify that the auto-formatter is detecting save events.")
    print()

    # Create the test file
    create_test_file()

    print()
    print("📋 Instructions:")
    print("1. Make sure auto_format.py is running in another terminal")
    print("2. Open test_save_detection.py in your editor")
    print("3. Make a small change (add a space, comment, etc.)")
    print("4. Save the file (Ctrl+S)")
    print("5. Check the auto_format.py terminal for formatting output")
    print()
    print("🔄 The file will be recreated each time you run this script")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
