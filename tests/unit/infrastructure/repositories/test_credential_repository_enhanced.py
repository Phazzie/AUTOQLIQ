#!/usr/bin/env python3
"""
Enhanced unit tests for FileSystemCredentialRepository class in src/infrastructure/repositories/credential_repository.py.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock, call

# Import the module under test
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository
from src.core.exceptions import CredentialError, RepositoryError, ValidationError
from src.infrastructure.common.validators import CredentialValidator


class TestFileSystemCredentialRepository(unittest.TestCase):
    """
    Test cases for the FileSystemCredentialRepository class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 6 main responsibilities of FileSystemCredentialRepository:
    1. Credential file management (creation, reading, writing)
    2. Credential CRUD operations
    3. Validation of credential data
    4. Error handling
    5. Handling file operations safety
    6. Handling directory operations
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory and file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cred_file_path = os.path.join(self.temp_dir.name, 'test_credentials.json')
        
        # Sample credential data
        self.sample_credential = {
            'name': 'TestCredential',
            'username': 'test_user',
            'password': 'hashed_password_123',
            'url': 'https://example.com'
        }
        
        # Create the repository
        self.repo = FileSystemCredentialRepository(self.cred_file_path)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_init_with_empty_path(self):
        """Test initialization with an empty file path."""
        with self.assertRaises(ValueError):
            FileSystemCredentialRepository('')
    
    def test_init_creates_directories(self):
        """Test that initialization creates directories if they don't exist."""
        # Create a path with non-existent directories
        deep_path = os.path.join(self.temp_dir.name, 'deep', 'path', 'test_credentials.json')
        
        # Create repo with the deep path
        repo = FileSystemCredentialRepository(deep_path)
        
        # Verify directory was created
        self.assertTrue(os.path.exists(os.path.dirname(deep_path)))
    
    def test_init_creates_empty_file(self):
        """Test that initialization creates an empty file if it doesn't exist."""
        # Create path to a non-existent file
        non_existent_file = os.path.join(self.temp_dir.name, 'new_file.json')
        
        # Ensure file doesn't exist
        if os.path.exists(non_existent_file):
            os.unlink(non_existent_file)
        
        # Create repo
        repo = FileSystemCredentialRepository(non_existent_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(non_existent_file))
        
        # Verify file contains an empty list
        with open(non_existent_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, [])
    
    def test_init_no_create_if_missing(self):
        """Test initialization with create_if_missing=False."""
        # Create path to a non-existent file
        non_existent_file = os.path.join(self.temp_dir.name, 'not_created.json')
        
        # Ensure file doesn't exist
        if os.path.exists(non_existent_file):
            os.unlink(non_existent_file)
        
        # Create repo with create_if_missing=False
        repo = FileSystemCredentialRepository(non_existent_file, create_if_missing=False)
        
        # File should not be created during initialization
        self.assertFalse(os.path.exists(non_existent_file))
        
        # Operations should fail when file doesn't exist
        with self.assertRaises(CredentialError):
            repo.list_credentials()
    
    def test_load_all_credentials_empty_file(self):
        """Test loading credentials from an empty file."""
        # Create an empty credentials file
        with open(self.cred_file_path, 'w') as f:
            json.dump([], f)
        
        # Load all credentials
        credentials = self.repo._load_all_credentials()
        
        # Verify an empty list is returned
        self.assertEqual(credentials, [])
    
    def test_load_all_credentials_with_data(self):
        """Test loading credentials from a file with data."""
        # Create a credentials file with test data
        test_data = [self.sample_credential]
        with open(self.cred_file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Load all credentials
        credentials = self.repo._load_all_credentials()
        
        # Verify the data is loaded correctly
        self.assertEqual(len(credentials), 1)
        self.assertEqual(credentials[0]['name'], 'TestCredential')
    
    def test_load_all_credentials_invalid_json(self):
        """Test loading credentials from a file with invalid JSON."""
        # Create a file with invalid JSON
        with open(self.cred_file_path, 'w') as f:
            f.write("This is not valid JSON")
        
        # Attempting to load should raise CredentialError
        with self.assertRaises(CredentialError):
            self.repo._load_all_credentials()
    
    def test_load_all_credentials_not_a_list(self):
        """Test loading credentials from a file that doesn't contain a list."""
        # Create a file with a JSON object (not a list)
        with open(self.cred_file_path, 'w') as f:
            json.dump({"not": "a list"}, f)
        
        # Attempting to load should raise CredentialError
        with self.assertRaises(CredentialError):
            self.repo._load_all_credentials()
    
    def test_load_all_credentials_non_dict_items(self):
        """Test loading credentials from a file with non-dict items in the list."""
        # Create a file with non-dict items
        with open(self.cred_file_path, 'w') as f:
            json.dump(["not a dict", 123], f)
        
        # Attempting to load should raise CredentialError
        with self.assertRaises(CredentialError):
            self.repo._load_all_credentials()
    
    def test_load_all_credentials_file_not_found(self):
        """Test loading credentials when the file doesn't exist."""
        # Create path to a non-existent file
        non_existent_file = os.path.join(self.temp_dir.name, 'non_existent.json')
        
        # Ensure file doesn't exist
        if os.path.exists(non_existent_file):
            os.unlink(non_existent_file)
        
        # Create repo with create_if_missing=False
        repo = FileSystemCredentialRepository(non_existent_file, create_if_missing=False)
        
        # Attempting to load should raise CredentialError
        with self.assertRaises(CredentialError):
            repo._load_all_credentials()
    
    def test_save_all_credentials(self):
        """Test saving all credentials."""
        # Test data to save
        test_data = [self.sample_credential]
        
        # Save all credentials
        self.repo._save_all_credentials(test_data)
        
        # Verify the data was saved correctly
        with open(self.cred_file_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, test_data)
    
    def test_save_all_credentials_error(self):
        """Test error handling when saving credentials."""
        # Mock write_json_file to raise an error
        with patch.object(self.repo, '_write_json_file', side_effect=IOError("Test IO error")):
            # Attempting to save should raise CredentialError
            with self.assertRaises(CredentialError):
                self.repo._save_all_credentials([self.sample_credential])
    
    def test_save_new_credential(self):
        """Test saving a new credential."""
        # Create an empty credentials file
        with open(self.cred_file_path, 'w') as f:
            json.dump([], f)
        
        # Mock validate_credential_data to avoid validation errors
        with patch.object(CredentialValidator, 'validate_credential_data'):
            # Save a new credential
            self.repo.save(self.sample_credential)
            
            # Verify the credential was saved
            with open(self.cred_file_path, 'r') as f:
                saved_data = json.load(f)
                self.assertEqual(len(saved_data), 1)
                self.assertEqual(saved_data[0]['name'], 'TestCredential')
    
    def test_save_update_credential(self):
        """Test updating an existing credential."""
        # Create a credentials file with test data
        initial_credential = self.sample_credential.copy()
        with open(self.cred_file_path, 'w') as f:
            json.dump([initial_credential], f)
        
        # Create an updated credential
        updated_credential = self.sample_credential.copy()
        updated_credential['username'] = 'updated_user'
        
        # Mock validate_credential_data to avoid validation errors
        with patch.object(CredentialValidator, 'validate_credential_data'):
            # Save the updated credential
            self.repo.save(updated_credential)
            
            # Verify the credential was updated
            with open(self.cred_file_path, 'r') as f:
                saved_data = json.load(f)
                self.assertEqual(len(saved_data), 1)
                self.assertEqual(saved_data[0]['username'], 'updated_user')
    
    def test_save_validation_error(self):
        """Test saving a credential with validation error."""
        # Mock validate_credential_data to raise a validation error
        error_msg = "Invalid credential data"
        with patch.object(CredentialValidator, 'validate_credential_data', side_effect=ValidationError(error_msg)):
            # Attempting to save should raise ValidationError
            with self.assertRaises(ValidationError) as context:
                self.repo.save(self.sample_credential)
            
            # Verify the error message
            self.assertEqual(str(context.exception), error_msg)
    
    def test_get_by_name_existing(self):
        """Test getting an existing credential by name."""
        # Create a credentials file with test data
        with open(self.cred_file_path, 'w') as f:
            json.dump([self.sample_credential], f)
        
        # Get the credential
        credential = self.repo.get_by_name('TestCredential')
        
        # Verify the credential was retrieved
        self.assertIsNotNone(credential)
        self.assertEqual(credential['name'], 'TestCredential')
        self.assertEqual(credential['username'], 'test_user')
    
    def test_get_by_name_non_existent(self):
        """Test getting a non-existent credential by name."""
        # Create a credentials file with test data
        with open(self.cred_file_path, 'w') as f:
            json.dump([self.sample_credential], f)
        
        # Get a non-existent credential
        credential = self.repo.get_by_name('NonExistentCredential')
        
        # Verify None is returned
        self.assertIsNone(credential)
    
    def test_get_by_name_invalid_name(self):
        """Test getting a credential with an invalid name."""
        # Attempting to get with an invalid name should raise ValidationError
        with self.assertRaises(ValidationError):
            self.repo.get_by_name('')
    
    def test_delete_existing(self):
        """Test deleting an existing credential."""
        # Create a credentials file with test data
        with open(self.cred_file_path, 'w') as f:
            json.dump([self.sample_credential], f)
        
        # Delete the credential
        result = self.repo.delete('TestCredential')
        
        # Verify the credential was deleted
        self.assertTrue(result)
        with open(self.cred_file_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(len(saved_data), 0)
    
    def test_delete_non_existent(self):
        """Test deleting a non-existent credential."""
        # Create a credentials file with test data
        with open(self.cred_file_path, 'w') as f:
            json.dump([self.sample_credential], f)
        
        # Delete a non-existent credential
        result = self.repo.delete('NonExistentCredential')
        
        # Verify the operation returned False and the data was not modified
        self.assertFalse(result)
        with open(self.cred_file_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(len(saved_data), 1)
    
    def test_delete_invalid_name(self):
        """Test deleting a credential with an invalid name."""
        # Attempting to delete with an invalid name should raise ValidationError
        with self.assertRaises(ValidationError):
            self.repo.delete('')
    
    def test_list_credentials_empty(self):
        """Test listing credentials when there are none."""
        # Create an empty credentials file
        with open(self.cred_file_path, 'w') as f:
            json.dump([], f)
        
        # List credentials
        credentials = self.repo.list_credentials()
        
        # Verify an empty list is returned
        self.assertEqual(credentials, [])
    
    def test_list_credentials_with_data(self):
        """Test listing credentials when there are some."""
        # Create multiple credentials
        cred1 = self.sample_credential.copy()
        cred2 = self.sample_credential.copy()
        cred2['name'] = 'AnotherCredential'
        
        # Create a credentials file with test data
        with open(self.cred_file_path, 'w') as f:
            json.dump([cred1, cred2], f)
        
        # List credentials
        credentials = self.repo.list_credentials()
        
        # Verify the list is returned and sorted
        self.assertEqual(len(credentials), 2)
        self.assertEqual(credentials[0], 'AnotherCredential')  # Should be sorted alphabetically
        self.assertEqual(credentials[1], 'TestCredential')
    
    def test_list_credentials_file_not_found(self):
        """Test listing credentials when the file doesn't exist."""
        # Create path to a non-existent file
        non_existent_file = os.path.join(self.temp_dir.name, 'non_existent.json')
        
        # Ensure file doesn't exist
        if os.path.exists(non_existent_file):
            os.unlink(non_existent_file)
        
        # Create repo with create_if_missing=False
        repo = FileSystemCredentialRepository(non_existent_file, create_if_missing=False)
        
        # Attempting to list should raise CredentialError
        with self.assertRaises(CredentialError):
            repo.list_credentials()


if __name__ == '__main__':
    unittest.main()