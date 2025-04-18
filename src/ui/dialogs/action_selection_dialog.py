"""Dialog for selecting action types with a visual, clickable interface."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Dict, List, Any

from src.core.actions.factory import ActionFactory
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class ActionSelectionDialog(tk.Toplevel):
    """
    A modal dialog for selecting action types with a visual, clickable interface.
    
    This dialog organizes actions into categories and displays them as buttons with
    descriptions, making it easier for users to find and select the appropriate action.
    """
    
    # Action categories with their actions
    ACTION_CATEGORIES = {
        "Navigation": ["Navigate", "Back", "Forward", "Refresh"],
        "Interaction": ["Click", "Type", "Select", "Upload"],
        "Waiting": ["Wait", "WaitForElement", "WaitForText"],
        "Verification": ["CheckElement", "CheckText", "Screenshot"],
        "Control Flow": ["Conditional", "Loop", "ErrorHandling"],
        "Advanced": ["Template", "ExecuteScript", "StoreValue"]
    }
    
    # Action descriptions
    ACTION_DESCRIPTIONS = {
        "Navigate": "Navigate to a URL",
        "Back": "Go back to the previous page",
        "Forward": "Go forward to the next page",
        "Refresh": "Refresh the current page",
        "Click": "Click on an element",
        "Type": "Type text into an input field",
        "Select": "Select an option from a dropdown",
        "Upload": "Upload a file to a file input",
        "Wait": "Wait for a specified time",
        "WaitForElement": "Wait for an element to appear",
        "WaitForText": "Wait for text to appear on the page",
        "CheckElement": "Verify an element exists or has a property",
        "CheckText": "Verify text exists on the page",
        "Screenshot": "Take a screenshot of the page",
        "Conditional": "Execute actions based on a condition",
        "Loop": "Repeat actions multiple times",
        "ErrorHandling": "Handle errors with try/catch",
        "Template": "Execute a saved template",
        "ExecuteScript": "Execute JavaScript code",
        "StoreValue": "Store a value in a variable"
    }
    
    def __init__(self, parent: tk.Widget):
        """Initialize the Action Selection Dialog."""
        super().__init__(parent)
        self.parent = parent
        self.selected_action: Optional[str] = None
        
        self.title("Select Action Type")
        self.geometry("600x500")
        self.resizable(True, True)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Get registered action types from ActionFactory
        self.registered_actions = ActionFactory.get_registered_action_types()
        
        try:
            self._create_widgets()
        except Exception as e:
            logger.exception("Failed to create ActionSelectionDialog UI.")
            tk.messagebox.showerror("Dialog Error", f"Failed to initialize action selection: {e}", parent=parent)
            self.destroy()
            return
        
        self.grab_set()
        self._center_window()
    
    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook with tabs for categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a tab for each category
        self.category_frames = {}
        for category in self.ACTION_CATEGORIES:
            frame = UIFactory.create_frame(self.notebook, padding="10")
            self.notebook.add(frame, text=category)
            self.category_frames[category] = frame
            
            # Make the frame use a grid layout
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            
            # Populate the category with action buttons
            self._populate_category(category, frame)
        
        # Create a search frame at the top
        search_frame = UIFactory.create_frame(main_frame, padding="5 5 5 10")
        search_frame.pack(fill=tk.X, side=tk.TOP, before=self.notebook)
        
        # Add search label and entry
        UIFactory.create_label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = UIFactory.create_entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_var.trace_add("write", self._on_search)
        
        # Create a frame for buttons at the bottom
        button_frame = UIFactory.create_frame(main_frame, padding="5")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        # Add Cancel button
        cancel_button = UIFactory.create_button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind keyboard shortcuts
        self.bind('<Escape>', lambda e: self._on_cancel())
        search_entry.focus_set()
    
    def _populate_category(self, category: str, frame: ttk.Frame):
        """Populate a category tab with action buttons."""
        actions = self.ACTION_CATEGORIES[category]
        row, col = 0, 0
        
        for action in actions:
            # Skip actions that aren't registered
            if action not in self.registered_actions:
                continue
            
            # Create a frame for this action
            action_frame = UIFactory.create_frame(frame, padding="5")
            action_frame.grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)
            action_frame.columnconfigure(0, weight=1)
            
            # Add a border to the frame
            action_frame.configure(relief=tk.RAISED, borderwidth=1)
            
            # Create the action button
            button = UIFactory.create_button(
                action_frame, 
                text=action,
                command=lambda a=action: self._on_action_selected(a),
                width=15,
                height=2
            )
            button.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
            
            # Add the description
            description = self.ACTION_DESCRIPTIONS.get(action, "")
            desc_label = UIFactory.create_label(action_frame, text=description, wraplength=150)
            desc_label.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
            
            # Store references for search filtering
            button.action_name = action
            button.description = description
            button.frame = action_frame
            
            # Move to the next column or row
            col += 1
            if col > 1:  # 2 columns per row
                col = 0
                row += 1
    
    def _on_action_selected(self, action: str):
        """Handle action selection."""
        self.selected_action = action
        self.destroy()
    
    def _on_cancel(self):
        """Close the dialog without selecting an action."""
        self.selected_action = None
        self.destroy()
    
    def _on_search(self, *args):
        """Filter actions based on search text."""
        search_text = self.search_var.get().lower()
        
        # If search is empty, show all categories and actions
        if not search_text:
            for category, frame in self.category_frames.items():
                # Show all action frames in this category
                for child in frame.winfo_children():
                    if hasattr(child, 'grid_info'):
                        child.grid()
            return
        
        # Find the first category with matching actions
        first_match_category = None
        
        for category, frame in self.category_frames.items():
            has_match = False
            
            # Check each action frame in this category
            for child in frame.winfo_children():
                if not hasattr(child, 'winfo_children'):
                    continue
                
                # Get the button from the action frame
                for widget in child.winfo_children():
                    if isinstance(widget, tk.Button) and hasattr(widget, 'action_name'):
                        action_name = widget.action_name.lower()
                        description = widget.description.lower()
                        
                        # Check if the action matches the search
                        if search_text in action_name or search_text in description:
                            child.grid()
                            has_match = True
                            if first_match_category is None:
                                first_match_category = category
                        else:
                            child.grid_remove()
                        
                        break
        
        # Switch to the first category with matches
        if first_match_category:
            category_index = list(self.category_frames.keys()).index(first_match_category)
            self.notebook.select(category_index)
    
    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_win = self.parent.winfo_toplevel()
        parent_x = parent_win.winfo_rootx()
        parent_y = parent_win.winfo_rooty()
        parent_w = parent_win.winfo_width()
        parent_h = parent_win.winfo_height()
        win_w = self.winfo_reqwidth()
        win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = max(0, min(pos_x, screen_w - win_w))
        pos_y = max(0, min(pos_y, screen_h - win_h))
        self.geometry(f"+{pos_x}+{pos_y}")
    
    def show(self) -> Optional[str]:
        """Make the dialog visible and wait for user interaction."""
        self.wait_window()
        return self.selected_action
