"""While loop handler implementation.

This module implements the handler for while loops.
"""

import logging
from typing import Dict, Any, List

from src.core.actions.loop_action import LoopAction
from src.core.exceptions import ActionError, WorkflowError
from src.core.workflow.control_flow.loop_handlers.base import BaseLoopHandler

logger = logging.getLogger(__name__)


class WhileLoopHandler(BaseLoopHandler):
    """Handler for while loops."""
    
    def handle_loop(self, action: LoopAction, context: Dict[str, Any],
                  workflow_name: str, log_prefix: str) -> int:
        """
        Handle a while loop.
        
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
        logger.info(f"{log_prefix}Starting 'while' loop.")
        max_while = action.max_iterations or 100  # Default max to prevent infinite loops
        
        i = 0
        while i < max_while:
            iteration_num = i + 1
            iter_log_prefix = f"{log_prefix}Iteration {iteration_num}: "
            
            # Check stop event if available
            if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.is_set():
                raise WorkflowError("Stop requested during while loop.")
            
            # Evaluate the condition
            condition_met = action._evaluate_while_condition(self.driver, context)
            
            if not condition_met:
                logger.info(f"{iter_log_prefix}Condition false. Exiting loop.")
                break
            
            logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
            
            # Create a copy of the context with loop variables
            iter_context = context.copy()
            iter_context.update({
                'loop_index': i, 
                'loop_iteration': iteration_num
            })
            
            # Execute the loop body
            self.execute_actions(
                action.loop_actions, 
                iter_context, 
                workflow_name, 
                iter_log_prefix
            )
            i += 1
        else:
            # Loop reached max iterations without condition becoming false
            raise ActionError(
                f"While loop exceeded max iterations ({max_while}).",
                action_name=action.name
            )
        
        return i
