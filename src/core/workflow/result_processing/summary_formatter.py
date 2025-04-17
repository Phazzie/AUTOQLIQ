"""Summary formatter for workflow execution.

This module provides the SummaryFormatter class for formatting workflow execution summaries.
"""

import logging
from typing import Dict, Any

from src.core.workflow.result_processing.interfaces import ISummaryFormatter

logger = logging.getLogger(__name__)


class SummaryFormatter(ISummaryFormatter):
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
        success_count = self._count_successful_actions(execution_log["action_results"])

        summary = self._build_summary(workflow_name, status, duration, success_count, action_count)

        if execution_log.get("error_message"):
            summary += f"\nError: {execution_log['error_message']}"

        return summary

    def _count_successful_actions(self, action_results: list) -> int:
        """
        Count the number of successful actions.

        Args:
            action_results: List of action results

        Returns:
            int: Number of successful actions
        """
        return sum(1 for result in action_results if result["status"] == "success")

    def _build_summary(self, workflow_name: str, status: str, duration: float, success_count: int, action_count: int) -> str:
        """
        Build the summary string.

        Args:
            workflow_name: Name of the workflow
            status: Final status of the workflow
            duration: Duration of the workflow execution
            success_count: Number of successful actions
            action_count: Total number of actions

        Returns:
            str: Summary string
        """
        summary = f"Workflow '{workflow_name}' {status.lower()}"
        summary += f" in {duration:.2f} seconds"
        summary += f" ({success_count}/{action_count} actions successful)"
        return summary
