"""Error handling package for AutoQliq workflows.

This package provides error handling strategies for the WorkflowRunner.
"""

from src.core.workflow.error_handling.base import ErrorHandlingStrategyBase
from src.core.workflow.error_handling.stop_strategy import StopOnErrorStrategy
from src.core.workflow.error_handling.continue_strategy import ContinueOnErrorStrategy
from src.core.workflow.error_handling.retry_strategy import RetryOnErrorStrategy
from src.core.workflow.error_handling.factory import create_error_handling_strategy

__all__ = [
    'ErrorHandlingStrategyBase',
    'StopOnErrorStrategy',
    'ContinueOnErrorStrategy',
    'RetryOnErrorStrategy',
    'create_error_handling_strategy',
]
