"""Factory module for creating action instances.

This module provides a facade for creating action instances from dictionary data.
It uses separate components for registration, validation, and creation to adhere
to the Single Responsibility Principle.
"""

import logging
from typing import Dict, Any, Type, List, Optional

# Core interfaces
from src.core.interfaces import IAction

# Action components
from src.core.actions.base import ActionBase
from src.core.actions.registry import ActionRegistry
from src.core.actions.validator import ActionValidator
from src.core.actions.nested_handler import NestedActionHandler
from src.core.actions.creator import ActionCreator

# Import specific action classes for registration
from src.core.actions.navigation import NavigateAction
from src.core.actions.interaction import ClickAction, TypeAction
from src.core.actions.utility import WaitAction, ScreenshotAction
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction

logger = logging.getLogger(__name__)


class ActionFactory:
    """
    Factory responsible for creating action instances from data.
    
    This class serves as a facade for the underlying components that handle
    registration, validation, and creation of actions. It maintains backward
    compatibility with existing code while adhering to SOLID principles.
    """
    # Initialize the components
    _registry = ActionRegistry()
    _validator = ActionValidator()
    # We need to use a function reference for the nested handler to avoid circular imports
    _nested_handler = None
    _creator = None
    
    @classmethod
    def _initialize_components(cls):
        """Initialize the components if they haven't been initialized yet."""
        if cls._nested_handler is None:
            # Create the nested handler with a reference to the create_action method
            cls._nested_handler = NestedActionHandler(cls.create_action)
        
        if cls._creator is None:
            # Create the creator with the registry, validator, and nested handler
            cls._creator = ActionCreator(cls._registry, cls._validator, cls._nested_handler)

    @classmethod
    def register_action(cls, action_class: Type[ActionBase]) -> None:
        """Register a new action type using its class.
        
        Args:
            action_class: The action class to register
            
        Raises:
            ValueError: If the action class is invalid or already registered
        """
        cls._registry.register_action(action_class)

    @classmethod
    def get_registered_action_types(cls) -> List[str]:
        """Returns a sorted list of registered action type names.
        
        Returns:
            A sorted list of registered action type strings
        """
        return cls._registry.get_registered_types()

    @classmethod
    def create_action(cls, action_data: Dict[str, Any]) -> IAction:
        """
        Create an action instance from a dictionary representation.

        Handles deserialization of nested actions.
        Does NOT handle template expansion (runner does this).
        
        Args:
            action_data: The action data dictionary
            
        Returns:
            The created action instance
            
        Raises:
            TypeError: If the action data is not a dictionary
            ActionError: If action creation fails
        """
        # Initialize the components if needed
        cls._initialize_components()
        
        # Use the creator to create the action
        return cls._creator.create_action(action_data)


# --- Auto-register known actions ---
ActionFactory.register_action(NavigateAction)
ActionFactory.register_action(ClickAction)
ActionFactory.register_action(TypeAction)
ActionFactory.register_action(WaitAction)
ActionFactory.register_action(ScreenshotAction)
ActionFactory.register_action(ConditionalAction)
ActionFactory.register_action(LoopAction)
ActionFactory.register_action(ErrorHandlingAction)
ActionFactory.register_action(TemplateAction)
