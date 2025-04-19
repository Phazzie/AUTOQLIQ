"""Error handling strategy enum for AutoQliq workflows.

This module provides an enum for error handling strategies.
"""

from enum import Enum, auto


class ErrorHandlingStrategy(Enum):
    """
    Enum representing different error handling strategies for workflow execution.
    
    STOP_ON_ERROR: Stop workflow execution on the first error.
    CONTINUE_ON_ERROR: Continue workflow execution after errors.
    RETRY_ON_ERROR: Retry failed actions before continuing or stopping.
    """
    STOP_ON_ERROR = auto()
    CONTINUE_ON_ERROR = auto()
    RETRY_ON_ERROR = auto()
