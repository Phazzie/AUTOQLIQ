"""Action list component for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Optional, Callable, Any, Dict

from src.core.exceptions import UIError
from src.ui.components.ui_component import UIComponent

logger = logging.getLogger(__name__)


class ActionList(UIComponent):
    """
    A component for displaying and editing workflow actions.
    
    This component provides a listbox with a scrollbar for displaying actions,
    along with buttons for common operations like adding, editing, and deleting actions.
    
    Attributes:
        frame: The main frame containing all widgets
        listbox: The listbox for displaying actions
        scrollbar: The scrollbar for the listbox
        button_frame: The frame containing the buttons
        add_button: Button for adding a new action
        edit_button: Button for editing the selected action
        delete_button: Button for deleting the selected action
        move_up_button: Button for moving the selected action up
        move_down_button: Button for moving the selected action down
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_select: Optional[Callable[[int], None]] = None,
        on_add: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        on_move_up: Optional[Callable[[int], None]] = None,
        on_move_down: Optional[Callable[[int], None]] = None,
        height: int = 15,
        width: int = 50
    ):
        """
        Initialize an ActionList component.
        
        Args:
            parent: The parent widget
            on_select: Callback when an action is selected
            on_add: Callback when the add button is clicked
            on_edit: Callback when the edit button is clicked
            on_delete: Callback when the delete button is clicked
            on_move_up: Callback when the move up button is clicked
            on_move_down: Callback when the move down button is clicked
            height: Height of the listbox in lines
            width: Width of the listbox in characters
            
        Raises:
            UIError: If the component cannot be created
        """
        super().__init__(parent)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        try:
            # Create the main frame
            self.frame = ttk.Frame(parent)
            self._widget = self.frame
            
            # Create a label
            label = ttk.Label(self.frame, text="Actions:")
            label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
            
            # Create a frame for the listbox and scrollbar
            list_frame = ttk.Frame(self.frame)
            list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Create the listbox
            self.listbox = tk.Listbox(
                list_frame,
                height=height,
                width=width,
                selectmode=tk.SINGLE,
                exportselection=0  # Don't lose selection when clicking elsewhere
            )
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create the scrollbar
            self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.listbox.config(yscrollcommand=self.scrollbar.set)
            
            # Create a frame for the buttons
            self.button_frame = ttk.Frame(self.frame)
            self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
            
            # Create the buttons
            self.add_button = ttk.Button(
                self.button_frame,
                text="Add",
                command=self._on_add if on_add else lambda: None
            )
            self.add_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.edit_button = ttk.Button(
                self.button_frame,
                text="Edit",
                command=self._on_edit if on_edit else lambda: None,
                state=tk.DISABLED
            )
            self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.delete_button = ttk.Button(
                self.button_frame,
                text="Delete",
                command=self._on_delete if on_delete else lambda: None,
                state=tk.DISABLED
            )
            self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.move_up_button = ttk.Button(
                self.button_frame,
                text="Move Up",
                command=self._on_move_up if on_move_up else lambda: None,
                state=tk.DISABLED
            )
            self.move_up_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.move_down_button = ttk.Button(
                self.button_frame,
                text="Move Down",
                command=self._on_move_down if on_move_down else lambda: None,
                state=tk.DISABLED
            )
            self.move_down_button.pack(side=tk.LEFT)
            
            # Store the callbacks
            self._on_select_callback = on_select
            self._on_add_callback = on_add
            self._on_edit_callback = on_edit
            self._on_delete_callback = on_delete
            self._on_move_up_callback = on_move_up
            self._on_move_down_callback = on_move_down
            
            # Bind the selection event
            self.listbox.bind("<<ListboxSelect>>", self._on_selection_changed)
            
            # Store the action data for each item
            self._action_data = []
            
            self.logger.debug("ActionList component initialized")
        except Exception as e:
            error_msg = "Failed to create ActionList component"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ActionList", cause=e) from e
    
    def set_actions(self, actions: List[Dict[str, Any]]) -> None:
        """
        Set the list of actions to display.
        
        Args:
            actions: List of action data dictionaries
            
        Raises:
            UIError: If the actions cannot be set
        """
        try:
            # Clear the listbox
            self.listbox.delete(0, tk.END)
            
            # Store the action data
            self._action_data = actions
            
            # Add the actions
            for action in actions:
                # Format the action for display
                display_text = self._format_action_for_display(action)
                self.listbox.insert(tk.END, display_text)
            
            # Disable the buttons
            self._update_button_states()
            
            self.logger.debug(f"Set {len(actions)} actions in the list")
        except Exception as e:
            error_msg = "Failed to set actions in ActionList"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ActionList", cause=e) from e
    
    def get_selected_index(self) -> Optional[int]:
        """
        Get the index of the currently selected action.
        
        Returns:
            The selected action index, or None if no action is selected
        """
        try:
            # Get the selected index
            selected_indices = self.listbox.curselection()
            if not selected_indices:
                return None
            
            return selected_indices[0]
        except Exception as e:
            self.logger.error(f"Failed to get selected action index: {e}")
            return None
    
    def get_selected_action(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected action data.
        
        Returns:
            The selected action data, or None if no action is selected
        """
        try:
            # Get the selected index
            selected_index = self.get_selected_index()
            if selected_index is None:
                return None
            
            # Get the selected action data
            return self._action_data[selected_index]
        except Exception as e:
            self.logger.error(f"Failed to get selected action data: {e}")
            return None
    
    def select_action(self, index: int) -> bool:
        """
        Select an action by index.
        
        Args:
            index: The index of the action to select
            
        Returns:
            True if the action was found and selected, False otherwise
        """
        try:
            # Check if the index is valid
            if index < 0 or index >= len(self._action_data):
                return False
            
            # Select the action
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.see(index)
            
            # Update the button states
            self._update_button_states()
            
            # Call the selection callback
            if self._on_select_callback:
                self._on_select_callback(index)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to select action at index {index}: {e}")
            return False
    
    def update_action(self, index: int, action: Dict[str, Any]) -> bool:
        """
        Update an action at the specified index.
        
        Args:
            index: The index of the action to update
            action: The new action data
            
        Returns:
            True if the action was updated, False otherwise
        """
        try:
            # Check if the index is valid
            if index < 0 or index >= len(self._action_data):
                return False
            
            # Update the action data
            self._action_data[index] = action
            
            # Update the display
            display_text = self._format_action_for_display(action)
            self.listbox.delete(index)
            self.listbox.insert(index, display_text)
            
            # Reselect the action
            self.select_action(index)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update action at index {index}: {e}")
            return False
    
    def add_action(self, action: Dict[str, Any]) -> int:
        """
        Add a new action to the list.
        
        Args:
            action: The action data to add
            
        Returns:
            The index of the added action
            
        Raises:
            UIError: If the action cannot be added
        """
        try:
            # Add the action data
            self._action_data.append(action)
            
            # Add the action to the listbox
            display_text = self._format_action_for_display(action)
            self.listbox.insert(tk.END, display_text)
            
            # Select the new action
            new_index = len(self._action_data) - 1
            self.select_action(new_index)
            
            return new_index
        except Exception as e:
            error_msg = "Failed to add action to ActionList"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="ActionList", cause=e) from e
    
    def delete_action(self, index: int) -> bool:
        """
        Delete an action at the specified index.
        
        Args:
            index: The index of the action to delete
            
        Returns:
            True if the action was deleted, False otherwise
        """
        try:
            # Check if the index is valid
            if index < 0 or index >= len(self._action_data):
                return False
            
            # Delete the action data
            del self._action_data[index]
            
            # Delete the action from the listbox
            self.listbox.delete(index)
            
            # Select the next action if available
            if len(self._action_data) > 0:
                next_index = min(index, len(self._action_data) - 1)
                self.select_action(next_index)
            else:
                # No actions left, disable the buttons
                self._update_button_states()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete action at index {index}: {e}")
            return False
    
    def move_action_up(self, index: int) -> bool:
        """
        Move an action up in the list.
        
        Args:
            index: The index of the action to move
            
        Returns:
            True if the action was moved, False otherwise
        """
        try:
            # Check if the index is valid and the action can be moved up
            if index <= 0 or index >= len(self._action_data):
                return False
            
            # Swap the action data
            self._action_data[index], self._action_data[index - 1] = self._action_data[index - 1], self._action_data[index]
            
            # Update the display
            display_text1 = self._format_action_for_display(self._action_data[index - 1])
            display_text2 = self._format_action_for_display(self._action_data[index])
            self.listbox.delete(index - 1)
            self.listbox.insert(index - 1, display_text1)
            self.listbox.delete(index)
            self.listbox.insert(index, display_text2)
            
            # Select the moved action
            self.select_action(index - 1)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to move action up at index {index}: {e}")
            return False
    
    def move_action_down(self, index: int) -> bool:
        """
        Move an action down in the list.
        
        Args:
            index: The index of the action to move
            
        Returns:
            True if the action was moved, False otherwise
        """
        try:
            # Check if the index is valid and the action can be moved down
            if index < 0 or index >= len(self._action_data) - 1:
                return False
            
            # Swap the action data
            self._action_data[index], self._action_data[index + 1] = self._action_data[index + 1], self._action_data[index]
            
            # Update the display
            display_text1 = self._format_action_for_display(self._action_data[index])
            display_text2 = self._format_action_for_display(self._action_data[index + 1])
            self.listbox.delete(index)
            self.listbox.insert(index, display_text1)
            self.listbox.delete(index + 1)
            self.listbox.insert(index + 1, display_text2)
            
            # Select the moved action
            self.select_action(index + 1)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to move action down at index {index}: {e}")
            return False
    
    def _format_action_for_display(self, action: Dict[str, Any]) -> str:
        """
        Format an action for display in the listbox.
        
        Args:
            action: The action data to format
            
        Returns:
            A formatted string representation of the action
        """
        try:
            # Get the action type and name
            action_type = action.get("action_type", "Unknown")
            action_name = action.get("name", "Unnamed")
            
            # Format the action based on its type
            if action_type == "Navigate":
                url = action.get("url", "")
                return f"{action_name} ({action_type}): {url}"
            elif action_type == "Click":
                selector = action.get("selector", "")
                return f"{action_name} ({action_type}): {selector}"
            elif action_type == "Type":
                selector = action.get("selector", "")
                value_type = action.get("value_type", "")
                value_key = action.get("value_key", "")
                return f"{action_name} ({action_type}): {selector} - {value_type}:{value_key}"
            elif action_type == "Wait":
                duration = action.get("duration_seconds", "")
                return f"{action_name} ({action_type}): {duration}s"
            elif action_type == "Screenshot":
                file_path = action.get("file_path", "")
                return f"{action_name} ({action_type}): {file_path}"
            else:
                # Generic format for other action types
                return f"{action_name} ({action_type})"
        except Exception as e:
            self.logger.error(f"Failed to format action for display: {e}")
            return "Error formatting action"
    
    def _update_button_states(self) -> None:
        """Update the states of the buttons based on the current selection."""
        try:
            # Get the selected index
            selected_index = self.get_selected_index()
            
            # Update the button states
            if selected_index is not None:
                self.edit_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
                
                # Enable/disable move buttons based on position
                if selected_index > 0:
                    self.move_up_button.config(state=tk.NORMAL)
                else:
                    self.move_up_button.config(state=tk.DISABLED)
                
                if selected_index < len(self._action_data) - 1:
                    self.move_down_button.config(state=tk.NORMAL)
                else:
                    self.move_down_button.config(state=tk.DISABLED)
            else:
                self.edit_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)
                self.move_up_button.config(state=tk.DISABLED)
                self.move_down_button.config(state=tk.DISABLED)
        except Exception as e:
            self.logger.error(f"Failed to update button states: {e}")
    
    def _on_selection_changed(self, event: tk.Event) -> None:
        """
        Handle selection changes in the listbox.
        
        Args:
            event: The event that triggered this callback
        """
        try:
            # Update the button states
            self._update_button_states()
            
            # Call the selection callback
            selected_index = self.get_selected_index()
            if selected_index is not None and self._on_select_callback:
                self._on_select_callback(selected_index)
        except Exception as e:
            self.logger.error(f"Error handling selection change: {e}")
    
    def _on_add(self) -> None:
        """Handle clicks on the add button."""
        try:
            if self._on_add_callback:
                self._on_add_callback()
        except Exception as e:
            self.logger.error(f"Error handling add button click: {e}")
    
    def _on_edit(self) -> None:
        """Handle clicks on the edit button."""
        try:
            selected_index = self.get_selected_index()
            if selected_index is not None and self._on_edit_callback:
                self._on_edit_callback(selected_index)
        except Exception as e:
            self.logger.error(f"Error handling edit button click: {e}")
    
    def _on_delete(self) -> None:
        """Handle clicks on the delete button."""
        try:
            selected_index = self.get_selected_index()
            if selected_index is not None and self._on_delete_callback:
                self._on_delete_callback(selected_index)
        except Exception as e:
            self.logger.error(f"Error handling delete button click: {e}")
    
    def _on_move_up(self) -> None:
        """Handle clicks on the move up button."""
        try:
            selected_index = self.get_selected_index()
            if selected_index is not None and selected_index > 0 and self._on_move_up_callback:
                self._on_move_up_callback(selected_index)
        except Exception as e:
            self.logger.error(f"Error handling move up button click: {e}")
    
    def _on_move_down(self) -> None:
        """Handle clicks on the move down button."""
        try:
            selected_index = self.get_selected_index()
            if (selected_index is not None and 
                selected_index < len(self._action_data) - 1 and 
                self._on_move_down_callback):
                self._on_move_down_callback(selected_index)
        except Exception as e:
            self.logger.error(f"Error handling move down button click: {e}")
