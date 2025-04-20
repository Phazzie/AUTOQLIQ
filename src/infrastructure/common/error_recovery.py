"""Error recovery mechanisms for AutoQliq.

This module provides error recovery mechanisms for handling various types of errors
that may occur during application execution.
"""

import logging
import time
import os
import shutil
import json
import threading
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from src.core.exceptions import (
    AutoQliqError, RepositoryError, WorkflowError, CredentialError,
    WebDriverError, ValidationError, UIError, ConfigError
)

logger = logging.getLogger(__name__)


class ErrorRecoveryStrategy:
    """Base class for error recovery strategies."""
    
    def can_handle(self, error: Exception) -> bool:
        """
        Check if this strategy can handle the given error.
        
        Args:
            error: The error to check
            
        Returns:
            True if this strategy can handle the error, False otherwise
        """
        return False
    
    def handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle the error.
        
        Args:
            error: The error to handle
            context: Additional context for error handling
            
        Returns:
            True if the error was handled successfully, False otherwise
        """
        return False


class RetryStrategy(ErrorRecoveryStrategy):
    """Strategy for retrying operations that failed due to transient errors."""
    
    def __init__(
        self,
        max_retries: int = 3,
        delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_errors: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize the retry strategy.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay_seconds: Initial delay between retries in seconds
            backoff_factor: Factor by which to increase the delay after each retry
            retryable_errors: List of error types that can be retried
        """
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds
        self.backoff_factor = backoff_factor
        self.retryable_errors = retryable_errors or [
            WebDriverError,  # Retry WebDriver errors (e.g., network issues)
            RepositoryError,  # Retry repository errors (e.g., file access issues)
        ]
    
    def can_handle(self, error: Exception) -> bool:
        """
        Check if this strategy can handle the given error.
        
        Args:
            error: The error to check
            
        Returns:
            True if this strategy can handle the error, False otherwise
        """
        # Check if the error is of a retryable type
        return any(isinstance(error, error_type) for error_type in self.retryable_errors)
    
    def handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle the error by retrying the operation.
        
        Args:
            error: The error to handle
            context: Additional context for error handling, including:
                - 'operation': The operation to retry (callable)
                - 'args': Arguments for the operation (tuple)
                - 'kwargs': Keyword arguments for the operation (dict)
                - 'retry_count': Current retry count (int)
            
        Returns:
            True if the operation was retried successfully, False otherwise
        """
        # Get the operation and its arguments
        operation = context.get('operation')
        args = context.get('args', ())
        kwargs = context.get('kwargs', {})
        retry_count = context.get('retry_count', 0)
        
        # Check if we can retry
        if not operation or retry_count >= self.max_retries:
            logger.warning(
                f"Cannot retry operation: {'Max retries exceeded' if retry_count >= self.max_retries else 'No operation provided'}"
            )
            return False
        
        # Calculate the delay
        delay = self.delay_seconds * (self.backoff_factor ** retry_count)
        
        # Log the retry attempt
        logger.info(f"Retrying operation (attempt {retry_count + 1}/{self.max_retries}) after {delay:.2f}s delay")
        
        try:
            # Wait before retrying
            time.sleep(delay)
            
            # Retry the operation
            result = operation(*args, **kwargs)
            
            # Update the context with the result
            context['result'] = result
            
            # Log the successful retry
            logger.info(f"Retry successful (attempt {retry_count + 1}/{self.max_retries})")
            
            return True
        except Exception as e:
            # Log the failed retry
            logger.warning(f"Retry failed (attempt {retry_count + 1}/{self.max_retries}): {e}")
            
            # Update the retry count
            context['retry_count'] = retry_count + 1
            context['last_error'] = e
            
            # Try again if we haven't exceeded the max retries
            if retry_count + 1 < self.max_retries:
                return self.handle(e, context)
            
            return False


class BackupRestoreStrategy(ErrorRecoveryStrategy):
    """Strategy for recovering from data corruption by restoring from backups."""
    
    def __init__(
        self,
        backup_dir: str = "backups",
        max_backups: int = 5,
        backup_interval_hours: float = 24.0
    ):
        """
        Initialize the backup/restore strategy.
        
        Args:
            backup_dir: Directory for storing backups
            max_backups: Maximum number of backups to keep
            backup_interval_hours: Interval between backups in hours
        """
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.backup_interval_hours = backup_interval_hours
        self.last_backup_time = 0.0
        
        # Create the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
    
    def can_handle(self, error: Exception) -> bool:
        """
        Check if this strategy can handle the given error.
        
        Args:
            error: The error to check
            
        Returns:
            True if this strategy can handle the error, False otherwise
        """
        # Check if the error is related to data corruption
        if isinstance(error, RepositoryError):
            error_str = str(error).lower()
            return any(keyword in error_str for keyword in [
                "corrupt", "invalid", "malformed", "json", "parse", "syntax"
            ])
        return False
    
    def handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle the error by restoring from a backup.
        
        Args:
            error: The error to handle
            context: Additional context for error handling, including:
                - 'file_path': Path to the corrupted file
                - 'repository': Repository instance
            
        Returns:
            True if the error was handled successfully, False otherwise
        """
        # Get the file path and repository
        file_path = context.get('file_path')
        repository = context.get('repository')
        
        if not file_path or not repository:
            logger.warning("Cannot restore from backup: Missing file path or repository")
            return False
        
        try:
            # Find the latest backup
            backup_file = self._find_latest_backup(file_path)
            
            if not backup_file:
                logger.warning(f"No backup found for {file_path}")
                return False
            
            # Restore from the backup
            logger.info(f"Restoring {file_path} from backup {backup_file}")
            
            # Create a backup of the current file before restoring
            self._create_backup(file_path, is_corrupted=True)
            
            # Copy the backup file to the original location
            shutil.copy2(backup_file, file_path)
            
            # Reload the repository if possible
            if hasattr(repository, 'reload'):
                repository.reload()
            
            logger.info(f"Successfully restored {file_path} from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """
        Create a backup of the specified file.
        
        Args:
            file_path: Path to the file to back up
            
        Returns:
            Path to the backup file, or None if backup failed
        """
        return self._create_backup(file_path)
    
    def _create_backup(self, file_path: str, is_corrupted: bool = False) -> Optional[str]:
        """
        Create a backup of the specified file.
        
        Args:
            file_path: Path to the file to back up
            is_corrupted: Whether the file is known to be corrupted
            
        Returns:
            Path to the backup file, or None if backup failed
        """
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                logger.warning(f"Cannot back up nonexistent file: {file_path}")
                return None
            
            # Check if it's time to create a backup
            current_time = time.time()
            if not is_corrupted and current_time - self.last_backup_time < self.backup_interval_hours * 3600:
                logger.debug(f"Skipping backup of {file_path}: Backup interval not reached")
                return None
            
            # Create the backup filename
            filename = os.path.basename(file_path)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filename}.{timestamp}{'.corrupted' if is_corrupted else ''}.bak"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy the file to the backup location
            shutil.copy2(file_path, backup_path)
            
            # Update the last backup time
            if not is_corrupted:
                self.last_backup_time = current_time
            
            # Clean up old backups
            self._cleanup_old_backups(file_path)
            
            logger.info(f"Created backup of {file_path} at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path}: {e}")
            return None
    
    def _find_latest_backup(self, file_path: str) -> Optional[str]:
        """
        Find the latest backup of the specified file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Path to the latest backup file, or None if no backup found
        """
        try:
            # Get the filename
            filename = os.path.basename(file_path)
            
            # Find all backups of this file
            backups = []
            for backup_file in os.listdir(self.backup_dir):
                if backup_file.startswith(filename) and backup_file.endswith(".bak"):
                    # Skip corrupted backups
                    if ".corrupted." in backup_file:
                        continue
                    
                    backup_path = os.path.join(self.backup_dir, backup_file)
                    backups.append((backup_path, os.path.getmtime(backup_path)))
            
            # Sort backups by modification time (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Return the latest backup
            return backups[0][0] if backups else None
        except Exception as e:
            logger.error(f"Failed to find latest backup for {file_path}: {e}")
            return None
    
    def _cleanup_old_backups(self, file_path: str) -> None:
        """
        Clean up old backups of the specified file.
        
        Args:
            file_path: Path to the file
        """
        try:
            # Get the filename
            filename = os.path.basename(file_path)
            
            # Find all backups of this file
            backups = []
            for backup_file in os.listdir(self.backup_dir):
                if backup_file.startswith(filename) and backup_file.endswith(".bak"):
                    backup_path = os.path.join(self.backup_dir, backup_file)
                    backups.append((backup_path, os.path.getmtime(backup_path)))
            
            # Sort backups by modification time (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for backup_path, _ in backups[self.max_backups:]:
                os.remove(backup_path)
                logger.debug(f"Removed old backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to clean up old backups for {file_path}: {e}")


class WebDriverRecoveryStrategy(ErrorRecoveryStrategy):
    """Strategy for recovering from WebDriver errors."""
    
    def __init__(self, max_restart_attempts: int = 3):
        """
        Initialize the WebDriver recovery strategy.
        
        Args:
            max_restart_attempts: Maximum number of restart attempts
        """
        self.max_restart_attempts = max_restart_attempts
    
    def can_handle(self, error: Exception) -> bool:
        """
        Check if this strategy can handle the given error.
        
        Args:
            error: The error to check
            
        Returns:
            True if this strategy can handle the error, False otherwise
        """
        return isinstance(error, WebDriverError)
    
    def handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle the error by restarting the WebDriver.
        
        Args:
            error: The error to handle
            context: Additional context for error handling, including:
                - 'webdriver': WebDriver instance
                - 'webdriver_factory': WebDriverFactory instance
                - 'browser_type': Browser type
                - 'restart_count': Current restart count
            
        Returns:
            True if the error was handled successfully, False otherwise
        """
        # Get the WebDriver and factory
        webdriver = context.get('webdriver')
        webdriver_factory = context.get('webdriver_factory')
        browser_type = context.get('browser_type')
        restart_count = context.get('restart_count', 0)
        
        # Check if we can restart
        if not webdriver or not webdriver_factory or restart_count >= self.max_restart_attempts:
            logger.warning(
                f"Cannot restart WebDriver: {'Max restart attempts exceeded' if restart_count >= self.max_restart_attempts else 'Missing WebDriver or factory'}"
            )
            return False
        
        try:
            # Close the current WebDriver
            logger.info("Closing WebDriver")
            try:
                webdriver.quit()
            except Exception as e:
                logger.warning(f"Failed to close WebDriver: {e}")
            
            # Create a new WebDriver
            logger.info(f"Creating new WebDriver (attempt {restart_count + 1}/{self.max_restart_attempts})")
            new_webdriver = webdriver_factory.create_driver(browser_type=browser_type)
            
            # Update the context with the new WebDriver
            context['webdriver'] = new_webdriver
            context['restart_count'] = restart_count + 1
            
            logger.info(f"WebDriver restart successful (attempt {restart_count + 1}/{self.max_restart_attempts})")
            return True
        except Exception as e:
            logger.error(f"Failed to restart WebDriver: {e}")
            
            # Update the restart count
            context['restart_count'] = restart_count + 1
            
            # Try again if we haven't exceeded the max restart attempts
            if restart_count + 1 < self.max_restart_attempts:
                return self.handle(e, context)
            
            return False


class ErrorRecoveryManager:
    """Manager for error recovery strategies."""
    
    def __init__(self):
        """Initialize the error recovery manager."""
        self.strategies: List[ErrorRecoveryStrategy] = []
        self.recovery_attempts: Dict[str, int] = {}
        self.max_recovery_attempts = 5
        self.recovery_timeout = 300  # 5 minutes
        self.last_recovery_time = 0.0
    
    def register_strategy(self, strategy: ErrorRecoveryStrategy) -> None:
        """
        Register an error recovery strategy.
        
        Args:
            strategy: The strategy to register
        """
        self.strategies.append(strategy)
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Handle an error using the registered strategies.
        
        Args:
            error: The error to handle
            context: Additional context for error handling
            
        Returns:
            Tuple of (success, result) where success is True if the error was handled
            successfully, and result is the result of the recovery operation if applicable
        """
        # Generate an error key for tracking recovery attempts
        error_key = self._generate_error_key(error, context)
        
        # Check if we've exceeded the max recovery attempts for this error
        if self._exceeded_recovery_attempts(error_key):
            logger.warning(f"Exceeded max recovery attempts for error: {error_key}")
            return False, None
        
        # Check if we're within the recovery timeout
        if not self._within_recovery_timeout():
            logger.warning("Recovery timeout in effect, not attempting recovery")
            return False, None
        
        # Try each strategy
        for strategy in self.strategies:
            if strategy.can_handle(error):
                logger.info(f"Attempting recovery using {strategy.__class__.__name__}")
                
                # Increment the recovery attempt count
                self._increment_recovery_attempts(error_key)
                
                # Update the last recovery time
                self.last_recovery_time = time.time()
                
                # Handle the error
                success = strategy.handle(error, context)
                
                if success:
                    logger.info(f"Recovery successful using {strategy.__class__.__name__}")
                    return True, context.get('result')
                
                logger.warning(f"Recovery failed using {strategy.__class__.__name__}")
        
        logger.warning(f"No suitable recovery strategy found for error: {error}")
        return False, None
    
    def _generate_error_key(self, error: Exception, context: Dict[str, Any]) -> str:
        """
        Generate a key for tracking recovery attempts for an error.
        
        Args:
            error: The error
            context: The error context
            
        Returns:
            A string key
        """
        # Use the error type and message as the key
        error_type = type(error).__name__
        error_message = str(error)
        
        # Include relevant context information
        context_str = ""
        if 'file_path' in context:
            context_str += f"file={context['file_path']}"
        if 'operation' in context:
            context_str += f"op={context['operation'].__name__}"
        
        return f"{error_type}:{error_message}:{context_str}"
    
    def _exceeded_recovery_attempts(self, error_key: str) -> bool:
        """
        Check if we've exceeded the max recovery attempts for an error.
        
        Args:
            error_key: The error key
            
        Returns:
            True if we've exceeded the max recovery attempts, False otherwise
        """
        return self.recovery_attempts.get(error_key, 0) >= self.max_recovery_attempts
    
    def _increment_recovery_attempts(self, error_key: str) -> None:
        """
        Increment the recovery attempt count for an error.
        
        Args:
            error_key: The error key
        """
        self.recovery_attempts[error_key] = self.recovery_attempts.get(error_key, 0) + 1
    
    def _within_recovery_timeout(self) -> bool:
        """
        Check if we're within the recovery timeout.
        
        Returns:
            True if we're within the recovery timeout, False otherwise
        """
        return time.time() - self.last_recovery_time >= self.recovery_timeout
    
    def reset_recovery_attempts(self) -> None:
        """Reset all recovery attempt counts."""
        self.recovery_attempts.clear()
        self.last_recovery_time = 0.0


# Create a global instance of the error recovery manager
recovery_manager = ErrorRecoveryManager()

# Register default strategies
recovery_manager.register_strategy(RetryStrategy())
recovery_manager.register_strategy(BackupRestoreStrategy())
recovery_manager.register_strategy(WebDriverRecoveryStrategy())


def with_error_recovery(
    error_context: str,
    recovery_context: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator for functions that should use error recovery.
    
    Args:
        error_context: Description of the operation for error messages
        recovery_context: Additional context for error recovery
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Create the context
            context = recovery_context or {}
            context.update({
                'operation': func,
                'args': args,
                'kwargs': kwargs,
                'retry_count': 0
            })
            
            try:
                # Call the function
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                logger.error(f"Error in {error_context}: {e}")
                
                # Try to recover
                success, result = recovery_manager.handle_error(e, context)
                
                if success:
                    logger.info(f"Successfully recovered from error in {error_context}")
                    return result
                
                # Re-raise the error if recovery failed
                logger.warning(f"Failed to recover from error in {error_context}")
                raise
        
        return wrapper
    
    return decorator
