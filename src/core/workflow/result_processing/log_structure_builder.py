"""Log structure builder for workflow execution.

This module provides the LogStructureBuilder class for building execution log structures.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LogStructureBuilder:
    """
    Builds structured execution log dictionaries.
    
    Responsible for creating the structured execution log dictionary.
    """
    
    def create_log_structure(self,
                           workflow_name: str,
                           time_metrics: Dict[str, Any],
                           final_status: str,
                           error_message: Optional[str],
                           summary: str,
                           error_strategy_name: str,
                           formatted_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create the structured execution log dictionary.
        
        Args:
            workflow_name: Name of the workflow
            time_metrics: Time-related metrics
            final_status: Final status of the workflow
            error_message: Optional error message
            summary: Summary of the workflow execution
            error_strategy_name: Name of the error handling strategy
            formatted_results: Formatted action results
            
        Returns:
            Dict[str, Any]: Structured execution log
        """
        return {
            "workflow_name": workflow_name,
            "start_time_iso": time_metrics["start_time_iso"],
            "end_time_iso": time_metrics["end_time_iso"],
            "duration_seconds": time_metrics["duration"],
            "final_status": final_status,
            "error_message": error_message,
            "summary": summary,
            "error_strategy": error_strategy_name,
            "action_results": formatted_results
        }
