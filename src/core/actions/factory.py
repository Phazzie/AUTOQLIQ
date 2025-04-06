"""Factory module for creating action instances."""

import logging
from typing import Dict, Any, Type

# Assuming IAction and ActionBase are defined
from src.core.interfaces import IAction
# Import specific action classes dynamically if possible, or explicitly
# Explicit imports are generally safer and clearer
# Adjust paths based on the final location of action classes
try:
    from src.core.actions.base import ActionBase
    from src.core.actions.navigation import NavigateAction
    from src.core.actions.interaction import ClickAction, TypeAction
    from src.core.actions.utility import WaitAction, ScreenshotAction
except ImportError:
     # Fallback if refactoring isn't complete - use original structure
     # This might indicate the refactoring step for actions wasn't applied yet.
     logging.warning("Could not import refactored actions, falling back to src.core.actions")
     # Need to handle potential circular import if base calls factory
     # Better to ensure imports are correct based on expected structure
     raise ImportError("Failed to import refactored action classes. Check structure.")


# Assuming ActionError is defined
from src.core.exceptions import ActionError

logger = logging.getLogger(__name__)


class ActionFactory:
    """
    Factory responsible for creating action instances from data.

    Uses a registry to map action type strings to action classes.
    """
    # Registry mapping type strings (from JSON/dict) to the corresponding class
    _registry: Dict[str, Type[ActionBase]] = {
        # Map type strings (case-sensitive) to the imported classes
        # These should match the 'action_type' class attributes of the actions
        NavigateAction.action_type: NavigateAction,
        ClickAction.action_type: ClickAction,
        TypeAction.action_type: TypeAction,
        WaitAction.action_type: WaitAction,
        ScreenshotAction.action_type: ScreenshotAction,
        # Add other action types here as they are created and imported
    }

    @classmethod
    def register_action(cls, action_class: Type[ActionBase]) -> None:
        """
        Register a new action type using its class.

        The action type identifier is taken from the class's `action_type` attribute.

        Args:
            action_class (Type[ActionBase]): The class implementing the action. Must inherit from ActionBase
                                             and define a unique `action_type` class attribute.

        Raises:
            ValueError: If the action_class is invalid, missing `action_type`, or `action_type` is empty.
        """
        if not isinstance(action_class, type) or not issubclass(action_class, ActionBase):
            raise ValueError(f"Action class {getattr(action_class, '__name__', '<unknown>')} must inherit from ActionBase.")

        action_type = getattr(action_class, 'action_type', None)
        if not isinstance(action_type, str) or not action_type:
             raise ValueError(f"Action class {action_class.__name__} must define a non-empty string 'action_type' class attribute.")

        if action_type in cls._registry and cls._registry[action_type] != action_class:
            # Decide on policy: overwrite or raise error? Overwriting is simpler for dynamic loading.
            logger.warning(f"Action type '{action_type}' is already registered with class {cls._registry[action_type].__name__}. Overwriting with {action_class.__name__}.")
        elif action_type in cls._registry:
            logger.debug(f"Action type '{action_type}' for class {action_class.__name__} already registered.")
            return # No need to re-register the same class

        cls._registry[action_type] = action_class
        logger.info(f"Registered action type '{action_type}' with class {action_class.__name__}")

    @classmethod
    def create_action(cls, action_data: Dict[str, Any]) -> IAction:
        """
        Create an action instance from a dictionary representation.

        Args:
            action_data (Dict[str, Any]): A dictionary containing action data.
                                          Must include a 'type' key corresponding to a registered action type.
                                          Other keys should match the parameters of the action class's constructor.

        Returns:
            IAction: An instance of the appropriate action class, initialized with the provided data.

        Raises:
            ActionError: If the action type is missing, unknown, or if instantiation fails
                         due to invalid/missing parameters in action_data.
            TypeError: If action_data is not a dictionary.
        """
        if not isinstance(action_data, dict):
            raise TypeError(f"Action data must be a dictionary, got {type(action_data).__name__}.")

        action_type = action_data.get("type")
        action_name_from_data = action_data.get("name") # For error context

        if not action_type:
            raise ActionError("Action data must include a 'type' key.", action_type=None, action_name=action_name_from_data)
        if not isinstance(action_type, str):
             raise ActionError("Action 'type' key must be a string.", action_type=str(action_type), action_name=action_name_from_data)

        action_class = cls._registry.get(action_type)
        if not action_class:
            logger.error(f"Unknown action type encountered: '{action_type}'. Available types: {list(cls._registry.keys())}")
            raise ActionError(f"Unknown action type: '{action_type}'", action_type=action_type, action_name=action_name_from_data)

        try:
            # Prepare arguments for the action class constructor.
            # Exclude the 'type' key itself from the parameters passed to __init__.
            # Other keys in action_data should match the __init__ parameters of the action_class.
            action_params = {k: v for k, v in action_data.items() if k != "type"}

            # Instantiate the action class with the parameters
            action_instance = action_class(**action_params)
            logger.debug(f"Created action instance: {action_instance!r}") # Use repr for more detail
            return action_instance
        except TypeError as e:
            # Catches errors like missing/unexpected keyword arguments in __init__
            # Python's TypeError message for kwargs is usually informative enough
            err_msg = f"Invalid or missing parameters for action type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}")
            # Raise ActionError providing context
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e
        except Exception as e:
            # Catch other potential errors during instantiation (e.g., ValueError in __init__)
            err_msg = f"Failed to create action of type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}", exc_info=True)
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e

# Optional: Auto-register known actions upon import
# ActionFactory.register_action(NavigateAction)
# ActionFactory.register_action(ClickAction)
# ... etc. (This is already handled by the initial _registry definition)