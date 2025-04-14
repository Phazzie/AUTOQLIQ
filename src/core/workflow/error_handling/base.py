"""Base interface for error handling strategies.

This module defines the base interface for error handling strategies used by the WorkflowRunner.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError

logger = logging.getLogger(__name__)


class ErrorHandlingStrategyBase(ABC):
    """
    Abstract base class for error handling strategies.
    
    Defines the interface for handling errors during workflow execution.
    Concrete implementations determine how errors are handled (stop, continue, retry).
    """
    
    @abstractmethod
    def handle_action_error(self, error: Exception, action: IAction, 
                           action_display: str) -> ActionResult:
        """
        Handle an error that occurred during action execution.
        
        Args:
            error: The exception that was caught
            action: The action that failed
            action_display: Display name of the action for logging
            
        Returns:
            ActionResult: Result to use for the failed action
            
        Raises:
            ActionError: If the strategy decides to stop execution
            WorkflowError: For workflow-level errors
        """
        pass
    
    @abstractmethod
    def handle_action_failure(self, result: ActionResult, action: IAction, 
                             action_display: str) -> None:
        """
        Handle a failed action result.
        
        Args:
            result: The failed ActionResult
            action: The action that failed
            action_display: Display name of the action for logging
            
        Raises:
            ActionError: If the strategy decides to stop execution
        """
        pass
