"""Template loader for template actions.

This module provides functionality for loading templates from a repository.
"""

import logging
from typing import List

from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    Loads templates from a workflow repository.
    """
    
    def __init__(self, workflow_repo: IWorkflowRepository):
        """
        Initialize the template loader.
        
        Args:
            workflow_repo: Repository for workflows/templates
        """
        self.workflow_repo = workflow_repo
    
    def load_template(self, template_name: str) -> List[IAction]:
        """
        Load a template from the workflow repository.
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            List[IAction]: The actions in the template
            
        Raises:
            RepositoryError: If the template cannot be loaded
        """
        try:
            return self.workflow_repo.load(template_name)
        except Exception as e:
            raise RepositoryError(
                f"Failed to load template '{template_name}': {e}",
                cause=e
            ) from e
