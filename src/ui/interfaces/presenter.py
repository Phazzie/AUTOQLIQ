"""Presenter interfaces for AutoQliq UI.

This module provides interfaces for presenters in the UI layer,
defining the contract between views and presenters.
"""

import abc
from typing import Any, List, Optional, Dict

# Assuming IAction is defined in core interfaces
from src.core.interfaces import IAction


class IPresenter(abc.ABC):
    """Base interface for presenters."""

    @abc.abstractmethod
    def set_view(self, view: Any) -> None:
        """Set the view associated with this presenter.

        Args:
            view: The view instance.
        """
        pass

    @abc.abstractmethod
    def initialize_view(self) -> None:
        """Initialize the associated view with necessary data."""
        pass


class IWorkflowEditorPresenter(IPresenter):
    """Interface for the Workflow Editor Presenter."""

    @abc.abstractmethod
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        pass

    @abc.abstractmethod
    def load_workflow(self, name: str) -> None:
        """Load the specified workflow into the editor view."""
        pass

    @abc.abstractmethod
    def save_workflow(self, name: str, actions: List[Dict[str, Any]]) -> None:
        """Save the currently edited workflow actions under the given name."""
        pass

    @abc.abstractmethod
    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow."""
        pass

    @abc.abstractmethod
    def delete_workflow(self, name: str) -> None:
        """Delete the specified workflow."""
        pass

    @abc.abstractmethod
    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action (represented by data) to the current workflow."""
        pass

    @abc.abstractmethod
    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update the action at the specified index with new data."""
        pass

    @abc.abstractmethod
    def delete_action(self, index: int) -> None:
        """Delete the action at the specified index."""
        pass

    @abc.abstractmethod
    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
         """Get the data dictionary for the action at the specified index."""
         pass


class IWorkflowRunnerPresenter(IPresenter):
    """Interface for the Workflow Runner Presenter."""

    @abc.abstractmethod
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        pass

    @abc.abstractmethod
    def get_credential_list(self) -> List[str]:
        """Get the list of available credential names."""
        pass

    @abc.abstractmethod
    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Start executing the specified workflow using the selected credential."""
        pass

    @abc.abstractmethod
    def stop_workflow(self) -> None:
        """Stop the currently running workflow execution (if any)."""
        pass