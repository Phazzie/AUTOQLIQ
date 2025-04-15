"""Action type detector implementation.

This module provides the ActionTypeDetector class for detecting action types.
"""

import logging
from typing import Optional

from src.core.interfaces import IAction
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
from src.core.workflow.action_execution.interfaces import IActionTypeDetector

logger = logging.getLogger(__name__)


class ActionTypeDetector(IActionTypeDetector):
    """
    Detects the type of an action.

    Responsible for determining if an action is a control flow action.
    """

    def detect_action_type(self, action: IAction) -> Optional[str]:
        """
        Detect the type of an action.

        Args:
            action: The action to detect the type of

        Returns:
            Optional[str]: The type of the action, or None if it's a regular action
        """
        if isinstance(action, ConditionalAction):
            return "conditional"
        elif isinstance(action, LoopAction):
            return "loop"
        elif isinstance(action, ErrorHandlingAction):
            return "error_handling"
        elif isinstance(action, TemplateAction):
            return "template"
        else:
            return None
