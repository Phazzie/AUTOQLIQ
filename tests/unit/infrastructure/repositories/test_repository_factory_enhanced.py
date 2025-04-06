"""Tests for the enhanced RepositoryFactory class."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.interfaces import ICredentialRepository, IWorkflowRepository
from src.infrastructure.repositories.repository_factory import RepositoryFactory
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.core.exceptions import RepositoryError

class TestRepositoryFactoryEnhanced(unittest.TestCase):
    """Test cases for the enhanced RepositoryFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = RepositoryFactory()
    
    def test_create_credential_repository_file_system(self):
        """Test creating a file system credential repository."""
        repo = self.factory.create_credential_repository("file_system", "test.json")
        
        self.assertIsInstance(repo, FileSystemCredentialRepository)
        self.assertEqual(repo.file_path, "test.json")
    
    def test_create_credential_repository_database(self):
        """Test creating a database credential repository."""
        repo = self.factory.create_credential_repository("database", "test.db")
        
        self.assertIsInstance(repo, DatabaseCredentialRepository)
        self.assertEqual(repo.db_path, "test.db")
    
    def test_create_credential_repository_invalid_type(self):
        """Test creating a credential repository with an invalid type."""
        with self.assertRaises(RepositoryError) as context:
            self.factory.create_credential_repository("invalid", "test.json")
        
        # Check that the error message is correct
        self.assertIn("Unsupported repository type: invalid", str(context.exception))
        
        # Check that the repository name is included in the error
        self.assertEqual(context.exception.repository_name, "CredentialRepository")
    
    def test_create_workflow_repository_file_system(self):
        """Test creating a file system workflow repository."""
        repo = self.factory.create_workflow_repository("file_system", "test_dir")
        
        self.assertIsInstance(repo, FileSystemWorkflowRepository)
        self.assertEqual(repo.directory_path, "test_dir")
    
    def test_create_workflow_repository_database(self):
        """Test creating a database workflow repository."""
        repo = self.factory.create_workflow_repository("database", "test.db")
        
        self.assertIsInstance(repo, DatabaseWorkflowRepository)
        self.assertEqual(repo.db_path, "test.db")
    
    def test_create_workflow_repository_invalid_type(self):
        """Test creating a workflow repository with an invalid type."""
        with self.assertRaises(RepositoryError) as context:
            self.factory.create_workflow_repository("invalid", "test_dir")
        
        # Check that the error message is correct
        self.assertIn("Unsupported repository type: invalid", str(context.exception))
        
        # Check that the repository name is included in the error
        self.assertEqual(context.exception.repository_name, "WorkflowRepository")
    
    @patch("src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository")
    def test_create_credential_repository_with_options(self, mock_repo_class):
        """Test that create_credential_repository passes options to the repository."""
        # Set up mock
        mock_repo = MagicMock(spec=FileSystemCredentialRepository)
        mock_repo_class.return_value = mock_repo
        
        # Create a credential repository with options
        options = {"create_if_missing": True}
        repo = self.factory.create_credential_repository("file_system", "test.json", **options)
        
        # Check that the repository was created with the correct options
        mock_repo_class.assert_called_once_with("test.json", **options)
        self.assertEqual(repo, mock_repo)
    
    @patch("src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository")
    def test_create_workflow_repository_with_options(self, mock_repo_class):
        """Test that create_workflow_repository passes options to the repository."""
        # Set up mock
        mock_repo = MagicMock(spec=FileSystemWorkflowRepository)
        mock_repo_class.return_value = mock_repo
        
        # Create a workflow repository with options
        options = {"create_if_missing": True}
        repo = self.factory.create_workflow_repository("file_system", "test_dir", **options)
        
        # Check that the repository was created with the correct options
        mock_repo_class.assert_called_once_with("test_dir", **options)
        self.assertEqual(repo, mock_repo)

if __name__ == "__main__":
    unittest.main()
