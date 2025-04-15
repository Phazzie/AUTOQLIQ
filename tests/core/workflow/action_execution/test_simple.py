"""Simple tests for action execution interfaces.

This module tests the implementation of action execution interfaces.
"""

import unittest

from src.core.workflow.action_execution.interfaces import (
    IActionExecutor,
    IActionTypeDetector,
    IActionFailureHandler,
    IActionErrorHandler,
    IActionDisplayFormatter,
    IActionExecutionManager
)
from src.core.workflow.action_execution.action_type_detector import ActionTypeDetector
from src.core.workflow.action_execution.action_display_formatter import ActionDisplayFormatter
from src.core.workflow.action_execution.action_failure_handler import ActionFailureHandler
from src.core.workflow.action_execution.action_error_handler import ActionErrorHandler
from src.core.workflow.action_execution.action_execution_manager import ActionExecutionManager


class TestSimpleInterfaces(unittest.TestCase):
    """Simple tests for action execution interfaces."""

    def test_action_type_detector_implements_interface(self):
        """Test that ActionTypeDetector implements IActionTypeDetector."""
        action_type_detector = ActionTypeDetector()
        self.assertIsInstance(action_type_detector, IActionTypeDetector)

    def test_action_failure_handler_implements_interface(self):
        """Test that ActionFailureHandler implements IActionFailureHandler."""
        action_failure_handler = ActionFailureHandler()
        self.assertIsInstance(action_failure_handler, IActionFailureHandler)

    def test_action_error_handler_implements_interface(self):
        """Test that ActionErrorHandler implements IActionErrorHandler."""
        action_error_handler = ActionErrorHandler()
        self.assertIsInstance(action_error_handler, IActionErrorHandler)

    def test_action_display_formatter_implements_interface(self):
        """Test that ActionDisplayFormatter implements IActionDisplayFormatter."""
        action_display_formatter = ActionDisplayFormatter()
        self.assertIsInstance(action_display_formatter, IActionDisplayFormatter)

    def test_action_execution_manager_implements_interface(self):
        """Test that ActionExecutionManager implements IActionExecutionManager."""
        action_execution_manager = ActionExecutionManager()
        self.assertIsInstance(action_execution_manager, IActionExecutionManager)


if __name__ == "__main__":
    unittest.main()
