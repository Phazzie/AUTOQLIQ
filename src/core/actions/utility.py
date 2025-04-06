"""Utility actions module for AutoQliq.

Contains actions for general browser automation tasks like waiting
or taking screenshots.
"""

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
    """
    Action to pause execution for a specified duration.

    Attributes:
        duration_seconds (float): The duration to wait in seconds.
        action_type (str): The type name of the action ("Wait").
    """
    action_type: str = "Wait"

    def __init__(self, duration_seconds: float, name: Optional[str] = None, **kwargs):
        """
        Initialize a WaitAction.

        Args:
            duration_seconds (float): The time to wait in seconds. Must be non-negative.
            name (Optional[str]): A descriptive name for the action instance. Defaults to "Wait".
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        try:
             # Attempt to convert to float, handling potential errors
             wait_duration = float(duration_seconds)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid duration_seconds value: '{duration_seconds}'. Must be a number.", field_name="duration_seconds") from e

        if wait_duration < 0:
            raise ValidationError("Duration must be a non-negative number.", field_name="duration_seconds")

        self.duration_seconds = wait_duration
        logger.debug(f"WaitAction '{self.name}' initialized for duration: {self.duration_seconds}s")

    def validate(self) -> bool:
        """Validate that the duration is a non-negative number."""
        super().validate()
        if not isinstance(self.duration_seconds, (int, float)) or self.duration_seconds < 0:
            raise ValidationError("Duration must be a non-negative number.", field_name="duration_seconds")
        return True

    def execute(
        self,
        driver: IWebDriver, # Parameter included for interface consistency, though not used
        credential_repo: Optional[ICredentialRepository] = None # Parameter included for interface consistency
    ) -> ActionResult:
        """
        Execute the wait action by pausing execution.

        Args:
            driver (IWebDriver): The web driver instance (not used directly).
            credential_repo (Optional[ICredentialRepository]): Not used by this action.

        Returns:
            ActionResult: Result indicating successful completion of the wait.
        """
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) for {self.duration_seconds} seconds")
        try:
            self.validate() # Ensure configuration is valid
            time.sleep(self.duration_seconds)
            msg = f"Successfully waited for {self.duration_seconds} seconds."
            logger.debug(msg)
            return ActionResult.success(msg)
        except ValidationError as e:
            # Catch validation errors
            msg = f"Invalid configuration for wait action '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            # time.sleep can be interrupted (e.g., KeyboardInterrupt), though unlikely in automation context
            error = ActionError(f"Wait action interrupted: {e}", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["duration_seconds"] = self.duration_seconds
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', duration_seconds={self.duration_seconds})"


class ScreenshotAction(ActionBase):
    """
    Action to take a screenshot of the current browser window.

    Attributes:
        file_path (str): The path where the screenshot file should be saved.
        action_type (str): The type name of the action ("Screenshot").
    """
    action_type: str = "Screenshot"

    def __init__(self, file_path: str, name: Optional[str] = None, **kwargs):
        """
        Initialize a ScreenshotAction.

        Args:
            file_path (str): The full path (including filename) to save the screenshot.
            name (Optional[str]): A descriptive name for the action instance. Defaults to "Screenshot".
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(file_path, str) or not file_path:
            raise ValidationError("File path must be a non-empty string.", field_name="file_path")
        # Basic path validation could be added (e.g., check extension, directory exists?)
        # For now, just ensure it's a non-empty string.
        self.file_path = file_path
        logger.debug(f"ScreenshotAction '{self.name}' initialized for path: '{self.file_path}'")

    def validate(self) -> bool:
        """Validate that the file path is a non-empty string."""
        super().validate()
        if not isinstance(self.file_path, str) or not self.file_path:
            raise ValidationError("File path must be a non-empty string.", field_name="file_path")
        # Optionally check if the directory exists and is writable here,
        # but might be better to let it fail during execute.
        # directory = os.path.dirname(self.file_path)
        # if directory and not os.path.isdir(directory):
        #      raise ValidationError(f"Directory does not exist: {directory}", field_name="file_path")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None # Parameter included for interface consistency
    ) -> ActionResult:
        """
        Execute the screenshot action using the web driver.

        Args:
            driver (IWebDriver): The web driver instance.
            credential_repo (Optional[ICredentialRepository]): Not used by this action.

        Returns:
            ActionResult: Result of the screenshot operation.
        """
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) to file: '{self.file_path}'")
        try:
            self.validate() # Ensure configuration is valid

             # Ensure directory exists before taking screenshot
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory for screenshot: {directory}")
                except OSError as e:
                     raise ActionError(f"Failed to create directory for screenshot '{self.file_path}': {e}", action_name=self.name, action_type=self.action_type, cause=e) from e

            driver.take_screenshot(self.file_path) # Assumes this raises WebDriverError on failure
            msg = f"Successfully saved screenshot to: {self.file_path}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            # Catch validation or driver errors
            msg = f"Error taking screenshot to '{self.file_path}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except IOError as e:
            # Catch file system errors explicitly (permissions, disk full etc.)
            msg = f"File system error saving screenshot to '{self.file_path}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            # Catch unexpected errors
            error = ActionError(f"Unexpected error taking screenshot to '{self.file_path}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["file_path"] = self.file_path
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', file_path='{self.file_path}')"