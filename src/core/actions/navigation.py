"""Navigation actions module for AutoQliq.

Contains actions related to browser navigation, such as going to a URL.
"""

import logging
from typing import Dict, Any, Optional
import re

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, ValidationError

logger = logging.getLogger(__name__)

# Basic URL pattern check (simplified)
URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)


class NavigateAction(ActionBase):
    """
    Action to navigate the browser to a specified URL.

    Attributes:
        url (str): The URL to navigate to.
        action_type (str): The type name of the action ("Navigate").
    """
    action_type: str = "Navigate"

    def __init__(self, url: str, name: Optional[str] = None, **kwargs):
        """
        Initialize a NavigateAction.

        Args:
            url (str): The URL to navigate to. Must start with http or https.
            name (Optional[str]): A descriptive name for the action instance. Defaults to "Navigate".
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(url, str) or not url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(url):
             logger.warning(f"URL '{url}' may not be valid for NavigateAction '{self.name}'.")
             # Decide whether to raise ValidationError or just warn
             # Raising might be too strict, warning allows flexibility
             # raise ValidationError(f"URL '{url}' does not appear to be a valid http/https URL.", field_name="url")
        self.url = url
        logger.debug(f"NavigateAction '{self.name}' initialized for URL: '{self.url}'")

    def validate(self) -> bool:
        """Validate that the URL is a non-empty string and looks like a URL."""
        super().validate()
        if not isinstance(self.url, str) or not self.url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(self.url):
             # Be stricter in validation than in init? Or consistent? Consistent warning is likely better.
             logger.warning(f"URL '{self.url}' may not be valid during validation.")
             # raise ValidationError(f"URL '{self.url}' does not appear to be a valid http/https URL.", field_name="url")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None # Parameter included for interface consistency
    ) -> ActionResult:
        """
        Execute the navigation action using the web driver.

        Args:
            driver (IWebDriver): The web driver instance.
            credential_repo (Optional[ICredentialRepository]): Not used by this action.

        Returns:
            ActionResult: Result of the navigation operation.
        """
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) to URL: '{self.url}'")
        try:
            self.validate() # Ensure configuration is valid before execution
            driver.get(self.url) # Assumes driver.get raises WebDriverError on failure
            msg = f"Successfully navigated to URL: {self.url}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            # Catch validation or driver errors
            msg = f"Error navigating to '{self.url}': {e}"
            logger.error(msg)
            # Return failure result, wrapping the original error message
            return ActionResult.failure(msg)
        except Exception as e:
            # Catch unexpected errors
            error = ActionError(f"Unexpected error navigating to '{self.url}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict() # Get 'type' and 'name'
        base_dict["url"] = self.url
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', url='{self.url}')"