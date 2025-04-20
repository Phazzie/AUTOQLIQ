"""Tests for UI components.

This module tests the UI components of the AutoQliq application.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from typing import Dict, Any, List, Optional

from src.ui.views.base_view import BaseView
from src.ui.presenters.base_presenter import BasePresenter
from src.ui.interfaces.view_interfaces import IView
from src.ui.interfaces.presenter_interfaces import IPresenter
from src.core.exceptions import ValidationError, ServiceError

class TestBaseView(unittest.TestCase):
    """Test case for BaseView."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        
        # Create a mock presenter
        self.presenter = MagicMock(spec=IPresenter)
        
        # Create the view
        self.view = BaseView(self.root)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.root.destroy()
    
    def test_show_error(self):
        """Test showing an error message."""
        with patch("tkinter.messagebox.showerror") as mock_showerror:
            self.view.show_error("Test error message")
            mock_showerror.assert_called_once_with("Error", "Test error message")
    
    def test_show_info(self):
        """Test showing an info message."""
        with patch("tkinter.messagebox.showinfo") as mock_showinfo:
            self.view.show_info("Test info message")
            mock_showinfo.assert_called_once_with("Information", "Test info message")
    
    def test_show_loading(self):
        """Test showing and hiding the loading indicator."""
        # Show loading
        self.view.show_loading(True)
        self.assertTrue(self.view._loading_var.get())
        
        # Hide loading
        self.view.show_loading(False)
        self.assertFalse(self.view._loading_var.get())
    
    def test_create_labeled_entry(self):
        """Test creating a labeled entry field."""
        entry = self.view.create_labeled_entry(self.root, "Test Label:", "Default Value", 30)
        self.assertIsInstance(entry, tk.Entry)
        self.assertEqual(entry.get(), "Default Value")
    
    def test_create_labeled_combobox(self):
        """Test creating a labeled combobox."""
        values = ["Option 1", "Option 2", "Option 3"]
        combobox = self.view.create_labeled_combobox(self.root, "Test Label:", values, 1, 30)
        self.assertIsInstance(combobox, tk.ttk.Combobox)
        self.assertEqual(combobox["values"], values)
        self.assertEqual(combobox.get(), "Option 2")  # Default index 1
    
    def test_create_button(self):
        """Test creating a button."""
        callback = MagicMock()
        button = self.view.create_button(self.root, "Test Button", callback, 15)
        self.assertIsInstance(button, tk.ttk.Button)
        self.assertEqual(button["text"], "Test Button")
        self.assertEqual(button["width"], 15)
        
        # Simulate button click
        button.invoke()
        callback.assert_called_once()
    
    def test_create_button_frame(self):
        """Test creating a button frame."""
        frame = self.view.create_button_frame(self.root)
        self.assertIsInstance(frame, tk.ttk.Frame)

class TestBasePresenter(unittest.TestCase):
    """Test case for BasePresenter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock view
        self.view = MagicMock(spec=IView)
        
        # Create the presenter
        self.presenter = BasePresenter()
        self.presenter.set_view(self.view)
    
    def test_initialize(self):
        """Test presenter initialization."""
        self.presenter.initialize()
        # No assertions needed, just checking that it doesn't raise
    
    def test_initialize_no_view(self):
        """Test initialization without a view."""
        presenter = BasePresenter()
        with self.assertRaises(ValueError):
            presenter.initialize()
    
    def test_handle_error(self):
        """Test error handling."""
        # Test with ValidationError
        error = ValidationError("Test validation error")
        self.presenter.handle_error(error)
        self.view.show_error.assert_called_with("Validation error: Test validation error")
        
        # Test with ServiceError
        self.view.show_error.reset_mock()
        error = ServiceError("Test service error")
        self.presenter.handle_error(error)
        self.view.show_error.assert_called_with("Service error: Test service error")
        
        # Test with custom message
        self.view.show_error.reset_mock()
        error = Exception("Test exception")
        self.presenter.handle_error(error, "Custom error message")
        self.view.show_error.assert_called_with("Custom error message")
    
    def test_run_in_background(self):
        """Test running a task in the background."""
        # Create a task that returns a value
        task = MagicMock(return_value="Task result")
        
        # Create a completion callback
        on_complete = MagicMock()
        
        # Run the task in the background
        self.presenter.run_in_background(task, on_complete)
        
        # Wait for the task to complete
        import time
        time.sleep(0.1)
        
        # Verify that the task was executed
        task.assert_called_once()
        
        # Verify that the completion callback was called with the task result
        on_complete.assert_called_once_with("Task result")
        
        # Verify that the loading indicator was shown and hidden
        self.view.show_loading.assert_any_call(True)
        self.view.show_loading.assert_any_call(False)
    
    def test_run_in_background_error(self):
        """Test running a task in the background that raises an error."""
        # Create a task that raises an exception
        error = Exception("Task error")
        task = MagicMock(side_effect=error)
        
        # Create an error callback
        on_error = MagicMock()
        
        # Run the task in the background
        self.presenter.run_in_background(task, on_error=on_error)
        
        # Wait for the task to complete
        import time
        time.sleep(0.1)
        
        # Verify that the task was executed
        task.assert_called_once()
        
        # Verify that the error callback was called with the exception
        on_error.assert_called_once_with(error)
        
        # Verify that the loading indicator was shown and hidden
        self.view.show_loading.assert_any_call(True)
        self.view.show_loading.assert_any_call(False)
    
    def test_cleanup(self):
        """Test presenter cleanup."""
        # Create a background task
        task = MagicMock()
        self.presenter.run_in_background(task)
        
        # Wait for the task to start
        import time
        time.sleep(0.1)
        
        # Cleanup
        self.presenter.cleanup()
        
        # Verify that the background tasks list is empty
        self.assertEqual(len(self.presenter._background_tasks), 0)

if __name__ == "__main__":
    unittest.main()
