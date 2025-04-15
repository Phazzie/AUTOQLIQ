"""Summary formatter for workflow execution.

This module provides the SummaryFormatter class for formatting workflow execution summaries.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SummaryFormatter:
    """
    Formats workflow execution summaries.
    
    Responsible for creating human-readable summaries of workflow executions.
    """
    
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
