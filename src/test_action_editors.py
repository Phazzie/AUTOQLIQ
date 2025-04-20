"""Test script for the action editor dialogs."""

import tkinter as tk
import logging
import os
import sys
import pytest
from typing import Dict, Any, Optional

# Skip this interactive UI script during pytest collection
pytest.skip("Skipping interactive UI test script.", allow_module_level=True)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from src.ui.factories.dialog_factory import DialogFactory


def setup_logging() -> None:
    """Set up logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_action_editors.log', mode='w')
        ]
    )


def test_regular_action_editor() -> Optional[Dict[str, Any]]:
    """Test the regular action editor dialog."""
    # Create a sample action data
    action_data = {
        "type": "Navigate",
        "name": "Go to Google",
        "url": "https://www.google.com"
    }
    
    # Show the action editor dialog
    result = DialogFactory.show_action_editor(root, action_data)
    
    return result


def test_conditional_action_editor() -> Optional[Dict[str, Any]]:
    """Test the conditional action editor dialog."""
    # Create a sample action data
    action_data = {
        "type": "Conditional",
        "name": "Check if element exists",
        "condition_type": "element_present",
        "selector": "#search-box",
        "true_branch": [
            {
                "type": "Click",
                "name": "Click search box",
                "selector": "#search-box"
            }
        ],
        "false_branch": [
            {
                "type": "Wait",
                "name": "Wait for page to load",
                "duration_seconds": 2
            }
        ]
    }
    
    # Show the conditional action editor dialog
    result = DialogFactory.show_action_editor(root, action_data)
    
    return result


def test_loop_action_editor() -> Optional[Dict[str, Any]]:
    """Test the loop action editor dialog."""
    # Create a sample action data
    action_data = {
        "type": "Loop",
        "name": "Repeat 5 times",
        "loop_type": "count",
        "count": 5,
        "actions": [
            {
                "type": "Click",
                "name": "Click button",
                "selector": "#button"
            },
            {
                "type": "Wait",
                "name": "Wait briefly",
                "duration_seconds": 1
            }
        ]
    }
    
    # Show the loop action editor dialog
    result = DialogFactory.show_action_editor(root, action_data)
    
    return result


def test_new_action_editor() -> Optional[Dict[str, Any]]:
    """Test creating a new action."""
    # Show the action editor dialog with no initial data
    result = DialogFactory.show_action_editor(root)
    
    return result


def main() -> None:
    """Main function for the test script."""
    global root
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting test_action_editors.py")
    
    try:
        # Create the root window
        root = tk.Tk()
        root.title("Action Editor Test")
        root.geometry("300x200")
        
        # Create a frame for the buttons
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create buttons for each test
        tk.Button(
            frame,
            text="Test Regular Action Editor",
            command=lambda: print(f"Result: {test_regular_action_editor()}")
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            frame,
            text="Test Conditional Action Editor",
            command=lambda: print(f"Result: {test_conditional_action_editor()}")
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            frame,
            text="Test Loop Action Editor",
            command=lambda: print(f"Result: {test_loop_action_editor()}")
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            frame,
            text="Test New Action Editor",
            command=lambda: print(f"Result: {test_new_action_editor()}")
        ).pack(fill=tk.X, pady=5)
        
        # Start the main loop
        root.mainloop()
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
