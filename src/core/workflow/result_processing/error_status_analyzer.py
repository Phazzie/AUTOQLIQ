"""Error status analyzer for workflow execution.

This module provides the ErrorStatusAnalyzer class for analyzing errors in workflow execution.
"""

import logging
from typing import List, Tuple, Optional

from src.core.exceptions import WorkflowError, ActionError
from src.core.workflow.result_processing.interfaces import IErrorStatusAnalyzer, IErrorHandler
from src.core.workflow.result_processing.error_handlers import (
    StopRequestHandler, ActionErrorHandler, WorkflowErrorHandler, GenericErrorHandler
)

logger = logging.getLogger(__name__)


class ErrorStatusAnalyzer(IErrorStatusAnalyzer):
    """
    Analyzes errors in workflow execution.

    Responsible for determining the status, error message, and summary based on errors.
    """

    def __init__(self, handlers: List[IErrorHandler] = None):
        """
        Initialize the error status analyzer.

        Args:
            handlers: Optional list of error handlers
        """
        self._handlers = handlers or [
            StopRequestHandler(),
            ActionErrorHandler(),
            WorkflowErrorHandler(),
            GenericErrorHandler()
        ]

    def analyze_error(self, error: Exception) -> Tuple[str, str, str]:
        """
        Analyze an error to determine the workflow status.

        Args:
            error: The exception that caused the workflow to fail

        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        for handler in self._handlers:
            if handler.can_handle(error):
                return handler.handle(error)

        # This should never happen because GenericErrorHandler handles all errors
        return "FAILED", f"Unhandled error: {error}", f"Unhandled error: {error}"
