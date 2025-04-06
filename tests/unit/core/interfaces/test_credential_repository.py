"""Tests for the ICredentialRepository interface.

This module provides tests to verify that implementations of the ICredentialRepository
interface correctly adhere to the contract defined by the interface.
"""
import unittest
from abc import ABC
from typing import Dict, List, Optional
from unittest.mock import MagicMock

from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError


class TestICredentialRepository(unittest.TestCase):
    """Test cases for the ICredentialRepository interface.

    This test suite defines a set of tests that any implementation of
    ICredentialRepository should pass. It uses a mock implementation
    to verify the interface contract.
    """

    def setUp(self):
        """Set up test fixtures.

        Creates a mock implementation of ICredentialRepository for testing.
        """
        # Create a concrete implementation of ICredentialRepository for testing
        class MockCredentialRepository(ICredentialRepository):
            def __init__(self):
                self.credentials = {}
                self.mock_save = MagicMock()
                self.mock_get_by_name = MagicMock()
                self.mock_delete = MagicMock()
                self.mock_list_credentials = MagicMock()

            def save(self, credential: Dict[str, str]) -> None:
                self.mock_save(credential)

            def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
                return self.mock_get_by_name(name)

            def delete(self, name: str) -> None:
                self.mock_delete(name)

            def list_credentials(self) -> List[str]:
                return self.mock_list_credentials()

        self.repo = MockCredentialRepository()

        # Sample credential for testing
        self.sample_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_pass"
        }

    def test_should_verify_icredential_repository_is_abstract(self):
        """
        Verifies that ICredentialRepository is an abstract base class.

        Given:
        - The ICredentialRepository class

        When:
        - Checking if it's a subclass of ABC

        Then:
        - It should be a subclass of ABC
        """
        # Arrange - done in setUp

        # Act & Assert
        self.assertTrue(issubclass(ICredentialRepository, ABC))

    def test_should_save_credential_with_required_fields(self):
        """
        Verifies that save method accepts a credential with required fields.

        Given:
        - A mock implementation of ICredentialRepository
        - A credential with name, username, and password fields

        When:
        - Calling save with the credential

        Then:
        - The save method should be called with the credential
        """
        # Arrange - done in setUp

        # Act
        self.repo.save(self.sample_credential)

        # Assert
        self.repo.mock_save.assert_called_once_with(self.sample_credential)

    def test_should_get_credential_by_name(self):
        """
        Verifies that get_by_name method returns a credential when it exists.

        Given:
        - A mock implementation of ICredentialRepository
        - A credential that exists in the repository

        When:
        - Calling get_by_name with the credential name

        Then:
        - The get_by_name method should be called with the credential name
        - The method should return the credential
        """
        # Arrange
        name = "test_credential"
        self.repo.mock_get_by_name.return_value = self.sample_credential

        # Act
        result = self.repo.get_by_name(name)

        # Assert
        self.assertEqual(result, self.sample_credential)
        self.repo.mock_get_by_name.assert_called_once_with(name)

    def test_should_return_none_when_credential_not_found(self):
        """
        Verifies that get_by_name method returns None when the credential doesn't exist.

        Given:
        - A mock implementation of ICredentialRepository
        - A credential that doesn't exist in the repository

        When:
        - Calling get_by_name with the credential name

        Then:
        - The get_by_name method should be called with the credential name
        - The method should return None
        """
        # Arrange
        name = "nonexistent_credential"
        self.repo.mock_get_by_name.return_value = None

        # Act
        result = self.repo.get_by_name(name)

        # Assert
        self.assertIsNone(result)
        self.repo.mock_get_by_name.assert_called_once_with(name)

    def test_should_delete_credential(self):
        """
        Verifies that delete method deletes a credential.

        Given:
        - A mock implementation of ICredentialRepository
        - A credential that exists in the repository

        When:
        - Calling delete with the credential name

        Then:
        - The delete method should be called with the credential name
        """
        # Arrange
        name = "test_credential"

        # Act
        self.repo.delete(name)

        # Assert
        self.repo.mock_delete.assert_called_once_with(name)

    def test_should_list_credentials(self):
        """
        Verifies that list_credentials method returns a list of credential names.

        Given:
        - A mock implementation of ICredentialRepository
        - Multiple credentials exist in the repository

        When:
        - Calling list_credentials

        Then:
        - The list_credentials method should be called
        - The method should return a list of credential names
        """
        # Arrange
        credential_names = ["credential1", "credential2"]
        self.repo.mock_list_credentials.return_value = credential_names

        # Act
        result = self.repo.list_credentials()

        # Assert
        self.assertEqual(result, credential_names)
        self.repo.mock_list_credentials.assert_called_once()


if __name__ == "__main__":
    unittest.main()
