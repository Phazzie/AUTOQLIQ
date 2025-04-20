"""Integration tests for Database Repositories using a real (in-memory) database."""

import unittest
import sqlite3
import os
import json
from typing import Dict, List
from datetime import datetime, timedelta, timezone # Added timezone
import time

# Assuming correct paths for imports
from src.infrastructure.repositories.database_credential_repository import DatabaseCredentialRepository
from src.infrastructure.repositories.database_workflow_repository import DatabaseWorkflowRepository
from src.core.exceptions import CredentialError, WorkflowError, RepositoryError, ValidationError, SerializationError
# Use concrete Mock actions for testing workflow save/load
from tests.unit.core.test_actions import MockTestAction # Import from actions test


# Use :memory: for a clean database on each run, no file cleanup needed
# This ensures tests are isolated and don't affect the actual database
IN_MEMORY_DB_PATH = ":memory:"

class TestDatabaseRepositoryIntegration(unittest.TestCase):
    """Integration tests for database repositories using in-memory SQLite."""

    def setUp(self):
        """Create repository instances using a fresh in-memory database for each test."""
        # Each test gets a fresh in-memory database connection implicitly via ConnectionManager
        # The repositories will create tables on init if they don't exist in the :memory: db
        self.cred_repo = DatabaseCredentialRepository(db_path=IN_MEMORY_DB_PATH)
        self.wf_repo = DatabaseWorkflowRepository(db_path=IN_MEMORY_DB_PATH)
        # Both repos point to the *same* in-memory db for tests involving both tables
        # This is important for testing relationships between credentials and workflows

    def tearDown(self):
        """Database is automatically discarded when connection closes."""
        del self.cred_repo
        del self.wf_repo


    # --- Credential Repository Tests ---

    def test_credential_save_and_get(self):
        """Test saving and retrieving a credential."""
        cred_name = "integ_user"; cred_data = {"name": cred_name, "username": "test@test.com", "password": "hashed_password"}
        self.cred_repo.save(cred_data)
        retrieved = self.cred_repo.get_by_name(cred_name)
        self.assertIsNotNone(retrieved); self.assertEqual(retrieved["name"], cred_name)
        self.assertEqual(retrieved["username"], "test@test.com"); self.assertEqual(retrieved["password"], "hashed_password")

    def test_credential_save_update_checks_timestamp(self):
        """Test updating an existing credential checks modified timestamp."""
        cred_name = "update_user"
        cred_data1 = {"name": cred_name, "username": "initial", "password": "hash1"}
        self.cred_repo.save(cred_data1)
        # Get initial metadata - need direct query as cred repo doesn't have get_metadata
        conn = sqlite3.connect(IN_MEMORY_DB_PATH); cursor = conn.cursor()
        cursor.execute("SELECT modified_at FROM credentials WHERE name = ?", (cred_name,))
        time1_mod_str = cursor.fetchone()[0]; conn.close()
        time.sleep(0.01) # Ensure time progresses
        cred_data2 = {"name": cred_name, "username": "updated", "password": "hash2"}
        self.cred_repo.save(cred_data2) # UPSERT logic
        retrieved = self.cred_repo.get_by_name(cred_name)
        self.assertIsNotNone(retrieved); self.assertEqual(retrieved["username"], "updated")
        # Check timestamps again
        conn = sqlite3.connect(IN_MEMORY_DB_PATH); cursor = conn.cursor()
        cursor.execute("SELECT modified_at FROM credentials WHERE name = ?", (cred_name,))
        time2_mod_str = cursor.fetchone()[0]; conn.close()
        self.assertNotEqual(time1_mod_str, time2_mod_str)
        self.assertLess(datetime.fromisoformat(time1_mod_str), datetime.fromisoformat(time2_mod_str))

    def test_credential_get_not_found(self):
        """Test getting a non-existent credential returns None."""
        self.assertIsNone(self.cred_repo.get_by_name("non_existent"))

    def test_credential_list(self):
        """Test listing credentials returns sorted names."""
        self.cred_repo.save({"name": "cred_b", "username": "u", "password": "p"})
        self.cred_repo.save({"name": "cred_a", "username": "u", "password": "p"})
        self.cred_repo.save({"name": "cred_c", "username": "u", "password": "p"})
        self.assertEqual(self.cred_repo.list_credentials(), ["cred_a", "cred_b", "cred_c"])

    def test_credential_delete_found(self):
        """Test deleting an existing credential."""
        cred_name = "delete_me"; self.cred_repo.save({"name": cred_name, "username": "u", "password": "p"})
        deleted = self.cred_repo.delete(cred_name); self.assertTrue(deleted)
        self.assertIsNone(self.cred_repo.get_by_name(cred_name))

    def test_credential_delete_not_found(self):
        """Test deleting a non-existent credential."""
        self.assertFalse(self.cred_repo.delete("not_there"))

    def test_credential_invalid_name_validation(self):
        """Test DB repo catches invalid names via validator."""
        with self.assertRaises(ValidationError): self.cred_repo.get_by_name("invalid name")
        with self.assertRaises(ValidationError): self.cred_repo.delete("invalid/name")
        with self.assertRaises(ValidationError): self.cred_repo.save({"name": " invalid ", "username":"u", "password":"p"})

    def test_credential_invalid_data_validation(self):
        """Test DB repo catches invalid data via validator."""
        with self.assertRaisesRegex(CredentialError, "missing required field.*password"):
            self.cred_repo.save({"name": "valid_name", "username":"u"})


    # --- Workflow Repository Tests ---

    def test_workflow_save_and_load(self):
        """Test saving and loading a workflow with actions."""
        wf_name = "integ_wf"; actions = [MockTestAction(name="A1", param="vA"), MockTestAction(name="A2", param="vB")]
        self.wf_repo.save(wf_name, actions)
        loaded = self.wf_repo.load(wf_name)
        self.assertEqual(len(loaded), 2); self.assertEqual(loaded[0].name, "A1"); self.assertEqual(loaded[1].name, "A2")

    def test_workflow_save_update_checks_timestamp(self):
        """Test updating an existing workflow updates modified time."""
        wf_name = "update_wf"; actions1 = [MockTestAction(name="Init", param="p1")]
        self.wf_repo.save(wf_name, actions1); meta1 = self.wf_repo.get_metadata(wf_name); time1_mod = meta1['modified_at']
        time.sleep(0.01)
        actions2 = [MockTestAction(name="Upd", param="p2")]; self.wf_repo.save(wf_name, actions2)
        loaded = self.wf_repo.load(wf_name); meta2 = self.wf_repo.get_metadata(wf_name); time2_mod = meta2['modified_at']
        self.assertEqual(len(loaded), 1); self.assertEqual(loaded[0].name, "Upd")
        self.assertNotEqual(time1_mod, time2_mod); self.assertLess(datetime.fromisoformat(time1_mod), datetime.fromisoformat(time2_mod))

    def test_workflow_create_and_load_empty(self):
        """Test creating an empty workflow."""
        wf_name = "empty_wf"; self.wf_repo.create_workflow(wf_name)
        loaded = self.wf_repo.load(wf_name); self.assertEqual(loaded, [])

    def test_workflow_load_invalid_json_raises_serialization_error(self):
        """Test loading workflow with invalid JSON raises SerializationError."""
        wf_name = "bad_json_wf"
        conn = sqlite3.connect(IN_MEMORY_DB_PATH); now = datetime.now().isoformat()
        try: conn.execute(f"INSERT INTO {self.wf_repo._WF_TABLE_NAME} (name, actions_json, created_at, modified_at) VALUES (?, ?, ?, ?)", (wf_name, "{bad", now, now)); conn.commit()
        finally: conn.close()
        with self.assertRaisesRegex(SerializationError, "Invalid JSON"): self.wf_repo.load(wf_name)

    def test_workflow_load_unknown_action_type_raises_serialization_error(self):
        """Test loading workflow with unknown action type raises SerializationError."""
        wf_name = "unknown_action_wf"; bad_data = json.dumps([{"type": "DoesNotExist", "name": "Bad"}])
        conn = sqlite3.connect(IN_MEMORY_DB_PATH); now = datetime.now().isoformat()
        try: conn.execute(f"INSERT INTO {self.wf_repo._WF_TABLE_NAME} (name, actions_json, created_at, modified_at) VALUES (?, ?, ?, ?)", (wf_name, bad_data, now, now)); conn.commit()
        finally: conn.close()
        with self.assertRaisesRegex(SerializationError, "Unknown action type.*DoesNotExist"): self.wf_repo.load(wf_name)

    def test_workflow_list(self):
        """Test listing workflows returns sorted names."""
        self.wf_repo.create_workflow("wf_z"); self.wf_repo.create_workflow("wf_a")
        self.assertEqual(self.wf_repo.list_workflows(), ["wf_a", "wf_z"])

    def test_workflow_delete_found(self):
        """Test deleting an existing workflow."""
        wf_name = "delete_wf"; self.wf_repo.create_workflow(wf_name)
        deleted = self.wf_repo.delete(wf_name); self.assertTrue(deleted)
        with self.assertRaises(RepositoryError): self.wf_repo.load(wf_name)

    # --- Template Methods (DB Implementation) ---

    def test_db_template_save_and_load(self):
        """Test saving and loading a template in the database."""
        tmpl_name = "db_tmpl_1"
        actions_data = [{"type": "Click", "name": "ClickA", "selector": "#a"}]
        self.wf_repo.save_template(tmpl_name, actions_data)

        loaded_data = self.wf_repo.load_template(tmpl_name)
        self.assertEqual(loaded_data, actions_data)

    def test_db_template_save_update(self):
        """Test updating an existing template in the database."""
        tmpl_name = "db_tmpl_update"
        data1 = [{"type": "Wait", "duration_seconds": 1}]
        data2 = [{"type": "Navigate", "url": "test.com"}]
        self.wf_repo.save_template(tmpl_name, data1)
        self.wf_repo.save_template(tmpl_name, data2) # UPSERT

        loaded_data = self.wf_repo.load_template(tmpl_name)
        self.assertEqual(loaded_data, data2)

    def test_db_template_load_not_found(self):
        """Test loading non-existent template raises RepositoryError."""
        with self.assertRaisesRegex(RepositoryError, "Template not found"):
            self.wf_repo.load_template("db_tmpl_missing")

    def test_db_template_list(self):
        """Test listing templates from the database."""
        self.wf_repo.save_template("db_tmpl_z", [])
        self.wf_repo.save_template("db_tmpl_a", [])
        templates = self.wf_repo.list_templates()
        self.assertEqual(templates, ["db_tmpl_a", "db_tmpl_z"]) # Should be sorted

    def test_db_template_delete_found(self):
        """Test deleting an existing template from the database."""
        tmpl_name = "db_tmpl_del"; self.wf_repo.save_template(tmpl_name, [])
        deleted = self.wf_repo.delete_template(tmpl_name); self.assertTrue(deleted)
        with self.assertRaises(RepositoryError): self.wf_repo.load_template(tmpl_name)

    def test_db_template_delete_not_found(self):
        """Test deleting a non-existent template from the database."""
        deleted = self.wf_repo.delete_template("db_tmpl_not_there"); self.assertFalse(deleted)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)