"""Template repository for AutoQliq.

This module provides a repository for storing and retrieving action templates.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional

from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)

class TemplateRepository:
    """
    Repository for storing and retrieving action templates.
    
    Templates are named sequences of actions that can be reused across workflows.
    """
    
    def __init__(self, directory_path: str = None):
        """
        Initialize the repository with the directory path.
        
        Args:
            directory_path: Path to the directory where templates will be stored.
                           If None, uses the default path.
        """
        if directory_path is None:
            # Use default path
            directory_path = os.path.join(os.path.expanduser("~"), ".autoqliq", "templates")
        
        self.directory_path = directory_path
        
        # Create directory if it doesn't exist
        os.makedirs(self.directory_path, exist_ok=True)
        
        logger.debug(f"TemplateRepository initialized with directory: {directory_path}")
    
    def save_template(self, template: Dict[str, Any]) -> None:
        """
        Save a template to the repository.
        
        Args:
            template: The template to save. Must have a 'name' key.
            
        Raises:
            RepositoryError: If the template could not be saved.
            ValueError: If the template does not have a name.
        """
        if "name" not in template:
            raise ValueError("Template must have a name")
        
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{template['name']}.json")
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            logger.info(f"Saved template '{template['name']}' to {file_path}")
        except Exception as e:
            logger.error(f"Error saving template '{template.get('name', 'unknown')}': {e}")
            raise RepositoryError(f"Failed to save template: {e}")
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by name.
        
        Args:
            name: The name of the template to get.
            
        Returns:
            The template, or None if not found.
            
        Raises:
            RepositoryError: If the template could not be retrieved.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{name}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Template not found: {name}")
                return None
            
            # Read from file
            with open(file_path, 'r') as f:
                template = json.load(f)
            
            logger.info(f"Retrieved template '{name}' from {file_path}")
            return template
        except Exception as e:
            logger.error(f"Error getting template '{name}': {e}")
            raise RepositoryError(f"Failed to get template: {e}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all templates.
        
        Returns:
            List of all templates.
            
        Raises:
            RepositoryError: If the templates could not be listed.
        """
        try:
            templates = []
            
            # Get all JSON files in the directory
            for filename in os.listdir(self.directory_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.directory_path, filename)
                    
                    try:
                        # Read from file
                        with open(file_path, 'r') as f:
                            template = json.load(f)
                        
                        # Add to list
                        templates.append(template)
                    except Exception as e:
                        logger.warning(f"Error reading template from {file_path}: {e}")
                        # Continue with next file
            
            logger.info(f"Listed {len(templates)} templates from {self.directory_path}")
            return templates
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            raise RepositoryError(f"Failed to list templates: {e}")
    
    def delete_template(self, name: str) -> None:
        """
        Delete a template by name.
        
        Args:
            name: The name of the template to delete.
            
        Raises:
            RepositoryError: If the template could not be deleted.
        """
        try:
            # Create file path
            file_path = os.path.join(self.directory_path, f"{name}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.info(f"Template not found for deletion: {name}")
                return
            
            # Delete file
            os.remove(file_path)
            
            logger.info(f"Deleted template: {name}")
        except Exception as e:
            logger.error(f"Error deleting template '{name}': {e}")
            raise RepositoryError(f"Failed to delete template: {e}")
