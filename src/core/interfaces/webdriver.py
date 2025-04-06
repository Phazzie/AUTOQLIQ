"""WebDriver interface for AutoQliq.

This module defines the interface for web driver implementations that provide
browser automation capabilities.
"""
import abc
from typing import Any, Union

# Assume WebDriverError is defined in core.exceptions
# from src.core.exceptions import WebDriverError

class IWebDriver(abc.ABC):
    """Interface for web driver implementations.

    This interface defines the contract for browser automation in the AutoQliq application.
    It abstracts the underlying web driver implementation, allowing the application to work
    with different browser automation libraries.
    """
    @abc.abstractmethod
    def get(self, url: str) -> None:
        """Navigate to the specified URL.

        Args:
            url: The URL to navigate to

        Raises:
            WebDriverError: If navigation fails
        """
        pass

    @abc.abstractmethod
    def quit(self) -> None:
        """Quit the WebDriver and close all associated windows.

        Raises:
            WebDriverError: If quitting the driver fails (optional, often called during cleanup)
        """
        pass

    @abc.abstractmethod
    def find_element(self, selector: str) -> Any:
        """Find a single element on the page using CSS selector.

        Args:
            selector: CSS selector to locate the element

        Returns:
            The found element (specific type depends on implementation, e.g., WebElement).

        Raises:
            WebDriverError: If the element cannot be found (e.g., NoSuchElementException).
        """
        pass

    @abc.abstractmethod
    def click_element(self, selector: str) -> None:
        """Click on an element identified by the CSS selector.

        Args:
            selector: CSS selector to locate the element to click

        Raises:
            WebDriverError: If the element cannot be found or clicked (e.g., ElementNotInteractable).
        """
        pass

    @abc.abstractmethod
    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the CSS selector.
        Should typically clear the element before typing unless specified otherwise.

        Args:
            selector: CSS selector to locate the element
            text: The text to type into the element

        Raises:
            WebDriverError: If the element cannot be found or the text cannot be typed.
        """
        pass

    @abc.abstractmethod
    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it to the specified file path.

        Args:
            file_path: Path where the screenshot should be saved

        Raises:
            WebDriverError: If taking or saving the screenshot fails (e.g., I/O error).
        """
        pass

    @abc.abstractmethod
    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error.

        Args:
            selector: CSS selector to locate the element

        Returns:
            True if the element is present, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_current_url(self) -> str:
        """Get the current URL of the browser.

        Returns:
            The current URL

        Raises:
            WebDriverError: If getting the current URL fails.
        """
        pass

    # --- Optional but Recommended Methods ---

    # @abc.abstractmethod
    # def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
    #     """Wait explicitly for an element to be present on the page.

    #     Args:
    #         selector: CSS selector to locate the element
    #         timeout: Maximum time to wait in seconds

    #     Returns:
    #         The found element

    #     Raises:
    #         WebDriverError: If the element is not found within the timeout (e.g., TimeoutException).
    #     """
    #     pass

    # @abc.abstractmethod
    # def switch_to_frame(self, frame_reference: Union[str, int, Any]) -> None:
    #     """Switch focus to a frame or iframe.

    #     Args:
    #         frame_reference: The frame to switch to. Can be an element, name/id, or index

    #     Raises:
    #         WebDriverError: If switching to the frame fails.
    #     """
    #     pass

    # @abc.abstractmethod
    # def switch_to_default_content(self) -> None:
    #     """Switch back to the default content (main document).

    #     Raises:
    #         WebDriverError: If switching to default content fails.
    #     """
    #     pass

    # @abc.abstractmethod
    # def accept_alert(self) -> None:
    #     """Accept an alert, confirm, or prompt dialog.

    #     Raises:
    #         WebDriverError: If no alert is present or accepting the alert fails.
    #     """
    #     pass

    # @abc.abstractmethod
    # def dismiss_alert(self) -> None:
    #     """Dismiss an alert, confirm, or prompt dialog.

    #     Raises:
    #         WebDriverError: If no alert is present or dismissing the alert fails.
    #     """
    #     pass

    # @abc.abstractmethod
    # def get_alert_text(self) -> str:
    #     """Get the text of an alert, confirm, or prompt dialog.

    #     Returns:
    #         The text of the alert

    #     Raises:
    #         WebDriverError: If no alert is present or getting the text fails.
    #     """
    #     pass