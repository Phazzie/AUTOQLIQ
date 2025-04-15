"""Tests for the FileSystemCredentialRepository class."""

import unittest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.repository.filesystem_credential_repository import FileSystemCredentialRepository
from src.core.credentials import Credential
from src.core.exceptions import RepositoryError
from src.core.security.encryption import IEncryptionService


class TestFileSystemCredentialRepository(unittest.TestCase):
    """Test cases for the FileSystemCredentialRepository class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Mock the encryption service
        self.mock_encryption = MagicMock(spec=IEncryptionService)
        # Set up the mock to "encrypt" by adding a prefix and "decrypt" by removing it
        self.mock_encryption.encrypt.side_effect = lambda text: f"encrypted_{text}"
        self.mock_encryption.decrypt.side_effect = lambda text: text.replace("encrypted_", "")
        
        # Create repository with the test directory and mock encryption service
        self.repo = FileSystemCredentialRepository(
            base_dir=self.test_dir,
            encryption_service=self.mock_encryption
        )
        
        # Sample credential for testing
        self.test_credential = Credential(
            name="test_cred",
            username="testuser",
            password="testpass123"
        )

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_init_creates_directory(self):
        """Test that initialization creates the credentials directory if it doesn't exist."""
        # Delete the directory created in setUp
        shutil.rmtree(self.test_dir)
        
        # Re-initialize the repository to create directory
        FileSystemCredentialRepository(
            base_dir=self.test_dir,
            encryption_service=self.mock_encryption
        )
        
        # Check that the directory and structure exists
        self.assertTrue(os.path.exists(self.test_dir))
        credentials_dir = os.path.join(self.test_dir, "credentials")
        self.assertTrue(os.path.exists(credentials_dir))

    def test_init_with_existing_directory(self):
        """Test that initialization works with existing directory structure."""
        # Create a new repository with the same test directory
        repo2 = FileSystemCredentialRepository(
            base_dir=self.test_dir,
            encryption_service=self.mock_encryption
        )
        
        # Should not raise any exceptions
        self.assertIsNotNone(repo2)

    def test_save_new_credential(self):
        """Test saving a new credential."""
        # Save the test credential
        self.repo.save(self.test_credential.to_dict())
        
        # Check that the credential file exists
        cred_path = Path(self.test_dir) / "credentials" / f"{self.test_credential.name}.json"
        self.assertTrue(cred_path.exists())
        
        # Check that the encryption service was called
        self.mock_encryption.encrypt.assert_called_with(self.test_credential.password)
        
        # Verify file contents
        with open(cred_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["name"], self.test_credential.name)
            self.assertEqual(saved_data["username"], self.test_credential.username)
            self.assertEqual(saved_data["password"], f"encrypted_{self.test_credential.password}")

    def test_save_update_existing_credential(self):
        """Test updating an existing credential."""
        # Save initial credential
        self.repo.save(self.test_credential.to_dict())
        
        # Update the credential
        updated_credential = Credential(
            name=self.test_credential.name,  # Same name
            username="newuser",
            password="newpass456"
        )
        
        # Save the updated credential
        self.repo.save(updated_credential.to_dict())
        
        # Check file exists and contains updated data
        cred_path = Path(self.test_dir) / "credentials" / f"{self.test_credential.name}.json"
        with open(cred_path, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["username"], "newuser")
            self.assertEqual(saved_data["password"], f"encrypted_newpass456")

    def test_save_with_missing_data(self):
        """Test saving a credential with missing required data."""
        # Missing name
        incomplete_cred = {"username": "user", "password": "pass"}
        with self.assertRaises(RepositoryError):
            self.repo.save(incomplete_cred)
        
        # Missing username
        incomplete_cred = {"name": "test", "password": "pass"}
        with self.assertRaises(RepositoryError):
            self.repo.save(incomplete_cred)
        
        # Missing password
        incomplete_cred = {"name": "test", "username": "user"}
        with self.assertRaises(RepositoryError):
            self.repo.save(incomplete_cred)

    def test_get_by_name_existing(self):
        """Test getting an existing credential by name."""
        # Save a credential
        self.repo.save(self.test_credential.to_dict())
        
        # Get it by name
        result = self.repo.get_by_name(self.test_credential.name)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], self.test_credential.name)
        self.assertEqual(result["username"], self.test_credential.username)
        self.assertEqual(result["password"], self.test_credential.password)
        
        # Verify decryption was called
        self.mock_encryption.decrypt.assert_called()

    def test_get_by_name_nonexistent(self):
        """Test getting a non-existent credential by name."""
        result = self.repo.get_by_name("nonexistent_credential")
        self.assertIsNone(result)

    def test_get_by_name_with_io_error(self):
        """Test getting a credential when an IO error occurs."""
        # Save a credential
        self.repo.save(self.test_credential.to_dict())
        
        # Mock open to raise an IOError
        with patch('builtins.open', side_effect=IOError("Mocked IO Error")):
            result = self.repo.get_by_name(self.test_credential.name)
            self.assertIsNone(result)

    def test_delete_existing(self):
        """Test deleting an existing credential."""
        # Save a credential
        self.repo.save(self.test_credential.to_dict())
        
        # Delete it
        result = self.repo.delete(self.test_credential.name)
        
        # Verify it was deleted
        self.assertTrue(result)
        cred_path = Path(self.test_dir) / "credentials" / f"{self.test_credential.name}.json"
        self.assertFalse(cred_path.exists())

    def test_delete_nonexistent(self):
        """Test deleting a non-existent credential."""
        result = self.repo.delete("nonexistent_credential")
        self.assertFalse(result)

    def test_list_credentials_empty(self):
        """Test listing credentials when none exist."""
        result = self.repo.list_credentials()
        self.assertEqual(result, [])

    def test_list_credentials_multiple(self):
        """Test listing multiple credentials."""
        # Save multiple credentials
        creds = [
            Credential("cred1", "user1", "pass1"),
            Credential("cred2", "user2", "pass2"),
            Credential("cred3", "user3", "pass3")
        ]
        
        for cred in creds:
            self.repo.save(cred.to_dict())
        
        # List them
        result = self.repo.list_credentials()
        
        # Verify the result (should be sorted alphabetically)
        self.assertEqual(sorted(result), ["cred1", "cred2", "cred3"])

    def test_list_credentials_with_non_json_files(self):
        """Test listing credentials when directory contains non-JSON files."""
        # Save a credential
        self.repo.save(self.test_credential.to_dict())
        
        # Create a non-JSON file in the credentials directory
        non_json_path = Path(self.test_dir) / "credentials" / "not_a_credential.txt"
        with open(non_json_path, 'w') as f:
            f.write("This is not a JSON file")
        
        # List credentials
        result = self.repo.list_credentials()
        
        # Verify only the JSON file is included
        self.assertEqual(result, [self.test_credential.name])

    def test_encryption_service_required(self):
        """Test that an encryption service is required for initialization."""
        with self.assertRaises(ValueError):
            FileSystemCredentialRepository(
                base_dir=self.test_dir,
                encryption_service=None
            )

    def test_save_with_file_permission_error(self):
        """Test handling of file permission errors during save."""
        # Mock open to raise a PermissionError
        with patch('builtins.open', side_effect=PermissionError("Mocked Permission Error")):
            with self.assertRaises(RepositoryError):
                self.repo.save(self.test_credential.to_dict())

    def test_save_with_encryption_error(self):
        """Test handling of encryption errors during save."""
        # Configure mock to raise an exception
        self.mock_encryption.encrypt.side_effect = Exception("Encryption failed")
        
        with self.assertRaises(RepositoryError):
            self.repo.save(self.test_credential.to_dict())

    def test_get_by_name_with_decryption_error(self):
        """Test handling of decryption errors during get_by_name."""
        # Save a credential
        self.repo.save(self.test_credential.to_dict())
        
        # Configure mock to raise an exception for decryption
        self.mock_encryption.decrypt.side_effect = Exception("Decryption failed")
        
        # Should return None when decryption fails
        result = self.repo.get_by_name(self.test_credential.name)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
