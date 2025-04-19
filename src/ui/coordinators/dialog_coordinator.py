"""Coordinator for dialog interactions."""

import logging
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from typing import Dict, Any, Optional, List, Tuple, Union

from src.core.exceptions import UIError

logger = logging.getLogger(__name__)

class DialogCoordinator:
    """Coordinates dialog interactions for the UI.

    This class abstracts dialog creation and interaction, providing a clean interface
    for presenters to show dialogs without directly coupling to specific dialog implementations.

    Responsibilities:
    1. Create and show dialog windows
    2. Handle dialog-related errors
    3. Provide a consistent interface for all dialog interactions
    4. Abstract away specific dialog implementation details
    """

    def __init__(self):
        """Initialize the dialog coordinator."""
        self.logger = logging.getLogger(__name__)

    def show_action_editor(self, parent: tk.Widget, initial_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Show the action editor dialog.

        Args:
            parent: The parent widget
            initial_data: Optional initial data for editing an existing action

        Returns:
            The action data if OK was pressed, None if cancelled

        Raises:
            UIError: If there was an error showing the dialog
        """
        try:
            from src.ui.dialogs.action_editor_dialog import ActionEditorDialog
            dialog = ActionEditorDialog(parent, initial_data=initial_data)
            return dialog.show()
        except Exception as e:
            self.logger.error(f"Failed to display action editor: {e}", exc_info=True)
            raise UIError(f"Failed to display action editor: {e}") from e

    def show_action_selector(self, parent: tk.Widget) -> Optional[str]:
        """Show the action type selector dialog.

        Args:
            parent: The parent widget

        Returns:
            The selected action type if OK was pressed, None if cancelled

        Raises:
            UIError: If there was an error showing the dialog
        """
        try:
            from src.ui.dialogs.action_selection_dialog import ActionSelectionDialog
            dialog = ActionSelectionDialog(parent)
            return dialog.show()
        except Exception as e:
            self.logger.error(f"Failed to display action selector: {e}", exc_info=True)
            raise UIError(f"Failed to display action selector: {e}") from e

    def prompt_for_text(self, parent: tk.Widget, title: str, prompt: str,
                       initial_value: str = "") -> Optional[str]:
        """Show a simple text input dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            prompt: The prompt text
            initial_value: Optional initial value for the input field

        Returns:
            The entered text if OK was pressed, None if cancelled
        """
        return simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=parent)

    def confirm_action(self, parent: tk.Widget, title: str, message: str) -> bool:
        """Show a confirmation dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            message: The confirmation message

        Returns:
            True if Yes was pressed, False if No was pressed
        """
        return messagebox.askyesno(title, message, parent=parent)

    def show_error(self, parent: tk.Widget, title: str, message: str) -> None:
        """Show an error dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            message: The error message
        """
        messagebox.showerror(title, message, parent=parent)

    def show_info(self, parent: tk.Widget, title: str, message: str) -> None:
        """Show an information dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            message: The information message
        """
        messagebox.showinfo(title, message, parent=parent)

    def show_warning(self, parent: tk.Widget, title: str, message: str) -> None:
        """Show a warning dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            message: The warning message
        """
        messagebox.showwarning(title, message, parent=parent)

    def browse_for_file(self, parent: tk.Widget, title: str = "Select File",
                        initial_dir: str = ".", file_types: Optional[List[Tuple[str, str]]] = None) -> Optional[str]:
        """Show a file open dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            initial_dir: The initial directory to show
            file_types: List of file type tuples (description, pattern)

        Returns:
            The selected file path or None if cancelled
        """
        return filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir,
            filetypes=file_types or [("All Files", "*.*")],
            parent=parent
        ) or None  # Convert empty string to None

    def browse_for_directory(self, parent: tk.Widget, title: str = "Select Directory",
                           initial_dir: str = ".") -> Optional[str]:
        """Show a directory selection dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            initial_dir: The initial directory to show

        Returns:
            The selected directory path or None if cancelled
        """
        return filedialog.askdirectory(
            title=title,
            initialdir=initial_dir,
            parent=parent
        ) or None  # Convert empty string to None

    def browse_for_save_file(self, parent: tk.Widget, title: str = "Save As",
                            initial_dir: str = ".", initial_file: str = "",
                            file_types: Optional[List[Tuple[str, str]]] = None) -> Optional[str]:
        """Show a file save dialog.

        Args:
            parent: The parent widget
            title: The dialog title
            initial_dir: The initial directory to show
            initial_file: The initial filename
            file_types: List of file type tuples (description, pattern)

        Returns:
            The selected file path or None if cancelled
        """
        return filedialog.asksaveasfilename(
            title=title,
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=file_types or [("All Files", "*.*")],
            parent=parent
        ) or None  # Convert empty string to None
