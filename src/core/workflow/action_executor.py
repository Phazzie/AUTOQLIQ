################################################################################
"""Action executor for workflow execution.

This module provides the ActionExecutor class for executing individual actions.
"""
################################################################################

import logging
from typing import Dict, Any, Optional

from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    ElementNotInteractableException, StaleElementReferenceException
)

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, ValidationError

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes individual actions.

    Handles validation, execution, and error handling for individual actions.
    """

    def __init__(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None):
        """
        Initialize the action executor.

        Args:
            driver: The web driver instance
            credential_repo: Optional credential repository
        """
        self.driver = driver
        self.credential_repo = credential_repo

    def execute_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action.

        Args:
            action: The action to execute
            context: The execution context

        Returns:
            ActionResult: The result of the action execution
        """
        action_display_name = f"{action.name} ({action.action_type})"
        logger.debug(f"Executing action: {action_display_name}")

        try:
            # Validate and execute the action
            result = self._execute_validated_action(action, context)

            # Log the result
            self._log_action_result(action_display_name, result)

            return result

        except ValidationError as error:
            return self._handle_validation_error(action_display_name, error)

        except ActionError as error:
            return self._handle_action_error(action_display_name, error)

        except (NoSuchElementException, ElementNotInteractableException) as error:
            return self._handle_element_error(action, action_display_name, error)

        except StaleElementReferenceException as error:
            return self._handle_stale_element_error(action, action_display_name, error)

        except TimeoutException as error:
            return self._handle_timeout_error(action, action_display_name, error)

        except WebDriverException as error:
            return self._handle_webdriver_error(action, action_display_name, error)

        except Exception as error:
            return self._handle_unexpected_error(action, action_display_name, error)

    def _execute_validated_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """Execute an action after validating it.

        Args:
            action: The action to execute
            context: The execution context

        Returns:
            ActionResult: The result of the action execution

        Raises:
            ValidationError: If the action validation fails
            ActionError: If the action execution fails
        """
        # Validate the action
        action.validate()

        # Execute the action
        result = action.execute(self.driver, self.credential_repo, context)

        # Validate the result
        if not isinstance(result, ActionResult):
            action_name = action.name
            logger.error(
                f"Action '{action_name}' did not return ActionResult "
                f"(got {type(result).__name__})."
            )
            return ActionResult.failure(
                f"Action '{action_name}' implementation error: Invalid return type."
            )

        return result

    def _log_action_result(self, action_display_name: str, result: ActionResult) -> None:
        """Log the result of an action execution.

        Args:
            action_display_name: The display name of the action
            result: The result of the action execution
        """
        if not result.is_success():
            logger.warning(f"Action '{action_display_name}' returned failure: {result.message}")
        else:
            logger.debug(f"Action '{action_display_name}' returned success.")

    def _handle_validation_error(self, action_display_name: str, error: ValidationError) -> ActionResult:
        """Handle a validation error.

        Args:
            action_display_name: The display name of the action
            error: The validation error

        Returns:
            ActionResult: A failure result
        """
        logger.error(f"Validation failed for action '{action_display_name}': {error}")
        return ActionResult.failure(f"Action validation failed: {error}")

    def _handle_action_error(self, action_display_name: str, error: ActionError) -> ActionResult:
        """Handle an action error.

        Args:
            action_display_name: The display name of the action
            error: The action error

        Returns:
            ActionResult: A failure result
        """
        logger.error(f"ActionError during execution of action '{action_display_name}': {error}")
        return ActionResult.failure(f"Action execution error: {error}")

    def _handle_element_error(
        self, action: IAction, action_display_name: str, error: Exception
    ) -> ActionResult:
        """Handle an element error.

        Args:
            action: The action that caused the error
            action_display_name: The display name of the action
            error: The element error

        Returns:
            ActionResult: A failure result
        """
        logger.error(f"Element error during execution of action '{action_display_name}': {error}")
        wrapped_error = ActionError(
            f"Element error: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )
        return ActionResult.failure(str(wrapped_error), {"error_type": "element_error"})

    def _handle_stale_element_error(
        self, action: IAction, action_display_name: str, error: StaleElementReferenceException
    ) -> ActionResult:
        """Handle a stale element error.

        Args:
            action: The action that caused the error
            action_display_name: The display name of the action
            error: The stale element error

        Returns:
            ActionResult: A failure result
        """
        logger.error(
            f"Stale element reference during execution of action '{action_display_name}': {error}"
        )
        wrapped_error = ActionError(
            f"Stale element: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )
        return ActionResult.failure(str(wrapped_error), {"error_type": "stale_element"})

    def _handle_timeout_error(
        self, action: IAction, action_display_name: str, error: TimeoutException
    ) -> ActionResult:
        """Handle a timeout error.

        Args:
            action: The action that caused the error
            action_display_name: The display name of the action
            error: The timeout error

        Returns:
            ActionResult: A failure result
        """
        logger.error(f"Timeout during execution of action '{action_display_name}': {error}")
        wrapped_error = ActionError(
            f"Timeout: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )
        return ActionResult.failure(str(wrapped_error), {"error_type": "timeout"})

    def _handle_webdriver_error(
        self, action: IAction, action_display_name: str, error: WebDriverException
    ) -> ActionResult:
        """Handle a webdriver error.

        Args:
            action: The action that caused the error
            action_display_name: The display name of the action
            error: The webdriver error

        Returns:
            ActionResult: A failure result
        """
        logger.error(f"WebDriver error during execution of action '{action_display_name}': {error}")
        wrapped_error = ActionError(
            f"WebDriver error: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )
        return ActionResult.failure(str(wrapped_error), {"error_type": "webdriver_error"})

    def _handle_unexpected_error(
        self, action: IAction, action_display_name: str, error: Exception
    ) -> ActionResult:
        """Handle an unexpected error.

        Args:
            action: The action that caused the error
            action_display_name: The display name of the action
            error: The unexpected error

        Returns:
            ActionResult: A failure result
        """
        logger.exception(
            f"Unexpected exception during execution of action '{action_display_name}'"
        )
        wrapped_error = ActionError(
            f"Unexpected exception: {error}",
            action_name=action.name,
            action_type=action.action_type,
            cause=error
        )
        return ActionResult.failure(str(wrapped_error), {"error_type": "unexpected_error"})
