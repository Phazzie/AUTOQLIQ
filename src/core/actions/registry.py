"""Registry for action classes.

This module provides a registry for mapping action type strings to
their corresponding action classes.
"""

import logging
from typing import Dict, Any, Type, List, Optional

from src.core.actions.base import ActionBase
from src.core.actions.interfaces import IActionRegistry

logger = logging.getLogger(__name__)


class ActionRegistry(IActionRegistry):
    """Registry for action classes.
    
    Maps action type strings to their corresponding action classes.
    """
    
    def __init__(self):
        """Initialize a new ActionRegistry."""
        self._registry: Dict[str, Type[ActionBase]] = {}
    
    def register_action(self, action_class: Type[ActionBase]) -> None:
        """Register a new action type using its class.
        
        Args:
            action_class: The action class to register
            
        Raises:
            ValueError: If the action class is invalid or already registered
        """
        if not isinstance(action_class, type) or not issubclass(action_class, ActionBase):
            raise ValueError(
                f"Action class {getattr(action_class, '__name__', '<unknown>')} "
                f"must inherit from ActionBase."
            )

        action_type = getattr(action_class, 'action_type', None)
        if not isinstance(action_type, str) or not action_type:
            raise ValueError(
                f"Action class {action_class.__name__} must define a "
                f"non-empty string 'action_type' class attribute."
            )

        if action_type in self._registry and self._registry[action_type] != action_class:
            logger.warning(
                f"Action type '{action_type}' re-registered. "
                f"Overwriting {self._registry[action_type].__name__} with {action_class.__name__}."
            )
        elif action_type in self._registry:
            return  # Already registered

        self._registry[action_type] = action_class
        logger.info(f"Registered action type '{action_type}' with class {action_class.__name__}")
    
    def get_action_class(self, action_type: str) -> Optional[Type[ActionBase]]:
        """Get the action class for a given action type.
        
        Args:
            action_type: The action type string
            
        Returns:
            The action class, or None if not found
        """
        return self._registry.get(action_type)
    
    def get_registered_types(self) -> List[str]:
        """Get a list of all registered action types.
        
        Returns:
            A sorted list of registered action type strings
        """
        return sorted(list(self._registry.keys()))
