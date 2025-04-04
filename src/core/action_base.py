from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Any, Optional

from src.core.interfaces import IAction, IWebDriver


class ActionStatus(Enum):
    """Enum representing the status of an action execution."""
    SUCCESS = auto()
    FAILURE = auto()


class ActionResult:
    """
    Represents the result of an action execution.
    
    Attributes:
        status: The status of the action execution (SUCCESS or FAILURE)
        message: An optional message providing details about the result
    """
    
    def __init__(self, status: ActionStatus, message: Optional[str] = None):
        """
        Initialize an ActionResult.
        
        Args:
            status: The status of the action execution
            message: An optional message providing details about the result
        """
        self.status = status
        self.message = message
    
    def is_success(self) -> bool:
        """
        Check if the result represents a successful execution.
        
        Returns:
            True if the status is SUCCESS, False otherwise
        """
        return self.status == ActionStatus.SUCCESS
    
    def __str__(self) -> str:
        """
        Return a string representation of the ActionResult.
        
        Returns:
            A string representation including status and message
        """
        return f"ActionResult(status={self.status.name}, message='{self.message}')"
    
    @classmethod
    def success(cls, message: Optional[str] = None) -> 'ActionResult':
        """
        Create a success result.
        
        Args:
            message: An optional message providing details about the success
            
        Returns:
            An ActionResult with SUCCESS status
        """
        return cls(ActionStatus.SUCCESS, message)
    
    @classmethod
    def failure(cls, message: str = "Action failed") -> 'ActionResult':
        """
        Create a failure result.
        
        Args:
            message: A message providing details about the failure
            
        Returns:
            An ActionResult with FAILURE status
        """
        return cls(ActionStatus.FAILURE, message)


class ActionBase(IAction, ABC):
    """
    Base class for all actions in the system.
    
    This abstract class provides common functionality for all actions
    and ensures they implement the IAction interface.
    
    Attributes:
        name: A descriptive name for the action
    """
    
    def __init__(self, name: str):
        """
        Initialize an ActionBase.
        
        Args:
            name: A descriptive name for the action
        """
        self.name = name
    
    def validate(self) -> bool:
        """
        Validate that the action is properly configured.
        
        This method can be overridden by subclasses to provide
        specific validation logic.
        
        Returns:
            True if the action is valid, False otherwise
        """
        return True
    
    @abstractmethod
    def execute(self, driver: IWebDriver) -> ActionResult:
        """
        Execute the action using the provided web driver.
        
        Args:
            driver: The web driver to use for execution
            
        Returns:
            An ActionResult indicating success or failure
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the action to a dictionary representation.
        
        Returns:
            A dictionary containing the action's data
        """
        pass
