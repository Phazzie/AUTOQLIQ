"""Visual representation of an action in a workflow."""

import tkinter as tk
from tkinter import ttk
import logging
import os
from typing import Optional, Dict, Any, Callable

# Assuming UIFactory exists for creating consistent widgets
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class WorkflowActionListItem(ttk.Frame):
    """
    A visual representation of a single action within the workflow editor list.
    Provides display of action details and buttons for interaction.
    """

    # Default icons - consider using images later
    ACTION_ICONS = {
        "Navigate": "🌐", "Click": "👆", "Type": "⌨️", "Wait": "⏱️",
        "Screenshot": "📷", "Conditional": "🔀", "Loop": "🔄",
        "ErrorHandling": "⚠️", "Template": "📋", "JavaScriptCondition": "🧪",
        "default": "⚙️" # Default icon
    }

    def __init__(self, parent: tk.Widget, action_data: Dict[str, Any], index: int,
                 on_edit: Optional[Callable[[int], None]] = None,
                 on_delete: Optional[Callable[[int], None]] = None,
                 on_move_up: Optional[Callable[[int], None]] = None,
                 on_move_down: Optional[Callable[[int], None]] = None):
        """
        Initialize a workflow action item frame.

        Args:
            parent: The parent widget (likely the inner frame of WorkflowActionList canvas).
            action_data: The dictionary representing the action's configuration.
            index: The index (position) of this action in the workflow list.
            on_edit: Callback function when the 'Edit' button is clicked (passes index).
            on_delete: Callback function when the 'Delete' button is clicked (passes index).
            on_move_up: Callback function when the 'Move Up' button is clicked (passes index).
            on_move_down: Callback function when the 'Move Down' button is clicked (passes index).
        """
        super().__init__(parent, padding=5, style="ActionItem.TFrame") # Use a custom style
        self.action_data = action_data
        self.index = index
        self.selected = False

        # --- Configure Styles (can be done once elsewhere) ---
        style = ttk.Style()
        style.configure("ActionItem.TFrame", relief=tk.RAISED, borderwidth=1)
        style.map("ActionItem.TFrame",
                  background=[('active', 'lightblue'), ('!active', 'systemTransparent')]) # Highlight on hover/select
        style.configure("SelectedAction.TFrame", relief=tk.SUNKEN, borderwidth=2, background="lightblue")
        style.configure("ActionButton.TButton", padding=1, width=2, font=('TkDefaultFont', 8)) # Smaller buttons

        # --- Widget Layout (Using Grid) ---
        self.columnconfigure(1, weight=1) # Allow description label to expand

        # Icon
        action_type = action_data.get("type", "Unknown")
        icon = self.ACTION_ICONS.get(action_type, self.ACTION_ICONS["default"])
        self.icon_label = UIFactory.create_label(self, text=icon, font=("TkDefaultFont", 14))
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 8), pady=2, sticky=tk.N)

        # Title (Action Name)
        title = action_data.get("name", action_type)
        self.title_label = UIFactory.create_label(self, text=title, font=("TkDefaultFont", 10, "bold"), anchor=tk.W)
        self.title_label.grid(row=0, column=1, sticky=tk.EW)

        # Description
        description = self._get_action_description(action_data)
        self.desc_label = UIFactory.create_label(self, text=description, wraplength=350, justify=tk.LEFT, anchor=tk.NW) # Adjust wraplength
        self.desc_label.grid(row=1, column=1, sticky=tk.NSEW)

        # Action Buttons Frame
        button_frame = UIFactory.create_frame(self, padding=0)
        button_frame.grid(row=0, column=2, rowspan=2, sticky=tk.NS, padx=(5, 0))

        # Edit Button
        edit_btn = UIFactory.create_button(
            button_frame, text="✏️", style="ActionButton.TButton",
            command=lambda: on_edit(self.index) if on_edit else None
        )
        edit_btn.pack(side=tk.TOP, pady=1)

        # Delete Button
        delete_btn = UIFactory.create_button(
            button_frame, text="🗑️", style="ActionButton.TButton",
            command=lambda: on_delete(self.index) if on_delete else None
        )
        delete_btn.pack(side=tk.TOP, pady=1)

        # Move Up Button (only pack if callback provided)
        if on_move_up:
            up_btn = UIFactory.create_button(
                button_frame, text="⬆️", style="ActionButton.TButton",
                command=lambda: on_move_up(self.index)
            )
            up_btn.pack(side=tk.TOP, pady=1)
        else: # Add placeholder padding if button missing
            tk.Frame(button_frame, height=5).pack(side=tk.TOP)


        # Move Down Button (only pack if callback provided)
        if on_move_down:
            down_btn = UIFactory.create_button(
                button_frame, text="⬇️", style="ActionButton.TButton",
                command=lambda: on_move_down(self.index)
            )
            down_btn.pack(side=tk.TOP, pady=1)
        else: # Add placeholder padding
             tk.Frame(button_frame, height=5).pack(side=tk.TOP)

        # --- Event Bindings ---
        # Bind clicks on all major elements to trigger selection
        clickable_widgets = [self, self.icon_label, self.title_label, self.desc_label]
        for widget in clickable_widgets:
            widget.bind("<Button-1>", self._on_click)
            # Bind double-click on labels/icon to edit action
            if widget != self:
                widget.bind("<Double-Button-1>", lambda e, idx=self.index: on_edit(idx) if on_edit else None)
        # Double-click on frame itself also edits
        self.bind("<Double-Button-1>", lambda e, idx=self.index: on_edit(idx) if on_edit else None)

        # Hover effect (optional, can make UI feel more responsive)
        self.bind("<Enter>", lambda e: self.configure(style="ActionItem.TFrame")) # Default hover style TBD
        self.bind("<Leave>", self._update_visual_state) # Revert based on selection

    def _get_action_description(self, action_data: Dict[str, Any]) -> str:
        """Generate a concise, human-readable description of the action."""
        action_type = action_data.get("type", "Unknown")
        params = {k: v for k, v in action_data.items() if k not in ["type", "name"]}
        desc = f"{action_type}" # Start with type

        # Add most relevant parameter based on type
        if action_type == "Navigate" and "url" in params: desc = f"Go to: {params['url'][:50]}..." if len(params['url'])>50 else f"Go to: {params['url']}"
        elif action_type == "Click" and "selector" in params: desc = f"Click: {params['selector']}"
        elif action_type == "Type" and "selector" in params:
            value_disp = params.get('value_key', '')
            if params.get('value_type') == 'credential': value_disp = f"[{value_disp}]"
            else: value_disp = f"'{value_disp[:20]}...' " if len(value_disp)>20 else f"'{value_disp}'"
            desc = f"Type {value_disp} into: {params['selector']}"
        elif action_type == "Wait" and "duration_seconds" in params: desc = f"Wait: {params['duration_seconds']} sec"
        elif action_type == "Screenshot" and "file_path" in params: desc = f"Save Screenshot: {os.path.basename(params['file_path'])}"
        elif action_type == "Conditional": desc = f"If ({params.get('condition_type', '...')})"
        elif action_type == "Loop": desc = f"Loop ({params.get('loop_type', '...')})"
        elif action_type == "ErrorHandling": desc = "Try / Catch Block"
        elif action_type == "Template": desc = f"Run Template: {params.get('template_name', '...')}"
        elif action_type == "JavaScriptCondition": desc = f"Check JS: {params.get('script', '')[:30]}..." if params.get('script') else "Check JS"
        # Add more descriptions...
        else: desc = f"Configure {action_type}..." # Generic fallback

        return desc

    def _on_click(self, event=None) -> None:
        """Handle click event to select this item and notify parent."""
        if not self.selected:
            # Generate event *before* changing style, parent list handles selection logic
            logger.debug(f"Action Item {self.index} clicked, generating <<ActionSelected>>")
            self.event_generate("<<ActionSelected>>")
            # Note: The WorkflowActionList should handle calling select()/deselect()

    def select(self) -> None:
        """Select this action item (visually)."""
        if not self.selected:
            self.selected = True
            self._update_visual_state()
            logger.debug(f"Action Item {self.index} visually selected.")

    def deselect(self) -> None:
        """Deselect this action item (visually)."""
        if self.selected:
            self.selected = False
            self._update_visual_state()
            logger.debug(f"Action Item {self.index} visually deselected.")

    def _update_visual_state(self, event=None):
        """Update background/relief based on selection state."""
        if self.selected:
            self.configure(style="SelectedAction.TFrame")
        else:
            self.configure(style="ActionItem.TFrame")
