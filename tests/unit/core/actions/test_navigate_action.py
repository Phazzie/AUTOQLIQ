"""Tests for the NavigateAction class."""

import unittest
from unittest.mock import MagicMock, patch
import logging

from src.core.actions.navigation import NavigateAction, URL_PATTERN
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError, WebDriverError, ActionError


class TestNavigateAction(unittest.TestCase):
    """Test cases for the NavigateAction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Capture logs for testing
        self.log_patcher = patch('src.core.actions.navigation.logger')
        self.mock_logger = self.log_patcher.start()
        
        # Mock objects
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        
        # Valid URL for testing
        self.valid_url = "https://example.com"
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.log_patcher.stop()
    
    def test_init_with_valid_url(self):
        """Test initialization with valid URL."""
        action = NavigateAction(url=self.valid_url, name="TestNav")
        self.assertEqual(action.url, self.valid_url)
        self.assertEqual(action.name, "TestNav")
        self.assertEqual(action.action_type, "Navigate")
    
    def test_init_with_invalid_url_logs_warning(self):
        """Test initialization with invalid URL format logs warning but doesn't fail."""
        invalid_url = "not-a-url"
        action = NavigateAction(url=invalid_url, name="TestInvalidNav")
        self.assertEqual(action.url, invalid_url)
        self.mock_logger.warning.assert_called_once()
    
    def test_init_with_empty_url_raises_error(self):
        """Test initialization with empty URL raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            NavigateAction(url="", name="EmptyUrl")
        
        self.assertIn("URL", str(context.exception))
        self.assertIn("non-empty", str(context.exception))
    
    def test_init_with_none_url_raises_error(self):
        """Test initialization with None URL raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            NavigateAction(url=None, name="NoneUrl")  # type: ignore
        
        self.assertIn("URL", str(context.exception))
        self.assertIn("non-empty", str(context.exception))
    
    def test_validate_with_valid_url(self):
        """Test validation passes with valid URL."""
        action = NavigateAction(url=self.valid_url)
        self.assertTrue(action.validate())
    
    def test_validate_with_invalid_url_logs_warning(self):
        """Test validation with invalid URL logs warning but passes."""
        invalid_url = "just-text"
        action = NavigateAction(url=invalid_url)
        self.assertTrue(action.validate())  # Should pass but log warning
        self.mock_logger.warning.assert_called()
    
    def test_execute_success(self):
        """Test successful execution of the navigate action."""
        action = NavigateAction(url=self.valid_url)
        
        # Configure mock
        self.mock_driver.get.return_value = None  # Successful navigation returns None
        
        # Execute and verify
        result = action.execute(self.mock_driver)
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertIn(self.valid_url, result.message)
        self.mock_driver.get.assert_called_once_with(self.valid_url)
        self.mock_logger.info.assert_called()
        self.mock_logger.debug.assert_called()
    
    def test_execute_with_driver_error(self):
        """Test execution when driver.get() raises WebDriverError."""
        action = NavigateAction(url=self.valid_url)
        
        # Configure mock to raise WebDriverError
        self.mock_driver.get.side_effect = WebDriverError("Connection failed")
        
        # Execute and verify
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("Error navigating", result.message)
        self.assertIn("Connection failed", result.message)
        self.mock_driver.get.assert_called_once_with(self.valid_url)
        self.mock_logger.error.assert_called()
    
    def test_execute_with_unexpected_error(self):
        """Test execution when an unexpected exception occurs."""
        action = NavigateAction(url=self.valid_url)
        
        # Configure mock to raise an unexpected error
        self.mock_driver.get.side_effect = RuntimeError("Something went wrong")
        
        # Execute and verify
        result = action.execute(self.mock_driver)
        
        self.assertFalse(result.is_success())
        self.assertEqual(result.status, ActionStatus.FAILURE)
        self.assertIn("Unexpected error", result.message)
        self.mock_driver.get.assert_called_once_with(self.valid_url)
        self.mock_logger.error.assert_called()
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary includes URL."""
        action = NavigateAction(url=self.valid_url, name="SerializeTest")
        
        # Mock the parent class to_dict method for testing
        with patch('src.core.actions.base.ActionBase.to_dict', return_value={"type": "Navigate", "name": "SerializeTest"}):
            result = action.to_dict()
        
        self.assertEqual(result["url"], self.valid_url)
        self.assertEqual(result["type"], "Navigate")
        self.assertEqual(result["name"], "SerializeTest")
    
    def test_url_pattern_matches_valid_urls(self):
        """Test that the URL_PATTERN correctly matches valid URLs."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://sub.example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com:8080/path"
        ]
        
        for url in valid_urls:
            self.assertTrue(URL_PATTERN.match(url), f"URL should be valid: {url}")
    
    def test_url_pattern_rejects_invalid_urls(self):
        """Test that the URL_PATTERN correctly rejects invalid URLs."""
        invalid_urls = [
            "example.com",  # Missing protocol
            "htp://example.com",  # Typo in protocol
            "http:/example.com",  # Missing slash
            "http://",  # Missing domain
            "ftp://example.com",  # Wrong protocol
            "http:example.com",  # Missing slashes
            ""  # Empty string
        ]
        
        for url in invalid_urls:
            self.assertFalse(URL_PATTERN.match(url), f"URL should be invalid: {url}")
    
    def test_repr_method(self):
        """Test the __repr__ method returns expected string."""
        action = NavigateAction(url=self.valid_url, name="ReprTest")
        expected = "NavigateAction(name='ReprTest', url='https://example.com')"
        self.assertEqual(repr(action), expected)


if __name__ == "__main__":
    unittest.main()
