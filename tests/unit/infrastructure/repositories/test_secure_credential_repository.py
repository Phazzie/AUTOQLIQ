"""Unit tests for the SecureCredentialRepository."""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from src.core.exceptions import CredentialError, ValidationError, RepositoryError
from src.core.interfaces import IEncryptionService
from src.infrastructure.repositories.secure_credential_repository import SecureCredentialRepository


class MockEncryptionService(IEncryptionService):
    """Mock encryption service for testing."""
    
    def encrypt(self, plaintext: str) -> str:
        """Mock encrypt method that adds 'ENC:' prefix."""
        return f"ENC:{plaintext}"
    
    def decrypt(self, ciphertext: str) -> str:
        """Mock decrypt method that removes 'ENC:' prefix."""
        if ciphertext.startswith("ENC:"):
            return ciphertext[4:]
        return ciphertext


class TestSecureCredentialRepository(unittest.TestCase):
    """Test cases for the SecureCredentialRepository."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_credentials.json")
        
        # Create a mock encryption service
        self.encryption_service = MockEncryptionService()
        
        # Create the repository
        self.repo = SecureCredentialRepository(
            file_path=self.test_file,
            encryption_service=self.encryption_service,
            create_if_missing=True
        )
        
        # Sample credential data
        self.sample_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_password"
        }
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_init_creates_file_if_missing(self):
        """Test that the repository creates the file if it doesn't exist."""
        self.assertTrue(os.path.exists(self.test_file))
        
        # Check that the file contains an empty list
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, [])
    
    def test_init_with_existing_file(self):
        """Test initialization with an existing file."""
        # Create a file with some data
        with open(self.test_file, 'w') as f:
            json.dump([{"name": "existing", "password": "ENC:pwd"}], f)
        
        # Create a new repository instance
        repo = SecureCredentialRepository(
            file_path=self.test_file,
            encryption_service=self.encryption_service,
            create_if_missing=True
        )
        
        # Check that the file was not overwritten
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "existing")
    
    def test_save_new_credential(self):
        """Test saving a new credential."""
        # Save a credential
        self.repo.save(self.sample_credential)
        
        # Check that the file contains the credential with encrypted password
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_credential")
            self.assertEqual(data[0]["username"], "test_user")
            self.assertEqual(data[0]["password"], "ENC:test_password")
            self.assertTrue(data[0]["encrypted"])
    
    def test_save_update_existing_credential(self):
        """Test updating an existing credential."""
        # Save a credential
        self.repo.save(self.sample_credential)
        
        # Update the credential
        updated_credential = self.sample_credential.copy()
        updated_credential["password"] = "new_password"
        self.repo.save(updated_credential)
        
        # Check that the file contains the updated credential
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_credential")
            self.assertEqual(data[0]["password"], "ENC:new_password")
    
    def test_get_by_name_existing(self):
        """Test getting an existing credential."""
        # Save a credential
        self.repo.save(self.sample_credential)
        
        # Get the credential
        credential = self.repo.get_by_name("test_credential")
        
        # Check that the credential was retrieved and decrypted
        self.assertIsNotNone(credential)
        self.assertEqual(credential["name"], "test_credential")
        self.assertEqual(credential["username"], "test_user")
        self.assertEqual(credential["password"], "test_password")
    
    def test_get_by_name_nonexistent(self):
        """Test getting a nonexistent credential."""
        # Get a nonexistent credential
        credential = self.repo.get_by_name("nonexistent")
        
        # Check that None was returned
        self.assertIsNone(credential)
    
    def test_delete_existing(self):
        """Test deleting an existing credential."""
        # Save a credential
        self.repo.save(self.sample_credential)
        
        # Delete the credential
        result = self.repo.delete("test_credential")
        
        # Check that the credential was deleted
        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_name("test_credential"))
    
    def test_delete_nonexistent(self):
        """Test deleting a nonexistent credential."""
        # Delete a nonexistent credential
        result = self.repo.delete("nonexistent")
        
        # Check that False was returned
        self.assertFalse(result)
    
    def test_list_credentials(self):
        """Test listing credentials."""
        # Save multiple credentials
        self.repo.save(self.sample_credential)
        self.repo.save({"name": "another", "username": "user", "password": "pwd"})
        
        # List the credentials
        credentials = self.repo.list_credentials()
        
        # Check that the credentials were listed
        self.assertEqual(len(credentials), 2)
        self.assertIn("test_credential", credentials)
        self.assertIn("another", credentials)
    
    def test_list_credentials_empty(self):
        """Test listing credentials when there are none."""
        # List the credentials
        credentials = self.repo.list_credentials()
        
        # Check that an empty list was returned
        self.assertEqual(credentials, [])
    
    def test_thread_safety(self):
        """Test thread safety by simulating concurrent access."""
        import threading
        
        # Function to save a credential in a thread
        def save_credential(name):
            credential = {
                "name": name,
                "username": f"user_{name}",
                "password": f"pwd_{name}"
            }
            self.repo.save(credential)
        
        # Create and start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_credential, args=(f"thread_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all credentials were saved
        credentials = self.repo.list_credentials()
        self.assertEqual(len(credentials), 10)
        for i in range(10):
            self.assertIn(f"thread_{i}", credentials)
    
    def test_encryption_error_handling(self):
        """Test handling of encryption errors."""
        # Create a mock encryption service that raises an exception
        mock_service = MagicMock(spec=IEncryptionService)
        mock_service.encrypt.side_effect = Exception("Encryption failed")
        
        # Create a repository with the mock service
        repo = SecureCredentialRepository(
            file_path=self.test_file,
            encryption_service=mock_service,
            create_if_missing=True
        )
        
        # Try to save a credential
        with self.assertRaises(CredentialError):
            repo.save(self.sample_credential)
    
    def test_decryption_error_handling(self):
        """Test handling of decryption errors."""
        # Save a credential
        self.repo.save(self.sample_credential)
        
        # Create a mock encryption service that raises an exception
        mock_service = MagicMock(spec=IEncryptionService)
        mock_service.decrypt.side_effect = Exception("Decryption failed")
        
        # Create a repository with the mock service
        repo = SecureCredentialRepository(
            file_path=self.test_file,
            encryption_service=mock_service,
            create_if_missing=True
        )
        
        # Try to get the credential
        with self.assertRaises(CredentialError):
            repo.get_by_name("test_credential")
    
    def test_invalid_credential_data(self):
        """Test handling of invalid credential data."""
        # Try to save a credential without a name
        with self.assertRaises(ValidationError):
            self.repo.save({"username": "user", "password": "pwd"})
        
        # Try to save a credential without a password
        with self.assertRaises(ValidationError):
            self.repo.save({"name": "test", "username": "user"})
        
        # Try to save a credential with an invalid name
        with self.assertRaises(ValidationError):
            self.repo.save({"name": "", "username": "user", "password": "pwd"})
    
    def test_file_io_error_handling(self):
        """Test handling of file I/O errors."""
        # Create a directory with the same name as the file to cause an I/O error
        os.remove(self.test_file)
        os.mkdir(self.test_file)
        
        # Try to save a credential
        with self.assertRaises(CredentialError):
            self.repo.save(self.sample_credential)


if __name__ == '__main__':
    unittest.main()
