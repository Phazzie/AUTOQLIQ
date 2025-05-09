"""Run all tests for the Code Quality Analyzer."""

import unittest
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Run all tests."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)

if __name__ == '__main__':
    main()
