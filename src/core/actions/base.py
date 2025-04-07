"""Base action module for AutoQliq.

This module provides the abstract base class for all action implementations,
ensuring they adhere to the IAction interface and provide common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

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
        elif not isinstance(name, str) or not name.strip(): # Check for non-empty stripped name
            logger.warning(f"Invalid or empty name '{name}' provided for {self.action_type} action. Defaulting to '{default_name}'.")
            self.name = default_name
        else:
            self.name = name.strip() # Store stripped name

        # Store unused kwargs for potential future use or debugging, but warn
        self._unused_kwargs = kwargs
        if kwargs:
            logger.warning(f"Unused parameters provided for {self.action_type} action '{self.name}': {list(kwargs.keys())}")

        logger.debug(f"Initialized action: {self.action_type} (Name: {self.name})")

    def validate(self) -> bool:
        """
        Validate that the action has the required configuration.

        Base implementation validates the 'name' attribute. Subclasses should
        call `super().validate()` and then add their specific parameter checks.

        Returns:
            bool: True if the action configuration is valid.

        Raises:
            ValidationError: If validation fails (recommended).
        """
        if not isinstance(self.name, str) or not self.name:
             raise ValidationError("Action name must be a non-empty string.", field_name="name")
        return True

    @abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Context added
    ) -> ActionResult:
        """
        Execute the action using the provided web driver and context.

        Args:
            driver (IWebDriver): The web driver instance to perform browser operations.
            credential_repo (Optional[ICredentialRepository]): Repository for credentials.
            context (Optional[Dict[str, Any]]): Dictionary holding execution context
                                                 (e.g., loop variables). Defaults to None.

        Returns:
            ActionResult: An object indicating the outcome (success/failure) and details.
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the action instance to a dictionary representation.

        Must include 'type' and 'name' keys. Subclasses must add their parameters.

        Returns:
            Dict[str, Any]: A dictionary representing the action.
        """
        # Ensure base implementation includes type and name
        return {"type": self.action_type, "name": self.name}

    def get_nested_actions(self) -> List['IAction']:
        """Return any nested actions contained within this action."""
        return []

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        attrs = []
        for key, value in self.__dict__.items():
             if key == 'name' or key.startswith('_'): continue
             if isinstance(value, list) and key.endswith("_actions"):
                 repr_val = f"[{len(value)} actions]"
             else:
                 try:
                      repr_val = repr(value); max_len=50
                      if len(repr_val) > max_len: repr_val = repr_val[:max_len-3] + "..."
                 except Exception: repr_val = "<repr error>"
             attrs.append(f"{key}={repr_val}")
        attr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}(name='{self.name}'{', ' + attr_str if attr_str else ''})"

    def __str__(self) -> str:
        """Return a user-friendly string representation for UI display."""
        return f"{self.action_type}: {self.name}"