"""Action result module for AutoQliq.

This module provides the ActionResult class for representing the outcome of action executions.
"""

import logging
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
    """

    def __init__(
        self,
        status: ActionStatus,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an ActionResult.

        Args:
            status: The status of the action execution
            message: An optional message providing details about the result
            data: Optional additional data related to the result
        """
        if not isinstance(status, ActionStatus):
            # Log error before raising
            logger.error(f"Invalid status type provided to ActionResult: {type(status).__name__}")
            raise TypeError("status must be an instance of ActionStatus Enum")
        self.status = status
        self.message = message
        self.data = data or {}
        # Log creation, mask sensitive data if necessary in the future
        logger.info(f"ActionResult created: Status={self.status.name}, Message='{self.message}'")

    def is_success(self) -> bool:
        """
        Check if the result represents a successful execution.

        Returns:
            True if the status is SUCCESS, False otherwise
        """
        return self.status == ActionStatus.SUCCESS

    @classmethod
    def success(cls, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> 'ActionResult':
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
    def failure(cls, message: str = "Action failed", data: Optional[Dict[str, Any]] = None) -> 'ActionResult':
        """
        Create a failure result.

        Args:
            message: A message providing details about the failure
            data: Optional additional data related to the failure

        Returns:
            An ActionResult with FAILURE status
        """
        # Logging happens in __init__
        return cls(ActionStatus.FAILURE, message, data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ActionResult to a dictionary.

        Returns:
            A dictionary representation of the ActionResult
        """
        # Kept for now, might move to serializer later
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionResult':
        """
        Create an ActionResult from a dictionary.

        Args:
            data: A dictionary containing the ActionResult data

        Returns:
            An ActionResult instance
        """
        # Kept for now, might move later
        status_value = data.get("status")
        try:
            status = ActionStatus(status_value) if status_value else ActionStatus.FAILURE
        except ValueError:
            logger.error(f"Invalid status value '{status_value}' encountered in from_dict. Defaulting to FAILURE.")
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
        if self.message:
            return f"{status_str}: {self.message}"
        return status_str

    def __repr__(self) -> str:
        """
        Get a developer-friendly string representation of the result.

        Returns:
            A string representation of the result instance.
        """
        return f"ActionResult(status={self.status}, message='{self.message}', data={self.data})"
