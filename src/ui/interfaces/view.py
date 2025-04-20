"""View interfaces for AutoQliq UI.

This module provides interfaces for views in the UI layer,
defining the contract between presenters and views.
"""

import abc
from typing import Any, Dict, List, Optional, Callable

# Assuming IAction is defined in core interfaces
from src.core.interfaces import IAction


class IView(abc.ABC):
    """Base interface for views."""

    @abc.abstractmethod
    def display_error(self, title: str, message: str) -> None:
        """Display an error message to the user."""
        pass

    @abc.abstractmethod
    def display_message(self, title: str, message: str) -> None:
        """Display an informational message to the user."""
        pass

    @abc.abstractmethod
    def confirm_action(self, title: str, message: str) -> bool:
        """Ask the user for confirmation."""
        pass

    @abc.abstractmethod
    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
         """Clear or reset the view's state."""
         pass

    @abc.abstractmethod
    def show_loading(self, is_loading: bool) -> None:
        """Show or hide a loading indicator."""
        pass


class IMainView(IView):
    """Interface for the main application view."""

    @abc.abstractmethod
    def set_title(self, title: str) -> None:
        """Set the window title."""
        pass

    @abc.abstractmethod
    def create_menu(self) -> None:
        """Create the application menu."""
        pass

    @abc.abstractmethod
    def bind_menu_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind menu item handlers."""
        pass


class IWorkflowEditorView(IView):
    """Interface for the Workflow Editor View."""

    @abc.abstractmethod
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the list of available workflows."""
        pass

    @abc.abstractmethod
    def set_action_list(self, actions_display: List[str]) -> None:
        """Display the actions for the currently loaded workflow."""
        pass

    @abc.abstractmethod
    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the workflow currently selected in the list."""
        pass

    @abc.abstractmethod
    def get_selected_action_index(self) -> Optional[int]:
         """Get the index of the action currently selected in the list."""
         pass

    @abc.abstractmethod
    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
         """Open a dialog/form to edit or add an action. Returns new data or None if cancelled."""
         pass

    @abc.abstractmethod
    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
         """Prompt the user to enter a name for a new workflow."""
         pass

    @abc.abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass


class IWorkflowRunnerView(IView):
    """Interface for the Workflow Runner View."""

    @abc.abstractmethod
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the list of available workflows."""
        pass

    @abc.abstractmethod
    def set_credential_list(self, credential_names: List[str]) -> None:
        """Populate the list of available credentials."""
        pass

    @abc.abstractmethod
    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the workflow selected by the user."""
        pass

    @abc.abstractmethod
    def get_selected_credential_name(self) -> Optional[str]:
        """Get the name of the credential selected by the user."""
        pass

    @abc.abstractmethod
    def log_message(self, message: str) -> None:
        """Append a message to the execution log display."""
        pass

    @abc.abstractmethod
    def clear_log(self) -> None:
        """Clear the execution log display."""
        pass

    @abc.abstractmethod
    def set_running_state(self, is_running: bool) -> None:
        """Update the UI elements based on whether a workflow is running (e.g., disable Run, enable Stop)."""
        pass

    @abc.abstractmethod
    def display_execution_status(self, status: Dict[str, Any]) -> None:
        """Display the current execution status."""
        pass

    @abc.abstractmethod
    def display_execution_results(self, results: List[Dict[str, Any]]) -> None:
        """Display the execution results."""
        pass

    @abc.abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass

    # Optional progress indication methods
    @abc.abstractmethod
    def start_progress(self) -> None:
        """Start a progress indicator (e.g., indeterminate progress bar)."""
        pass

    @abc.abstractmethod
    def stop_progress(self) -> None:
        """Stop the progress indicator."""
        pass

    @abc.abstractmethod
    def set_progress(self, value: float) -> None:
        """Set the value of a determinate progress indicator (0-100)."""
        pass


class ISettingsView(IView):
    """Interface for the settings view."""

    @abc.abstractmethod
    def display_settings(self, settings: Dict[str, Any]) -> None:
        """Display the current settings."""
        pass

    @abc.abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass

    @abc.abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings from the UI."""
        pass