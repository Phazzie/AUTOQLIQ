"""Action type detector module for AutoQliq.

Provides functionality for detecting action types.
"""

import logging
from typing import Dict, Any, Optional

from src.core.interfaces import IAction
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction

logger = logging.getLogger(__name__)


def detect_action_type(action: IAction) -> Optional[str]:
    """
    Detect the type of an action.
    
    Args:
        action: The action to detect the type of
        
    Returns:
        Optional[str]: The type of the action, or None if not a special type
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


def get_handler_prefix(action_type: str, step_number: int, log_prefix: str) -> str:
    """
    Get the prefix for a handler log message.
    
    Args:
        action_type: The type of the action
        step_number: The step number
        log_prefix: The prefix for log messages
        
    Returns:
        str: The prefix for the handler log message
    """
    if action_type == "conditional":
        return f"{log_prefix}Cond {step_number}: "
    elif action_type == "loop":
        return f"{log_prefix}Loop {step_number}: "
    elif action_type == "error_handling":
        return f"{log_prefix}ErrH {step_number}: "
    elif action_type == "template":
        return f"{log_prefix}Tmpl {step_number}: "
    else:
        return f"{log_prefix}Step {step_number}: "
