"""Test script for the UI components."""

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
from src.ui.components.workflow_action_item import WorkflowActionListItem
from src.ui.components.workflow_action_list import WorkflowActionList


class TestApp:
    """Test application for UI components."""
    
    def __init__(self, root):
        """Initialize the test application."""
        self.root = root
        self.root.title("AutoQliq - UI Components Test")
        self.root.geometry("1000x700")
        
        # Create a frame for the components
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sample action data
        self.actions = [
            {"type": "Navigate", "url": "https://example.com", "name": "Navigate to Example"},
            {"type": "Click", "selector": "#button1", "name": "Click Button 1"},
            {"type": "Type", "selector": "#input1", "value_key": "test", "name": "Type Text"},
            {"type": "Wait", "duration_seconds": "5", "name": "Wait 5 Seconds"},
            {"type": "Screenshot", "file_path": "screenshot.png", "name": "Take Screenshot"},
            {"type": "Conditional", "condition_type": "element_present", "selector": "#element1", "name": "Check Element"},
            {"type": "Loop", "loop_type": "count", "count": "3", "name": "Repeat 3 Times"},
            {"type": "ErrorHandling", "name": "Handle Errors"},
            {"type": "Template", "template_name": "Login", "name": "Execute Login Template"},
        ]
        
        # Create the action list
        self.action_list = WorkflowActionList(
            self.frame,
            on_insert=self.on_insert_action,
            on_edit=self.on_edit_action,
            on_delete=self.on_delete_action,
            on_move=self.on_move_action
        )
        self.action_list.pack(fill=tk.BOTH, expand=True)
        
        # Update the action list
        self.action_list.update_actions(self.actions)
    
    def on_insert_action(self, position):
        """Handle inserting an action."""
        print(f"Insert action at position {position}")
        
        # For testing, just add a new action at the specified position
        new_action = {"type": "Click", "selector": f"#new_button_{position}", "name": f"New Action {position}"}
        self.actions.insert(position, new_action)
        self.action_list.update_actions(self.actions)
    
    def on_edit_action(self, index):
        """Handle editing an action."""
        print(f"Edit action at index {index}")
        
        # For testing, just update the action name
        if 0 <= index < len(self.actions):
            self.actions[index]["name"] = f"{self.actions[index]['name']} (Edited)"
            self.action_list.update_actions(self.actions)
    
    def on_delete_action(self, index):
        """Handle deleting an action."""
        print(f"Delete action at index {index}")
        
        # For testing, just remove the action
        if 0 <= index < len(self.actions):
            del self.actions[index]
            self.action_list.update_actions(self.actions)
    
    def on_move_action(self, from_index, to_index):
        """Handle moving an action."""
        print(f"Move action from index {from_index} to {to_index}")
        
        # For testing, just move the action
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.action_list.update_actions(self.actions)


def main():
    """Run the UI components test."""
    # Create the root window
    root = tk.Tk()
    
    # Create the test application
    app = TestApp(root)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()
