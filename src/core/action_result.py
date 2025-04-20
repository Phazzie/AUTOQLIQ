"""Action result module for AutoQliq.

This module provides the ActionResult class for representing the outcome of action executions.
"""

import logging
import traceback
from enum import Enum
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ActionStatus(Enum):
    """
    Enum representing the status of an action execution.
    """
    SUCCESS = "success"
    FAILURE = "failure"


class ActionResult:
    """
    Represents the result of an action execution.

    Attributes:
        status: The status of the action execution (SUCCESS or FAILURE)
        message: An optional message providing details about the result
        data: Optional additional data related to the result
        cause: Optional exception that caused a failure (only for FAILURE status)
    """

    def __init__(
        self,
        status: ActionStatus,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize an ActionResult.

        Args:
            status: The status of the action execution
            message: An optional message providing details about the result
            data: Optional additional data related to the result
            cause: Optional exception that caused the failure (only for FAILURE status)
        """
        if not isinstance(status, ActionStatus):
            # Log error before raising
            logger.error(f"Invalid status type provided to ActionResult: {type(status).__name__}")
            raise TypeError("status must be an instance of ActionStatus Enum")
        
        self.status = status
        self.message = message
        self.data = data or {}
        self.cause = cause
        
        # If cause is provided but status is SUCCESS, log a warning
        if self.cause and self.status == ActionStatus.SUCCESS:
            logger.warning("Exception cause provided for a SUCCESS result, which is unusual.")
        
        # Add exception details to data if cause is provided
        if self.cause:
            self.data["exception"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause),
                "traceback": traceback.format_exception(type(self.cause), self.cause, self.cause.__traceback__)
            }

        # Log creation with masked sensitive data
        log_data = self._filter_sensitive_data(self.data.copy()) if self.data else {}
        log_level = logging.INFO if self.is_success() else logging.ERROR
        
        logger.log(
            log_level,
            f"ActionResult created: Status={self.status.name}, "
            f"Message='{self.message}', Data={log_data}"
        )

    def is_success(self) -> bool:
        """
        Check if the result represents a successful execution.

        Returns:
            True if the status is SUCCESS, False otherwise
        """
        return self.status == ActionStatus.SUCCESS

    @classmethod
    def success(
        cls,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> 'ActionResult':
        """
        Create a success result.

        Args:
            message: An optional message providing details about the result
            data: Optional additional data related to the result

        Returns:
            An ActionResult with SUCCESS status
        """
        # Logging happens in __init__
        return cls(ActionStatus.SUCCESS, message, data)

    @classmethod
    def failure(
        cls,
        message: str = "Action failed",
        data: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> 'ActionResult':
        """
        Create a failure result.

        Args:
            message: A message providing details about the failure
            data: Optional additional data related to the failure
            cause: Optional exception that caused the failure

        Returns:
            An ActionResult with FAILURE status
        """
        # Logging happens in __init__
        return cls(ActionStatus.FAILURE, message, data, cause)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ActionResult to a dictionary.

        Returns:
            A dictionary representation of the ActionResult
        """
        result = {
            "status": self.status.value,
            "message": self.message,
            "data": self.data
        }
        
        # Include exception type if available
        if self.cause:
            result["exception_type"] = type(self.cause).__name__
        
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionResult':
        """
        Create an ActionResult from a dictionary.

        Args:
            data: A dictionary containing the ActionResult data

        Returns:
            An ActionResult instance
        """
        status_value = data.get("status")
        try:
            status = ActionStatus(status_value) if status_value else ActionStatus.FAILURE
        except ValueError:
            logger.error(
                f"Invalid status value '{status_value}' encountered in from_dict. "
                f"Defaulting to FAILURE."
            )
            status = ActionStatus.FAILURE

        return cls(
            status=status,
            message=data.get("message"),
            data=data.get("data", {})
        )

    def __str__(self) -> str:
        """
        Get a string representation of the result.

        Returns:
            A string representation of the result
        """
        status_str = "Success" if self.is_success() else "Failure"
        cause_str = f" (Caused by: {type(self.cause).__name__})" if self.cause else ""
        
        if self.message:
            return f"{status_str}{cause_str}: {self.message}"
        return f"{status_str}{cause_str}"

    def __repr__(self) -> str:
        """
        Get a developer-friendly string representation of the result.

        Returns:
            A string representation of the result instance with masked sensitive data.
        """
        # Mask sensitive data in the representation
        safe_data = self._filter_sensitive_data(self.data.copy()) if self.data else {}
        cause_repr = f", cause={type(self.cause).__name__}" if self.cause else ""
        return f"ActionResult(status={self.status}, message='{self.message}', data={safe_data}{cause_repr})"

    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out sensitive data from the result data.

        Args:
            data: The data to filter

        Returns:
            Dict[str, Any]: Filtered data
        """
        # List of keys that might contain sensitive information
        sensitive_keys = ["password", "token", "secret", "key", "credential", "auth"]

        # Remove or mask sensitive data
        for key in list(data.keys()):
            if any(sensitive_word in key.lower() for sensitive_word in sensitive_keys):
                data[key] = "********"  # Mask sensitive data
            elif isinstance(data[key], dict):
                # Recursively filter nested dictionaries
                data[key] = self._filter_sensitive_data(data[key])

        return data
