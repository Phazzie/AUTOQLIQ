```python
import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, WorkflowError
# Import JavaScriptCondition specifically, as it's a likely condition type
from src.core.actions.javascript_condition import JavaScriptCondition

logger = logging.getLogger(__name__)

# Define a maximum number of iterations to prevent accidental infinite loops
MAX_WHILE_ITERATIONS = 1000

class WhileLoopAction(ActionBase):
    """
    Action that repeatedly executes a block of actions while a condition action evaluates to true.

    Attributes:
        condition_action (IAction): An action (like JavaScriptCondition) whose result.data
                                    is evaluated as a boolean condition.
        loop_actions (List[IAction]): The list of actions to execute in each loop iteration.
        max_iterations (int): A safety limit for the maximum number of iterations.
        action_type (str): Static type name ("WhileLoop").
    """
    action_type: str = "WhileLoop"

    def __init__(self,
                 name: Optional[str] = None,
                 condition_action: Optional[IAction] = None,
                 loop_actions: Optional[List[IAction]] = None,
                 max_iterations: int = MAX_WHILE_ITERATIONS,
                 **kwargs):
        """Initialize WhileLoopAction."""
        super().__init__(name, **kwargs)
        if condition_action is None or not isinstance(condition_action, IAction):
            raise ValidationError("The 'condition_action' parameter is required and must be a valid Action.",
                                  action_name=self.name, action_type=self.action_type, field_name="condition_action")
        # Basic validation for loop_actions list structure
        if loop_actions is None:
             loop_actions = [] # Default to empty list if None
        if not isinstance(loop_actions, list):
             raise ValidationError("The 'loop_actions' parameter must be a list of actions.",
                                   action_name=self.name, action_type=self.action_type, field_name="loop_actions")
        if not all(isinstance(act, IAction) for act in loop_actions):
             raise ValidationError("All items in 'loop_actions' must be valid Action objects.",
                                   action_name=self.name, action_type=self.action_type, field_name="loop_actions")

        self.condition_action = condition_action
        self.loop_actions = loop_actions
        self.max_iterations = max_iterations if isinstance(max_iterations, int) and max_iterations > 0 else MAX_WHILE_ITERATIONS
        logger.debug(f"Initialized {self.action_type} action (Name: {self.name}) with {len(self.loop_actions)} loop actions.")

    def validate(self) -> bool:
        """Validate the configuration of the while loop action and its nested actions."""
        super().validate() # Base validation (name)
        if not isinstance(self.condition_action, IAction):
            raise ValidationError("The 'condition_action' must be a valid Action instance.",
                                  action_name=self.name, action_type=self.action_type, field_name="condition_action")
        try:
            self.condition_action.validate() # Validate the condition action itself
        except ValidationError as e:
            raise ValidationError(f"Validation failed for nested condition action '{self.condition_action.name}': {e}",
                                  action_name=self.name, action_type=self.action_type, field_name="condition_action") from e

        if not isinstance(self.loop_actions, list):
             raise ValidationError("'loop_actions' must be a list.",
                                   action_name=self.name, action_type=self.action_type, field_name="loop_actions")
        if not isinstance(self.max_iterations, int) or self.max_iterations <= 0:
             raise ValidationError("'max_iterations' must be a positive integer.",
                                   action_name=self.name, action_type=self.action_type, field_name="max_iterations")

        # Validate nested loop actions
        for i, action in enumerate(self.loop_actions):
            if not isinstance(action, IAction):
                raise ValidationError(f"Item at index {i} in 'loop_actions' is not a valid Action.",
                                      action_name=self.name, action_type=self.action_type, field_name=f"loop_actions[{i}]")
            try:
                action.validate()
            except ValidationError as e:
                raise ValidationError(f"Validation failed for nested loop action '{action.name}' (index {i}): {e}",
                                      action_name=self.name, action_type=self.action_type, field_name=f"loop_actions[{i}]") from e

        logger.debug(f"Validation successful for {self.action_type} action (Name: {self.name})")
        return True

    def _evaluate_condition(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository], context: Dict[str, Any]) -> bool:
        """Evaluates the condition action and returns its boolean result."""
        logger.debug(f"Evaluating condition action '{self.condition_action.name}' for WhileLoop '{self.name}'.")
        try:
            # Execute the condition action, passing context
            condition_result = self.condition_action.execute(driver, credential_repo, context)

            if not condition_result.is_success():
                # If the condition action itself fails, the loop cannot proceed safely.
                raise ActionError(f"Condition action '{self.condition_action.name}' failed: {condition_result.message}",
                                  action_name=self.name, action_type=self.action_type)

            # Expect the boolean result to be in the 'data' field of the ActionResult
            condition_value = condition_result.data
            if not isinstance(condition_value, bool):
                 raise ActionError(f"Condition action '{self.condition_action.name}' did not return a boolean result in its data field (got {type(condition_value).__name__}).",
                                   action_name=self.name, action_type=self.action_type)

            logger.debug(f"Condition action '{self.condition_action.name}' evaluated to: {condition_value}")
            return condition_value

        except (ActionError, ValidationError, WebDriverError) as e:
            # Propagate errors from condition evaluation
            logger.error(f"Error evaluating condition action '{self.condition_action.name}' in WhileLoop '{self.name}': {e}")
            raise ActionError(f"Error evaluating condition: {e}",
                              action_name=self.name, action_type=self.action_type, cause=e) from e
        except Exception as e:
            logger.exception(f"Unexpected error evaluating condition action '{self.condition_action.name}' in WhileLoop '{self.name}'.")
            raise ActionError(f"Unexpected error evaluating condition: {e}",
                              action_name=self.name, action_type=self.action_type, cause=e) from e


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the nested actions repeatedly while the condition is true."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Max iterations: {self.max_iterations}")
        context = context or {}
        iterations_executed = 0
        log_prefix = f"WhileLoop '{self.name}': "

        try:
            self.validate()

            if not self.loop_actions:
                 logger.warning(f"{log_prefix}Loop has no actions. Skipping.")
                 return ActionResult.success("Loop completed (no actions).")

            # --- Use local runner helper for nested execution ---
            # Avoid circular import by importing locally
            from src.core.workflow.runner import WorkflowRunner, ErrorHandlingStrategy
            # Create a temporary runner for the loop body.
            # It inherits driver, repos, but crucially *not* the stop_event from the main runner.
            # Error strategy within the loop body could be configurable, but default to STOP_ON_ERROR for now.
            # If the loop *itself* needs to be stoppable, the main runner's check is sufficient.
            temp_runner = WorkflowRunner(driver, credential_repo, None, None, ErrorHandlingStrategy.STOP_ON_ERROR)

            while iterations_executed < self.max_iterations:
                iteration_num = iterations_executed + 1
                iter_log_prefix = f"{log_prefix}Iter {iteration_num}: "

                # Check stop event *before* condition evaluation (using context if passed down)
                stop_event = context.get('_stop_event_runner') # Check for stop event passed by main runner
                if stop_event and stop_event.is_set():
                    logger.info(f"{log_prefix}Stop requested before iteration {iteration_num}.")
                    raise WorkflowError("Workflow execution stopped by request during while loop.")

                logger.debug(f"{iter_log_prefix}Evaluating condition...")
                condition_met = self._evaluate_condition(driver, credential_repo, context) # Raises ActionError on failure

                if not condition_met:
                    logger.info(f"{iter_log_prefix}Condition evaluated to false. Exiting loop.")
                    break

                logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                # Create a context for this iteration, including loop index/iteration count
                iter_context = context.copy()
                iter_context.update({'loop_index': iterations_executed, 'loop_iteration': iteration_num})

                # Execute the block of actions using the temporary runner
                # This will raise ActionError if any action inside fails (due to STOP_ON_ERROR strategy)
                temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix)

                iterations_executed += 1

            else:
                # This block executes if the loop finished due to max_iterations
                if iterations_executed == self.max_iterations:
                    logger.warning(f"{log_prefix}Loop terminated after reaching the maximum of {self.max_iterations} iterations.")
                    # Consider if this should be a failure or just a warning. Treating as success with warning.
                    return ActionResult.success(f"Loop finished after reaching max {self.max_iterations} iterations.", data={'iterations_executed': iterations_executed})

            # Loop finished normally (condition became false)
            logger.info(f"{log_prefix}Loop completed successfully after {iterations_executed} iterations.")
            return ActionResult.success(f"Loop completed after {iterations_executed} iterations.", data={'iterations_executed': iterations_executed})

        except (ValidationError, ActionError, WorkflowError) as e:
            # Catch errors from validation, condition evaluation, or nested action execution
            msg = f"Error during {self.action_type} execution '{self.name}': {e}"
            logger.error(msg, exc_info=False) # Log error, but avoid duplicate stack trace if ActionError
            # Re-raise ActionError/WorkflowError to be handled by the main runner
            raise e
        except Exception as e:
            # Catch unexpected errors
            error = ActionError(f"Unexpected error in {self.action_type} action '{self.name}'",
                                action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            # Raise ActionError for unexpected issues
            raise error from e

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        # Recursively serialize nested actions
        base_dict["condition_action"] = self.condition_action.to_dict() if self.condition_action else None
        base_dict["loop_actions"] = [action.to_dict() for action in self.loop_actions]
        base_dict["max_iterations"] = self.max_iterations
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return nested condition and loop actions."""
        nested = []
        if self.condition_action:
            nested.append(self.condition_action)
        nested.extend(self.loop_actions)
        return nested

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"condition={self.condition_action.name if self.condition_action else 'None'}, "
                f"actions=[{len(self.loop_actions)} actions], max_iter={self.max_iterations})")

# STATUS: COMPLETE ✓
```
