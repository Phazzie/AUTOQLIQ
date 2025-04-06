"""Serialization utilities for repository implementations."""
import json
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from src.core.interfaces import IAction
from src.core.actions import ActionFactory

# Type variable for the entity type
T = TypeVar('T')

def serialize_actions(actions: List[IAction]) -> List[Dict[str, Any]]:
    """Serialize a list of actions to a list of dictionaries.
    
    Args:
        actions: The list of actions to serialize
        
    Returns:
        A list of serialized actions
    """
    return [action.to_dict() for action in actions]

def deserialize_actions(action_data: List[Dict[str, Any]]) -> List[IAction]:
    """Deserialize a list of dictionaries to a list of actions.
    
    Args:
        action_data: The list of serialized actions
        
    Returns:
        A list of deserialized actions
        
    Raises:
        Exception: If an action cannot be deserialized
    """
    return [ActionFactory.create_action(data) for data in action_data]

def extract_workflow_actions(workflow_data: Any) -> List[Dict[str, Any]]:
    """Extract action data from workflow data.
    
    This function handles both the new format (with metadata) and the old format
    (just a list of actions).
    
    Args:
        workflow_data: The workflow data
        
    Returns:
        A list of action data
    """
    if isinstance(workflow_data, dict) and "actions" in workflow_data:
        return workflow_data["actions"]
    else:
        # Legacy format - just a list of actions
        return workflow_data

def extract_workflow_metadata(workflow_data: Any, name: str) -> Dict[str, Any]:
    """Extract metadata from workflow data.
    
    This function handles both the new format (with metadata) and the old format
    (just a list of actions).
    
    Args:
        workflow_data: The workflow data
        name: The name of the workflow
        
    Returns:
        A dictionary containing workflow metadata
    """
    if isinstance(workflow_data, dict) and "metadata" in workflow_data:
        return workflow_data["metadata"]
    else:
        # Legacy format - create minimal metadata
        return {
            "name": name,
            "version": "unknown",
            "legacy_format": True
        }
