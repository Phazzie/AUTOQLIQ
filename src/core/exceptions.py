from typing import Optional


class AutoQliqError(Exception):
    """
    Base exception for all AutoQliq-specific errors.

    This serves as the parent class for all custom exceptions in the application,
    providing a consistent way to handle errors and add context information.

    Attributes:
        message: The error message
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize an AutoQliqError.

        Args:
            message: The error message
            cause: The original exception that caused this error, if any
        """
        self.message = message
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """
        Format the error message, including cause information if available.

        Returns:
            The formatted error message
        """
        if self.cause is None:
            return self.message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{self.message} (caused by: {cause_str})"


class WorkflowError(AutoQliqError):
    """
    Raised when there is an error in workflow execution.

    Attributes:
        message: The error message
        workflow_name: The name of the workflow that encountered the error
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, workflow_name: Optional[str] = None, cause: Optional[Exception] = None):
        """
        Initialize a WorkflowError.

        Args:
            message: The error message
            workflow_name: The name of the workflow that encountered the error
            cause: The original exception that caused this error, if any
        """
        self.workflow_name = workflow_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        """
        Format the error message, including workflow name and cause information if available.

        Returns:
            The formatted error message
        """
        base_message = self.message

        if self.workflow_name is not None:
            base_message = f"{base_message} (workflow: {self.workflow_name})"

        if self.cause is None:
            return base_message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{base_message} (caused by: {cause_str})"


class ActionError(AutoQliqError):
    """
    Raised when there is an error in action execution.

    Attributes:
        message: The error message
        action_name: The name of the action that encountered the error
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, action_name: Optional[str] = None, cause: Optional[Exception] = None):
        """
        Initialize an ActionError.

        Args:
            message: The error message
            action_name: The name of the action that encountered the error
            cause: The original exception that caused this error, if any
        """
        self.action_name = action_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        """
        Format the error message, including action name and cause information if available.

        Returns:
            The formatted error message
        """
        base_message = self.message

        if self.action_name is not None:
            base_message = f"{base_message} (action: {self.action_name})"

        if self.cause is None:
            return base_message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{base_message} (caused by: {cause_str})"


class ValidationError(AutoQliqError):
    """
    Raised when validation fails for an entity or input.

    Attributes:
        message: The error message
        field_name: The name of the field that failed validation
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, field_name: Optional[str] = None, cause: Optional[Exception] = None):
        """
        Initialize a ValidationError.

        Args:
            message: The error message
            field_name: The name of the field that failed validation
            cause: The original exception that caused this error, if any
        """
        self.field_name = field_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        """
        Format the error message, including field name and cause information if available.

        Returns:
            The formatted error message
        """
        base_message = self.message

        if self.field_name is not None:
            base_message = f"{base_message} (field: {self.field_name})"

        if self.cause is None:
            return base_message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{base_message} (caused by: {cause_str})"


class CredentialError(AutoQliqError):
    """
    Raised when there is an error related to credentials.

    Attributes:
        message: The error message
        credential_name: The name of the credential that encountered the error
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, credential_name: Optional[str] = None, cause: Optional[Exception] = None):
        """
        Initialize a CredentialError.

        Args:
            message: The error message
            credential_name: The name of the credential that encountered the error
            cause: The original exception that caused this error, if any
        """
        self.credential_name = credential_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        """
        Format the error message, including credential name and cause information if available.

        Returns:
            The formatted error message
        """
        base_message = self.message

        if self.credential_name is not None:
            base_message = f"{base_message} (credential: {self.credential_name})"

        if self.cause is None:
            return base_message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{base_message} (caused by: {cause_str})"


class WebDriverError(AutoQliqError):
    """
    Raised when there is an error related to the web driver.

    Attributes:
        message: The error message
        driver_type: The type of web driver that encountered the error
        cause: The original exception that caused this error, if any
    """

    def __init__(self, message: str, driver_type: Optional[str] = None, cause: Optional[Exception] = None):
        """
        Initialize a WebDriverError.

        Args:
            message: The error message
            driver_type: The type of web driver that encountered the error
            cause: The original exception that caused this error, if any
        """
        self.driver_type = driver_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        """
        Format the error message, including driver type and cause information if available.

        Returns:
            The formatted error message
        """
        base_message = self.message

        if self.driver_type is not None:
            base_message = f"{base_message} (driver: {self.driver_type})"

        if self.cause is None:
            return base_message

        cause_str = f"{type(self.cause).__name__} - {str(self.cause)}"
        return f"{base_message} (caused by: {cause_str})"


# For backward compatibility
class LoginFailedError(ActionError):
    """
    Raised when login fails due to incorrect credentials or other issues.

    This is a specialized ActionError for login failures.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize a LoginFailedError.

        Args:
            message: The error message
            cause: The original exception that caused this error, if any
        """
        super().__init__(message, action_name="Login", cause=cause)
