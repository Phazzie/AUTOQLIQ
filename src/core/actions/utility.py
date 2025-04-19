"""Utility actions module for AutoQliq."""

import logging
import time
import os
import threading
import datetime
import shutil
from typing import Dict, Any, Optional

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, ValidationError

logger = logging.getLogger(__name__)


class WaitAction(ActionBase):
    """Action to pause execution for a specified duration."""
    action_type: str = "Wait"
    # Default max wait time (can be overridden by config)
    _DEFAULT_MAX_WAIT_TIME = 300  # 5 minutes
    
    def __init__(self, 
                duration_seconds: float, 
                name: Optional[str] = None, 
                max_wait_time: Optional[float] = None,
                report_interval: Optional[float] = None, 
                **kwargs):
        """Initialize a WaitAction.
        
        Args:
            duration_seconds: The number of seconds to wait
            name: Optional name for this action instance
            max_wait_time: Optional maximum allowed wait time
            report_interval: Optional interval for progress reporting
        """
        super().__init__(name or self.action_type, **kwargs)
        self.duration_seconds = self._validate_duration(duration_seconds)
        self.max_wait_time = self._get_max_wait_time(max_wait_time)
        self.report_interval = self._get_report_interval(report_interval)
        self._stop_event = threading.Event()
        
        logger.debug(
            f"WaitAction '{self.name}' initialized for {self.duration_seconds}s "
            f"(max: {self.max_wait_time}s, report every: {self.report_interval}s)"
        )

    def _validate_duration(self, duration_seconds) -> float:
        """Validate and convert duration to float."""
        try:
            wait_duration = float(duration_seconds)
        except (ValueError, TypeError) as error:
            raise ValidationError(
                f"Invalid duration: '{duration_seconds}'. Must be a number.",
                field_name="duration_seconds"
            ) from error
            
        if wait_duration < 0:
            raise ValidationError(
                "Duration must be non-negative.",
                field_name="duration_seconds"
            )
            
        return wait_duration
        
    def _get_max_wait_time(self, max_wait_time) -> float:
        """Get the maximum wait time value."""
        if max_wait_time is not None:
            return float(max_wait_time)
        return self._DEFAULT_MAX_WAIT_TIME
        
    def _get_report_interval(self, report_interval) -> float:
        """Get the report interval value."""
        if report_interval is not None:
            return float(report_interval)
        return max(1.0, self.duration_seconds / 10)

    def validate(self) -> bool:
        """Validate the duration."""
        super().validate()
        if self.duration_seconds > self.max_wait_time:
            logger.warning(
                f"Wait duration ({self.duration_seconds}s) exceeds maximum "
                f"({self.max_wait_time}s). Will limit to maximum."
            )
        return True

    def interrupt(self) -> None:
        """Interrupt the wait operation."""
        self._stop_event.set()
        logger.info(f"Wait action '{self.name}' interrupted.")

    def _do_wait(self, actual_duration: float) -> tuple:
        """Perform the wait operation with progress reporting.
        
        Returns:
            tuple: (success, message, elapsed_time)
        """
        # Reset stop event in case of reuse
        self._stop_event.clear()
        
        # Start time for tracking
        start_time = time.time()
        elapsed = 0
        
        # Interruptible wait with progress reporting
        while elapsed < actual_duration and not self._stop_event.is_set():
            next_report_time = min(self.report_interval, actual_duration - elapsed)
            # Wait for the next report interval or until interrupted
            interrupted = self._stop_event.wait(next_report_time)
            if interrupted:
                break
                
            elapsed = time.time() - start_time
            progress_pct = min(100, (elapsed / actual_duration) * 100)
            
            # Log progress at report intervals
            logger.debug(
                f"Wait progress: {progress_pct:.1f}% "
                f"({elapsed:.1f}s / {actual_duration:.1f}s)"
            )
        
        # Final elapsed time
        elapsed = time.time() - start_time
        
        if self._stop_event.is_set():
            msg = (f"Wait interrupted after {elapsed:.2f} seconds "
                   f"(requested: {actual_duration:.2f}s).")
            logger.info(msg)
            success = elapsed >= actual_duration
        else:
            msg = f"Successfully waited for {elapsed:.2f} seconds."
            logger.debug(msg)
            success = True
            
        return success, msg, elapsed

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the wait action using interruptible sleep."""
        logger.info(
            f"Executing {self.action_type} action (Name: {self.name}) "
            f"for {self.duration_seconds} seconds"
        )
        
        try:
            self.validate()
            
            # Use actual duration or cap at max_wait_time
            actual_duration = min(self.duration_seconds, self.max_wait_time)
            
            # Do the actual wait operation
            success, message, _ = self._do_wait(actual_duration)
            
            return (ActionResult.success(message) if success 
                    else ActionResult.failure(message))
                
        except ValidationError as error:
            msg = f"Invalid config for wait action '{self.name}': {error}"
            logger.error(msg)
            return ActionResult.failure(msg)
            
        except KeyboardInterrupt:
            elapsed = time.time() - time.time()  # Should be near zero
            msg = f"Wait interrupted by user after {elapsed:.2f} seconds."
            logger.warning(msg)
            return ActionResult.failure(msg)
            
        except Exception as error:
            error_obj = ActionError(
                f"Wait interrupted: {error}", 
                action_name=self.name, 
                action_type=self.action_type,
                cause=error
            )
            logger.error(str(error_obj), exc_info=True)
            return ActionResult.failure(str(error_obj))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["duration_seconds"] = self.duration_seconds
        
        # Include advanced parameters only if they differ from defaults
        if self.max_wait_time != self._DEFAULT_MAX_WAIT_TIME:
            base_dict["max_wait_time"] = self.max_wait_time
            
        default_report_interval = max(1.0, self.duration_seconds / 10)
        if self.report_interval != default_report_interval:
            base_dict["report_interval"] = self.report_interval
            
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"duration_seconds={self.duration_seconds}, "
                f"max_wait_time={self.max_wait_time})")


class ScreenshotAction(ActionBase):
    """Action to take a screenshot."""
    action_type: str = "Screenshot"
    
    def __init__(self, file_path: str, name: Optional[str] = None, **kwargs):
        """Initialize a ScreenshotAction."""
        super().__init__(name or self.action_type, **kwargs)
        self.file_path = self._validate_file_path(file_path)
        logger.debug(
            f"ScreenshotAction '{self.name}' initialized for path: '{self.file_path}'"
        )

    def _validate_file_path(self, file_path: str) -> str:
        """Validate file path is a non-empty string and return it."""
        if not isinstance(file_path, str) or not file_path:
            raise ValidationError(
                "File path must be a non-empty string.", 
                field_name="file_path"
            )
        return file_path

    def _ensure_directory_exists(self, directory_path: str) -> None:
        """Ensure the directory for the screenshot exists."""
        if not directory_path:
            return
            
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                logger.info(f"Created directory for screenshot: {directory_path}")
        except OSError as error:
            raise ActionError(
                f"Failed to create directory '{directory_path}': {error}", 
                action_name=self.name, 
                action_type=self.action_type,
                cause=error
            ) from error

    def _create_backup(self) -> Optional[str]:
        """Create a backup of existing file if it exists.
        
        Returns:
            Optional[str]: Path to backup file or None if no backup was created
        """
        if not os.path.exists(self.file_path):
            return None
            
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.file_path}.{timestamp}.bak"
            shutil.copy2(self.file_path, backup_path)
            logger.debug(f"Created backup of existing screenshot: {backup_path}")
            return backup_path
        except (OSError, IOError) as error:
            logger.warning(
                f"Failed to create backup of {self.file_path}: {error}"
            )
            return None

    def validate(self) -> bool:
        """Validate the file path."""
        super().validate()
        self._validate_file_path(self.file_path)
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the screenshot action."""
        logger.info(
            f"Executing {self.action_type} action (Name: {self.name}) "
            f"to file: '{self.file_path}'"
        )
        
        backup_path = None
        
        try:
            self.validate()
            
            # Prepare directory
            directory = os.path.dirname(self.file_path)
            self._ensure_directory_exists(directory)
            
            # Create backup if file exists
            backup_path = self._create_backup()
            
            # Take screenshot
            driver.take_screenshot(self.file_path)
            
            # Success message includes backup info if applicable
            backup_info = f" (backup: {backup_path})" if backup_path else ""
            msg = f"Successfully saved screenshot to: {self.file_path}{backup_info}"
            logger.debug(msg)
            return ActionResult.success(msg)
            
        except (ValidationError, WebDriverError) as error:
            msg = f"Error taking screenshot to '{self.file_path}': {error}"
            logger.error(msg)
            return ActionResult.failure(msg)
            
        except IOError as error:
            # Try to restore from backup if we have one
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, self.file_path)
                    logger.info(f"Restored from backup: {backup_path}")
                except (OSError, IOError) as restore_error:
                    logger.warning(
                        f"Failed to restore from backup: {restore_error}"
                    )
                    
            msg = f"File system error saving screenshot: {error}"
            logger.error(msg)
            return ActionResult.failure(msg)
            
        except Exception as error:
            error_obj = ActionError(
                f"Unexpected error taking screenshot to '{self.file_path}'", 
                action_name=self.name, 
                action_type=self.action_type,
                cause=error
            )
            logger.error(str(error_obj), exc_info=True)
            return ActionResult.failure(str(error_obj))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["file_path"] = self.file_path
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"{self.__class__.__name__}"
                f"(name='{self.name}', file_path='{self.file_path}')")
