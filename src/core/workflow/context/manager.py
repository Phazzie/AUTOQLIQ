"""Context manager for workflow execution.

This module provides the main context manager for workflow execution.
"""

import logging
from typing import Dict, Any, List, Optional, Set

from src.core.workflow.context.base import ContextManager
from src.core.workflow.context.variable_substitution import VariableSubstitutor
from src.core.workflow.context.validator import ContextValidator
from src.core.workflow.context.serializer import ContextSerializer
from src.core.workflow.context.initializer import initialize_context
from src.core.workflow.context.interfaces import IWorkflowContextManager

logger = logging.getLogger(__name__)


class WorkflowContextManager(IWorkflowContextManager):
    """
    Main context manager for workflow execution.

    Combines all context management functionality.
    """

    def __init__(self):
        """Initialize the workflow context manager."""
        self.base_manager = ContextManager()
        self.variable_substitutor = VariableSubstitutor()
        self.validator = ContextValidator()
        self.serializer = ContextSerializer()

    def create_context(self) -> Dict[str, Any]:
        """
        Create a new execution context.

        Returns:
            Dict[str, Any]: A new execution context
        """
        return initialize_context()

    def update_context(self, context: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an execution context with new values.

        Args:
            context: The context to update
            updates: The values to add to the context

        Returns:
            Dict[str, Any]: The updated context
        """
        return self.base_manager.update_context(context, updates)

    def get_value(self, context: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Get a value from the context.

        Args:
            context: The execution context
            key: The key to get
            default: The default value to return if the key is not found

        Returns:
            Any: The value from the context, or the default value
        """
        return self.base_manager.get_value(context, key, default)

    def set_value(self, context: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set a value in the context.

        Args:
            context: The execution context
            key: The key to set
            value: The value to set
        """
        self.base_manager.set_value(context, key, value)

    def substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute variables in a string.

        Args:
            text: The string to substitute variables in
            context: The execution context

        Returns:
            str: The string with variables substituted
        """
        return self.variable_substitutor.substitute_variables(text, context)

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
        return self.variable_substitutor.substitute_variables_in_dict(data, context)

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
        return self.validator.validate_context(context, required_keys)

    def serialize_context(self, context: Dict[str, Any]) -> str:
        """
        Serialize a context dictionary to a JSON string.

        Args:
            context: The execution context

        Returns:
            str: The serialized context

        Raises:
            ValueError: If the context cannot be serialized
        """
        return self.serializer.serialize_context(context)

    def deserialize_context(self, serialized_context: str) -> Dict[str, Any]:
        """
        Deserialize a JSON string to a context dictionary.

        Args:
            serialized_context: The serialized context

        Returns:
            Dict[str, Any]: The deserialized context

        Raises:
            ValueError: If the context cannot be deserialized
        """
        return self.serializer.deserialize_context(serialized_context)
