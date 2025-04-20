"""Tests for the ExecutionService.

This module tests the ExecutionService implementation.
"""

import unittest
from unittest.mock import MagicMock, patch
import threading
import time
from typing import List, Optional, Dict, Any

from src.application.services.execution_service import ExecutionService
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credentials
from src.core.action_result import ActionResult
from src.core.exceptions import ValidationError, ServiceError

class TestExecutionService(unittest.TestCase):
    """Test case for ExecutionService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_repository = MagicMock()
        self.credential_repository = MagicMock()
        self.webdriver_factory = MagicMock()
        
        self.service = ExecutionService(
            self.workflow_repository,
            self.credential_repository,
            self.webdriver_factory
        )
    
    def test_execute_workflow_success(self):
        """Test executing a workflow successfully."""
        # Mock workflow
        workflow = MagicMock(spec=Workflow)
        workflow.name = "test_workflow"
        workflow.actions = []
        
        # Mock credential
        credential = MagicMock(spec=Credentials)
        credential.name = "test_credential"
        
        # Mock repositories
        self.workflow_repository.get.return_value = workflow
        self.credential_repository.get.return_value = credential
        
        # Execute workflow
        status = self.service.execute_workflow("test_workflow", "test_credential")
        
        # Check that the workflow was retrieved
        self.workflow_repository.get.assert_called_once_with("test_workflow")
        
        # Check that the credential was retrieved
        self.credential_repository.get.assert_called_once_with("test_credential")
        
        # Check that the execution was started
        self.assertEqual(status["status"], "starting")
        self.assertEqual(status["workflow_name"], "test_workflow")
        
        # Wait for execution to complete
        max_wait = 5  # seconds
        start_time = time.time()
        while self.service._execution_thread and self.service._execution_thread.is_alive():
            if time.time() - start_time > max_wait:
                self.fail("Execution thread did not complete in time")
            time.sleep(0.1)
    
    def test_execute_workflow_workflow_not_found(self):
        """Test executing a workflow that doesn't exist."""
        # Mock repository to return None for workflow
        self.workflow_repository.get.return_value = None
        
        # Execute workflow should raise ValidationError
        with self.assertRaises(ServiceError):
            self.service.execute_workflow("nonexistent_workflow")
        
        # Check that the workflow was attempted to be retrieved
        self.workflow_repository.get.assert_called_once_with("nonexistent_workflow")
    
    def test_execute_workflow_credential_not_found(self):
        """Test executing a workflow with a credential that doesn't exist."""
        # Mock workflow
        workflow = MagicMock(spec=Workflow)
        workflow.name = "test_workflow"
        
        # Mock repositories
        self.workflow_repository.get.return_value = workflow
        self.credential_repository.get.return_value = None
        
        # Execute workflow should raise ValidationError
        with self.assertRaises(ServiceError):
            self.service.execute_workflow("test_workflow", "nonexistent_credential")
        
        # Check that the workflow was retrieved
        self.workflow_repository.get.assert_called_once_with("test_workflow")
        
        # Check that the credential was attempted to be retrieved
        self.credential_repository.get.assert_called_once_with("nonexistent_credential")
    
    def test_execute_workflow_already_running(self):
        """Test executing a workflow when another is already running."""
        # Mock workflow
        workflow = MagicMock(spec=Workflow)
        workflow.name = "test_workflow"
        workflow.actions = []
        
        # Mock repository
        self.workflow_repository.get.return_value = workflow
        
        # Start a fake execution thread
        self.service._execution_thread = threading.Thread(target=lambda: time.sleep(1))
        self.service._execution_thread.start()
        
        # Execute workflow should raise ServiceError
        with self.assertRaises(ServiceError):
            self.service.execute_workflow("test_workflow")
        
        # Wait for thread to complete
        self.service._execution_thread.join()
    
    def test_stop_execution(self):
        """Test stopping a running workflow."""
        # Mock workflow
        workflow = MagicMock(spec=Workflow)
        workflow.name = "test_workflow"
        workflow.actions = []
        
        # Mock repository
        self.workflow_repository.get.return_value = workflow
        
        # Execute workflow
        self.service.execute_workflow("test_workflow")
        
        # Stop execution
        result = self.service.stop_execution()
        
        # Check that stop was requested
        self.assertTrue(result)
        self.assertTrue(self.service._stop_event.is_set())
        
        # Wait for execution to complete
        if self.service._execution_thread:
            self.service._execution_thread.join(timeout=1)
    
    def test_stop_execution_not_running(self):
        """Test stopping when no workflow is running."""
        # Stop execution
        result = self.service.stop_execution()
        
        # Check that stop was not requested
        self.assertFalse(result)
    
    def test_get_execution_status(self):
        """Test getting execution status."""
        # Set a test status
        test_status = {
            "status": "running",
            "workflow_name": "test_workflow",
            "progress": 50
        }
        self.service._execution_status = test_status
        
        # Get status
        status = self.service.get_execution_status()
        
        # Check that the status was returned
        self.assertEqual(status, test_status)
        
        # Check that the returned status is a copy
        self.assertIsNot(status, self.service._execution_status)
    
    def test_get_execution_results(self):
        """Test getting execution results."""
        # Set test results
        test_results = [MagicMock(spec=ActionResult) for _ in range(3)]
        self.service._execution_results = test_results
        
        # Get results
        results = self.service.get_execution_results()
        
        # Check that the results were returned
        self.assertEqual(len(results), 3)
        
        # Check that the returned results are a copy
        self.assertIsNot(results, self.service._execution_results)

if __name__ == "__main__":
    unittest.main()
