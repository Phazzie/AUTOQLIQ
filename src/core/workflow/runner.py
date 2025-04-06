"""Workflow Runner module for AutoQliq.

Provides the WorkflowRunner class responsible for executing a sequence of actions.
"""

import logging
from typing import List, Optional

# Assuming necessary interfaces, classes, and exceptions are defined
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError, ActionError

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a given sequence of actions using a web driver.

    This class focuses solely on the execution logic, iterating through actions
    and collecting their results. It relies on external components for loading
    workflows and managing credentials.

    Attributes:
        driver (IWebDriver): The web driver instance for browser interaction.
        credential_repo (Optional[ICredentialRepository]): Repository for credentials,
            passed to actions that require them (e.g., TypeAction).
    """

    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None
    ):
        """
        Initialize the WorkflowRunner.

        Args:
            driver (IWebDriver): The web driver to use for executing actions.
            credential_repo (Optional[ICredentialRepository]): The credential repository
                to be used by actions requiring credentials. Defaults to None.
        """
        if driver is None:
            raise ValueError("WebDriver instance cannot be None.")
        self.driver = driver
        self.credential_repo = credential_repo
        logger.info("WorkflowRunner initialized.")
        if credential_repo:
            logger.debug(f"Using credential repository: {credential_repo.__class__.__name__}")
        else:
            logger.debug("No credential repository provided.")

    def run(self, actions: List[IAction], workflow_name: str = "Unnamed Workflow") -> List[ActionResult]:
        """
        Execute a list of actions sequentially.

        Iterates through the provided actions, executes each one, and collects
        the results. Execution stops immediately if an action fails.

        Args:
            actions (List[IAction]): The sequence of action instances to execute.
            workflow_name (str): The name of the workflow being executed (for logging/error context).
                                 Defaults to "Unnamed Workflow".

        Returns:
            List[ActionResult]: A list containing the result of each executed action.
                                If an action fails, the list contains results up to
                                and including the failed action.

        Raises:
            WorkflowError: If an action fails during execution or an unexpected
                           error occurs within the runner.
        """
        if not isinstance(actions, list):
            raise TypeError("Actions must be provided as a list.")
        if not workflow_name:
             workflow_name = "Unnamed Workflow" # Ensure a name for logging

        logger.info(f"Starting execution of workflow: '{workflow_name}' with {len(actions)} actions.")
        results: List[ActionResult] = []

        for i, action in enumerate(actions):
            action_display_name = f"{action.name} ({action.action_type}, Step {i+1})"
            logger.debug(f"Executing action: {action_display_name}")

            if not isinstance(action, IAction):
                msg = f"Item at index {i} in actions list is not a valid IAction instance."
                logger.error(msg)
                raise WorkflowError(msg, workflow_name=workflow_name)

            try:
                # Pass driver and credential repo to the action's execute method
                result = action.execute(self.driver, self.credential_repo)
                results.append(result)

                if not result.is_success():
                    msg = f"Action '{action_display_name}' failed: {result.message}"
                    logger.error(msg)
                    # Raise error to stop workflow execution
                    raise ActionError(msg, action_name=action.name, action_type=action.action_type)

                logger.debug(f"Action '{action_display_name}' completed successfully.")

            except ActionError as ae:
                # ActionError raised by the action itself or by the failure check above
                logger.error(f"Workflow '{workflow_name}' failed during action '{action_display_name}'.")
                # Wrap in WorkflowError for consistent workflow-level failure reporting
                raise WorkflowError(
                    f"Workflow execution failed: {str(ae)}",
                    workflow_name=workflow_name,
                    action_name=action.name,
                    cause=ae
                ) from ae
            except Exception as e:
                # Catch unexpected errors during the loop or action execution call
                logger.exception(f"Unexpected error during action '{action_display_name}' in workflow '{workflow_name}'.")
                raise WorkflowError(
                    f"Unexpected error during workflow execution: {str(e)}",
                    workflow_name=workflow_name,
                    action_name=action.name,
                    cause=e
                ) from e

        logger.info(f"Workflow '{workflow_name}' completed successfully.")
        return results

```

```text