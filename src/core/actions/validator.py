"""Validator for action data.

This module provides a validator for checking that action data is valid
before creating action instances.
"""

import logging
from typing import Dict, Any, Optional

from src.core.actions.interfaces import IActionValidator
from src.core.exceptions import ActionError

logger = logging.getLogger(__name__)


class ActionValidator(IActionValidator):
    """Validator for action data.
    
    Checks that action data is valid before creating action instances.
    """
    
    def validate_action_data(self, action_data: Dict[str, Any]) -> None:
        """Validate action data before creating an action.
        
        Args:
            action_data: The action data to validate
            
        Raises:
            TypeError: If the action data is not a dictionary
            ActionError: If the action data is invalid
        """
        if not isinstance(action_data, dict):
            raise TypeError(
                f"Action data must be a dictionary, got {type(action_data).__name__}."
            )

        action_type = action_data.get("type")
        action_name = action_data.get("name")

        if not action_type:
            raise ActionError(
                "Action data must include a 'type' key.",
                action_type=None,
                action_name=action_name
            )
            
        if not isinstance(action_type, str):
            raise ActionError(
                "Action 'type' key must be a string.",
                action_type=str(action_type),
                action_name=action_name
            )
