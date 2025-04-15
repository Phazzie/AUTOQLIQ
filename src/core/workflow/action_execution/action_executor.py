"""Action executor implementation.

This module provides the ActionExecutor class for executing actions.
"""

import logging
from typing import Dict, Any, Optional

from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ValidationError, ActionError
from src.core.workflow.action_execution.interfaces import IActionExecutor

logger = logging.getLogger(__name__)


class ActionExecutor(IActionExecutor):
    """
    Executes actions.

    Responsible for validating and executing individual actions.
    """

    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None
    ):
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

    def _execute_validated_action(
        self,
        action: IAction,
        context: Dict[str, Any]
    ) -> ActionResult:
        """
        Validate and execute an action.

        Args:
            action: The action to execute
            context: The execution context

        Returns:
            ActionResult: The result of the action execution

        Raises:
            ValidationError: If the action fails validation
            ActionError: If an error occurs during execution
        """
        # Validate the action
        action.validate()

        # Execute the action
        result = action.execute(self.driver, self.credential_repo, context)

        # Verify the result is an ActionResult
        if not isinstance(result, ActionResult):
            logger.error(
                f"Action '{action.name}' did not return ActionResult "
                f"(got {type(result).__name__})."
            )
            return ActionResult.failure(
                f"Action '{action.name}' implementation error: Invalid return type."
            )

        return result

    def _log_action_result(self, action_display_name: str, result: ActionResult) -> None:
        """
        Log the result of an action execution.

        Args:
            action_display_name: Display name of the action
            result: The result of the action execution
        """
        if not result.is_success():
            logger.warning(
                f"Action '{action_display_name}' returned failure: {result.message}"
            )
        else:
            logger.debug(f"Action '{action_display_name}' returned success.")

    def _handle_validation_error(
        self,
        action_display_name: str,
        error: ValidationError
    ) -> ActionResult:
        """
        Handle a validation error.

        Args:
            action_display_name: Display name of the action
            error: The validation error

        Returns:
            ActionResult: A failure result with validation error information
        """
        logger.error(f"Validation error for {action_display_name}: {error}")
        return ActionResult.failure(
            f"Validation error: {error}",
            data={"validation_error": str(error)}
        )

    def _handle_action_error(
        self,
        action_display_name: str,
        error: ActionError
    ) -> ActionResult:
        """
        Handle an action error.

        Args:
            action_display_name: Display name of the action
            error: The action error

        Returns:
            ActionResult: A failure result with action error information
        """
        logger.error(f"Action error for {action_display_name}: {error}")
        return ActionResult.failure(
            f"Action error: {error}",
            data={"action_error": str(error)}
        )
