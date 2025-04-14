"""Result processor for workflow execution.

This module provides the ResultProcessor class for processing workflow execution results.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Processes workflow execution results.
    
    Responsible for creating the execution log and determining the final status.
    """
    
    def __init__(self):
        """Initialize the result processor."""
        pass
    
    def create_execution_log(self, 
                            workflow_name: str,
                            action_results: List[ActionResult],
                            start_time: float,
                            error: Optional[Exception] = None,
                            error_strategy_name: str = "STOP_ON_ERROR") -> Dict[str, Any]:
        """
        Create a detailed execution log from the workflow results.
        
        Args:
            workflow_name: Name of the workflow
            action_results: Results of the executed actions
            start_time: Start time of the workflow execution (from time.time())
            error: Optional exception that caused the workflow to fail
            error_strategy_name: Name of the error handling strategy used
            
        Returns:
            Dict[str, Any]: Detailed execution log
        """
        end_time = time.time()
        duration = end_time - start_time
        
        # Determine final status based on results and error
        final_status, error_message, summary = self._determine_status(action_results, error)
        
        # Format action results for the log
        formatted_results = self._format_action_results(action_results)
        
        # Create the execution log
        execution_log = {
            "workflow_name": workflow_name,
            "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
            "end_time_iso": datetime.fromtimestamp(end_time).isoformat(),
            "duration_seconds": round(duration, 2),
            "final_status": final_status,
            "error_message": error_message,
            "summary": summary,
            "error_strategy": error_strategy_name,
            "action_results": formatted_results
        }
        
        logger.info(f"Workflow '{workflow_name}' completed with status: {final_status}")
        if error_message:
            logger.error(f"Workflow error: {error_message}")
        
        return execution_log
    
    def _determine_status(self, 
                         action_results: List[ActionResult],
                         error: Optional[Exception]) -> Tuple[str, Optional[str], str]:
        """
        Determine the final status, error message, and summary of a workflow execution.
        
        Args:
            action_results: Results of the executed actions
            error: Optional exception that caused the workflow to fail
            
        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        if error:
            # Handle different error types
            if isinstance(error, WorkflowError) and "stopped by request" in str(error).lower():
                return "STOPPED", "Execution stopped by user request.", "Execution stopped by user request"
            elif isinstance(error, ActionError):
                return "FAILED", str(error), f"Failed during action '{error.action_name}': {error}"
            elif isinstance(error, WorkflowError):
                return "FAILED", str(error), f"Workflow error: {error}"
            else:
                return "FAILED", f"Unexpected error: {error}", f"Unexpected error: {error}"
        
        # Check if any actions failed
        if any(not result.is_success() for result in action_results):
            return "COMPLETED_WITH_ERRORS", "Some actions failed", "Completed with some actions failing"
        
        # All actions succeeded
        return "SUCCESS", None, f"All {len(action_results)} actions completed successfully"
    
    def _format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the execution log.
        
        Args:
            action_results: Results of the executed actions
            
        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        formatted_results = []
        
        for result in action_results:
            formatted_result = {
                "status": result.status.value,
                "message": result.message
            }
            
            # Include additional data if present
            if result.data:
                # Filter out sensitive data if needed
                safe_data = self._filter_sensitive_data(result.data)
                if safe_data:
                    formatted_result["data"] = safe_data
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out sensitive data from the result data.
        
        Args:
            data: The data to filter
            
        Returns:
            Dict[str, Any]: Filtered data
        """
        # Create a copy to avoid modifying the original
        filtered_data = data.copy()
        
        # List of keys that might contain sensitive information
        sensitive_keys = ["password", "token", "secret", "key", "credential"]
        
        # Remove or mask sensitive data
        for key in list(filtered_data.keys()):
            if any(sensitive_word in key.lower() for sensitive_word in sensitive_keys):
                filtered_data[key] = "********"  # Mask sensitive data
        
        return filtered_data
