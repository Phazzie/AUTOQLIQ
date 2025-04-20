################################################################################
from typing import List, Optional
import logging

from src.application.interfaces.service_interfaces import IWorkflowService
from src.core.interfaces.repository_interfaces import IWorkflowRepository
from src.core.workflow.workflow_entity import Workflow
from src.core.exceptions import RepositoryError, ValidationError

logger = logging.getLogger(__name__)

class WorkflowService(IWorkflowService):
    """Service for managing workflows."""
    def __init__(self, repository: IWorkflowRepository):
        self.repo = repository

    def create(self, name: str, description: str = "") -> Workflow:
        if not name:
            raise ValidationError("Workflow name cannot be empty", field_name="name")
        workflow = Workflow(name=name, description=description)
        try:
            self.repo.save(workflow)
            logger.info(f"Created workflow: {workflow.id}")
            return workflow
        except RepositoryError as e:
            logger.error(f"Failed to create workflow: {e}")
            raise

    def save(self, workflow: Workflow) -> None:
        if workflow is None:
            raise ValidationError("Workflow cannot be None", field_name="workflow")
        try:
            self.repo.save(workflow)
            logger.info(f"Saved workflow: {workflow.id}")
        except RepositoryError as e:
            logger.error(f"Failed to save workflow: {e}")
            raise

    def get(self, workflow_id: str) -> Optional[Workflow]:
        if not workflow_id:
            raise ValidationError("Workflow ID cannot be empty", field_name="workflow_id")
        try:
            return self.repo.get(workflow_id)
        except RepositoryError as e:
            logger.error(f"Failed to get workflow: {e}")
            raise

    def list(self) -> List[Workflow]:
        try:
            return self.repo.list()
        except RepositoryError as e:
            logger.error(f"Failed to list workflows: {e}")
            raise

    def delete(self, workflow_id: str) -> None:
        if not workflow_id:
            raise ValidationError("Workflow ID cannot be empty", field_name="workflow_id")
        try:
            self.repo.delete(workflow_id)
            logger.info(f"Deleted workflow: {workflow_id}")
        except RepositoryError as e:
            logger.error(f"Failed to delete workflow: {e}")
            raise
################################################################################