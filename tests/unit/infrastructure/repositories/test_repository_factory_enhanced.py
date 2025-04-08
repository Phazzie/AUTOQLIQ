#!/usr/bin/env python3
"""
Enhanced unit tests for RepositoryFactory class in src/infrastructure/repositories/repository_factory.py.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

# Import the module under test
from src.infrastructure.repositories.repository_factory import RepositoryFactory
from src.core.exceptions import RepositoryError, ConfigError
from src.core.interfaces import ICredentialRepository, IWorkflowRepository
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository


class TestRepositoryFactory(unittest.TestCase):
    """
    Test cases for the RepositoryFactory class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 7 main responsibilities of RepositoryFactory:
    1. Creating credential repositories
    2. Creating workflow repositories
    3. Repository type validation
    4. Error handling
    5. Default parameters management
    6. Option normalization
    7. Component initialization
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create the factory
        self.factory = RepositoryFactory()
    
    def test_init(self):
        """Test initialization."""
        # Simply verify the factory is created successfully
        factory = RepositoryFactory()
        self.assertIsNotNone(factory)
        self.assertIsNotNone(factory.logger)
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository')
    def test_create_credential_repository_file_system(self, mock_fs_cred_repo):
        """Test creating a file system credential repository."""
        # Configure mock
        mock_instance = MagicMock(spec=FileSystemCredentialRepository)
        mock_fs_cred_repo.return_value = mock_instance
        
        # Call the factory method
        repo = self.factory.create_credential_repository(
            repository_type="file_system",
            path="test_credentials.json"
        )
        
        # Verify the correct type was instantiated
        self.assertEqual(repo, mock_instance)
        
        # Verify the constructor was called with correct parameters
        mock_fs_cred_repo.assert_called_once_with(
            file_path="test_credentials.json",
            create_if_missing=True  # Default option
        )
    
    @patch('src.infrastructure.repositories.repository_factory.DatabaseCredentialRepository')
    def test_create_credential_repository_database(self, mock_db_cred_repo):
        """Test creating a database credential repository."""
        # Configure mock
        mock_instance = MagicMock(spec=DatabaseCredentialRepository)
        mock_db_cred_repo.return_value = mock_instance
        
        # Call the factory method
        repo = self.factory.create_credential_repository(
            repository_type="database",
            path="test.db"
        )
        
        # Verify the correct type was instantiated
        self.assertEqual(repo, mock_instance)
        
        # Verify the constructor was called with correct parameters
        mock_db_cred_repo.assert_called_once_with(
            db_path="test.db"
        )
    
    def test_create_credential_repository_invalid_type(self):
        """Test creating a credential repository with an invalid type."""
        # Call the factory method with an invalid type
        with self.assertRaises(ConfigError):
            self.factory.create_credential_repository(
                repository_type="invalid_type",  # Not a valid type
                path="test_credentials.json"
            )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository')
    def test_create_credential_repository_with_options(self, mock_fs_cred_repo):
        """Test creating a credential repository with additional options."""
        # Configure mock
        mock_instance = MagicMock(spec=FileSystemCredentialRepository)
        mock_fs_cred_repo.return_value = mock_instance
        
        # Call the factory method with additional options
        repo = self.factory.create_credential_repository(
            repository_type="file_system",
            path="test_credentials.json",
            create_if_missing=False,  # Override default
            custom_option="value"
        )
        
        # Verify the constructor was called with correct parameters
        mock_fs_cred_repo.assert_called_once_with(
            file_path="test_credentials.json",
            create_if_missing=False,  # Overridden option
            custom_option="value"
        )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository')
    def test_create_credential_repository_error_handling(self, mock_fs_cred_repo):
        """Test error handling when creating a credential repository."""
        # Configure mock to raise an exception
        mock_fs_cred_repo.side_effect = ValueError("Test error")
        
        # Call the factory method
        with self.assertRaises(RepositoryError):
            self.factory.create_credential_repository(
                repository_type="file_system",
                path="test_credentials.json"
            )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository')
    def test_create_workflow_repository_file_system(self, mock_fs_wf_repo):
        """Test creating a file system workflow repository."""
        # Configure mock
        mock_instance = MagicMock(spec=FileSystemWorkflowRepository)
        mock_fs_wf_repo.return_value = mock_instance
        
        # Call the factory method
        repo = self.factory.create_workflow_repository(
            repository_type="file_system",
            path="workflows"
        )
        
        # Verify the correct type was instantiated
        self.assertEqual(repo, mock_instance)
        
        # Verify the constructor was called with correct parameters
        mock_fs_wf_repo.assert_called_once_with(
            directory_path="workflows",
            create_if_missing=True  # Default option
        )
    
    @patch('src.infrastructure.repositories.repository_factory.DatabaseWorkflowRepository')
    def test_create_workflow_repository_database(self, mock_db_wf_repo):
        """Test creating a database workflow repository."""
        # Configure mock
        mock_instance = MagicMock(spec=DatabaseWorkflowRepository)
        mock_db_wf_repo.return_value = mock_instance
        
        # Call the factory method
        repo = self.factory.create_workflow_repository(
            repository_type="database",
            path="test.db"
        )
        
        # Verify the correct type was instantiated
        self.assertEqual(repo, mock_instance)
        
        # Verify the constructor was called with correct parameters
        mock_db_wf_repo.assert_called_once_with(
            db_path="test.db"
        )
    
    def test_create_workflow_repository_invalid_type(self):
        """Test creating a workflow repository with an invalid type."""
        # Call the factory method with an invalid type
        with self.assertRaises(ConfigError):
            self.factory.create_workflow_repository(
                repository_type="invalid_type",  # Not a valid type
                path="workflows"
            )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository')
    def test_create_workflow_repository_with_options(self, mock_fs_wf_repo):
        """Test creating a workflow repository with additional options."""
        # Configure mock
        mock_instance = MagicMock(spec=FileSystemWorkflowRepository)
        mock_fs_wf_repo.return_value = mock_instance
        
        # Call the factory method with additional options
        repo = self.factory.create_workflow_repository(
            repository_type="file_system",
            path="workflows",
            create_if_missing=False,  # Override default
            template_path="templates",
            custom_option="value"
        )
        
        # Verify the constructor was called with correct parameters
        mock_fs_wf_repo.assert_called_once_with(
            directory_path="workflows",
            create_if_missing=False,  # Overridden option
            template_path="templates",
            custom_option="value"
        )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository')
    def test_create_workflow_repository_error_handling(self, mock_fs_wf_repo):
        """Test error handling when creating a workflow repository."""
        # Configure mock to raise an exception
        mock_fs_wf_repo.side_effect = ValueError("Test error")
        
        # Call the factory method
        with self.assertRaises(RepositoryError):
            self.factory.create_workflow_repository(
                repository_type="file_system",
                path="workflows"
            )
    
    def test_default_parameters_credential_repository(self):
        """Test default parameters for credential repository creation."""
        with patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository') as mock_fs_cred_repo:
            # Configure mock
            mock_instance = MagicMock(spec=FileSystemCredentialRepository)
            mock_fs_cred_repo.return_value = mock_instance
            
            # Call the factory method with no parameters
            repo = self.factory.create_credential_repository()
            
            # Verify the constructor was called with default parameters
            mock_fs_cred_repo.assert_called_once_with(
                file_path="credentials.json",  # Default path
                create_if_missing=True  # Default option
            )
    
    def test_default_parameters_workflow_repository(self):
        """Test default parameters for workflow repository creation."""
        with patch('src.infrastructure.repositories.repository_factory.FileSystemWorkflowRepository') as mock_fs_wf_repo:
            # Configure mock
            mock_instance = MagicMock(spec=FileSystemWorkflowRepository)
            mock_fs_wf_repo.return_value = mock_instance
            
            # Call the factory method with no parameters
            repo = self.factory.create_workflow_repository()
            
            # Verify the constructor was called with default parameters
            mock_fs_wf_repo.assert_called_once_with(
                directory_path="workflows",  # Default path
                create_if_missing=True  # Default option
            )
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository')
    def test_config_error_propagation(self, mock_fs_cred_repo):
        """Test that ConfigError is propagated without wrapping."""
        # Configure mock to raise ConfigError
        mock_fs_cred_repo.side_effect = ConfigError("Test config error")
        
        # Call the factory method
        with self.assertRaises(ConfigError):
            self.factory.create_credential_repository()
    
    @patch('src.infrastructure.repositories.repository_factory.FileSystemCredentialRepository')
    def test_repository_error_propagation(self, mock_fs_cred_repo):
        """Test that RepositoryError is propagated without wrapping."""
        # Configure mock to raise RepositoryError
        mock_fs_cred_repo.side_effect = RepositoryError("Test repository error")
        
        # Call the factory method
        with self.assertRaises(RepositoryError):
            self.factory.create_credential_repository()


if __name__ == '__main__':
    unittest.main()
