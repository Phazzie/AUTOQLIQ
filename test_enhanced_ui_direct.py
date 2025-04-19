"""Test script for the enhanced UI components directly."""

import tkinter as tk
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import required modules
from src.ui.views.workflow_editor_view_enhanced import WorkflowEditorViewEnhanced
from src.ui.interfaces.presenter import IWorkflowEditorPresenter


# Create a mock presenter that implements the IWorkflowEditorPresenter interface
class MockWorkflowEditorPresenter(IWorkflowEditorPresenter):
    """Mock implementation of IWorkflowEditorPresenter for testing."""

    def __init__(self):
        """Initialize the mock presenter."""
        self.logger = logging.getLogger("MockPresenter")
        self._view = None
        self._current_workflow_name = None
        self._current_actions = []
        self._workflows = {}

    def set_view(self, view):
        """Set the view component."""
        self._view = view
        self.logger.debug("View set: %s", type(view).__name__)

    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        return list(self._workflows.keys())

    def load_workflow(self, name: str) -> None:
        """Load the specified workflow into the editor view."""
        if name in self._workflows:
            self._current_workflow_name = name
            self._current_actions = self._workflows[name].copy()
            self.logger.debug("Loaded workflow: %s with %d actions", name, len(self._current_actions))
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning("Workflow not found: %s", name)

    def save_workflow(self, name: Optional[str] = None, actions_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save the currently edited workflow actions under the given name."""
        if name is None:
            name = self._current_workflow_name
        if actions_data is None:
            actions_data = self._current_actions

        if name:
            self._workflows[name] = actions_data.copy()
            self.logger.debug("Saved workflow: %s with %d actions", name, len(actions_data))
        else:
            self.logger.warning("Cannot save workflow: No name provided")

    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow."""
        self._current_workflow_name = name
        self._current_actions = []
        self._workflows[name] = []
        self.logger.debug("Created new workflow: %s", name)
        if self._view:
            # Update the workflow list to include the new workflow
            self._view.set_workflow_list(self.get_workflow_list())
            # Select the new workflow in the list
            if hasattr(self._view, 'workflow_list_widget'):
                workflows = self.get_workflow_list()
                if name in workflows:
                    index = workflows.index(name)
                    self._view.workflow_list_widget.selection_clear(0, tk.END)
                    self._view.workflow_list_widget.selection_set(index)
                    self._view.workflow_list_widget.see(index)
                    # Trigger the selection event
                    self._view.workflow_list_widget.event_generate('<<ListboxSelect>>')
            # Update the action list to show an empty list
            self._view.set_action_data_list([])

    def delete_workflow(self, name: str) -> None:
        """Delete the specified workflow."""
        if name in self._workflows:
            del self._workflows[name]
            self.logger.debug("Deleted workflow: %s", name)
            if name == self._current_workflow_name:
                self._current_workflow_name = None
                self._current_actions = []
                if self._view:
                    self._view.set_action_data_list([])
        else:
            self.logger.warning("Cannot delete workflow: %s not found", name)

    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action to the current workflow."""
        if self._current_workflow_name:
            self._current_actions.append(action_data)
            self.logger.debug("Added action: %s to %s", action_data.get('type'), self._current_workflow_name)
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning("Cannot add action: No workflow selected")

    def insert_action(self, position: int, action_data: Dict[str, Any]) -> None:
        """Insert a new action at the specified position."""
        if self._current_workflow_name:
            if 0 <= position <= len(self._current_actions):
                self._current_actions.insert(position, action_data)
                self.logger.debug("Inserted action: %s at position %d", action_data.get('type'), position)
                if self._view:
                    self._view.set_action_data_list(self._current_actions)
            else:
                self.logger.warning("Invalid position for insertion: %d", position)
        else:
            self.logger.warning("Cannot insert action: No workflow selected")

    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update the action at the specified index."""
        if self._current_workflow_name and 0 <= index < len(self._current_actions):
            self._current_actions[index] = action_data
            self.logger.debug("Updated action at index %d", index)
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning("Cannot update action: Invalid index %d or no workflow selected", index)

    def delete_action(self, index: int) -> None:
        """Delete the action at the specified index."""
        if self._current_workflow_name and 0 <= index < len(self._current_actions):
            del self._current_actions[index]
            self.logger.debug("Deleted action at index %d", index)
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning("Cannot delete action: Invalid index %d or no workflow selected", index)

    def move_action(self, from_index: int, to_index: int) -> None:
        """Move an action from one position to another."""
        if self._current_workflow_name:
            if 0 <= from_index < len(self._current_actions) and 0 <= to_index < len(self._current_actions):
                action = self._current_actions.pop(from_index)
                self._current_actions.insert(to_index, action)
                self.logger.debug("Moved action from index %d to %d", from_index, to_index)
                if self._view:
                    self._view.set_action_data_list(self._current_actions)
            else:
                self.logger.warning("Invalid indices for move: from=%d, to=%d", from_index, to_index)
        else:
            self.logger.warning("Cannot move action: No workflow selected")

    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
        """Get the data dictionary for the action at the specified index."""
        if self._current_workflow_name and 0 <= index < len(self._current_actions):
            return self._current_actions[index]
        return None

    def get_all_actions_data(self) -> List[Dict[str, Any]]:
        """Get data dictionaries for all actions in the current workflow."""
        return self._current_actions.copy()

    def initialize_view(self) -> None:
        """Initialize the view with data."""
        self.logger.debug("Initializing view")
        if self._view:
            # Update the workflow list
            self._view.set_workflow_list(self.get_workflow_list())
            # Update the action list if a workflow is loaded
            if self._current_workflow_name and self._current_actions:
                self._view.set_action_data_list(self._current_actions)


def main():
    """Main entry point for the test application."""
    # Create the root window
    root = tk.Tk()
    root.title("AutoQliq - Enhanced UI Direct Test")
    root.geometry("1000x700")

    # Create the mock presenter
    presenter = MockWorkflowEditorPresenter()

    # Create the enhanced view
    view = WorkflowEditorViewEnhanced(root, presenter)

    # Set the view in the presenter
    presenter.set_view(view)

    # Create some test workflows
    presenter.create_new_workflow("Test Workflow 1")

    # Add actions to Test Workflow 1
    workflow1_actions = [
        {
            "type": "Navigate",
            "name": "Navigate to Example",
            "url": "https://example.com"
        },
        {
            "type": "Click",
            "name": "Click Button",
            "selector": "#button1"
        }
    ]

    # Save the actions to the workflow
    presenter._workflows["Test Workflow 1"] = workflow1_actions

    # Create another test workflow
    presenter.create_new_workflow("Test Workflow 2")

    # Add actions to Test Workflow 2
    workflow2_actions = [
        {
            "type": "Type",
            "name": "Type Text",
            "selector": "#input1",
            "value_key": "test"
        }
    ]

    # Save the actions to the workflow
    presenter._workflows["Test Workflow 2"] = workflow2_actions

    # Load the first workflow
    presenter.load_workflow("Test Workflow 1")

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
