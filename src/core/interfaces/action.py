################################################################################
"""Action interface for AutoQliq.

This module defines the interface for action implementations that provide
workflow step capabilities.
"""
import abc
from typing import Dict, Any, Optional, List

# Assuming ActionResult and IWebDriver are defined elsewhere
from src.core.action_result import ActionResult
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.repository import ICredentialRepository
# ActionError likely defined in core.exceptions
# from src.core.exceptions import ActionError


class IAction(abc.ABC):
    """Interface for action implementations.

    Defines the contract for executable steps within a workflow.

    Attributes:
        name (str): A user-defined name for this specific action instance.
        action_type (str): The identifier for the action type (e.g., "Navigate", "Loop").
                           Must be defined as a class attribute in implementations.
    """
    name: str
    action_type: str

    @abc.abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Context added
    ) -> ActionResult:
        """Execute the action using the provided web driver and context.

        Args:
            driver: The web driver instance.
            credential_repo: Optional credential repository.
            context: Optional dictionary holding execution context (e.g., loop variables).

        Returns:
            An ActionResult indicating success or failure.

        Raises:
            ActionError: For action-specific execution failures.
            CredentialError: For credential-related failures.
            WebDriverError: For driver-related failures.
            ValidationError: If context needed is missing/invalid.
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary representation.

        Must include 'type' and 'name' keys, plus action-specific parameters.
        Nested actions (like in Loop or Conditional) should also be serialized.

        Returns:
            A dictionary representation of the action.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the action's configuration parameters.

        Checks if required parameters are present and have valid types/formats.
        Should also validate nested actions if applicable (e.g., Loop, Conditional).

        Returns:
            True if the action is configured correctly.

        Raises:
            ValidationError: If validation fails (recommended approach).
        """
        pass

    # Optional: Method to get nested actions, useful for editors/validation
    def get_nested_actions(self) -> List['IAction']:
        """Return any nested actions contained within this action."""
        return [] # Default implementation for actions that don't contain others


################################################################################