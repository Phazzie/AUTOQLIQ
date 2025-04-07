"""WebDriver interface for AutoQliq.

This module defines the interface for web driver implementations that provide
browser automation capabilities.
"""
import abc
from typing import Any, Union, List, Dict, Optional # Added List, Dict, Optional

# Assume WebDriverError is defined in core.exceptions
# from src.core.exceptions import WebDriverError

class IWebDriver(abc.ABC):
    """Interface for web driver implementations."""
    @abc.abstractmethod
    def get(self, url: str) -> None:
        """Navigate to the specified URL."""
        pass

    @abc.abstractmethod
    def quit(self) -> None:
        """Quit the WebDriver and close all associated windows."""
        pass

    @abc.abstractmethod
    def find_element(self, selector: str) -> Any:
        """Find a single element on the page using CSS selector."""
        pass

    @abc.abstractmethod
    def click_element(self, selector: str) -> None:
        """Click on an element identified by the CSS selector."""
        pass

    @abc.abstractmethod
    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the CSS selector."""
        pass

    @abc.abstractmethod
    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it to the specified file path."""
        pass

    @abc.abstractmethod
    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error."""
        pass

    @abc.abstractmethod
    def get_current_url(self) -> str:
        """Get the current URL of the browser."""
        pass

    @abc.abstractmethod
    def execute_script(self, script: str, *args: Any) -> Any:
        """Executes JavaScript in the current window/frame.

        Args:
            script: The JavaScript code to execute.
            *args: Any arguments to pass to the script. These will be available
                   in the script as the 'arguments' array.

        Returns:
            The value returned by the script (if any), JSON-serializable.

        Raises:
            WebDriverError: If script execution fails.
        """
        pass

    # --- Optional but Recommended Methods ---

    @abc.abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait explicitly for an element to be present on the page."""
        pass

    @abc.abstractmethod
    def switch_to_frame(self, frame_reference: Union[str, int, Any]) -> None:
        """Switch focus to a frame or iframe."""
        pass

    @abc.abstractmethod
    def switch_to_default_content(self) -> None:
        """Switch back to the default content (main document)."""
        pass

    @abc.abstractmethod
    def accept_alert(self) -> None:
        """Accept an alert, confirm, or prompt dialog."""
        pass

    @abc.abstractmethod
    def dismiss_alert(self) -> None:
        """Dismiss an alert or confirm dialog."""
        pass

    @abc.abstractmethod
    def get_alert_text(self) -> str:
        """Get the text content of an alert, confirm, or prompt dialog."""
        pass