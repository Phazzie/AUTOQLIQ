"""Action serialization utilities for AutoQliq.

This module provides functions and classes for serializing and deserializing
action objects to and from dictionary representations.
"""

import logging
from typing import Dict, Any, List

# Assuming IAction is defined in core interfaces
from src.core.interfaces import IAction
# Assuming SerializationError is defined in core exceptions
from src.core.exceptions import SerializationError, ActionError, ValidationError

logger = logging.getLogger(__name__)


class ActionSerializer:
    """
    Handles serialization and deserialization of action objects.

    This class provides methods for converting action objects to dictionaries
    and vice versa, using the action factory to create action instances.
    """

    @staticmethod
    def serialize_action(action: IAction) -> Dict[str, Any]:
        """
        Serialize an action instance to a dictionary.

        Relies on the action's `to_dict()` method.

        Args:
            action (IAction): The action instance to serialize.

        Returns:
            Dict[str, Any]: A dictionary representation of the action.

        Raises:
            SerializationError: If the action object is invalid or serialization fails.
        """
        if not isinstance(action, IAction):
             raise SerializationError(f"Object to serialize is not an IAction instance: {type(action).__name__}")
        try:
            # Ensure the action itself is valid before trying to serialize
            if not action.validate():
                # Ideally, validation should happen before saving, but add a check here too.
                # We might need a more specific exception or log a warning.
                logger.warning(f"Serializing an action that failed validation: {action.name} ({action.action_type})")
                # raise ValidationError(f"Action '{action.name}' failed validation and cannot be serialized.") # Or just warn?

            # Use the action's to_dict method to get a dictionary representation
            action_dict = action.to_dict()
            # Ensure 'type' key exists and matches the action_type attribute
            # The `action_type` class attribute is crucial for deserialization lookups
            expected_type = getattr(action, 'action_type', None)
            if 'type' not in action_dict or action_dict['type'] != expected_type:
                 logger.warning(f"Action {getattr(action, 'name', 'Unnamed')} to_dict() missing or mismatched 'type' key. Using action_type attribute: '{expected_type}'.")
                 if expected_type is None:
                     raise SerializationError(f"Action type attribute is missing for {type(action).__name__}, cannot serialize reliably.")
                 action_dict['type'] = expected_type # Ensure correct type is in dict

            return action_dict
        except (AttributeError, NotImplementedError) as e:
             # Catch if to_dict or action_type is missing, or if validate/to_dict not implemented
             error_msg = f"Action object {type(action).__name__} is missing required methods/attributes for serialization: {e}"
             logger.error(error_msg)
             raise SerializationError(error_msg) from e
        except Exception as e:
            # Catch other unexpected errors during serialization
            error_msg = f"Failed to serialize action '{getattr(action, 'name', 'Unnamed')}': {e}"
            logger.error(error_msg, exc_info=True)
            raise SerializationError(error_msg, cause=e) from e

    @staticmethod
    def deserialize_action(action_data: Dict[str, Any]) -> IAction:
        """
        Deserialize an action from a dictionary using the ActionFactory.

        Args:
            action_data (Dict[str, Any]): The dictionary representation of the action.
                                          Must contain a 'type' key.

        Returns:
            IAction: An instantiated action object.

        Raises:
            SerializationError: If the action data is invalid or deserialization fails (e.g., unknown type, missing parameters).
        """
        if not isinstance(action_data, dict):
            raise SerializationError(f"Action data must be a dictionary, got {type(action_data).__name__}.")
        if 'type' not in action_data:
            raise SerializationError("Action data dictionary is missing the required 'type' key.")

        action_type = action_data['type']
        try:
            # Import ActionFactory locally to avoid potential circular imports at module level
            # Ensure ActionFactory is appropriately located after potential refactoring
            try:
                from src.core.actions.factory import ActionFactory
            except ImportError:
                 logger.warning("Could not import refactored ActionFactory, falling back to src.core.actions")
                 from src.core.actions import ActionFactory # Fallback to original location


            action_instance = ActionFactory.create_action(action_data) # Raises ActionError
            logger.debug(f"Successfully deserialized action of type '{action_type}'.")
            return action_instance
        except (ActionError, ValueError, TypeError) as e:
            # Catch errors from ActionFactory (unknown type, bad params)
            error_msg = f"Failed to deserialize action type '{action_type}': {e}"
            logger.error(f"{error_msg} Data: {action_data}")
            # Wrap factory errors in SerializationError for consistent error type from this layer
            raise SerializationError(error_msg, cause=e) from e
        except Exception as e:
            # Catch other unexpected errors during deserialization
            error_msg = f"Unexpected error deserializing action type '{action_type}': {e}"
            logger.error(f"{error_msg} Data: {action_data}", exc_info=True)
            raise SerializationError(error_msg, cause=e) from e


# --- Module-level convenience functions ---

def serialize_actions(actions: List[IAction]) -> List[Dict[str, Any]]:
    """
    Serialize a list of action instances to a list of dictionaries.

    Args:
        actions (List[IAction]): The list of action instances to serialize.

    Returns:
        List[Dict[str, Any]]: A list of dictionary representations of the actions.

    Raises:
        SerializationError: If any action in the list cannot be serialized.
        TypeError: If the input is not a list.
    """
    if not isinstance(actions, list):
        raise TypeError("Input 'actions' must be a list.")
    serialized_list = []
    for i, action in enumerate(actions):
        try:
            serialized_list.append(ActionSerializer.serialize_action(action))
        except SerializationError as e:
            # Add context about which action failed
            raise SerializationError(f"Failed to serialize action at index {i}: {e}", cause=e.cause) from e
    return serialized_list


def deserialize_actions(action_data_list: List[Dict[str, Any]]) -> List[IAction]:
    """
    Deserialize a list of dictionaries into a list of action instances.

    Args:
        action_data_list (List[Dict[str, Any]]): The list of dictionary representations
                                                  of the actions.

    Returns:
        List[IAction]: A list of instantiated action objects.

    Raises:
        SerializationError: If any action dictionary is invalid or deserialization fails.
        TypeError: If the input is not a list of dictionaries.
    """
    if not isinstance(action_data_list, list):
        raise TypeError("Input 'action_data_list' must be a list.")
    deserialized_list = []
    for i, action_data in enumerate(action_data_list):
        if not isinstance(action_data, dict):
             raise TypeError(f"Item at index {i} in 'action_data_list' must be a dictionary, got {type(action_data).__name__}.")
        try:
            deserialized_list.append(ActionSerializer.deserialize_action(action_data))
        except SerializationError as e:
             # Add context about which action failed
            action_type = action_data.get('type', 'Unknown')
            raise SerializationError(f"Failed to deserialize action of type '{action_type}' at index {i}: {e}", cause=e.cause) from e
    return deserialized_list