"""Error Handling Action (Try/Catch) for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, AutoQliqError

logger = logging.getLogger(__name__)


class ErrorHandlingAction(ActionBase):
    """
    Action that attempts to execute a sequence of actions ('try') and
    optionally executes another sequence ('catch') if an error occurs in 'try'.

    If an error occurs in the 'try' block:
    - If a 'catch' block exists, it's executed. The ErrorHandlingAction SUCCEEDS
      if the 'catch' block completes without error (error is considered handled).
      It FAILS if the 'catch' block itself fails.
    - If no 'catch' block exists, the ErrorHandlingAction FAILS immediately,
      propagating the original error context.

    Attributes:
        try_actions (List[IAction]): Actions to attempt execution.
        catch_actions (List[IAction]): Actions to execute if an error occurs in try_actions.
        action_type (str): Static type name ("ErrorHandling").
    """
    action_type: str = "ErrorHandling"

    def __init__(self,
                 name: Optional[str] = None,
                 try_actions: Optional[List[IAction]] = None,
                 catch_actions: Optional[List[IAction]] = None,
                 **kwargs):
        """
        Initialize an ErrorHandlingAction.

        Args:
            name: Descriptive name for the action. Defaults to "ErrorHandling".
            try_actions: List of IAction objects for the 'try' block.
            catch_actions: Optional list of IAction objects for the 'catch' block.
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        self.try_actions = try_actions or []
        self.catch_actions = catch_actions or []

        # Initial validation
        if not isinstance(self.try_actions, list) or not all(isinstance(a, IAction) for a in self.try_actions):
             raise ValidationError("try_actions must be a list of IAction objects.", field_name="try_actions")
        if not isinstance(self.catch_actions, list) or not all(isinstance(a, IAction) for a in self.catch_actions):
             raise ValidationError("catch_actions must be a list of IAction objects.", field_name="catch_actions")
        if not self.try_actions:
            logger.warning(f"ErrorHandling action '{self.name}' initialized with no actions in 'try' block.")

        logger.debug(f"{self.action_type} '{self.name}' initialized.")

    def validate(self) -> bool:
        """Validate the configuration and nested actions."""
        super().validate()

        # Validate nested actions
        if not self.try_actions: logger.warning(f"Validation: ErrorHandling '{self.name}' has no try_actions.")
        for i, action in enumerate(self.try_actions):
            branch = "try_actions"
            if not isinstance(action, IAction): raise ValidationError(f"Item {i+1} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {i+1} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        for i, action in enumerate(self.catch_actions):
            branch = "catch_actions"
            if not isinstance(action, IAction): raise ValidationError(f"Item {i+1} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {i+1} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the 'try' actions, running 'catch' actions if an error occurs."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}).")
        original_error: Optional[Exception] = None
        original_failure_result: Optional[ActionResult] = None
        try_block_success = True

        # --- Execute Try Block ---
        logger.debug(f"Entering 'try' block of '{self.name}'.")
        for i, action in enumerate(self.try_actions):
            action_display = f"{action.name} ({action.action_type}, Step {i+1} in 'try')"
            logger.debug(f"Executing nested action: {action_display}")
            try:
                # Execute nested action, passing context
                nested_result = action.execute(driver, credential_repo, context)
                if not nested_result.is_success():
                    error_msg = f"Nested action '{action_display}' failed: {nested_result.message}"
                    logger.warning(error_msg) # Warning as it might be caught
                    original_failure_result = nested_result # Store the failed result
                    try_block_success = False
                    break
                logger.debug(f"Nested action '{action_display}' succeeded.")
            except Exception as e:
                error_msg = f"Exception in nested action '{action_display}': {e}"
                logger.error(error_msg, exc_info=True)
                original_error = e # Store the original exception
                try_block_success = False
                break

        # --- Execute Catch Block (if error occurred and catch exists) ---
        if not try_block_success:
            fail_reason = str(original_error or original_failure_result.message)
            logger.warning(f"'try' block of '{self.name}' failed. Reason: {fail_reason}")

            if not self.catch_actions:
                 logger.warning(f"No 'catch' block defined for '{self.name}'. Propagating failure.")
                 fail_msg = f"'try' block failed and no 'catch' block defined. Original error: {fail_reason}"
                 # Return failure, preserving original failure if possible
                 return ActionResult.failure(fail_msg)
            else:
                logger.info(f"Executing 'catch' block of '{self.name}' due to error.")
                catch_context = (context or {}).copy()
                # Add error details to context for catch block
                catch_context['try_block_error_message'] = fail_reason
                catch_context['try_block_error_type'] = type(original_error).__name__ if original_error else "ActionFailure"

                for i, catch_action in enumerate(self.catch_actions):
                     action_display = f"{catch_action.name} ({catch_action.action_type}, Step {i+1} in 'catch')"
                     logger.debug(f"Executing catch action: {action_display}")
                     try:
                         catch_result = catch_action.execute(driver, credential_repo, catch_context)
                         if not catch_result.is_success():
                              error_msg = f"Catch action '{action_display}' failed: {catch_result.message}"
                              logger.error(error_msg)
                              # If catch block fails, the whole action fails definitively
                              return ActionResult.failure(f"Original error occurred AND 'catch' block failed. Catch failure: {error_msg}")
                         logger.debug(f"Catch action '{action_display}' succeeded.")
                     except Exception as catch_e:
                          error_msg = f"Exception in catch action '{action_display}': {catch_e}"
                          logger.error(error_msg, exc_info=True)
                          # Exception in catch block also means overall failure
                          return ActionResult.failure(f"Original error occurred AND 'catch' block raised exception. Catch exception: {error_msg}")

                # If catch block completed without errors
                logger.info(f"'catch' block of '{self.name}' executed successfully after handling error.")
                # The error was "handled" by the catch block
                return ActionResult.success(f"Error handled by 'catch' block in '{self.name}'.")

        # If try block succeeded without errors
        logger.info(f"'try' block of '{self.name}' executed successfully.")
        return ActionResult.success(f"'{self.name}' executed successfully (no errors).")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error handling action and its branches."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "try_actions": serialize_actions(self.try_actions),
            "catch_actions": serialize_actions(self.catch_actions),
        })
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from both try and catch branches, recursively."""
        nested = []
        for action in self.try_actions + self.catch_actions:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        try_count = len(self.try_actions)
        catch_count = len(self.catch_actions)
        return f"{self.action_type}: {self.name} (Try: {try_count} actions, Catch: {catch_count} actions)"