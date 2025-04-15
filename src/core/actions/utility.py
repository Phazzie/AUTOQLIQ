"""Utility actions module for AutoQliq."""

import logging
import time
import os
from typing import Dict, Any, Optional

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, ValidationError

logger = logging.getLogger(__name__)


class WaitAction(ActionBase):
    """Action to pause execution for a specified duration."""
    action_type: str = "Wait"

    def __init__(self, duration_seconds: float, name: Optional[str] = None, **kwargs):
        """Initialize a WaitAction."""
        super().__init__(name or self.action_type, **kwargs)
        try:
             wait_duration = float(duration_seconds)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid duration_seconds: '{duration_seconds}'. Must be number.", field_name="duration_seconds") from e
        if wait_duration < 0:
            raise ValidationError("Duration must be non-negative.", field_name="duration_seconds")
        self.duration_seconds = wait_duration
        logger.debug(f"WaitAction '{self.name}' initialized for {self.duration_seconds}s")

    def validate(self) -> bool:
        """Validate the duration."""
        super().validate()
        if not isinstance(self.duration_seconds, (int, float)) or self.duration_seconds < 0:
            raise ValidationError("Duration must be non-negative number.", field_name="duration_seconds")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the wait action."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) for {self.duration_seconds} seconds")
        try:
            self.validate()
            time.sleep(self.duration_seconds)
            msg = f"Successfully waited for {self.duration_seconds} seconds."
            logger.debug(msg)
            return ActionResult.success(msg)
        except ValidationError as e:
            msg = f"Invalid config for wait action '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Wait interrupted: {e}", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["duration_seconds"] = self.duration_seconds
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', duration_seconds={self.duration_seconds})"


class ScreenshotAction(ActionBase):
    """Action to take a screenshot."""
    action_type: str = "Screenshot"

    def __init__(self, file_path: str, name: Optional[str] = None, **kwargs):
        """Initialize a ScreenshotAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(file_path, str) or not file_path:
            raise ValidationError("File path must be non-empty string.", field_name="file_path")
        self.file_path = file_path
        logger.debug(f"ScreenshotAction '{self.name}' initialized for path: '{self.file_path}'")

    def validate(self) -> bool:
        """Validate the file path."""
        super().validate()
        if not isinstance(self.file_path, str) or not self.file_path:
            raise ValidationError("File path must be non-empty string.", field_name="file_path")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the screenshot action."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) to file: '{self.file_path}'")
        try:
            self.validate()
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory for screenshot: {directory}")
                except OSError as e:
                     raise ActionError(f"Failed directory '{directory}': {e}", action_name=self.name, action_type=self.action_type, cause=e) from e

            driver.take_screenshot(self.file_path) # Raises WebDriverError
            msg = f"Successfully saved screenshot to: {self.file_path}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            msg = f"Error taking screenshot to '{self.file_path}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except IOError as e:
            msg = f"File system error saving screenshot to '{self.file_path}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error taking screenshot to '{self.file_path}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["file_path"] = self.file_path
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', file_path='{self.file_path}')"
