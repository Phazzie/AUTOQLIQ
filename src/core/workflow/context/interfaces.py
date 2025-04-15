"""Interfaces for context management components.

This module provides interfaces for the context management components to enable
dependency inversion and improve SOLID compliance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set


class IContextProvider(ABC):
    """Interface for context providers."""

    @abstractmethod
    def create_context(self) -> Dict[str, Any]:
        """
        Create a new execution context.

        Returns:
            Dict[str, Any]: A new execution context
        """
        pass

    @abstractmethod
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
        pass


class IContextUpdater(ABC):
    """Interface for context updaters."""

    @abstractmethod
    def update_context(self, context: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an execution context with new values.

        Args:
            context: The context to update
            updates: The values to add to the context

        Returns:
            Dict[str, Any]: The updated context
        """
        pass

    @abstractmethod
    def set_value(self, context: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set a value in the context.

        Args:
            context: The execution context
            key: The key to set
            value: The value to set
        """
        pass


class IVariableResolver(ABC):
    """Interface for variable resolvers."""

    @abstractmethod
    def substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute variables in a string.

        Args:
            text: The string to substitute variables in
            context: The execution context

        Returns:
            str: The string with variables substituted
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass


class IContextValidator(ABC):
    """Interface for context validators."""

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_available_keys(self, context: Dict[str, Any]) -> Set[str]:
        """
        Get a set of all keys available in the context.

        Args:
            context: The execution context

        Returns:
            Set[str]: Set of available keys
        """
        pass


class IContextSerializer(ABC):
    """Interface for context serializers."""

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass


class IWorkflowContextManager(ABC):
    """Interface for workflow context managers."""

    @abstractmethod
    def create_context(self) -> Dict[str, Any]:
        """
        Create a new execution context.

        Returns:
            Dict[str, Any]: A new execution context
        """
        pass

    @abstractmethod
    def update_context(self, context: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an execution context with new values.

        Args:
            context: The context to update
            updates: The values to add to the context

        Returns:
            Dict[str, Any]: The updated context
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def set_value(self, context: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set a value in the context.

        Args:
            context: The execution context
            key: The key to set
            value: The value to set
        """
        pass

    @abstractmethod
    def substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute variables in a string.

        Args:
            text: The string to substitute variables in
            context: The execution context

        Returns:
            str: The string with variables substituted
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
