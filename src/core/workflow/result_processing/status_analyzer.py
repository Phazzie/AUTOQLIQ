"""Status analyzer for workflow execution.

This module provides the StatusAnalyzer class for analyzing workflow execution status.
"""

import logging
from typing import List, Optional, Tuple

from src.core.action_result import ActionResult
from src.core.workflow.result_processing.interfaces import (
    IStatusAnalyzer,
    IErrorStatusAnalyzer,
    IResultStatusAnalyzer
)
from src.core.workflow.result_processing.error_status_analyzer import ErrorStatusAnalyzer
from src.core.workflow.result_processing.result_status_analyzer import ResultStatusAnalyzer

logger = logging.getLogger(__name__)


class StatusAnalyzer(IStatusAnalyzer):
    """
    Analyzes workflow execution status.

    Determines the final status of a workflow execution based on action results and errors.
    """

    def __init__(self,
                error_analyzer: IErrorStatusAnalyzer = None,
                result_analyzer: IResultStatusAnalyzer = None):
        """Initialize the status analyzer.

        Args:
            error_analyzer: Optional analyzer for errors
            result_analyzer: Optional analyzer for action results
        """
        self._error_analyzer = error_analyzer or ErrorStatusAnalyzer()
        self._result_analyzer = result_analyzer or ResultStatusAnalyzer()

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
            return self._error_analyzer.analyze_error(error)

        return self._result_analyzer.analyze_results(action_results)
