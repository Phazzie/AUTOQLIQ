"""Error monitoring system for AutoQliq.

This module provides an error monitoring system for tracking errors and providing insights.
"""

import logging
import time
import os
import json
import threading
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from src.core.exceptions import (
    AutoQliqError, RepositoryError, WorkflowError, CredentialError,
    WebDriverError, ValidationError, UIError, ConfigError
)

logger = logging.getLogger(__name__)


class ErrorRecord:
    """Record of an error occurrence."""
    
    def __init__(
        self,
        error: Exception,
        context: str,
        timestamp: float = None,
        traceback_str: str = None
    ):
        """
        Initialize an error record.
        
        Args:
            error: The error that occurred
            context: The context in which the error occurred
            timestamp: The time the error occurred (default: current time)
            traceback_str: The traceback string (default: current traceback)
        """
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.context = context
        self.timestamp = timestamp or time.time()
        self.traceback_str = traceback_str or traceback.format_exc()
        
        # Extract additional information from AutoQliqError
        self.cause = None
        if isinstance(error, AutoQliqError) and error.cause:
            self.cause = {
                'type': type(error.cause).__name__,
                'message': str(error.cause)
            }
        
        # Extract specific error information
        self.details = {}
        if isinstance(error, WorkflowError):
            self.details.update({
                'workflow_name': error.workflow_name,
                'action_name': error.action_name,
                'action_type': error.action_type
            })
        elif isinstance(error, RepositoryError):
            self.details.update({
                'repository_name': error.repository_name,
                'entity_id': error.entity_id
            })
        elif isinstance(error, WebDriverError):
            self.details.update({
                'driver_type': error.driver_type
            })
        elif isinstance(error, ValidationError):
            self.details.update({
                'field_name': error.field_name
            })
        elif isinstance(error, UIError):
            self.details.update({
                'component_name': error.component_name
            })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error record to a dictionary.
        
        Returns:
            Dictionary representation of the error record
        """
        return {
            'error_type': self.error_type,
            'error_message': self.error_message,
            'context': self.context,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'traceback': self.traceback_str,
            'cause': self.cause,
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorRecord':
        """
        Create an error record from a dictionary.
        
        Args:
            data: Dictionary representation of an error record
            
        Returns:
            An ErrorRecord instance
        """
        # Create a dummy exception
        error = Exception(data['error_message'])
        error.__class__.__name__ = data['error_type']
        
        # Create the error record
        record = cls(
            error=error,
            context=data['context'],
            timestamp=data['timestamp'],
            traceback_str=data.get('traceback')
        )
        
        # Set additional fields
        record.cause = data.get('cause')
        record.details = data.get('details', {})
        
        return record


class ErrorMonitor:
    """Monitor for tracking errors and providing insights."""
    
    def __init__(
        self,
        max_records: int = 1000,
        error_log_file: str = "error_log.json",
        auto_save: bool = True
    ):
        """
        Initialize the error monitor.
        
        Args:
            max_records: Maximum number of error records to keep in memory
            error_log_file: File for persisting error records
            auto_save: Whether to automatically save error records to disk
        """
        self.max_records = max_records
        self.error_log_file = error_log_file
        self.auto_save = auto_save
        
        self.records: List[ErrorRecord] = []
        self.lock = threading.RLock()
        
        # Load existing records
        self._load_records()
    
    def record_error(
        self,
        error: Exception,
        context: str,
        traceback_str: Optional[str] = None
    ) -> None:
        """
        Record an error.
        
        Args:
            error: The error to record
            context: The context in which the error occurred
            traceback_str: The traceback string (default: current traceback)
        """
        with self.lock:
            # Create an error record
            record = ErrorRecord(
                error=error,
                context=context,
                traceback_str=traceback_str
            )
            
            # Add the record to the list
            self.records.append(record)
            
            # Trim the list if necessary
            if len(self.records) > self.max_records:
                self.records = self.records[-self.max_records:]
            
            # Save the records if auto-save is enabled
            if self.auto_save:
                self._save_records()
            
            # Log the error
            logger.debug(f"Recorded error: {record.error_type} in {context}")
    
    def get_recent_errors(
        self,
        count: int = 10,
        error_type: Optional[str] = None,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent error records.
        
        Args:
            count: Maximum number of records to return
            error_type: Filter by error type
            context: Filter by context
            
        Returns:
            List of error records as dictionaries
        """
        with self.lock:
            # Filter the records
            filtered_records = self.records
            
            if error_type:
                filtered_records = [r for r in filtered_records if r.error_type == error_type]
            
            if context:
                filtered_records = [r for r in filtered_records if context in r.context]
            
            # Sort by timestamp (newest first) and limit to count
            sorted_records = sorted(filtered_records, key=lambda r: r.timestamp, reverse=True)
            limited_records = sorted_records[:count]
            
            # Convert to dictionaries
            return [record.to_dict() for record in limited_records]
    
    def get_error_summary(
        self,
        days: int = 7,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Get a summary of errors.
        
        Args:
            days: Number of days to include in the summary
            include_details: Whether to include detailed error records
            
        Returns:
            Dictionary with error summary information
        """
        with self.lock:
            # Calculate the cutoff time
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            # Filter records by time
            recent_records = [r for r in self.records if r.timestamp >= cutoff_time]
            
            # Count errors by type
            error_counts = Counter(r.error_type for r in recent_records)
            
            # Count errors by context
            context_counts = Counter(r.context for r in recent_records)
            
            # Group errors by day
            errors_by_day = defaultdict(int)
            for record in recent_records:
                day = datetime.fromtimestamp(record.timestamp).strftime('%Y-%m-%d')
                errors_by_day[day] += 1
            
            # Create the summary
            summary = {
                'total_errors': len(recent_records),
                'unique_error_types': len(error_counts),
                'error_counts': dict(error_counts.most_common()),
                'context_counts': dict(context_counts.most_common(10)),
                'errors_by_day': dict(sorted(errors_by_day.items())),
                'period_days': days
            }
            
            # Include detailed records if requested
            if include_details:
                summary['records'] = [record.to_dict() for record in sorted(
                    recent_records,
                    key=lambda r: r.timestamp,
                    reverse=True
                )]
            
            return summary
    
    def clear_records(self) -> None:
        """Clear all error records."""
        with self.lock:
            self.records = []
            self._save_records()
            logger.info("Cleared all error records")
    
    def _load_records(self) -> None:
        """Load error records from disk."""
        try:
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r') as f:
                    data = json.load(f)
                    
                    # Convert dictionaries to ErrorRecord objects
                    self.records = [ErrorRecord.from_dict(record_data) for record_data in data]
                    
                    logger.info(f"Loaded {len(self.records)} error records from {self.error_log_file}")
        except Exception as e:
            logger.error(f"Failed to load error records: {e}")
            self.records = []
    
    def _save_records(self) -> None:
        """Save error records to disk."""
        try:
            # Convert records to dictionaries
            data = [record.to_dict() for record in self.records]
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.error_log_file)), exist_ok=True)
            
            # Save to disk
            with open(self.error_log_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.records)} error records to {self.error_log_file}")
        except Exception as e:
            logger.error(f"Failed to save error records: {e}")


class ErrorMonitoringMiddleware:
    """Middleware for monitoring errors in the application."""
    
    def __init__(self, error_monitor: ErrorMonitor):
        """
        Initialize the error monitoring middleware.
        
        Args:
            error_monitor: The error monitor to use
        """
        self.error_monitor = error_monitor
    
    def __call__(self, func):
        """
        Decorator for monitoring errors in a function.
        
        Args:
            func: The function to monitor
            
        Returns:
            Decorated function
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Record the error
                self.error_monitor.record_error(
                    error=e,
                    context=f"{func.__module__}.{func.__name__}"
                )
                
                # Re-raise the exception
                raise
        
        return wrapper


# Create a global instance of the error monitor
error_monitor = ErrorMonitor(
    error_log_file=os.path.join("logs", "error_log.json")
)


def monitor_errors(context: Optional[str] = None):
    """
    Decorator for monitoring errors in a function.
    
    Args:
        context: The context for the error (default: function name)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Record the error
                error_context = context or f"{func.__module__}.{func.__name__}"
                error_monitor.record_error(
                    error=e,
                    context=error_context
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator
