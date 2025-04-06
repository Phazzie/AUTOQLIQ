"""Common validation utilities for the infrastructure layer."""

import re
from typing import Dict, Any, List, Optional

# Assuming specific exceptions are defined in core.exceptions
from src.core.exceptions import RepositoryError, CredentialError, ValidationError, WorkflowError

# Compiled regex for validating entity IDs/names (adjust pattern as needed)
# Example: Allow alphanumeric, underscore, hyphen, period. No spaces. Min length 1.
VALID_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+$')
# Example: Disallow leading/trailing whitespace and certain symbols like / \ : * ? " < > |
INVALID_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]|\s+$|^\s+') # Control chars, FS reserved, trailing/leading whitespace


class EntityValidator:
    """Validator for generic entity IDs."""

    @staticmethod
    def validate_entity_id(entity_id: Optional[str], entity_type: str = "Entity") -> None:
        """
        Validate a generic entity ID.

        Args:
            entity_id (Optional[str]): The ID string to validate.
            entity_type (str): The type of entity for clearer error messages (e.g., "Workflow", "Credential").

        Raises:
            ValidationError: If the entity ID is invalid (None, empty, wrong type, or contains invalid characters).
                             Changed from RepositoryError to ValidationError for semantic correctness.
        """
        if entity_id is None:
            raise ValidationError(f"{entity_type} ID cannot be None.")
        if not isinstance(entity_id, str):
            raise ValidationError(f"{entity_type} ID must be a string, got {type(entity_id).__name__}.")
        if not entity_id:
            raise ValidationError(f"{entity_type} ID cannot be empty.")

        # Check for generally invalid filesystem/URL characters or problematic whitespace
        if INVALID_CHARS_PATTERN.search(entity_id):
            raise ValidationError(
                f"{entity_type} ID '{entity_id}' contains invalid characters or leading/trailing whitespace.",
                field_name=f"{entity_type}_id"
            )

        # Optional: Enforce a stricter pattern if needed
        # if not VALID_ID_PATTERN.match(entity_id):
        #     raise ValidationError(
        #         f"{entity_type} ID '{entity_id}' does not match the required pattern.",
        #         field_name=f"{entity_type}_id"
        #     )


class CredentialValidator:
    """Validator specifically for credential dictionaries."""

    @staticmethod
    def validate_credential_data(credential_data: Optional[Dict[str, Any]]) -> None:
        """
        Validate the structure and content of a credential dictionary.

        Args:
            credential_data (Optional[Dict[str, Any]]): The credential dictionary to validate.

        Raises:
            CredentialError: If the credential data is invalid (None, not a dict, missing required fields, or empty fields).
                             Keeping CredentialError as it's more specific than ValidationError here.
        """
        if credential_data is None:
            raise CredentialError("Credential data cannot be None.")
        if not isinstance(credential_data, dict):
            raise CredentialError(f"Credential data must be a dictionary, got {type(credential_data).__name__}.")

        required_fields = ['name', 'username', 'password']
        credential_name = credential_data.get('name', '<unknown>') # For error context

        missing_fields = [field for field in required_fields if field not in credential_data]
        if missing_fields:
            raise CredentialError(f"Credential '{credential_name}' missing required field(s): {', '.join(missing_fields)}.", credential_name=credential_name)

        for field in required_fields:
            value = credential_data[field]
            if not isinstance(value, str):
                 raise CredentialError(f"Credential '{credential_name}' field '{field}' must be a string, got {type(value).__name__}.", credential_name=credential_name)
            if not value: # Disallow empty strings for required fields
                raise CredentialError(f"Credential '{credential_name}' field '{field}' cannot be empty.", credential_name=credential_name)

        # Additionally validate the 'name' field using EntityValidator rules
        try:
            # Use ValidationError from EntityValidator
            EntityValidator.validate_entity_id(credential_name, entity_type="Credential")
        except ValidationError as e:
            # Convert ValidationError back to CredentialError for consistency within this context
            raise CredentialError(str(e), credential_name=credential_name, cause=e) from e


class WorkflowValidator:
    """Validator specifically for workflow names and actions."""

    @staticmethod
    def validate_workflow_name(workflow_name: Optional[str]) -> None:
        """
        Validate a workflow name.

        Args:
            workflow_name (Optional[str]): The workflow name to validate.

        Raises:
            ValidationError: If the workflow name is invalid. Changed from WorkflowError.
        """
        try:
            EntityValidator.validate_entity_id(workflow_name, entity_type="Workflow")
        except ValidationError as e:
             raise # Re-raise ValidationError directly

    @staticmethod
    def validate_actions(actions: Optional[List[Any]]) -> None:
        """
        Validate a list of actions (basic structure and type check).

        Args:
            actions (Optional[List[Any]]): The list of actions to validate.

        Raises:
            ValidationError: If the actions list is invalid (not a list, contains non-IAction items).
        """
        # Assuming IAction is defined in core.interfaces
        from src.core.interfaces import IAction # Local import to avoid circular dependency issues

        if actions is None:
            # Allow empty list, but not None
            raise ValidationError("Workflow actions list cannot be None.")
        if not isinstance(actions, list):
            raise ValidationError(f"Workflow actions must be a list, got {type(actions).__name__}.")

        for i, action in enumerate(actions):
             if not isinstance(action, IAction):
                 raise ValidationError(f"Item at index {i} in actions list is not a valid IAction instance, got {type(action).__name__}.")
             # Defer detailed action validation to the action itself
             # try:
             #     if not action.validate():
             #         raise ValidationError(f"Action at index {i} ({getattr(action, 'name', 'Unnamed')}) failed validation.")
             # except Exception as e:
             #      raise ValidationError(f"Error validating action at index {i} ({getattr(action, 'name', 'Unnamed')}): {e}") from e


# Example Usage:
# try:
#     EntityValidator.validate_entity_id("my-valid_id.123")
#     CredentialValidator.validate_credential_data({"name": "test", "username": "user", "password": "pwd"})
#     WorkflowValidator.validate_workflow_name("My_Workflow-1")
# except ValidationError as e:
#     print(f"Validation failed: {e}")