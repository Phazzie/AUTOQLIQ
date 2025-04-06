"""UI component interface and base class.

This module provides an interface and base class for UI components.
"""

import abc
import tkinter as tk
from typing import Optional, Any


class IUIComponent(abc.ABC):
    """Interface for UI components.
    
    This interface defines the common methods and properties for UI components.
    """
    
    @property
    @abc.abstractmethod
    def widget(self) -> tk.Widget:
        """Get the main widget for this component.
        
        Returns:
            The main widget
        """
        pass
    
    @abc.abstractmethod
    def update(self) -> None:
        """Update the component state."""
        pass
    
    @abc.abstractmethod
    def clear(self) -> None:
        """Clear the component state."""
        pass


class UIComponent(IUIComponent):
    """Base class for UI components.
    
    This class provides a base implementation for UI components.
    
    Attributes:
        _parent: The parent widget
        _widget: The main widget
    """
    
    def __init__(self, parent: tk.Widget):
        """Initialize a new UIComponent.
        
        Args:
            parent: The parent widget
        """
        self._parent = parent
        self._widget = tk.Frame(parent)
    
    @property
    def parent(self) -> tk.Widget:
        """Get the parent widget.
        
        Returns:
            The parent widget
        """
        return self._parent
    
    @property
    def widget(self) -> tk.Widget:
        """Get the main widget.
        
        Returns:
            The main widget
        """
        return self._widget
    
    def update(self) -> None:
        """Update the component state."""
        pass
    
    def clear(self) -> None:
        """Clear the component state."""
        pass
