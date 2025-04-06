"""Tests for the ICredentialService interface.

This module provides tests to verify that implementations of the ICredentialService
interface correctly adhere to the contract defined by the interface.
"""
import unittest
from abc import ABC
from typing import Dict, List
from unittest.mock import MagicMock

from src.application.interfaces import ICredentialService
from src.core.exceptions import CredentialError


class TestICredentialService(unittest.TestCase):
    """Test cases for the ICredentialService interface.
    
    This test suite defines a set of tests that any implementation of
    ICredentialService should pass. It uses a mock implementation
    to verify the interface contract.
    """

    def setUp(self):
        """Set up test fixtures.
        
        Creates a mock implementation of ICredentialService for testing.
        """
        # Create a concrete implementation of ICredentialService for testing
        class MockCredentialService(ICredentialService):
            def __init__(self):
                self.mock_create_credential = MagicMock()
                self.mock_update_credential = MagicMock()
                self.mock_delete_credential = MagicMock()
                self.mock_get_credential = MagicMock()
                self.mock_list_credentials = MagicMock()
                
            def create_credential(self, name: str, username: str, password: str) -> bool:
                return self.mock_create_credential(name, username, password)
                
            def update_credential(self, name: str, username: str, password: str) -> bool:
                return self.mock_update_credential(name, username, password)
                
            def delete_credential(self, name: str) -> bool:
                return self.mock_delete_credential(name)
                
            def get_credential(self, name: str) -> Dict[str, str]:
                return self.mock_get_credential(name)
                
            def list_credentials(self) -> List[str]:
                return self.mock_list_credentials()
        
        self.service = MockCredentialService()
        
        # Sample credential for testing
        self.sample_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_pass"
        }

    def test_should_verify_icredential_service_is_abstract(self):
        """
        Verifies that ICredentialService is an abstract base class.
        
        Given:
        - The ICredentialService class
        
        When:
        - Checking if it's a subclass of ABC
        
        Then:
        - It should be a subclass of ABC
        """
        # Arrange - done in setUp
        
        # Act & Assert
        self.assertTrue(issubclass(ICredentialService, ABC))

    def test_should_create_credential(self):
        """
        Verifies that create_credential method creates a credential.
        
        Given:
        - A mock implementation of ICredentialService
        - Valid credential information
        
        When:
        - Calling create_credential with the information
        
        Then:
        - The create_credential method should be called with the information
        - The method should return True
        """
        # Arrange
        name = "test_credential"
        username = "test_user"
        password = "test_pass"
        self.service.mock_create_credential.return_value = True
        
        # Act
        result = self.service.create_credential(name, username, password)
        
        # Assert
        self.assertTrue(result)
        self.service.mock_create_credential.assert_called_once_with(name, username, password)

    def test_should_update_credential(self):
        """
        Verifies that update_credential method updates a credential.
        
        Given:
        - A mock implementation of ICredentialService
        - Valid credential information
        
        When:
        - Calling update_credential with the information
        
        Then:
        - The update_credential method should be called with the information
        - The method should return True
        """
        # Arrange
        name = "test_credential"
        username = "new_user"
        password = "new_pass"
        self.service.mock_update_credential.return_value = True
        
        # Act
        result = self.service.update_credential(name, username, password)
        
        # Assert
        self.assertTrue(result)
        self.service.mock_update_credential.assert_called_once_with(name, username, password)

    def test_should_delete_credential(self):
        """
        Verifies that delete_credential method deletes a credential.
        
        Given:
        - A mock implementation of ICredentialService
        - A credential name
        
        When:
        - Calling delete_credential with the name
        
        Then:
        - The delete_credential method should be called with the name
        - The method should return True
        """
        # Arrange
        name = "test_credential"
        self.service.mock_delete_credential.return_value = True
        
        # Act
        result = self.service.delete_credential(name)
        
        # Assert
        self.assertTrue(result)
        self.service.mock_delete_credential.assert_called_once_with(name)

    def test_should_get_credential(self):
        """
        Verifies that get_credential method returns a credential.
        
        Given:
        - A mock implementation of ICredentialService
        - A credential name
        
        When:
        - Calling get_credential with the name
        
        Then:
        - The get_credential method should be called with the name
        - The method should return the credential
        """
        # Arrange
        name = "test_credential"
        self.service.mock_get_credential.return_value = self.sample_credential
        
        # Act
        result = self.service.get_credential(name)
        
        # Assert
        self.assertEqual(result, self.sample_credential)
        self.service.mock_get_credential.assert_called_once_with(name)

    def test_should_list_credentials(self):
        """
        Verifies that list_credentials method returns a list of credential names.
        
        Given:
        - A mock implementation of ICredentialService
        
        When:
        - Calling list_credentials
        
        Then:
        - The list_credentials method should be called
        - The method should return a list of credential names
        """
        # Arrange
        credential_names = ["credential1", "credential2"]
        self.service.mock_list_credentials.return_value = credential_names
        
        # Act
        result = self.service.list_credentials()
        
        # Assert
        self.assertEqual(result, credential_names)
        self.service.mock_list_credentials.assert_called_once()

    def test_should_raise_credential_error_for_invalid_operations(self):
        """
        Verifies that methods raise CredentialError for invalid operations.
        
        Given:
        - A mock implementation of ICredentialService
        - The implementation is configured to raise CredentialError
        
        When:
        - Calling methods with invalid inputs
        
        Then:
        - CredentialError should be raised
        """
        # Arrange
        error_message = "Invalid operation"
        self.service.mock_create_credential.side_effect = CredentialError(error_message)
        self.service.mock_get_credential.side_effect = CredentialError(error_message)
        
        # Act & Assert - create_credential
        with self.assertRaises(CredentialError) as context:
            self.service.create_credential("invalid", "user", "pass")
        self.assertEqual(str(context.exception), error_message)
        
        # Act & Assert - get_credential
        with self.assertRaises(CredentialError) as context:
            self.service.get_credential("nonexistent")
        self.assertEqual(str(context.exception), error_message)


if __name__ == "__main__":
    unittest.main()
