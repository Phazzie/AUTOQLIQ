"""Error handling handler implementation.

This module implements the handler for error handling actions.
"""

import logging
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase

logger = logging.getLogger(__name__)


class ErrorHandlingHandler(ControlFlowHandlerBase):
    """Handler for ErrorHandlingAction (Try/Catch) execution."""
    
    def handle(self, action: IAction, context: Dict[str, Any], 
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle an ErrorHandlingAction by executing its try block and catch block if needed.
        
        Args:
            action: The ErrorHandlingAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages
            
        Returns:
            ActionResult: The result of handling the action
            
        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: If action is not an ErrorHandlingAction
        """
        if not isinstance(action, ErrorHandlingAction):
            raise WorkflowError(f"ErrorHandlingHandler received non-ErrorHandlingAction: {type(action).__name__}")
        
        logger.info(f"{log_prefix}Entering 'try' block.")
        original_error: Optional[Exception] = None
        
        try:
            # Execute try block
            self.execute_actions(action.try_actions, context, workflow_name, f"{log_prefix}Try: ")
            logger.info(f"{log_prefix}'try' block succeeded.")
            return ActionResult.success("Try block succeeded.")
            
        except Exception as try_error:
            original_error = try_error
            logger.warning(f"{log_prefix}'try' block failed: {try_error}", exc_info=False)
            
            if not action.catch_actions:
                logger.info(f"{log_prefix}No 'catch' block defined, re-raising error.")
                raise
            
            logger.info(f"{log_prefix}Entering 'catch' block.")
            
            try:
                # Add error information to context for catch block
                catch_context = context.copy()
                catch_context.update({
                    'error': str(try_error),
                    'error_type': type(try_error).__name__,
                    'try_block_error_message': str(try_error),
                    'try_block_error_type': type(try_error).__name__
                })
                
                # Execute catch block
                catch_results = self.execute_actions(
                    action.catch_actions, catch_context, workflow_name, f"{log_prefix}Catch: "
                )
                
                # Check if catch block succeeded
                all_success = all(result.is_success() for result in catch_results)
                if all_success:
                    logger.info(f"{log_prefix}'catch' block succeeded, error handled.")
                    return ActionResult.success(
                        f"Error handled by catch block: {str(try_error)}"
                    )
                else:
                    # If we got here with failures in catch block, we must be using CONTINUE_ON_ERROR
                    logger.warning(f"{log_prefix}'catch' block had failures.")
                    return ActionResult.failure(
                        f"Catch block had failures after try error: {str(try_error)}"
                    )
                    
            except Exception as catch_error:
                logger.error(f"{log_prefix}'catch' block failed: {catch_error}", exc_info=True)
                
                # Raise new error indicating catch failure
                raise ActionError(
                    f"'catch' block failed after 'try' error ({try_error}): {catch_error}",
                    action_name=action.name,
                    cause=catch_error
                ) from catch_error
