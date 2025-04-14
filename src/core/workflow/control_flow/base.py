"""Base interface for control flow handlers.

This module defines the base interface for control flow handlers used by the WorkflowRunner.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError

logger = logging.getLogger(__name__)


class ControlFlowHandlerBase(ABC):
    """
    Abstract base class for control flow handlers.
    
    Defines the interface for handling different types of control flow actions.
    """
    
    def __init__(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None,
                workflow_repo: Optional[IWorkflowRepository] = None):
        """
        Initialize the control flow handler.
        
        Args:
            driver: The web driver instance
            credential_repo: Optional credential repository
            workflow_repo: Optional workflow repository
        """
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo
        self.execute_actions_func: Optional[Callable] = None
    
    @abstractmethod
    def handle(self, action: IAction, context: Dict[str, Any], 
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle a control flow action.
        
        Args:
            action: The control flow action to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages
            
        Returns:
            ActionResult: The result of handling the action
            
        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: For workflow-level errors
        """
        pass
    
    def set_execute_actions_func(self, func: Callable) -> None:
        """
        Set the function to use for executing actions.
        
        Args:
            func: Function that takes (actions, context, workflow_name, log_prefix)
                 and returns a list of ActionResult objects
        """
        self.execute_actions_func = func
    
    def execute_actions(self, actions: List[IAction], context: Dict[str, Any], 
                       workflow_name: str, log_prefix: str) -> List[ActionResult]:
        """
        Execute a list of actions using the provided function.
        
        Args:
            actions: List of actions to execute
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages
            
        Returns:
            List[ActionResult]: Results of the executed actions
            
        Raises:
            RuntimeError: If execute_actions_func is not set
        """
        if self.execute_actions_func is None:
            raise RuntimeError("execute_actions_func must be set before calling execute_actions")
        
        return self.execute_actions_func(actions, context, workflow_name, log_prefix)
