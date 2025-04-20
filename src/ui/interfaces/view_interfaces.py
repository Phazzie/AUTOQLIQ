"""View interfaces for AutoQliq.

This module defines the interfaces for views in the MVP architecture.
These interfaces establish contracts for view implementations and facilitate
testing through mocking.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

class IView(ABC):
    """Base interface for all views."""
    
    @abstractmethod
    def show_error(self, message: str) -> None:
        """Display an error message to the user."""
        pass
    
    @abstractmethod
    def show_info(self, message: str) -> None:
        """Display an informational message to the user."""
        pass
    
    @abstractmethod
    def show_loading(self, is_loading: bool) -> None:
        """Show or hide a loading indicator."""
        pass

class IMainView(IView):
    """Interface for the main application view."""
    
    @abstractmethod
    def set_status(self, status: str) -> None:
        """Set the status message in the status bar."""
        pass
    
    @abstractmethod
    def set_title(self, title: str) -> None:
        """Set the window title."""
        pass
    
    @abstractmethod
    def create_menu(self) -> None:
        """Create the application menu."""
        pass
    
    @abstractmethod
    def bind_menu_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind menu item handlers."""
        pass

class IWorkflowEditorView(IView):
    """Interface for the workflow editor view."""
    
    @abstractmethod
    def display_workflows(self, workflows: List[str]) -> None:
        """Display a list of available workflows."""
        pass
    
    @abstractmethod
    def display_actions(self, actions: List[Dict[str, Any]]) -> None:
        """Display the actions in the current workflow."""
        pass
    
    @abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass
    
    @abstractmethod
    def get_selected_workflow(self) -> Optional[str]:
        """Get the currently selected workflow."""
        pass
    
    @abstractmethod
    def get_selected_action(self) -> Optional[int]:
        """Get the index of the currently selected action."""
        pass

class IWorkflowRunnerView(IView):
    """Interface for the workflow runner view."""
    
    @abstractmethod
    def display_workflows(self, workflows: List[str]) -> None:
        """Display a list of available workflows."""
        pass
    
    @abstractmethod
    def display_credentials(self, credentials: List[str]) -> None:
        """Display a list of available credentials."""
        pass
    
    @abstractmethod
    def display_execution_status(self, status: Dict[str, Any]) -> None:
        """Display the current execution status."""
        pass
    
    @abstractmethod
    def display_execution_results(self, results: List[Dict[str, Any]]) -> None:
        """Display the execution results."""
        pass
    
    @abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass
    
    @abstractmethod
    def get_selected_workflow(self) -> Optional[str]:
        """Get the currently selected workflow."""
        pass
    
    @abstractmethod
    def get_selected_credential(self) -> Optional[str]:
        """Get the currently selected credential."""
        pass

class ISettingsView(IView):
    """Interface for the settings view."""
    
    @abstractmethod
    def display_settings(self, settings: Dict[str, Any]) -> None:
        """Display the current settings."""
        pass
    
    @abstractmethod
    def bind_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Bind event handlers for UI elements."""
        pass
    
    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings from the UI."""
        pass
