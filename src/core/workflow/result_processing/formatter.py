"""Result formatter for workflow execution.

This module provides the ResultFormatter class for formatting workflow execution results.
"""

import logging
from typing import Dict, Any, List

from src.core.action_result import ActionResult

logger = logging.getLogger(__name__)


class ResultFormatter:
    """
    Formats workflow execution results for display or logging.
    
    Provides methods for formatting execution logs in different formats.
    """
    
    def __init__(self):
        """Initialize the result formatter."""
        pass
    
    def format_summary(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a human-readable summary of the workflow execution.
        
        Args:
            execution_log: The execution log
            
        Returns:
            str: Human-readable summary
        """
        workflow_name = execution_log["workflow_name"]
        status = execution_log["final_status"]
        duration = execution_log["duration_seconds"]
        action_count = len(execution_log["action_results"])
        success_count = sum(1 for result in execution_log["action_results"] 
                          if result["status"] == "success")
        
        summary = f"Workflow '{workflow_name}' {status.lower()}"
        summary += f" in {duration:.2f} seconds"
        summary += f" ({success_count}/{action_count} actions successful)"
        
        if execution_log.get("error_message"):
            summary += f"\nError: {execution_log['error_message']}"
        
        return summary
    
    def format_detailed_report(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a detailed report of the workflow execution.
        
        Args:
            execution_log: The execution log
            
        Returns:
            str: Detailed report
        """
        workflow_name = execution_log["workflow_name"]
        status = execution_log["final_status"]
        start_time = execution_log["start_time_iso"]
        end_time = execution_log["end_time_iso"]
        duration = execution_log["duration_seconds"]
        error_message = execution_log.get("error_message", "None")
        
        report = [
            f"Workflow Execution Report: '{workflow_name}'",
            f"Status: {status}",
            f"Start Time: {start_time}",
            f"End Time: {end_time}",
            f"Duration: {duration:.2f} seconds",
            f"Error: {error_message}",
            "\nAction Results:"
        ]
        
        for i, result in enumerate(execution_log["action_results"]):
            status_str = "✓" if result["status"] == "success" else "✗"
            report.append(f"{i+1}. {status_str} {result['message']}")
        
        return "\n".join(report)
    
    def format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
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
                # Filter out sensitive data
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
