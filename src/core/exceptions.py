class LoginFailedError(Exception):
    """Raised when login fails due to incorrect credentials or other issues."""
    pass

class WorkflowError(Exception):
    """Raised when there is an error in the workflow execution."""
    pass
