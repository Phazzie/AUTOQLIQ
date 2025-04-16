"""Context validator for workflow execution.

This module provides validation functionality for workflow execution context.
"""

import logging
from typing import Dict, Any, List, Optional, Set

from src.core.workflow.context.interfaces import IContextValidator

logger = logging.getLogger(__name__)


class ContextValidator(IContextValidator):
    """
    Validates workflow execution context.

    Ensures that required variables are present and have the correct types.
    """

    def __init__(self):
        """Initialize the context validator."""
        pass

    def validate_context(self, context: Dict[str, Any],
                         required_keys: Optional[List[str]] = None) -> bool:
        """
        Validate that a context contains all required keys.

        Args:
            context: The execution context
            required_keys: Optional list of keys that must be present

        Returns:
            bool: True if the context is valid, False otherwise
        """
        if required_keys is None:
            return True
        return self.validate_required_keys(context, required_keys)

    def validate_required_keys(self, context: Dict[str, Any],
                               required_keys: List[str]) -> bool:
        """
        Validate that all required keys are present in the context.

        Args:
            context: The execution context
            required_keys: List of keys that must be present

        Returns:
            bool: True if all required keys are present, False otherwise
        """
        missing_keys = self.get_missing_keys(context, required_keys)
        if missing_keys:
            logger.warning(f"Missing required context keys: {missing_keys}")
            return False
        return True

    def validate_key_types(self, context: Dict[str, Any],
                           type_requirements: Dict[str, type]) -> bool:
        """
        Validate that keys have the correct types.

        Args:
            context: The execution context
            type_requirements: Dictionary mapping keys to their required types

        Returns:
            bool: True if all keys have the correct types, False otherwise
        """
        invalid_types = self.get_invalid_key_types(context, type_requirements)
        if invalid_types:
            logger.warning(f"Invalid context key types: {invalid_types}")
            return False
        return True

    def get_missing_keys(self, context: Dict[str, Any],
                         required_keys: List[str]) -> List[str]:
        """
        Get a list of required keys that are missing from the context.

        Args:
            context: The execution context
            required_keys: List of keys that must be present

        Returns:
            List[str]: List of missing keys
        """
        return [key for key in required_keys if key not in context]

    def get_available_keys(self, context: Dict[str, Any]) -> Set[str]:
        """
        Get a set of all keys available in the context.

        Args:
            context: The execution context

        Returns:
            Set[str]: Set of available keys
        """
        return set(context.keys())

    def get_invalid_key_types(self, context: Dict[str, Any],
                              type_requirements: Dict[str, type]) -> List[str]:
        """
        Get a list of keys that have invalid types.

        Args:
            context: The execution context
            type_requirements: Dictionary mapping keys to their required types

        Returns:
            List[str]: List of keys with invalid types
        """
        invalid_types = []
        for key, required_type in type_requirements.items():
            if key in context and not isinstance(context[key], required_type):
                invalid_types.append(
                    f"{key} (expected {required_type.__name__}, got {type(context[key]).__name__})"
                )
        return invalid_types
