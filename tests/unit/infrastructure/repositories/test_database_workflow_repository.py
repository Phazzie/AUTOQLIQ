"""Tests for the database workflow repository."""
import unittest
import os
import sqlite3
import json
from unittest.mock import patch, MagicMock

from src.core.exceptions import WorkflowError
from src.core.interfaces import IAction
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.infrastructure.repositories.serialization.action_serializer import serialize_actions

class TestDatabaseWorkflowRepository(unittest.TestCase):
    """Test cases for the DatabaseWorkflowRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test repository with an in-memory database
        self.repo = DatabaseWorkflowRepository(":memory:")
        
        # Create mock actions
        self.action1 = MagicMock(spec=IAction)
        self.action1.to_dict.return_value = {"type": "Navigate", "url": "https://example.com"}
        
        self.action2 = MagicMock(spec=IAction)
        self.action2.to_dict.return_value = {"type": "Click", "selector": "#button"}
        
        # Create a test workflow
        self.workflow_name = "test_workflow"
        self.workflow_actions = [self.action1, self.action2]
        
        # Patch the deserialize_actions function
        self.patcher = patch("src.infrastructure.repositories.database_workflow_repository.deserialize_actions")
        self.mock_deserialize_actions = self.patcher.start()
        self.mock_deserialize_actions.return_value = self.workflow_actions
        
        # Save the test workflow
        self.repo.save(self.workflow_name, self.workflow_actions)

    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()

    def test_initialization(self):
        """Test that a DatabaseWorkflowRepository can be initialized with a database path."""
        # Check that the repository was initialized correctly
        self.assertEqual(self.repo.db_path, ":memory:")
        self.assertIsNotNone(self.repo.logger)
        
        # Check that the workflows table exists
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workflows'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_create_workflow(self):
        """Test that create_workflow creates a new workflow."""
        # Create a new workflow
        self.repo.create_workflow("new_workflow")
        
        # Check that the workflow exists
        workflows = self.repo.list_workflows()
        self.assertIn("new_workflow", workflows)
        
        # Check that the workflow has no actions
        actions = self.repo.load("new_workflow")
        self.assertEqual(len(actions), 0)

    def test_create_workflow_already_exists(self):
        """Test that create_workflow raises WorkflowError if the workflow already exists."""
        # Try to create a workflow with the same name
        with self.assertRaises(WorkflowError):
            self.repo.create_workflow(self.workflow_name)

    def test_create_workflow_invalid_name(self):
        """Test that create_workflow raises WorkflowError for invalid workflow names."""
        # Try to create workflows with invalid names
        invalid_names = [
            "",  # Empty name
            "invalid name",  # Contains spaces
            "invalid/name",  # Contains slashes
            "invalid\\name",  # Contains backslashes
            "invalid:name"  # Contains colons
        ]
        
        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(WorkflowError):
                    self.repo.create_workflow(invalid_name)

    def test_save(self):
        """Test that save updates an existing workflow."""
        # Update the test workflow
        new_action = MagicMock(spec=IAction)
        new_action.to_dict.return_value = {"type": "Type", "selector": "#input", "value": "test"}
        
        self.repo.save(self.workflow_name, [new_action])
        
        # Load the workflow
        self.mock_deserialize_actions.return_value = [new_action]
        actions = self.repo.load(self.workflow_name)
        
        # Check that the workflow was updated
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], new_action)

    def test_save_new_workflow(self):
        """Test that save creates a new workflow if it doesn't exist."""
        # Save a new workflow
        new_workflow_name = "new_workflow"
        self.repo.save(new_workflow_name, self.workflow_actions)
        
        # Check that the workflow exists
        workflows = self.repo.list_workflows()
        self.assertIn(new_workflow_name, workflows)
        
        # Load the workflow
        actions = self.repo.load(new_workflow_name)
        
        # Check that the workflow has the correct actions
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0], self.action1)
        self.assertEqual(actions[1], self.action2)

    def test_save_invalid_name(self):
        """Test that save raises WorkflowError for invalid workflow names."""
        # Try to save workflows with invalid names
        invalid_names = [
            "",  # Empty name
            "invalid name",  # Contains spaces
            "invalid/name",  # Contains slashes
            "invalid\\name",  # Contains backslashes
            "invalid:name"  # Contains colons
        ]
        
        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(WorkflowError):
                    self.repo.save(invalid_name, self.workflow_actions)

    def test_save_empty_actions(self):
        """Test that save raises WorkflowError for empty actions."""
        # Try to save a workflow with empty actions
        with self.assertRaises(WorkflowError):
            self.repo.save(self.workflow_name, [])

    def test_load(self):
        """Test that load returns the actions for a workflow."""
        # Load the test workflow
        actions = self.repo.load(self.workflow_name)
        
        # Check that the correct actions were returned
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0], self.action1)
        self.assertEqual(actions[1], self.action2)
        
        # Check that deserialize_actions was called with the correct data
        action_data = [
            {"type": "Navigate", "url": "https://example.com"},
            {"type": "Click", "selector": "#button"}
        ]
        self.mock_deserialize_actions.assert_called_with(action_data)

    def test_load_not_found(self):
        """Test that load raises WorkflowError if the workflow is not found."""
        # Try to load a nonexistent workflow
        with self.assertRaises(WorkflowError):
            self.repo.load("nonexistent")

    def test_list_workflows(self):
        """Test that list_workflows returns all workflow names."""
        # Create some additional workflows
        self.repo.create_workflow("workflow1")
        self.repo.create_workflow("workflow2")
        
        # List all workflows
        workflows = self.repo.list_workflows()
        
        # Check that all workflows are listed
        self.assertIn(self.workflow_name, workflows)
        self.assertIn("workflow1", workflows)
        self.assertIn("workflow2", workflows)

    def test_delete(self):
        """Test that delete removes a workflow."""
        # Delete the test workflow
        result = self.repo.delete(self.workflow_name)
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the workflow was deleted
        workflows = self.repo.list_workflows()
        self.assertNotIn(self.workflow_name, workflows)
        
        # Try to load the deleted workflow
        with self.assertRaises(WorkflowError):
            self.repo.load(self.workflow_name)

    def test_delete_not_found(self):
        """Test that delete returns False if the workflow is not found."""
        # Delete a nonexistent workflow
        result = self.repo.delete("nonexistent")
        
        # Check the result
        self.assertFalse(result)

    def test_get_metadata(self):
        """Test that get_metadata returns metadata for a workflow."""
        # Get metadata for the test workflow
        metadata = self.repo.get_metadata(self.workflow_name)
        
        # Check that the metadata contains the expected fields
        self.assertEqual(metadata["name"], self.workflow_name)
        self.assertIn("created", metadata)
        self.assertIn("modified", metadata)

    def test_get_metadata_not_found(self):
        """Test that get_metadata raises WorkflowError if the workflow is not found."""
        # Try to get metadata for a nonexistent workflow
        with self.assertRaises(WorkflowError):
            self.repo.get_metadata("nonexistent")

if __name__ == "__main__":
    unittest.main()
