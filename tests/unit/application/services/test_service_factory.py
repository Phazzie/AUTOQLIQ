"""Tests for the ServiceFactory class."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.application.interfaces import IWorkflowService, ICredentialService, IWebDriverService
from src.application.services.service_factory import ServiceFactory
from src.application.services.workflow_service import WorkflowService
from src.application.services.credential_service import CredentialService
from src.application.services.webdriver_service import WebDriverService


class TestServiceFactory(unittest.TestCase):
    """Test cases for the ServiceFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_repo = MagicMock(spec=IWorkflowRepository)
        self.credential_repo = MagicMock(spec=ICredentialRepository)
        self.factory = ServiceFactory(
            workflow_repository=self.workflow_repo,
            credential_repository=self.credential_repo
        )

    def test_create_workflow_service(self):
        """Test that create_workflow_service creates a WorkflowService instance."""
        # Call create_workflow_service
        service = self.factory.create_workflow_service()
        
        # Check result
        self.assertIsInstance(service, WorkflowService)
        self.assertIsInstance(service, IWorkflowService)
        
        # Check that the service was initialized with the correct repositories
        self.assertEqual(service.workflow_repository, self.workflow_repo)
        self.assertEqual(service.credential_repository, self.credential_repo)

    def test_create_credential_service(self):
        """Test that create_credential_service creates a CredentialService instance."""
        # Call create_credential_service
        service = self.factory.create_credential_service()
        
        # Check result
        self.assertIsInstance(service, CredentialService)
        self.assertIsInstance(service, ICredentialService)
        
        # Check that the service was initialized with the correct repository
        self.assertEqual(service.credential_repository, self.credential_repo)

    def test_create_webdriver_service(self):
        """Test that create_webdriver_service creates a WebDriverService instance."""
        # Call create_webdriver_service
        service = self.factory.create_webdriver_service()
        
        # Check result
        self.assertIsInstance(service, WebDriverService)
        self.assertIsInstance(service, IWebDriverService)
        
        # Check that the service was initialized with the correct factory
        self.assertEqual(service.web_driver_factory, self.factory.web_driver_factory)

    def test_service_caching(self):
        """Test that services are cached and reused."""
        # Call create_workflow_service twice
        service1 = self.factory.create_workflow_service()
        service2 = self.factory.create_workflow_service()
        
        # Check that the same instance was returned
        self.assertIs(service1, service2)
        
        # Call create_credential_service twice
        service3 = self.factory.create_credential_service()
        service4 = self.factory.create_credential_service()
        
        # Check that the same instance was returned
        self.assertIs(service3, service4)
        
        # Call create_webdriver_service twice
        service5 = self.factory.create_webdriver_service()
        service6 = self.factory.create_webdriver_service()
        
        # Check that the same instance was returned
        self.assertIs(service5, service6)


if __name__ == "__main__":
    unittest.main()
