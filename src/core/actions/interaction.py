"""Interaction actions module for AutoQliq.

Contains actions that simulate user interactions with web elements,
such as clicking or typing.
"""

import logging
from typing import Dict, Any, Optional

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, CredentialError, ValidationError

logger = logging.getLogger(__name__)


class ClickAction(ActionBase):
    """
    Action to click on a web element identified by a CSS selector.

    Attributes:
        selector (str): The CSS selector to locate the element.
        action_type (str): The type name of the action ("Click").
    """
    action_type: str = "Click"

    def __init__(self, selector: str, name: Optional[str] = None, **kwargs):
        """
        Initialize a ClickAction.

        Args:
            selector (str): The CSS selector for the element to click.
            name (Optional[str]): A descriptive name for the action instance. Defaults to "Click".
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs) # Pass name and kwargs to base
        if not isinstance(selector, str) or not selector:
            # Raise validation error early
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        self.selector = selector
        logger.debug(f"ClickAction '{self.name}' initialized for selector: '{self.selector}'")

    def validate(self) -> bool:
        """Validate that the selector is a non-empty string."""
        super().validate() # Validate base properties like name
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None # Parameter included for interface consistency
    ) -> ActionResult:
        """
        Execute the click action using the web driver.

        Args:
            driver (IWebDriver): The web driver instance.
            credential_repo (Optional[ICredentialRepository]): Not used by this action.

        Returns:
            ActionResult: Result of the click operation.
        """
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate() # Ensure configuration is valid before execution
            driver.click_element(self.selector) # Assumes click_element raises WebDriverError on failure
            msg = f"Successfully clicked element with selector: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            # Catch validation errors or driver errors (like element not found/interactable)
            msg = f"Error clicking element '{self.selector}': {e}"
            logger.error(msg)
            # Return failure result, wrapping the original error message
            return ActionResult.failure(msg)
        except Exception as e:
            # Catch unexpected errors
            error = ActionError(f"Unexpected error clicking element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict() # Get 'type' and 'name'
        base_dict["selector"] = self.selector
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}')"


class TypeAction(ActionBase):
    """
    Action to type text into a web element identified by a CSS selector.

    Can optionally retrieve text from a credential repository.

    Attributes:
        selector (str): The CSS selector to locate the element.
        text (str): The text to type. Can contain placeholders like `credential:key`.
        value_type (str): Either 'text' (default) or 'credential'. Determines how `text` is interpreted.
        action_type (str): The type name of the action ("Type").
    """
    action_type: str = "Type"

    def __init__(self, selector: str, text: str, value_type: str = "text", name: Optional[str] = None, **kwargs):
        """
        Initialize a TypeAction.

        Args:
            selector (str): The CSS selector for the input element.
            text (str): The text value or the credential key (e.g., "my_login.username").
            value_type (str): How to interpret the 'text' field: 'text' or 'credential'. Defaults to 'text'.
            name (Optional[str]): A descriptive name for the action instance. Defaults to "Type".
             **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(text, str): # Allow empty string for text value
             raise ValidationError("Text/Key value must be a string.", field_name="text")
        if value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")

        self.selector = selector
        self.text = text # This holds either the literal text or the credential key
        self.value_type = value_type
        logger.debug(f"TypeAction '{self.name}' initialized for selector: '{self.selector}', type: {self.value_type}")

    def validate(self) -> bool:
        """Validate that selector, text, and value_type are set correctly."""
        super().validate()
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(self.text, str):
             raise ValidationError("Text/Key value must be a string.", field_name="text")
        if self.value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")
        if self.value_type == "credential" and not self.text:
             raise ValidationError("Credential key cannot be empty when value_type is 'credential'.", field_name="text")
        # Allow empty self.text if value_type is "text"
        return True

    def _resolve_text(self, credential_repo: Optional[ICredentialRepository]) -> str:
        """
        Resolve the text, potentially fetching from credential repository.

        Args:
            credential_repo: The credential repository instance.

        Returns:
            The resolved text to type.

        Raises:
            CredentialError: If credential type is used but repo is missing or key not found.
            ValidationError: If the credential key format is invalid.
        """
        if self.value_type == "text":
            return self.text
        elif self.value_type == "credential":
            if credential_repo is None:
                raise CredentialError(f"Credential repository is required for action '{self.name}' but was not provided.")

            # Expect key format "credential_name.field" (e.g., "my_login.username")
            key_parts = self.text.split('.', 1)
            if len(key_parts) != 2:
                raise ValidationError(f"Invalid credential key format '{self.text}'. Expected 'credential_name.field'.", field_name="text")
            credential_name, field_key = key_parts

            if not credential_name or not field_key:
                 raise ValidationError(f"Invalid credential key format '{self.text}'. Both name and field must be provided.", field_name="text")

            try:
                logger.debug(f"Resolving credential: name='{credential_name}'")
                credential_dict = credential_repo.get_by_name(credential_name)
                if credential_dict is None:
                    raise CredentialError(f"Credential '{credential_name}' not found.", credential_name=credential_name)

                if field_key not in credential_dict:
                     raise CredentialError(f"Field '{field_key}' not found in credential '{credential_name}'.", credential_name=credential_name)

                resolved_value = credential_dict[field_key]
                logger.debug(f"Resolved credential field '{field_key}' for '{credential_name}'.")
                return resolved_value
            except CredentialError:
                 raise # Re-raise credential errors directly
            except Exception as e:
                 # Wrap other repo errors
                 raise CredentialError(f"Failed to retrieve credential '{credential_name}': {e}", credential_name=credential_name, cause=e) from e
        else:
             # Should be caught by __init__/validate, but defensively handle
             raise ActionError(f"Unsupported value_type '{self.value_type}' in action '{self.name}'.")


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None
    ) -> ActionResult:
        """
        Execute the type action using the web driver.

        Args:
            driver (IWebDriver): The web driver instance.
            credential_repo (Optional[ICredentialRepository]): Repository for credentials.

        Returns:
            ActionResult: Result of the type operation.
        """
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate() # Ensure configuration is valid
            text_to_type = self._resolve_text(credential_repo) # Raises CredentialError/ValidationError
            # Log text length instead of potentially sensitive text
            logger.debug(f"Typing text of length {len(text_to_type)} into '{self.selector}'")
            driver.type_text(self.selector, text_to_type) # Assumes type_text raises WebDriverError
            msg = f"Successfully typed text into element: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, CredentialError, WebDriverError) as e:
            # Handle known errors related to config, credentials, or driver
            msg = f"Error typing into element '{self.selector}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            # Handle unexpected errors
            error = ActionError(f"Unexpected error typing into element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["selector"] = self.selector
        base_dict["text"] = self.text
        base_dict["value_type"] = self.value_type
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        # Avoid logging potentially sensitive text in repr, show type instead
        value_repr = f"'{self.text}'" if self.value_type == 'text' else f"credential:'{self.text}'"
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}', value={value_repr})"