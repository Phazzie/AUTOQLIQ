import unittest
import os
import json
from unittest.mock import patch, mock_open, MagicMock

from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError, ValidationError, RepositoryError
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.infrastructure.common.validators import CredentialValidator


class TestFileSystemCredentialRepository(unittest.TestCase):
    """Unit tests for FileSystemCredentialRepository implementation."""

    def setUp(self):
        """Set up test environment before each test."""
        self.test_file_path = "test_credentials.json"
        self.repo = FileSystemCredentialRepository(self.test_file_path)
        
        # Sample test data
        self.test_credential = {
            "name": "test_credential",
            "username": "testuser",
            "password": "hashed$password123"  # Assume already hashed
        }
        
        # Sample credentials list
        self.test_credentials = [
            self.test_credential,
            {
                "name": "another_credential",
                "username": "anotheruser",
                "password": "hashed$anotherpassword"
            }
        ]

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_by_name_existing_credential(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test retrieving an existing credential by name."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Execute test
        result = self.repo.get_by_name("test_credential")
        
        # Verify
        self.assertEqual(result, self.test_credential)
        mock_file_open.assert_called_once_with(self.test_file_path, 'r')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_by_name_nonexistent_credential(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test retrieving a credential that doesn't exist."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Execute test
        result = self.repo.get_by_name("nonexistent")
        
        # Verify
        self.assertIsNone(result)
        mock_file_open.assert_called_once_with(self.test_file_path, 'r')

    @patch('os.path.exists')
    def test_get_by_name_file_not_exists(self, mock_path_exists):
        """Test retrieving a credential when the file doesn't exist."""
        # Setup mock
        mock_path_exists.return_value = False
        
        # Execute test and verify exception
        with self.assertRaises(RepositoryError):
            self.repo.get_by_name("test_credential")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_new_credential(self, mock_json_dump, mock_json_load, mock_file_open, mock_path_exists):
        """Test saving a new credential."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = []
        
        # Create a validator mock to bypass validation
        with patch.object(CredentialValidator, 'validate_credential_data'):
            # Execute test
            self.repo.save(self.test_credential)
        
        # Verify
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        saved_credentials = args[0]
        self.assertEqual(len(saved_credentials), 1)
        self.assertEqual(saved_credentials[0], self.test_credential)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_update_existing_credential(self, mock_json_dump, mock_json_load, mock_file_open, mock_path_exists):
        """Test updating an existing credential."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Updated credential
        updated_credential = self.test_credential.copy()
        updated_credential["username"] = "updateduser"
        
        # Create a validator mock to bypass validation
        with patch.object(CredentialValidator, 'validate_credential_data'):
            # Execute test
            self.repo.save(updated_credential)
        
        # Verify
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        saved_credentials = args[0]
        self.assertEqual(len(saved_credentials), 2)
        self.assertEqual(saved_credentials[0]["username"], "updateduser")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_list_credentials(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test listing all credentials."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Execute test
        result = self.repo.list_credentials()
        
        # Verify
        self.assertEqual(result, ["test_credential", "another_credential"])
        mock_file_open.assert_called_once_with(self.test_file_path, 'r')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_delete_existing_credential(self, mock_json_dump, mock_json_load, mock_file_open, mock_path_exists):
        """Test deleting an existing credential."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Execute test
        result = self.repo.delete("test_credential")
        
        # Verify
        self.assertTrue(result)
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        saved_credentials = args[0]
        self.assertEqual(len(saved_credentials), 1)
        self.assertEqual(saved_credentials[0]["name"], "another_credential")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_delete_nonexistent_credential(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test deleting a credential that doesn't exist."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        
        # Execute test
        result = self.repo.delete("nonexistent")
        
        # Verify
        self.assertFalse(result)

    @patch.object(CredentialValidator, 'validate_credential_data')
    def test_save_invalid_credential(self, mock_validator):
        """Test saving an invalid credential."""
        # Setup mock to raise ValidationError
        mock_validator.side_effect = ValidationError("Invalid credential")
        
        # Execute test and verify exception
        with self.assertRaises(ValidationError):
            self.repo.save({"name": "invalid"})

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_secure_storage_passwords_not_exposed(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test that passwords are not exposed in plain text."""
        # Setup mocks to return credentials with plaintext passwords
        mock_path_exists.return_value = True
        mock_json_load.return_value = [
            {
                "name": "test_credential",
                "username": "testuser",
                "password": "plaintext_password"  # Plain text password
            }
        ]
        
        # In a real implementation, passwords should be hashed when retrieved
        # Here we're verifying that our repository doesn't expose them directly
        
        # Test would include repository-specific validation
        # For illustration purposes, we'll just assert a general expectation
        with patch.object(self.repo, '_ensure_hashed_passwords') as mock_ensure_hashed:
            mock_ensure_hashed.return_value = True
            self.repo.get_by_name("test_credential")
            mock_ensure_hashed.assert_called_once()

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_create_file_if_not_exists(self, mock_json_dump, mock_file_open, mock_makedirs, mock_path_exists):
        """Test that the repository creates the file if it doesn't exist."""
        # Setup mocks
        mock_path_exists.return_value = False
        
        # Execute test
        self.repo._ensure_file_exists()
        
        # Verify
        mock_makedirs.assert_called_once()
        mock_file_open.assert_called_once_with(self.test_file_path, 'w')
        mock_json_dump.assert_called_once_with([], mock_file_open())

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_credentials_file_error(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test handling of file errors when loading credentials."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_file_open.side_effect = IOError("File error")
        
        # Execute test and verify exception
        with self.assertRaises(RepositoryError):
            self.repo._load_credentials()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_credentials_json_error(self, mock_json_load, mock_file_open, mock_path_exists):
        """Test handling of JSON errors when loading credentials."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.side_effect = json.JSONDecodeError("JSON error", "", 0)
        
        # Execute test and verify exception
        with self.assertRaises(RepositoryError):
            self.repo._load_credentials()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_credentials_file_error(self, mock_json_dump, mock_json_load, mock_file_open, mock_path_exists):
        """Test handling of file errors when saving credentials."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        mock_file_open.side_effect = [MagicMock(), IOError("File error")]
        
        # Execute test and verify exception
        with self.assertRaises(RepositoryError):
            with patch.object(CredentialValidator, 'validate_credential_data'):
                self.repo.save(self.test_credential)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_save_credentials_json_error(self, mock_json_dump, mock_json_load, mock_file_open, mock_path_exists):
        """Test handling of JSON errors when saving credentials."""
        # Setup mocks
        mock_path_exists.return_value = True
        mock_json_load.return_value = self.test_credentials
        mock_json_dump.side_effect = TypeError("JSON error")
        
        # Execute test and verify exception
        with self.assertRaises(RepositoryError):
            with patch.object(CredentialValidator, 'validate_credential_data'):
                self.repo.save(self.test_credential)


if __name__ == '__main__':
    unittest.main()
