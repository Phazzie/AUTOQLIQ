"""Visual list of actions in a workflow with add buttons between items."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Optional, Callable

from src.ui.components.workflow_action_item import WorkflowActionListItem

logger = logging.getLogger(__name__)

class WorkflowActionList(ttk.Frame):
    """A visual list of actions in a workflow with add buttons between items."""
    
    def __init__(self, parent: tk.Widget, 
                 on_insert: Optional[Callable[[int], None]] = None,
                 on_edit: Optional[Callable[[int], None]] = None,
                 on_delete: Optional[Callable[[int], None]] = None,
                 on_move: Optional[Callable[[int, int], None]] = None):
        """
        Initialize a workflow action list.
        
        Args:
            parent: The parent widget
            on_insert: Callback for inserting an action at a position
            on_edit: Callback for editing an action
            on_delete: Callback for deleting an action
            on_move: Callback for moving an action from one position to another
        """
        super().__init__(parent)
        self.on_insert = on_insert
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_move = on_move
        
        self.action_frames = []
        self.add_buttons = []
        self.selected_index = None
        
        # Create a canvas with scrollbar for the action list
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the action items
        self.action_container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.action_container, anchor=tk.NW)
        
        # Configure canvas to resize with the frame
        self.action_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Add an initial "+" button at the top
        self._add_insert_button(0)
    
    def update_actions(self, actions: List[Dict[str, Any]]) -> None:
        """
        Update the action list with the current actions.
        
        Args:
            actions: List of action data dictionaries
        """
        # Clear existing action frames
        for frame in self.action_frames:
            frame.destroy()
        self.action_frames = []
        
        # Clear existing add buttons
        for button in self.add_buttons:
            button.destroy()
        self.add_buttons = []
        
        # Add an initial "+" button at the top
        self._add_insert_button(0)
        
        # Add each action with a "+" button after it
        for i, action in enumerate(actions):
            # Create action frame
            action_frame = WorkflowActionListItem(
                self.action_container, 
                action, 
                i,
                on_edit=self._on_edit_action,
                on_delete=self._on_delete_action,
                on_move_up=self._on_move_action_up if i > 0 else None,
                on_move_down=self._on_move_action_down if i < len(actions) - 1 else None
            )
            action_frame.grid(row=i*2+1, column=0, sticky=tk.EW, padx=5, pady=5)
            self.action_frames.append(action_frame)
            
            # Add "+" button after this action
            self._add_insert_button(i+1)
        
        # Reset selected index
        self.selected_index = None
    
    def _add_insert_button(self, position: int) -> None:
        """
        Add a '+' button to insert an action at the specified position.
        
        Args:
            position: The position to insert the action at
        """
        button_frame = ttk.Frame(self.action_container)
        button_frame.grid(row=position*2, column=0, sticky=tk.EW, padx=5, pady=2)
        
        # Add a line before the button (except for the first button)
        if position > 0:
            separator = ttk.Separator(button_frame, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, padx=20, pady=2)
        
        # Create the "+" button
        add_button = ttk.Button(
            button_frame, 
            text="➕ Add Action", 
            command=lambda pos=position: self._on_insert_action(pos)
        )
        add_button.pack(pady=2)
        self.add_buttons.append(button_frame)
    
    def _on_insert_action(self, position: int) -> None:
        """
        Handle inserting an action at the specified position.
        
        Args:
            position: The position to insert the action at
        """
        if self.on_insert:
            self.on_insert(position)
    
    def _on_edit_action(self, index: int) -> None:
        """
        Handle editing an action.
        
        Args:
            index: The index of the action to edit
        """
        if self.on_edit:
            self.on_edit(index)
    
    def _on_delete_action(self, index: int) -> None:
        """
        Handle deleting an action.
        
        Args:
            index: The index of the action to delete
        """
        if self.on_delete:
            self.on_delete(index)
    
    def _on_move_action_up(self, index: int) -> None:
        """
        Handle moving an action up in the list.
        
        Args:
            index: The index of the action to move up
        """
        if self.on_move and index > 0:
            self.on_move(index, index - 1)
    
    def _on_move_action_down(self, index: int) -> None:
        """
        Handle moving an action down in the list.
        
        Args:
            index: The index of the action to move down
        """
        if self.on_move and index < len(self.action_frames) - 1:
            self.on_move(index, index + 1)
    
    def _on_frame_configure(self, event: tk.Event) -> None:
        """
        Update the scrollregion when the frame size changes.
        
        Args:
            event: The configure event
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event: tk.Event) -> None:
        """
        Resize the canvas window when the canvas size changes.
        
        Args:
            event: The configure event
        """
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event: tk.Event) -> None:
        """
        Handle mouse wheel scrolling.
        
        Args:
            event: The mousewheel event
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def select_action(self, index: int) -> None:
        """
        Select an action by index.
        
        Args:
            index: The index of the action to select
        """
        # Deselect previously selected action
        if self.selected_index is not None and 0 <= self.selected_index < len(self.action_frames):
            self.action_frames[self.selected_index].deselect()
        
        # Select the new action
        if 0 <= index < len(self.action_frames):
            self.action_frames[index].select()
            self.selected_index = index
    
    def get_selected_index(self) -> Optional[int]:
        """
        Get the index of the currently selected action.
        
        Returns:
            The index of the selected action, or None if no action is selected
        """
        return self.selected_index
