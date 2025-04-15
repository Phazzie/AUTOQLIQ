"""Action result formatter for workflow execution.

This module provides the ActionResultFormatter class for formatting action results.
"""

import logging
from typing import Dict, Any, List

from src.core.action_result import ActionResult
from src.core.workflow.result_processing.sensitive_data_filter import SensitiveDataFilter

logger = logging.getLogger(__name__)


class ActionResultFormatter:
    """
    Formats action results for workflow execution logs.
    
    Responsible for formatting individual action results.
    """
    
    def __init__(self, sensitive_data_filter: SensitiveDataFilter = None):
        """
        Initialize the action result formatter.
        
        Args:
            sensitive_data_filter: Optional filter for sensitive data
        """
        self.sensitive_data_filter = sensitive_data_filter or SensitiveDataFilter()
    
    def format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the execution log.
        
        Args:
            action_results: Results of the executed actions
            
        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        return [self._format_single_result(result) for result in action_results]
    
    def _format_single_result(self, result: ActionResult) -> Dict[str, Any]:
        """
        Format a single action result for the execution log.
        
        Args:
            result: The action result to format
            
        Returns:
            Dict[str, Any]: Formatted action result
        """
        formatted_result = {
            "status": result.status.value,
            "message": result.message
        }
        
        # Include additional data if present
        if result.data:
            # Filter out sensitive data
            safe_data = self.sensitive_data_filter.filter_data(result.data)
            if safe_data:
                formatted_result["data"] = safe_data
        
        return formatted_result
