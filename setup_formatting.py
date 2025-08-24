#!/usr/bin/env python3
"""
Setup script for code formatting tools.
Installs required packages and creates configuration files.
"""

import subprocess
import sys
from pathlib import Path

def install_packages():
    """Install required formatting packages."""
    packages = ['black', 'isort', 'flake8', 'watchdog']
    
    print("📦 Installing formatting tools...")
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            return False
    return True

def check_installation():
    """Verify that all tools are properly installed."""
    tools = ['black', 'isort', 'flake8']
    
    print("\n🔍 Verifying installation...")
    all_good = True
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], capture_output=True, text=True, check=True)
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ {tool}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"✗ {tool} not found")
            all_good = False
    
    return all_good

def main():
    print("🚀 Setting up code formatting tools for FlexXray Transcript Summarizer")
    print("=" * 60)
    
    # Install packages
    if not install_packages():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Verify installation
    if not check_installation():
        print("\n❌ Some tools are not properly installed.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the auto-formatter: python auto_format.py")
    print("2. Or format manually: black . && isort . && flake8 .")
    print("3. The formatter will watch for file changes automatically")

if __name__ == "__main__":
    main()

