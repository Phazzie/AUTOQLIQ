"""Service factory for AutoQliq application services."""
import logging
from typing import Optional

from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.application.interfaces import IWorkflowService, ICredentialService, IWebDriverService
from src.application.services.workflow_service import WorkflowService
from src.application.services.credential_service import CredentialService
from src.application.services.webdriver_service import WebDriverService
from src.infrastructure.webdrivers.factory import WebDriverFactory


class ServiceFactory:
    """Factory for creating application services.
    
    This class provides methods for creating application services with the
    appropriate dependencies.
    
    Attributes:
        workflow_repository: Repository for workflow storage and retrieval
        credential_repository: Repository for credential storage and retrieval
        web_driver_factory: Factory for creating web driver instances
        logger: Logger for recording factory operations and errors
    """
    
    def __init__(self, workflow_repository: IWorkflowRepository,
                 credential_repository: ICredentialRepository):
        """Initialize a new ServiceFactory.
        
        Args:
            workflow_repository: Repository for workflow storage and retrieval
            credential_repository: Repository for credential storage and retrieval
        """
        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.web_driver_factory = WebDriverFactory
        self.logger = logging.getLogger(__name__)
        
        # Cached service instances
        self._workflow_service: Optional[IWorkflowService] = None
        self._credential_service: Optional[ICredentialService] = None
        self._webdriver_service: Optional[IWebDriverService] = None
    
    def create_workflow_service(self) -> IWorkflowService:
        """Create a new WorkflowService instance.
        
        Returns:
            A configured WorkflowService instance
        """
        self.logger.debug("Creating WorkflowService")
        
        if self._workflow_service is None:
            self._workflow_service = WorkflowService(
                workflow_repository=self.workflow_repository,
                credential_repository=self.credential_repository,
                web_driver_factory=self.create_webdriver_service()
            )
        
        return self._workflow_service
    
    def create_credential_service(self) -> ICredentialService:
        """Create a new CredentialService instance.
        
        Returns:
            A configured CredentialService instance
        """
        self.logger.debug("Creating CredentialService")
        
        if self._credential_service is None:
            self._credential_service = CredentialService(
                credential_repository=self.credential_repository
            )
        
        return self._credential_service
    
    def create_webdriver_service(self) -> IWebDriverService:
        """Create a new WebDriverService instance.
        
        Returns:
            A configured WebDriverService instance
        """
        self.logger.debug("Creating WebDriverService")
        
        if self._webdriver_service is None:
            self._webdriver_service = WebDriverService(
                web_driver_factory=self.web_driver_factory
            )
        
        return self._webdriver_service
