"""Action executor for workflow execution.

This module provides the ActionExecutor class for executing individual actions.
"""

import logging
from typing import Dict, Any, Optional

from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, ValidationError, WorkflowError

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes individual actions.
    
    Handles validation, execution, and error handling for individual actions.
    """
    
    def __init__(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository] = None):
        """
        Initialize the action executor.
        
        Args:
            driver: The web driver instance
            credential_repo: Optional credential repository
        """
        self.driver = driver
        self.credential_repo = credential_repo
    
    def execute_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
        """
        Execute a single action.
        
        Args:
            action: The action to execute
            context: The execution context
            
        Returns:
            ActionResult: The result of the action execution
        """
        action_display_name = f"{action.name} ({action.action_type})"
        logger.debug(f"Executing action: {action_display_name}")
        
        try:
            # Validate the action
            action.validate()
            
            # Execute the action
            result = action.execute(self.driver, self.credential_repo, context)
            
            # Validate the result
            if not isinstance(result, ActionResult):
                logger.error(
                    f"Action '{action_display_name}' did not return ActionResult (got {type(result).__name__})."
                )
                return ActionResult.failure(
                    f"Action '{action.name}' implementation error: Invalid return type."
                )
            
            # Log the result
            if not result.is_success():
                logger.warning(f"Action '{action_display_name}' returned failure: {result.message}")
            else:
                logger.debug(f"Action '{action_display_name}' returned success.")
            
            return result
            
        except ValidationError as e:
            logger.error(f"Validation failed for action '{action_display_name}': {e}")
            return ActionResult.failure(f"Action validation failed: {e}")
        except ActionError as e:
            logger.error(f"ActionError during execution of action '{action_display_name}': {e}")
            return ActionResult.failure(f"Action execution error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected exception during execution of action '{action_display_name}'")
            wrapped_error = ActionError(
                f"Unexpected exception: {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            )
            return ActionResult.failure(str(wrapped_error))
