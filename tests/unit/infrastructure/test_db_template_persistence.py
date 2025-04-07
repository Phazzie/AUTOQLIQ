"""Unit tests for the DatabaseWorkflowRepository template methods."""

import unittest
import sqlite3
import json
from unittest.mock import patch, MagicMock, call, ANY
from typing import Dict, Any, List, Optional

# Assuming correct paths for imports
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.core.exceptions import RepositoryError, ValidationError, SerializationError
from src.infrastructure.common.database_connection import ConnectionManager

class TestDatabaseTemplatePersistence(unittest.TestCase):
    """Test suite for DatabaseWorkflowRepository template methods using mocked DB."""

    DB_PATH = ":memory:" # Use in-memory database path for config

    def setUp(self):
        """Set up mocks for ConnectionManager and validators."""
        self.mock_conn_manager = MagicMock(spec=ConnectionManager)
        self.mock_conn = MagicMock(spec=sqlite3.Connection)
        self.mock_cursor = MagicMock(spec=sqlite3.Cursor)
        self.mock_conn_manager.get_connection.return_value = self.mock_conn
        self.mock_conn_manager.transaction.return_value.__enter__.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_conn_manager.create_table.return_value = None
        self.mock_conn_manager.table_exists.return_value = True

        self.conn_manager_patcher = patch('src.infrastructure.repositories.base.database_repository.ConnectionManager')
        self.mock_conn_manager_class = self.conn_manager_patcher.start()
        self.mock_conn_manager_class.return_value = self.mock_conn_manager

        self.base_validator_patcher = patch('src.infrastructure.repositories.base.database_repository.EntityValidator')
        self.mock_base_validator = self.base_validator_patcher.start()
        self.mock_base_validator.validate_entity_id.return_value = None

        # Create the repository instance - this will use the mocked ConnectionManager
        # It will call _create_table_if_not_exists for workflows AND _create_templates_table_if_not_exists
        self.repository = DatabaseWorkflowRepository(db_path=self.DB_PATH)

        # Reset mocks *after* init
        self.mock_conn_manager.reset_mock()
        self.mock_conn.reset_mock()
        self.mock_cursor.reset_mock()
        self.mock_base_validator.reset_mock()

    def tearDown(self):
        """Clean up patches."""
        self.conn_manager_patcher.stop()
        self.base_validator_patcher.stop()

    def test_init_creates_templates_table(self):
        """Test that __init__ attempts to create the templates table."""
        # Reset and re-patch to test init specifically
        self.tearDown()
        mock_conn_mgr = MagicMock(spec=ConnectionManager)
        conn_mgr_patcher = patch('src.infrastructure.repositories.base.database_repository.ConnectionManager', return_value=mock_conn_mgr)
        conn_mgr_patcher.start()
        repo = DatabaseWorkflowRepository(db_path=self.DB_PATH)
        # Assert create_table called for templates table
        template_call = next((c for c in mock_conn_mgr.create_table.call_args_list if c[0][0] == repo._TMPL_TABLE_NAME), None)
        self.assertIsNotNone(template_call); self.assertIn("actions_json TEXT NOT NULL", template_call[0][1])
        conn_mgr_patcher.stop(); self.setUp() # Restore mocks

    def test_save_template_success(self):
        """Test saving a new template executes correct UPSERT."""
        name = "tmpl1"; data = [{"type":"A"}]; actions_json = json.dumps(data)
        self.mock_conn_manager.execute_modification.return_value = 1 # Simulate insert

        self.repository.save_template(name, data)

        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Template")
        self.mock_conn_manager.execute_modification.assert_called_once()
        args, _ = self.mock_conn_manager.execute_modification.call_args
        query = args[0]; params = args[1]
        self.assertIn(f"INSERT INTO {self.repository._TMPL_TABLE_NAME}", query)
        self.assertIn(f"ON CONFLICT({self.repository._TMPL_PK_COLUMN}) DO UPDATE SET", query)
        self.assertEqual(params[0], name); self.assertEqual(params[1], actions_json)
        self.assertIsInstance(params[2], str) # created_at
        self.assertIsInstance(params[3], str) # modified_at
        # Check update params (actions_json, modified_at)
        self.assertEqual(params[4], actions_json)
        self.assertEqual(params[5], params[3]) # modified_at should be the same


    def test_save_template_update(self):
        """Test saving an existing template updates it."""
        name = "tmpl1"; data = [{"type":"B"}]; actions_json = json.dumps(data)
        self.mock_conn_manager.execute_modification.return_value = 1 # Simulate update

        self.repository.save_template(name, data) # Should trigger UPSERT's update path

        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Template")
        self.mock_conn_manager.execute_modification.assert_called_once()
        # Query/params are the same for UPSERT, DB handles the update part

    def test_save_template_invalid_data(self):
        """Test saving template with non-list data raises SerializationError."""
        with self.assertRaises(SerializationError): self.repository.save_template("bad1", "s") # type: ignore
        with self.assertRaises(SerializationError): self.repository.save_template("bad2", [{}, "s"]) # type: ignore

    def test_load_template_success(self):
        """Test loading an existing template."""
        name = "tmpl_load"; actions_data = [{"type":"C"}]; actions_json = json.dumps(actions_data)
        db_row = {"actions_json": actions_json}
        self.mock_conn_manager.execute_query.return_value = [db_row]

        result = self.repository.load_template(name)

        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Template")
        expected_query = f"SELECT actions_json FROM {self.repository._TMPL_TABLE_NAME} WHERE {self.repository._TMPL_PK_COLUMN} = ?"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query, (name,))
        self.assertEqual(result, actions_data)

    def test_load_template_not_found(self):
        """Test loading non-existent template raises RepositoryError."""
        name = "not_found_tmpl"; self.mock_conn_manager.execute_query.return_value = []
        with self.assertRaisesRegex(RepositoryError, "Template not found"): self.repository.load_template(name)

    def test_load_template_invalid_json(self):
        """Test loading template with invalid JSON raises SerializationError."""
        name = "bad_json_tmpl"; db_row = {"actions_json": "{bad json"}
        self.mock_conn_manager.execute_query.return_value = [db_row]
        with self.assertRaisesRegex(SerializationError, "Invalid JSON"): self.repository.load_template(name)

    def test_delete_template_success(self):
        """Test deleting an existing template."""
        name = "tmpl_del"; self.mock_conn_manager.execute_modification.return_value = 1
        result = self.repository.delete_template(name)
        self.assertTrue(result)
        self.mock_base_validator.validate_entity_id.assert_called_once_with(name, entity_type="Template")
        expected_query = f"DELETE FROM {self.repository._TMPL_TABLE_NAME} WHERE {self.repository._TMPL_PK_COLUMN} = ?"
        self.mock_conn_manager.execute_modification.assert_called_once_with(expected_query, (name,))

    def test_delete_template_not_found(self):
        """Test deleting a non-existent template."""
        name = "tmpl_del_miss"; self.mock_conn_manager.execute_modification.return_value = 0
        result = self.repository.delete_template(name); self.assertFalse(result)

    def test_list_templates(self):
        """Test listing template names."""
        db_rows = [{self.repository._TMPL_PK_COLUMN: "tmpl_b"}, {self.repository._TMPL_PK_COLUMN: "tmpl_a"}]
        self.mock_conn_manager.execute_query.return_value = db_rows
        result = self.repository.list_templates()
        expected_query = f"SELECT {self.repository._TMPL_PK_COLUMN} FROM {self.repository._TMPL_TABLE_NAME} ORDER BY {self.repository._TMPL_PK_COLUMN}"
        self.mock_conn_manager.execute_query.assert_called_once_with(expected_query)
        self.assertEqual(result, ["tmpl_b", "tmpl_a"]) # Order as returned by mock


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)