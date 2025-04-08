#!/usr/bin/env python3
"""
Unit tests for UIFactory class in src/ui/common/ui_factory.py.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Import the module under test
from src.ui.common.ui_factory import UIFactory


class TestUIFactory(unittest.TestCase):
    """
    Test cases for the UIFactory class.
    
    This test suite verifies that UIFactory correctly creates UI components
    with appropriate configurations.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a root window for testing
        self.root = tk.Tk()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Destroy the root window
        self.root.destroy()
    
    def test_create_scrolled_text(self):
        """Test creating a scrolled text component."""
        # Create a scrolled text component
        result = UIFactory.create_scrolled_text(
            self.root,
            height=10,
            width=50,
            wrap=tk.WORD,
            state=tk.NORMAL
        )
        
        # Verify the result structure
        self.assertIn("frame", result)
        self.assertIn("text", result)
        self.assertIn("scrollbar", result)
        
        # Verify the types of returned widgets
        self.assertIsInstance(result["frame"], tk.Frame)
        self.assertIsInstance(result["text"], tk.Text)
        self.assertIsInstance(result["scrollbar"], ttk.Scrollbar)
        
        # Verify the text widget configuration
        text_widget = result["text"]
        self.assertEqual(text_widget["height"], 10)
        self.assertEqual(text_widget["width"], 50)
        self.assertEqual(text_widget["wrap"], tk.WORD)
        self.assertEqual(text_widget["state"], tk.NORMAL)
        
        # Verify scrollbar command is connected to text widget
        scrollbar = result["scrollbar"]
        self.assertEqual(scrollbar["command"], text_widget.yview)
        self.assertEqual(text_widget["yscrollcommand"], scrollbar.set)
    
    def test_create_scrolled_text_with_custom_params(self):
        """Test creating a scrolled text component with custom parameters."""
        # Create a scrolled text component with custom parameters
        result = UIFactory.create_scrolled_text(
            self.root,
            height=20,
            width=80,
            wrap=tk.CHAR,
            state=tk.DISABLED,
            font=("Courier", 12),
            bg="black",
            fg="white"
        )
        
        # Verify the text widget configuration with custom parameters
        text_widget = result["text"]
        self.assertEqual(text_widget["height"], 20)
        self.assertEqual(text_widget["width"], 80)
        self.assertEqual(text_widget["wrap"], tk.CHAR)
        self.assertEqual(text_widget["state"], tk.DISABLED)
        
        # Verify font, bg, fg were passed through
        # Note: Font comparison may vary by platform, so test carefully
        self.assertEqual(text_widget["bg"], "black")
        self.assertEqual(text_widget["fg"], "white")
        
        # Font might be represented differently, but should contain our values
        font_obj = tkfont.Font(font=text_widget["font"])
        self.assertEqual(font_obj.actual()["family"], "Courier")
        self.assertEqual(font_obj.actual()["size"], 12)
    
    def test_create_labeled_entry(self):
        """Test creating a labeled entry component."""
        # Create a labeled entry component
        result = UIFactory.create_labeled_entry(
            self.root,
            label_text="Username:",
            width=30
        )
        
        # Verify the result structure
        self.assertIn("frame", result)
        self.assertIn("label", result)
        self.assertIn("entry", result)
        
        # Verify the types of returned widgets
        self.assertIsInstance(result["frame"], tk.Frame)
        self.assertIsInstance(result["label"], ttk.Label)
        self.assertIsInstance(result["entry"], ttk.Entry)
        
        # Verify the label configuration
        label_widget = result["label"]
        self.assertEqual(label_widget["text"], "Username:")
        
        # Verify the entry configuration
        entry_widget = result["entry"]
        self.assertEqual(entry_widget["width"], 30)
    
    def test_create_labeled_entry_with_custom_params(self):
        """Test creating a labeled entry component with custom parameters."""
        # Create a labeled entry component with custom parameters
        result = UIFactory.create_labeled_entry(
            self.root,
            label_text="Password:",
            width=20,
            show="*",
            font=("Arial", 10),
            label_width=15
        )
        
        # Verify the entry configuration with custom parameters
        entry_widget = result["entry"]
        self.assertEqual(entry_widget["width"], 20)
        self.assertEqual(entry_widget["show"], "*")
        
        # Verify label with custom width
        label_widget = result["label"]
        self.assertEqual(label_widget["text"], "Password:")
        self.assertEqual(label_widget["width"], 15)
    
    def test_create_button(self):
        """Test creating a button component."""
        # Create a mock command function
        mock_command = MagicMock()
        
        # Create a button component
        button = UIFactory.create_button(
            self.root,
            text="Click Me",
            command=mock_command
        )
        
        # Verify the button type
        self.assertIsInstance(button, ttk.Button)
        
        # Verify the button configuration
        self.assertEqual(button["text"], "Click Me")
        
        # Simulate click and verify command was called
        button.invoke()
        mock_command.assert_called_once()
    
    def test_create_button_with_custom_params(self):
        """Test creating a button component with custom parameters."""
        # Create a button with custom parameters
        button = UIFactory.create_button(
            self.root,
            text="Save",
            command=None,
            width=20,
            state=tk.DISABLED
        )
        
        # Verify custom parameters
        self.assertEqual(button["text"], "Save")
        self.assertEqual(button["width"], 20)
        self.assertEqual(button["state"], tk.DISABLED)
    
    def test_create_combobox(self):
        """Test creating a combobox component."""
        # Create a combobox component
        values = ["Option 1", "Option 2", "Option 3"]
        combobox = UIFactory.create_combobox(
            self.root,
            values=values,
            width=30
        )
        
        # Verify the combobox type
        self.assertIsInstance(combobox, ttk.Combobox)
        
        # Verify the combobox configuration
        self.assertEqual(combobox["width"], 30)
        self.assertEqual(combobox["values"], values)
    
    def test_create_combobox_with_custom_params(self):
        """Test creating a combobox with custom parameters."""
        # Create a combobox with custom parameters
        values = ["Red", "Green", "Blue"]
        combobox = UIFactory.create_combobox(
            self.root,
            values=values,
            width=15,
            state="readonly",
            font=("Helvetica", 12)
        )
        
        # Verify custom parameters
        self.assertEqual(combobox["width"], 15)
        self.assertEqual(combobox["values"], values)
        self.assertEqual(combobox["state"], "readonly")
    
    def test_create_checkbox(self):
        """Test creating a checkbox component."""
        # Create a variable for the checkbox
        var = tk.BooleanVar()
        
        # Create a checkbox component
        checkbox = UIFactory.create_checkbox(
            self.root,
            text="Enable feature",
            variable=var
        )
        
        # Verify the checkbox type
        self.assertIsInstance(checkbox, ttk.Checkbutton)
        
        # Verify the checkbox configuration
        self.assertEqual(checkbox["text"], "Enable feature")
        self.assertEqual(checkbox["variable"], var)
        
        # Verify initial state
        self.assertFalse(var.get())
        
        # Simulate click and verify variable changed
        checkbox.invoke()
        self.assertTrue(var.get())
    
    def test_create_radio_button(self):
        """Test creating a radio button component."""
        # Create a variable for the radio button
        var = tk.StringVar()
        
        # Create a radio button component
        radio = UIFactory.create_radio_button(
            self.root,
            text="Option A",
            variable=var,
            value="A"
        )
        
        # Verify the radio button type
        self.assertIsInstance(radio, ttk.Radiobutton)
        
        # Verify the radio button configuration
        self.assertEqual(radio["text"], "Option A")
        self.assertEqual(radio["variable"], var)
        self.assertEqual(radio["value"], "A")
        
        # Verify initial state
        self.assertEqual(var.get(), "")
        
        # Simulate click and verify variable changed
        radio.invoke()
        self.assertEqual(var.get(), "A")
    
    def test_create_label(self):
        """Test creating a label component."""
        # Create a label component
        label = UIFactory.create_label(
            self.root,
            text="Hello, World!"
        )
        
        # Verify the label type
        self.assertIsInstance(label, ttk.Label)
        
        # Verify the label configuration
        self.assertEqual(label["text"], "Hello, World!")
    
    def test_create_label_with_custom_params(self):
        """Test creating a label with custom parameters."""
        # Create a label with custom parameters
        label = UIFactory.create_label(
            self.root,
            text="Status: Ready",
            font=("Arial", 14, "bold"),
            foreground="green",
            background="white",
            anchor=tk.CENTER
        )
        
        # Verify custom parameters
        self.assertEqual(label["text"], "Status: Ready")
        self.assertEqual(label["foreground"], "green")
        self.assertEqual(label["background"], "white")
        self.assertEqual(label["anchor"], tk.CENTER)
    
    def test_create_frame(self):
        """Test creating a frame component."""
        # Create a frame component
        frame = UIFactory.create_frame(self.root)
        
        # Verify the frame type
        self.assertIsInstance(frame, ttk.Frame)
    
    def test_create_frame_with_custom_params(self):
        """Test creating a frame with custom parameters."""
        # Create a frame with custom parameters
        frame = UIFactory.create_frame(
            self.root,
            padding=10,
            borderwidth=2,
            relief=tk.RAISED
        )
        
        # Verify custom parameters
        self.assertEqual(frame["padding"], 10)
        self.assertEqual(frame["borderwidth"], 2)
        self.assertEqual(frame["relief"], tk.RAISED)


if __name__ == '__main__':
    unittest.main()