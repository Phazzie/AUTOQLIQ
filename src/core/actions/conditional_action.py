################################################################################
"""Conditional Action (If/Else) for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, WebDriverError

logger = logging.getLogger(__name__)


class ConditionalAction(ActionBase):
    """
    Action that executes one of two branches based on a condition.

    Supported Conditions:
        - 'element_present'
        - 'element_not_present'
        - 'variable_equals'
        - 'javascript_eval' (Executes JS, expects truthy/falsy return)

    Attributes:
        condition_type (str): Type of condition.
        selector (Optional[str]): CSS selector for element conditions.
        variable_name (Optional[str]): Context variable name for variable checks.
        expected_value (Optional[str]): Value to compare against for variable checks.
        script (Optional[str]): JavaScript code for JS conditions.
        true_branch (List[IAction]): Actions if condition is true.
        false_branch (List[IAction]): Actions if condition is false.
    """
    action_type: str = "Conditional"
    SUPPORTED_CONDITIONS = ["element_present", "element_not_present", "variable_equals", "javascript_eval"]

    def __init__(self,
                 name: Optional[str] = None,
                 condition_type: str = "element_present",
                 selector: Optional[str] = None,
                 variable_name: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 script: Optional[str] = None,
                 true_branch: Optional[List[IAction]] = None,
                 false_branch: Optional[List[IAction]] = None,
                 **kwargs):
        """Initialize a ConditionalAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(condition_type, str): raise ValidationError("condition_type must be str.", field_name="condition_type")
        if selector is not None and not isinstance(selector, str): raise ValidationError("selector must be str or None.", field_name="selector")
        if variable_name is not None and not isinstance(variable_name, str): raise ValidationError("variable_name must be str or None.", field_name="variable_name")
        if expected_value is not None and not isinstance(expected_value, str): raise ValidationError("expected_value must be str or None.", field_name="expected_value")
        if script is not None and not isinstance(script, str): raise ValidationError("script must be str or None.", field_name="script")

        self.condition_type = condition_type
        self.selector = selector
        self.variable_name = variable_name
        self.expected_value = expected_value
        self.script = script
        self.true_branch = true_branch or []
        self.false_branch = false_branch or []

        if not isinstance(self.true_branch, list) or not all(isinstance(a, IAction) for a in self.true_branch):
             raise ValidationError("true_branch must be list of IAction.", field_name="true_branch")
        if not isinstance(self.false_branch, list) or not all(isinstance(a, IAction) for a in self.false_branch):
             raise ValidationError("false_branch must be list of IAction.", field_name="false_branch")
        try: self.validate()
        except ValidationError as e: raise e from e

        logger.debug(f"{self.action_type} '{self.name}' initialized. Condition: {self.condition_type}")


    def validate(self) -> bool:
        """Validate the configuration of the conditional action and its nested actions."""
        super().validate()
        if self.condition_type not in self.SUPPORTED_CONDITIONS:
            raise ValidationError(f"Unsupported condition_type: '{self.condition_type}'. Supported: {self.SUPPORTED_CONDITIONS}", field_name="condition_type")

        if self.condition_type in ["element_present", "element_not_present"]:
            if not isinstance(self.selector, str) or not self.selector:
                raise ValidationError("Selector required for element conditions.", field_name="selector")
        elif self.condition_type == "variable_equals":
            if not isinstance(self.variable_name, str) or not self.variable_name:
                 raise ValidationError("variable_name required.", field_name="variable_name")
            if self.expected_value is None: logger.warning(f"Cond '{self.name}' compares against None.")
            elif not isinstance(self.expected_value, str): raise ValidationError("expected_value must be string or None.", field_name="expected_value")
        elif self.condition_type == "javascript_eval":
             if not isinstance(self.script, str) or not self.script:
                  raise ValidationError("Non-empty 'script' required.", field_name="script")

        for i, action in enumerate(self.true_branch):
            branch = "true_branch"; idx_disp = i + 1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx_disp} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx_disp} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e
        for i, action in enumerate(self.false_branch):
            branch = "false_branch"; idx_disp = i + 1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx_disp} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx_disp} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def _evaluate_condition(self, driver: IWebDriver, context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate the condition based on the driver state and context."""
        context = context or {}
        result = False
        try:
            if self.condition_type == "element_present":
                if not self.selector: raise ActionError("Selector missing.", self.name)
                logger.debug(f"Evaluating: element_present ('{self.selector}')?")
                result = driver.is_element_present(self.selector)
            elif self.condition_type == "element_not_present":
                 if not self.selector: raise ActionError("Selector missing.", self.name)
                 logger.debug(f"Evaluating: element_not_present ('{self.selector}')?")
                 result = not driver.is_element_present(self.selector)
            elif self.condition_type == "variable_equals":
                 if not self.variable_name: raise ActionError("variable_name missing.", self.name)
                 actual_value = context.get(self.variable_name)
                 actual_str = str(actual_value) if actual_value is not None else None
                 expected_str = str(self.expected_value) if self.expected_value is not None else None
                 logger.debug(f"Evaluating: variable_equals ('{self.variable_name}' == '{self.expected_value}')? Actual: '{actual_str}'")
                 result = actual_str == expected_str
            elif self.condition_type == "javascript_eval":
                 if not self.script: raise ActionError("Script missing.", self.name)
                 logger.debug(f"Evaluating: javascript_eval ('{self.script[:50]}...')?")
                 script_result = driver.execute_script(self.script) # Raises WebDriverError
                 logger.debug(f"JS script returned: {script_result} (type: {type(script_result).__name__})")
                 result = bool(script_result)
            else:
                raise ActionError(f"Condition evaluation not implemented for type: {self.condition_type}", self.name)
        except WebDriverError as e:
             raise ActionError(f"WebDriver error evaluating condition: {e}", action_name=self.name, cause=e) from e
        logger.debug(f"Condition result: {result}")
        return result


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute either the true or false branch based on the condition."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Evaluating condition...")
        try:
            self.validate()
            condition_result = self._evaluate_condition(driver, context) # Can raise ActionError(WebDriverError)
            logger.info(f"Condition '{self.condition_type}' evaluated to: {condition_result}")

            branch_to_execute = self.true_branch if condition_result else self.false_branch
            branch_name = "true" if condition_result else "false"

            if not branch_to_execute:
                 logger.info(f"No actions in '{branch_name}' branch of '{self.name}'.")
                 return ActionResult.success(f"Condition {condition_result}, '{branch_name}' branch empty.")

            logger.info(f"Executing '{branch_name}' branch of '{self.name}'...")

            # --- Execute Chosen Branch ---
            # This action executes its children. Use local runner helper.
            from src.core.workflow.workflow_runner import WorkflowRunner
            temp_runner = WorkflowRunner(driver)

            # Pass the *current* context down. Conditional branches don't create new scope.
            branch_results = temp_runner._execute_actions(branch_to_execute, context or {}, credential_repo=credential_repo, workflow_name=self.name, log_prefix=f"{branch_name}: ")
            # If _execute_actions completes without raising ActionError, the branch succeeded.

            logger.info(f"Successfully executed '{branch_name}' branch of '{self.name}'.")
            final_msg = f"Condition {condition_result}, '{branch_name}' branch ({len(branch_results)} actions) executed."
            return ActionResult.success(final_msg)

        except (ValidationError, ActionError) as e: # Catch errors from validate, _evaluate, or nested execute
            msg = f"Error during conditional execution '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e: # Catch unexpected errors
            error = ActionError(f"Unexpected error in conditional '{self.name}'", self.name, self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the conditional action and its branches."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "condition_type": self.condition_type,
            "true_branch": serialize_actions(self.true_branch),
            "false_branch": serialize_actions(self.false_branch),
        })
        if self.condition_type in ["element_present", "element_not_present"] and self.selector: base_dict["selector"] = self.selector
        elif self.condition_type == "variable_equals":
             if self.variable_name: base_dict["variable_name"] = self.variable_name
             base_dict["expected_value"] = self.expected_value
        elif self.condition_type == "javascript_eval" and self.script: base_dict["script"] = self.script
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from both branches, recursively."""
        nested = []
        for action in self.true_branch + self.false_branch:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        condition_detail = ""
        if self.condition_type in ["element_present", "element_not_present"]: condition_detail = f"selector='{self.selector}'"
        elif self.condition_type == "variable_equals": condition_detail = f"var[{self.variable_name}] == '{self.expected_value}'"
        elif self.condition_type == "javascript_eval": condition_detail = f"script='{self.script[:20]}...'" if self.script else "script=''"
        true_count = len(self.true_branch); false_count = len(self.false_branch)
        return f"{self.action_type}: {self.name} (if {self.condition_type} {condition_detail} ? {true_count} : {false_count})"

################################################################################