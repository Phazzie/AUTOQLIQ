#!/usr/bin/env python
"""
Test Script for Code Quality Analyzers

This script tests the code quality analyzers on a sample file to verify they work correctly.

Usage:
    python test_analyzers.py
"""

import os
import tempfile

def create_test_file():
    """Create a temporary test file with code quality issues for all SOLID principles."""
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write("""
# SRP Violation: Class with multiple responsibilities
class TooManyResponsibilities:
    def __init__(self):
        self.data = []

    def load_data(self):
        # This is a data access responsibility
        self.data = [1, 2, 3]

    def process_data(self):
        # This is a calculation responsibility
        return sum(self.data)

    def display_data(self):
        # This is a UI responsibility
        print(self.data)

# OCP Violation: Type checking with conditionals
class ShapeCalculator:
    def calculate_area(self, shape):
        # Violates OCP: Need to modify this method to add new shapes
        if shape.type == 'circle':
            return 3.14 * shape.radius * shape.radius
        elif shape.type == 'square':
            return shape.side * shape.side
        elif shape.type == 'rectangle':
            return shape.width * shape.height
        else:
            raise ValueError(f"Unknown shape type: {shape.type}")

# LSP Violation: Breaking the contract of the base class
class Bird:
    def fly(self):
        return "Flying high"

class Penguin(Bird):
    def fly(self):
        # Violates LSP: Penguins can't fly, breaking the contract
        raise NotImplementedError("Penguins can't fly!")

# ISP Violation: Interface with too many methods
class Worker:
    def work(self):
        pass

    def eat(self):
        pass

    def sleep(self):
        pass

class Robot(Worker):
    def work(self):
        return "Working..."

    def eat(self):
        # Robots don't eat, but forced to implement this method
        raise NotImplementedError("Robots don't eat!")

    def sleep(self):
        # Robots don't sleep, but forced to implement this method
        raise NotImplementedError("Robots don't sleep!")

# DIP Violation: High-level module depends on low-level module
class UserService:
    def __init__(self):
        # Violates DIP: Direct instantiation of concrete class
        self.database = MySQLDatabase()

    def save_user(self, user):
        # Depends directly on MySQLDatabase implementation
        self.database.save(user)

class MySQLDatabase:
    def save(self, data):
        print(f"Saving {data} to MySQL")

# KISS Violation: Complex method with deep nesting
def complex_method(data):
    # This is a complex method with deep nesting
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    for subitem in value:
                        if isinstance(subitem, str):
                            result.append(subitem.upper())
                        else:
                            result.append(str(subitem))
                else:
                    result.append(str(value))
        else:
            result.append(str(item))
    return result

# DRY Violation: Duplicate code
def validate_email(email):
    return '@' in email and '.' in email

def validate_user(user):
    if not user.get('email'):
        return False
    return '@' in user.get('email') and '.' in user.get('email')
""")
    return f.name

def test_analyzers():
    """Test all code quality analyzers."""
    # Create test file
    test_file = create_test_file()
    print(f"Created test file: {test_file}")

    try:
        # Note: Individual standalone analyzers have been archived
        # They can still be found in the 'archived' directory if needed

        # Test the integrated analyzer if available
        if os.path.exists("code_quality_analyzer"):
            print("\n=== Testing Integrated Analyzer ===")
            # Test with all analyzers
            print("\n--- Testing with all analyzers ---")
            os.system(f"python -m code_quality_analyzer {test_file} --analyzers all")

            # Test with SOLID analyzers only
            print("\n--- Testing with SOLID analyzers only ---")
            os.system(f"python -m code_quality_analyzer {test_file} --analyzers solid")

            # Test with individual analyzers
            print("\n--- Testing with individual analyzers ---")
            os.system(f"python -m code_quality_analyzer {test_file} --analyzers srp ocp lsp isp dip")
    finally:
        # Clean up
        os.unlink(test_file)
        print(f"\nRemoved test file: {test_file}")

if __name__ == "__main__":
    test_analyzers()
