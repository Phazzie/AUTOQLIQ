"""Base class for UI testing in AutoQliq."""

import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


class UITestBase(unittest.TestCase):
    """Base class for UI testing in AutoQliq.
    
    This class provides common functionality for testing UI components:
    - Setting up a Tkinter root window
    - Mocking common dialogs and message boxes
    - Utility methods for interacting with UI components
    - Cleanup after tests
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a root window for testing
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Set up common mocks
        self.setup_mocks()
        
        logger.debug("UI test setup complete")
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Destroy the root window
        self.root.destroy()
        
        # Stop all patches
        for patcher in getattr(self, '_patchers', []):
            patcher.stop()
        
        logger.debug("UI test teardown complete")
    
    def setup_mocks(self):
        """Set up common mocks for UI testing."""
        self._patchers = []
        
        # Mock tkinter dialogs
        self.mock_simpledialog()
        self.mock_messagebox()
        self.mock_filedialog()
    
    def mock_simpledialog(self):
        """Mock tkinter.simpledialog for testing."""
        patcher = patch('tkinter.simpledialog')
        self.mock_simpledialog_module = patcher.start()
        self._patchers.append(patcher)
        
        # Configure default return values
        self.mock_simpledialog_module.askstring.return_value = "Test Input"
        
        return self.mock_simpledialog_module
    
    def mock_messagebox(self):
        """Mock tkinter.messagebox for testing."""
        patcher = patch('tkinter.messagebox')
        self.mock_messagebox_module = patcher.start()
        self._patchers.append(patcher)
        
        # Configure default return values
        self.mock_messagebox_module.askyesno.return_value = True
        self.mock_messagebox_module.askokcancel.return_value = True
        self.mock_messagebox_module.showinfo.return_value = None
        self.mock_messagebox_module.showwarning.return_value = None
        self.mock_messagebox_module.showerror.return_value = None
        
        return self.mock_messagebox_module
    
    def mock_filedialog(self):
        """Mock tkinter.filedialog for testing."""
        patcher = patch('tkinter.filedialog')
        self.mock_filedialog_module = patcher.start()
        self._patchers.append(patcher)
        
        # Configure default return values
        self.mock_filedialog_module.askopenfilename.return_value = "/path/to/file.txt"
        self.mock_filedialog_module.asksaveasfilename.return_value = "/path/to/save.txt"
        self.mock_filedialog_module.askdirectory.return_value = "/path/to/directory"
        
        return self.mock_filedialog_module
    
    def create_mock_presenter(self, presenter_class):
        """Create a mock presenter for testing views."""
        mock_presenter = MagicMock(spec=presenter_class)
        return mock_presenter
    
    # UI Interaction Helpers
    
    def click_button(self, button):
        """Simulate clicking a button."""
        button.invoke()
    
    def select_listbox_item(self, listbox, index):
        """Select an item in a listbox."""
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        listbox.event_generate("<<ListboxSelect>>")
    
    def set_combobox_value(self, combobox, value):
        """Set a value in a combobox."""
        combobox.set(value)
        combobox.event_generate("<<ComboboxSelected>>")
    
    def set_entry_value(self, entry, value):
        """Set a value in an entry widget."""
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.event_generate("<FocusOut>")
    
    def set_text_value(self, text_widget, value):
        """Set a value in a text widget."""
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", value)
    
    def get_listbox_items(self, listbox):
        """Get all items in a listbox."""
        return [listbox.get(i) for i in range(listbox.size())]
    
    def get_combobox_items(self, combobox):
        """Get all items in a combobox."""
        return combobox['values']
    
    def assert_widget_state(self, widget, state):
        """Assert that a widget is in the expected state."""
        self.assertEqual(widget['state'], state)
    
    def assert_widget_text(self, widget, expected_text):
        """Assert that a widget contains the expected text."""
        if isinstance(widget, tk.Text):
            actual_text = widget.get("1.0", tk.END).strip()
        elif isinstance(widget, (tk.Entry, ttk.Entry, ttk.Combobox)):
            actual_text = widget.get()
        elif isinstance(widget, (tk.Label, ttk.Label)):
            actual_text = widget['text']
        else:
            raise ValueError(f"Unsupported widget type: {type(widget)}")
        
        self.assertEqual(actual_text, expected_text)
