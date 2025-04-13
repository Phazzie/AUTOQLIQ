#!/usr/bin/env python3
"""
Unit tests for ScrolledList component in src/ui/components/scrolled_list.py.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk

# Import the module under test
from src.ui.components.scrolled_list import ScrolledList
from src.core.exceptions import UIError


class TestScrolledList(unittest.TestCase):
    """
    Test cases for the ScrolledList component.
    
    This test suite verifies that ScrolledList correctly handles list items,
    selection, and event callbacks.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock Tk root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock the UIFactory.create_scrolled_listbox method
        self.listbox_widget = MagicMock(spec=tk.Listbox)
        self.scrollbar_widget = MagicMock(spec=ttk.Scrollbar)
        self.frame_widget = MagicMock(spec=ttk.Frame)
        
        # Mock UIFactory to return our mock widgets
        factory_patcher = patch('src.ui.common.ui_factory.UIFactory.create_scrolled_listbox')
        self.mock_factory = factory_patcher.start()
        self.mock_factory.return_value = {
            "frame": self.frame_widget,
            "listbox": self.listbox_widget,
            "scrollbar": self.scrollbar_widget
        }
        self.addCleanup(factory_patcher.stop)
        
        # Create the ScrolledList instance
        self.scrolled_list = ScrolledList(
            parent=self.root,
            height=10,
            width=50,
            selectmode=tk.SINGLE
        )
    
    def test_init(self):
        """Test initialization of ScrolledList component."""
        # Verify the UIFactory was called with the correct parameters
        self.mock_factory.assert_called_once_with(
            self.root,
            height=10,
            width=50,
            selectmode=tk.SINGLE
        )
        
        # Verify the widgets were stored properly
        self.assertEqual(self.scrolled_list.frame, self.frame_widget)
        self.assertEqual(self.scrolled_list.listbox, self.listbox_widget)
        self.assertEqual(self.scrolled_list.scrollbar, self.scrollbar_widget)
        
        # Verify the main widget was set
        self.assertEqual(self.scrolled_list._widget, self.frame_widget)
    
    def test_init_with_on_select(self):
        """Test initialization with on_select callback."""
        # Create a mock callback
        on_select = MagicMock()
        
        # Create a ScrolledList with the callback
        scrolled_list = ScrolledList(
            parent=self.root,
            height=10,
            width=50,
            on_select=on_select
        )
        
        # Verify the callback was bound to the listbox widget
        self.listbox_widget.bind.assert_called_once_with("<<ListboxSelect>>", on_select)
    
    def test_init_error(self):
        """Test error handling during initialization."""
        # Make the factory raise an exception
        self.mock_factory.side_effect = Exception("Factory error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            ScrolledList(parent=self.root)
        
        # Verify the error message
        self.assertIn("Failed to create ScrolledList", str(context.exception))
    
    def test_set_items(self):
        """Test setting multiple items in the listbox."""
        # Set the items
        items = ["Item 1", "Item 2", "Item 3"]
        self.scrolled_list.set_items(items)
        
        # Verify the listbox was cleared
        self.listbox_widget.delete.assert_called_once_with(0, tk.END)
        
        # Verify the items were inserted
        self.assertEqual(self.listbox_widget.insert.call_count, 3)
        self.listbox_widget.insert.assert_any_call(tk.END, "Item 1")
        self.listbox_widget.insert.assert_any_call(tk.END, "Item 2")
        self.listbox_widget.insert.assert_any_call(tk.END, "Item 3")
    
    def test_set_items_error(self):
        """Test error handling when setting items."""
        # Make the listbox widget raise an exception
        self.listbox_widget.delete.side_effect = Exception("Delete error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_list.set_items(["Item 1"])
        
        # Verify the error message
        self.assertIn("Failed to set items in ScrolledList", str(context.exception))
    
    def test_add_item(self):
        """Test adding a single item to the listbox."""
        # Add an item
        self.scrolled_list.add_item("New Item")
        
        # Verify the item was inserted
        self.listbox_widget.insert.assert_called_once_with(tk.END, "New Item")
    
    def test_add_item_error(self):
        """Test error handling when adding an item."""
        # Make the listbox widget raise an exception
        self.listbox_widget.insert.side_effect = Exception("Insert error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_list.add_item("New Item")
        
        # Verify the error message
        self.assertIn("Failed to add item to ScrolledList", str(context.exception))
    
    def test_remove_selected(self):
        """Test removing selected items from the listbox."""
        # Mock the curselection method to return selected indices
        self.listbox_widget.curselection.return_value = (1, 3)
        
        # Remove the selected items
        self.scrolled_list.remove_selected()
        
        # Verify the items were deleted in reverse order
        self.assertEqual(self.listbox_widget.delete.call_count, 2)
        self.listbox_widget.delete.assert_any_call(3)
        self.listbox_widget.delete.assert_any_call(1)
    
    def test_remove_selected_none(self):
        """Test removing selected items when none are selected."""
        # Mock the curselection method to return no selection
        self.listbox_widget.curselection.return_value = ()
        
        # Remove the selected items
        self.scrolled_list.remove_selected()
        
        # Verify no items were deleted
        self.listbox_widget.delete.assert_not_called()
    
    def test_remove_selected_error(self):
        """Test error handling when removing selected items."""
        # Make the listbox widget raise an exception
        self.listbox_widget.curselection.side_effect = Exception("Curselection error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_list.remove_selected()
        
        # Verify the error message
        self.assertIn("Failed to remove selected items from ScrolledList", str(context.exception))
    
    def test_get_selected_index(self):
        """Test getting the index of the selected item."""
        # Mock the curselection method to return a selected index
        self.listbox_widget.curselection.return_value = (2,)
        
        # Get the selected index
        index = self.scrolled_list.get_selected_index()
        
        # Verify the returned index
        self.assertEqual(index, 2)
    
    def test_get_selected_index_none(self):
        """Test getting the selected index when no item is selected."""
        # Mock the curselection method to return no selection
        self.listbox_widget.curselection.return_value = ()
        
        # Get the selected index
        index = self.scrolled_list.get_selected_index()
        
        # Verify the returned index is None
        self.assertIsNone(index)
    
    def test_get_selected_index_error(self):
        """Test error handling when getting the selected index."""
        # Make the listbox widget raise an exception
        self.listbox_widget.curselection.side_effect = Exception("Curselection error")
        
        # Verify the component raises a UIError
        with self.assertRaises(UIError) as context:
            self.scrolled_list.get_selected_index()
        
        # Verify the error message
        self.assertIn("Failed to get selected index from ScrolledList", str(context.exception))
    
    def test_get_selected_item(self):
        """Test getting the selected item."""
        # Mock the curselection method to return a selected index
        self.listbox_widget.curselection.return_value = (1,)
        
        # Mock the get method to return an item
        self.listbox_widget.get.return_value = "Selected Item"
        
        # Get the selected item
        item = self.scrolled_list.get_selected_item()
        
        # Verify the listbox get method was called with the correct index
        self.listbox_widget.get.assert_called_once_with(1)
        
        # Verify the returned item
        self.assertEqual(item, "Selected Item")
    
    def test_get_selected_item_none(self):
        """Test getting the selected item when no item is selected."""
        # Mock the curselection method to return no selection
        self.listbox_widget.curselection.return_value = ()
        
        # Get the selected item
        item = self.scrolled_list.get_selected_item()
        
        # Verify the returned item is None
        self.assertIsNone(item)
        
        # Verify the listbox get method was not called
        self.listbox_widget.get.assert_not_called()


if __name__ == '__main__':
    unittest.main()