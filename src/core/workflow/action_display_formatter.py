"""Action display formatter module for AutoQliq.

Provides functionality for formatting action display names.
"""

import logging
from typing import Dict, Any

from src.core.interfaces import IAction

logger = logging.getLogger(__name__)


def format_action_display_name(
    current_action: IAction,
    log_prefix: str,
    step_number: int
) -> str:
    """
    Format an action display name.
    
    Args:
        current_action: The action to format the display name for
        log_prefix: The prefix for log messages
        step_number: The step number
        
    Returns:
        str: The formatted action display name
    """
    return (
        f"{current_action.name} ({current_action.action_type}, {log_prefix}Step {step_number})"
    )
