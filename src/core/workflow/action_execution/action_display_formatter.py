"""Action display formatter implementation.

This module provides the ActionDisplayFormatter class for formatting action display names.
"""

import logging
from typing import Optional

from src.core.interfaces import IAction
from src.core.workflow.action_execution.interfaces import IActionDisplayFormatter

logger = logging.getLogger(__name__)


class ActionDisplayFormatter(IActionDisplayFormatter):
    """
    Formats action display names for logging.

    Responsible for creating human-readable display names for actions.
    """

    def format_action_display_name(
        self,
        action: IAction,
        log_prefix: str,
        step_number: int
    ) -> str:
        """
        Format an action's display name for logging.

        Args:
            action: The action to format the display name for
            log_prefix: Prefix for log messages
            step_number: Step number in the workflow

        Returns:
            str: Formatted display name
        """
        action_type = getattr(action, "action_type", "Unknown")
        action_name = getattr(action, "name", "Unnamed")
        
        return f"{log_prefix}Step {step_number}: {action_name} ({action_type})"
