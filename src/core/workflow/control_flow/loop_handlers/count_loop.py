"""Count loop handler implementation.

This module implements the handler for count-based loops.
"""

import logging
from typing import Dict, Any, List

from src.core.actions.loop_action import LoopAction
from src.core.exceptions import ActionError
from src.core.workflow.control_flow.loop_handlers.base import BaseLoopHandler

logger = logging.getLogger(__name__)


class CountLoopHandler(BaseLoopHandler):
    """Handler for count-based loops."""
    
    def handle_loop(self, action: LoopAction, context: Dict[str, Any],
                  workflow_name: str, log_prefix: str) -> int:
        """
        Handle a count-based loop.
        
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
        count = action.count
        if count <= 0:
            return 0
        
        logger.info(f"{log_prefix}Starting count-based loop with {count} iterations.")
        
        for i in range(count):
            iteration_num = i + 1
            iter_log_prefix = f"{log_prefix}Iteration {iteration_num}/{count}: "
            logger.info(f"{iter_log_prefix}Starting iteration.")
            
            # Create a copy of the context with loop variables
            iter_context = context.copy()
            iter_context.update({
                'loop_index': i, 
                'loop_iteration': iteration_num, 
                'loop_total': count
            })
            
            # Execute the loop body
            self.execute_actions(
                action.loop_actions, 
                iter_context, 
                workflow_name, 
                iter_log_prefix
            )
        
        return count
