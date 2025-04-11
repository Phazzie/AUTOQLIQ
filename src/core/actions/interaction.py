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
    """
    action_type: str = "Click"

    def __init__(self, selector: str, name: Optional[str] = None, **kwargs):
        """Initialize a ClickAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        self.selector = selector
        logger.debug(f"ClickAction '{self.name}' initialized for selector: '{self.selector}'")

    def validate(self) -> bool:
        """Validate that the selector is a non-empty string."""
        super().validate()
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the click action using the web driver."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate()
            driver.click_element(self.selector) # Raises WebDriverError on failure
            msg = f"Successfully clicked element with selector: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            msg = f"Error clicking element '{self.selector}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error clicking element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["selector"] = self.selector
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}')"


class TypeAction(ActionBase):
    """
    Action to type text into a web element identified by a CSS selector.
    Uses `value_type` ('text' or 'credential') and `value_key` (the literal
    text or the credential key like 'login.username') to determine the source
    of the text.
    """
    action_type: str = "Type"

    def __init__(self, selector: str, value_key: str, value_type: str, name: Optional[str] = None, **kwargs):
        """Initialize a TypeAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(value_key, str): # Allow empty string for text value
             raise ValidationError("Value key must be a string.", field_name="value_key")
        if value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")
        if value_type == "credential" and not value_key:
             raise ValidationError("Credential key cannot be empty when value_type is 'credential'.", field_name="value_key")

        self.selector = selector
        self.value_key = value_key
        self.value_type = value_type
        logger.debug(f"TypeAction '{self.name}' initialized for selector: '{self.selector}', type: {self.value_type}")

    def validate(self) -> bool:
        """Validate that selector, value_key, and value_type are set correctly."""
        super().validate()
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(self.value_key, str):
             raise ValidationError("Value key must be a string.", field_name="value_key")
        if self.value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")
        if self.value_type == "credential":
            if not self.value_key:
                raise ValidationError("Credential key cannot be empty.", field_name="value_key")
            if '.' not in self.value_key:
                raise ValidationError("Credential key format should be 'credential_name.field'.", field_name="value_key")
        return True

    def _resolve_text(self, credential_repo: Optional[ICredentialRepository]) -> str:
        """Resolve the text to be typed."""
        if self.value_type == "text":
            return self.value_key
        elif self.value_type == "credential":
            if credential_repo is None:
                raise CredentialError(f"Credential repo needed for action '{self.name}'.")

            key_parts = self.value_key.split('.', 1)
            if len(key_parts) != 2: raise ValidationError(f"Invalid credential key format '{self.value_key}'.", field_name="value_key")
            credential_name, field_key = key_parts
            if not credential_name or not field_key: raise ValidationError(f"Invalid credential key format '{self.value_key}'.", field_name="value_key")

            try:
                credential_dict = credential_repo.get_by_name(credential_name) # Raises ValidationError on bad name format
                if credential_dict is None: raise CredentialError(f"Credential '{credential_name}' not found.", credential_name=credential_name)
                if field_key not in credential_dict: raise CredentialError(f"Field '{field_key}' not found in credential '{credential_name}'.", credential_name=credential_name)
                resolved_value = credential_dict[field_key]
                logger.debug(f"Resolved credential field '{field_key}' for '{credential_name}'.")
                return str(resolved_value) if resolved_value is not None else ""
            except ValidationError as e: raise CredentialError(f"Invalid credential name format '{credential_name}': {e}", credential_name=credential_name, cause=e) from e
            except CredentialError: raise
            except Exception as e: raise CredentialError(f"Failed to retrieve credential '{credential_name}': {e}", credential_name=credential_name, cause=e) from e
        else:
             raise ActionError(f"Unsupported value_type '{self.value_type}' in action '{self.name}'.")


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the type action using the web driver."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate()
            # Pass the specific credential repo instance needed for resolution
            text_to_type = self._resolve_text(credential_repo) # Raises CredentialError/ValidationError
            logger.debug(f"Typing text (length {len(text_to_type)}) into '{self.selector}'")
            driver.type_text(self.selector, text_to_type) # Raises WebDriverError
            msg = f"Successfully typed text into element: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, CredentialError, WebDriverError) as e:
            msg = f"Error typing into element '{self.selector}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error typing into element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["selector"] = self.selector
        base_dict["value_key"] = self.value_key
        base_dict["value_type"] = self.value_type
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        value_repr = f"text:'{self.value_key}'" if self.value_type == 'text' else f"credential:'{self.value_key}'"
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}', {value_repr})"
