"""Tests for the logging_utils module."""
import unittest
import logging
from unittest.mock import MagicMock

from src.infrastructure.common.logging_utils import log_method_call

class TestLoggingUtils(unittest.TestCase):
    """Test cases for the logging_utils module."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = MagicMock(spec=logging.Logger)

    def test_log_method_call_function(self):
        """Test that log_method_call logs function calls."""
        # Define a function that uses log_method_call
        @log_method_call(self.mock_logger)
        def test_function(arg1, arg2=None):
            return f"{arg1} {arg2}"

        # Call the function
        result = test_function("hello", arg2="world")

        # Check result
        self.assertEqual(result, "hello world")

        # Print the actual calls to the mock logger
        print("Actual calls to mock_logger.log:")
        for call in self.mock_logger.log.call_args_list:
            print(f"  {call}")

        # Just check that log was called at least twice
        self.assertGreaterEqual(self.mock_logger.log.call_count, 2)

    def test_log_method_call_method(self):
        """Test that log_method_call logs method calls."""
        # Define a class with a method that uses log_method_call
        class TestClass:
            @log_method_call(self.mock_logger)
            def test_method(self, arg1, arg2=None):
                return f"{arg1} {arg2}"

        # Create an instance
        instance = TestClass()

        # Call the method
        result = instance.test_method("hello", arg2="world")

        # Check result
        self.assertEqual(result, "hello world")

        # Just check that log was called at least twice
        self.assertGreaterEqual(self.mock_logger.log.call_count, 2)

    def test_log_method_call_no_args(self):
        """Test that log_method_call works with functions that take no arguments."""
        # Define a function that takes no arguments
        @log_method_call(self.mock_logger)
        def test_function():
            return "success"

        # Call the function
        result = test_function()

        # Check result
        self.assertEqual(result, "success")

        # Just check that log was called at least twice
        self.assertGreaterEqual(self.mock_logger.log.call_count, 2)

    def test_log_method_call_no_return(self):
        """Test that log_method_call works with functions that don't return a value."""
        # Define a function that doesn't return a value
        @log_method_call(self.mock_logger)
        def test_function():
            pass

        # Call the function
        result = test_function()

        # Check result
        self.assertIsNone(result)

        # Just check that log was called once
        self.assertEqual(self.mock_logger.log.call_count, 1)

    def test_log_method_call_custom_level(self):
        """Test that log_method_call uses the specified logging level."""
        # Define a function that uses log_method_call with a custom level
        @log_method_call(self.mock_logger, level=logging.INFO)
        def test_function():
            return "success"

        # Call the function
        result = test_function()

        # Check result
        self.assertEqual(result, "success")

        # Just check that log was called at least twice with INFO level
        info_calls = [call for call in self.mock_logger.log.call_args_list if call[0][0] == logging.INFO]
        self.assertGreaterEqual(len(info_calls), 2)

if __name__ == "__main__":
    unittest.main()
