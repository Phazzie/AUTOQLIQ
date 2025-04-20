"""Unit tests for the WorkflowFSRepository."""

import unittest
import os
import shutil
import tempfile
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.exceptions import RepositoryError, ValidationError
from src.core.workflow.workflow_entity import Workflow
from src.core.actions.base_action import ActionBase
from src.infrastructure.repositories.workflow_fs_repository import WorkflowFSRepository


class MockAction(ActionBase):
    """Mock action for testing."""
    
    def __init__(self, name="Mock Action", action_type="Mock"):
        super().__init__(name)
        self.action_type = action_type
    
    def execute(self, driver, credential_repository=None):
        return None
    
    def validate(self):
        pass
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.action_type
        }


class TestWorkflowFSRepository(unittest.TestCase):
    """Test cases for the WorkflowFSRepository."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_init_with_existing_directory(self):
        """Test initializing the repository with an existing directory."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Check that the repository was created with the correct directory
        self.assertEqual(repo.directory_path, os.path.abspath(self.test_dir))
    
    def test_init_with_nonexistent_directory_create_if_missing(self):
        """Test initializing the repository with a nonexistent directory and create_if_missing=True."""
        # Create a path to a nonexistent directory
        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")
        
        # Create the repository with create_if_missing=True
        repo = WorkflowFSRepository(nonexistent_dir, create_if_missing=True)
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(nonexistent_dir))
        
        # Check that the repository was created with the correct directory
        self.assertEqual(repo.directory_path, os.path.abspath(nonexistent_dir))
    
    def test_init_with_nonexistent_directory_no_create(self):
        """Test initializing the repository with a nonexistent directory and create_if_missing=False."""
        # Create a path to a nonexistent directory
        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")
        
        # Try to create the repository with create_if_missing=False
        with self.assertRaises(RepositoryError):
            WorkflowFSRepository(nonexistent_dir, create_if_missing=False)
    
    def test_get_file_path(self):
        """Test getting the file path for a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Get the file path for a workflow
        file_path = repo._get_file_path("test-workflow")
        
        # Check that the file path is correct
        expected_path = os.path.join(self.test_dir, "test-workflow.json")
        self.assertEqual(file_path, expected_path)
    
    def test_get_file_path_with_invalid_id(self):
        """Test getting the file path with an invalid workflow ID."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Try to get the file path with an empty workflow ID
        with self.assertRaises(ValidationError):
            repo._get_file_path("")
    
    def test_serialize_workflow(self):
        """Test serializing a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        workflow.description = "Test workflow description"
        workflow.created_at = datetime(2023, 1, 1, 12, 0, 0)
        workflow.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        
        # Add an action to the workflow
        action = MockAction(name="Test Action", action_type="Test")
        workflow.add_action(action)
        
        # Serialize the workflow
        data = repo._serialize_workflow(workflow)
        
        # Check that the serialized data is correct
        self.assertEqual(data["id"], "test-workflow")
        self.assertEqual(data["name"], "Test Workflow")
        self.assertEqual(data["description"], "Test workflow description")
        self.assertEqual(data["created_at"], "2023-01-01T12:00:00")
        self.assertEqual(data["updated_at"], "2023-01-02T12:00:00")
        self.assertEqual(len(data["actions"]), 1)
        self.assertEqual(data["actions"][0]["name"], "Test Action")
        self.assertEqual(data["actions"][0]["type"], "Test")
    
    def test_deserialize_workflow(self):
        """Test deserializing a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create serialized workflow data
        data = {
            "id": "test-workflow",
            "name": "Test Workflow",
            "description": "Test workflow description",
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
            "actions": [
                {
                    "name": "Test Action",
                    "type": "Test"
                }
            ]
        }
        
        # Mock the ActionFactory
        with patch("src.core.actions.factory.ActionFactory") as mock_factory:
            # Set up the mock to return a MockAction
            mock_action = MockAction(name="Test Action", action_type="Test")
            mock_factory.create_from_dict.return_value = mock_action
            
            # Deserialize the workflow
            workflow = repo._deserialize_workflow(data)
            
            # Check that the deserialized workflow is correct
            self.assertEqual(workflow.id, "test-workflow")
            self.assertEqual(workflow.name, "Test Workflow")
            self.assertEqual(workflow.description, "Test workflow description")
            self.assertEqual(workflow.created_at, datetime(2023, 1, 1, 12, 0, 0))
            self.assertEqual(workflow.updated_at, datetime(2023, 1, 2, 12, 0, 0))
            self.assertEqual(len(workflow.actions), 1)
            self.assertEqual(workflow.actions[0].name, "Test Action")
            self.assertEqual(workflow.actions[0].action_type, "Test")
    
    def test_save_workflow(self):
        """Test saving a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        
        # Save the workflow
        repo.save(workflow)
        
        # Check that the workflow file was created
        file_path = os.path.join(self.test_dir, "test-workflow.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check that the file contains the correct data
        with open(file_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["id"], "test-workflow")
            self.assertEqual(data["name"], "Test Workflow")
    
    def test_save_workflow_with_no_id(self):
        """Test saving a workflow with no ID."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow with no ID
        workflow = Workflow(name="Test Workflow")
        
        # Save the workflow
        repo.save(workflow)
        
        # Check that the workflow was assigned an ID
        self.assertIsNotNone(workflow.id)
        
        # Check that the workflow file was created
        file_path = os.path.join(self.test_dir, f"{workflow.id}.json")
        self.assertTrue(os.path.exists(file_path))
    
    def test_save_workflow_with_no_timestamps(self):
        """Test saving a workflow with no timestamps."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow with no timestamps
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        
        # Save the workflow
        repo.save(workflow)
        
        # Check that the timestamps were set
        self.assertIsNotNone(workflow.created_at)
        self.assertIsNotNone(workflow.updated_at)
        self.assertEqual(workflow.created_at, workflow.updated_at)
    
    def test_save_workflow_with_existing_created_at(self):
        """Test saving a workflow with an existing created_at timestamp."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow with an existing created_at timestamp
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        workflow.created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Save the workflow
        repo.save(workflow)
        
        # Check that the created_at timestamp was preserved
        self.assertEqual(workflow.created_at, datetime(2023, 1, 1, 12, 0, 0))
        
        # Check that the updated_at timestamp was set
        self.assertIsNotNone(workflow.updated_at)
        self.assertNotEqual(workflow.created_at, workflow.updated_at)
    
    def test_get_workflow(self):
        """Test getting a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create a workflow
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        
        # Save the workflow
        repo.save(workflow)
        
        # Get the workflow
        retrieved_workflow = repo.get("test-workflow")
        
        # Check that the retrieved workflow is correct
        self.assertIsNotNone(retrieved_workflow)
        self.assertEqual(retrieved_workflow.id, "test-workflow")
        self.assertEqual(retrieved_workflow.name, "Test Workflow")
    
    def test_get_nonexistent_workflow(self):
        """Test getting a nonexistent workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Try to get a nonexistent workflow
        workflow = repo.get("nonexistent")
        
        # Check that the result is None
        self.assertIsNone(workflow)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create and save some workflows
        workflow1 = Workflow(id="test-workflow-1", name="Test Workflow 1")
        workflow2 = Workflow(id="test-workflow-2", name="Test Workflow 2")
        repo.save(workflow1)
        repo.save(workflow2)
        
        # List the workflows
        workflows = repo.list()
        
        # Check that the list contains the correct workflows
        self.assertEqual(len(workflows), 2)
        workflow_ids = [w.id for w in workflows]
        self.assertIn("test-workflow-1", workflow_ids)
        self.assertIn("test-workflow-2", workflow_ids)
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Create and save a workflow
        workflow = Workflow(id="test-workflow", name="Test Workflow")
        repo.save(workflow)
        
        # Check that the workflow file exists
        file_path = os.path.join(self.test_dir, "test-workflow.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Delete the workflow
        repo.delete("test-workflow")
        
        # Check that the workflow file was deleted
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_nonexistent_workflow(self):
        """Test deleting a nonexistent workflow."""
        # Create the repository
        repo = WorkflowFSRepository(self.test_dir)
        
        # Try to delete a nonexistent workflow
        # This should not raise an exception
        repo.delete("nonexistent")


if __name__ == "__main__":
    unittest.main()
