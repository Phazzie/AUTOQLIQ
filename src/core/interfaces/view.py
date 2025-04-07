"""View interface for AutoQliq.

This module defines the interface for view implementations in the MVP pattern.
"""

import abc
from typing import TypeVar, Generic, Optional

# Define a type variable for the presenter
P = TypeVar('P')


class IView(Generic[P], abc.ABC):
    """Interface for view implementations in the MVP pattern.
    
    Views are responsible for displaying information to the user and
    capturing user input. They delegate business logic to presenters.
    
    Type Parameters:
        P: The type of presenter this view is associated with.
    """
    
    @abc.abstractmethod
    def set_presenter(self, presenter: P) -> None:
        """Set the presenter for this view.
        
        Args:
            presenter: The presenter instance to associate with this view.
        """
        pass
