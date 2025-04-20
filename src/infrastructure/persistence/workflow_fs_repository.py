from typing import List, Optional
import os
import json
import logging

from src.core.interfaces.repository_interfaces import IWorkflowRepository
from src.core.workflow.workflow_entity import Workflow
from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class FileSystemWorkflowRepository(IWorkflowRepository):
    """Filesystem-based repository for Workflow entities."""
    def __init__(self, path: str, create_if_missing: bool = True):
        self.path = path
        if create_if_missing and not os.path.exists(self.path):
            try:
                os.makedirs(self.path, exist_ok=True)
                logger.info(f"Created workflow directory: {self.path}")
            except Exception as e:
                logger.error(f"Failed to create workflow dir: {e}")
                raise RepositoryError("Cannot initialize workflow repository", cause=e)

    def save(self, workflow: Workflow) -> None:
        file = os.path.join(self.path, f"{workflow.id}.json")
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            logger.info(f"Saved workflow: {workflow.id}")
        except Exception as e:
            logger.error(f"Error saving workflow {workflow.id}: {e}")
            raise RepositoryError("Save failed", repository_name="WorkflowRepository", entity_id=workflow.id, cause=e)

    def get(self, workflow_id: str) -> Optional[Workflow]:
        file = os.path.join(self.path, f"{workflow_id}.json")
        try:
            if not os.path.exists(file):
                return None
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Workflow.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading workflow {workflow_id}: {e}")
            raise RepositoryError("Get failed", repository_name="WorkflowRepository", entity_id=workflow_id, cause=e)

    def list(self) -> List[Workflow]:
        workflows = []
        try:
            for fname in os.listdir(self.path):
                if fname.endswith('.json'):
                    wid = fname[:-5]
                    wf = self.get(wid)
                    if wf:
                        workflows.append(wf)
            return workflows
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise RepositoryError("List failed", repository_name="WorkflowRepository", cause=e)

    def delete(self, workflow_id: str) -> None:
        file = os.path.join(self.path, f"{workflow_id}.json")
        try:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"Deleted workflow: {workflow_id}")
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise RepositoryError("Delete failed", repository_name="WorkflowRepository", entity_id=workflow_id, cause=e)
