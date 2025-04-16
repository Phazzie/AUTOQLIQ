"""Creator for action instances.

This module provides a creator for creating action instances from dictionary data.
"""

import logging
from typing import Dict, Any, Type, List, Optional

from src.core.interfaces import IAction
from src.core.actions.base import ActionBase
from src.core.actions.interfaces import IActionCreator, IActionRegistry, IActionValidator, INestedActionHandler
from src.core.exceptions import ActionError, ValidationError, SerializationError

logger = logging.getLogger(__name__)


class ActionCreator(IActionCreator):
    """Creator for action instances.
    
    Creates action instances from dictionary data.
    """
    
    def __init__(
        self,
        registry: IActionRegistry,
        validator: IActionValidator,
        nested_handler: INestedActionHandler
    ):
        """Initialize a new ActionCreator.
        
        Args:
            registry: The action registry
            validator: The action validator
            nested_handler: The nested action handler
        """
        self._registry = registry
        self._validator = validator
        self._nested_handler = nested_handler
    
    def create_action(self, action_data: Dict[str, Any]) -> IAction:
        """Create an action instance from dictionary data.
        
        Args:
            action_data: The action data
            
        Returns:
            The created action instance
            
        Raises:
            ActionError: If action creation fails
        """
        try:
            # Validate the action data
            self._validator.validate_action_data(action_data)
            
            # Get the action type and name
            action_type = action_data.get("type")
            action_name = action_data.get("name")
            
            # Get the action class from the registry
            action_class = self._registry.get_action_class(action_type)
            if not action_class:
                logger.error(
                    f"Unknown action type encountered: '{action_type}'. "
                    f"Available: {self._registry.get_registered_types()}"
                )
                raise ActionError(
                    f"Unknown action type: '{action_type}'",
                    action_type=action_type,
                    action_name=action_name
                )
            
            # Extract action parameters (excluding the type)
            action_params = {k: v for k, v in action_data.items() if k != "type"}
            
            # Process nested actions if needed
            action_params = self._nested_handler.process_nested_actions(action_type, action_params)
            
            # Instantiate the action class
            action_instance = action_class(**action_params)
            logger.debug(f"Created action instance: {action_instance!r}")
            
            return action_instance
            
        except (TypeError, ValueError, ValidationError) as e:
            err_msg = f"Invalid parameters or validation failed for action type '{action_data.get('type')}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}")
            raise ActionError(
                err_msg,
                action_name=action_data.get("name"),
                action_type=action_data.get("type")
            ) from e
        except SerializationError as e:
            raise ActionError(
                f"Failed to create nested action within '{action_data.get('type')}': {e}",
                action_name=action_data.get("name"),
                action_type=action_data.get("type"),
                cause=e
            ) from e
        except Exception as e:
            err_msg = f"Failed to create action of type '{action_data.get('type')}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}", exc_info=True)
            raise ActionError(
                err_msg,
                action_name=action_data.get("name"),
                action_type=action_data.get("type")
            ) from e
