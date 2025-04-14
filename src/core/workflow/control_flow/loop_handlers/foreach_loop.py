"""For-each loop handler implementation.

This module implements the handler for for-each loops.
"""

import logging
from typing import Dict, Any, List

from src.core.actions.loop_action import LoopAction
from src.core.exceptions import ActionError
from src.core.workflow.control_flow.loop_handlers.base import BaseLoopHandler

logger = logging.getLogger(__name__)


class ForEachLoopHandler(BaseLoopHandler):
    """Handler for for-each loops."""
    
    def handle_loop(self, action: LoopAction, context: Dict[str, Any],
                  workflow_name: str, log_prefix: str) -> int:
        """
        Handle a for-each loop.
        
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
        if not action.list_variable_name:
            raise ActionError("list_variable_name missing", action.name)
        
        target_list = context.get(action.list_variable_name)
        if not isinstance(target_list, list):
            raise ActionError(
                f"Context var '{action.list_variable_name}' not list.", 
                action.name
            )
        
        iterations_total = len(target_list)
        logger.info(
            f"{log_prefix}Starting 'for_each' over '{action.list_variable_name}' "
            f"({iterations_total} items)."
        )
        
        for i, item in enumerate(target_list):
            iteration_num = i + 1
            iter_log_prefix = f"{log_prefix}Item {iteration_num}: "
            logger.info(f"{iter_log_prefix}Starting.")
            
            # Create a copy of the context with loop variables
            iter_context = context.copy()
            iter_context.update({
                'loop_index': i, 
                'loop_iteration': iteration_num, 
                'loop_total': iterations_total, 
                'loop_item': item
            })
            
            # Execute the loop body
            self.execute_actions(
                action.loop_actions, 
                iter_context, 
                workflow_name, 
                iter_log_prefix
            )
        
        return iterations_total
