import unittest
from unittest.mock import patch, MagicMock
from src.infrastructure.webdrivers import SeleniumWebDriver

class TestSeleniumWebDriver(unittest.TestCase):
    @patch("src.infrastructure.webdrivers.webdriver.Chrome")
    def setUp(self, MockChrome):
        self.mock_driver = MockChrome.return_value
        self.webdriver = SeleniumWebDriver()

    def test_get(self):
        url = "https://example.com"
        self.webdriver.get(url)
        self.mock_driver.get.assert_called_once_with(url)

    def test_quit(self):
        self.webdriver.quit()
        self.mock_driver.quit.assert_called_once()

    def test_find_element(self):
        selector = "#element"
        self.webdriver.find_element(selector)
        self.mock_driver.find_element.assert_called_once_with("css selector", selector)

    def test_click_element(self):
        selector = "#button"
        self.webdriver.click_element(selector)
        self.mock_driver.find_element.return_value.click.assert_called_once()

    def test_type_text(self):
        selector = "#input"
        text = "test"
        self.webdriver.type_text(selector, text)
        self.mock_driver.find_element.return_value.send_keys.assert_called_once_with(text)

    def test_take_screenshot(self):
        file_path = "screenshot.png"
        self.webdriver.take_screenshot(file_path)
        self.mock_driver.save_screenshot.assert_called_once_with(file_path)

    def test_is_element_present(self):
        selector = "#element"
        self.mock_driver.find_element.return_value = True
        result = self.webdriver.is_element_present(selector)
        self.assertTrue(result)
        self.mock_driver.find_element.assert_called_once_with("css selector", selector)

    def test_is_element_present_not_found(self):
        selector = "#element"
        self.mock_driver.find_element.side_effect = Exception("Element not found")
        result = self.webdriver.is_element_present(selector)
        self.assertFalse(result)
        self.mock_driver.find_element.assert_called_once_with("css selector", selector)

    def test_get_current_url(self):
        url = "https://example.com"
        self.mock_driver.current_url = url
        result = self.webdriver.get_current_url()
        self.assertEqual(result, url)

if __name__ == "__main__":
    unittest.main()
