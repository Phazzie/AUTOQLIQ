"""Tests for service interfaces.

This module tests that the service interfaces are properly defined and can be implemented.
"""

import unittest
from unittest.mock import MagicMock
from typing import List, Optional, Dict, Any

from src.application.interfaces.service_interfaces import (
    IWorkflowService, ICredentialService, IExecutionService
)
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credentials
from src.core.action_result import ActionResult

class TestServiceInterfaces(unittest.TestCase):
    """Test case for service interfaces."""
    
    def test_workflow_service_interface(self):
        """Test that IWorkflowService can be implemented."""
        
        class MockWorkflowService(IWorkflowService):
            """Mock implementation of IWorkflowService."""
            
            def create_workflow(self, name: str, description: str = "") -> Workflow:
                return MagicMock(spec=Workflow)
            
            def save_workflow(self, workflow: Workflow) -> None:
                pass
            
            def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
                return MagicMock(spec=Workflow)
            
            def list_workflows(self) -> List[Workflow]:
                return [MagicMock(spec=Workflow)]
            
            def delete_workflow(self, workflow_id: str) -> None:
                pass
        
        # Create an instance of the mock service
        service = MockWorkflowService()
        
        # Test that the service implements the interface
        self.assertIsInstance(service, IWorkflowService)
        
        # Test that the methods can be called
        workflow = service.create_workflow("test")
        self.assertIsNotNone(workflow)
        
        service.save_workflow(workflow)
        
        retrieved_workflow = service.get_workflow("test")
        self.assertIsNotNone(retrieved_workflow)
        
        workflows = service.list_workflows()
        self.assertEqual(len(workflows), 1)
        
        service.delete_workflow("test")
    
    def test_credential_service_interface(self):
        """Test that ICredentialService can be implemented."""
        
        class MockCredentialService(ICredentialService):
            """Mock implementation of ICredentialService."""
            
            def create_credential(self, name: str, username: str, password: str) -> Credentials:
                return MagicMock(spec=Credentials)
            
            def save_credential(self, credential: Credentials) -> None:
                pass
            
            def get_credential(self, name: str) -> Optional[Credentials]:
                return MagicMock(spec=Credentials)
            
            def list_credentials(self) -> List[Credentials]:
                return [MagicMock(spec=Credentials)]
            
            def delete_credential(self, name: str) -> None:
                pass
            
            def validate_credential(self, name: str, password: str) -> bool:
                return True
        
        # Create an instance of the mock service
        service = MockCredentialService()
        
        # Test that the service implements the interface
        self.assertIsInstance(service, ICredentialService)
        
        # Test that the methods can be called
        credential = service.create_credential("test", "user", "pass")
        self.assertIsNotNone(credential)
        
        service.save_credential(credential)
        
        retrieved_credential = service.get_credential("test")
        self.assertIsNotNone(retrieved_credential)
        
        credentials = service.list_credentials()
        self.assertEqual(len(credentials), 1)
        
        is_valid = service.validate_credential("test", "pass")
        self.assertTrue(is_valid)
        
        service.delete_credential("test")
    
    def test_execution_service_interface(self):
        """Test that IExecutionService can be implemented."""
        
        class MockExecutionService(IExecutionService):
            """Mock implementation of IExecutionService."""
            
            def execute_workflow(self, workflow_id: str, credential_name: Optional[str] = None) -> Dict[str, Any]:
                return {"status": "running"}
            
            def stop_execution(self) -> bool:
                return True
            
            def get_execution_status(self) -> Dict[str, Any]:
                return {"status": "completed"}
            
            def get_execution_results(self) -> List[ActionResult]:
                return [MagicMock(spec=ActionResult)]
        
        # Create an instance of the mock service
        service = MockExecutionService()
        
        # Test that the service implements the interface
        self.assertIsInstance(service, IExecutionService)
        
        # Test that the methods can be called
        status = service.execute_workflow("test")
        self.assertEqual(status["status"], "running")
        
        stopped = service.stop_execution()
        self.assertTrue(stopped)
        
        status = service.get_execution_status()
        self.assertEqual(status["status"], "completed")
        
        results = service.get_execution_results()
        self.assertEqual(len(results), 1)

if __name__ == "__main__":
    unittest.main()
