"""Action interface for AutoQliq.

This module defines the interface for action implementations that provide
workflow step capabilities.
"""
import abc
from typing import Dict, Any, Optional

# Assuming ActionResult and IWebDriver are defined elsewhere
# (Adjust import paths if necessary)
from src.core.action_result import ActionResult
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.repository import ICredentialRepository
# ActionError likely defined in core.exceptions
# from src.core.exceptions import ActionError


class IAction(abc.ABC):
    """Interface for action implementations.

    This interface defines the contract for actions that can be executed as part
    of a workflow. Actions represent discrete steps in a browser automation workflow,
    such as navigating to a URL, clicking a button, or typing text.

    Attributes:
        name (str): A descriptive name for the action instance.
        action_type (str): The type name of the action (e.g., "Navigate").
                           Should be defined as a class attribute in implementations.
    """
    name: str
    action_type: str

    @abc.abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None
    ) -> ActionResult:
        """Execute the action using the provided web driver.

        Args:
            driver: The web driver to use for execution.
            credential_repo: Optional credential repository needed by some actions.

        Returns:
            An ActionResult indicating success or failure.

        Raises:
            ActionError: If a configuration or execution error specific to the action occurs.
                         WebDriver exceptions should be caught and wrapped or handled internally.
            CredentialError: If credential access fails (if applicable).
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary representation.

        This dictionary should be serializable (e.g., to JSON) and contain
        all necessary information to reconstruct the action later using a factory.
        Must include a 'type' key matching the `action_type` attribute.

        Returns:
            A dictionary containing the action's type and parameters.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the action's configuration.

        Checks if the action has all necessary parameters set correctly.

        Returns:
            True if the action is configured correctly, False otherwise.

        Raises:
            ValidationError: If validation fails (optional, can also return False).
        """
        pass