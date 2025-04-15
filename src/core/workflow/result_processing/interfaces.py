"""Interfaces for result processing components.

This module provides interfaces for the result processing components to enable
dependency inversion and improve SOLID compliance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Type, TypeVar

from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError


T = TypeVar('T')


class IFactory(ABC):
    """Interface for component factories."""

    @abstractmethod
    def create(self, component_type: Type[T], **kwargs) -> T:
        """
        Create a component of the specified type.

        Args:
            component_type: The type of component to create
            **kwargs: Additional arguments for component creation

        Returns:
            T: An instance of the specified component type
        """
        pass


class IErrorHandler(ABC):
    """Interface for error handlers."""

    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """
        Determine if this handler can handle the given error.

        Args:
            error: The exception to handle

        Returns:
            bool: True if this handler can handle the error
        """
        pass

    @abstractmethod
    def handle(self, error: Exception) -> Tuple[str, str, str]:
        """
        Handle the error and determine the workflow status.

        Args:
            error: The exception to handle

        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        pass


class ITimeMetricsCalculator(ABC):
    """Interface for calculating time-related metrics for workflow execution."""

    @abstractmethod
    def calculate_time_metrics(self, start_time: float) -> Dict[str, Any]:
        """
        Calculate time-related metrics for the execution log.

        Args:
            start_time: Start time of the workflow execution (from time.time())

        Returns:
            Dict[str, Any]: Time metrics including end time, duration, and formatted timestamps
        """
        pass


class ILogStructureBuilder(ABC):
    """Interface for building structured execution log dictionaries."""

    @abstractmethod
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
        pass


class IWorkflowCompletionLogger(ABC):
    """Interface for logging workflow completion status."""

    @abstractmethod
    def log_workflow_completion(self,
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
        pass


class IErrorStatusAnalyzer(ABC):
    """Interface for analyzing errors in workflow execution."""

    @abstractmethod
    def analyze_error(self, error: Exception) -> Tuple[str, str, str]:
        """
        Analyze an error to determine the workflow status.

        Args:
            error: The exception that caused the workflow to fail

        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        pass


class IResultStatusAnalyzer(ABC):
    """Interface for analyzing action results in workflow execution."""

    @abstractmethod
    def analyze_results(self, action_results: List[ActionResult]) -> Tuple[str, Optional[str], str]:
        """
        Analyze action results to determine the workflow status.

        Args:
            action_results: Results of the executed actions

        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        pass


class IStatusAnalyzer(ABC):
    """Interface for analyzing workflow execution status."""

    @abstractmethod
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
        pass


class ISummaryFormatter(ABC):
    """Interface for formatting workflow execution summaries."""

    @abstractmethod
    def format_summary(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a human-readable summary of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Human-readable summary
        """
        pass


class IDetailedReportFormatter(ABC):
    """Interface for formatting detailed workflow execution reports."""

    @abstractmethod
    def format_detailed_report(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a detailed report of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Detailed report
        """
        pass


class IActionResultFormatter(ABC):
    """Interface for formatting action results for workflow execution logs."""

    @abstractmethod
    def format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the execution log.

        Args:
            action_results: Results of the executed actions

        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        pass


class IResultFormatter(ABC):
    """Interface for formatting workflow execution results."""

    @abstractmethod
    def format_summary(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a human-readable summary of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Human-readable summary
        """
        pass

    @abstractmethod
    def format_detailed_report(self, execution_log: Dict[str, Any]) -> str:
        """
        Format a detailed report of the workflow execution.

        Args:
            execution_log: The execution log

        Returns:
            str: Detailed report
        """
        pass

    @abstractmethod
    def format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
        """
        Format action results for the execution log.

        Args:
            action_results: Results of the executed actions

        Returns:
            List[Dict[str, Any]]: Formatted action results
        """
        pass
