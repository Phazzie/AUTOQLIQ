"""Test script for the enhanced UI integration."""

import tkinter as tk
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import required modules
from src.ui.views.workflow_editor_view_enhanced import WorkflowEditorViewEnhanced
from src.ui.interfaces.presenter import IWorkflowEditorPresenter

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


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
        self.logger.debug(f"View set: {type(view).__name__}")

    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        return list(self._workflows.keys())

    def load_workflow(self, name: str) -> None:
        """Load the specified workflow into the editor view."""
        if name in self._workflows:
            self._current_workflow_name = name
            self._current_actions = self._workflows[name].copy()
            self.logger.debug(f"Loaded workflow: {name} with {len(self._current_actions)} actions")
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning(f"Workflow not found: {name}")

    def save_workflow(self, name: Optional[str] = None, actions_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save the currently edited workflow actions under the given name."""
        if name is None:
            name = self._current_workflow_name
        if actions_data is None:
            actions_data = self._current_actions

        if name:
            self._workflows[name] = actions_data.copy()
            self.logger.debug(f"Saved workflow: {name} with {len(actions_data)} actions")
        else:
            self.logger.warning("Cannot save workflow: No name provided")

    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow."""
        self._current_workflow_name = name
        self._current_actions = []
        self._workflows[name] = []
        self.logger.debug(f"Created new workflow: {name}")
        if self._view:
            self._view.set_action_data_list([])

    def delete_workflow(self, name: str) -> None:
        """Delete the specified workflow."""
        if name in self._workflows:
            del self._workflows[name]
            self.logger.debug(f"Deleted workflow: {name}")
            if name == self._current_workflow_name:
                self._current_workflow_name = None
                self._current_actions = []
                if self._view:
                    self._view.set_action_data_list([])
        else:
            self.logger.warning(f"Cannot delete workflow: {name} not found")

    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action to the current workflow."""
        if self._current_workflow_name:
            self._current_actions.append(action_data)
            self.logger.debug(f"Added action: {action_data.get('type')} to {self._current_workflow_name}")
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning("Cannot add action: No workflow selected")

    def insert_action(self, position: int, action_data: Dict[str, Any]) -> None:
        """Insert a new action at the specified position."""
        if self._current_workflow_name:
            if 0 <= position <= len(self._current_actions):
                self._current_actions.insert(position, action_data)
                self.logger.debug(f"Inserted action: {action_data.get('type')} at position {position}")
                if self._view:
                    self._view.set_action_data_list(self._current_actions)
            else:
                self.logger.warning(f"Invalid position for insertion: {position}")
        else:
            self.logger.warning("Cannot insert action: No workflow selected")

    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update the action at the specified index."""
        if self._current_workflow_name and 0 <= index < len(self._current_actions):
            self._current_actions[index] = action_data
            self.logger.debug(f"Updated action at index {index}")
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning(f"Cannot update action: Invalid index {index} or no workflow selected")

    def delete_action(self, index: int) -> None:
        """Delete the action at the specified index."""
        if self._current_workflow_name and 0 <= index < len(self._current_actions):
            del self._current_actions[index]
            self.logger.debug(f"Deleted action at index {index}")
            if self._view:
                self._view.set_action_data_list(self._current_actions)
        else:
            self.logger.warning(f"Cannot delete action: Invalid index {index} or no workflow selected")

    def move_action(self, from_index: int, to_index: int) -> None:
        """Move an action from one position to another."""
        if self._current_workflow_name:
            if 0 <= from_index < len(self._current_actions) and 0 <= to_index < len(self._current_actions):
                action = self._current_actions.pop(from_index)
                self._current_actions.insert(to_index, action)
                self.logger.debug(f"Moved action from index {from_index} to {to_index}")
                if self._view:
                    self._view.set_action_data_list(self._current_actions)
            else:
                self.logger.warning(f"Invalid indices for move: from={from_index}, to={to_index}")
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


class TestEnhancedUIIntegration:
    """Test the integration of the enhanced UI with the presenter."""

    def __init__(self, root):
        """Initialize the test application."""
        self.root = root
        self.root.title("AutoQliq - Enhanced UI Integration Test")
        self.root.geometry("1000x700")

        # Create a frame for the components
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the mock presenter
        self.presenter = MockWorkflowEditorPresenter()

        # Create the enhanced view
        self.view = WorkflowEditorViewEnhanced(self.frame, self.presenter)

        # Set the view in the presenter
        self.presenter.set_view(self.view)

        # Add test buttons
        self.add_test_buttons()

    def add_test_buttons(self):
        """Add buttons to test the integration."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Create a new workflow
        tk.Button(
            button_frame,
            text="Create Test Workflow",
            command=self.create_test_workflow
        ).pack(side=tk.LEFT, padx=5)

        # Add actions
        tk.Button(
            button_frame,
            text="Add Test Actions",
            command=self.add_test_actions
        ).pack(side=tk.LEFT, padx=5)

        # Test insert action
        tk.Button(
            button_frame,
            text="Insert Action at Position 1",
            command=self.insert_test_action
        ).pack(side=tk.LEFT, padx=5)

        # Test move action
        tk.Button(
            button_frame,
            text="Move Action 0 to 2",
            command=self.move_test_action
        ).pack(side=tk.LEFT, padx=5)

    def create_test_workflow(self):
        """Create a test workflow."""
        self.presenter.create_new_workflow("Test Workflow")

    def add_test_actions(self):
        """Add test actions to the workflow."""
        # Add a Navigate action
        self.presenter.add_action({
            "type": "Navigate",
            "name": "Navigate to Example",
            "url": "https://example.com"
        })

        # Add a Click action
        self.presenter.add_action({
            "type": "Click",
            "name": "Click Button",
            "selector": "#button1"
        })

        # Add a Type action
        self.presenter.add_action({
            "type": "Type",
            "name": "Type Text",
            "selector": "#input1",
            "value_key": "test"
        })

    def insert_test_action(self):
        """Insert a test action at position 1."""
        self.presenter.insert_action(1, {
            "type": "Wait",
            "name": "Wait 5 Seconds",
            "duration_seconds": "5"
        })

    def move_test_action(self):
        """Move an action from position 0 to position 2."""
        self.presenter.move_action(0, 2)


def main():
    """Run the enhanced UI integration test."""
    # Create the root window
    root = tk.Tk()

    # Create the test application
    TestEnhancedUIIntegration(root)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
