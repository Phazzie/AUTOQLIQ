"""Context serializer for workflow execution.

This module provides serialization functionality for workflow execution context.
"""

import logging
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ContextSerializer:
    """
    Serializes and deserializes workflow execution context.
    
    Handles conversion between context dictionaries and serialized formats.
    """
    
    def __init__(self):
        """Initialize the context serializer."""
        pass
    
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
        try:
            # Filter out non-serializable values
            serializable_context = self._make_serializable(context)
            return json.dumps(serializable_context)
        except Exception as e:
            logger.error(f"Error serializing context: {e}")
            raise ValueError(f"Error serializing context: {e}") from e
    
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
        try:
            return json.loads(serialized_context)
        except Exception as e:
            logger.error(f"Error deserializing context: {e}")
            raise ValueError(f"Error deserializing context: {e}") from e
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Make an object serializable by converting non-serializable types.
        
        Args:
            obj: The object to make serializable
            
        Returns:
            Any: The serializable object
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert other types to strings
            return str(obj)
