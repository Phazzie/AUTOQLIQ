"""Workflow entity module for AutoQliq.

This module provides the Workflow entity class for browser automation.
"""

import json
import uuid
from typing import List, Dict, Any, Optional

from src.core.interfaces import IAction, IWorkflow
from src.core.exceptions import ValidationError


class Workflow(IWorkflow):
    """
    Represents a sequence of actions to be executed.
    
    A workflow is the core entity in AutoQliq, consisting of a sequence of actions
    that will be executed in order by the WorkflowRunner.
    
    Attributes:
        id (str): Unique identifier for the workflow.
        name (str): User-friendly name for the workflow.
        description (str): Optional description of the workflow's purpose.
        actions (List[IAction]): Sequence of actions to be executed.
        metadata (Dict[str, Any]): Additional metadata about the workflow.
    """
    
    def __init__(
        self,
        name: str,
        actions: Optional[List[IAction]] = None,
        description: str = "",
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Workflow instance.
        
        Args:
            name: User-friendly name for the workflow.
            actions: List of actions to be executed (default empty list).
            description: Optional description of the workflow's purpose.
            workflow_id: Optional unique identifier (generated if not provided).
            metadata: Optional additional metadata.
        
        Raises:
            ValidationError: If name is empty or actions contains non-IAction objects.
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty.")
        
        self.id = workflow_id or str(uuid.uuid4())
        self._name = name
        self.description = description
        self._actions = actions or []
        self.metadata = metadata or {}
        
        # Validate actions
        for i, action in enumerate(self._actions):
            if not isinstance(action, IAction):
                raise ValidationError(f"Item at index {i} is not an IAction: {type(action).__name__}")
    
    @property
    def name(self) -> str:
        """Get the name of the workflow."""
        return self._name
    
    @property
    def actions(self) -> List[IAction]:
        """Get the list of actions in the workflow."""
        return self._actions.copy()  # Return a copy to prevent direct modification
    
    def add_action(self, action: IAction) -> None:
        """Add an action to the workflow.
        
        Args:
            action: The action to add.
            
        Raises:
            ValidationError: If action is not an IAction.
        """
        if not isinstance(action, IAction):
            raise ValidationError(f"Cannot add non-IAction object: {type(action).__name__}")
        
        self._actions.append(action)
    
    def remove_action(self, index: int) -> None:
        """Remove an action from the workflow.
        
        Args:
            index: The index of the action to remove.
            
        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= len(self._actions):
            raise IndexError(f"Action index {index} out of range")
        
        self._actions.pop(index)
    
    def validate(self) -> bool:
        """Validate the workflow and all its actions.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self._name:
            raise ValidationError("Workflow name cannot be empty.")
        
        for i, action in enumerate(self._actions):
            try:
                action.validate()
            except ValidationError as e:
                raise ValidationError(f"Action at index {i} ({action.name}) failed validation: {e}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary representation.
        
        Returns:
            A dictionary containing the workflow's data.
        """
        return {
            "id": self.id,
            "name": self._name,
            "description": self.description,
            "actions": [action.to_dict() for action in self._actions],
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert the workflow to a JSON string.
        
        Returns:
            A JSON string representing the workflow.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], action_factory=None) -> 'Workflow':
        """Create a Workflow from a dictionary.
        
        Args:
            data: A dictionary containing workflow data.
            action_factory: Optional factory for creating actions from dictionaries.
                If not provided, actions must be pre-instantiated.
                
        Returns:
            A new Workflow instance.
            
        Raises:
            ValidationError: If required data is missing or invalid.
        """
        if not data.get("name"):
            raise ValidationError("Workflow data must include a name.")
        
        # Handle actions based on whether a factory is provided
        actions = []
        action_dicts = data.get("actions", [])
        
        if action_factory and callable(getattr(action_factory, "create_action", None)):
            actions = [action_factory.create_action(action_dict) for action_dict in action_dicts]
        elif all(isinstance(a, IAction) for a in action_dicts):
            # If action_dicts contains IAction instances directly
            actions = action_dicts
        else:
            # Cannot create actions without a factory
            raise ValidationError("Cannot create actions from dictionaries without an action factory.")
        
        return cls(
            name=data["name"],
            actions=actions,
            description=data.get("description", ""),
            workflow_id=data.get("id"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str, action_factory=None) -> 'Workflow':
        """Create a Workflow from a JSON string.
        
        Args:
            json_str: A JSON string representing a workflow.
            action_factory: Optional factory for creating actions from dictionaries.
                
        Returns:
            A new Workflow instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data, action_factory)
    
    def __str__(self) -> str:
        """Return a string representation of the workflow."""
        return f"Workflow(id={self.id}, name={self._name}, actions={len(self._actions)})"
