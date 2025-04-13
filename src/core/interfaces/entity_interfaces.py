"""Entity interfaces for AutoQliq.

This module defines interfaces for core domain entities in the AutoQliq application.
These interfaces establish contracts for entity implementations and facilitate
testing through mocking.
"""

import abc
from typing import List, Dict, Any, Optional

from src.core.interfaces.action import IAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.repository import ICredentialRepository


class IWorkflow(abc.ABC):
    """Interface for workflow entities.
    
    A workflow is a sequence of actions that can be executed to automate
    a specific task in a web browser.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the name of the workflow."""
        pass
    
    @property
    @abc.abstractmethod
    def actions(self) -> List[IAction]:
        """Get the list of actions in the workflow."""
        pass
    
    @abc.abstractmethod
    def add_action(self, action: IAction) -> None:
        """Add an action to the workflow.
        
        Args:
            action: The action to add.
            
        Raises:
            ValidationError: If action is not an IAction.
        """
        pass
    
    @abc.abstractmethod
    def remove_action(self, index: int) -> None:
        """Remove an action from the workflow.
        
        Args:
            index: The index of the action to remove.
            
        Raises:
            IndexError: If the index is out of range.
        """
        pass
    
    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the workflow and all its actions.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        pass
    
    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary representation.
        
        Returns:
            A dictionary containing the workflow's data.
        """
        pass


class ICredential(abc.ABC):
    """Interface for credential entities.
    
    A credential represents a set of login credentials for a website or service.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the name of the credential."""
        pass
    
    @property
    @abc.abstractmethod
    def username(self) -> str:
        """Get the username of the credential."""
        pass
    
    @property
    @abc.abstractmethod
    def password(self) -> str:
        """Get the password of the credential."""
        pass
    
    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the credential data.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        pass
    
    @abc.abstractmethod
    def to_dict(self) -> Dict[str, str]:
        """Convert the credential to a dictionary representation.
        
        Returns:
            A dictionary containing the credential's data.
        """
        pass
