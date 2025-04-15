"""Context manager for workflow execution.

This module provides a facade for the context management components.
"""

import logging
from typing import Dict, Any

from src.core.workflow.context.initializer import initialize_context
from src.core.workflow.context.variable_substitution import VariableSubstitutor
from src.core.workflow.context.validator import ContextValidator
from src.core.workflow.context.serializer import ContextSerializer

logger = logging.getLogger(__name__)


class WorkflowContextManager:
    """
    Manages workflow execution context.

    Handles variable storage, sensitive data, and context lifecycle.
    """

    def __init__(self):
        """Initialize the context manager."""
        self.context = initialize_context()
        self.substitutor = VariableSubstitutor()
        self.validator = ContextValidator()
        self.serializer = ContextSerializer()

    def get_context(self) -> Dict[str, Any]:
        """
        Get the current execution context.

        Returns:
            Dict[str, Any]: The current context
        """
        return self.context

    def update_context(self, updates: Dict[str, Any]) -> None:
        """
        Update the execution context with new values.

        Args:
            updates: Dictionary of updates to apply to the context
        """
        self.context.update(updates)

    def substitute_variables(self, text: str) -> str:
        """
        Substitute variables in a string using the current context.

        Args:
            text: The string to substitute variables in

        Returns:
            str: The string with variables substituted
        """
        return self.substitutor.substitute_variables(text, self.context)

    def validate_context(self, required_keys: Dict[str, type]) -> bool:
        """
        Validate the execution context.

        Args:
            required_keys: Dictionary of required keys and their types

        Returns:
            bool: True if the context is valid, False otherwise
        """
        return self.validator.validate_required_keys(self.context, list(required_keys.keys())) and \
               self.validator.validate_key_types(self.context, required_keys)

    def serialize_context(self) -> str:
        """
        Serialize the execution context to a JSON string.

        Returns:
            str: The serialized context
        """
        return self.serializer.serialize_context(self.context)

    def deserialize_context(self, serialized_context: str) -> None:
        """
        Deserialize a JSON string to update the execution context.

        Args:
            serialized_context: The serialized context
        """
        self.context = self.serializer.deserialize_context(serialized_context)


# For backward compatibility, re-export the WorkflowContextManager as ContextManager
ContextManager = WorkflowContextManager
