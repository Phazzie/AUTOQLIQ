import unittest
import os
import tempfile
import shutil
import json
from typing import List, Dict, Any

from src.core.interfaces import ICredentialRepository
from src.infrastructure.persistence import FileSystemCredentialRepository


class TestCredentialManagement(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.credentials_file = os.path.join(self.test_dir, "credentials.json")
        
        # Create an empty credentials file
        with open(self.credentials_file, 'w') as f:
            json.dump([], f)
        
        # Create repository
        self.repository = FileSystemCredentialRepository(self.credentials_file)
        
        # Test data
        self.test_credentials = [
            {
                "name": "test_credential_1",
                "username": "testuser1",
                "password": "testpass1"
            },
            {
                "name": "test_credential_2",
                "username": "testuser2",
                "password": "testpass2"
            }
        ]
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_save_and_get_credential(self):
        # Act - Save a credential
        self.repository.save_credential(self.test_credentials[0])
        
        # Assert - Verify the credential was saved
        credential = self.repository.get_by_name(self.test_credentials[0]["name"])
        
        # Verify the credential
        self.assertIsNotNone(credential)
        self.assertEqual(credential["name"], self.test_credentials[0]["name"])
        self.assertEqual(credential["username"], self.test_credentials[0]["username"])
        self.assertEqual(credential["password"], self.test_credentials[0]["password"])
    
    def test_get_all_credentials(self):
        # Arrange - Save multiple credentials
        for credential in self.test_credentials:
            self.repository.save_credential(credential)
        
        # Act
        credentials = self.repository.get_all()
        
        # Assert
        self.assertEqual(len(credentials), len(self.test_credentials))
        
        # Verify each credential
        for i, credential in enumerate(credentials):
            self.assertEqual(credential["name"], self.test_credentials[i]["name"])
            self.assertEqual(credential["username"], self.test_credentials[i]["username"])
            self.assertEqual(credential["password"], self.test_credentials[i]["password"])
    
    def test_update_credential(self):
        # Arrange - Save a credential
        self.repository.save_credential(self.test_credentials[0])
        
        # Create updated credential
        updated_credential = {
            "name": self.test_credentials[0]["name"],
            "username": "updated_user",
            "password": "updated_pass"
        }
        
        # Act - Update the credential
        self.repository.save_credential(updated_credential)
        
        # Assert - Verify the credential was updated
        credential = self.repository.get_by_name(updated_credential["name"])
        
        # Verify the credential
        self.assertIsNotNone(credential)
        self.assertEqual(credential["name"], updated_credential["name"])
        self.assertEqual(credential["username"], updated_credential["username"])
        self.assertEqual(credential["password"], updated_credential["password"])
        
        # Verify only one credential exists
        credentials = self.repository.get_all()
        self.assertEqual(len(credentials), 1)
    
    def test_delete_credential(self):
        # Arrange - Save multiple credentials
        for credential in self.test_credentials:
            self.repository.save_credential(credential)
        
        # Act - Delete a credential
        result = self.repository.delete_credential(self.test_credentials[0]["name"])
        
        # Assert
        self.assertTrue(result)
        
        # Verify the credential was deleted
        credential = self.repository.get_by_name(self.test_credentials[0]["name"])
        self.assertIsNone(credential)
        
        # Verify only one credential remains
        credentials = self.repository.get_all()
        self.assertEqual(len(credentials), 1)
        self.assertEqual(credentials[0]["name"], self.test_credentials[1]["name"])
    
    def test_delete_nonexistent_credential(self):
        # Act - Delete a nonexistent credential
        result = self.repository.delete_credential("nonexistent")
        
        # Assert
        self.assertFalse(result)
    
    def test_get_nonexistent_credential(self):
        # Act
        credential = self.repository.get_by_name("nonexistent")
        
        # Assert
        self.assertIsNone(credential)
    
    def test_credential_persistence(self):
        # Arrange - Save credentials
        for credential in self.test_credentials:
            self.repository.save_credential(credential)
        
        # Create a new repository instance with the same file
        new_repository = FileSystemCredentialRepository(self.credentials_file)
        
        # Act - Get credentials from the new repository
        credentials = new_repository.get_all()
        
        # Assert - Verify the credentials were loaded
        self.assertEqual(len(credentials), len(self.test_credentials))
        
        # Verify each credential
        for i, credential in enumerate(credentials):
            self.assertEqual(credential["name"], self.test_credentials[i]["name"])
            self.assertEqual(credential["username"], self.test_credentials[i]["username"])
            self.assertEqual(credential["password"], self.test_credentials[i]["password"])
    
    def test_invalid_credential_validation(self):
        # Test cases for invalid credentials
        invalid_credentials = [
            # Missing name
            {"username": "testuser", "password": "testpass"},
            # Missing username
            {"name": "test_credential", "password": "testpass"},
            # Missing password
            {"name": "test_credential", "username": "testuser"},
            # Empty name
            {"name": "", "username": "testuser", "password": "testpass"},
            # Empty username
            {"name": "test_credential", "username": "", "password": "testpass"},
            # Empty password
            {"name": "test_credential", "username": "testuser", "password": ""},
            # Not a dictionary
            "not_a_dictionary"
        ]
        
        # Test each invalid credential
        for invalid_credential in invalid_credentials:
            with self.assertRaises(Exception):
                self.repository.save_credential(invalid_credential)


if __name__ == "__main__":
    unittest.main()
