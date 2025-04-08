#!/usr/bin/env python
"""
Code Quality Dashboard Launcher

This script checks for required dependencies and launches the Code Quality Dashboard.
"""

import os
import sys
import subprocess
import importlib.util

def check_dependency(package):
    """Check if a package is installed."""
    return importlib.util.find_spec(package) is not None

def install_dependency(package):
    """Install a package using pip."""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Main function to check dependencies and launch the dashboard."""
    print("Checking dependencies...")
    
    # Required packages
    required_packages = [
        "PyQt5",
        "PyQt5-Qt5",
        "PyQt5-sip",
        "PyQtChart",
        "matplotlib"
    ]
    
    # Check and install missing packages
    missing_packages = []
    for package in required_packages:
        package_name = package.split('-')[0].lower()
        if not check_dependency(package_name):
            missing_packages.append(package)
    
    if missing_packages:
        print("The following dependencies are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        
        install = input("Do you want to install them now? (y/n): ")
        if install.lower() == 'y':
            for package in missing_packages:
                install_dependency(package)
        else:
            print("Cannot launch dashboard without required dependencies.")
            return
    
    # Launch the dashboard
    print("Launching Code Quality Dashboard...")
    if os.path.exists("code_quality_dashboard.py"):
        subprocess.call([sys.executable, "code_quality_dashboard.py"])
    else:
        print("Error: code_quality_dashboard.py not found.")

if __name__ == "__main__":
    main()
