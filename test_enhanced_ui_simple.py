"""Simple test script for the enhanced workflow editor UI."""

import tkinter as tk
import logging
import sys
from pathlib import Path

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
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter


class MockRepository:
    """Mock repository for testing."""
    
    def __init__(self):
        """Initialize the mock repository."""
        self.workflows = {
            "Test Workflow 1": {"actions": []},
            "Test Workflow 2": {"actions": [
                {"type": "Navigate", "url": "https://example.com", "name": "Navigate to Example"},
                {"type": "Click", "selector": "#button1", "name": "Click Button 1"},
                {"type": "Type", "selector": "#input1", "value_key": "test", "name": "Type Text"},
                {"type": "Wait", "duration_seconds": "5", "name": "Wait 5 Seconds"},
            ]},
        }
    
    def get_all_workflow_names(self):
        """Get all workflow names."""
        return list(self.workflows.keys())
    
    def get_workflow(self, name):
        """Get a workflow by name."""
        return self.workflows.get(name, {"actions": []})
    
    def save_workflow(self, name, workflow):
        """Save a workflow."""
        self.workflows[name] = workflow
        return True
    
    def delete_workflow(self, name):
        """Delete a workflow."""
        if name in self.workflows:
            del self.workflows[name]
            return True
        return False


class MockPresenter(WorkflowEditorPresenter):
    """Mock presenter for testing."""
    
    def __init__(self):
        """Initialize the mock presenter."""
        self.repository = MockRepository()
        self.view = None
        self._current_workflow_name = None
        self._current_actions = []
    
    def set_view(self, view):
        """Set the view."""
        self.view = view
        self.refresh_workflow_list()
    
    def refresh_workflow_list(self):
        """Refresh the workflow list."""
        workflow_names = self.repository.get_all_workflow_names()
        if self.view:
            self.view.set_workflow_list(workflow_names)
    
    def load_workflow(self, name):
        """Load a workflow."""
        workflow = self.repository.get_workflow(name)
        self._current_workflow_name = name
        self._current_actions = workflow.get("actions", [])
        
        # Convert actions to display format for the view
        action_displays = []
        for action in self._current_actions:
            action_type = action.get("type", "Unknown")
            if action_type == "Navigate":
                display = f"Navigate: {action.get('url', '')}"
            elif action_type == "Click":
                display = f"Click: {action.get('selector', '')}"
            elif action_type == "Type":
                display = f"Type: {action.get('selector', '')} = {action.get('value_key', '')}"
            elif action_type == "Wait":
                display = f"Wait: {action.get('duration_seconds', '')} seconds"
            else:
                display = f"{action_type}: {action.get('name', '')}"
            action_displays.append(display)
        
        if self.view:
            self.view.set_action_list(action_displays)
    
    def create_new_workflow(self, name):
        """Create a new workflow."""
        if name in self.repository.get_all_workflow_names():
            if self.view:
                self.view.display_error("Error", f"Workflow '{name}' already exists.")
            return False
        
        self.repository.save_workflow(name, {"actions": []})
        self.refresh_workflow_list()
        self.load_workflow(name)
        return True
    
    def save_workflow(self, name):
        """Save the current workflow."""
        workflow = {"actions": self._current_actions}
        self.repository.save_workflow(name, workflow)
        if self.view:
            self.view.set_status(f"Workflow '{name}' saved.")
        return True
    
    def delete_workflow(self, name):
        """Delete a workflow."""
        if self.repository.delete_workflow(name):
            self.refresh_workflow_list()
            if self._current_workflow_name == name:
                self._current_workflow_name = None
                self._current_actions = []
                if self.view:
                    self.view.set_action_list([])
            if self.view:
                self.view.set_status(f"Workflow '{name}' deleted.")
            return True
        return False
    
    def add_action(self, action_data):
        """Add an action to the current workflow."""
        self._current_actions.append(action_data)
        self.load_workflow(self._current_workflow_name)
        if self.view:
            self.view.set_status(f"Action '{action_data.get('type', 'Unknown')}' added.")
        return True
    
    def update_action(self, index, action_data):
        """Update an action in the current workflow."""
        if 0 <= index < len(self._current_actions):
            self._current_actions[index] = action_data
            self.load_workflow(self._current_workflow_name)
            if self.view:
                self.view.set_status(f"Action '{action_data.get('type', 'Unknown')}' updated.")
            return True
        return False
    
    def delete_action(self, index):
        """Delete an action from the current workflow."""
        if 0 <= index < len(self._current_actions):
            action = self._current_actions.pop(index)
            self.load_workflow(self._current_workflow_name)
            if self.view:
                self.view.set_status(f"Action '{action.get('type', 'Unknown')}' deleted.")
            return True
        return False
    
    def get_action_data(self, index):
        """Get action data by index."""
        if 0 <= index < len(self._current_actions):
            return self._current_actions[index]
        return None


def main():
    """Run the enhanced workflow editor UI test."""
    # Create the root window
    root = tk.Tk()
    root.title("AutoQliq - Enhanced UI Test")
    root.geometry("1000x700")
    
    # Create a mock presenter
    presenter = MockPresenter()
    
    # Create the enhanced workflow editor view
    view = WorkflowEditorViewEnhanced(root, presenter)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
