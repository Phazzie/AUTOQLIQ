"""Result processor for workflow execution.

This module provides the ResultProcessor class for processing workflow execution results.
"""

import logging
from typing import List, Dict, Any, Optional

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
        # Calculate execution time metrics
        time_metrics = self._time_calculator.calculate_time_metrics(start_time)

        # Determine final status based on results and error
        final_status, error_message, summary = self._status_analyzer.determine_status(
            action_results, error
        )

        # Format action results for the log
        formatted_results = self._formatter.format_action_results(action_results)

        # Create the execution log
        execution_log = self._log_builder.create_log_structure(
            workflow_name,
            time_metrics,
            final_status,
            error_message,
            summary,
            error_strategy_name,
            formatted_results
        )

        # Log the workflow completion status
        self._completion_logger.log_workflow_completion(
            workflow_name, final_status, error_message
        )

        return execution_log
