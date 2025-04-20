"""Defines the interface for WebDriver interactions."""

import logging
from typing import Any, List, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class IWebDriver(ABC):
    """Interface for web driver operations required by actions."""

    @abstractmethod
    def get(self, url: str) -> None:
        """Navigate to the specified URL."""
        pass

    @abstractmethod
    def find_element(self, selector: str) -> Any:
        """Locate an element using the provided selector."""
        pass

    @abstractmethod
    def click_element(self, selector: str) -> None:
        """Click on an element identified by the CSS selector."""
        pass

    @abstractmethod
    def click(self, selector: str) -> None:
        """Alias for click_element for backward compatibility."""
        pass

    @abstractmethod
    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the CSS selector."""
        pass

    @abstractmethod
    def get_attribute(self, selector: str, attribute: str) -> Any:
        """Retrieve the specified attribute from the element identified by the CSS selector."""
        pass

    @abstractmethod
    def quit(self) -> None:
        """Quit the WebDriver and close all associated windows."""
        pass

    @abstractmethod
    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it to the specified file path."""
        pass

    @abstractmethod
    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error."""
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        """Get the current URL of the browser."""
        pass

    @abstractmethod
    def execute_script(self, script: str, *args: Any) -> Any:
        """Executes JavaScript in the current window/frame."""
        pass

    @abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait explicitly for an element to be present on the page."""
        pass

    @abstractmethod
    def switch_to_frame(self, frame_reference: Any) -> None:
        """Switch focus to a frame or iframe."""
        pass

    @abstractmethod
    def switch_to_default_content(self) -> None:
        """Switch back to the default content (main document)."""
        pass

    @abstractmethod
    def accept_alert(self) -> None:
        """Accept an alert, confirm, or prompt dialog."""
        pass

    @abstractmethod
    def dismiss_alert(self) -> None:
        """Dismiss an alert or confirm dialog."""
        pass

    @abstractmethod
    def get_alert_text(self) -> str:
        """Get the text content of an alert, confirm, or prompt dialog."""
        pass
