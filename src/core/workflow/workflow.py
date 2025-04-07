"""Workflow module for AutoQliq.

Provides the Workflow class that represents a sequence of actions to be executed.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

from src.core.interfaces.action import IAction
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Workflow:
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
        self.name = name
        self.description = description
        self.actions = actions or []
        self.metadata = metadata or {}
        
        # Validate actions
        for i, action in enumerate(self.actions):
            if not isinstance(action, IAction):
                raise ValidationError(f"Item at index {i} is not an IAction: {type(action).__name__}")
    
    def add_action(self, action: IAction) -> None:
        """Add an action to the workflow.
        
        Args:
            action: The action to add.
            
        Raises:
            ValidationError: If action is not an IAction.
        """
        if not isinstance(action, IAction):
            raise ValidationError(f"Cannot add non-IAction object: {type(action).__name__}")
        
        self.actions.append(action)
        logger.debug(f"Added action '{action.name}' to workflow '{self.name}'")
    
    def remove_action(self, index: int) -> IAction:
        """Remove an action from the workflow by index.
        
        Args:
            index: The index of the action to remove.
            
        Returns:
            The removed action.
            
        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self.actions):
            raise IndexError(f"Action index {index} out of range (0-{len(self.actions)-1})")
        
        action = self.actions.pop(index)
        logger.debug(f"Removed action '{action.name}' from workflow '{self.name}'")
        return action
    
    def move_action(self, from_index: int, to_index: int) -> None:
        """Move an action from one position to another.
        
        Args:
            from_index: The current index of the action.
            to_index: The target index for the action.
            
        Raises:
            IndexError: If either index is out of range.
        """
        if from_index < 0 or from_index >= len(self.actions):
            raise IndexError(f"Source index {from_index} out of range (0-{len(self.actions)-1})")
        
        # Allow to_index to be equal to len(self.actions) to move to the end
        if to_index < 0 or to_index > len(self.actions):
            raise IndexError(f"Target index {to_index} out of range (0-{len(self.actions)})")
        
        if from_index == to_index:
            return  # No change needed
        
        action = self.actions.pop(from_index)
        self.actions.insert(to_index, action)
        logger.debug(f"Moved action '{action.name}' from position {from_index} to {to_index}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the workflow to a dictionary.
        
        Returns:
            A dictionary representation of the workflow.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], actions: List[IAction]) -> 'Workflow':
        """Create a Workflow instance from a dictionary and pre-deserialized actions.
        
        Args:
            data: Dictionary containing workflow data.
            actions: List of already deserialized IAction objects.
            
        Returns:
            A new Workflow instance.
            
        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict, got {type(data).__name__}")
        
        required_fields = ["name"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        return cls(
            name=data["name"],
            actions=actions,
            description=data.get("description", ""),
            workflow_id=data.get("id"),
            metadata=data.get("metadata", {})
        )
    
    def validate(self) -> bool:
        """Validate the workflow and all its actions.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self.name:
            raise ValidationError("Workflow name cannot be empty.")
        
        for i, action in enumerate(self.actions):
            try:
                action.validate()
            except ValidationError as e:
                raise ValidationError(f"Action at index {i} ({action.name}) failed validation: {e}")
        
        return True
    
    def __str__(self) -> str:
        """Return a string representation of the workflow."""
        return f"Workflow(id={self.id}, name={self.name}, actions={len(self.actions)})"
