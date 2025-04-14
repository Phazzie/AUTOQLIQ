"""Stop event checker module for AutoQliq.

Provides functionality for checking if a workflow should be stopped.
"""

import logging
import threading

from src.core.exceptions import WorkflowError

logger = logging.getLogger(__name__)


def check_stop_event(stop_event: threading.Event) -> None:
    """
    Check if a workflow should be stopped.
    
    Args:
        stop_event: The stop event to check
        
    Raises:
        WorkflowError: If the stop event is set
    """
    if stop_event and stop_event.is_set():
        raise WorkflowError("Workflow execution stopped by request")
