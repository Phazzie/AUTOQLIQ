import json
from typing import List, Dict, Callable
from src.core.interfaces import IWorkflowRepository, IAction
from src.core.actions import ActionFactory

class EditorPresenter:
    def __init__(self, view, workflow_repo: IWorkflowRepository):
        self.view = view
        self.workflow_repo = workflow_repo
        self.actions = []

    def add_action(self, action_data: Dict[str, Any]) -> None:
        action = ActionFactory.create_action(action_data)
        self.actions.append(action)
        self.view.update_action_list(self.actions)

    def remove_action(self, index: int) -> None:
        if 0 <= index < len(self.actions):
            del self.actions[index]
            self.view.update_action_list(self.actions)

    def save_workflow(self, name: str) -> None:
        self.workflow_repo.save(name, self.actions)

    def load_workflow(self, name: str) -> None:
        self.actions = self.workflow_repo.load(name)
        self.view.update_action_list(self.actions)

    def list_workflows(self) -> List[str]:
        return self.workflow_repo.list_workflows()
