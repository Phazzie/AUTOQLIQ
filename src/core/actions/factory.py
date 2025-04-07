"""Factory module for creating action instances."""

import logging
from typing import Dict, Any, Type, List # Added List

# Assuming IAction and ActionBase are defined
from src.core.interfaces import IAction
# Import specific action classes dynamically if possible, or explicitly
from src.core.actions.base import ActionBase
from src.core.actions.navigation import NavigateAction
from src.core.actions.interaction import ClickAction, TypeAction
from src.core.actions.utility import WaitAction, ScreenshotAction
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction # New

# Assuming ActionError is defined
from src.core.exceptions import ActionError, ValidationError, SerializationError

logger = logging.getLogger(__name__)


class ActionFactory:
    """
    Factory responsible for creating action instances from data.

    Uses a registry to map action type strings to action classes.
    Handles recursive deserialization for nested actions.
    """
    # Registry mapping type strings (from JSON/dict) to the corresponding class
    _registry: Dict[str, Type[ActionBase]] = {} # Start empty, register below

    @classmethod
    def register_action(cls, action_class: Type[ActionBase]) -> None:
        """Register a new action type using its class."""
        if not isinstance(action_class, type) or not issubclass(action_class, ActionBase):
            raise ValueError(f"Action class {getattr(action_class, '__name__', '<unknown>')} must inherit from ActionBase.")

        action_type = getattr(action_class, 'action_type', None)
        if not isinstance(action_type, str) or not action_type:
             raise ValueError(f"Action class {action_class.__name__} must define a non-empty string 'action_type' class attribute.")

        if action_type in cls._registry and cls._registry[action_type] != action_class:
            logger.warning(f"Action type '{action_type}' re-registered. Overwriting {cls._registry[action_type].__name__} with {action_class.__name__}.")
        elif action_type in cls._registry: return # Already registered

        cls._registry[action_type] = action_class
        logger.info(f"Registered action type '{action_type}' with class {action_class.__name__}")

    @classmethod
    def get_registered_action_types(cls) -> List[str]:
        """Returns a sorted list of registered action type names."""
        return sorted(list(cls._registry.keys()))

    @classmethod
    def create_action(cls, action_data: Dict[str, Any]) -> IAction:
        """
        Create an action instance from a dictionary representation.

        Handles deserialization of nested actions.
        Does NOT handle template expansion (runner does this).
        """
        if not isinstance(action_data, dict):
            raise TypeError(f"Action data must be a dictionary, got {type(action_data).__name__}.")

        action_type = action_data.get("type")
        action_name_from_data = action_data.get("name")

        if not action_type:
            raise ActionError("Action data must include a 'type' key.", action_type=None, action_name=action_name_from_data)
        if not isinstance(action_type, str):
             raise ActionError("Action 'type' key must be a string.", action_type=str(action_type), action_name=action_name_from_data)

        action_class = cls._registry.get(action_type)
        if not action_class:
            logger.error(f"Unknown action type encountered: '{action_type}'. Available: {list(cls._registry.keys())}")
            raise ActionError(f"Unknown action type: '{action_type}'", action_type=action_type, action_name=action_name_from_data)

        try:
            action_params = {k: v for k, v in action_data.items() if k != "type"}

            # --- Handle Nested Actions Deserialization ---
            nested_action_fields = {
                 ConditionalAction.action_type: ["true_branch", "false_branch"],
                 LoopAction.action_type: ["loop_actions"],
                 ErrorHandlingAction.action_type: ["try_actions", "catch_actions"],
            }
            # Note: TemplateAction does not have nested actions defined in its own data dict.

            if action_type in nested_action_fields:
                for field_name in nested_action_fields[action_type]:
                    nested_data_list = action_params.get(field_name)
                    if isinstance(nested_data_list, list):
                        try:
                            action_params[field_name] = [cls.create_action(nested_data) for nested_data in nested_data_list]
                            logger.debug(f"Deserialized {len(action_params[field_name])} nested actions for '{field_name}' in '{action_type}'.")
                        except (TypeError, ActionError, SerializationError, ValidationError) as nested_e:
                             err_msg = f"Invalid nested action data in field '{field_name}' for action type '{action_type}': {nested_e}"
                             logger.error(f"{err_msg} Parent Data: {action_data}")
                             raise SerializationError(err_msg, cause=nested_e) from nested_e
                    elif nested_data_list is not None:
                         raise SerializationError(f"Field '{field_name}' for action type '{action_type}' must be a list, got {type(nested_data_list).__name__}.")

            # Instantiate the action class
            action_instance = action_class(**action_params)
            logger.debug(f"Created action instance: {action_instance!r}")
            return action_instance
        except (TypeError, ValueError, ValidationError) as e:
            err_msg = f"Invalid parameters or validation failed for action type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}")
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e
        except SerializationError as e:
             raise ActionError(f"Failed to create nested action within '{action_type}': {e}", action_name=action_name_from_data, action_type=action_type, cause=e) from e
        except Exception as e:
            err_msg = f"Failed to create action of type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}", exc_info=True)
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e

# --- Auto-register known actions ---
ActionFactory.register_action(NavigateAction)
ActionFactory.register_action(ClickAction)
ActionFactory.register_action(TypeAction)
ActionFactory.register_action(WaitAction)
ActionFactory.register_action(ScreenshotAction)
ActionFactory.register_action(ConditionalAction)
ActionFactory.register_action(LoopAction)
ActionFactory.register_action(ErrorHandlingAction)
ActionFactory.register_action(TemplateAction) # New