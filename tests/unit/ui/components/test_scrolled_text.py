#!/usr/bin/env python3
"""
Unit tests for ScrolledText component in src/ui/components/scrolled_text.py.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk

# Import the module under test
from src.ui.components.scrolled_text import ScrolledText
from src.core.exceptions import UIError


class TestScrolledText(unittest.TestCase):
    """
    Test cases for the ScrolledText component.
    
    This test suite verifies that ScrolledText correctly handles text display,
    scrolling, and state management.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Tk root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock the UIFactory.create_scrolled_text method
        self.text_widget = MagicMock(spec=tk.Text)
        self.scrollbar_widget = MagicMock(spec=ttk.Scrollbar)
        self.frame_widget = MagicMock(spec=ttk.Frame)
        
        # Configure the text widget mock
        self.text_widget.__getitem__.return_value = tk.NORMAL
        
        # Mock UIFactory to return our mock widgets
        factory_patcher = patch('src.ui.common.ui_factory.UIFactory.create_scrolled_text')
        self.mock_factory = factory_patcher.start()
        self.mock_factory.return_value = {
            "frame": self.frame_widget,
            "text": self.text_widget,
            "scrollbar": self.scrollbar_widget
        }
        self.addCleanup(factory_patcher.stop)
        
        # Create the ScrolledText instance
        self.scrolled_text = ScrolledText(
            parent=self.root,
            height=10,
            width=50,
            wrap=tk.WORD,
            state=tk.NORMAL
        )
    
    def test_init(self):
        """Test initialization of ScrolledText component."""
        # Verify the UIFactory was called with the correct parameters
        self.mock_factory.assert_called_once_with(
            self.root,
            height=10,
            width=50,
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        
        # Verify the widgets were stored properly
        self.assertEqual(self.scrolled_text.frame, self.frame_widget)
        self.assertEqual(self.scrolled_text.text, self.text_widget)
        self.assertEqual(self.scrolled_text.scrollbar, self.scrollbar_widget)
        
        # Verify the main widget was set
        self.assertEqual(self.scrolled_text._widget, self.frame_widget)
    
    def test_init_with_on_change(self):
        """Test initialization with on_change callback."""
        # Create a mock callback
        on_change = MagicMock()
        
        # Create a ScrolledText with the callback
        scrolled_text = ScrolledText(
            parent=self.root,
            height=10,
            width=50,
            on_change=on_change
        )
        
        # Verify the callback was bound to the text widget
        self.text_widget.bind.assert_called_once_with("<<Modified>>", on_change)
    
    def test_init_error(self):
        """Test error handling during initialization."""
        # Make the factory raise an exception
        self.mock_factory.side_effect = Exception("Factory error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            ScrolledText(parent=self.root)
        
        # Verify the error message
        self.assertIn("Failed to create ScrolledText", str(context.exception))
    
    def test_set_text(self):
        """Test setting the text content."""
        # Set the text
        self.scrolled_text.set_text("Hello, world!")
        
        # Verify the text was cleared
        self.text_widget.delete.assert_called_once_with("1.0", tk.END)
        
        # Verify the text was inserted
        self.text_widget.insert.assert_called_once_with(tk.END, "Hello, world!")
    
    def test_set_text_error(self):
        """Test error handling when setting text."""
        # Make the text widget raise an exception
        self.text_widget.delete.side_effect = Exception("Delete error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_text.set_text("Hello, world!")
        
        # Verify the error message
        self.assertIn("Failed to set text in ScrolledText", str(context.exception))
    
    def test_append_text(self):
        """Test appending text to the content."""
        # Append text
        self.scrolled_text.append_text("More text")
        
        # Verify the text was inserted
        self.text_widget.insert.assert_called_once_with(tk.END, "More text")
        
        # Verify the view was scrolled to the end
        self.text_widget.see.assert_called_once_with(tk.END)
    
    def test_append_text_disabled(self):
        """Test appending text when the widget is disabled."""
        # Configure the text widget to be disabled
        self.text_widget.__getitem__.return_value = tk.DISABLED
        
        # Append text
        self.scrolled_text.append_text("More text")
        
        # Verify the state was changed to NORMAL
        self.text_widget.config.assert_any_call(state=tk.NORMAL)
        
        # Verify the text was inserted
        self.text_widget.insert.assert_called_once_with(tk.END, "More text")
        
        # Verify the view was scrolled to the end
        self.text_widget.see.assert_called_once_with(tk.END)
        
        # Verify the state was restored to DISABLED
        self.text_widget.config.assert_any_call(state=tk.DISABLED)
    
    def test_append_text_error(self):
        """Test error handling when appending text."""
        # Make the text widget raise an exception
        self.text_widget.insert.side_effect = Exception("Insert error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_text.append_text("More text")
        
        # Verify the error message
        self.assertIn("Failed to append text to ScrolledText", str(context.exception))
    
    def test_append_line(self):
        """Test appending a line of text to the content."""
        # Append a line
        self.scrolled_text.append_line("Line of text")
        
        # Verify the text was inserted with a newline
        self.text_widget.insert.assert_called_once_with(tk.END, "Line of text\n")
    
    def test_get_text(self):
        """Test getting the text content."""
        # Configure the text widget to return some text
        self.text_widget.get.return_value = "Text content"
        
        # Get the text
        text = self.scrolled_text.get_text()
        
        # Verify the text widget was called with the correct parameters
        self.text_widget.get.assert_called_once_with("1.0", tk.END)
        
        # Verify the returned text
        self.assertEqual(text, "Text content")
    
    def test_get_text_error(self):
        """Test error handling when getting text."""
        # Make the text widget raise an exception
        self.text_widget.get.side_effect = Exception("Get error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_text.get_text()
        
        # Verify the error message
        self.assertIn("Failed to get text from ScrolledText", str(context.exception))
    
    def test_clear(self):
        """Test clearing the text content."""
        # Clear the text
        self.scrolled_text.clear()
        
        # Verify the text was deleted
        self.text_widget.delete.assert_called_once_with("1.0", tk.END)
    
    def test_clear_disabled(self):
        """Test clearing text when the widget is disabled."""
        # Configure the text widget to be disabled
        self.text_widget.__getitem__.return_value = tk.DISABLED
        
        # Clear the text
        self.scrolled_text.clear()
        
        # Verify the state was changed to NORMAL
        self.text_widget.config.assert_any_call(state=tk.NORMAL)
        
        # Verify the text was deleted
        self.text_widget.delete.assert_called_once_with("1.0", tk.END)
        
        # Verify the state was restored to DISABLED
        self.text_widget.config.assert_any_call(state=tk.DISABLED)
    
    def test_clear_error(self):
        """Test error handling when clearing text."""
        # Make the text widget raise an exception
        self.text_widget.delete.side_effect = Exception("Delete error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_text.clear()
        
        # Verify the error message
        self.assertIn("Failed to clear ScrolledText", str(context.exception))
    
    def test_update(self):
        """Test updating the component state."""
        # Update the component
        self.scrolled_text.update()
        
        # No assertions needed, just verify it doesn't raise an exception
    
    def test_set_state(self):
        """Test setting the state of the text widget."""
        # Set the state
        self.scrolled_text.set_state(tk.DISABLED)
        
        # Verify the state was set
        self.text_widget.config.assert_called_once_with(state=tk.DISABLED)
    
    def test_set_state_error(self):
        """Test error handling when setting state."""
        # Make the text widget raise an exception
        self.text_widget.config.side_effect = Exception("Config error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_text.set_state(tk.DISABLED)
        
        # Verify the error message
        self.assertIn("Failed to set state of ScrolledText", str(context.exception))


if __name__ == '__main__':
    unittest.main()