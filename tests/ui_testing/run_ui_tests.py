"""Run all UI tests for AutoQliq."""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the test modules
from tests.ui_testing.test_action_selection_dialog import TestActionSelectionDialog
from tests.ui_testing.test_action_editor_dialog import TestActionEditorDialog
from tests.ui_testing.test_settings_view import TestSettingsView


def run_tests():
    """Run all UI tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestActionSelectionDialog))
    test_suite.addTest(unittest.makeSuite(TestActionEditorDialog))
    test_suite.addTest(unittest.makeSuite(TestSettingsView))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result


if __name__ == "__main__":
    result = run_tests()
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
