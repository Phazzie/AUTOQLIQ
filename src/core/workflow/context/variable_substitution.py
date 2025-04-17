"""Variable substitution for workflow execution.

This module provides variable substitution functionality for workflow execution.
"""

import logging
import re
from typing import Dict, Any, List, Union

from src.core.workflow.context.interfaces import IVariableResolver

logger = logging.getLogger(__name__)


class VariableSubstitutor(IVariableResolver):
    """
    Handles variable substitution in strings and data structures.
    """

    def __init__(self):
        """Initialize the variable substitutor."""
        pass

    def substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute variables in a string.

        Args:
            text: The string to substitute variables in
            context: The execution context

        Returns:
            str: The string with variables substituted
        """
        if not text or not isinstance(text, str):
            return text

        # Find all {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, text)

        result = text
        for match in matches:
            variable_name = match.strip()
            if variable_name in context:
                value = context[variable_name]
                placeholder = f"{{{{{variable_name}}}}}"
                result = result.replace(placeholder, str(value))

        return result

    def substitute_variables_in_dict(self, data: Dict[str, Any],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute variables in a dictionary.

        Args:
            data: The dictionary to substitute variables in
            context: The execution context

        Returns:
            Dict[str, Any]: The dictionary with variables substituted
        """
        result = {}

        for key, value in data.items():
            result[key] = self._substitute_value(value, context)

        return result

    def substitute_variables_in_list(self, data: List[Any],
                                    context: Dict[str, Any]) -> List[Any]:
        """
        Substitute variables in a list.

        Args:
            data: The list to substitute variables in
            context: The execution context

        Returns:
            List[Any]: The list with variables substituted
        """
        result = []

        for item in data:
            result.append(self._substitute_value(item, context))

        return result

    def _substitute_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Substitute variables in a value based on its type.

        Args:
            value: The value to substitute variables in
            context: The execution context

        Returns:
            Any: The value with variables substituted
        """
        if isinstance(value, str):
            return self.substitute_variables(value, context)
        elif isinstance(value, dict):
            return self.substitute_variables_in_dict(value, context)
        elif isinstance(value, list):
            return self.substitute_variables_in_list(value, context)
        else:
            return value
