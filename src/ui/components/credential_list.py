"""Credential list component for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Optional, Callable, Any

from src.core.exceptions import UIError
from src.ui.components.ui_component import UIComponent

logger = logging.getLogger(__name__)


class CredentialList(UIComponent):
    """
    A component for displaying and selecting credentials.
    
    This component provides a listbox with a scrollbar for displaying credentials,
    along with buttons for common operations like creating, editing, and deleting credentials.
    
    Attributes:
        frame: The main frame containing all widgets
        listbox: The listbox for displaying credentials
        scrollbar: The scrollbar for the listbox
        button_frame: The frame containing the buttons
        create_button: Button for creating a new credential
        edit_button: Button for editing the selected credential
        delete_button: Button for deleting the selected credential
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        on_create: Optional[Callable[[], None]] = None,
        on_edit: Optional[Callable[[str], None]] = None,
        on_delete: Optional[Callable[[str], None]] = None,
        height: int = 10,
        width: int = 30
    ):
        """
        Initialize a CredentialList component.
        
        Args:
            parent: The parent widget
            on_select: Callback when a credential is selected
            on_create: Callback when the create button is clicked
            on_edit: Callback when the edit button is clicked
            on_delete: Callback when the delete button is clicked
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
            label = ttk.Label(self.frame, text="Credentials:")
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
            self.create_button = ttk.Button(
                self.button_frame,
                text="Create",
                command=self._on_create if on_create else lambda: None
            )
            self.create_button.pack(side=tk.LEFT, padx=(0, 5))
            
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
            self.delete_button.pack(side=tk.LEFT)
            
            # Store the callbacks
            self._on_select_callback = on_select
            self._on_create_callback = on_create
            self._on_edit_callback = on_edit
            self._on_delete_callback = on_delete
            
            # Bind the selection event
            self.listbox.bind("<<ListboxSelect>>", self._on_selection_changed)
            
            self.logger.debug("CredentialList component initialized")
        except Exception as e:
            error_msg = "Failed to create CredentialList component"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="CredentialList", cause=e) from e
    
    def set_credentials(self, credentials: List[str]) -> None:
        """
        Set the list of credentials to display.
        
        Args:
            credentials: List of credential names
            
        Raises:
            UIError: If the credentials cannot be set
        """
        try:
            # Clear the listbox
            self.listbox.delete(0, tk.END)
            
            # Add the credentials
            for credential in credentials:
                self.listbox.insert(tk.END, credential)
            
            # Disable the edit and delete buttons
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            
            self.logger.debug(f"Set {len(credentials)} credentials in the list")
        except Exception as e:
            error_msg = "Failed to set credentials in CredentialList"
            self.logger.exception(error_msg)
            raise UIError(error_msg, component_name="CredentialList", cause=e) from e
    
    def get_selected_credential(self) -> Optional[str]:
        """
        Get the currently selected credential.
        
        Returns:
            The selected credential name, or None if no credential is selected
        """
        try:
            # Get the selected index
            selected_indices = self.listbox.curselection()
            if not selected_indices:
                return None
            
            # Get the selected credential
            selected_index = selected_indices[0]
            return self.listbox.get(selected_index)
        except Exception as e:
            self.logger.error(f"Failed to get selected credential: {e}")
            return None
    
    def select_credential(self, credential_name: str) -> bool:
        """
        Select a credential by name.
        
        Args:
            credential_name: The name of the credential to select
            
        Returns:
            True if the credential was found and selected, False otherwise
        """
        try:
            # Find the credential in the list
            for i in range(self.listbox.size()):
                if self.listbox.get(i) == credential_name:
                    # Select the credential
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(i)
                    self.listbox.see(i)
                    
                    # Enable the edit and delete buttons
                    self.edit_button.config(state=tk.NORMAL)
                    self.delete_button.config(state=tk.NORMAL)
                    
                    # Call the selection callback
                    if self._on_select_callback:
                        self._on_select_callback(credential_name)
                    
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to select credential '{credential_name}': {e}")
            return False
    
    def _on_selection_changed(self, event: tk.Event) -> None:
        """
        Handle selection changes in the listbox.
        
        Args:
            event: The event that triggered this callback
        """
        try:
            # Get the selected credential
            selected_credential = self.get_selected_credential()
            
            # Update the button states
            if selected_credential:
                self.edit_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
            else:
                self.edit_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)
            
            # Call the selection callback
            if selected_credential and self._on_select_callback:
                self._on_select_callback(selected_credential)
        except Exception as e:
            self.logger.error(f"Error handling selection change: {e}")
    
    def _on_create(self) -> None:
        """Handle clicks on the create button."""
        try:
            if self._on_create_callback:
                self._on_create_callback()
        except Exception as e:
            self.logger.error(f"Error handling create button click: {e}")
    
    def _on_edit(self) -> None:
        """Handle clicks on the edit button."""
        try:
            selected_credential = self.get_selected_credential()
            if selected_credential and self._on_edit_callback:
                self._on_edit_callback(selected_credential)
        except Exception as e:
            self.logger.error(f"Error handling edit button click: {e}")
    
    def _on_delete(self) -> None:
        """Handle clicks on the delete button."""
        try:
            selected_credential = self.get_selected_credential()
            if selected_credential and self._on_delete_callback:
                self._on_delete_callback(selected_credential)
        except Exception as e:
            self.logger.error(f"Error handling delete button click: {e}")
