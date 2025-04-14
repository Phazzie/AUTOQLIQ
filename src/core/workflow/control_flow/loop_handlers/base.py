"""Base interface for loop handlers.

This module defines the base interface for loop handlers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.actions.loop_action import LoopAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase

logger = logging.getLogger(__name__)


class BaseLoopHandler(ControlFlowHandlerBase):
    """Base class for loop handlers."""
    
    @abstractmethod
    def handle_loop(self, action: LoopAction, context: Dict[str, Any],
                  workflow_name: str, log_prefix: str) -> int:
        """
        Handle a specific type of loop.
        
        Args:
            action: The LoopAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages
            
        Returns:
            int: Number of iterations executed
            
        Raises:
            ActionError: If an error occurs during handling
        """
        pass
