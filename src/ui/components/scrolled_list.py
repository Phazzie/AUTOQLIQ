"""Scrolled list component for AutoQliq UI."""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Any, Dict, Union

from src.core.exceptions import UIError
from src.ui.common.ui_factory import UIFactory
from src.ui.components.ui_component import UIComponent


class ScrolledList(UIComponent):
    """A listbox with a scrollbar.

    This component provides a listbox with a scrollbar and methods for managing
    the list items.

    Attributes:
        frame: The frame containing the listbox and scrollbar
        listbox: The listbox widget
        scrollbar: The scrollbar widget
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.SINGLE,
        on_select: Optional[Callable[[tk.Event], None]] = None
    ):
        """Initialize a ScrolledList.

        Args:
            parent: The parent widget
            height: The height of the listbox in lines
            width: The width of the listbox in characters
            selectmode: The selection mode (SINGLE, MULTIPLE, EXTENDED, BROWSE)
            on_select: A callback to execute when an item is selected

        Raises:
            UIError: If the component cannot be created
        """
        super().__init__(parent)
        try:
            # Create the component
            result = UIFactory.create_scrolled_listbox(
                parent, height=height, width=width, selectmode=selectmode
            )

            # Store the widgets
            self.frame = result["frame"]
            self.listbox = result["listbox"]
            self.scrollbar = result["scrollbar"]

            # Set the main widget
            self._widget = self.frame

            # Bind the selection event if a callback is provided
            if on_select:
                self.listbox.bind("<<ListboxSelect>>", on_select)
        except Exception as e:
            error_msg = "Failed to create ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def set_items(self, items: List[str]) -> None:
        """Set the items in the listbox.

        Args:
            items: The items to display

        Raises:
            UIError: If the items cannot be set
        """
        try:
            # Clear the listbox
            self.listbox.delete(0, tk.END)

            # Add the items
            for item in items:
                self.listbox.insert(tk.END, item)
        except Exception as e:
            error_msg = "Failed to set items in ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def add_item(self, item: str) -> None:
        """Add an item to the listbox.

        Args:
            item: The item to add

        Raises:
            UIError: If the item cannot be added
        """
        try:
            self.listbox.insert(tk.END, item)
        except Exception as e:
            error_msg = f"Failed to add item to ScrolledList: {item}"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def remove_selected(self) -> None:
        """Remove the selected items from the listbox.

        Raises:
            UIError: If the items cannot be removed
        """
        try:
            # Get the selected indices
            selected_indices = self.listbox.curselection()

            # Remove the items in reverse order to avoid index shifting
            for index in sorted(selected_indices, reverse=True):
                self.listbox.delete(index)
        except Exception as e:
            error_msg = "Failed to remove selected items from ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def get_selected_index(self) -> Optional[int]:
        """Get the index of the selected item.

        Returns:
            The index of the selected item, or None if no item is selected

        Raises:
            UIError: If the selected index cannot be retrieved
        """
        try:
            # Get the selected indices
            selected_indices = self.listbox.curselection()

            # Return the first selected index, or None if no item is selected
            return selected_indices[0] if selected_indices else None
        except Exception as e:
            error_msg = "Failed to get selected index from ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def get_selected_item(self) -> Optional[str]:
        """Get the selected item.

        Returns:
            The selected item, or None if no item is selected

        Raises:
            UIError: If the selected item cannot be retrieved
        """
        try:
            # Get the selected index
            index = self.get_selected_index()

            # Return the item at the selected index, or None if no item is selected
            return self.listbox.get(index) if index is not None else None
        except Exception as e:
            error_msg = "Failed to get selected item from ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def get_all_items(self) -> List[str]:
        """Get all items in the listbox.

        Returns:
            A list of all items in the listbox

        Raises:
            UIError: If the items cannot be retrieved
        """
        try:
            # Get the number of items
            count = self.listbox.size()

            # Get all items
            return [self.listbox.get(i) for i in range(count)]
        except Exception as e:
            error_msg = "Failed to get all items from ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def select_item(self, index: int) -> None:
        """Select an item in the listbox.

        Args:
            index: The index of the item to select

        Raises:
            UIError: If the item cannot be selected
        """
        try:
            # Clear the current selection
            self.listbox.selection_clear(0, tk.END)

            # Select the item
            self.listbox.selection_set(index)

            # Ensure the item is visible
            self.listbox.see(index)
        except Exception as e:
            error_msg = f"Failed to select item in ScrolledList: {index}"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def clear(self) -> None:
        """Clear the listbox.

        Raises:
            UIError: If the listbox cannot be cleared
        """
        try:
            self.listbox.delete(0, tk.END)
        except Exception as e:
            error_msg = "Failed to clear ScrolledList"
            raise UIError(error_msg, component_name="ScrolledList", cause=e)

    def update(self) -> None:
        """Update the component state."""
        # Nothing to update by default
        pass
