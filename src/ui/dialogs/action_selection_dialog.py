"""Dialog for selecting action types with a visual, clickable interface."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, List, Any

# Core imports
from src.core.actions.factory import ActionFactory
# UI imports
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class ActionSelectionDialog(tk.Toplevel):
    """
    A modal dialog for selecting action types with a visual, clickable interface.

    Groups actions by category and displays them as buttons with descriptions.
    Includes search functionality.
    """

    # --- Action Categorization & Descriptions ---
    ACTION_CATEGORIES = {
        "Navigation": ["Navigate"],
        "Interaction": ["Click", "Type"],
        "Waiting": ["Wait"],
        "Data & Verification": ["Screenshot", "JavaScriptCondition"],
        "Control Flow": ["Conditional"],
        # Removed per YAGNI: "Loop", "ErrorHandling", "Template"
    }

    ACTION_DESCRIPTIONS = {
        "Navigate": "Go to a specific web address (URL).",
        "Click": "Simulate a mouse click on an element (button, link, etc.).",
        "Type": "Enter text or credentials into an input field.",
        "Wait": "Pause execution for a fixed duration.",
        "Screenshot": "Capture an image of the current browser window.",
        "Conditional": "Execute different actions based on a condition (If/Else).",
        "JavaScriptCondition": "Evaluate a JavaScript expression for conditions."
        # Removed per YAGNI: Loop, ErrorHandling, Template
    }

    ACTION_ICONS = { # Optional icons
        "Navigate": "🌐", "Click": "👆", "Type": "⌨️", "Wait": "⏱️",
        "Screenshot": "📷", "Conditional": "🔀", "JavaScriptCondition": "🧪"
        # Removed per YAGNI: Loop, ErrorHandling, Template
    }

    def __init__(self, parent: tk.Widget):
        """Initialize the Action Selection Dialog."""
        super().__init__(parent)
        self.parent = parent
        self.selected_action: Optional[str] = None

        self.title("Select Action Type")
        # Make resizable for different screen sizes
        self.resizable(True, True)
        # Adjust initial size
        self.geometry("700x550")
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Get registered action types to filter available actions
        try:
            self.registered_actions = ActionFactory.get_registered_action_types()
            if not self.registered_actions:
                 logger.error("No actions registered in ActionFactory!")
                 # Show error and destroy?
                 messagebox.showerror("Error", "No actions available.", parent=parent)
                 self.destroy()
                 return
        except Exception as e:
            logger.exception("Failed to get registered actions from ActionFactory.")
            messagebox.showerror("Error", f"Failed to load actions: {e}", parent=parent)
            self.destroy()
            return

        # Store references to created button frames for filtering
        self._action_widgets: List[Dict[str, Any]] = []

        try:
            self._create_widgets()
        except Exception as e:
            logger.exception("Failed to create ActionSelectionDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize action selection: {e}", parent=parent)
            self.destroy()
            return

        self.grab_set() # Make modal
        self._center_window()
        self.wait_window() # Make it blocking

    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(1, weight=1) # Allow notebook/content to expand
        main_frame.columnconfigure(0, weight=1)

        # --- Search Frame ---
        search_frame = UIFactory.create_frame(main_frame, padding="5")
        search_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 5))
        search_frame.columnconfigure(1, weight=1)

        UIFactory.create_label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = UIFactory.create_entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=tk.EW)
        self.search_var.trace_add("write", self._on_search)
        search_entry.focus_set() # Focus search bar initially

        # --- Content Area (Notebook or Single Scrollable Frame) ---
        # Using a single scrollable frame might be simpler than notebook for filtering
        content_canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
        content_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=content_canvas.yview)
        content_canvas.configure(yscrollcommand=content_scrollbar.set)

        content_canvas.grid(row=1, column=0, sticky=tk.NSEW)
        content_scrollbar.grid(row=1, column=1, sticky=tk.NS)

        # Frame inside the canvas to hold all categories and actions
        self.scrollable_content_frame = UIFactory.create_frame(content_canvas, padding=5)
        canvas_window = content_canvas.create_window((0, 0), window=self.scrollable_content_frame, anchor=tk.NW)

        self.scrollable_content_frame.bind("<Configure>", lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
        content_canvas.bind("<Configure>", lambda e: content_canvas.itemconfig(canvas_window, width=e.width))
        # Bind mouse wheel for scrolling (might need platform-specific adjustments)
        self.bind_all("<MouseWheel>", lambda e: content_canvas.yview_scroll(int(-1*(e.delta/120)), "units"), add='+')
        self.bind_all("<Button-4>", lambda e: content_canvas.yview_scroll(-1, "units"), add='+') # Linux scroll up
        self.bind_all("<Button-5>", lambda e: content_canvas.yview_scroll(1, "units"), add='+') # Linux scroll down

        # --- Populate Content Frame ---
        self._populate_content_frame(self.scrollable_content_frame)

        # --- Buttons ---
        button_frame = UIFactory.create_frame(main_frame, padding="5")
        button_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        # Add padding to push button right
        button_frame.columnconfigure(0, weight=1)

        cancel_button = UIFactory.create_button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.grid(row=0, column=1, padx=5) # Place on right

        # Bind Enter key to select first visible action (if any) after search? (Optional)
        self.bind('<Return>', self._select_first_visible)

    def _populate_content_frame(self, parent_frame: ttk.Frame):
        """Populate the content frame with categories and action buttons."""
        parent_frame.columnconfigure(0, weight=1) # Allow action items to expand horizontally
        current_row = 0
        self._action_widgets = [] # Clear previous list

        for category, action_types in self.ACTION_CATEGORIES.items():
            # Filter actions that are actually registered
            available_actions = [at for at in action_types if at in self.registered_actions]
            if not available_actions: continue # Skip empty categories

            # Category Header
            category_label = UIFactory.create_label(parent_frame, text=category, font=("TkDefaultFont", 12, "bold"))
            category_label.grid(row=current_row, column=0, sticky=tk.W, pady=(10, 5))
            current_row += 1

            # Actions in this category (using grid for better alignment)
            category_frame = UIFactory.create_frame(parent_frame)
            category_frame.grid(row=current_row, column=0, sticky=tk.NSEW)
            # Configure columns for action items (e.g., 3 columns)
            num_columns = 3
            for i in range(num_columns): category_frame.columnconfigure(i, weight=1, uniform="action_col")
            current_row += 1
            action_row, action_col = 0, 0

            for action_type in available_actions:
                description = self.ACTION_DESCRIPTIONS.get(action_type, "No description available.")
                icon = self.ACTION_ICONS.get(action_type, "")

                # Frame for each action item (card-like)
                action_item_frame = UIFactory.create_frame(category_frame, padding=5, relief=tk.RAISED, borderwidth=1)
                action_item_frame.grid(row=action_row, column=action_col, sticky=tk.NSEW, padx=3, pady=3)
                action_item_frame.columnconfigure(0, weight=1)

                # Action Name (Button)
                button_text = f"{icon} {action_type}".strip()
                action_button = UIFactory.create_button(
                    action_item_frame,
                    text=button_text,
                    command=lambda at=action_type: self._on_action_selected(at),
                    anchor=tk.W, # Align text left
                )
                action_button.grid(row=0, column=0, sticky=tk.EW, pady=(0, 3))

                # Action Description
                desc_label = UIFactory.create_label(action_item_frame, text=description, wraplength=150, justify=tk.LEFT, anchor=tk.NW)
                desc_label.grid(row=1, column=0, sticky=tk.NSEW)

                # Make frame clickable too
                action_item_frame.bind("<Button-1>", lambda e, at=action_type: self._on_action_selected(at))
                action_button.bind("<Button-1>", lambda e, at=action_type: self._on_action_selected(at))
                desc_label.bind("<Button-1>", lambda e, at=action_type: self._on_action_selected(at))


                # Store reference for filtering
                self._action_widgets.append({
                    'frame': action_item_frame,
                    'name': action_type,
                    'description': description
                })

                action_col += 1
                if action_col >= num_columns:
                    action_col = 0
                    action_row += 1

    def _on_action_selected(self, action_type: str):
        """Handle action selection."""
        logger.info(f"Action type selected: {action_type}")
        self.selected_action = action_type
        self.destroy()

    def _on_cancel(self):
        """Close the dialog without selecting an action."""
        logger.debug("Action selection cancelled.")
        self.selected_action = None
        self.destroy()

    def _on_search(self, *args):
        """Filter visible actions based on search text."""
        search_term = self.search_var.get().lower().strip()
        logger.debug(f"Filtering actions by: '{search_term}'")

        visible_count = 0
        for item_info in self._action_widgets:
            frame = item_info['frame']
            name = item_info['name'].lower()
            description = item_info['description'].lower()

            is_match = search_term in name or search_term in description
            if is_match:
                frame.grid() # Show using grid
                visible_count += 1
            else:
                frame.grid_remove() # Hide using grid_remove

        # Update scroll region after hiding/showing items
        self.scrollable_content_frame.update_idletasks()
        self.scrollable_content_frame.event_generate("<Configure>") # Trigger scroll region update
        logger.debug(f"{visible_count} actions match search.")

    def _select_first_visible(self, event=None):
         """Selects the first action currently visible."""
         for item_info in self._action_widgets:
              if item_info['frame'].winfo_manager(): # Check if managed by grid (visible)
                   self._on_action_selected(item_info['name'])
                   return # Select the first one found
         logger.debug("Enter pressed, but no visible action found to select.")


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
        # wait_window() is called implicitly by grab_set() + main event loop
        # This method is just for clarity in the caller if needed, but not strictly necessary
        # for a blocking dialog created as a Toplevel with grab_set().
        # The result is retrieved after the Toplevel window is destroyed.
        return self.selected_action # Will be None until selection or cancel
