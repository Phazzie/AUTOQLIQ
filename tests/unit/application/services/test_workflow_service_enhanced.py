#!/usr/bin/env python3
"""
Enhanced unit tests for WorkflowService class in src/application/services/workflow_service.py.
"""

import unittest
from unittest.mock import MagicMock, patch, call
import threading
from typing import Dict, List, Any, Optional

# Import the module under test
from src.application.services.workflow_service import WorkflowService
from src.core.interfaces import IAction, IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.interfaces.service import IWebDriverService, IReportingService
from src.core.workflow.runner import WorkflowRunner
from src.core.exceptions import WorkflowError, CredentialError, ValidationError, RepositoryError, SerializationError
from src.infrastructure.webdrivers.base import BrowserType


class TestWorkflowService(unittest.TestCase):
    """
    Test cases for the WorkflowService class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 5 main responsibilities of WorkflowService:
    1. Workflow management (CRUD operations)
    2. Workflow execution coordination
    3. WebDriver initialization and disposal
    4. Error handling and reporting
    5. Execution logging and result collection
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for all dependencies
        self.mock_workflow_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_credential_repo = MagicMock(spec=ICredentialRepository)
        self.mock_webdriver_service = MagicMock(spec=IWebDriverService)
        self.mock_reporting_service = MagicMock(spec=IReportingService)
        
        # Create the service
        self.service = WorkflowService(
            workflow_repository=self.mock_workflow_repo,
            credential_repository=self.mock_credential_repo,
            webdriver_service=self.mock_webdriver_service,
            reporting_service=self.mock_reporting_service
        )
        
        # Create a sample workflow name and actions
        self.workflow_name = "TestWorkflow"
        self.mock_actions = [MagicMock(spec=IAction) for _ in range(3)]
    
    def test_init(self):
        """Test initialization."""
        # Test with valid parameters
        service = WorkflowService(
            workflow_repository=self.mock_workflow_repo,
            credential_repository=self.mock_credential_repo,
            webdriver_service=self.mock_webdriver_service,
            reporting_service=self.mock_reporting_service
        )
        
        self.assertEqual(service.workflow_repository, self.mock_workflow_repo)
        self.assertEqual(service.credential_repository, self.mock_credential_repo)
        self.assertEqual(service.webdriver_service, self.mock_webdriver_service)
        self.assertEqual(service.reporting_service, self.mock_reporting_service)
        
        # Test with None workflow repository (should raise)
        with self.assertRaises(ValueError):
            WorkflowService(
                workflow_repository=None,
                credential_repository=self.mock_credential_repo,
                webdriver_service=self.mock_webdriver_service,
                reporting_service=self.mock_reporting_service
            )
        
        # Test with None credential repository (should raise)
        with self.assertRaises(ValueError):
            WorkflowService(
                workflow_repository=self.mock_workflow_repo,
                credential_repository=None,
                webdriver_service=self.mock_webdriver_service,
                reporting_service=self.mock_reporting_service
            )
        
        # Test with None webdriver service (should raise)
        with self.assertRaises(ValueError):
            WorkflowService(
                workflow_repository=self.mock_workflow_repo,
                credential_repository=self.mock_credential_repo,
                webdriver_service=None,
                reporting_service=self.mock_reporting_service
            )
        
        # Test with None reporting service (should raise)
        with self.assertRaises(ValueError):
            WorkflowService(
                workflow_repository=self.mock_workflow_repo,
                credential_repository=self.mock_credential_repo,
                webdriver_service=self.mock_webdriver_service,
                reporting_service=None
            )
    
    def test_create_workflow(self):
        """Test creating a workflow."""
        # Configure mock
        self.mock_workflow_repo.create_workflow.return_value = None
        
        # Call the method
        result = self.service.create_workflow(self.workflow_name)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the repository was called
        self.mock_workflow_repo.create_workflow.assert_called_once_with(self.workflow_name)
    
    def test_create_workflow_error(self):
        """Test creating a workflow with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.create_workflow.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.create_workflow(self.workflow_name)
        
        # Verify the repository was called
        self.mock_workflow_repo.create_workflow.assert_called_once_with(self.workflow_name)
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Configure mock
        self.mock_workflow_repo.delete.return_value = True
        
        # Call the method
        result = self.service.delete_workflow(self.workflow_name)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the repository was called
        self.mock_workflow_repo.delete.assert_called_once_with(self.workflow_name)
    
    def test_delete_workflow_not_found(self):
        """Test deleting a non-existent workflow."""
        # Configure mock
        self.mock_workflow_repo.delete.return_value = False
        
        # Call the method
        result = self.service.delete_workflow(self.workflow_name)
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify the repository was called
        self.mock_workflow_repo.delete.assert_called_once_with(self.workflow_name)
    
    def test_delete_workflow_error(self):
        """Test deleting a workflow with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.delete.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.delete_workflow(self.workflow_name)
        
        # Verify the repository was called
        self.mock_workflow_repo.delete.assert_called_once_with(self.workflow_name)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        # Configure mock
        expected_workflows = ["Workflow1", "Workflow2", "Workflow3"]
        self.mock_workflow_repo.list_workflows.return_value = expected_workflows
        
        # Call the method
        result = self.service.list_workflows()
        
        # Verify the result
        self.assertEqual(result, expected_workflows)
        
        # Verify the repository was called
        self.mock_workflow_repo.list_workflows.assert_called_once()
    
    def test_list_workflows_error(self):
        """Test listing workflows with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.list_workflows.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.list_workflows()
        
        # Verify the repository was called
        self.mock_workflow_repo.list_workflows.assert_called_once()
    
    def test_get_workflow(self):
        """Test getting a workflow's actions."""
        # Configure mock
        self.mock_workflow_repo.load.return_value = self.mock_actions
        
        # Call the method
        result = self.service.get_workflow(self.workflow_name)
        
        # Verify the result
        self.assertEqual(result, self.mock_actions)
        
        # Verify the repository was called
        self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
    
    def test_get_workflow_error(self):
        """Test getting a workflow's actions with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.load.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.get_workflow(self.workflow_name)
        
        # Verify the repository was called
        self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
    
    def test_save_workflow(self):
        """Test saving a workflow."""
        # Configure mock
        self.mock_workflow_repo.save.return_value = None
        
        # Call the method
        result = self.service.save_workflow(self.workflow_name, self.mock_actions)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the repository was called
        self.mock_workflow_repo.save.assert_called_once_with(self.workflow_name, self.mock_actions)
    
    def test_save_workflow_error(self):
        """Test saving a workflow with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.save.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.save_workflow(self.workflow_name, self.mock_actions)
        
        # Verify the repository was called
        self.mock_workflow_repo.save.assert_called_once_with(self.workflow_name, self.mock_actions)
    
    def test_get_workflow_metadata(self):
        """Test getting workflow metadata."""
        # Configure mock
        expected_metadata = {"created": "2025-04-01", "modified": "2025-04-08", "action_count": 3}
        self.mock_workflow_repo.get_metadata.return_value = expected_metadata
        
        # Call the method
        result = self.service.get_workflow_metadata(self.workflow_name)
        
        # Verify the result
        self.assertEqual(result, expected_metadata)
        
        # Verify the repository was called
        self.mock_workflow_repo.get_metadata.assert_called_once_with(self.workflow_name)
    
    def test_get_workflow_metadata_error(self):
        """Test getting workflow metadata with repository error."""
        # Configure mock to raise
        self.mock_workflow_repo.get_metadata.side_effect = RepositoryError("Test error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.get_workflow_metadata(self.workflow_name)
        
        # Verify the repository was called
        self.mock_workflow_repo.get_metadata.assert_called_once_with(self.workflow_name)
    
    def test_run_workflow_success(self):
        """Test running a workflow successfully."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        
        # Mock the WorkflowRunner.run method
        expected_result = {
            "workflow_name": self.workflow_name,
            "final_status": "SUCCESS",
            "action_results": [{"status": "SUCCESS", "message": "Action succeeded"} for _ in range(3)]
        }
        
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.return_value = expected_result
            
            # Call the method
            result = self.service.run_workflow(self.workflow_name)
            
            # Verify the result
            self.assertEqual(result, expected_result)
            
            # Verify the dependencies were called
            self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
            self.mock_webdriver_service.create_web_driver.assert_called_once_with(browser_type_str=BrowserType.CHROME.value)
            mock_runner_class.assert_called_once_with(
                mock_driver, 
                self.mock_credential_repo, 
                self.mock_workflow_repo, 
                None  # stop_event
            )
            mock_runner.run.assert_called_once_with(self.mock_actions, workflow_name=self.workflow_name)
            self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver)
            self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_result)
    
    def test_run_workflow_with_credential_and_browser(self):
        """Test running a workflow with credential and specific browser."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        
        # Mock the WorkflowRunner.run method
        expected_result = {
            "workflow_name": self.workflow_name,
            "final_status": "SUCCESS",
            "action_results": [{"status": "SUCCESS", "message": "Action succeeded"} for _ in range(3)]
        }
        
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.return_value = expected_result
            
            # Call the method with credential and custom browser
            credential_name = "TestCredential"
            browser_type = BrowserType.FIREFOX
            result = self.service.run_workflow(
                self.workflow_name,
                credential_name=credential_name,
                browser_type=browser_type
            )
            
            # Verify the result
            self.assertEqual(result, expected_result)
            
            # Verify the dependencies were called with correct parameters
            self.mock_webdriver_service.create_web_driver.assert_called_once_with(browser_type_str=browser_type.value)
    
    def test_run_workflow_with_stop_event(self):
        """Test running a workflow with a stop event."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        
        # Create a stop event
        stop_event = threading.Event()
        
        # Mock the WorkflowRunner.run method
        expected_result = {
            "workflow_name": self.workflow_name,
            "final_status": "STOPPED",
            "error_message": "Execution stopped by user request.",
            "action_results": []
        }
        
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.return_value = expected_result
            
            # Call the method with stop event
            result = self.service.run_workflow(
                self.workflow_name,
                stop_event=stop_event
            )
            
            # Verify the result
            self.assertEqual(result, expected_result)
            
            # Verify the runner was created with the stop event
            mock_runner_class.assert_called_once_with(
                mock_driver, 
                self.mock_credential_repo, 
                self.mock_workflow_repo, 
                stop_event
            )
    
    def test_run_workflow_load_error(self):
        """Test running a workflow with an error loading the workflow."""
        # Configure mocks to raise on load
        self.mock_workflow_repo.load.side_effect = RepositoryError("Test load error")
        
        # Call the method - should re-raise
        with self.assertRaises(RepositoryError):
            self.service.run_workflow(self.workflow_name)
        
        # Verify repository was called but not webdriver_service
        self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
        self.mock_webdriver_service.create_web_driver.assert_not_called()
        self.mock_webdriver_service.dispose_web_driver.assert_not_called()
    
    def test_run_workflow_webdriver_error(self):
        """Test running a workflow with an error creating the webdriver."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        self.mock_webdriver_service.create_web_driver.side_effect = Exception("Test webdriver error")
        
        # Call the method - should wrap in WorkflowError
        with self.assertRaises(WorkflowError):
            self.service.run_workflow(self.workflow_name)
        
        # Verify repository and webdriver_service were called
        self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
        self.mock_webdriver_service.create_web_driver.assert_called_once()
        self.mock_webdriver_service.dispose_web_driver.assert_not_called()
    
    def test_run_workflow_execution_error(self):
        """Test running a workflow with an error during execution."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        
        # Mock the WorkflowRunner.run method to raise
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.side_effect = WorkflowError("Test execution error")
            
            # Call the method - should re-raise
            with self.assertRaises(WorkflowError):
                self.service.run_workflow(self.workflow_name)
            
            # Verify the dependencies were called
            self.mock_workflow_repo.load.assert_called_once_with(self.workflow_name)
            self.mock_webdriver_service.create_web_driver.assert_called_once()
            mock_runner.run.assert_called_once()
            
            # Verify webdriver was disposed
            self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver)
            
            # Verify reporting service was called to save error log
            self.mock_reporting_service.save_execution_log.assert_called_once()
            # Check error fields in the log
            log_arg = self.mock_reporting_service.save_execution_log.call_args[0][0]
            self.assertEqual(log_arg["workflow_name"], self.workflow_name)
            self.assertEqual(log_arg["final_status"], "FAILED")
            self.assertIn("Test execution error", log_arg["error_message"])
    
    def test_run_workflow_unexpected_error(self):
        """Test running a workflow with an unexpected error."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        
        # Mock the WorkflowRunner.run method to raise an unexpected error
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.side_effect = ValueError("Unexpected test error")
            
            # Call the method - should wrap in WorkflowError
            with self.assertRaises(WorkflowError):
                self.service.run_workflow(self.workflow_name)
            
            # Verify webdriver was disposed
            self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver)
            
            # Verify reporting service was called to save error log
            self.mock_reporting_service.save_execution_log.assert_called_once()
            # Check error fields in the log
            log_arg = self.mock_reporting_service.save_execution_log.call_args[0][0]
            self.assertEqual(log_arg["workflow_name"], self.workflow_name)
            self.assertEqual(log_arg["final_status"], "FAILED")
            self.assertIn("Unexpected error", log_arg["error_message"])
    
    def test_run_workflow_dispose_error(self):
        """Test running a workflow with an error disposing the WebDriver."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        self.mock_webdriver_service.dispose_web_driver.side_effect = Exception("Test dispose error")
        
        # Mock the WorkflowRunner.run method
        expected_result = {
            "workflow_name": self.workflow_name,
            "final_status": "SUCCESS",
            "action_results": []
        }
        
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.return_value = expected_result
            
            # Call the method - should not raise from dispose error
            result = self.service.run_workflow(self.workflow_name)
            
            # Verify the result
            self.assertEqual(result, expected_result)
            
            # Verify dispose was attempted
            self.mock_webdriver_service.dispose_web_driver.assert_called_once_with(mock_driver)
            
            # Verify log was still saved
            self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_result)
    
    def test_run_workflow_reporting_error(self):
        """Test running a workflow with an error saving the report."""
        # Configure mocks
        self.mock_workflow_repo.load.return_value = self.mock_actions
        mock_driver = MagicMock(spec=IWebDriver)
        self.mock_webdriver_service.create_web_driver.return_value = mock_driver
        self.mock_reporting_service.save_execution_log.side_effect = Exception("Test reporting error")
        
        # Mock the WorkflowRunner.run method
        expected_result = {
            "workflow_name": self.workflow_name,
            "final_status": "SUCCESS",
            "action_results": []
        }
        
        with patch('src.application.services.workflow_service.WorkflowRunner') as mock_runner_class:
            mock_runner = mock_runner_class.return_value
            mock_runner.run.return_value = expected_result
            
            # Call the method - should not raise from reporting error
            result = self.service.run_workflow(self.workflow_name)
            
            # Verify the result
            self.assertEqual(result, expected_result)
            
            # Verify reporting was attempted
            self.mock_reporting_service.save_execution_log.assert_called_once_with(expected_result)


if __name__ == '__main__':
    unittest.main()