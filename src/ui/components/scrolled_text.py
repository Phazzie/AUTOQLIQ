"""Scrolled text component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, Union

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory
from src.ui.components.ui_component import UIComponent


class ScrolledText(UIComponent):
    """A text widget with a scrollbar.

    This component provides a text widget with a scrollbar and methods for managing
    the text content.

    Attributes:
        frame: The frame containing the text widget and scrollbar
        text: The text widget
        scrollbar: The scrollbar widget
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL,
        on_change: Optional[Callable[[tk.Event], None]] = None
    ):
        """Initialize a ScrolledText.

        Args:
            parent: The parent widget
            height: The height of the text widget in lines
            width: The width of the text widget in characters
            wrap: The wrap mode (WORD, CHAR, NONE)
            state: The initial state of the text widget (NORMAL, DISABLED)
            on_change: A callback to execute when the text changes

        Raises:
            UIError: If the component cannot be created
        """
        super().__init__(parent)
        try:
            # Create the component
            result = UIFactory.create_scrolled_text(
                parent, height=height, width=width, wrap=wrap, state=state
            )

            # Store the widgets
            self.frame = result["frame"]
            self.text = result["text"]
            self.scrollbar = result["scrollbar"]

            # Set the main widget
            self._widget = self.frame

            # Bind the change event if a callback is provided
            if on_change:
                self.text.bind("<<Modified>>", on_change)
        except Exception as e:
            error_msg = "Failed to create ScrolledText"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)

    def set_text(self, text: str) -> None:
        """Set the text content.

        Args:
            text: The text to display

        Raises:
            UIError: If the text cannot be set
        """
        try:
            # Clear the text widget
            self.clear()

            # Add the text
            self.text.insert(tk.END, text)
        except Exception as e:
            error_msg = "Failed to set text in ScrolledText"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)

    def append_text(self, text: str) -> None:
        """Append text to the content.

        Args:
            text: The text to append

        Raises:
            UIError: If the text cannot be appended
        """
        try:
            # Get the current state
            current_state = self.text["state"]

            # Enable editing if the widget is disabled
            if current_state == tk.DISABLED:
                self.text.config(state=tk.NORMAL)

            # Append the text
            self.text.insert(tk.END, text)

            # Scroll to the end
            self.text.see(tk.END)

            # Restore the original state
            if current_state == tk.DISABLED:
                self.text.config(state=current_state)
        except Exception as e:
            error_msg = f"Failed to append text to ScrolledText: {text}"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)

    def append_line(self, text: str) -> None:
        """Append a line of text to the content.

        Args:
            text: The text to append

        Raises:
            UIError: If the text cannot be appended
        """
        self.append_text(f"{text}\n")

    def get_text(self) -> str:
        """Get the text content.

        Returns:
            The text content

        Raises:
            UIError: If the text cannot be retrieved
        """
        try:
            return self.text.get("1.0", tk.END)
        except Exception as e:
            error_msg = "Failed to get text from ScrolledText"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)

    def clear(self) -> None:
        """Clear the text content.

        Raises:
            UIError: If the text cannot be cleared
        """
        try:
            # Get the current state
            current_state = self.text["state"]

            # Enable editing if the widget is disabled
            if current_state == tk.DISABLED:
                self.text.config(state=tk.NORMAL)

            # Clear the text
            self.text.delete("1.0", tk.END)

            # Restore the original state
            if current_state == tk.DISABLED:
                self.text.config(state=current_state)
        except Exception as e:
            error_msg = "Failed to clear ScrolledText"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)

    def update(self) -> None:
        """Update the component state."""
        # Nothing to update by default
        pass

    def set_state(self, state: str) -> None:
        """Set the state of the text widget.

        Args:
            state: The state to set (NORMAL, DISABLED)

        Raises:
            UIError: If the state cannot be set
        """
        try:
            self.text.config(state=state)
        except Exception as e:
            error_msg = f"Failed to set state of ScrolledText: {state}"
            raise UIError(error_msg, component_name="ScrolledText", cause=e)
