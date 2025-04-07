#!/usr/bin/env python
"""
Dependency Installer

This script installs the required dependencies for the code quality analyzer scripts.

Usage:
    python install_dependencies.py
"""

import subprocess
import sys
import os

# List of required packages
REQUIRED_PACKAGES = [
    "networkx",
    "matplotlib"  # Often used with networkx for visualization
]

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies for code quality analyzer scripts...")
    
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {str(e)}")
    
    print("\nInstallation completed.")
    
    # Install the code_quality_analyzer package in development mode
    if os.path.exists("code_quality_analyzer/setup.py"):
        print("\nInstalling code_quality_analyzer package in development mode...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "code_quality_analyzer"])
            print("✅ Successfully installed code_quality_analyzer package")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install code_quality_analyzer package: {str(e)}")

if __name__ == "__main__":
    install_dependencies()
