"""Result processor for workflow execution.

This module provides the ResultProcessor class for processing workflow execution results.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError

logger = logging.getLogger(__name__)


class ResultProcessor:
    """
    Processes workflow execution results.

    Responsible for creating the execution log and determining the final status.
    """

    def __init__(self):
        """Initialize the result processor."""
        pass

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
        time_metrics = self._calculate_time_metrics(start_time)

        # Determine final status based on results and error
        final_status, error_message, summary = self._determine_status(action_results, error)

        # Format action results for the log
        formatted_results = self._format_action_results(action_results)

        # Create the execution log
        execution_log = self._create_log_structure(
            workflow_name,
            time_metrics,
            final_status,
            error_message,
            summary,
            error_strategy_name,
            formatted_results
        )

        # Log the workflow completion status
        self._log_workflow_completion(workflow_name, final_status, error_message)

        return execution_log

    def _calculate_time_metrics(self, start_time: float) -> Dict[str, Any]:
        """
        Calculate time-related metrics for the execution log.

        Args:
            start_time: Start time of the workflow execution (from time.time())

        Returns:
            Dict[str, Any]: Time metrics including end time, duration, and formatted timestamps
        """
        # Define precision for duration rounding
        DURATION_PRECISION = 2

        # Calculate time metrics
        end_time = time.time()
        duration_seconds = end_time - start_time

        # Create and return time metrics dictionary
        return {
            "start_time": start_time,
            "end_time": end_time,
            "duration": round(duration_seconds, DURATION_PRECISION),
            "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
            "end_time_iso": datetime.fromtimestamp(end_time).isoformat()
        }

    def _create_log_structure(self,
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
        logger.info(f"Workflow '{workflow_name}' completed with status: {final_status}")
        if error_message:
            logger.error(f"Workflow error: {error_message}")

    def _determine_status(self,
                         action_results: List[ActionResult],
                         error: Optional[Exception]) -> Tuple[str, Optional[str], str]:
        """
        Determine the final status, error message, and summary of a workflow execution.

        Args:
            action_results: Results of the executed actions
            error: Optional exception that caused the workflow to fail

        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        if error:
            return self._determine_error_status(error)

        return self._determine_result_status(action_results)

    def _determine_error_status(self, error: Exception) -> Tuple[str, str, str]:
        """
        Determine the status when an error occurred during workflow execution.

        Args:
            error: The exception that caused the workflow to fail

        Returns:
            Tuple[str, str, str]: Final status, error message, and summary
        """
        # Check for user-requested stop
        if isinstance(error, WorkflowError) and "stopped by request" in str(error).lower():
            stop_message = "Execution stopped by user request."
            return "STOPPED", stop_message, stop_message

        # Handle action errors
        if isinstance(error, ActionError):
            return "FAILED", str(error), f"Failed during action '{error.action_name}': {error}"

        # Handle workflow errors
        if isinstance(error, WorkflowError):
            return "FAILED", str(error), f"Workflow error: {error}"

        # Handle unexpected errors
        error_message = f"Unexpected error: {error}"
        return "FAILED", error_message, error_message

    def _determine_result_status(
        self, action_results: List[ActionResult]
    ) -> Tuple[str, Optional[str], str]:
        """
        Determine the status based on action results when no error occurred.

        Args:
            action_results: Results of the executed actions

        Returns:
            Tuple[str, Optional[str], str]: Final status, error message, and summary
        """
        # Check if any actions failed
        if any(not result.is_success() for result in action_results):
            status = "COMPLETED_WITH_ERRORS"
            message = "Some actions failed"
            summary = "Completed with some actions failing"
            return status, message, summary

        # All actions succeeded
        return "SUCCESS", None, f"All {len(action_results)} actions completed successfully"

    def _format_action_results(self, action_results: List[ActionResult]) -> List[Dict[str, Any]]:
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
            safe_data = self._filter_sensitive_data(result.data)
            if safe_data:
                formatted_result["data"] = safe_data

        return formatted_result

    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out sensitive data from the result data.

        Args:
            data: The data to filter

        Returns:
            Dict[str, Any]: Filtered data
        """
        # Create a copy to avoid modifying the original
        filtered_data = data.copy()

        # Process each key in the data
        for key in list(filtered_data.keys()):
            if self._is_sensitive_key(key):
                filtered_data[key] = "********"  # Mask sensitive data
            elif isinstance(filtered_data[key], dict):
                # Recursively filter nested dictionaries
                filtered_data[key] = self._filter_sensitive_data(filtered_data[key])
            elif isinstance(filtered_data[key], list):
                # Filter lists that might contain dictionaries
                filtered_data[key] = self._filter_sensitive_list(filtered_data[key])

        return filtered_data

    def _is_sensitive_key(self, key: str) -> bool:
        """
        Determine if a key might contain sensitive information.

        Args:
            key: The key to check

        Returns:
            bool: True if the key might contain sensitive information
        """
        # List of words that might indicate sensitive information
        sensitive_words = ["password", "token", "secret", "key", "credential", "auth", "api_key"]

        return any(sensitive_word in key.lower() for sensitive_word in sensitive_words)

    def _filter_sensitive_list(self, data_list: List[Any]) -> List[Any]:
        """
        Filter sensitive data from a list of items.

        Args:
            data_list: The list to filter

        Returns:
            List[Any]: Filtered list
        """
        filtered_list = []

        for item in data_list:
            if isinstance(item, dict):
                # Recursively filter dictionaries in the list
                filtered_list.append(self._filter_sensitive_data(item))
            elif isinstance(item, list):
                # Recursively filter nested lists
                filtered_list.append(self._filter_sensitive_list(item))
            else:
                # Keep non-dictionary, non-list items as is
                filtered_list.append(item)

        return filtered_list
