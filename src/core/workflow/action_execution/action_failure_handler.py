"""Action failure handler implementation.

This module provides the ActionFailureHandler class for handling action failures.
"""

import logging
from typing import Dict, Any

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError
from src.core.workflow.action_execution.interfaces import IActionFailureHandler

logger = logging.getLogger(__name__)


class ActionFailureHandler(IActionFailureHandler):
    """
    Handles action failures.

    Responsible for determining what to do when an action fails.
    """

    def handle_action_failure(
        self,
        action_result: ActionResult,
        action: IAction,
        action_display_name: str,
        error_strategy: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Handle an action failure.

        Args:
            action_result: The result of the failed action
            action: The action that failed
            action_display_name: Display name of the action
            error_strategy: Error handling strategy
            context: Execution context

        Raises:
            ActionError: If the error strategy is STOP_ON_ERROR
        """
        # Mark in the context that we had failures
        if "state" in context and isinstance(context["state"], dict):
            context["state"]["had_action_failures"] = True

        # Log the failure
        logger.warning(f"Action failed: {action_display_name} - {action_result.message}")

        # If the error strategy is STOP_ON_ERROR, raise an ActionError
        if error_strategy == "STOP_ON_ERROR":
            raise ActionError(
                f"Action failed: {action_display_name} - {action_result.message}",
                action=action,
                result=action_result
            )
