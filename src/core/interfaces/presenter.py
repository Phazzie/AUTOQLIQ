"""Presenter interface for AutoQliq.

This module defines the interface for presenter implementations in the MVP pattern.
"""

import abc
from typing import TypeVar, Generic, Optional

# Define a type variable for the view
V = TypeVar('V')


class IPresenter(Generic[V], abc.ABC):
    """Interface for presenter implementations in the MVP pattern.
    
    Presenters handle the logic between models and views. They respond to
    user actions from the view, manipulate model data, and update the view.
    
    Type Parameters:
        V: The type of view this presenter is associated with.
    """
    
    @abc.abstractmethod
    def set_view(self, view: V) -> None:
        """Set the view for this presenter.
        
        Args:
            view: The view instance to associate with this presenter.
        """
        pass
