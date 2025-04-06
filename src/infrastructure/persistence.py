import json
import os
from typing import List, Dict, Optional, Any
from src.core.interfaces import ICredentialRepository, IWorkflowRepository, IAction
from src.core.credentials import Credential
from src.core.actions import ActionFactory

class FileSystemCredentialRepository(ICredentialRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all(self) -> List[Dict[str, str]]:
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        credentials = self.get_all()
        for credential in credentials:
            if credential['name'] == name:
                return credential
        return None

class FileSystemWorkflowRepository(IWorkflowRepository):
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        file_path = os.path.join(self.directory_path, f"{name}.json")
        with open(file_path, 'w') as file:
            json.dump([action.to_dict() for action in workflow_actions], file)

    def load(self, name: str) -> List[IAction]:
        file_path = os.path.join(self.directory_path, f"{name}.json")
        with open(file_path, 'r') as file:
            actions_data = json.load(file)
        return [self._create_action(action_data) for action_data in actions_data]

    def list_workflows(self) -> List[str]:
        return [f.split('.')[0] for f in os.listdir(self.directory_path) if f.endswith('.json')]

    def _create_action(self, action_data: Dict[str, Any]) -> IAction:
        return ActionFactory.create_action(action_data)
