"""Detailed report formatter for workflow execution.

This module provides the DetailedReportFormatter class for formatting detailed workflow execution reports.
"""

import logging
from typing import Dict, Any, List

from src.core.workflow.result_processing.interfaces import IDetailedReportFormatter

logger = logging.getLogger(__name__)


class DetailedReportFormatter(IDetailedReportFormatter):
    """
    Formats detailed workflow execution reports.

    Responsible for creating detailed reports of workflow executions.
    """

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
