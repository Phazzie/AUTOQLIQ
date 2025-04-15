"""Mock WebDriver implementation for testing."""

from src.core.interfaces import IWebDriver


class MockWebDriver(IWebDriver):
    """
    A mock implementation of IWebDriver for testing purposes.
    
    This driver doesn't actually interact with a browser but simulates
    the interface for testing workflows without a real browser.
    """
    
    def __init__(self):
        """Initialize the mock driver."""
        self.browser_type = "mock"
        self.current_url = "about:blank"
        self.page_source = "<html><body>Mock page</body></html>"
        self.title = "Mock Browser"
        self.is_open = False
    
    def open(self) -> None:
        """Open the mock browser."""
        self.is_open = True
    
    def close(self) -> None:
        """Close the mock browser."""
        self.is_open = False
    
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        self.current_url = url
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.current_url
    
    def get_page_source(self) -> str:
        """Get the page source."""
        return self.page_source
    
    def get_title(self) -> str:
        """Get the page title."""
        return self.title
    
    def find_element(self, selector: str) -> object:
        """Find an element by selector."""
        return MockElement(selector)
    
    def find_elements(self, selector: str) -> list:
        """Find elements by selector."""
        return [MockElement(selector)]
    
    def execute_script(self, script: str, *args) -> any:
        """Execute JavaScript."""
        return None
    
    def take_screenshot(self, file_path: str) -> bool:
        """Take a screenshot."""
        return True
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> object:
        """Wait for an element to be present."""
        return MockElement(selector)
    
    def wait_for_element_visible(self, selector: str, timeout: int = 10) -> object:
        """Wait for an element to be visible."""
        return MockElement(selector)
    
    def wait_for_element_clickable(self, selector: str, timeout: int = 10) -> object:
        """Wait for an element to be clickable."""
        return MockElement(selector)


class MockElement:
    """A mock element for testing."""
    
    def __init__(self, selector: str):
        """Initialize the mock element."""
        self.selector = selector
        self.text = f"Mock element text for {selector}"
        self.is_displayed = True
        self.is_enabled = True
    
    def click(self) -> None:
        """Click the element."""
        pass
    
    def send_keys(self, text: str) -> None:
        """Send keys to the element."""
        pass
    
    def clear(self) -> None:
        """Clear the element."""
        pass
    
    def get_attribute(self, name: str) -> str:
        """Get an attribute of the element."""
        return f"mock-{name}-value"
    
    def get_text(self) -> str:
        """Get the text of the element."""
        return self.text
