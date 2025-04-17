"""Time metrics calculator for workflow execution.

This module provides the TimeMetricsCalculator class for calculating time-related metrics.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any

from src.core.workflow.result_processing.interfaces import ITimeMetricsCalculator

logger = logging.getLogger(__name__)


class TimeMetricsCalculator(ITimeMetricsCalculator):
    """
    Calculates time-related metrics for workflow execution.

    Responsible for calculating execution time, duration, and formatted timestamps.
    """

    def calculate_time_metrics(self, start_time: float) -> Dict[str, Any]:
        """
        Calculate time-related metrics for the execution log.

        Args:
            start_time: Start time of the workflow execution (from time.time())

        Returns:
            Dict[str, Any]: Time metrics including end time, duration, and formatted timestamps
        """
        DURATION_PRECISION = 2

        end_time = self._get_current_time()
        duration_seconds = self._calculate_duration(start_time, end_time)

        return self._create_time_metrics_dict(start_time, end_time, duration_seconds, DURATION_PRECISION)

    def _get_current_time(self) -> float:
        """
        Get the current time.

        Returns:
            float: Current time (from time.time())
        """
        return time.time()

    def _calculate_duration(self, start_time: float, end_time: float) -> float:
        """
        Calculate the duration between start and end times.

        Args:
            start_time: Start time of the workflow execution
            end_time: End time of the workflow execution

        Returns:
            float: Duration in seconds
        """
        return end_time - start_time

    def _create_time_metrics_dict(self, start_time: float, end_time: float, duration_seconds: float, precision: int) -> Dict[str, Any]:
        """
        Create a dictionary with time metrics.

        Args:
            start_time: Start time of the workflow execution
            end_time: End time of the workflow execution
            duration_seconds: Duration in seconds
            precision: Precision for rounding the duration

        Returns:
            Dict[str, Any]: Time metrics dictionary
        """
        return {
            "start_time": start_time,
            "end_time": end_time,
            "duration": round(duration_seconds, precision),
            "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
            "end_time_iso": datetime.fromtimestamp(end_time).isoformat()
        }
