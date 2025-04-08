#!/usr/bin/env python3
"""
Unit tests for UIComponent base class in src/ui/components/ui_component.py.
"""

import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

# Import the module under test
from src.ui.components.ui_component import UIComponent


class TestUIComponent(unittest.TestCase):
    """
    Test cases for the UIComponent abstract base class.
    
    This test suite verifies that UIComponent provides the expected interface
    and base functionality for UI components.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a root window for testing
        self.root = tk.Tk()
        
        # Create a concrete subclass of UIComponent for testing
        class ConcreteUIComponent(UIComponent):
            def __init__(self, parent):
                super().__init__(parent)
                self.frame = tk.Frame(parent)
                self._widget = self.frame
                self.setup_called = False
                self.update_called = False
            
            def setup(self):
                self.setup_called = True
            
            def update(self):
                self.update_called = True
        
        self.ConcreteUIComponent = ConcreteUIComponent
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Destroy the root window
        self.root.destroy()
    
    def test_init(self):
        """Test initialization of the component."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Verify attributes are set correctly
        self.assertEqual(component.parent, self.root)
        self.assertEqual(component._widget, component.frame)
        self.assertFalse(component.setup_called)
    
    def test_widget_property(self):
        """Test the widget property."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Verify widget property returns the correct widget
        self.assertEqual(component.widget, component._widget)
    
    def test_pack(self):
        """Test the pack method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's pack method
        component._widget.pack = MagicMock()
        
        # Call pack with some parameters
        component.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Verify pack was called on the widget with the correct parameters
        component._widget.pack.assert_called_once_with(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def test_grid(self):
        """Test the grid method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's grid method
        component._widget.grid = MagicMock()
        
        # Call grid with some parameters
        component.grid(row=0, column=1, sticky=tk.NSEW)
        
        # Verify grid was called on the widget with the correct parameters
        component._widget.grid.assert_called_once_with(row=0, column=1, sticky=tk.NSEW)
    
    def test_place(self):
        """Test the place method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's place method
        component._widget.place = MagicMock()
        
        # Call place with some parameters
        component.place(x=10, y=20, width=100, height=50)
        
        # Verify place was called on the widget with the correct parameters
        component._widget.place.assert_called_once_with(x=10, y=20, width=100, height=50)
    
    def test_grid_forget(self):
        """Test the grid_forget method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's grid_forget method
        component._widget.grid_forget = MagicMock()
        
        # Call grid_forget
        component.grid_forget()
        
        # Verify grid_forget was called on the widget
        component._widget.grid_forget.assert_called_once()
    
    def test_pack_forget(self):
        """Test the pack_forget method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's pack_forget method
        component._widget.pack_forget = MagicMock()
        
        # Call pack_forget
        component.pack_forget()
        
        # Verify pack_forget was called on the widget
        component._widget.pack_forget.assert_called_once()
    
    def test_place_forget(self):
        """Test the place_forget method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's place_forget method
        component._widget.place_forget = MagicMock()
        
        # Call place_forget
        component.place_forget()
        
        # Verify place_forget was called on the widget
        component._widget.place_forget.assert_called_once()
    
    def test_update(self):
        """Test the update method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Call update
        component.update()
        
        # Verify update was called on the concrete class
        self.assertTrue(component.update_called)
    
    def test_config(self):
        """Test the config method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's config method
        component._widget.config = MagicMock()
        
        # Call config with some parameters
        component.config(bg="white", fg="black")
        
        # Verify config was called on the widget with the correct parameters
        component._widget.config.assert_called_once_with(bg="white", fg="black")
    
    def test_configure(self):
        """Test the configure method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's configure method
        component._widget.configure = MagicMock()
        
        # Call configure with some parameters
        component.configure(bg="white", fg="black")
        
        # Verify configure was called on the widget with the correct parameters
        component._widget.configure.assert_called_once_with(bg="white", fg="black")
    
    def test_bind(self):
        """Test the bind method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's bind method
        component._widget.bind = MagicMock()
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Call bind with an event and callback
        component.bind("<Button-1>", mock_callback)
        
        # Verify bind was called on the widget with the correct parameters
        component._widget.bind.assert_called_once_with("<Button-1>", mock_callback)
    
    def test_unbind(self):
        """Test the unbind method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's unbind method
        component._widget.unbind = MagicMock()
        
        # Call unbind with an event
        component.unbind("<Button-1>")
        
        # Verify unbind was called on the widget with the correct parameters
        component._widget.unbind.assert_called_once_with("<Button-1>")
    
    def test_get_widget(self):
        """Test the get_widget method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Call get_widget
        widget = component.get_widget()
        
        # Verify it returns the correct widget
        self.assertEqual(widget, component._widget)
    
    def test_destroy(self):
        """Test the destroy method."""
        # Create a component
        component = self.ConcreteUIComponent(self.root)
        
        # Create a mock for the widget's destroy method
        component._widget.destroy = MagicMock()
        
        # Call destroy
        component.destroy()
        
        # Verify destroy was called on the widget
        component._widget.destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()