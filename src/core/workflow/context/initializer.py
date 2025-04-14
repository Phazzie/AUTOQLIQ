"""Context initializer module for AutoQliq.

Provides functionality for initializing execution contexts.
"""

import logging
from typing import Dict, Any
import datetime

logger = logging.getLogger(__name__)


def initialize_context() -> Dict[str, Any]:
    """
    Initialize a new execution context.
    
    Returns:
        Dict[str, Any]: The initialized context
    """
    # Create a new context with default values
    context = {
        # System variables
        "system": {
            "start_time": datetime.datetime.now().isoformat(),
            "execution_id": _generate_execution_id(),
        },
        # User variables (to be populated during execution)
        "variables": {},
        # Execution state
        "state": {
            "had_action_failures": False,
            "current_step": 0,
            "total_steps": 0,
        }
    }
    
    return context


def _generate_execution_id() -> str:
    """
    Generate a unique execution ID.
    
    Returns:
        str: The generated execution ID
    """
    # Generate a unique ID based on timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"exec-{timestamp}"
