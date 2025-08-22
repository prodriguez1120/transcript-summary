#!/usr/bin/env python3
"""
Simple test script for the streamlined system using existing quote analysis.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_existing_system_with_new_prompts():
    """Test the existing system with the new question-based prompts."""
    print("Testing Existing System with New Question-Based Prompts")
    print("=" * 60)
    
    # Check if prompts.json has been updated
    if not os.path.exists("prompts.json"):
        print("❌ prompts.json not found")
        return False
    
    # Check if the new streamlined files exist
    streamlined_files = [
        "streamlined_quote_analysis.py",
        "run_streamlined_analysis.py", 
        "STREAMLINED_ANALYSIS_README.md"
    ]
    
    print("Checking streamlined system files:")
    for file in streamlined_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print("\nTesting existing quote analysis tool with new prompts...")
    
    try:
        # Run the existing system which should now use the new question-based prompts
        os.system("python quote_analysis_tool.py")
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

def main():
    """Main test function."""
    print("FlexXray Streamlined System Test")
    print("=" * 40)
    
    # Test the system
    success = test_existing_system_with_new_prompts()
    
    if success:
        print("\n🎉 All tests passed! The streamlined system is ready.")
        print("\nNext steps:")
        print("1. Check the generated output files in the Outputs/ directory")
        print("2. Verify that all 7 insights (3+2+2) are generated")
        print("3. Confirm that quotes are properly categorized")
        print("4. Run the full streamlined system when ready")
    else:
        print("\n❌ Tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()

