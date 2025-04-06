from enum import Enum
from typing import Optional


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
    """

    def __init__(self, status: ActionStatus, message: Optional[str] = None):
        """
        Initialize an ActionResult.

        Args:
            status: The status of the action execution
            message: An optional message providing details about the result
        """
        if not isinstance(status, ActionStatus):
            raise TypeError("status must be an instance of ActionStatus Enum")
        self.status = status
        self.message = message

    def is_success(self) -> bool:
        """
        Check if the result represents a successful execution.

        Returns:
            True if the status is SUCCESS, False otherwise
        """
        return self.status == ActionStatus.SUCCESS

    @classmethod
    def success(cls, message: Optional[str] = None) -> 'ActionResult':
        """
        Create a success result.

        Args:
            message: An optional message providing details about the result

        Returns:
            An ActionResult with SUCCESS status
        """
        return cls(ActionStatus.SUCCESS, message)

    @classmethod
    def failure(cls, message: str = "Action failed") -> 'ActionResult':
        """
        Create a failure result.

        Args:
            message: A message providing details about the failure

        Returns:
            An ActionResult with FAILURE status
        """
        return cls(ActionStatus.FAILURE, message)

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
        return f"ActionResult(status={self.status}, message='{self.message}')"