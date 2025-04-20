"""Custom exceptions for the AutoQliq application."""

from typing import Optional


class AutoQliqError(Exception):
    """Base exception for all AutoQliq-specific errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.message = message
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.cause:
            # Ensure cause message is included, especially for wrapped standard exceptions
            cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
            return f"{self.message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return self.message

    def __str__(self) -> str:
        return self._format_message()

    def __repr__(self) -> str:
        cause_repr = f", cause={self.cause!r}" if self.cause else ""
        return f"{self.__class__.__name__}(message={self.message!r}{cause_repr})"


class ConfigError(AutoQliqError):
    """Raised for configuration-related errors."""
    pass


class WorkflowError(AutoQliqError):
    """Raised for errors during workflow definition or execution."""
    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        action_name: Optional[str] = None,
        action_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.workflow_name = workflow_name
        self.action_name = action_name
        self.action_type = action_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.workflow_name: context.append(f"workflow='{self.workflow_name}'")
        if self.action_name: context.append(f"action='{self.action_name}'")
        if self.action_type: context.append(f"type='{self.action_type}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class ActionError(AutoQliqError):
    """Raised for errors during the execution or configuration of a specific action."""
    def __init__(
        self,
        message: str,
        action_name: Optional[str] = None,
        action_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.action_name = action_name
        self.action_type = action_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.action_name: context.append(f"action='{self.action_name}'")
        if self.action_type: context.append(f"type='{self.action_type}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class WebDriverError(AutoQliqError):
    """Raised for errors related to WebDriver operations."""
    def __init__(
        self,
        message: str,
        driver_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.driver_type = driver_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (driver: {self.driver_type})" if self.driver_type else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class RepositoryError(AutoQliqError):
    """Raised for errors related to repository operations (persistence)."""
    def __init__(
        self,
        message: str,
        repository_name: Optional[str] = None,
        entity_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.repository_name = repository_name
        self.entity_id = entity_id
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.repository_name: context.append(f"repository='{self.repository_name}'")
        if self.entity_id: context.append(f"id='{self.entity_id}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class CredentialError(RepositoryError):
    """Raised specifically for errors related to credential storage or retrieval."""
    def __init__(
        self,
        message: str,
        credential_name: Optional[str] = None, # Specific alias for entity_id
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message,
            repository_name="CredentialRepository",
            entity_id=credential_name,
            cause=cause
        )
        self.credential_name = credential_name # Keep specific attribute if needed


class SerializationError(AutoQliqError):
    """Raised for errors during serialization or deserialization."""
    pass


class ValidationError(AutoQliqError):
    """Raised when data validation fails."""
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.field_name = field_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (field: {self.field_name})" if self.field_name else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class UIError(AutoQliqError):
    """Raised for errors originating from the UI layer."""
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.component_name = component_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (component: {self.component_name})" if self.component_name else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message