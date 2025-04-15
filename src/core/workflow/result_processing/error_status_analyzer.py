"""Error status analyzer for workflow execution.

This module provides the ErrorStatusAnalyzer class for analyzing errors in workflow execution.
"""

import logging
from typing import Tuple, Optional

from src.core.exceptions import WorkflowError, ActionError

logger = logging.getLogger(__name__)


class ErrorStatusAnalyzer:
    """
    Analyzes errors in workflow execution.
    
    Responsible for determining the status, error message, and summary based on errors.
    """
    
    def analyze_error(self, error: Exception) -> Tuple[str, str, str]:
        """
        Analyze an error to determine the workflow status.
        
        Args:
            error: The exception that caused the workflow to fail
            
        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        # Handle different error types
        if isinstance(error, WorkflowError) and "stopped by request" in str(error).lower():
            return "STOPPED", "Execution stopped by user request.", "Execution stopped by user request"
        elif isinstance(error, ActionError):
            return "FAILED", str(error), f"Failed during action '{error.action_name}': {error}"
        elif isinstance(error, WorkflowError):
            return "FAILED", str(error), f"Workflow error: {error}"
        else:
            return "FAILED", f"Unexpected error: {error}", f"Unexpected error: {error}"
