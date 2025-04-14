"""Status analyzer for workflow execution.

This module provides the StatusAnalyzer class for analyzing workflow execution status.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError

logger = logging.getLogger(__name__)


class StatusAnalyzer:
    """
    Analyzes workflow execution status.
    
    Determines the final status of a workflow execution based on action results and errors.
    """
    
    def __init__(self):
        """Initialize the status analyzer."""
        pass
    
    def determine_status(self, 
                        action_results: List[ActionResult],
                        error: Optional[Exception] = None) -> Tuple[str, Optional[str], str]:
        """
        Determine the final status, error message, and summary of a workflow execution.
        
        Args:
            action_results: Results of the executed actions
            error: Optional exception that caused the workflow to fail
            
        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        if error:
            return self._analyze_error(error)
        
        return self._analyze_results(action_results)
    
    def _analyze_error(self, error: Exception) -> Tuple[str, str, str]:
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
    
    def _analyze_results(self, action_results: List[ActionResult]) -> Tuple[str, Optional[str], str]:
        """
        Analyze action results to determine the workflow status.
        
        Args:
            action_results: Results of the executed actions
            
        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        # Count successes and failures
        success_count = sum(1 for result in action_results if result.is_success())
        failure_count = len(action_results) - success_count
        
        # Check if any actions failed
        if failure_count > 0:
            return (
                "COMPLETED_WITH_ERRORS",
                f"{failure_count} action(s) failed",
                f"Completed with {success_count} successful actions and {failure_count} failures"
            )
        
        # All actions succeeded
        return (
            "SUCCESS",
            None,
            f"All {len(action_results)} actions completed successfully"
        )
