"""Visual representation of an action in a workflow."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)

class WorkflowActionListItem(ttk.Frame):
    """A visual representation of an action in the workflow."""
    
    ACTION_ICONS = {
        "Navigate": "🌐",  # Web icon
        "Click": "👆",     # Click icon
        "Type": "⌨️",      # Keyboard icon
        "Wait": "⏱️",      # Timer icon
        "Screenshot": "📷", # Camera icon
        "Conditional": "🔀", # Branch icon
        "Loop": "🔄",      # Loop icon
        "ErrorHandling": "⚠️", # Warning icon
        "Template": "📋",   # Template icon
        # Add more icons for other action types
    }
    
    def __init__(self, parent: tk.Widget, action_data: Dict[str, Any], index: int, 
                 on_edit: Optional[Callable[[int], None]] = None, 
                 on_delete: Optional[Callable[[int], None]] = None, 
                 on_move_up: Optional[Callable[[int], None]] = None, 
                 on_move_down: Optional[Callable[[int], None]] = None):
        """
        Initialize a workflow action item.
        
        Args:
            parent: The parent widget
            action_data: The action data dictionary
            index: The index of this action in the workflow
            on_edit: Callback for editing this action
            on_delete: Callback for deleting this action
            on_move_up: Callback for moving this action up
            on_move_down: Callback for moving this action down
        """
        super().__init__(parent, padding=5)
        self.action_data = action_data
        self.index = index
        self.selected = False
        
        # Configure the frame
        self.configure(relief=tk.RAISED, borderwidth=1)
        self.columnconfigure(1, weight=1)
        
        # Action icon
        action_type = action_data.get("type", "Unknown")
        icon = self.ACTION_ICONS.get(action_type, "❓")
        self.icon_label = ttk.Label(self, text=icon, font=("TkDefaultFont", 16))
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=5)
        
        # Action title
        title = action_data.get("name", action_type)
        self.title_label = ttk.Label(self, text=title, font=("TkDefaultFont", 11, "bold"))
        self.title_label.grid(row=0, column=1, sticky=tk.W)
        
        # Action description
        description = self._get_action_description(action_data)
        self.desc_label = ttk.Label(self, text=description, wraplength=300)
        self.desc_label.grid(row=1, column=1, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=2, rowspan=2, padx=5)
        
        # Edit button
        edit_btn = ttk.Button(
            button_frame, 
            text="✏️", 
            width=3, 
            command=lambda: on_edit(self.index) if on_edit else None
        )
        edit_btn.pack(side=tk.TOP, pady=2)
        
        # Delete button
        delete_btn = ttk.Button(
            button_frame, 
            text="🗑️", 
            width=3, 
            command=lambda: on_delete(self.index) if on_delete else None
        )
        delete_btn.pack(side=tk.TOP, pady=2)
        
        # Move up button
        if on_move_up:
            up_btn = ttk.Button(
                button_frame, 
                text="⬆️", 
                width=3, 
                command=lambda: on_move_up(self.index)
            )
            up_btn.pack(side=tk.TOP, pady=2)
        
        # Move down button
        if on_move_down:
            down_btn = ttk.Button(
                button_frame, 
                text="⬇️", 
                width=3, 
                command=lambda: on_move_down(self.index)
            )
            down_btn.pack(side=tk.TOP, pady=2)
        
        # Bind click events
        self.bind("<Button-1>", lambda e: self._on_click())
        self.title_label.bind("<Button-1>", lambda e: self._on_click())
        self.desc_label.bind("<Button-1>", lambda e: self._on_click())
        self.icon_label.bind("<Button-1>", lambda e: self._on_click())
        
        # Double-click to edit
        self.bind("<Double-Button-1>", lambda e: on_edit(self.index) if on_edit else None)
        self.title_label.bind("<Double-Button-1>", lambda e: on_edit(self.index) if on_edit else None)
        self.desc_label.bind("<Double-Button-1>", lambda e: on_edit(self.index) if on_edit else None)
        self.icon_label.bind("<Double-Button-1>", lambda e: on_edit(self.index) if on_edit else None)
    
    def _get_action_description(self, action_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable description of the action.
        
        Args:
            action_data: The action data dictionary
            
        Returns:
            A human-readable description of the action
        """
        action_type = action_data.get("type", "Unknown")
        
        if action_type == "Navigate":
            return f"Navigate to: {action_data.get('url', '')}"
        elif action_type == "Click":
            return f"Click element: {action_data.get('selector', '')}"
        elif action_type == "Type":
            return f"Type '{action_data.get('value_key', '')}' into: {action_data.get('selector', '')}"
        elif action_type == "Wait":
            return f"Wait for {action_data.get('duration_seconds', '')} seconds"
        elif action_type == "Screenshot":
            return f"Take screenshot: {action_data.get('file_path', '')}"
        elif action_type == "Conditional":
            condition = action_data.get("condition_type", "")
            if condition == "element_present":
                return f"If element exists: {action_data.get('selector', '')}"
            elif condition == "element_not_present":
                return f"If element does not exist: {action_data.get('selector', '')}"
            elif condition == "variable_equals":
                return f"If {action_data.get('variable_name', '')} equals {action_data.get('expected_value', '')}"
            return f"Conditional: {condition}"
        elif action_type == "Loop":
            loop_type = action_data.get("loop_type", "")
            if loop_type == "count":
                return f"Repeat {action_data.get('count', '')} times"
            elif loop_type == "for_each":
                return f"For each item in {action_data.get('list_variable_name', '')}"
            return f"Loop: {loop_type}"
        elif action_type == "ErrorHandling":
            return "Try/Catch error handling"
        elif action_type == "Template":
            return f"Execute template: {action_data.get('template_name', '')}"
        
        # Default description
        return f"{action_type} action"
    
    def _on_click(self) -> None:
        """Handle click event to select this item."""
        # Highlight this item
        self.select()
        
        # Notify parent that this item is selected
        self.event_generate("<<ActionSelected>>", data=self.index)
    
    def select(self) -> None:
        """Select this action item."""
        self.selected = True
        self.configure(relief=tk.SUNKEN, borderwidth=2)
    
    def deselect(self) -> None:
        """Deselect this action item."""
        self.selected = False
        self.configure(relief=tk.RAISED, borderwidth=1)
