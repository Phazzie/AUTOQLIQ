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
            raise ValidationError("URL must be a non-empty string.", field_name="url", action_name=self.name, action_type=self.action_type)
        if not URL_PATTERN.match(url):
             logger.warning(f"[{self.action_type} '{self.name}'] URL '{url}' may not be valid.")
        self.url = url
        logger.debug(f"[{self.action_type} '{self.name}'] Initialized for URL: '{self.url}'")

    def validate(self) -> bool:
        """Validate the URL."""
        super().validate()
        logger.debug(f"[{self.action_type} '{self.name}'] Validating URL: '{self.url}'")
        if not isinstance(self.url, str) or not self.url:
            raise ValidationError("URL must be a non-empty string.", field_name="url", action_name=self.name, action_type=self.action_type)
        if not URL_PATTERN.match(self.url):
             logger.warning(f"[{self.action_type} '{self.name}'] URL '{self.url}' may not be valid during validation.")
        return True

    def execute(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None, context: Optional[Dict[str, Any]] = None) -> ActionResult:
        """Execute the navigation action."""
        logger.info(f"[{self.action_type} '{self.name}'] Executing -> {self.url}")
        try:
            self.validate()
            driver.get(self.url)
            logger.info(f"[{self.action_type} '{self.name}'] Successfully navigated to {self.url}")
            return ActionResult.success(f"Navigated to {self.url}")
        except (ValidationError, WebDriverError) as e:
            msg = f"[{self.action_type} '{self.name}'] Navigation failed: {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            err_msg = f"[{self.action_type} '{self.name}'] Unexpected error during navigation to {self.url}: {e}"
            logger.error(err_msg, exc_info=True)
            return ActionResult.failure(err_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["url"] = self.url
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', url='{self.url}')"
