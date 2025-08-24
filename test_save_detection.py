#!/usr/bin/env python3
"""
Test script to verify file save detection is working.
Run this alongside auto_format.py to test the save functionality.
"""

import time
from pathlib import Path


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
    main()
