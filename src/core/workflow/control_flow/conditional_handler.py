"""Conditional handler implementation.

This module implements the handler for conditional actions.
"""

import logging
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError
from src.core.actions.conditional_action import ConditionalAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.interfaces import IConditionalActionHandler
from src.core.workflow.control_flow.utils import evaluate_action_results

logger = logging.getLogger(__name__)


class ConditionalHandler(ControlFlowHandlerBase, IConditionalActionHandler):
    """Handler for ConditionalAction (If/Else) execution."""

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition.

        Args:
            condition: The condition to evaluate
            context: The execution context

        Returns:
            bool: The result of evaluating the condition
        """
        # This is a simplified implementation
        # In a real implementation, we would parse and evaluate the condition
        if not condition:
            return False

        # For now, just check if the condition is a variable in the context
        if condition in context:
            return bool(context[condition])

        # Otherwise, try to evaluate it as a Python expression
        try:
            # Create a safe evaluation context with only the context variables
            eval_context = {**context}
            return bool(eval(condition, {"__builtins__": {}}, eval_context))
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False

    def handle(self, action: IAction, context: Dict[str, Any],
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle a ConditionalAction by evaluating the condition and executing
        the appropriate branch.

        Args:
            action: The ConditionalAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages

        Returns:
            ActionResult: The result of handling the action

        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: If action is not a ConditionalAction
        """
        if not isinstance(action, ConditionalAction):
            raise WorkflowError(f"ConditionalHandler received non-ConditionalAction: {type(action).__name__}")

        try:
            condition_met = self._evaluate_condition(action, context)
            logger.info(f"{log_prefix}Condition '{action.condition_type}' evaluated to {condition_met}")

            branch_to_run = action.true_branch if condition_met else action.false_branch
            branch_name = "'true'" if condition_met else "'false'"

            if not branch_to_run:
                return ActionResult.success(f"Cond {condition_met}, {branch_name} branch empty.")

            # Execute the selected branch
            branch_prefix = f"{log_prefix}{branch_name} branch: "
            branch_results = self.execute_actions(branch_to_run, context, workflow_name, branch_prefix)

            # Return success if all branch actions succeeded
            return self._determine_action_result(branch_results, branch_name)

        except ActionError as e:
            # Let the runner's error handling strategy deal with this
            raise
        except Exception as e:
            # Wrap other exceptions in ActionError
            raise ActionError(
                f"Error evaluating condition: {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            ) from e

    def _evaluate_condition(self, action: ConditionalAction, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition of a ConditionalAction.

        Args:
            action: The ConditionalAction to evaluate
            context: The execution context

        Returns:
            bool: The result of evaluating the condition
        """
        return action._evaluate_condition(self.driver, context)

    def _determine_action_result(self, branch_results: List[ActionResult], branch_name: str) -> ActionResult:
        """
        Determine the ActionResult based on the branch results.

        Args:
            branch_results: List of ActionResult objects from the executed branch
            branch_name: Name of the branch ('true' or 'false')

        Returns:
            ActionResult: The final ActionResult
        """
        # Use the common utility function to evaluate action results
        return evaluate_action_results(
            results=branch_results,
            branch_name=f"Conditional {branch_name} branch",
            success_message_template="Conditional executed {branch_name} successfully ({action_count} actions)",
            failure_message_template="Conditional {branch_name} had failures ({action_count} actions)"
        )
