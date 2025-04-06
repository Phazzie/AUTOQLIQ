"""Tests for the workflow runner presenter."""
import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.core.interfaces import IWorkflowRepository, ICredentialRepository, IWebDriver, IAction
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError

class TestWorkflowRunnerPresenter(unittest.TestCase):
    """Test cases for the WorkflowRunnerPresenter class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock view
        self.view = Mock()
        
        # Create mock repositories
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.credential_repo = Mock(spec=ICredentialRepository)
        
        # Create a mock webdriver factory
        self.webdriver_factory = Mock()
        self.mock_webdriver = Mock(spec=IWebDriver)
        self.webdriver_factory.create_webdriver.return_value = self.mock_webdriver
        
        # Create a mock workflow runner
        self.workflow_runner = Mock()
        
        # Create the presenter
        self.presenter = WorkflowRunnerPresenter(
            self.workflow_repo,
            self.credential_repo,
            self.webdriver_factory,
            self.workflow_runner
        )
        self.presenter.view = self.view
        
        # Set up test data
        self.test_workflow_name = "test_workflow"
        self.test_credential_name = "test_credential"
        self.test_credential = {"name": "test_credential", "username": "user", "password": "pass"}
        self.test_actions = [Mock(spec=IAction), Mock(spec=IAction)]

    def test_initialization(self):
        """Test that a WorkflowRunnerPresenter can be initialized with the required parameters."""
        # Check that the presenter was initialized correctly
        self.assertEqual(self.presenter.workflow_repository, self.workflow_repo)
        self.assertEqual(self.presenter.credential_repository, self.credential_repo)
        self.assertEqual(self.presenter.webdriver_factory, self.webdriver_factory)
        self.assertEqual(self.presenter.workflow_runner, self.workflow_runner)
        self.assertEqual(self.presenter.view, self.view)

    def test_get_workflow_list(self):
        """Test that get_workflow_list returns a list of workflows from the repository."""
        # Set up the mock repository to return a list of workflows
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]
        
        # Call the method
        result = self.presenter.get_workflow_list()
        
        # Check the result
        self.assertEqual(result, ["workflow1", "workflow2"])
        
        # Check that the repository method was called
        self.workflow_repo.list_workflows.assert_called_once()

    def test_get_credential_list(self):
        """Test that get_credential_list returns a list of credentials from the repository."""
        # Set up the mock repository to return a list of credentials
        self.credential_repo.get_all.return_value = [self.test_credential]
        
        # Call the method
        result = self.presenter.get_credential_list()
        
        # Check the result
        self.assertEqual(result, [self.test_credential])
        
        # Check that the repository method was called
        self.credential_repo.get_all.assert_called_once()

    def test_run_workflow_success(self):
        """Test that run_workflow runs a workflow with the specified credential."""
        # Set up the mock repositories
        self.workflow_repo.load.return_value = self.test_actions
        self.credential_repo.get_by_name.return_value = self.test_credential
        
        # Set up the mock workflow runner
        self.workflow_runner.run_workflow.return_value = True
        
        # Call the method
        result = self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the repository methods were called
        self.workflow_repo.load.assert_called_once_with(self.test_workflow_name)
        self.credential_repo.get_by_name.assert_called_once_with(self.test_credential_name)
        
        # Check that the webdriver factory was called
        self.webdriver_factory.create_webdriver.assert_called_once()
        
        # Check that the workflow runner was called
        self.workflow_runner.run_workflow.assert_called_once_with(
            self.test_actions,
            self.mock_webdriver,
            self.test_credential
        )

    def test_run_workflow_workflow_error(self):
        """Test that run_workflow handles WorkflowError."""
        # Set up the mock repository to raise a WorkflowError
        self.workflow_repo.load.side_effect = WorkflowError("Test error")
        
        # Call the method and check that it raises the expected exception
        with self.assertRaises(WorkflowError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)
        
        # Check that the repository method was called
        self.workflow_repo.load.assert_called_once_with(self.test_workflow_name)
        
        # Check that the webdriver factory was not called
        self.webdriver_factory.create_webdriver.assert_not_called()
        
        # Check that the workflow runner was not called
        self.workflow_runner.run_workflow.assert_not_called()

    def test_run_workflow_credential_error(self):
        """Test that run_workflow handles CredentialError."""
        # Set up the mock repositories
        self.workflow_repo.load.return_value = self.test_actions
        self.credential_repo.get_by_name.side_effect = CredentialError("Test error")
        
        # Call the method and check that it raises the expected exception
        with self.assertRaises(CredentialError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)
        
        # Check that the repository methods were called
        self.workflow_repo.load.assert_called_once_with(self.test_workflow_name)
        self.credential_repo.get_by_name.assert_called_once_with(self.test_credential_name)
        
        # Check that the webdriver factory was not called
        self.webdriver_factory.create_webdriver.assert_not_called()
        
        # Check that the workflow runner was not called
        self.workflow_runner.run_workflow.assert_not_called()

    def test_run_workflow_webdriver_error(self):
        """Test that run_workflow handles WebDriverError."""
        # Set up the mock repositories
        self.workflow_repo.load.return_value = self.test_actions
        self.credential_repo.get_by_name.return_value = self.test_credential
        
        # Set up the mock webdriver factory to raise a WebDriverError
        self.webdriver_factory.create_webdriver.side_effect = WebDriverError("Test error")
        
        # Call the method and check that it raises the expected exception
        with self.assertRaises(WebDriverError):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)
        
        # Check that the repository methods were called
        self.workflow_repo.load.assert_called_once_with(self.test_workflow_name)
        self.credential_repo.get_by_name.assert_called_once_with(self.test_credential_name)
        
        # Check that the webdriver factory was called
        self.webdriver_factory.create_webdriver.assert_called_once()
        
        # Check that the workflow runner was not called
        self.workflow_runner.run_workflow.assert_not_called()

    def test_run_workflow_unexpected_error(self):
        """Test that run_workflow handles unexpected errors."""
        # Set up the mock repositories
        self.workflow_repo.load.return_value = self.test_actions
        self.credential_repo.get_by_name.return_value = self.test_credential
        
        # Set up the mock workflow runner to raise an unexpected error
        self.workflow_runner.run_workflow.side_effect = Exception("Test error")
        
        # Call the method and check that it raises the expected exception
        with self.assertRaises(Exception):
            self.presenter.run_workflow(self.test_workflow_name, self.test_credential_name)
        
        # Check that the repository methods were called
        self.workflow_repo.load.assert_called_once_with(self.test_workflow_name)
        self.credential_repo.get_by_name.assert_called_once_with(self.test_credential_name)
        
        # Check that the webdriver factory was called
        self.webdriver_factory.create_webdriver.assert_called_once()
        
        # Check that the workflow runner was called
        self.workflow_runner.run_workflow.assert_called_once_with(
            self.test_actions,
            self.mock_webdriver,
            self.test_credential
        )

    def test_stop_workflow_success(self):
        """Test that stop_workflow stops a running workflow."""
        # Set up the mock workflow runner
        self.workflow_runner.stop_workflow.return_value = True
        
        # Call the method
        result = self.presenter.stop_workflow()
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the workflow runner was called
        self.workflow_runner.stop_workflow.assert_called_once()

    def test_stop_workflow_failure(self):
        """Test that stop_workflow handles errors."""
        # Set up the mock workflow runner to raise an error
        self.workflow_runner.stop_workflow.side_effect = Exception("Test error")
        
        # Call the method and check that it raises the expected exception
        with self.assertRaises(Exception):
            self.presenter.stop_workflow()
        
        # Check that the workflow runner was called
        self.workflow_runner.stop_workflow.assert_called_once()

if __name__ == "__main__":
    unittest.main()
