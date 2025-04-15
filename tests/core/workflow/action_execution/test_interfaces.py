"""Tests for action execution interfaces.

This module tests the implementation of action execution interfaces.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, ValidationError
from src.core.workflow.action_execution.interfaces import (
    IActionExecutor,
    IActionTypeDetector,
    IActionFailureHandler,
    IActionErrorHandler,
    IActionDisplayFormatter,
    IActionExecutionManager
)
from src.core.workflow.action_execution.action_executor import ActionExecutor
from src.core.workflow.action_execution.action_type_detector import ActionTypeDetector
from src.core.workflow.action_execution.action_failure_handler import ActionFailureHandler
from src.core.workflow.action_execution.action_error_handler import ActionErrorHandler
from src.core.workflow.action_execution.action_display_formatter import ActionDisplayFormatter
from src.core.workflow.action_execution.action_execution_manager import ActionExecutionManager


class TestActionExecutionInterfaces(unittest.TestCase):
    """Test the implementation of action execution interfaces."""

    def test_action_executor_implements_interface(self):
        """Test that ActionExecutor implements IActionExecutor."""
        driver_mock = MagicMock(spec=IWebDriver)
        credential_repo_mock = MagicMock(spec=ICredentialRepository)
        
        action_executor = ActionExecutor(driver_mock, credential_repo_mock)
        self.assertIsInstance(action_executor, IActionExecutor)

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

    def test_action_executor_execute_action(self):
        """Test that ActionExecutor.execute_action works correctly."""
        # Create mocks
        driver_mock = MagicMock(spec=IWebDriver)
        action_mock = MagicMock(spec=IAction)
        action_mock.name = "Test Action"
        action_mock.action_type = "test"
        action_mock.execute.return_value = ActionResult.success("Test success")
        
        # Create context
        context = {"test_key": "test_value"}
        
        # Create executor
        executor = ActionExecutor(driver_mock)
        
        # Execute action
        result = executor.execute_action(action_mock, context)
        
        # Verify results
        self.assertTrue(result.is_success())
        self.assertEqual(result.message, "Test success")
        action_mock.validate.assert_called_once()
        action_mock.execute.assert_called_once_with(driver_mock, None, context)

    def test_action_type_detector_detect_action_type(self):
        """Test that ActionTypeDetector.detect_action_type works correctly."""
        # Create mocks
        action_mock = MagicMock(spec=IAction)
        
        # Create detector
        detector = ActionTypeDetector()
        
        # Test with regular action
        result = detector.detect_action_type(action_mock)
        self.assertIsNone(result)

    def test_action_failure_handler_handle_action_failure(self):
        """Test that ActionFailureHandler.handle_action_failure works correctly."""
        # Create mocks
        action_mock = MagicMock(spec=IAction)
        action_result = ActionResult.failure("Test failure")
        
        # Create context
        context = {"state": {}}
        
        # Create handler
        handler = ActionFailureHandler()
        
        # Test with CONTINUE_ON_ERROR
        handler.handle_action_failure(
            action_result, action_mock, "Test Action", "CONTINUE_ON_ERROR", context
        )
        self.assertTrue(context["state"]["had_action_failures"])
        
        # Test with STOP_ON_ERROR
        with self.assertRaises(ActionError):
            handler.handle_action_failure(
                action_result, action_mock, "Test Action", "STOP_ON_ERROR", context
            )

    def test_action_error_handler_handle_action_error(self):
        """Test that ActionErrorHandler.handle_action_error works correctly."""
        # Create mocks
        action_mock = MagicMock(spec=IAction)
        error = ValueError("Test error")
        
        # Create context
        context = {"state": {}}
        
        # Create handler
        handler = ActionErrorHandler()
        
        # Test with CONTINUE_ON_ERROR
        result = handler.handle_action_error(
            error, action_mock, "Test Action", "CONTINUE_ON_ERROR", context
        )
        self.assertFalse(result.is_success())
        self.assertTrue(context["state"]["had_action_failures"])
        
        # Test with STOP_ON_ERROR
        with self.assertRaises(ActionError):
            handler.handle_action_error(
                error, action_mock, "Test Action", "STOP_ON_ERROR", context
            )

    def test_action_display_formatter_format_action_display_name(self):
        """Test that ActionDisplayFormatter.format_action_display_name works correctly."""
        # Create mocks
        action_mock = MagicMock(spec=IAction)
        action_mock.name = "Test Action"
        action_mock.action_type = "test"
        
        # Create formatter
        formatter = ActionDisplayFormatter()
        
        # Test formatting
        result = formatter.format_action_display_name(action_mock, "Prefix: ", 1)
        self.assertEqual(result, "Prefix: Step 1: Test Action (test)")

    @patch('src.core.workflow.action_execution.action_execution_manager.ActionTypeDetector')
    @patch('src.core.workflow.action_execution.action_execution_manager.ActionDisplayFormatter')
    @patch('src.core.workflow.action_execution.action_execution_manager.ActionFailureHandler')
    @patch('src.core.workflow.action_execution.action_execution_manager.ActionErrorHandler')
    def test_action_execution_manager_execute_actions(
        self, 
        mock_error_handler, 
        mock_failure_handler,
        mock_display_formatter,
        mock_type_detector
    ):
        """Test that ActionExecutionManager.execute_actions works correctly."""
        # Create mocks
        action_mock = MagicMock(spec=IAction)
        action_executor_mock = MagicMock(spec=IActionExecutor)
        action_executor_mock.execute_action.return_value = ActionResult.success("Test success")
        
        # Create context
        context = {"test_key": "test_value"}
        
        # Create control flow handlers
        control_flow_handlers = {}
        
        # Create manager with mocked dependencies
        manager = ActionExecutionManager()
        
        # Configure mocks
        manager.action_type_detector.detect_action_type.return_value = None
        manager.action_display_formatter.format_action_display_name.return_value = "Test Action"
        
        # Execute actions
        results = manager.execute_actions(
            [action_mock],
            context,
            "Test Workflow",
            "Prefix: ",
            action_executor_mock,
            control_flow_handlers,
            "CONTINUE_ON_ERROR"
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].is_success())
        action_executor_mock.execute_action.assert_called_once_with(action_mock, context)


if __name__ == "__main__":
    unittest.main()
