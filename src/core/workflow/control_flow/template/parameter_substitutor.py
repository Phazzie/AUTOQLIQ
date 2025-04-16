"""Parameter substitutor for template actions.

This module provides functionality for substituting parameters in template actions.
"""

import logging
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.exceptions import ActionError
from src.core.actions.factory import ActionFactory

logger = logging.getLogger(__name__)


class ParameterSubstitutor:
    """
    Substitutes parameters in template actions.
    """
    
    def __init__(self):
        """Initialize the parameter substitutor."""
        self.action_factory = ActionFactory()
    
    def apply_parameters(self, actions: List[IAction], parameters: Dict[str, Any]) -> List[IAction]:
        """
        Apply parameter substitutions to template actions.
        
        Args:
            actions: The actions to apply parameters to
            parameters: The parameters to apply
            
        Returns:
            List[IAction]: The actions with parameters applied
            
        Raises:
            ActionError: If parameter substitution fails
        """
        try:
            action_dicts = self._serialize_actions(actions)
            self._substitute_parameters_in_dicts(action_dicts, parameters)
            return self._deserialize_actions(action_dicts)
        except Exception as e:
            raise ActionError(f"Failed to apply template parameters: {e}", cause=e) from e

    def _serialize_actions(self, actions: List[IAction]) -> List[Dict[str, Any]]:
        """Serialize actions to dictionaries."""
        return [action.to_dict() for action in actions]

    def _substitute_parameters_in_dicts(self, action_dicts: List[Dict[str, Any]], parameters: Dict[str, Any]) -> None:
        """Apply parameter substitutions to serialized actions."""
        for action_dict in action_dicts:
            self._substitute_parameters_in_dict(action_dict, parameters)

    def _deserialize_actions(self, action_dicts: List[Dict[str, Any]]) -> List[IAction]:
        """Deserialize dictionaries back to actions."""
        return [self.action_factory.create_action(action_dict) for action_dict in action_dicts]
    
    def _substitute_parameters_in_dict(self, data: Dict[str, Any], parameters: Dict[str, Any]) -> None:
        """
        Recursively substitute parameters in a dictionary.
        
        Args:
            data: The dictionary to apply substitutions to
            parameters: The parameters to apply
        """
        for key, value in data.items():
            if isinstance(value, str):
                # Replace {{param}} with parameters["param"]
                for param_name, param_value in parameters.items():
                    placeholder = f"{{{{{param_name}}}}}"
                    if placeholder in value:
                        data[key] = value.replace(placeholder, str(param_value))
            elif isinstance(value, dict):
                self._substitute_parameters_in_dict(value, parameters)
            elif isinstance(value, list):
                self._substitute_parameters_in_list(value, parameters)
    
    def _substitute_parameters_in_list(self, data: List[Any], parameters: Dict[str, Any]) -> None:
        """
        Recursively substitute parameters in a list.
        
        Args:
            data: The list to apply substitutions to
            parameters: The parameters to apply
        """
        for i, item in enumerate(data):
            if isinstance(item, dict):
                self._substitute_parameters_in_dict(item, parameters)
            elif isinstance(item, str):
                for param_name, param_value in parameters.items():
                    placeholder = f"{{{{{param_name}}}}}"
                    if placeholder in item:
                        data[i] = item.replace(placeholder, str(param_value))
