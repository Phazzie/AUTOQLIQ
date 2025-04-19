"""Unit tests for the CredentialService (Post-Refactoring)."""

import unittest
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.credential_service import CredentialService
# Import the new password handler interface
from src.application.security.password_handler import IPasswordHandler
from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError, ValidationError, RepositoryError

# No need to patch werkzeug here anymore, we inject a mock password handler

class TestCredentialServiceRefactored(unittest.TestCase):
    """Test suite for CredentialService after extracting IPasswordHandler."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_repo = MagicMock(spec=ICredentialRepository)
        # Create a mock Password Handler
        self.mock_pw_handler = MagicMock(spec=IPasswordHandler)
        # Initialize service with mock repo and mock handler
        self.service = CredentialService(self.mock_repo, self.mock_pw_handler)

        # Reset mocks for each test
        self.mock_repo.reset_mock()
        self.mock_pw_handler.reset_mock()


    def test_create_credential_success(self):
        """Test creating a new credential successfully calls handler and repo."""
        name, user, pwd = "new_cred", "new_user", "new_pass"
        expected_hash = "mock_hashed_password"
        expected_data = {"name": name, "username": user, "password": expected_hash}

        self.mock_repo.get_by_name.return_value = None
        self.mock_pw_handler.hash_password.return_value = expected_hash
        self.mock_repo.save.return_value = None # Simulate success

        result = self.service.create_credential(name, user, pwd)

        self.assertTrue(result)
        self.mock_pw_handler.hash_password.assert_called_once_with(pwd)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_repo.save.assert_called_once_with(expected_data)


    def test_create_credential_already_exists(self):
        """Test creating a credential that already exists raises CredentialError."""
        name, user, pwd = "existing_cred", "user", "pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": user, "password": "some_hash"}

        with self.assertRaisesRegex(CredentialError, f"Credential '{name}' already exists."):
            self.service.create_credential(name, user, pwd)

        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_pw_handler.hash_password.assert_not_called()
        self.mock_repo.save.assert_not_called()


    def test_create_credential_empty_input(self):
        """Test creating with empty input raises ValidationError."""
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("", "user", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "user", "")

        self.mock_repo.get_by_name.assert_not_called()
        self.mock_pw_handler.hash_password.assert_not_called()
        self.mock_repo.save.assert_not_called()

    def test_delete_credential_success(self):
        """Test deleting an existing credential."""
        name = "delete_me"
        self.mock_repo.delete.return_value = True

        result = self.service.delete_credential(name)

        self.assertTrue(result)
        self.mock_repo.delete.assert_called_once_with(name)


    def test_get_credential_success_removes_password(self):
        """Test retrieving credential removes password hash."""
        name = "get_me"
        # Repo returns data *with* the hash
        repo_data = {"name": name, "username": "user", "password": "hashed_password"}
        self.mock_repo.get_by_name.return_value = repo_data

        result = self.service.get_credential(name)

        # Service should return data *without* the hash
        expected_safe_data = {"name": name, "username": "user"}
        self.assertEqual(result, expected_safe_data)
        self.assertNotIn('password', result) # Ensure password key is removed
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_get_credential_not_found(self):
        """Test retrieving a non-existent credential."""
        name = "not_found"
        self.mock_repo.get_by_name.return_value = None
        result = self.service.get_credential(name)
        self.assertIsNone(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_list_credentials_success(self):
        """Test listing credential names."""
        expected_names = ["cred1", "cred2"]
        self.mock_repo.list_credentials.return_value = expected_names

        result = self.service.list_credentials()

        self.assertEqual(result, expected_names)
        self.mock_repo.list_credentials.assert_called_once()


    def test_verify_credential_success(self):
        """Test successful password verification delegates to handler."""
        name, pwd_to_check = "mycred", "correct_pass"
        stored_hash = "mock_hashed_password"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}
        self.mock_pw_handler.verify_password.return_value = True # Mock handler returns True

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertTrue(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_pw_handler.verify_password.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_failure(self):
        """Test failed password verification delegates to handler."""
        name, pwd_to_check = "mycred", "wrong_pass"
        stored_hash = "mock_hashed_password"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}
        self.mock_pw_handler.verify_password.return_value = False # Mock handler returns False

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_pw_handler.verify_password.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_not_found(self):
        """Test verification fails if credential doesn't exist."""
        name, pwd_to_check = "notfound", "pass"
        self.mock_repo.get_by_name.return_value = None

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_pw_handler.verify_password.assert_not_called()


    def test_verify_credential_empty_password_check(self):
        """Test verification fails immediately for empty password check."""
        name = "mycred"; result = self.service.verify_credential(name, "")
        self.assertFalse(result); self.mock_repo.get_by_name.assert_not_called(); self.mock_pw_handler.verify_password.assert_not_called()

    def test_verify_credential_missing_hash(self):
        """Test verification fails if stored credential has no password hash."""
        name = "nohash"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": None} # Simulate missing hash
        result = self.service.verify_credential(name, "some_pass")
        self.assertFalse(result); self.mock_repo.get_by_name.assert_called_once_with(name); self.mock_pw_handler.verify_password.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
