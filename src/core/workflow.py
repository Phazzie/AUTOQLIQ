from typing import List
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.exceptions import WorkflowError
from src.core.action_base import ActionResult

class WorkflowRunner:
    def __init__(self, driver: IWebDriver, credential_repo: ICredentialRepository, workflow_repo: IWorkflowRepository):
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo

    def run_workflow(self, workflow_name: str) -> List[ActionResult]:
        try:
            actions = self.workflow_repo.load(workflow_name)
            results = []

            for action in actions:
                result = action.execute(self.driver)
                results.append(result)

                # Stop execution if an action fails
                if not result.is_success():
                    raise WorkflowError(f"Action '{action.name}' failed: {result.message}")

            return results
        except WorkflowError as e:
            # Re-raise workflow errors
            raise
        except Exception as e:
            raise WorkflowError(f"An unexpected error occurred during workflow '{workflow_name}': {str(e)}")

    def save_workflow(self, workflow_name: str, actions: List[IAction]) -> None:
        self.workflow_repo.save(workflow_name, actions)

    def list_workflows(self) -> List[str]:
        return self.workflow_repo.list_workflows()

    def load_workflow(self, workflow_name: str) -> List[IAction]:
        return self.workflow_repo.load(workflow_name)
