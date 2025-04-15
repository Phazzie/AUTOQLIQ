"""Tests for the error_handler module."""
import unittest
from unittest.mock import MagicMock, patch
import logging

from src.core.exceptions import WebDriverError
# Import directly from the module to avoid importing selenium
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from src.infrastructure.webdrivers.error_handler import map_webdriver_exception, handle_driver_exceptions, StandardExceptionMapper, StandardExceptionHandler, IExceptionMapper, IExceptionHandler

# Mock exceptions for testing
class MockWebDriverException(Exception):
    """Mock WebDriver exception for testing."""
    pass

class MockTimeoutException(Exception):
    """Mock timeout exception for testing."""
    pass

class MockNoSuchElementException(Exception):
    """Mock no such element exception for testing."""
    pass


class TestMapWebDriverException(unittest.TestCase):
    """Test cases for the map_webdriver_exception function."""

    def test_map_webdriver_exception_basic(self):
        """Test that map_webdriver_exception creates a WebDriverError with the correct message."""
        # Create a mock exception
        exception = MockWebDriverException("Test error")

        # Map the exception
        result = map_webdriver_exception(exception, "Test context")

        # Check result
        self.assertIsInstance(result, WebDriverError)
        self.assertEqual(str(result), "Test context: [MockWebDriverException] Test error")
        self.assertEqual(result.cause, exception)
        self.assertIsNone(result.driver_type)

    def test_map_webdriver_exception_with_driver_type(self):
        """Test that map_webdriver_exception includes driver type in the WebDriverError."""
        # Create a mock exception
        exception = MockWebDriverException("Test error")

        # Map the exception with driver type
        result = map_webdriver_exception(exception, "Test context", "selenium")

        # Check result
        self.assertIsInstance(result, WebDriverError)
        self.assertEqual(result.driver_type, "selenium")

    @patch("src.infrastructure.webdrivers.error_handler.logger")
    def test_map_webdriver_exception_logging_warning(self, mock_logger):
        """Test that map_webdriver_exception logs warnings for certain exceptions."""
        # Create a mock exception that should trigger a warning
        exception = MockNoSuchElementException("Element not found")

        # Map the exception
        map_webdriver_exception(exception, "Test context")

        # Check that a warning was logged
        mock_logger.log.assert_called_once_with(
            logging.WARNING,
            "Test context: [MockNoSuchElementException] Element not found",
            exc_info=False
        )

    @patch("src.infrastructure.webdrivers.error_handler.logger")
    def test_map_webdriver_exception_logging_error(self, mock_logger):
        """Test that map_webdriver_exception logs errors for other exceptions."""
        # Create a mock exception that should trigger an error
        exception = MockWebDriverException("Test error")

        # Map the exception
        map_webdriver_exception(exception, "Test context")

        # Check that an error was logged
        mock_logger.log.assert_called_once_with(
            logging.ERROR,
            "Test context: [MockWebDriverException] Test error",
            exc_info=False
        )


class TestHandleDriverExceptions(unittest.TestCase):
    """Test cases for the handle_driver_exceptions decorator."""

    def test_handle_driver_exceptions_no_error(self):
        """Test that handle_driver_exceptions doesn't affect a function that doesn't raise an error."""
        # Define a function that doesn't raise an error
        @handle_driver_exceptions("Test operation")
        def test_function():
            return "success"

        # Call the function
        result = test_function()

        # Check result
        self.assertEqual(result, "success")

    def test_handle_driver_exceptions_with_error(self):
        """Test that handle_driver_exceptions catches and maps exceptions."""
        # Define a function that raises an error
        @handle_driver_exceptions("Test operation")
        def test_function():
            raise MockWebDriverException("Test error")

        # Call the function
        with self.assertRaises(WebDriverError) as context:
            test_function()

        # Check the exception
        self.assertIn("Test operation", str(context.exception))
        self.assertIn("MockWebDriverException", str(context.exception))
        self.assertIn("Test error", str(context.exception))

    def test_handle_driver_exceptions_with_format(self):
        """Test that handle_driver_exceptions formats the context message."""
        # Define a function that raises an error
        @handle_driver_exceptions("Failed to find element with selector: {selector}")
        def find_element(selector):
            raise MockNoSuchElementException("Element not found")

        # Call the function
        with self.assertRaises(WebDriverError) as context:
            find_element("#test")

        # Check the exception
        self.assertIn("Failed to find element with selector: #test", str(context.exception))

    def test_handle_driver_exceptions_with_driver_instance(self):
        """Test that handle_driver_exceptions extracts driver type from instance."""
        # Create a mock driver instance
        mock_driver = MagicMock()
        mock_driver.browser_type.value = "chrome"

        # Define a function that raises an error
        @handle_driver_exceptions("Test operation")
        def test_function(driver):
            raise MockWebDriverException("Test error")

        # Call the function
        with self.assertRaises(WebDriverError) as context:
            test_function(mock_driver)

        # Check the exception
        self.assertEqual(context.exception.driver_type, "chrome")


if __name__ == "__main__":
    unittest.main()
