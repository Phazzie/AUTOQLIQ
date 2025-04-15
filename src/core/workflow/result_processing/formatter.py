"""Result formatter for workflow execution.

This module provides the ResultFormatter class for formatting workflow execution results.
"""

import logging
from typing import Dict, Any, List

from src.core.action_result import ActionResult
from src.core.workflow.result_processing.interfaces import (
    IResultFormatter,
    ISummaryFormatter,
    IDetailedReportFormatter,
    IActionResultFormatter
)
from src.core.workflow.result_processing.summary_formatter import SummaryFormatter
from src.core.workflow.result_processing.detailed_report_formatter import DetailedReportFormatter
from src.core.workflow.result_processing.action_result_formatter import ActionResultFormatter

logger = logging.getLogger(__name__)


class ResultFormatter(IResultFormatter):
    """
    Formats workflow execution results for display or logging.

    Provides methods for formatting execution logs in different formats.
    """

    def __init__(self,
                summary_formatter: ISummaryFormatter = None,
                detailed_report_formatter: IDetailedReportFormatter = None,
                action_result_formatter: IActionResultFormatter = None):
        """Initialize the result formatter.

        Args:
            summary_formatter: Optional formatter for summaries
            detailed_report_formatter: Optional formatter for detailed reports
            action_result_formatter: Optional formatter for action results
        """
        self._summary_formatter = summary_formatter or SummaryFormatter()
        self._detailed_report_formatter = detailed_report_formatter or DetailedReportFormatter()
        self._action_result_formatter = action_result_formatter or ActionResultFormatter()

    def format_summary(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a human-readable summary of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Human-readable summary
        """
        return self._summary_formatter.format_summary(execution_log)

    def format_detailed_report(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a detailed report of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Detailed report
        """
        return self._detailed_report_formatter.format_detailed_report(execution_log)

    def format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the execution log.

        Args:
            action_results: Results of the executed actions

        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        return self._action_result_formatter.format_action_results(action_results)
