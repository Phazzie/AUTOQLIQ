"""Database workflow repository implementation for AutoQliq.

This module provides a database-based implementation of the IWorkflowRepository
interface for storing and retrieving workflows.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.core.interfaces.repository.workflow import IWorkflowRepository
from src.infrastructure.repositories.base.database_repository import DatabaseRepository

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from src.core.interfaces.action import IAction
    from src.core.workflow.workflow_entity import Workflow

logger = logging.getLogger(__name__)

class DatabaseWorkflowRepository(DatabaseRepository["Workflow"], IWorkflowRepository):
    """Database implementation of the workflow repository.
    
    This class provides a database-based implementation of the IWorkflowRepository
    interface. It stores workflows in a SQLite database.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        connection_manager: Manager for database connections
    """
    
    _WF_TABLE_NAME = "workflows"
    _WF_PK_COLUMN = "id"
    _TMPL_TABLE_NAME = "templates"
    _TMPL_PK_COLUMN = "name"
    
    def __init__(self, db_path: str, **options: Any):
        """Initialize a new DatabaseWorkflowRepository.
        
        Args:
            db_path: Path to the SQLite database file
            **options: Additional options
                
        Raises:
            RepositoryError: If the database cannot be created or accessed
        """
        super().__init__(db_path, self._WF_TABLE_NAME, "workflow_repository")
        self._create_templates_table_if_not_exists()
        logger.info(f"Initialized workflow repository with database: {db_path}")
    
    def save(self, workflow: "Workflow") -> None:
        """Save a workflow to the repository.
        
        Args:
            workflow: The workflow to save
            
        Raises:
            ValidationError: If the workflow is invalid
            RepositoryError: If the operation fails
        """
        if not workflow:
            raise ValidationError("Workflow cannot be None")
        
        if not workflow.id:
            raise ValidationError("Workflow ID cannot be empty")
        
        # Update the workflow's updated_at timestamp
        workflow.updated_at = datetime.now()
        
        # If this is a new workflow, set the created_at timestamp
        if not workflow.created_at:
            workflow.created_at = workflow.updated_at
        
        # Save the workflow
        super().save(workflow.id, workflow)
    
    def get(self, workflow_id: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by ID.
        
        Args:
            workflow_id: ID of the workflow to get
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails
        """
        return super().get(workflow_id)
    
    def get_by_name(self, name: str) -> Optional["Workflow"]:
        """Get a workflow from the repository by name.
        
        Args:
            name: Name of the workflow to get
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty")
        
        try:
            query = f"SELECT {self._WF_PK_COLUMN} FROM {self._WF_TABLE_NAME} WHERE name = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            
            if not rows:
                logger.debug(f"Workflow not found with name: {name}")
                return None
            
            workflow_id = rows[0][self._WF_PK_COLUMN]
            return self.get(workflow_id)
        except Exception as e:
            error_msg = f"Failed to get workflow by name '{name}': {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    def get_metadata(self, workflow_id: str) -> Dict[str, Any]:
        """Get metadata for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary containing workflow metadata
            
        Raises:
            ValidationError: If the workflow ID is invalid
            RepositoryError: If the operation fails or the workflow is not found
        """
        self._validate_entity_id(workflow_id)
        
        try:
            query = f"""
                SELECT 
                    {self._WF_PK_COLUMN}, 
                    name, 
                    description, 
                    created_at, 
                    updated_at,
                    actions_json
                FROM {self._WF_TABLE_NAME} 
                WHERE {self._WF_PK_COLUMN} = ?
            """
            rows = self.connection_manager.execute_query(query, (workflow_id,))
            
            if not rows:
                raise RepositoryError(
                    f"Workflow not found: {workflow_id}",
                    repository_name="WorkflowRepository",
                    entity_id=workflow_id
                )
            
            row = rows[0]
            
            # Count actions
            actions_json = row.get("actions_json", "[]")
            actions_data = json.loads(actions_json)
            action_count = len(actions_data)
            
            return {
                "id": row.get(self._WF_PK_COLUMN),
                "name": row.get("name"),
                "description": row.get("description"),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
                "action_count": action_count,
                "source": "database"
            }
        except RepositoryError:
            raise
        except Exception as e:
            error_msg = f"Failed to get metadata for workflow '{workflow_id}': {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=workflow_id, cause=e) from e
    
    def create_empty(self, name: str) -> "Workflow":
        """Create a new empty workflow.
        
        Args:
            name: Name for the new workflow
            
        Returns:
            The newly created workflow
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails or a workflow with the same name already exists
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty")
        
        # Check if a workflow with this name already exists
        existing = self.get_by_name(name)
        if existing:
            raise RepositoryError(
                f"Workflow with name '{name}' already exists",
                repository_name="WorkflowRepository"
            )
        
        # Import here to avoid circular imports
        from src.core.workflow.workflow_entity import Workflow
        
        # Create a new workflow
        workflow = Workflow(
            name=name,
            description=f"Workflow created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            actions=[]
        )
        
        # Save the workflow
        self.save(workflow)
        
        return workflow
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with basic metadata.
        
        Returns:
            List of dictionaries containing workflow ID, name, and creation date
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            query = f"""
                SELECT 
                    {self._WF_PK_COLUMN}, 
                    name, 
                    description, 
                    created_at, 
                    updated_at,
                    actions_json
                FROM {self._WF_TABLE_NAME}
                ORDER BY name
            """
            rows = self.connection_manager.execute_query(query)
            
            workflows = []
            for row in rows:
                # Count actions
                actions_json = row.get("actions_json", "[]")
                actions_data = json.loads(actions_json)
                action_count = len(actions_data)
                
                workflows.append({
                    "id": row.get(self._WF_PK_COLUMN),
                    "name": row.get("name"),
                    "description": row.get("description"),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                    "action_count": action_count
                })
            
            return workflows
        except Exception as e:
            error_msg = f"Failed to list workflows: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    def save_template(self, name: str, actions: List["IAction"]) -> None:
        """Save a template to the repository.
        
        Args:
            name: Name of the template
            actions: List of actions in the template
            
        Raises:
            ValidationError: If the name or actions are invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        if not actions:
            raise ValidationError("Template actions cannot be empty")
        
        try:
            # Serialize the actions
            actions_data = []
            for action in actions:
                actions_data.append(action.to_dict())
            
            # Convert to JSON
            actions_json = json.dumps(actions_data)
            
            # Get current timestamp
            now = datetime.now().isoformat()
            
            # Check if the template already exists
            query = f"SELECT COUNT(*) as count FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            
            if rows and rows[0].get("count", 0) > 0:
                # Update existing template
                query = f"""
                    UPDATE {self._TMPL_TABLE_NAME}
                    SET actions_json = ?, updated_at = ?
                    WHERE {self._TMPL_PK_COLUMN} = ?
                """
                self.connection_manager.execute_modification(query, (actions_json, now, name))
            else:
                # Insert new template
                query = f"""
                    INSERT INTO {self._TMPL_TABLE_NAME}
                    ({self._TMPL_PK_COLUMN}, actions_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """
                self.connection_manager.execute_modification(query, (name, actions_json, now, now))
            
            logger.info(f"Saved template: {name}")
        except Exception as e:
            error_msg = f"Failed to save template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def get_template(self, name: str) -> Optional[List["IAction"]]:
        """Get a template from the repository by name.
        
        Args:
            name: Name of the template
            
        Returns:
            List of actions in the template if found, None otherwise
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        try:
            query = f"SELECT actions_json FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            
            if not rows:
                logger.debug(f"Template not found: {name}")
                return None
            
            # Get the actions JSON
            actions_json = rows[0].get("actions_json", "[]")
            actions_data = json.loads(actions_json)
            
            # Deserialize the actions
            actions = []
            
            # Import here to avoid circular imports
            from src.core.actions import ActionFactory
            
            for action_data in actions_data:
                action = ActionFactory.create_from_dict(action_data)
                actions.append(action)
            
            logger.info(f"Loaded template: {name}")
            return actions
        except Exception as e:
            error_msg = f"Failed to load template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def delete_template(self, name: str) -> bool:
        """Delete a template from the repository by name.
        
        Args:
            name: Name of the template
            
        Returns:
            True if the template was deleted, False if it wasn't found
            
        Raises:
            ValidationError: If the name is invalid
            RepositoryError: If the operation fails
        """
        if not name:
            raise ValidationError("Template name cannot be empty")
        
        try:
            query = f"DELETE FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
            affected_rows = self.connection_manager.execute_modification(query, (name,))
            
            if affected_rows > 0:
                logger.info(f"Deleted template: {name}")
                return True
            else:
                logger.debug(f"Template not found: {name}")
                return False
        except Exception as e:
            error_msg = f"Failed to delete template {name}: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", entity_id=name, cause=e) from e
    
    def list_templates(self) -> List[str]:
        """List all template names in the repository.
        
        Returns:
            List of template names
            
        Raises:
            RepositoryError: If the operation fails
        """
        try:
            query = f"SELECT {self._TMPL_PK_COLUMN} FROM {self._TMPL_TABLE_NAME} ORDER BY {self._TMPL_PK_COLUMN}"
            rows = self.connection_manager.execute_query(query)
            
            template_names = []
            for row in rows:
                template_names.append(row.get(self._TMPL_PK_COLUMN))
            
            logger.info(f"Listed {len(template_names)} templates")
            return template_names
        except Exception as e:
            error_msg = f"Failed to list templates: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
    
    # Implementation of abstract methods from DatabaseRepository
    
    def _get_table_creation_sql(self) -> str:
        """Get the SQL for creating the workflows table.
        
        Returns:
            SQL statement for creating the table
        """
        return f"""
            {self._WF_PK_COLUMN} TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            actions_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        """
    
    def _map_row_to_entity(self, row: Dict[str, Any]) -> "Workflow":
        """Map a database row to a workflow entity.
        
        Args:
            row: Database row
            
        Returns:
            Workflow entity
            
        Raises:
            SerializationError: If the row cannot be mapped to a workflow
        """
        try:
            # Import here to avoid circular imports
            from src.core.workflow.workflow_entity import Workflow
            from src.core.actions import ActionFactory
            
            # Get the workflow data
            workflow_id = row.get(self._WF_PK_COLUMN)
            name = row.get("name")
            description = row.get("description")
            created_at_str = row.get("created_at")
            updated_at_str = row.get("updated_at")
            actions_json = row.get("actions_json", "[]")
            
            # Parse dates
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
            updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else None
            
            # Parse actions
            actions_data = json.loads(actions_json)
            actions = []
            
            for action_data in actions_data:
                action = ActionFactory.create_from_dict(action_data)
                actions.append(action)
            
            # Create the workflow
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                actions=actions,
                created_at=created_at,
                updated_at=updated_at
            )
            
            return workflow
        except Exception as e:
            error_msg = f"Failed to map row to workflow: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
    
    def _map_entity_to_params(self, entity_id: str, entity: "Workflow") -> Dict[str, Any]:
        """Map a workflow entity to database parameters.
        
        Args:
            entity_id: ID of the workflow
            entity: Workflow entity
            
        Returns:
            Dictionary of database parameters
            
        Raises:
            SerializationError: If the workflow cannot be mapped to parameters
        """
        try:
            # Serialize actions
            actions_data = []
            for action in entity.actions:
                actions_data.append(action.to_dict())
            
            # Convert to JSON
            actions_json = json.dumps(actions_data)
            
            # Map to parameters
            params = {
                self._WF_PK_COLUMN: entity_id,
                "name": entity.name,
                "description": entity.description,
                "actions_json": actions_json,
                "created_at": entity.created_at.isoformat() if entity.created_at else None,
                "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
            }
            
            return params
        except Exception as e:
            error_msg = f"Failed to map workflow to parameters: {e}"
            logger.error(error_msg)
            raise SerializationError(error_msg, cause=e) from e
    
    def _get_primary_key_col(self) -> str:
        """Get the primary key column name.
        
        Returns:
            Name of the primary key column
        """
        return self._WF_PK_COLUMN
    
    # Helper methods
    
    def _create_templates_table_if_not_exists(self) -> None:
        """Create the templates table if it doesn't exist.
        
        Raises:
            RepositoryError: If the table cannot be created
        """
        try:
            columns_sql = f"""
                {self._TMPL_PK_COLUMN} TEXT PRIMARY KEY,
                actions_json TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            """
            self.connection_manager.create_table(self._TMPL_TABLE_NAME, columns_sql)
        except Exception as e:
            error_msg = f"Failed to create templates table: {e}"
            logger.error(error_msg)
            raise RepositoryError(error_msg, repository_name="WorkflowRepository", cause=e) from e
