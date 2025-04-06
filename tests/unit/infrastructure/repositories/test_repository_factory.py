"""Tests for the repository factory module."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.interfaces import ICredentialRepository, IWorkflowRepository
from src.infrastructure.repositories.repository_factory import RepositoryFactory
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository

class TestRepositoryFactory(unittest.TestCase):
    """Test cases for the RepositoryFactory class."""

    def test_create_credential_repository(self):
        """Test that create_credential_repository creates a FileSystemCredentialRepository."""
        # Create a repository factory
        factory = RepositoryFactory()
        
        # Create a credential repository
        repo = factory.create_credential_repository("test_credentials.json")
        
        # Check that the repository is of the correct type
        self.assertIsInstance(repo, FileSystemCredentialRepository)
        self.assertIsInstance(repo, ICredentialRepository)
        self.assertEqual(repo.file_path, "test_credentials.json")

    def test_create_workflow_repository(self):
        """Test that create_workflow_repository creates a FileSystemWorkflowRepository."""
        # Create a repository factory
        factory = RepositoryFactory()
        
        # Create a workflow repository
        repo = factory.create_workflow_repository("test_workflows")
        
        # Check that the repository is of the correct type
        self.assertIsInstance(repo, FileSystemWorkflowRepository)
        self.assertIsInstance(repo, IWorkflowRepository)
        self.assertEqual(repo.directory_path, "test_workflows")

    @patch("src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository")
    def test_create_credential_repository_with_options(self, mock_repo_class):
        """Test that create_credential_repository passes options to the repository."""
        # Set up mock
        mock_repo = MagicMock(spec=FileSystemCredentialRepository)
        mock_repo_class.return_value = mock_repo
        
        # Create a repository factory
        factory = RepositoryFactory()
        
        # Create a credential repository with options
        options = {"create_if_missing": True}
        repo = factory.create_credential_repository("test_credentials.json", **options)
        
        # Check that the repository was created with the correct options
        mock_repo_class.assert_called_once_with("test_credentials.json", **options)
        self.assertEqual(repo, mock_repo)

    @patch("src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository")
    def test_create_workflow_repository_with_options(self, mock_repo_class):
        """Test that create_workflow_repository passes options to the repository."""
        # Set up mock
        mock_repo = MagicMock(spec=FileSystemWorkflowRepository)
        mock_repo_class.return_value = mock_repo
        
        # Create a repository factory
        factory = RepositoryFactory()
        
        # Create a workflow repository with options
        options = {"create_if_missing": True}
        repo = factory.create_workflow_repository("test_workflows", **options)
        
        # Check that the repository was created with the correct options
        mock_repo_class.assert_called_once_with("test_workflows", **options)
        self.assertEqual(repo, mock_repo)

if __name__ == "__main__":
    unittest.main()
