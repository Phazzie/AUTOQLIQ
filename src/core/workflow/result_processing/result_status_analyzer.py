"""Result status analyzer for workflow execution.

This module provides the ResultStatusAnalyzer class for analyzing action results in workflow execution.
"""

import logging
from typing import List, Optional, Tuple

from src.core.action_result import ActionResult

logger = logging.getLogger(__name__)


class ResultStatusAnalyzer:
    """
    Analyzes action results in workflow execution.
    
    Responsible for determining the status, error message, and summary based on action results.
    """
    
    def analyze_results(self, action_results: List[ActionResult]) -> Tuple[str, Optional[str], str]:
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
