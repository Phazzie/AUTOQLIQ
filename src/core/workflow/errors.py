"""Workflow-specific error classes for AutoQliq."""

from src.core.exceptions import AutoQliqError


class WorkflowError(AutoQliqError):
    """Base class for workflow-related errors."""
    
    def __init__(self, message: str, workflow_name: str = None, cause: Exception = None):
        """Initialize a WorkflowError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow where the error occurred.
            cause: Optional exception that caused this error.
        """
        self.workflow_name = workflow_name
        super().__init__(message, cause)
        
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.workflow_name:
            return f"Workflow '{self.workflow_name}': {self.message}"
        return self.message


class WorkflowNotFoundError(WorkflowError):
    """Error raised when a workflow cannot be found."""
    
    def __init__(self, workflow_id: str, cause: Exception = None):
        """Initialize a WorkflowNotFoundError.
        
        Args:
            workflow_id: ID of the workflow that could not be found.
            cause: Optional exception that caused this error.
        """
        super().__init__(f"Workflow not found: {workflow_id}", cause=cause)
        self.workflow_id = workflow_id


class WorkflowValidationError(WorkflowError):
    """Error raised when a workflow fails validation."""
    
    def __init__(self, message: str, workflow_name: str = None, cause: Exception = None):
        """Initialize a WorkflowValidationError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow that failed validation.
            cause: Optional exception that caused this error.
        """
        super().__init__(f"Validation error: {message}", workflow_name, cause)


class WorkflowExecutionError(WorkflowError):
    """Error raised during workflow execution."""
    
    def __init__(self, message: str, workflow_name: str = None, action_name: str = None, cause: Exception = None):
        """Initialize a WorkflowExecutionError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow being executed.
            action_name: Optional name of the action that failed.
            cause: Optional exception that caused this error.
        """
        self.action_name = action_name
        if action_name:
            full_message = f"Execution error in action '{action_name}': {message}"
        else:
            full_message = f"Execution error: {message}"
        super().__init__(full_message, workflow_name, cause)
