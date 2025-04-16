"""Interfaces for action-related components.

This module defines interfaces for action-related components such as
registries, validators, creators, and nested action handlers.
"""

import abc
from typing import Dict, Any, Type, List, Optional

from src.core.interfaces import IAction
from src.core.actions.base import ActionBase


class IActionRegistry(abc.ABC):
    """Interface for action registry implementations.
    
    Action registries manage the mapping between action type strings and
    their corresponding action classes.
    """
    
    @abc.abstractmethod
    def register_action(self, action_class: Type[ActionBase]) -> None:
        """Register a new action type using its class.
        
        Args:
            action_class: The action class to register
            
        Raises:
            ValueError: If the action class is invalid or already registered
        """
        pass
    
    @abc.abstractmethod
    def get_action_class(self, action_type: str) -> Optional[Type[ActionBase]]:
        """Get the action class for a given action type.
        
        Args:
            action_type: The action type string
            
        Returns:
            The action class, or None if not found
        """
        pass
    
    @abc.abstractmethod
    def get_registered_types(self) -> List[str]:
        """Get a list of all registered action types.
        
        Returns:
            A sorted list of registered action type strings
        """
        pass


class IActionValidator(abc.ABC):
    """Interface for action validator implementations.
    
    Action validators check that action data is valid before creating
    action instances.
    """
    
    @abc.abstractmethod
    def validate_action_data(self, action_data: Dict[str, Any]) -> None:
        """Validate action data before creating an action.
        
        Args:
            action_data: The action data to validate
            
        Raises:
            TypeError: If the action data is not a dictionary
            ActionError: If the action data is invalid
        """
        pass


class INestedActionHandler(abc.ABC):
    """Interface for nested action handler implementations.
    
    Nested action handlers process nested actions in control flow actions.
    """
    
    @abc.abstractmethod
    def process_nested_actions(
        self, 
        action_type: str, 
        action_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process nested actions in control flow actions.
        
        Args:
            action_type: The action type string
            action_params: The action parameters
            
        Returns:
            The updated action parameters with processed nested actions
            
        Raises:
            SerializationError: If nested action processing fails
        """
        pass


class IActionCreator(abc.ABC):
    """Interface for action creator implementations.
    
    Action creators create action instances from dictionary data.
    """
    
    @abc.abstractmethod
    def create_action(self, action_data: Dict[str, Any]) -> IAction:
        """Create an action instance from dictionary data.
        
        Args:
            action_data: The action data
            
        Returns:
            The created action instance
            
        Raises:
            ActionError: If action creation fails
        """
        pass
