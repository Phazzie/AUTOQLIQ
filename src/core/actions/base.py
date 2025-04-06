"""Base action module for AutoQliq.

This module provides the abstract base class for all action implementations,
ensuring they adhere to the IAction interface and provide common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# Assuming these interfaces and classes are defined elsewhere
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ActionBase(IAction, ABC):
    """
    Abstract base class for all actions in the system.

    Provides common structure and enforces the IAction interface.

    Attributes:
        name (str): A descriptive name for the action instance.
        action_type (str): The type name of the action (e.g., "Navigate").
                           Must be defined as a class attribute in subclasses.
    """
    action_type: str = "Base" # Must be overridden by subclasses

    def __init__(self, name: Optional[str] = None, **kwargs):
        """
        Initialize an ActionBase.

        Args:
            name (Optional[str]): A descriptive name for this specific action instance.
                                  If None, defaults to the action_type.
            **kwargs: Catches potential extra parameters from deserialization
                      but doesn't use them by default. Subclasses should handle
                      their specific parameters.
        """
        if not hasattr(self, 'action_type') or self.action_type == "Base":
             raise NotImplementedError(f"Subclass {self.__class__.__name__} must define 'action_type' class attribute.")

        default_name = self.action_type
        if name is None:
            self.name = default_name
        elif not isinstance(name, str) or not name:
            logger.warning(f"Invalid name '{name}' provided for {self.action_type} action. Defaulting to '{default_name}'.")
            self.name = default_name
        else:
            self.name = name

        if kwargs:
            logger.warning(f"Unused parameters provided for {self.action_type} action '{self.name}': {kwargs.keys()}")

        logger.debug(f"Initialized action: {self.action_type} (Name: {self.name})")

    def validate(self) -> bool:
        """
        Validate that the action has the required configuration.

        Base implementation always returns True. Subclasses should override
        this method to provide specific validation logic based on their parameters.
        It's recommended to raise ValidationError on failure for clarity,
        although returning False is also supported by the interface.

        Returns:
            bool: True if the action configuration is valid.

        Raises:
            ValidationError: If validation fails (recommended).
        """
        # Basic check: name should be a non-empty string
        if not isinstance(self.name, str) or not self.name:
             raise ValidationError("Action name must be a non-empty string.", field_name="name")
        return True

    @abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None
    ) -> ActionResult:
        """
        Execute the action using the provided web driver.

        Args:
            driver (IWebDriver): The web driver instance to perform browser operations.
            credential_repo (Optional[ICredentialRepository]): Repository for credentials,
                required by some actions like TypeAction. Defaults to None.

        Returns:
            ActionResult: An object indicating the outcome (success/failure) and details.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
            ActionError: For action-specific execution failures.
            CredentialError: For credential-related failures.
            WebDriverError: For driver-related failures during execution.
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the action instance to a dictionary representation.

        This dictionary should contain all necessary information to reconstruct
        the action instance later, typically including 'type', 'name', and
        action-specific parameters. The 'type' key MUST match the class's
        `action_type` attribute.

        Returns:
            Dict[str, Any]: A dictionary representing the action.

        Raises:
            NotImplementedError: If a subclass does not implement this method.
        """
        # Ensure base implementation includes type and name
        # Subclasses should call super().to_dict() and update the dictionary
        # Or implement their own, ensuring 'type' and 'name' are present
        return {"type": self.action_type, "name": self.name}


    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        # Collect subclass attributes for a more informative repr
        attrs = []
        for key, value in self.__dict__.items():
             if key != 'name' and not key.startswith('_'): # Exclude name (already shown) and private attrs
                 attrs.append(f"{key}={value!r}")
        attr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}(name='{self.name}'{', ' + attr_str if attr_str else ''})"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        # Subclasses might want to override this for better display in UI lists
        return f"{self.action_type}: {self.name}"