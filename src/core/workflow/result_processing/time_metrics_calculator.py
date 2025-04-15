"""Time metrics calculator for workflow execution.

This module provides the TimeMetricsCalculator class for calculating time-related metrics.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TimeMetricsCalculator:
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
