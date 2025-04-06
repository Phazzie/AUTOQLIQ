"""Tests for the error_handling module."""
import unittest
from unittest.mock import MagicMock

from src.core.exceptions import WorkflowError
import src.infrastructure.common.error_handling
from src.infrastructure.common.error_handling import handle_exceptions

class TestErrorHandling(unittest.TestCase):
    """Test cases for the error_handling module."""

    def test_handle_exceptions_no_error(self):
        """Test that handle_exceptions doesn't affect a function that doesn't raise an error."""
        # Define a function that doesn't raise an error
        @handle_exceptions(WorkflowError, "Test error")
        def test_function():
            return "success"

        # Call the function
        result = test_function()

        # Check result
        self.assertEqual(result, "success")

    def test_handle_exceptions_domain_error(self):
        """Test that handle_exceptions re-raises domain-specific errors."""
        # Define a function that raises a domain-specific error
        @handle_exceptions(WorkflowError, "Test error")
        def test_function():
            raise WorkflowError("Domain error")

        # Call the function
        with self.assertRaises(WorkflowError) as cm:
            test_function()

        # Check error message
        self.assertEqual(str(cm.exception), "Domain error")

    def test_handle_exceptions_other_error(self):
        """Test that handle_exceptions converts other errors to domain-specific errors."""
        # Define a function that raises a non-domain-specific error
        @handle_exceptions(WorkflowError, "Test error")
        def test_function():
            raise ValueError("Other error")

        # Call the function
        with self.assertRaises(WorkflowError) as cm:
            test_function()

        # Check error message
        self.assertEqual(str(cm.exception), "Test error: Other error")

        # Check cause
        self.assertIsInstance(cm.exception.cause, ValueError)
        self.assertEqual(str(cm.exception.cause), "Other error")

    def test_handle_exceptions_logging(self):
        """Test that handle_exceptions logs errors."""
        # Create a mock logger
        mock_logger = MagicMock()

        # Save the original logger
        original_logger = src.infrastructure.common.error_handling.logger

        try:
            # Replace the logger with our mock
            src.infrastructure.common.error_handling.logger = mock_logger

            # Define a function that raises an error
            @handle_exceptions(WorkflowError, "Test error")
            def test_function():
                raise ValueError("Other error")

            # Call the function
            with self.assertRaises(WorkflowError):
                test_function()

            # Check that the error was logged
            mock_logger.log.assert_called_once()
        finally:
            # Restore the original logger
            src.infrastructure.common.error_handling.logger = original_logger

    def test_handle_exceptions_with_args(self):
        """Test that handle_exceptions works with functions that take arguments."""
        # Define a function that takes arguments
        @handle_exceptions(WorkflowError, "Test error")
        def test_function(arg1, arg2=None):
            if arg2 is None:
                raise ValueError("arg2 is None")
            return f"{arg1} {arg2}"

        # Call the function with arguments
        result = test_function("hello", "world")

        # Check result
        self.assertEqual(result, "hello world")

        # Call the function with an error
        with self.assertRaises(WorkflowError):
            test_function("hello")

    def test_handle_exceptions_with_method(self):
        """Test that handle_exceptions works with methods."""
        # Define a class with a method that uses handle_exceptions
        class TestClass:
            @handle_exceptions(WorkflowError, "Test error")
            def test_method(self, arg):
                if arg is None:
                    raise ValueError("arg is None")
                return f"success: {arg}"

        # Create an instance
        instance = TestClass()

        # Call the method
        result = instance.test_method("test")

        # Check result
        self.assertEqual(result, "success: test")

        # Call the method with an error
        with self.assertRaises(WorkflowError):
            instance.test_method(None)

if __name__ == "__main__":
    unittest.main()
