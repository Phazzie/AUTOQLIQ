"""Integration tests for presenter and repository interactions."""
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from src.core.workflow.entity import WorkflowEntity
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.infrastructure.repositories.repository_factory import RepositoryFactory
from src.ui.presenters.workflow_editor_presenter_refactored import WorkflowEditorPresenter


class TestPresenterRepositoryIntegration(unittest.TestCase):
    """Integration tests for presenter and repository interactions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Create repositories
        self.workflow_repository = DatabaseWorkflowRepository(db_path=self.db_path)
        
        # Mock repository factory to return our test repositories
        self.repository_factory = MagicMock(spec=RepositoryFactory)
        self.repository_factory.create_workflow_repository.return_value = self.workflow_repository
        
        # Mock view
        self.view = MagicMock()
        
        # Create presenter with real repository and mock view
        self.presenter = WorkflowEditorPresenter(
            view=self.view,
            repository_factory=self.repository_factory
        )
        
        # Sample workflow data
        self.workflow_id = "test-workflow-1"
        self.workflow_data = {
            "id": self.workflow_id,
            "name": "Test Workflow",
            "description": "A test workflow",
            "actions": [
                {
                    "type": "navigate",
                    "url": "https://example.com",
                    "id": "action-1"
                },
                {
                    "type": "click",
                    "selector": "#submit-button",
                    "id": "action-2"
                }
            ]
        }
        self.workflow = WorkflowEntity.from_dict(self.workflow_data)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_save_and_load_workflow(self):
        """Test saving a workflow through the presenter and loading it back."""
        # Arrange - Initialize the presenter
        self.presenter.initialize()
        
        # Act - Save the workflow through the presenter
        self.presenter.current_workflow = self.workflow
        self.presenter.save_workflow()
        
        # Reset the presenter's current workflow
        self.presenter.current_workflow = None
        
        # Load the workflow through the presenter
        self.presenter.load_workflow(self.workflow_id)
        
        # Assert - Verify the loaded workflow matches the original
        loaded_workflow = self.presenter.current_workflow
        self.assertIsNotNone(loaded_workflow)
        self.assertEqual(loaded_workflow.id, self.workflow_id)
        self.assertEqual(loaded_workflow.name, "Test Workflow")
        self.assertEqual(len(loaded_workflow.actions), 2)
        self.assertEqual(loaded_workflow.actions[0].action_type, "navigate")
        self.assertEqual(loaded_workflow.actions[1].action_type, "click")

    def test_update_workflow(self):
        """Test updating a workflow through the presenter."""
        # Arrange - Save the initial workflow
        self.workflow_repository.save_workflow(self.workflow)
        
        # Initialize the presenter and load the workflow
        self.presenter.initialize()
        self.presenter.load_workflow(self.workflow_id)
        
        # Act - Update the workflow through the presenter
        self.presenter.current_workflow.name = "Updated Workflow"
        self.presenter.current_workflow.description = "Updated description"
        self.presenter.save_workflow()
        
        # Load the workflow directly from the repository
        updated_workflow = self.workflow_repository.get_by_id(self.workflow_id)
        
        # Assert - Verify the updates were saved
        self.assertEqual(updated_workflow.name, "Updated Workflow")
        self.assertEqual(updated_workflow.description, "Updated description")

    def test_delete_workflow(self):
        """Test deleting a workflow through the presenter."""
        # Arrange - Save the workflow
        self.workflow_repository.save_workflow(self.workflow)
        
        # Initialize the presenter
        self.presenter.initialize()
        
        # Act - Delete the workflow through the presenter
        self.presenter.delete_workflow(self.workflow_id)
        
        # Try to load the workflow directly from the repository
        deleted_workflow = self.workflow_repository.get_by_id(self.workflow_id)
        
        # Assert - Verify the workflow was deleted
        self.assertIsNone(deleted_workflow)

    def test_list_workflows(self):
        """Test listing workflows through the presenter."""
        # Arrange - Save multiple workflows
        self.workflow_repository.save_workflow(self.workflow)
        
        # Create and save a second workflow
        second_workflow_data = self.workflow_data.copy()
        second_workflow_data["id"] = "test-workflow-2"
        second_workflow_data["name"] = "Second Test Workflow"
        second_workflow = WorkflowEntity.from_dict(second_workflow_data)
        self.workflow_repository.save_workflow(second_workflow)
        
        # Initialize the presenter
        self.presenter.initialize()
        
        # Act - Load the workflow list through the presenter
        self.presenter.load_workflow_list()
        
        # Assert - Verify the view was called with the correct data
        self.view.display_workflow_list.assert_called_once()
        # Extract the workflow list from the call arguments
        workflow_list = self.view.display_workflow_list.call_args[0][0]
        self.assertEqual(len(workflow_list), 2)
        
        # Verify the workflow IDs are in the list
        workflow_ids = [w["id"] for w in workflow_list]
        self.assertIn(self.workflow_id, workflow_ids)
        self.assertIn("test-workflow-2", workflow_ids)

    def test_add_action(self):
        """Test adding an action to a workflow through the presenter."""
        # Arrange - Initialize the presenter with a new workflow
        self.presenter.initialize()
        self.presenter.create_new_workflow()
        self.presenter.current_workflow.id = self.workflow_id
        self.presenter.current_workflow.name = "Test Workflow"
        
        # Act - Add actions through the presenter
        self.presenter.add_action("navigate", {"url": "https://example.com"})
        self.presenter.add_action("click", {"selector": "#submit-button"})
        
        # Save the workflow
        self.presenter.save_workflow()
        
        # Load the workflow directly from the repository
        saved_workflow = self.workflow_repository.get_by_id(self.workflow_id)
        
        # Assert - Verify the actions were added and saved
        self.assertEqual(len(saved_workflow.actions), 2)
        self.assertEqual(saved_workflow.actions[0].action_type, "navigate")
        self.assertEqual(saved_workflow.actions[0].parameters["url"], "https://example.com")
        self.assertEqual(saved_workflow.actions[1].action_type, "click")
        self.assertEqual(saved_workflow.actions[1].parameters["selector"], "#submit-button")

    def test_remove_action(self):
        """Test removing an action from a workflow through the presenter."""
        # Arrange - Save the workflow
        self.workflow_repository.save_workflow(self.workflow)
        
        # Initialize the presenter and load the workflow
        self.presenter.initialize()
        self.presenter.load_workflow(self.workflow_id)
        
        # Get the ID of the first action
        action_id = self.presenter.current_workflow.actions[0].id
        
        # Act - Remove the action through the presenter
        self.presenter.remove_action(action_id)
        
        # Save the workflow
        self.presenter.save_workflow()
        
        # Load the workflow directly from the repository
        updated_workflow = self.workflow_repository.get_by_id(self.workflow_id)
        
        # Assert - Verify the action was removed
        self.assertEqual(len(updated_workflow.actions), 1)
        self.assertNotEqual(updated_workflow.actions[0].id, action_id)


if __name__ == "__main__":
    unittest.main()
