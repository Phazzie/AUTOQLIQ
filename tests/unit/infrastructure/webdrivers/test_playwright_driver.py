"""Unit tests for PlaywrightDriver implementation.

This module contains comprehensive unit tests for the PlaywrightDriver class.
The tests verify that the driver correctly implements the IWebDriver interface
and properly handles various scenarios, including error conditions.

The tests use unittest.mock to mock Playwright's API, allowing us to test
the driver without actually launching a browser. This approach makes the
tests faster, more reliable, and independent of the environment.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock

# Define exception classes for testing
class PlaywrightError(Exception):
    pass

class PlaywrightTimeoutError(PlaywrightError):
    pass

from src.core.exceptions import WebDriverError
from src.infrastructure.webdrivers.base import BrowserType
from src.infrastructure.webdrivers.playwright import PlaywrightDriver


class TestPlaywrightDriver(unittest.TestCase):
    """Test cases for PlaywrightDriver class.

    This test suite verifies that the PlaywrightDriver correctly implements
    the IWebDriver interface and handles various scenarios, including errors.

    The tests use mocks to simulate Playwright's behavior without actually
    launching a browser. This approach allows us to test edge cases and error
    handling that would be difficult to reproduce with a real browser.

    We follow the Arrange-Act-Assert pattern for test structure:
    1. Arrange: Set up the test environment and mocks
    2. Act: Call the method being tested
    3. Assert: Verify the expected behavior
    """

    @patch('src.infrastructure.webdrivers.playwright.driver.sync_playwright')
    def setUp(self, mock_sync_playwright):
        """Set up test fixtures."""
        # Setup mocks
        self.mock_playwright = MagicMock()
        mock_sync_playwright.return_value.start.return_value = self.mock_playwright
        self.mock_browser = MagicMock()
        self.mock_playwright.chromium.launch.return_value = self.mock_browser
        self.mock_page = MagicMock()
        self.mock_browser.new_page.return_value = self.mock_page

        # Create driver
        self.driver = PlaywrightDriver(browser_type=BrowserType.CHROME)

        # Verify initialization
        mock_sync_playwright.return_value.start.assert_called_once()
        self.mock_playwright.chromium.launch.assert_called_once()
        self.mock_browser.new_page.assert_called_once()

    def test_initialization(self):
        """Test that PlaywrightDriver initializes correctly."""
        # Verify initialization
        self.assertEqual(self.driver.browser_type, BrowserType.CHROME)
        self.assertEqual(self.driver.browser, self.mock_browser)
        self.assertEqual(self.driver.page, self.mock_page)

    def test_get_method(self):
        """Test that get method navigates to URL."""
        # Call get
        self.driver.get("https://example.com")

        # Verify get was called
        self.mock_page.goto.assert_called_once_with("https://example.com")

    def test_get_error(self):
        """Test that get raises WebDriverError when navigation fails."""
        # Set up mock to raise an exception
        self.mock_page.goto.side_effect = PlaywrightError("Navigation failed")

        # Try to call get
        with self.assertRaises(WebDriverError):
            self.driver.get("https://example.com")

    def test_find_element(self):
        """Test that find_element returns a locator."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value.first = mock_locator
        mock_locator.count.return_value = 1

        # Call find_element
        element = self.driver.find_element("#test-element")

        # Verify locator was created and returned
        self.mock_page.locator.assert_called_once_with("#test-element")
        self.assertEqual(element, mock_locator)

    def test_find_element_not_found(self):
        """Test that find_element raises WebDriverError when element not found."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value.first = mock_locator
        mock_locator.count.return_value = 0

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.find_element("#non-existent-element")

    def test_is_element_present(self):
        """Test that is_element_present returns True when element exists."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value = mock_locator
        mock_locator.count.return_value = 1

        # Call is_element_present
        result = self.driver.is_element_present("#test-element")

        # Verify result is True
        self.assertTrue(result)
        self.mock_page.locator.assert_called_once_with("#test-element")

    def test_is_element_present_not_found(self):
        """Test that is_element_present returns False when element doesn't exist."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value = mock_locator
        mock_locator.count.return_value = 0

        # Call is_element_present
        result = self.driver.is_element_present("#non-existent-element")

        # Verify result is False
        self.assertFalse(result)
        self.mock_page.locator.assert_called_once_with("#non-existent-element")

    def test_quit(self):
        """Test that quit method closes browser and stops playwright."""
        # Call quit
        self.driver.quit()

        # Verify browser was closed and playwright was stopped
        self.mock_browser.close.assert_called_once()
        self.mock_playwright.stop.assert_called_once()

    def test_quit_browser_error(self):
        """Test that quit handles errors when closing the browser."""
        # Set up mock to raise an exception
        self.mock_browser.close.side_effect = PlaywrightError("Close failed")

        # Call quit (should not raise an error)
        self.driver.quit()

        # Verify playwright.stop was still called
        self.mock_playwright.stop.assert_called_once()

    def test_quit_playwright_error(self):
        """Test that quit handles errors when stopping the playwright instance."""
        # Set up mock to raise an exception
        self.mock_playwright.stop.side_effect = Exception("Stop failed")

        # Call quit (should not raise an error)
        self.driver.quit()

        # Verify browser.close was still called
        self.mock_browser.close.assert_called_once()

    def test_click_element(self):
        """Test that click_element clicks an element."""
        # Call click_element
        self.driver.click_element("#test-element")

        # Verify page.click was called with correct arguments
        self.mock_page.click.assert_called_once_with("#test-element")

    def test_click_element_not_found(self):
        """Test that click_element raises WebDriverError when element not found."""
        # Setup mock to raise an exception
        self.mock_page.click.side_effect = PlaywrightTimeoutError("Element not found")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.click_element("#non-existent-element")

    def test_click_element_error(self):
        """Test that click_element raises WebDriverError when clicking fails."""
        # Setup mock to raise an exception
        self.mock_page.click.side_effect = PlaywrightError("Click failed")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.click_element("#test-element")

    def test_type_text(self):
        """Test that type_text types text into an element."""
        # Call type_text
        self.driver.type_text("#test-element", "test text")

        # Verify page.fill was called with correct arguments
        self.mock_page.fill.assert_called_once_with("#test-element", "test text")

    def test_type_text_not_found(self):
        """Test that type_text raises WebDriverError when element not found."""
        # Setup mock to raise an exception
        self.mock_page.fill.side_effect = PlaywrightTimeoutError("Element not found")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.type_text("#non-existent-element", "test text")

    def test_type_text_error(self):
        """Test that type_text raises WebDriverError when typing fails."""
        # Setup mock to raise an exception
        self.mock_page.fill.side_effect = PlaywrightError("Fill failed")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.type_text("#test-element", "test text")

    def test_take_screenshot(self):
        """Test that take_screenshot takes a screenshot."""
        # Call take_screenshot
        self.driver.take_screenshot("screenshot.png")

        # Verify screenshot was taken
        self.mock_page.screenshot.assert_called_once_with(path="screenshot.png")

    def test_take_screenshot_error(self):
        """Test that take_screenshot raises WebDriverError when screenshot fails."""
        # Setup mock to raise an exception
        self.mock_page.screenshot.side_effect = PlaywrightError("Screenshot failed")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.take_screenshot("screenshot.png")

    def test_get_current_url(self):
        """Test that get_current_url returns the current URL."""
        # Setup mock
        type(self.mock_page).url = PropertyMock(return_value="https://example.com")

        # Call get_current_url
        result = self.driver.get_current_url()

        # Verify result
        self.assertEqual(result, "https://example.com")

    def test_get_current_url_error(self):
        """Test that get_current_url raises WebDriverError when getting URL fails."""
        # Setup mock to raise an exception
        def raise_exception(*args, **kwargs):
            raise PlaywrightError("Get URL failed")
        type(self.mock_page).url = PropertyMock(side_effect=raise_exception)

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.get_current_url()

    def test_wait_for_element(self):
        """Test that wait_for_element waits for an element."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value = mock_locator
        mock_locator.wait_for.return_value = mock_locator

        # Call wait_for_element
        result = self.driver.wait_for_element("#test-element", 10)

        # Verify wait_for was called and result is correct
        self.mock_page.locator.assert_called_once_with("#test-element")
        mock_locator.wait_for.assert_called_once_with(timeout=10000)
        self.assertEqual(result, mock_locator)

    def test_wait_for_element_timeout(self):
        """Test that wait_for_element raises WebDriverError on timeout."""
        # Setup mocks
        mock_locator = MagicMock()
        self.mock_page.locator.return_value = mock_locator
        mock_locator.wait_for.side_effect = PlaywrightTimeoutError("Timeout waiting for element")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.wait_for_element("#test-element", 10)

    def test_execute_script(self):
        """Test that execute_script executes JavaScript."""
        # Setup mock
        self.mock_page.evaluate.return_value = "result"

        # Call execute_script
        result = self.driver.execute_script("return 'result';")

        # Verify evaluate was called and result is correct
        self.mock_page.evaluate.assert_called_once_with("return 'result';")
        self.assertEqual(result, "result")

    def test_execute_script_error(self):
        """Test that execute_script raises WebDriverError when script fails."""
        # Setup mock to raise an exception
        self.mock_page.evaluate.side_effect = PlaywrightError("Script failed")

        # Verify WebDriverError is raised
        with self.assertRaises(WebDriverError):
            self.driver.execute_script("invalid script")


if __name__ == '__main__':
    unittest.main()
