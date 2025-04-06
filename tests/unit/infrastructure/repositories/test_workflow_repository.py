"""Tests for the FileSystemWorkflowRepository class."""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.core.exceptions import WorkflowError
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository

class TestFileSystemWorkflowRepository(unittest.TestCase):
    """Test cases for the FileSystemWorkflowRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workflows_dir = self.temp_dir.name
        self.repo = FileSystemWorkflowRepository(self.workflows_dir)

        # Sample workflow actions for testing
        self.action1 = MagicMock()
        self.action1.to_dict.return_value = {"type": "action1", "param": "value1"}

        self.action2 = MagicMock()
        self.action2.to_dict.return_value = {"type": "action2", "param": "value2"}

        self.sample_actions = [self.action1, self.action2]

        # Sample workflow data for testing
        self.sample_workflow_data = [
            {"type": "Navigate", "url": "https://example.com"},
            {"type": "Click", "selector": "#button"}
        ]

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_create_workflow(self):
        """Test that create_workflow creates a new empty workflow file."""
        # Create workflow
        self.repo.create_workflow("test_workflow")

        # Check that the workflow file was created
        workflow_file = os.path.join(self.workflows_dir, "test_workflow.json")
        self.assertTrue(os.path.exists(workflow_file))

        # Check that the workflow file contains an empty list
        with open(workflow_file, "r") as f:
            workflow_data = json.load(f)

        self.assertEqual(workflow_data, [])

    def test_create_workflow_invalid_name_empty(self):
        """Test that create_workflow raises WorkflowError when the name is empty."""
        # Try to create workflow with empty name
        with self.assertRaises(WorkflowError):
            self.repo.create_workflow("")

    def test_create_workflow_invalid_name_format(self):
        """Test that create_workflow raises WorkflowError when the name has invalid format."""
        # Try to create workflow with invalid name
        with self.assertRaises(WorkflowError):
            self.repo.create_workflow("invalid name")  # Contains space

    def test_create_workflow_already_exists(self):
        """Test that create_workflow raises WorkflowError when the workflow already exists."""
        # Create workflow
        self.repo.create_workflow("test_workflow")

        # Try to create workflow with same name
        with self.assertRaises(WorkflowError):
            self.repo.create_workflow("test_workflow")

    @patch("src.infrastructure.repositories.workflow_repository.serialize_actions")
    def test_save(self, mock_serialize_actions):
        """Test that save saves a workflow to a file."""
        # Set up mock return value
        mock_serialize_actions.return_value = self.sample_workflow_data

        # Save workflow
        self.repo.save("test_workflow", self.sample_actions)

        # Check that the workflow file was created
        workflow_file = os.path.join(self.workflows_dir, "test_workflow.json")
        self.assertTrue(os.path.exists(workflow_file))

        # Verify serialize_actions was called
        mock_serialize_actions.assert_called_once_with(self.sample_actions)

    def test_save_invalid_name_empty(self):
        """Test that save raises WorkflowError when the name is empty."""
        # Try to save workflow with empty name
        with self.assertRaises(WorkflowError):
            self.repo.save("", self.sample_actions)

    def test_save_invalid_name_format(self):
        """Test that save raises WorkflowError when the name has invalid format."""
        # Try to save workflow with invalid name
        with self.assertRaises(WorkflowError):
            self.repo.save("invalid name", self.sample_actions)  # Contains space

    def test_save_empty_actions(self):
        """Test that save raises WorkflowError when the actions list is empty."""
        # Try to save workflow with empty actions list
        with self.assertRaises(WorkflowError):
            self.repo.save("test_workflow", [])

    @patch("src.infrastructure.repositories.workflow_repository.deserialize_actions")
    def test_load(self, mock_deserialize_actions):
        """Test that load loads a workflow from a file."""
        # Set up mock return value
        mock_deserialize_actions.return_value = self.sample_actions

        # Create workflow file
        workflow_file = os.path.join(self.workflows_dir, "test_workflow.json")
        with open(workflow_file, "w") as f:
            json.dump(self.sample_workflow_data, f)

        # Load workflow
        result = self.repo.load("test_workflow")

        # Check result
        self.assertEqual(result, self.sample_actions)

        # Verify deserialize_actions was called
        mock_deserialize_actions.assert_called_once()

    def test_load_not_found(self):
        """Test that load raises WorkflowError when the workflow doesn't exist."""
        # Try to load nonexistent workflow
        with self.assertRaises(WorkflowError):
            self.repo.load("nonexistent_workflow")

    def test_load_invalid_json(self):
        """Test that load raises WorkflowError when the workflow file contains invalid JSON."""
        # Create workflow file with invalid JSON
        workflow_file = os.path.join(self.workflows_dir, "invalid_workflow.json")
        with open(workflow_file, "w") as f:
            f.write("invalid json")

        # Try to load workflow
        with self.assertRaises(WorkflowError):
            self.repo.load("invalid_workflow")

    def test_list_workflows(self):
        """Test that list_workflows returns a list of workflow names."""
        # Create workflow files
        workflow_files = [
            os.path.join(self.workflows_dir, "workflow1.json"),
            os.path.join(self.workflows_dir, "workflow2.json")
        ]

        for file in workflow_files:
            with open(file, "w") as f:
                json.dump([], f)

        # List workflows
        result = self.repo.list_workflows()

        # Check result
        self.assertEqual(set(result), {"workflow1", "workflow2"})

    def test_list_workflows_empty(self):
        """Test that list_workflows returns an empty list when there are no workflows."""
        # List workflows
        result = self.repo.list_workflows()

        # Check result
        self.assertEqual(result, [])

    def test_delete_found(self):
        """Test that delete removes a workflow file."""
        # Create workflow file
        workflow_file = os.path.join(self.workflows_dir, "test_workflow.json")
        with open(workflow_file, "w") as f:
            json.dump([], f)

        # Delete workflow
        result = self.repo.delete("test_workflow")

        # Check result
        self.assertTrue(result)

        # Check that the workflow file was removed
        self.assertFalse(os.path.exists(workflow_file))

    def test_delete_not_found(self):
        """Test that delete returns False when the workflow doesn't exist."""
        # Delete nonexistent workflow
        result = self.repo.delete("nonexistent_workflow")

        # Check result
        self.assertFalse(result)

    @patch("src.infrastructure.repositories.workflow_repository.extract_workflow_metadata")
    def test_get_metadata(self, mock_extract_metadata):
        """Test that get_metadata returns metadata for a workflow."""
        # Set up mock return value
        mock_metadata = {
            "name": "test_workflow",
            "version": "unknown",
            "legacy_format": True
        }
        mock_extract_metadata.return_value = mock_metadata

        # Create workflow file
        workflow_file = os.path.join(self.workflows_dir, "test_workflow.json")
        with open(workflow_file, "w") as f:
            json.dump(self.sample_workflow_data, f)

        # Get metadata
        result = self.repo.get_metadata("test_workflow")

        # Check result
        self.assertEqual(result, mock_metadata)

        # Verify extract_workflow_metadata was called
        mock_extract_metadata.assert_called_once()

    def test_get_metadata_not_found(self):
        """Test that get_metadata raises WorkflowError when the workflow doesn't exist."""
        # Try to get metadata for nonexistent workflow
        with self.assertRaises(WorkflowError):
            self.repo.get_metadata("nonexistent_workflow")

    def test_get_metadata_invalid_json(self):
        """Test that get_metadata raises WorkflowError when the workflow file contains invalid JSON."""
        # Create workflow file with invalid JSON
        workflow_file = os.path.join(self.workflows_dir, "invalid_workflow.json")
        with open(workflow_file, "w") as f:
            f.write("invalid json")

        # Try to get metadata
        with self.assertRaises(WorkflowError):
            self.repo.get_metadata("invalid_workflow")

    def test_get_workflow_path(self):
        """Test that _get_workflow_path returns the correct file path for a workflow."""
        # Get workflow path
        result = self.repo._get_workflow_path("test_workflow")

        # Check result
        expected_path = os.path.join(self.workflows_dir, "test_workflow.json")
        self.assertEqual(result, expected_path)

    def test_validate_workflow_name_valid(self):
        """Test that _validate_workflow_name doesn't raise an error for a valid name."""
        # Valid names
        valid_names = [
            "test_workflow",
            "test-workflow",
            "testWorkflow",
            "test123"
        ]

        # Validate names (should not raise an error)
        for name in valid_names:
            self.repo._validate_workflow_name(name)

    def test_validate_workflow_name_empty(self):
        """Test that _validate_workflow_name raises WorkflowError when the name is empty."""
        # Try to validate empty name
        with self.assertRaises(WorkflowError):
            self.repo._validate_workflow_name("")

    def test_validate_workflow_name_invalid_format(self):
        """Test that _validate_workflow_name raises WorkflowError when the name has invalid format."""
        # Invalid names
        invalid_names = [
            "test workflow",  # Contains space
            "test.workflow",  # Contains period
            "test/workflow",  # Contains slash
            "test@workflow"   # Contains special character
        ]

        # Try to validate invalid names
        for name in invalid_names:
            with self.assertRaises(WorkflowError):
                self.repo._validate_workflow_name(name)

if __name__ == "__main__":
    unittest.main()
