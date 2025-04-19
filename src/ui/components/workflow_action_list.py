"""Visual list of actions in a workflow with add buttons between items."""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Optional, Callable

# Import the action item component
from src.ui.components.workflow_action_item import WorkflowActionListItem
# Import factory for consistency
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class WorkflowActionList(ttk.Frame):
    """
    A scrollable list that visually displays workflow actions using
    WorkflowActionListItem components, allowing insertion, editing, deletion,
    and reordering.
    """

    def __init__(self, parent: tk.Widget,
                 on_insert: Optional[Callable[[int], None]] = None,
                 on_edit: Optional[Callable[[int], None]] = None,
                 on_delete: Optional[Callable[[int], None]] = None,
                 on_move: Optional[Callable[[int, int], None]] = None):
        """
        Initialize the visual workflow action list.

        Args:
            parent: The parent widget.
            on_insert: Callback(position) triggered when an insert ('+') button is clicked.
            on_edit: Callback(index) triggered when an action item's edit button is clicked.
            on_delete: Callback(index) triggered when an action item's delete button is clicked.
            on_move: Callback(from_index, to_index) triggered when an action is moved (e.g., via drag-drop or buttons).
        """
        super().__init__(parent)
        self.on_insert = on_insert
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_move = on_move

        # Store references to the action item frames and insert buttons
        self._action_item_frames: List[WorkflowActionListItem] = []
        self._insert_button_frames: List[ttk.Frame] = [] # Frames holding insert buttons
        self._selected_item_index: Optional[int] = None

        # --- Create Scrollable Canvas Setup ---
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = UIFactory.create_scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame inside the canvas to hold the list content
        self.action_container = UIFactory.create_frame(self.canvas, padding=2)
        # Add container frame to canvas window
        self.canvas_window = self.canvas.create_window((0, 0), window=self.action_container, anchor=tk.NW)

        # Configure resizing and scrolling
        self.action_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # Bind mouse wheel for scrolling (consider platform differences if needed)
        self.bind_all("<MouseWheel>", self._on_mousewheel, add='+') # Use bind_all carefully
        self.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"), add='+') # Linux scroll up
        self.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"), add='+') # Linux scroll down

        # Initialize with the top insert button
        self._redraw_list([]) # Initial empty draw

    def update_actions(self, actions_data: List[Dict[str, Any]]) -> None:
        """
        Update the entire action list display based on new data.

        Args:
            actions_data: A list of dictionaries, where each dictionary
                          represents the data for an action.
        """
        logger.debug(f"Updating action list with {len(actions_data)} items.")
        self._selected_item_index = None # Clear selection on full update
        self._redraw_list(actions_data)

    def _redraw_list(self, actions_data: List[Dict[str, Any]]):
        """Internal helper to clear and redraw all items and insert buttons."""
        # Clear existing widgets from the container frame
        for widget in self.action_container.winfo_children():
            widget.destroy()
        self._action_item_frames = []
        self._insert_button_frames = []

        # Add the top insert button (position 0)
        self._add_insert_button_frame(0)

        # Add each action item and the insert button below it
        for i, data in enumerate(actions_data):
            can_move_up = i > 0
            can_move_down = i < len(actions_data) - 1

            # Create action item
            action_item = WorkflowActionListItem(
                self.action_container,
                action_data=data,
                index=i,
                on_edit=self._on_edit_request,
                on_delete=self._on_delete_request,
                on_move_up=self._on_move_up_request if can_move_up else None,
                on_move_down=self._on_move_down_request if can_move_down else None
            )
            # Use grid within the container for consistent spacing
            action_item.grid(row=i*2 + 1, column=0, sticky=tk.EW, pady=(2, 2))
            # Make action item frame expand horizontally
            self.action_container.columnconfigure(0, weight=1)
            self._action_item_frames.append(action_item)

            # Bind selection event from the item to the list's handler
            action_item.bind("<<ActionSelected>>", self._on_action_item_selected)

            # Add insert button below this action (position i+1)
            self._add_insert_button_frame(i + 1)

        # Ensure the previously selected item (if any) is visually selected
        if self._selected_item_index is not None and 0 <= self._selected_item_index < len(self._action_item_frames):
            self._action_item_frames[self._selected_item_index].select()

        # Update scroll region after drawing
        self.action_container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _add_insert_button_frame(self, position: int):
        """Creates and grids the frame containing the insert button."""
        button_frame = UIFactory.create_frame(self.action_container, padding=0)
        # Center the button within its grid cell
        button_frame.columnconfigure(0, weight=1)

        # Simple thin separator line (optional)
        # separator = ttk.Separator(button_frame, orient=tk.HORIZONTAL)
        # separator.grid(row=0, column=0, sticky=tk.EW, padx=20, pady=1)

        add_button = ttk.Button( # Use ttk.Button for better styling
            button_frame,
            text="➕", # Smaller '+' sign
            width=3,
            style="Toolbutton", # Use Toolbutton style if available for less padding
            command=lambda pos=position: self._on_insert_request(pos)
        )
        add_button.grid(row=1, column=0, pady=2) # Place button below separator

        # Grid the button frame itself
        button_frame.grid(row=position * 2, column=0, sticky=tk.EW, pady=(1, 1))
        self._insert_button_frames.append(button_frame)

    # --- Internal Callback Wrappers (Call external callbacks) ---

    def _on_insert_request(self, position: int):
        logger.debug(f"Insert button clicked at position {position}")
        if self.on_insert:
            self.on_insert(position)

    def _on_edit_request(self, index: int):
        logger.debug(f"Edit request for index {index}")
        if self.on_edit:
            self.on_edit(index)

    def _on_delete_request(self, index: int):
        logger.debug(f"Delete request for index {index}")
        if self.on_delete:
            self.on_delete(index) # Presenter handles confirmation

    def _on_move_up_request(self, index: int):
        logger.debug(f"Move up request for index {index}")
        if self.on_move and index > 0:
            self.on_move(index, index - 1)

    def _on_move_down_request(self, index: int):
        logger.debug(f"Move down request for index {index}")
        if self.on_move and index < len(self._action_item_frames) - 1:
            self.on_move(index, index + 1)

    # --- Selection Handling ---

    def _on_action_item_selected(self, event: tk.Event):
        """Handles the <<ActionSelected>> event from a WorkflowActionListItem."""
        # Find the widget that generated the event (the WorkflowActionListItem frame)
        selected_widget = event.widget
        if not isinstance(selected_widget, WorkflowActionListItem): return

        new_index = selected_widget.index
        logger.debug(f"Received selection event for index {new_index}")

        if new_index == self._selected_item_index:
            return # Already selected

        # Deselect previous item
        if self._selected_item_index is not None and 0 <= self._selected_item_index < len(self._action_item_frames):
            self._action_item_frames[self._selected_item_index].deselect()

        # Select new item
        if 0 <= new_index < len(self._action_item_frames):
            self._action_item_frames[new_index].select()
            self._selected_item_index = new_index
        else:
             self._selected_item_index = None # Should not happen if index is from widget

        # Optional: Notify external listeners about selection change if needed
        # self.event_generate("<<ListSelectionChanged>>")


    def get_selected_index(self) -> Optional[int]:
        """Get the index of the currently selected action item."""
        return self._selected_item_index

    # --- Canvas/Scrolling Helpers ---

    def _on_frame_configure(self, event=None):
        """Update scroll region when the inner frame resizes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize the frame inside the canvas to match canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Scroll the canvas using the mouse wheel."""
        # Determine scroll direction and amount (platform dependent)
        if event.num == 5 or event.delta < 0: # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0: # Scroll up
            self.canvas.yview_scroll(-1, "units")
