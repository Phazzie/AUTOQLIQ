"""Defines the interface for WebDriver interactions."""

import logging
from typing import Protocol, Any, List, Tuple

logger = logging.getLogger(__name__)

class IWebDriver(Protocol):
    """Interface defining methods for browser automation drivers."""

    def get(self, url: str) -> None:
        """Navigate to a given URL."""
        ...

    def find_element(self, by: str, value: str) -> Any:
        """Find a single element using the specified locator strategy.

        Args:
            by: Locator strategy (e.g., 'id', 'xpath', 'css selector').
            value: The value of the locator.

        Returns:
            A representation of the web element.

        Raises:
            NoSuchElementException: If the element cannot be found.
        """
        ...

    def find_elements(self, by: str, value: str) -> List[Any]:
        """Find multiple elements using the specified locator strategy."""
        ...

    def click(self, element: Any) -> None:
        """Click on a given element."""
        ...

    def type_text(self, element: Any, text: str, clear_first: bool = True) -> None:
        """Type text into a given element, optionally clearing it first."""
        ...

    def get_attribute(self, element: Any, attribute_name: str) -> str | None:
        """Get the value of an attribute from a given element."""
        ...

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the context of the current frame or window."""
        ...

    def switch_to_frame(self, frame_reference: Any) -> None:
        """Switch focus to a frame (by index, name, id, or element)."""
        ...

    def switch_to_default_content(self) -> None:
        """Switch focus back to the default content from a frame."""
        ...

    def close(self) -> None:
        """Close the current window."""
        ...

    def quit(self) -> None:
        """Quit the driver and close all associated windows."""
        ...

    # Add other necessary methods like wait_for_element, get_current_url, etc.
