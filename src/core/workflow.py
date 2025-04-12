from typing import List
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository
from src.core.exceptions import WorkflowError
from src.core.action_result import ActionResult
from src.core.actions import TypeAction

class WorkflowManager:
    def __init__(self, workflow_repo: IWorkflowRepository):
        self.workflow_repo = workflow_repo

    def save_workflow(self, workflow_name: str, actions: List[IAction]) -> None:
        self.workflow_repo.save(workflow_name, actions)

    def list_workflows(self) -> List[str]:
        return self.workflow_repo.list_workflows()

    def load_workflow(self, workflow_name: str) -> List[IAction]:
        return self.workflow_repo.load(workflow_name)
