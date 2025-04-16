"""Handler for nested actions in control flow actions.

This module provides a handler for processing nested actions in control flow actions.
"""

import logging
from typing import Dict, Any, List, Callable

from src.core.actions.interfaces import INestedActionHandler
from src.core.exceptions import SerializationError, ActionError, ValidationError

logger = logging.getLogger(__name__)


class NestedActionHandler(INestedActionHandler):
    """Handler for nested actions in control flow actions.

    Processes nested actions in control flow actions.
    """

    def __init__(self, action_creator_func: Callable[[Dict[str, Any]], Any]):
        """Initialize a new NestedActionHandler.

        Args:
            action_creator_func: A function that creates actions from dictionaries
        """
        self._action_creator_func = action_creator_func

        # Define nested action fields for each control flow action type
        self._nested_action_fields = {
            "Conditional": ["true_branch", "false_branch"],
            "Loop": ["loop_actions"],
            "ErrorHandling": ["try_actions", "catch_actions"],
            # TemplateAction does not have nested actions defined in its own data dict
        }

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
        # If this is not a control flow action, return the params unchanged
        if action_type not in self._nested_action_fields:
            return action_params

        # Create a copy of the parameters to avoid modifying the original
        processed_params = action_params.copy()

        # Process each nested action field
        for field_name in self._nested_action_fields[action_type]:
            nested_data_list = processed_params.get(field_name)

            if isinstance(nested_data_list, list):
                try:
                    # Create a list to hold the processed actions
                    processed_actions = []

                    # Process each nested action data individually
                    for nested_data in nested_data_list:
                        try:
                            processed_action = self._action_creator_func(nested_data)
                            processed_actions.append(processed_action)
                        except (TypeError, ActionError, SerializationError, ValidationError, ValueError) as nested_e:
                            # Include ValueError in the caught exceptions
                            err_msg = (
                                f"Invalid nested action data in field '{field_name}' "
                                f"for action type '{action_type}': {nested_e}"
                            )
                            logger.error(f"{err_msg} Parent Data: {action_params}")
                            raise SerializationError(err_msg, cause=nested_e) from nested_e

                    # Assign the processed actions to the field
                    processed_params[field_name] = processed_actions

                    logger.debug(
                        f"Deserialized {len(processed_params[field_name])} nested actions "
                        f"for '{field_name}' in '{action_type}'."
                    )
                except (TypeError, ActionError, SerializationError, ValidationError) as nested_e:
                    err_msg = (
                        f"Invalid nested action data in field '{field_name}' "
                        f"for action type '{action_type}': {nested_e}"
                    )
                    logger.error(f"{err_msg} Parent Data: {action_params}")
                    raise SerializationError(err_msg, cause=nested_e) from nested_e
            elif nested_data_list is not None:
                # If the field exists but is not a list, that's an error
                err_msg = (
                    f"Field '{field_name}' for action type '{action_type}' "
                    f"must be a list, got {type(nested_data_list).__name__}."
                )
                logger.error(f"{err_msg} Parent Data: {action_params}")
                raise SerializationError(err_msg)

        return processed_params
