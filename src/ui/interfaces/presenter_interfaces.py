"""Presenter interfaces for AutoQliq.

This module defines the interfaces for presenters in the MVP architecture.
These interfaces establish contracts for presenter implementations and facilitate
testing through mocking.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class IPresenter(ABC):
    """Base interface for all presenters."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the presenter and prepare the view."""
        pass

class IMainPresenter(IPresenter):
    """Interface for the main application presenter."""
    
    @abstractmethod
    def on_exit(self) -> None:
        """Handle application exit."""
        pass
    
    @abstractmethod
    def on_about(self) -> None:
        """Show the about dialog."""
        pass
    
    @abstractmethod
    def on_open_credential_manager(self) -> None:
        """Open the credential manager dialog."""
        pass
    
    @abstractmethod
    def on_open_settings(self) -> None:
        """Open the settings dialog."""
        pass

class IWorkflowEditorPresenter(IPresenter):
    """Interface for the workflow editor presenter."""
    
    @abstractmethod
    def load_workflows(self) -> None:
        """Load and display available workflows."""
        pass
    
    @abstractmethod
    def on_workflow_selected(self, workflow_name: str) -> None:
        """Handle workflow selection."""
        pass
    
    @abstractmethod
    def on_create_workflow(self) -> None:
        """Handle create workflow request."""
        pass
    
    @abstractmethod
    def on_delete_workflow(self) -> None:
        """Handle delete workflow request."""
        pass
    
    @abstractmethod
    def on_add_action(self) -> None:
        """Handle add action request."""
        pass
    
    @abstractmethod
    def on_edit_action(self, action_index: int) -> None:
        """Handle edit action request."""
        pass
    
    @abstractmethod
    def on_delete_action(self, action_index: int) -> None:
        """Handle delete action request."""
        pass
    
    @abstractmethod
    def on_move_action_up(self, action_index: int) -> None:
        """Handle move action up request."""
        pass
    
    @abstractmethod
    def on_move_action_down(self, action_index: int) -> None:
        """Handle move action down request."""
        pass
    
    @abstractmethod
    def on_save_workflow(self) -> None:
        """Handle save workflow request."""
        pass

class IWorkflowRunnerPresenter(IPresenter):
    """Interface for the workflow runner presenter."""
    
    @abstractmethod
    def load_workflows(self) -> None:
        """Load and display available workflows."""
        pass
    
    @abstractmethod
    def load_credentials(self) -> None:
        """Load and display available credentials."""
        pass
    
    @abstractmethod
    def on_run_workflow(self) -> None:
        """Handle run workflow request."""
        pass
    
    @abstractmethod
    def on_stop_workflow(self) -> None:
        """Handle stop workflow request."""
        pass
    
    @abstractmethod
    def update_execution_status(self) -> None:
        """Update the execution status display."""
        pass

class ISettingsPresenter(IPresenter):
    """Interface for the settings presenter."""
    
    @abstractmethod
    def load_settings(self) -> None:
        """Load and display current settings."""
        pass
    
    @abstractmethod
    def on_save_settings(self) -> None:
        """Handle save settings request."""
        pass
    
    @abstractmethod
    def on_reset_settings(self) -> None:
        """Handle reset settings to defaults request."""
        pass
