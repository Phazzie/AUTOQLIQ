"""Loop Action for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, WebDriverError
# Need ConditionalAction._evaluate_condition helper for 'while' loop
from src.core.actions.conditional_action import ConditionalAction

logger = logging.getLogger(__name__)


class LoopAction(ActionBase):
    """
    Action that repeats a sequence of nested actions based on a condition or count.

    Supported Loop Types:
        - 'count': Repeats fixed number of times. Context: `loop_index`, `loop_iteration`, `loop_total`.
        - 'for_each': Iterates list from context var `list_variable_name`. Context: `loop_item`, + index/iter/total.
        - 'while': Repeats while a condition (like ConditionalAction's) is true. Uses condition parameters.

    Attributes:
        loop_type (str): 'count', 'for_each', or 'while'.
        count (Optional[int]): Iterations for 'count'.
        list_variable_name (Optional[str]): Context variable name holding list for 'for_each'.
        loop_actions (List[IAction]): Actions to execute in each iteration.
        # Attributes for 'while' loop
        condition_type (Optional[str]): Condition type for 'while' loop.
        selector (Optional[str]): CSS selector for element conditions in 'while'.
        variable_name (Optional[str]): Context variable name for variable checks in 'while'.
        expected_value (Optional[str]): Value to compare against for variable checks in 'while'.
        script (Optional[str]): JavaScript code for JS conditions in 'while'.
    """
    action_type: str = "Loop"
    SUPPORTED_TYPES = ["count", "for_each", "while"]

    def __init__(self,
                 name: Optional[str] = None,
                 loop_type: str = "count",
                 count: Optional[int] = None,
                 list_variable_name: Optional[str] = None,
                 condition_type: Optional[str] = None,
                 selector: Optional[str] = None,
                 variable_name: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 script: Optional[str] = None,
                 loop_actions: Optional[List[IAction]] = None,
                 **kwargs):
        """Initialize a LoopAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(loop_type, str) or loop_type not in self.SUPPORTED_TYPES:
             raise ValidationError(f"loop_type must be one of {self.SUPPORTED_TYPES}.", field_name="loop_type")
        self.loop_type = loop_type
        self.count = None
        self.list_variable_name = None
        self.condition_type = condition_type
        self.selector = selector
        self.variable_name = variable_name
        self.expected_value = expected_value
        self.script = script

        if self.loop_type == "count":
             if count is None: raise ValidationError("'count' required.", field_name="count")
             try: self.count = int(count); assert self.count > 0
             except: raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(list_variable_name, str) or not list_variable_name:
                  raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
             self.list_variable_name = list_variable_name
        elif self.loop_type == "while":
             if not condition_type: raise ValidationError("'condition_type' required.", field_name="condition_type")
             # Detailed validation in validate()

        self.loop_actions = loop_actions or []
        if not isinstance(self.loop_actions, list) or not all(isinstance(a, IAction) for a in self.loop_actions):
             raise ValidationError("loop_actions must be list of IAction.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Loop '{self.name}' initialized with no actions.")

        logger.debug(f"{self.action_type} '{self.name}' initialized. Type: {self.loop_type}")


    def validate(self) -> bool:
        """Validate the configuration of the loop action and its nested actions."""
        super().validate()
        if self.loop_type not in self.SUPPORTED_TYPES:
            raise ValidationError(f"Unsupported loop_type: '{self.loop_type}'.", field_name="loop_type")

        if self.loop_type == "count":
            if not isinstance(self.count, int) or self.count <= 0: raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(self.list_variable_name, str) or not self.list_variable_name: raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
        elif self.loop_type == "while":
             if not self.condition_type or self.condition_type not in ConditionalAction.SUPPORTED_CONDITIONS: raise ValidationError(f"Invalid 'condition_type' for 'while'.", field_name="condition_type")
             if self.condition_type in ["element_present", "element_not_present"]:
                 if not isinstance(self.selector, str) or not self.selector: raise ValidationError("Selector required.", field_name="selector")
             elif self.condition_type == "variable_equals":
                 if not isinstance(self.variable_name, str) or not self.variable_name: raise ValidationError("variable_name required.", field_name="variable_name")
                 if self.expected_value is None: logger.warning(f"'while' loop '{self.name}' compares against None.")
                 elif not isinstance(self.expected_value, str): raise ValidationError("expected_value must be string or None.", field_name="expected_value")
             elif self.condition_type == "javascript_eval":
                  if not isinstance(self.script, str) or not self.script: raise ValidationError("Non-empty 'script' required.", field_name="script")

        if not isinstance(self.loop_actions, list): raise ValidationError("loop_actions must be list.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Validation: Loop '{self.name}' has no actions.")

        for i, action in enumerate(self.loop_actions):
            branch="loop_actions"; idx=i+1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def _evaluate_while_condition(self, driver: IWebDriver, context: Optional[Dict[str, Any]]) -> bool:
         """Evaluate the 'while' loop condition."""
         # Create temporary ConditionalAction to reuse its evaluation logic
         temp_cond = ConditionalAction(
              condition_type=self.condition_type or "", selector=self.selector,
              variable_name=self.variable_name, expected_value=self.expected_value, script=self.script
         )
         return temp_cond._evaluate_condition(driver, context) # Can raise ActionError(WebDriverError)

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the nested actions repeatedly based on the loop type."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Type: {self.loop_type}")
        try:
            self.validate()
            context = context or {}

            if not self.loop_actions:
                 logger.warning(f"Loop '{self.name}' has no actions. Skipping.")
                 return ActionResult.success("Loop completed (no actions).")

            iterations_executed = 0
            max_while_iterations = 1000 # Safety break

            # --- Use local runner helper for nested execution ---
            from src.core.workflow.runner import WorkflowRunner # Local import
            temp_runner = WorkflowRunner(driver, credential_repo, None, None) # No repo/stop needed

            if self.loop_type == "count":
                iterations_total = self.count or 0
                for i in range(iterations_total):
                    iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Iter {iteration_num}: "
                    logger.info(f"{iter_log_prefix}Starting.")
                    iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total})
                    # Execute block using helper - raises ActionError on failure
                    temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix)
                    iterations_executed = iteration_num
            elif self.loop_type == "for_each":
                 if not self.list_variable_name: raise ActionError("list_variable_name missing", self.name)
                 target_list = context.get(self.list_variable_name)
                 if not isinstance(target_list, list): return ActionResult.failure(f"Context var '{self.list_variable_name}' not list.")

                 iterations_total = len(target_list)
                 logger.info(f"Loop '{self.name}' starting 'for_each' over '{self.list_variable_name}' ({iterations_total} items).")
                 for i, item in enumerate(target_list):
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Item {iteration_num}: "
                      logger.info(f"{iter_log_prefix}Starting.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total, 'loop_item': item})
                      temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
            elif self.loop_type == "while":
                 logger.info(f"Loop '{self.name}' starting 'while' loop.")
                 i = 0
                 while i < max_while_iterations:
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' While Iter {iteration_num}: "
                      logger.debug(f"{iter_log_prefix}Evaluating condition...")
                      condition_met = self._evaluate_while_condition(driver, context) # Raises ActionError(WebDriverError)
                      if not condition_met: logger.info(f"{iter_log_prefix}Condition false. Exiting loop."); break
                      logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num})
                      temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
                      i += 1
                 else: raise ActionError(f"While loop exceeded max iterations ({max_while_iterations}).", self.name)
            else:
                raise ActionError(f"Loop execution not implemented for type: {self.loop_type}", self.name)

            logger.info(f"Loop '{self.name}' completed successfully after {iterations_executed} iterations.")
            return ActionResult.success(f"Loop completed {iterations_executed} iterations.")

        except (ValidationError, ActionError) as e:
            msg = f"Error during loop execution '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error in loop action '{self.name}'", self.name, self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))


    def to_dict(self) -> Dict[str, Any]:
        """Serialize the loop action and its nested actions."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "loop_type": self.loop_type,
            "loop_actions": serialize_actions(self.loop_actions),
        })
        if self.loop_type == "count": base_dict["count"] = self.count
        if self.loop_type == "for_each": base_dict["list_variable_name"] = self.list_variable_name
        if self.loop_type == "while":
             base_dict["condition_type"] = self.condition_type
             if self.condition_type in ["element_present", "element_not_present"]: base_dict["selector"] = self.selector
             elif self.condition_type == "variable_equals":
                  base_dict["variable_name"] = self.variable_name; base_dict["expected_value"] = self.expected_value
             elif self.condition_type == "javascript_eval": base_dict["script"] = self.script
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from the loop_actions list, recursively."""
        nested = []
        for action in self.loop_actions:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        detail = ""
        if self.loop_type == "count": detail = f"{self.count} times"
        elif self.loop_type == "for_each": detail = f"for each item in '{self.list_variable_name}'"
        elif self.loop_type == "while": detail = f"while {self.condition_type} (...)"
        action_count = len(self.loop_actions)
        return f"{self.action_type}: {self.name} ({detail}, {action_count} actions)"