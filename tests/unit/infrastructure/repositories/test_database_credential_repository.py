"""Unit tests for the DatabaseCredentialRepository."""

import unittest
import sqlite3
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any, List, Optional

# Assuming correct path for the module to test and dependencies
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.core.exceptions import CredentialError, RepositoryError, ValidationError
from src.infrastructure.common.database_connection import ConnectionManager

# Mock Action classes if needed by validators (though likely not for credentials)
# Mock IAction if base class uses it (it doesn't directly)

class TestDatabaseCredentialRepository(unittest.TestCase):
    """Test suite for DatabaseCredentialRepository."""

    DB_PATH = ":memory:" # Use in-memory database for tests

    def setUp(self):
        """Set up test environment before each test."""
        # Mock the ConnectionManager to avoid actual DB operations
        self.mock_conn_manager = MagicMock(spec=ConnectionManager)
        self.mock_conn = MagicMock(spec=sqlite3.Connection)
        self.mock_cursor = MagicMock(spec=sqlite3.Cursor)

        # Configure mocks
        # get_connection returns the mock connection
        self.mock_conn_manager.get_connection.return_value = self.mock_conn
        # transaction yields the mock connection
        self.mock_conn_manager.transaction.return_value.__enter__.return_value = self.mock_conn
        # connection returns the mock cursor
        self.mock_conn.cursor.return_value = self.mock_cursor
        # Simulate successful table creation/existence check initially
        self.mock_conn_manager.create_table.return_value = None
        self.mock_conn_manager.table_exists.return_value = True


        # Patch the ConnectionManager *within the scope of the repository module*
        # This is crucial: patch where it's looked up, not where it's defined.
        self.conn_manager_patcher = patch('src.infrastructure.repositories.base.database_repository.ConnectionManager')
        self.mock_conn_manager_class = self.conn_manager_patcher.start()
        self.mock_conn_manager_class.return_value = self.mock_conn_manager

        # Patch the validator to control its behavior if needed
        self.validator_patcher = patch('src.infrastructure.repositories.database_credential_repository.CredentialValidator')
        self.mock_validator = self.validator_patcher.start()
        self.mock_validator.validate_credential_data.return_value = None # Assume valid by default

        # Patch the base validator used for IDs
        self.base_validator_patcher = patch('src.infrastructure.repositories.base.database_repository.EntityValidator')
        self.mock_base_validator = self.base_validator_patcher.start()
        self.mock_base_validator.validate_entity_id.return_value = None

        # Create the repository instance - this will use the mocked ConnectionManager
        self.repository = DatabaseCredentialRepository(db_path=self.DB_PATH)

        # Reset mock calls before each test
        self.mock_conn_manager.reset_mock()
        self.mock_conn.reset_mock()
        self.mock_cursor.reset_mock()
        self.mock_validator.reset_mock()
        self.mock_base_validator.reset_mock()


    def tearDown(self):
        """Clean up after each test."""
        self.conn_manager_patcher.stop()
        self.validator_patcher.stop()
        self.base_validator_patcher.stop()

    def test_init_creates_table_if_not_exists(self):
        """Test that __init__ attempts to create the table."""
        # Reset and re-patch to test init specifically
        self.tearDown()

        mock_conn_mgr = MagicMock(spec=ConnectionManager)
        conn_mgr_patcher = patch('src.infrastructure.repositories.base.database_repository.ConnectionManager', return_value=mock_conn_mgr)
        conn_mgr_patcher.start()

        # Initialize repository - this calls _create_table_if_not_exists
        repo = DatabaseCredentialRepository(db_path=self.DB_PATH)

        # Assert create_table was called on the connection manager instance
        mock_conn_mgr.create_table.assert_called_once()
        args, _ = mock_conn_mgr.create_table.call_args
        self.assertEqual(args[0], repo._TABLE_NAME) # Check table name
        self.assertIn("name TEXT PRIMARY KEY NOT NULL", args[1]) # Check columns SQL fragment
        self.assertIn("username TEXT NOT NULL", args[1])
        self.assertIn("password TEXT NOT NULL", args[1])

        conn_mgr_patcher.stop()
        # Restore original patches for other tests
        self.setUp()


    def test_save_credential_insert(self):
        """Test saving a new credential."""
        credential = {"name": "test_user", "username": "user", "password": "pwd"}
        # Mock execute_modification to simulate insert
        self.mock_conn_manager.execute_modification.return_value = 1 # 1 row affected

        self.repository.save(credential)

        # Verify validation was called
        self.mock_validator.validate_credential_data.assert_called_once_with(credential)
        self.mock_base_validator.validate_entity_id.assert_called_once_with("test_user", entity_type="Credential")

        # Verify execute_modification was called with UPSERT logic
        self.mock_conn_manager.execute_modification.assert_called_once()
        args, _ = self.mock_conn_manager.execute_modification.call_args
        query = args[0]
        params = args[1]

        self.assertIn(f"INSERT INTO {self.repository._TABLE_NAME}", query)
        self.assertIn(f"ON CONFLICT({self.repository._PK_COLUMN}) DO UPDATE SET", query)
        # Check parameter count (name, user, pwd, created, modified + user, pwd, modified for update) = 7
        self.assertEqual(len(params), 7)
        self.assertEqual(params[0], "test_user")
        self.assertEqual(params[1], "user")
        self.assertEqual(params[2], "pwd") # Password stored directly (as per current code)
        # created_at/modified_at are isoformat strings, difficult to match exactly, check type/presence
        self.assertIsInstance(params[3], str) # created_at
        self.assertIsInstance(params[4], str) # modified_at
        # Check UPDATE params
        self.assertEqual(params[5], "user") # username for update
        self.assertEqual(params[6], "pwd")  # password for update


    def test_save_credential_update(self):
        """Test updating an existing credential."""
        credential = {"name": "test_user", "username": "new_user", "password": "new_pwd"}
        # Mock execute_modification to simulate update
        self.mock_conn_manager.execute_modification.return_value = 1

        self.repository.save(credential)

        # Verify validation was called
        self.mock_validator.validate_credential_data.assert_called_once_with(credential)
        self.mock_base_validator.validate_entity_id.assert_called_once_with("test_user", entity_type="Credential")

        # Verify execute_modification was called (UPSERT logic)
        self.mock_conn_manager.execute_modification.assert_called_once()
        args, _ = self.mock_conn_manager.execute_modification.call_args
        query = args[0]
        params = args[1]

        self.assertIn(f"INSERT INTO {self.repository._TABLE_NAME}", query)
        self.assertIn(f"ON CONFLICT({self.repository._PK_COLUMN}) DO UPDATE SET", query)
        self.assertEqual(len(params), 7)
        self.assertEqual(params[0], "test_user")
        self.assertEqual(params[1], "new_user")
        self.assertEqual(params[2], "new_pwd")


    def test_get_by_name_found(self):
        """Test getting an existing credential."""
        name = "existing_user"
        db_row = {"name": name, "username": "user", "password": "pwd"}
        # Configure execute_query to return the mock row
        self.mock_conn_manager.execute_query.return_value = [db_row]

        result = self.repository.get_by_name(name)

        # Verify validation was called
        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Credential")
        # Verify query execution
        expected_query = f"SELECT * FROM {self.repository._TABLE_NAME} WHERE {self.repository._PK_COLUMN} = ?"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query, (name,))
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], name)
        self.assertEqual(result["username"], "user")
        self.assertEqual(result["password"], "pwd")


    def test_get_by_name_not_found(self):
        """Test getting a non-existent credential."""
        name = "non_existent_user"
        # Configure execute_query to return empty list
        self.mock_conn_manager.execute_query.return_value = []

        result = self.repository.get_by_name(name)

        # Verify validation was called
        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Credential")
        # Verify query execution
        expected_query = f"SELECT * FROM {self.repository._TABLE_NAME} WHERE {self.repository._PK_COLUMN} = ?"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query, (name,))
        # Verify result
        self.assertIsNone(result)


    def test_delete_credential_found(self):
        """Test deleting an existing credential."""
        name = "user_to_delete"
        # Configure execute_modification to simulate successful deletion (1 row affected)
        self.mock_conn_manager.execute_modification.return_value = 1

        result = self.repository.delete(name)

        # Verify validation was called
        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Credential")
        # Verify query execution
        expected_query = f"DELETE FROM {self.repository._TABLE_NAME} WHERE {self.repository._PK_COLUMN} = ?"
        self.mock_conn_manager.execute_modification.assert_called_once_with(expected_query, (name,))
        # Verify result
        self.assertTrue(result)


    def test_delete_credential_not_found(self):
        """Test deleting a non-existent credential."""
        name = "non_existent_user"
        # Configure execute_modification to simulate deletion where no rows were affected
        self.mock_conn_manager.execute_modification.return_value = 0

        result = self.repository.delete(name)

         # Verify validation was called
        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Credential")
       # Verify query execution
        expected_query = f"DELETE FROM {self.repository._TABLE_NAME} WHERE {self.repository._PK_COLUMN} = ?"
        self.mock_conn_manager.execute_modification.assert_called_once_with(expected_query, (name,))
        # Verify result
        self.assertFalse(result)


    def test_list_credentials(self):
        """Test listing all credential names."""
        db_rows = [{"name": "user1"}, {"name": "user2"}]
        # Configure execute_query to return the mock rows
        self.mock_conn_manager.execute_query.return_value = db_rows

        result = self.repository.list_credentials()

        # Verify query execution
        expected_query = f"SELECT {self.repository._PK_COLUMN} FROM {self.repository._TABLE_NAME} ORDER BY {self.repository._PK_COLUMN}"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query)
        # Verify result
        self.assertEqual(result, ["user1", "user2"])


    def test_list_credentials_empty(self):
        """Test listing credentials when the repository is empty."""
        # Configure execute_query to return empty list
        self.mock_conn_manager.execute_query.return_value = []

        result = self.repository.list_credentials()

        # Verify query execution
        expected_query = f"SELECT {self.repository._PK_COLUMN} FROM {self.repository._TABLE_NAME} ORDER BY {self.repository._PK_COLUMN}"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query)
        # Verify result
        self.assertEqual(result, [])

    # --- Error Handling Tests ---

    def test_save_invalid_data_raises_error(self):
        """Test that saving invalid credential data raises CredentialError."""
        invalid_credential = {"name": "test", "username": "", "password": "pwd"} # Empty username
        # Configure validator to raise error
        self.mock_validator.validate_credential_data.side_effect = CredentialError("Credential field cannot be empty: username.")

        with self.assertRaisesRegex(CredentialError, "Credential field cannot be empty: username."):
            self.repository.save(invalid_credential)

        # Ensure DB modification was NOT called
        self.mock_conn_manager.execute_modification.assert_not_called()


    def test_save_db_error_raises_repository_error(self):
        """Test that database errors during save raise RepositoryError."""
        credential = {"name": "test_user", "username": "user", "password": "pwd"}
        # Configure execute_modification to raise a database error
        db_error = sqlite3.OperationalError("Disk I/O error")
        self.mock_conn_manager.execute_modification.side_effect = RepositoryError("DB error", cause=db_error)

        with self.assertRaisesRegex(CredentialError, "Error saving credential.*Disk I/O error"):
             self.repository.save(credential)


    def test_get_by_name_db_error_raises_repository_error(self):
        """Test that database errors during get raise RepositoryError."""
        name = "test_user"
        # Configure execute_query to raise a database error
        db_error = sqlite3.IntegrityError("Schema mismatch")
        self.mock_conn_manager.execute_query.side_effect = RepositoryError("DB error", cause=db_error)

        with self.assertRaisesRegex(CredentialError, "Error retrieving credential.*Schema mismatch"):
             self.repository.get_by_name(name)


    def test_delete_db_error_raises_repository_error(self):
        """Test that database errors during delete raise RepositoryError."""
        name = "test_user"
        # Configure execute_modification to raise a database error
        db_error = sqlite3.ProgrammingError("Cannot operate on a closed database.")
        self.mock_conn_manager.execute_modification.side_effect = RepositoryError("DB error", cause=db_error)

        with self.assertRaisesRegex(CredentialError, "Error deleting credential.*Cannot operate on a closed database."):
             self.repository.delete(name)


    def test_list_db_error_raises_repository_error(self):
        """Test that database errors during list raise RepositoryError."""
         # Configure execute_query to raise a database error
        db_error = sqlite3.DatabaseError("Database is locked")
        self.mock_conn_manager.execute_query.side_effect = RepositoryError("DB error", cause=db_error)

        with self.assertRaisesRegex(CredentialError, "Error listing credentials.*Database is locked"):
             self.repository.list_credentials()

    def test_invalid_id_raises_validation_error(self):
        """Test that methods raise ValidationError for invalid IDs."""
        invalid_name = "invalid name" # Contains space
        # Configure base validator to raise error
        self.mock_base_validator.validate_entity_id.side_effect = ValidationError(f"Entity ID '{invalid_name}' contains invalid characters")

        with self.assertRaisesRegex(ValidationError, "contains invalid characters"):
            self.repository.get_by_name(invalid_name)

        with self.assertRaisesRegex(ValidationError, "contains invalid characters"):
            self.repository.delete(invalid_name)

        # Reset side effect for save test
        self.mock_base_validator.validate_entity_id.side_effect = ValidationError(f"Entity ID '{invalid_name}' contains invalid characters")
        with self.assertRaisesRegex(ValidationError, "contains invalid characters"):
             credential = {"name": invalid_name, "username": "user", "password": "pwd"}
             # Validation happens in base save before mapping
             self.repository.save(credential)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)