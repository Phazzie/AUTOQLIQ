"""Navigation actions module for AutoQliq."""

import logging
from typing import Dict, Any, Optional
import re

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, ValidationError

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

class NavigateAction(ActionBase):
    """Action to navigate the browser to a specified URL."""
    action_type: str = "Navigate"

    def __init__(self, url: str, name: Optional[str] = None, **kwargs):
        """Initialize a NavigateAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(url, str) or not url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(url):
             logger.warning(f"URL '{url}' may not be valid for NavigateAction '{self.name}'.")
        self.url = url
        logger.debug(f"NavigateAction '{self.name}' initialized for URL: '{self.url}'")

    def validate(self) -> bool:
        """Validate the URL."""
        super().validate()
        if not isinstance(self.url, str) or not self.url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(self.url):
             logger.warning(f"URL '{self.url}' may not be valid during validation.")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the navigation action."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) to URL: '{self.url}'")
        try:
            self.validate()
            driver.get(self.url) # Raises WebDriverError on failure
            msg = f"Successfully navigated to URL: {self.url}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            msg = f"Error navigating to '{self.url}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error navigating to '{self.url}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["url"] = self.url
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', url='{self.url}')"