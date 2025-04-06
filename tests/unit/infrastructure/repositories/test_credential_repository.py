"""Tests for the FileSystemCredentialRepository class."""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.core.exceptions import CredentialError
from src.infrastructure.repositories.credential_repository import FileSystemCredentialRepository

class TestFileSystemCredentialRepository(unittest.TestCase):
    """Test cases for the FileSystemCredentialRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.credentials_file = os.path.join(self.temp_dir.name, "credentials.json")
        self.repo = FileSystemCredentialRepository(self.credentials_file)
        
        # Sample credentials for testing
        self.sample_credentials = [
            {
                "name": "test_credential",
                "username": "test_user",
                "password": "test_password"
            },
            {
                "name": "another_credential",
                "username": "another_user",
                "password": "another_password"
            }
        ]

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_get_all_empty_file(self):
        """Test that get_all returns an empty list when the file is empty."""
        # Create empty credentials file
        with open(self.credentials_file, "w") as f:
            json.dump([], f)
        
        # Get all credentials
        result = self.repo.get_all()
        
        # Check result
        self.assertEqual(result, [])

    def test_get_all_with_credentials(self):
        """Test that get_all returns all credentials from the file."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Get all credentials
        result = self.repo.get_all()
        
        # Check result
        self.assertEqual(result, self.sample_credentials)

    def test_get_all_file_not_found(self):
        """Test that get_all raises CredentialError when the file doesn't exist."""
        # Don't create the credentials file
        
        # Try to get all credentials
        with self.assertRaises(CredentialError):
            self.repo.get_all()

    def test_get_all_invalid_json(self):
        """Test that get_all raises CredentialError when the file contains invalid JSON."""
        # Create credentials file with invalid JSON
        with open(self.credentials_file, "w") as f:
            f.write("invalid json")
        
        # Try to get all credentials
        with self.assertRaises(CredentialError):
            self.repo.get_all()

    def test_get_by_name_found(self):
        """Test that get_by_name returns the credential with the specified name."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Get credential by name
        result = self.repo.get_by_name("test_credential")
        
        # Check result
        self.assertEqual(result, self.sample_credentials[0])

    def test_get_by_name_not_found(self):
        """Test that get_by_name returns None when the credential doesn't exist."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Get credential by name
        result = self.repo.get_by_name("nonexistent_credential")
        
        # Check result
        self.assertIsNone(result)

    def test_save_credential_new(self):
        """Test that save_credential adds a new credential to the file."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # New credential to save
        new_credential = {
            "name": "new_credential",
            "username": "new_user",
            "password": "new_password"
        }
        
        # Save credential
        self.repo.save_credential(new_credential)
        
        # Check that the credential was added
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        self.assertEqual(len(credentials), 3)
        self.assertIn(new_credential, credentials)

    def test_save_credential_update(self):
        """Test that save_credential updates an existing credential in the file."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Updated credential
        updated_credential = {
            "name": "test_credential",
            "username": "updated_user",
            "password": "updated_password"
        }
        
        # Save credential
        self.repo.save_credential(updated_credential)
        
        # Check that the credential was updated
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        self.assertEqual(len(credentials), 2)
        self.assertIn(updated_credential, credentials)
        self.assertNotIn(self.sample_credentials[0], credentials)

    def test_save_credential_invalid(self):
        """Test that save_credential raises CredentialError when the credential is invalid."""
        # Invalid credential (missing required field)
        invalid_credential = {
            "name": "invalid_credential",
            "username": "invalid_user"
            # Missing password
        }
        
        # Try to save credential
        with self.assertRaises(CredentialError):
            self.repo.save_credential(invalid_credential)

    def test_delete_credential_found(self):
        """Test that delete_credential removes the credential with the specified name."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Delete credential
        result = self.repo.delete_credential("test_credential")
        
        # Check result
        self.assertTrue(result)
        
        # Check that the credential was removed
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        self.assertEqual(len(credentials), 1)
        self.assertNotIn(self.sample_credentials[0], credentials)
        self.assertIn(self.sample_credentials[1], credentials)

    def test_delete_credential_not_found(self):
        """Test that delete_credential returns False when the credential doesn't exist."""
        # Create credentials file with sample credentials
        with open(self.credentials_file, "w") as f:
            json.dump(self.sample_credentials, f)
        
        # Delete nonexistent credential
        result = self.repo.delete_credential("nonexistent_credential")
        
        # Check result
        self.assertFalse(result)
        
        # Check that the credentials file wasn't modified
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        self.assertEqual(credentials, self.sample_credentials)

    def test_validate_credential_valid(self):
        """Test that _validate_credential doesn't raise an error for a valid credential."""
        # Valid credential
        valid_credential = {
            "name": "valid_credential",
            "username": "valid_user",
            "password": "valid_password"
        }
        
        # Validate credential (should not raise an error)
        self.repo._validate_credential(valid_credential)

    def test_validate_credential_not_dict(self):
        """Test that _validate_credential raises CredentialError when the credential is not a dictionary."""
        # Invalid credential (not a dictionary)
        invalid_credential = "not a dictionary"
        
        # Try to validate credential
        with self.assertRaises(CredentialError):
            self.repo._validate_credential(invalid_credential)

    def test_validate_credential_missing_field(self):
        """Test that _validate_credential raises CredentialError when a required field is missing."""
        # Invalid credential (missing required field)
        invalid_credential = {
            "name": "invalid_credential",
            "username": "invalid_user"
            # Missing password
        }
        
        # Try to validate credential
        with self.assertRaises(CredentialError):
            self.repo._validate_credential(invalid_credential)

    def test_validate_credential_empty_field(self):
        """Test that _validate_credential raises CredentialError when a required field is empty."""
        # Invalid credential (empty required field)
        invalid_credential = {
            "name": "invalid_credential",
            "username": "",  # Empty username
            "password": "invalid_password"
        }
        
        # Try to validate credential
        with self.assertRaises(CredentialError):
            self.repo._validate_credential(invalid_credential)

if __name__ == "__main__":
    unittest.main()
