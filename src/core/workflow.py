import json
from typing import List
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.exceptions import LoginFailedError, WorkflowError
from src.core.actions import ActionFactory

class WorkflowRunner:
    def __init__(self, driver: IWebDriver, credential_repo: ICredentialRepository, workflow_repo: IWorkflowRepository):
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo

    def run_workflow(self, workflow_name: str) -> None:
        try:
            actions = self.workflow_repo.load(workflow_name)
            for action in actions:
                action.execute(self.driver)
        except LoginFailedError as e:
            raise WorkflowError(f"Workflow '{workflow_name}' failed: {str(e)}")
        except Exception as e:
            raise WorkflowError(f"An unexpected error occurred during workflow '{workflow_name}': {str(e)}")

    def save_workflow(self, workflow_name: str, actions: List[IAction]) -> None:
        self.workflow_repo.save(workflow_name, actions)

    def list_workflows(self) -> List[str]:
        return self.workflow_repo.list_workflows()

    def load_workflow(self, workflow_name: str) -> List[IAction]:
        return self.workflow_repo.load(workflow_name)
