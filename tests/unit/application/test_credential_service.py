"""Unit tests for the CredentialService."""

import unittest
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.credential_service import CredentialService, WERKZEUG_AVAILABLE
from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError, ValidationError, RepositoryError

# Mock werkzeug hashing functions if available, otherwise use simple mocks
MOCK_HASH_PREFIX = "hashed$" if WERKZEUG_AVAILABLE else "plaintext:"
def mock_generate_hash(password, method, salt_length):
    # Simulate prefix based on availability for realistic testing
    prefix = "pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:"
    return prefix + password # Simple mock, not real hashing

def mock_check_hash(pwhash, password):
    if pwhash is None: return False
    if pwhash.startswith("pbkdf2:"):
         # Simulate check for mock hash
         return pwhash[len("pbkdf2:"):] == password
    elif pwhash.startswith("plaintext:"):
        # Simulate check for plaintext fallback
        return pwhash[len("plaintext:"):] == password
    return False # Unknown hash format


@patch('src.application.services.credential_service.generate_password_hash', side_effect=mock_generate_hash)
@patch('src.application.services.credential_service.check_password_hash', side_effect=mock_check_hash)
class TestCredentialService(unittest.TestCase):
    """Test suite for CredentialService."""

    def setUp(self, mock_check, mock_generate): # Mocks passed by decorators
        """Set up mocks for each test."""
        self.mock_repo = MagicMock(spec=ICredentialRepository)
        self.service = CredentialService(self.mock_repo)
        # Keep references to mocks if needed for assert counts
        self.mock_generate_hash = mock_generate
        self.mock_check_hash = mock_check
        # Reset mocks for each test
        self.mock_generate_hash.reset_mock()
        self.mock_check_hash.reset_mock()
        self.mock_repo.reset_mock()


    def test_create_credential_success(self, mock_check, mock_generate):
        """Test creating a new credential successfully hashes and saves."""
        name, user, pwd = "new_cred", "new_user", "new_pass"
        expected_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + pwd
        expected_data = {"name": name, "username": user, "password": expected_hash}

        self.mock_repo.get_by_name.return_value = None
        self.mock_repo.save.return_value = None

        result = self.service.create_credential(name, user, pwd)

        self.assertTrue(result)
        self.mock_generate_hash.assert_called_once_with(pwd, method=ANY, salt_length=ANY)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_repo.save.assert_called_once()
        call_args, _ = self.mock_repo.save.call_args
        saved_data = call_args[0]
        self.assertEqual(saved_data["name"], name)
        self.assertEqual(saved_data["username"], user)
        self.assertEqual(saved_data["password"], expected_hash)


    def test_create_credential_already_exists(self, mock_check, mock_generate):
        """Test creating a credential that already exists raises CredentialError."""
        name, user, pwd = "existing_cred", "user", "pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": user, "password": "some_hash"}

        with self.assertRaisesRegex(CredentialError, f"Credential '{name}' already exists."):
            self.service.create_credential(name, user, pwd)

        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_generate_hash.assert_not_called()
        self.mock_repo.save.assert_not_called()


    def test_create_credential_empty_input(self, mock_check, mock_generate):
        """Test creating with empty input raises ValidationError."""
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("", "user", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "user", "")

        self.mock_repo.get_by_name.assert_not_called()
        self.mock_generate_hash.assert_not_called()
        self.mock_repo.save.assert_not_called()

    def test_delete_credential_success(self, mock_check, mock_generate):
        """Test deleting an existing credential."""
        name = "delete_me"
        self.mock_repo.delete.return_value = True

        result = self.service.delete_credential(name)

        self.assertTrue(result)
        self.mock_repo.delete.assert_called_once_with(name)


    def test_delete_credential_not_found(self, mock_check, mock_generate):
        """Test deleting a non-existent credential."""
        name = "not_found"
        self.mock_repo.delete.return_value = False

        result = self.service.delete_credential(name)

        self.assertFalse(result)
        self.mock_repo.delete.assert_called_once_with(name)


    def test_get_credential_success(self, mock_check, mock_generate):
        """Test retrieving an existing credential (returns hash)."""
        name = "get_me"
        expected_data = {"name": name, "username": "user", "password": "hashed_password"}
        self.mock_repo.get_by_name.return_value = expected_data

        result = self.service.get_credential(name)

        self.assertEqual(result, expected_data)
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_get_credential_not_found(self, mock_check, mock_generate):
        """Test retrieving a non-existent credential."""
        name = "not_found"
        self.mock_repo.get_by_name.return_value = None

        result = self.service.get_credential(name)

        self.assertIsNone(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_list_credentials_success(self, mock_check, mock_generate):
        """Test listing credential names."""
        expected_names = ["cred1", "cred2"]
        self.mock_repo.list_credentials.return_value = expected_names

        result = self.service.list_credentials()

        self.assertEqual(result, expected_names)
        self.mock_repo.list_credentials.assert_called_once()


    def test_verify_credential_success(self, mock_check, mock_generate):
        """Test successful password verification."""
        name, pwd_to_check = "mycred", "correct_pass"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + pwd_to_check
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertTrue(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_failure(self, mock_check, mock_generate):
        """Test failed password verification (wrong password)."""
        name, pwd_to_check = "mycred", "wrong_pass"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + "correct_pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_not_found(self, mock_check, mock_generate):
        """Test verification fails if credential doesn't exist."""
        name, pwd_to_check = "notfound", "pass"
        self.mock_repo.get_by_name.return_value = None

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_not_called()


    def test_verify_credential_empty_password_check(self, mock_check, mock_generate):
        """Test verification fails immediately for empty password check."""
        name = "mycred"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + "correct_pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, "")

        self.assertFalse(result)
        # Repo should not be called if password check is empty
        self.mock_repo.get_by_name.assert_not_called()
        self.mock_check_hash.assert_not_called()

    def test_verify_credential_missing_hash(self, mock_check, mock_generate):
        """Test verification fails if stored credential has no password hash."""
        name = "nohash"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": None} # Simulate missing hash

        result = self.service.verify_credential(name, "some_pass")

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)