"""Unit tests for the CredentialFSRepository."""

import unittest
import os
import shutil
import tempfile
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.exceptions import RepositoryError, ValidationError
from src.core.credentials import Credentials
from src.core.interfaces import IEncryptionService
from src.infrastructure.repositories.credential_fs_repository import CredentialFSRepository


class MockEncryptionService(IEncryptionService):
    """Mock encryption service for testing."""
    
    def encrypt(self, plaintext):
        """Mock encrypt method that adds 'encrypted:' prefix."""
        return f"encrypted:{plaintext}"
    
    def decrypt(self, ciphertext):
        """Mock decrypt method that removes 'encrypted:' prefix."""
        if ciphertext.startswith("encrypted:"):
            return ciphertext[len("encrypted:"):]
        return ciphertext


class TestCredentialFSRepository(unittest.TestCase):
    """Test cases for the CredentialFSRepository."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "credentials.json")
        
        # Create a mock encryption service
        self.encryption_service = MockEncryptionService()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_init_with_existing_file(self):
        """Test initializing the repository with an existing file."""
        # Create an empty credentials file
        with open(self.test_file, "w") as f:
            json.dump([], f)
        
        # Create the repository
        repo = CredentialFSRepository(self.test_file, self.encryption_service)
        
        # Check that the repository was created with the correct file path
        self.assertEqual(repo.file_path, os.path.abspath(self.test_file))
    
    def test_init_with_nonexistent_file_create_if_missing(self):
        """Test initializing the repository with a nonexistent file and create_if_missing=True."""
        # Create the repository with create_if_missing=True
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.test_file))
        
        # Check that the repository was created with the correct file path
        self.assertEqual(repo.file_path, os.path.abspath(self.test_file))
    
    def test_init_with_nonexistent_file_no_create(self):
        """Test initializing the repository with a nonexistent file and create_if_missing=False."""
        # Try to create the repository with create_if_missing=False
        with self.assertRaises(RepositoryError):
            CredentialFSRepository(
                self.test_file,
                self.encryption_service,
                create_if_missing=False
            )
    
    def test_init_with_nonexistent_directory_create_if_missing(self):
        """Test initializing the repository with a nonexistent directory and create_if_missing=True."""
        # Create a path to a file in a nonexistent directory
        nonexistent_dir = os.path.join(self.test_dir, "nonexistent")
        nonexistent_file = os.path.join(nonexistent_dir, "credentials.json")
        
        # Create the repository with create_if_missing=True
        repo = CredentialFSRepository(
            nonexistent_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(nonexistent_dir))
        
        # Check that the file was created
        self.assertTrue(os.path.exists(nonexistent_file))
        
        # Check that the repository was created with the correct file path
        self.assertEqual(repo.file_path, os.path.abspath(nonexistent_file))
    
    def test_load_credentials(self):
        """Test loading credentials from the file."""
        # Create a credentials file with some data
        data = [
            {
                "name": "test-credential",
                "username": "test-user",
                "password": "encrypted:test-password",
                "description": "Test credential",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00",
                "encrypted": True
            }
        ]
        with open(self.test_file, "w") as f:
            json.dump(data, f)
        
        # Create the repository
        repo = CredentialFSRepository(self.test_file, self.encryption_service)
        
        # Load the credentials
        credentials_data = repo._load_credentials()
        
        # Check that the loaded data is correct
        self.assertEqual(len(credentials_data), 1)
        self.assertEqual(credentials_data[0]["name"], "test-credential")
        self.assertEqual(credentials_data[0]["username"], "test-user")
        self.assertEqual(credentials_data[0]["password"], "encrypted:test-password")
    
    def test_save_credentials(self):
        """Test saving credentials to the file."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create some credentials data
        data = [
            {
                "name": "test-credential",
                "username": "test-user",
                "password": "encrypted:test-password",
                "description": "Test credential",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-02T12:00:00",
                "encrypted": True
            }
        ]
        
        # Save the credentials
        repo._save_credentials(data)
        
        # Check that the file contains the correct data
        with open(self.test_file, "r") as f:
            saved_data = json.load(f)
            self.assertEqual(len(saved_data), 1)
            self.assertEqual(saved_data[0]["name"], "test-credential")
            self.assertEqual(saved_data[0]["username"], "test-user")
            self.assertEqual(saved_data[0]["password"], "encrypted:test-password")
    
    def test_serialize_credentials(self):
        """Test serializing credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create credentials
        credentials = Credentials(
            name="test-credential",
            username="test-user",
            password="test-password",
            description="Test credential"
        )
        credentials.created_at = datetime(2023, 1, 1, 12, 0, 0)
        credentials.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        
        # Serialize the credentials
        data = repo._serialize_credentials(credentials)
        
        # Check that the serialized data is correct
        self.assertEqual(data["name"], "test-credential")
        self.assertEqual(data["username"], "test-user")
        self.assertEqual(data["password"], "encrypted:test-password")
        self.assertEqual(data["description"], "Test credential")
        self.assertEqual(data["created_at"], "2023-01-01T12:00:00")
        self.assertEqual(data["updated_at"], "2023-01-02T12:00:00")
        self.assertTrue(data["encrypted"])
    
    def test_deserialize_credentials(self):
        """Test deserializing credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create serialized credentials data
        data = {
            "name": "test-credential",
            "username": "test-user",
            "password": "encrypted:test-password",
            "description": "Test credential",
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
            "encrypted": True
        }
        
        # Deserialize the credentials
        credentials = repo._deserialize_credentials(data)
        
        # Check that the deserialized credentials are correct
        self.assertEqual(credentials.name, "test-credential")
        self.assertEqual(credentials.username, "test-user")
        self.assertEqual(credentials.password, "test-password")  # Decrypted
        self.assertEqual(credentials.description, "Test credential")
        self.assertEqual(credentials.created_at, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(credentials.updated_at, datetime(2023, 1, 2, 12, 0, 0))
    
    def test_deserialize_credentials_not_encrypted(self):
        """Test deserializing credentials that are not encrypted."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create serialized credentials data without encryption
        data = {
            "name": "test-credential",
            "username": "test-user",
            "password": "test-password",
            "description": "Test credential",
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-02T12:00:00",
            "encrypted": False
        }
        
        # Deserialize the credentials
        credentials = repo._deserialize_credentials(data)
        
        # Check that the deserialized credentials are correct
        self.assertEqual(credentials.name, "test-credential")
        self.assertEqual(credentials.username, "test-user")
        self.assertEqual(credentials.password, "test-password")  # Not decrypted
        self.assertEqual(credentials.description, "Test credential")
        self.assertEqual(credentials.created_at, datetime(2023, 1, 1, 12, 0, 0))
        self.assertEqual(credentials.updated_at, datetime(2023, 1, 2, 12, 0, 0))
    
    def test_save_credentials_method(self):
        """Test saving credentials using the save method."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create credentials
        credentials = Credentials(
            name="test-credential",
            username="test-user",
            password="test-password",
            description="Test credential"
        )
        
        # Save the credentials
        repo.save(credentials)
        
        # Check that the timestamps were set
        self.assertIsNotNone(credentials.created_at)
        self.assertIsNotNone(credentials.updated_at)
        self.assertEqual(credentials.created_at, credentials.updated_at)
        
        # Check that the credentials were saved to the file
        with open(self.test_file, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test-credential")
            self.assertEqual(data[0]["username"], "test-user")
            self.assertEqual(data[0]["password"], "encrypted:test-password")
    
    def test_save_credentials_with_existing_created_at(self):
        """Test saving credentials with an existing created_at timestamp."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create credentials with an existing created_at timestamp
        credentials = Credentials(
            name="test-credential",
            username="test-user",
            password="test-password",
            description="Test credential"
        )
        credentials.created_at = datetime(2023, 1, 1, 12, 0, 0)
        
        # Save the credentials
        repo.save(credentials)
        
        # Check that the created_at timestamp was preserved
        self.assertEqual(credentials.created_at, datetime(2023, 1, 1, 12, 0, 0))
        
        # Check that the updated_at timestamp was set
        self.assertIsNotNone(credentials.updated_at)
        self.assertNotEqual(credentials.created_at, credentials.updated_at)
    
    def test_save_credentials_update_existing(self):
        """Test saving credentials to update existing ones."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create and save initial credentials
        credentials1 = Credentials(
            name="test-credential",
            username="test-user",
            password="test-password",
            description="Test credential"
        )
        repo.save(credentials1)
        
        # Create updated credentials with the same name
        credentials2 = Credentials(
            name="test-credential",
            username="updated-user",
            password="updated-password",
            description="Updated credential"
        )
        
        # Save the updated credentials
        repo.save(credentials2)
        
        # Check that the credentials were updated in the file
        with open(self.test_file, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)  # Still only one credential
            self.assertEqual(data[0]["name"], "test-credential")
            self.assertEqual(data[0]["username"], "updated-user")
            self.assertEqual(data[0]["password"], "encrypted:updated-password")
            self.assertEqual(data[0]["description"], "Updated credential")
    
    def test_get_credentials(self):
        """Test getting credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create and save credentials
        credentials = Credentials(
            name="test-credential",
            username="test-user",
            password="test-password",
            description="Test credential"
        )
        repo.save(credentials)
        
        # Get the credentials
        retrieved_credentials = repo.get("test-credential")
        
        # Check that the retrieved credentials are correct
        self.assertIsNotNone(retrieved_credentials)
        self.assertEqual(retrieved_credentials.name, "test-credential")
        self.assertEqual(retrieved_credentials.username, "test-user")
        self.assertEqual(retrieved_credentials.password, "test-password")
        self.assertEqual(retrieved_credentials.description, "Test credential")
    
    def test_get_nonexistent_credentials(self):
        """Test getting nonexistent credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Try to get nonexistent credentials
        credentials = repo.get("nonexistent")
        
        # Check that the result is None
        self.assertIsNone(credentials)
    
    def test_list_credentials(self):
        """Test listing credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create and save some credentials
        credentials1 = Credentials(
            name="test-credential-1",
            username="test-user-1",
            password="test-password-1"
        )
        credentials2 = Credentials(
            name="test-credential-2",
            username="test-user-2",
            password="test-password-2"
        )
        repo.save(credentials1)
        repo.save(credentials2)
        
        # List the credentials
        credentials_list = repo.list()
        
        # Check that the list contains the correct credentials
        self.assertEqual(len(credentials_list), 2)
        credential_names = [c.name for c in credentials_list]
        self.assertIn("test-credential-1", credential_names)
        self.assertIn("test-credential-2", credential_names)
    
    def test_delete_credentials(self):
        """Test deleting credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Create and save some credentials
        credentials1 = Credentials(
            name="test-credential-1",
            username="test-user-1",
            password="test-password-1"
        )
        credentials2 = Credentials(
            name="test-credential-2",
            username="test-user-2",
            password="test-password-2"
        )
        repo.save(credentials1)
        repo.save(credentials2)
        
        # Delete one of the credentials
        repo.delete("test-credential-1")
        
        # Check that the credentials were deleted
        credentials_list = repo.list()
        self.assertEqual(len(credentials_list), 1)
        self.assertEqual(credentials_list[0].name, "test-credential-2")
    
    def test_delete_nonexistent_credentials(self):
        """Test deleting nonexistent credentials."""
        # Create the repository
        repo = CredentialFSRepository(
            self.test_file,
            self.encryption_service,
            create_if_missing=True
        )
        
        # Try to delete nonexistent credentials
        # This should not raise an exception
        repo.delete("nonexistent")


if __name__ == "__main__":
    unittest.main()
