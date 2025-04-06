"""Tests for the WorkflowService class."""
import unittest
from unittest.mock import patch, MagicMock, call

from src.core.exceptions import WorkflowError
from src.core.interfaces import IAction, IWebDriver, IWorkflowRepository, ICredentialRepository
from src.application.interfaces import IWorkflowService
from src.application.services.workflow_service import WorkflowService


class TestWorkflowService(unittest.TestCase):
    """Test cases for the WorkflowService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_repo = MagicMock(spec=IWorkflowRepository)
        self.credential_repo = MagicMock(spec=ICredentialRepository)
        self.web_driver_factory = MagicMock()
        self.web_driver = MagicMock(spec=IWebDriver)
        self.web_driver_factory.create_web_driver.return_value = self.web_driver

        self.service = WorkflowService(
            workflow_repository=self.workflow_repo,
            credential_repository=self.credential_repo,
            web_driver_factory=self.web_driver_factory
        )

        # Sample actions for testing
        self.action1 = MagicMock(spec=IAction)
        self.action2 = MagicMock(spec=IAction)
        self.sample_actions = [self.action1, self.action2]

    def test_create_workflow(self):
        """Test that create_workflow creates a new workflow."""
        # Set up mock
        self.workflow_repo.save.return_value = None

        # Call create_workflow
        result = self.service.create_workflow("test_workflow")

        # Check result
        self.assertTrue(result)

        # Verify workflow_repo.save was called with correct arguments
        self.workflow_repo.save.assert_called_once_with("test_workflow", [])

    def test_create_workflow_error(self):
        """Test that create_workflow raises WorkflowError when creating a workflow fails."""
        # Set up mock to raise an exception
        self.workflow_repo.save.side_effect = WorkflowError("Create workflow failed")

        # Try to call create_workflow
        with self.assertRaises(WorkflowError):
            self.service.create_workflow("test_workflow")

    def test_delete_workflow(self):
        """Test that delete_workflow deletes a workflow."""
        # Set up mock
        self.workflow_repo.delete.return_value = True

        # Call delete_workflow
        result = self.service.delete_workflow("test_workflow")

        # Check result
        self.assertTrue(result)

        # Verify workflow_repo.delete was called with correct arguments
        self.workflow_repo.delete.assert_called_once_with("test_workflow")

    def test_delete_workflow_error(self):
        """Test that delete_workflow raises WorkflowError when deleting a workflow fails."""
        # Set up mock to raise an exception
        self.workflow_repo.delete.side_effect = WorkflowError("Delete workflow failed")

        # Try to call delete_workflow
        with self.assertRaises(WorkflowError):
            self.service.delete_workflow("test_workflow")

    def test_list_workflows(self):
        """Test that list_workflows returns a list of workflows."""
        # Set up mock
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]

        # Call list_workflows
        result = self.service.list_workflows()

        # Check result
        self.assertEqual(result, ["workflow1", "workflow2"])

        # Verify workflow_repo.list_workflows was called
        self.workflow_repo.list_workflows.assert_called_once()

    def test_list_workflows_error(self):
        """Test that list_workflows raises WorkflowError when listing workflows fails."""
        # Set up mock to raise an exception
        self.workflow_repo.list_workflows.side_effect = WorkflowError("List workflows failed")

        # Try to call list_workflows
        with self.assertRaises(WorkflowError):
            self.service.list_workflows()

    def test_get_workflow(self):
        """Test that get_workflow returns a workflow."""
        # Set up mock
        self.workflow_repo.load.return_value = self.sample_actions

        # Call get_workflow
        result = self.service.get_workflow("test_workflow")

        # Check result
        self.assertEqual(result, self.sample_actions)

        # Verify workflow_repo.load was called with correct arguments
        self.workflow_repo.load.assert_called_once_with("test_workflow")

    def test_get_workflow_error(self):
        """Test that get_workflow raises WorkflowError when getting a workflow fails."""
        # Set up mock to raise an exception
        self.workflow_repo.load.side_effect = WorkflowError("Get workflow failed")

        # Try to call get_workflow
        with self.assertRaises(WorkflowError):
            self.service.get_workflow("test_workflow")

    def test_save_workflow(self):
        """Test that save_workflow saves a workflow."""
        # Set up mock
        self.workflow_repo.save.return_value = True

        # Call save_workflow
        result = self.service.save_workflow("test_workflow", self.sample_actions)

        # Check result
        self.assertTrue(result)

        # Verify workflow_repo.save was called with correct arguments
        self.workflow_repo.save.assert_called_once_with("test_workflow", self.sample_actions)

    def test_save_workflow_error(self):
        """Test that save_workflow raises WorkflowError when saving a workflow fails."""
        # Set up mock to raise an exception
        self.workflow_repo.save.side_effect = WorkflowError("Save workflow failed")

        # Try to call save_workflow
        with self.assertRaises(WorkflowError):
            self.service.save_workflow("test_workflow", self.sample_actions)

    @patch("src.application.services.workflow_service.WorkflowRunner")
    def test_run_workflow(self, mock_workflow_runner_class):
        """Test that run_workflow runs a workflow."""
        # Set up mocks
        mock_workflow_runner = MagicMock()
        mock_workflow_runner_class.return_value = mock_workflow_runner
        mock_workflow_runner.run_workflow.return_value = True

        self.workflow_repo.load.return_value = self.sample_actions

        # Call run_workflow
        result = self.service.run_workflow("test_workflow")

        # Check result
        self.assertTrue(result)

        # Verify workflow_repo.load was called
        self.workflow_repo.load.assert_called_with("test_workflow")

        # Verify WorkflowRunner was initialized with correct arguments
        mock_workflow_runner_class.assert_called_once()

        # Verify run_workflow was called
        mock_workflow_runner.run_workflow.assert_called_once()

    @patch("src.application.services.workflow_service.WorkflowRunner")
    def test_run_workflow_with_credential(self, mock_workflow_runner_class):
        """Test that run_workflow runs a workflow with a credential."""
        # Set up mocks
        mock_workflow_runner = MagicMock()
        mock_workflow_runner_class.return_value = mock_workflow_runner
        mock_workflow_runner.run_workflow.return_value = True

        self.workflow_repo.load.return_value = self.sample_actions
        self.credential_repo.get_by_name.return_value = {"username": "test_user", "password": "test_pass"}

        # Call run_workflow
        result = self.service.run_workflow("test_workflow", "test_credential")

        # Check result
        self.assertTrue(result)

        # Verify workflow_repo.load was called
        self.workflow_repo.load.assert_called_with("test_workflow")

        # Verify credential_repo.get_by_name was called with correct arguments
        self.credential_repo.get_by_name.assert_called_with("test_credential")

        # Verify WorkflowRunner was initialized with correct arguments
        mock_workflow_runner_class.assert_called_once()

        # Verify run_workflow was called
        mock_workflow_runner.run_workflow.assert_called_once()

    def test_run_workflow_error(self):
        """Test that run_workflow raises WorkflowError when running a workflow fails."""
        # Set up mock to raise an exception
        self.workflow_repo.load.side_effect = WorkflowError("Run workflow failed")

        # Try to call run_workflow
        with self.assertRaises(WorkflowError):
            self.service.run_workflow("test_workflow")

    def test_get_workflow_metadata(self):
        """Test that get_workflow_metadata returns workflow metadata."""
        # Set up mock
        expected_metadata = {"name": "test_workflow", "version": "1.0", "description": "Test workflow"}
        self.workflow_repo.get_metadata.return_value = expected_metadata

        # Call get_workflow_metadata
        result = self.service.get_workflow_metadata("test_workflow")

        # Check result
        self.assertEqual(result, expected_metadata)

        # Verify workflow_repo.get_metadata was called with correct arguments
        self.workflow_repo.get_metadata.assert_called_once_with("test_workflow")

    def test_get_workflow_metadata_error(self):
        """Test that get_workflow_metadata raises WorkflowError when getting workflow metadata fails."""
        # Set up mock to raise an exception
        self.workflow_repo.get_metadata.side_effect = WorkflowError("Get workflow metadata failed")

        # Try to call get_workflow_metadata
        with self.assertRaises(WorkflowError):
            self.service.get_workflow_metadata("test_workflow")


if __name__ == "__main__":
    unittest.main()
