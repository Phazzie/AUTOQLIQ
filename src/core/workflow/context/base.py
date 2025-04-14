"""Base context manager for workflow execution.

This module provides the base context manager for workflow execution.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Base context manager for workflow execution.
    
    Handles context creation and basic operations.
    """
    
    def __init__(self):
        """Initialize the context manager."""
        pass
    
    def create_context(self) -> Dict[str, Any]:
        """
        Create a new execution context.
        
        Returns:
            Dict[str, Any]: A new execution context
        """
        return {}
    
    def update_context(self, context: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an execution context with new values.
        
        Args:
            context: The context to update
            updates: The values to add to the context
            
        Returns:
            Dict[str, Any]: The updated context
        """
        context.update(updates)
        return context
    
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
        return context.get(key, default)
    
    def set_value(self, context: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set a value in the context.
        
        Args:
            context: The execution context
            key: The key to set
            value: The value to set
        """
        context[key] = value
