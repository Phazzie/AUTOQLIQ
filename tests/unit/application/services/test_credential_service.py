"""Tests for the CredentialService class."""
import unittest
from unittest.mock import patch, MagicMock, call

from src.core.exceptions import CredentialError
from src.core.interfaces import ICredentialRepository
from src.application.interfaces import ICredentialService
from src.application.services.credential_service import CredentialService


class TestCredentialService(unittest.TestCase):
    """Test cases for the CredentialService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.credential_repo = MagicMock(spec=ICredentialRepository)
        self.service = CredentialService(credential_repository=self.credential_repo)

        # Sample credential for testing
        self.sample_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_pass"
        }

    def test_create_credential(self):
        """Test that create_credential creates a new credential."""
        # Set up mock
        self.credential_repo.save_credential.return_value = None

        # Call create_credential
        result = self.service.create_credential(
            name="test_credential",
            username="test_user",
            password="test_pass"
        )

        # Check result
        self.assertTrue(result)

        # Verify credential_repo.save_credential was called with correct arguments
        expected_credential = {
            "name": "test_credential",
            "username": "test_user",
            "password": "test_pass"
        }
        self.credential_repo.save_credential.assert_called_once_with(expected_credential)

    def test_create_credential_error(self):
        """Test that create_credential raises CredentialError when creating a credential fails."""
        # Set up mock to raise an exception
        self.credential_repo.save_credential.side_effect = CredentialError("Create credential failed")

        # Try to call create_credential
        with self.assertRaises(CredentialError):
            self.service.create_credential(
                name="test_credential",
                username="test_user",
                password="test_pass"
            )

    def test_update_credential(self):
        """Test that update_credential updates an existing credential."""
        # Set up mocks
        self.credential_repo.get_by_name.return_value = self.sample_credential
        self.credential_repo.save_credential.return_value = None

        # Call update_credential
        result = self.service.update_credential(
            name="test_credential",
            username="new_user",
            password="new_pass"
        )

        # Check result
        self.assertTrue(result)

        # Verify credential_repo.get_by_name was called with correct arguments
        self.credential_repo.get_by_name.assert_called_once_with("test_credential")

        # Verify credential_repo.save_credential was called with correct arguments
        expected_credential = {
            "name": "test_credential",
            "username": "new_user",
            "password": "new_pass"
        }
        self.credential_repo.save_credential.assert_called_once_with(expected_credential)

    def test_update_credential_not_found(self):
        """Test that update_credential raises CredentialError when the credential doesn't exist."""
        # Set up mock to raise an exception
        self.credential_repo.get_by_name.side_effect = CredentialError("Credential not found")

        # Try to call update_credential
        with self.assertRaises(CredentialError):
            self.service.update_credential(
                name="test_credential",
                username="new_user",
                password="new_pass"
            )

    def test_update_credential_error(self):
        """Test that update_credential raises CredentialError when updating a credential fails."""
        # Set up mocks
        self.credential_repo.get_by_name.return_value = self.sample_credential
        self.credential_repo.save_credential.side_effect = CredentialError("Update credential failed")

        # Try to call update_credential
        with self.assertRaises(CredentialError):
            self.service.update_credential(
                name="test_credential",
                username="new_user",
                password="new_pass"
            )

    def test_delete_credential(self):
        """Test that delete_credential deletes a credential."""
        # Set up mock
        self.credential_repo.delete_credential.return_value = True

        # Call delete_credential
        result = self.service.delete_credential("test_credential")

        # Check result
        self.assertTrue(result)

        # Verify credential_repo.delete_credential was called with correct arguments
        self.credential_repo.delete_credential.assert_called_once_with("test_credential")

    def test_delete_credential_error(self):
        """Test that delete_credential raises CredentialError when deleting a credential fails."""
        # Set up mock to raise an exception
        self.credential_repo.delete_credential.side_effect = CredentialError("Delete credential failed")

        # Try to call delete_credential
        with self.assertRaises(CredentialError):
            self.service.delete_credential("test_credential")

    def test_get_credential(self):
        """Test that get_credential returns a credential."""
        # Set up mock
        self.credential_repo.get_by_name.return_value = self.sample_credential

        # Call get_credential
        result = self.service.get_credential("test_credential")

        # Check result
        self.assertEqual(result, self.sample_credential)

        # Verify credential_repo.get_by_name was called with correct arguments
        self.credential_repo.get_by_name.assert_called_once_with("test_credential")

    def test_get_credential_error(self):
        """Test that get_credential raises CredentialError when getting a credential fails."""
        # Set up mock to raise an exception
        self.credential_repo.get_by_name.side_effect = CredentialError("Get credential failed")

        # Try to call get_credential
        with self.assertRaises(CredentialError):
            self.service.get_credential("test_credential")

    def test_list_credentials(self):
        """Test that list_credentials returns a list of credentials."""
        # Set up mock
        self.credential_repo.get_all.return_value = [
            {"name": "credential1", "username": "user1", "password": "pass1"},
            {"name": "credential2", "username": "user2", "password": "pass2"}
        ]

        # Call list_credentials
        result = self.service.list_credentials()

        # Check result
        self.assertEqual(result, ["credential1", "credential2"])

        # Verify credential_repo.get_all was called
        self.credential_repo.get_all.assert_called_once()

    def test_list_credentials_error(self):
        """Test that list_credentials raises CredentialError when listing credentials fails."""
        # Set up mock to raise an exception
        self.credential_repo.get_all.side_effect = CredentialError("List credentials failed")

        # Try to call list_credentials
        with self.assertRaises(CredentialError):
            self.service.list_credentials()


if __name__ == "__main__":
    unittest.main()
