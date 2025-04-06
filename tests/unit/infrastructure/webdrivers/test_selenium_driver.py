"""Tests for the SeleniumWebDriver class."""
import unittest
from unittest.mock import patch, MagicMock

# Define exception classes for testing
class WebDriverException(Exception):
    pass

class TimeoutException(Exception):
    pass

class NoSuchElementException(Exception):
    pass

# Define By class for testing
class By:
    CSS_SELECTOR = "css selector"

from src.core.exceptions import WebDriverError
from src.infrastructure.webdrivers.browser_type import BrowserType
from src.infrastructure.webdrivers.selenium_driver import SeleniumWebDriver

class TestSeleniumWebDriver(unittest.TestCase):
    """Test cases for the SeleniumWebDriver class."""

    @patch("src.infrastructure.webdrivers.factory.WebDriverFactory.create_driver")
    def setUp(self, mock_create_driver):
        """Set up test fixtures."""
        # Set up mock return value
        self.mock_driver = MagicMock()
        mock_create_driver.return_value = self.mock_driver

        # Create SeleniumWebDriver instance
        self.web_driver = SeleniumWebDriver(BrowserType.CHROME)

        # Verify create_driver was called with correct arguments
        mock_create_driver.assert_called_once_with(BrowserType.CHROME, None)

    def test_get(self):
        """Test that get navigates to the specified URL."""
        # Call get
        self.web_driver.get("https://example.com")

        # Verify driver.get was called with correct arguments
        self.mock_driver.get.assert_called_once_with("https://example.com")

    def test_get_error(self):
        """Test that get raises WebDriverError when navigation fails."""
        # Set up mock to raise an exception
        self.mock_driver.get.side_effect = WebDriverException("Navigation failed")

        # Try to call get
        with self.assertRaises(WebDriverError):
            self.web_driver.get("https://example.com")

    def test_quit(self):
        """Test that quit closes the browser."""
        # Call quit
        self.web_driver.quit()

        # Verify driver.quit was called
        self.mock_driver.quit.assert_called_once()

    def test_quit_error(self):
        """Test that quit doesn't raise an error when quitting fails."""
        # Set up mock to raise an exception
        self.mock_driver.quit.side_effect = WebDriverException("Quit failed")

        # Call quit (should not raise an error)
        self.web_driver.quit()

    def test_find_element(self):
        """Test that find_element finds an element using CSS selector."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Call find_element
        result = self.web_driver.find_element(".selector")

        # Check result
        self.assertEqual(result, mock_element)

        # Verify driver.find_element was called with correct arguments
        self.mock_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, ".selector")

    def test_find_element_not_found(self):
        """Test that find_element raises WebDriverError when the element is not found."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

        # Try to call find_element
        with self.assertRaises(WebDriverError):
            self.web_driver.find_element(".selector")

    def test_find_element_error(self):
        """Test that find_element raises WebDriverError when finding an element fails."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = WebDriverException("Find element failed")

        # Try to call find_element
        with self.assertRaises(WebDriverError):
            self.web_driver.find_element(".selector")

    def test_click_element(self):
        """Test that click_element clicks on an element."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Call click_element
        self.web_driver.click_element(".selector")

        # Verify driver.find_element was called with correct arguments
        self.mock_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, ".selector")

        # Verify element.click was called
        mock_element.click.assert_called_once()

    def test_click_element_not_found(self):
        """Test that click_element raises WebDriverError when the element is not found."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

        # Try to call click_element
        with self.assertRaises(WebDriverError):
            self.web_driver.click_element(".selector")

    def test_click_element_error(self):
        """Test that click_element raises WebDriverError when clicking an element fails."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Set up mock to raise an exception
        mock_element.click.side_effect = WebDriverException("Click failed")

        # Try to call click_element
        with self.assertRaises(WebDriverError):
            self.web_driver.click_element(".selector")

    def test_type_text(self):
        """Test that type_text types text into an element."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Call type_text
        self.web_driver.type_text(".selector", "text")

        # Verify driver.find_element was called with correct arguments
        self.mock_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, ".selector")

        # Verify element.send_keys was called with correct arguments
        mock_element.send_keys.assert_called_once_with("text")

    def test_type_text_not_found(self):
        """Test that type_text raises WebDriverError when the element is not found."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

        # Try to call type_text
        with self.assertRaises(WebDriverError):
            self.web_driver.type_text(".selector", "text")

    def test_type_text_error(self):
        """Test that type_text raises WebDriverError when typing text fails."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Set up mock to raise an exception
        mock_element.send_keys.side_effect = WebDriverException("Type text failed")

        # Try to call type_text
        with self.assertRaises(WebDriverError):
            self.web_driver.type_text(".selector", "text")

    def test_take_screenshot(self):
        """Test that take_screenshot takes a screenshot."""
        # Call take_screenshot
        self.web_driver.take_screenshot("screenshot.png")

        # Verify driver.save_screenshot was called with correct arguments
        self.mock_driver.save_screenshot.assert_called_once_with("screenshot.png")

    def test_take_screenshot_error(self):
        """Test that take_screenshot raises WebDriverError when taking a screenshot fails."""
        # Set up mock to raise an exception
        self.mock_driver.save_screenshot.side_effect = WebDriverException("Take screenshot failed")

        # Try to call take_screenshot
        with self.assertRaises(WebDriverError):
            self.web_driver.take_screenshot("screenshot.png")

    def test_is_element_present(self):
        """Test that is_element_present returns True when the element is present."""
        # Set up mock return value
        mock_element = MagicMock()
        self.mock_driver.find_element.return_value = mock_element

        # Call is_element_present
        result = self.web_driver.is_element_present(".selector")

        # Check result
        self.assertTrue(result)

        # Verify driver.find_element was called with correct arguments
        self.mock_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, ".selector")

    def test_is_element_present_not_found(self):
        """Test that is_element_present returns False when the element is not found."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

        # Call is_element_present
        result = self.web_driver.is_element_present(".selector")

        # Check result
        self.assertFalse(result)

    def test_is_element_present_error(self):
        """Test that is_element_present returns False when checking for an element fails."""
        # Set up mock to raise an exception
        self.mock_driver.find_element.side_effect = WebDriverException("Find element failed")

        # Call is_element_present
        result = self.web_driver.is_element_present(".selector")

        # Check result
        self.assertFalse(result)

    def test_get_current_url(self):
        """Test that get_current_url returns the current URL."""
        # Set up mock return value
        self.mock_driver.current_url = "https://example.com"

        # Call get_current_url
        result = self.web_driver.get_current_url()

        # Check result
        self.assertEqual(result, "https://example.com")

    def test_get_current_url_error(self):
        """Test that get_current_url raises WebDriverError when getting the current URL fails."""
        # Set up mock to raise an exception when accessing current_url
        def raise_exception(*args, **kwargs):
            raise WebDriverException("Get current URL failed")

        # Create a property that raises an exception when accessed
        mock_property = property(fget=raise_exception)
        type(self.mock_driver).current_url = mock_property

        # Try to call get_current_url
        with self.assertRaises(WebDriverError):
            self.web_driver.get_current_url()

    @patch("src.infrastructure.webdrivers.selenium_driver.WebDriverWait")
    def test_wait_for_element(self, mock_wait_class):
        """Test that wait_for_element waits for an element to be present."""
        # Set up mock return value
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait

        mock_element = MagicMock()
        mock_wait.until.return_value = mock_element

        # Call wait_for_element
        result = self.web_driver.wait_for_element(".selector", 20)

        # Check result
        self.assertEqual(result, mock_element)

        # Verify WebDriverWait was called with correct arguments
        mock_wait_class.assert_called_once_with(self.mock_driver, 20)

        # Verify wait.until was called with correct arguments
        # We can't directly check the EC.presence_of_element_located argument,
        # but we can check that until was called
        mock_wait.until.assert_called_once()

    @patch("src.infrastructure.webdrivers.selenium_driver.WebDriverWait")
    def test_wait_for_element_timeout(self, mock_wait_class):
        """Test that wait_for_element raises WebDriverError when waiting for an element times out."""
        # Set up mock return value
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait

        # Set up mock to raise an exception
        mock_wait.until.side_effect = TimeoutException("Timeout")

        # Try to call wait_for_element
        with self.assertRaises(WebDriverError):
            self.web_driver.wait_for_element(".selector")

    @patch("src.infrastructure.webdrivers.selenium_driver.WebDriverWait")
    def test_wait_for_element_error(self, mock_wait_class):
        """Test that wait_for_element raises WebDriverError when waiting for an element fails."""
        # Set up mock return value
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait

        # Set up mock to raise an exception
        mock_wait.until.side_effect = WebDriverException("Wait failed")

        # Try to call wait_for_element
        with self.assertRaises(WebDriverError):
            self.web_driver.wait_for_element(".selector")

    def test_switch_to_frame(self):
        """Test that switch_to_frame switches to a frame."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        # Call switch_to_frame
        self.web_driver.switch_to_frame("frame")

        # Verify switch_to.frame was called with correct arguments
        mock_switch_to.frame.assert_called_once_with("frame")

    def test_switch_to_frame_error(self):
        """Test that switch_to_frame raises WebDriverError when switching to a frame fails."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        # Set up mock to raise an exception
        mock_switch_to.frame.side_effect = WebDriverException("Switch to frame failed")

        # Try to call switch_to_frame
        with self.assertRaises(WebDriverError):
            self.web_driver.switch_to_frame("frame")

    def test_switch_to_default_content(self):
        """Test that switch_to_default_content switches to the default content."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        # Call switch_to_default_content
        self.web_driver.switch_to_default_content()

        # Verify switch_to.default_content was called
        mock_switch_to.default_content.assert_called_once()

    def test_switch_to_default_content_error(self):
        """Test that switch_to_default_content raises WebDriverError when switching to default content fails."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        # Set up mock to raise an exception
        mock_switch_to.default_content.side_effect = WebDriverException("Switch to default content failed")

        # Try to call switch_to_default_content
        with self.assertRaises(WebDriverError):
            self.web_driver.switch_to_default_content()

    def test_accept_alert(self):
        """Test that accept_alert accepts an alert."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Call accept_alert
        self.web_driver.accept_alert()

        # Verify alert.accept was called
        mock_alert.accept.assert_called_once()

    def test_accept_alert_error(self):
        """Test that accept_alert raises WebDriverError when accepting an alert fails."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Set up mock to raise an exception
        mock_alert.accept.side_effect = WebDriverException("Accept alert failed")

        # Try to call accept_alert
        with self.assertRaises(WebDriverError):
            self.web_driver.accept_alert()

    def test_dismiss_alert(self):
        """Test that dismiss_alert dismisses an alert."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Call dismiss_alert
        self.web_driver.dismiss_alert()

        # Verify alert.dismiss was called
        mock_alert.dismiss.assert_called_once()

    def test_dismiss_alert_error(self):
        """Test that dismiss_alert raises WebDriverError when dismissing an alert fails."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Set up mock to raise an exception
        mock_alert.dismiss.side_effect = WebDriverException("Dismiss alert failed")

        # Try to call dismiss_alert
        with self.assertRaises(WebDriverError):
            self.web_driver.dismiss_alert()

    def test_get_alert_text(self):
        """Test that get_alert_text returns the text of an alert."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Set up mock return value
        mock_alert.text = "Alert text"

        # Call get_alert_text
        result = self.web_driver.get_alert_text()

        # Check result
        self.assertEqual(result, "Alert text")

    def test_get_alert_text_error(self):
        """Test that get_alert_text raises WebDriverError when getting alert text fails."""
        # Set up mock
        mock_switch_to = MagicMock()
        self.mock_driver.switch_to = mock_switch_to

        mock_alert = MagicMock()
        mock_switch_to.alert = mock_alert

        # Set up mock to raise an exception when accessing text
        def raise_exception(*args, **kwargs):
            raise WebDriverException("Get alert text failed")

        # Create a property that raises an exception when accessed
        mock_property = property(fget=raise_exception)
        type(mock_alert).text = mock_property

        # Try to call get_alert_text
        with self.assertRaises(WebDriverError):
            self.web_driver.get_alert_text()

if __name__ == "__main__":
    unittest.main()
