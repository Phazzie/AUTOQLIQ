"""Result processor for workflow execution.

This module provides the ResultProcessor class for processing workflow execution results.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from src.core.action_result import ActionResult
from src.core.workflow.result_processing.interfaces import (
    IResultFormatter,
    IStatusAnalyzer,
    ITimeMetricsCalculator,
    ILogStructureBuilder,
    IWorkflowCompletionLogger,
    IFactory
)
from src.core.workflow.result_processing.factory import ComponentFactory

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Processes workflow execution results.

    Responsible for creating the execution log and determining the final status.
    """

    def __init__(self,
                factory: IFactory = None,
                formatter: IResultFormatter = None,
                status_analyzer: IStatusAnalyzer = None,
                time_calculator: ITimeMetricsCalculator = None,
                log_builder: ILogStructureBuilder = None,
                completion_logger: IWorkflowCompletionLogger = None):
        """Initialize the result processor.

        Args:
            factory: Optional factory for creating components
            formatter: Optional formatter for results
            status_analyzer: Optional analyzer for determining status
            time_calculator: Optional calculator for time metrics
            log_builder: Optional builder for log structure
            completion_logger: Optional logger for workflow completion
        """
        self._factory = factory or ComponentFactory()

        # Initialize components using factory if not provided
        self._formatter = formatter or self._factory.create(IResultFormatter)
        self._status_analyzer = status_analyzer or self._factory.create(IStatusAnalyzer)
        self._time_calculator = time_calculator or self._factory.create(ITimeMetricsCalculator)
        self._log_builder = log_builder or self._factory.create(ILogStructureBuilder)
        self._completion_logger = completion_logger or self._factory.create(IWorkflowCompletionLogger)

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
        time_metrics = self._calculate_time_metrics(start_time)
        final_status, error_message, summary = self._determine_status(action_results, error)
        formatted_results = self._format_action_results(action_results)
        execution_log = self._build_log_structure(
            workflow_name,
            time_metrics,
            final_status,
            error_message,
            summary,
            error_strategy_name,
            formatted_results
        )
        self._log_workflow_completion(workflow_name, final_status, error_message)
        return execution_log

    def _calculate_time_metrics(self, start_time: float) -> Dict[str, Any]:
        """
        Calculate execution time metrics.

        Args:
            start_time: Start time of the workflow execution (from time.time())

        Returns:
            Dict[str, Any]: Time metrics including end time, duration, and formatted timestamps
        """
        return self._time_calculator.calculate_time_metrics(start_time)

    def _determine_status(self,
                        action_results: List[ActionResult],
                        error: Optional[Exception] = None) -> Tuple[str, Optional[str], str]:
        """
        Determine final status based on results and error.

        Args:
            action_results: Results of the executed actions
            error: Optional exception that caused the workflow to fail

        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        return self._status_analyzer.determine_status(action_results, error)

    def _format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the log.

        Args:
            action_results: Results of the executed actions

        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        return self._formatter.format_action_results(action_results)

    def _build_log_structure(self,
                            workflow_name: str,
                            time_metrics: Dict[str, Any],
                            final_status: str,
                            error_message: Optional[str],
                            summary: str,
                            error_strategy_name: str,
                            formatted_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create the execution log.

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
        return self._log_builder.create_log_structure(
            workflow_name,
            time_metrics,
            final_status,
            error_message,
            summary,
            error_strategy_name,
            formatted_results
        )

    def _log_workflow_completion(self,
                                workflow_name: str,
                                final_status: str,
                                error_message: Optional[str]) -> None:
        """
        Log the workflow completion status.

        Args:
            workflow_name: Name of the workflow
            final_status: Final status of the workflow
            error_message: Optional error message
        """
        self._completion_logger.log_workflow_completion(
            workflow_name, final_status, error_message
        )
