from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credentials

class IWorkflowRepository(ABC):
    """Contract for persisting Workflow entities."""

    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        pass

    @abstractmethod
    def get(self, workflow_id: str) -> Optional[Workflow]:
        pass

    @abstractmethod
    def list(self) -> List[Workflow]:
        pass

    @abstractmethod
    def delete(self, workflow_id: str) -> None:
        pass

class ICredentialRepository(ABC):
    """Contract for persisting credential entities."""

    @abstractmethod
    def save(self, credentials: Credentials) -> None:
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[Credentials]:
        pass

    @abstractmethod
    def list(self) -> List[Credentials]:
        pass

    @abstractmethod
    def delete(self, name: str) -> None:
        pass