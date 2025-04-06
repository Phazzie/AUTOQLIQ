"""Tests for the database repository base class."""
import unittest
import sqlite3
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.base.database_repository import DatabaseRepository
from src.core.exceptions import AutoQliqError

class TestDatabaseRepository(unittest.TestCase):
    """Test cases for the DatabaseRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test database repository
        self.repo = DatabaseRepository("test_logger", ":memory:")

    def test_initialization(self):
        """Test that a DatabaseRepository can be initialized with a database path."""
        # Check that the repository was initialized correctly
        self.assertEqual(self.repo.db_path, ":memory:")
        self.assertIsNotNone(self.repo.logger)

    def test_get_connection(self):
        """Test that get_connection returns a database connection."""
        # Get a connection
        conn = self.repo._get_connection()

        # Check that it's a valid connection
        self.assertIsInstance(conn, sqlite3.Connection)

        # Clean up
        conn.close()

    def test_get_connection_error(self):
        """Test that get_connection raises AutoQliqError if the connection fails."""
        # Create a repository with an invalid database path
        repo = DatabaseRepository("test_logger", "/nonexistent/path/db.sqlite")

        # Try to get a connection
        with self.assertRaises(AutoQliqError):
            repo._get_connection()

    def test_execute_query(self):
        """Test that execute_query executes a SQL query."""
        # Create a test table
        self.repo._execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")

        # Insert some data
        self.repo._execute_query("INSERT INTO test (name) VALUES (?)", ("test1",))
        self.repo._execute_query("INSERT INTO test (name) VALUES (?)", ("test2",))

        # Query the data
        rows = self.repo._execute_query("SELECT * FROM test ORDER BY id")

        # Check the results
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "test1")
        self.assertEqual(rows[1]["name"], "test2")

    def test_execute_query_error(self):
        """Test that execute_query raises AutoQliqError if the query fails."""
        # Try to execute an invalid query
        with self.assertRaises(AutoQliqError):
            self.repo._execute_query("SELECT * FROM nonexistent_table")

    def test_table_exists(self):
        """Test that table_exists returns True if the table exists."""
        # Create a test table
        self.repo._execute_query("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")

        # Check that the table exists
        self.assertTrue(self.repo._table_exists("test"))

        # Check that a nonexistent table doesn't exist
        self.assertFalse(self.repo._table_exists("nonexistent"))

    def test_create_table(self):
        """Test that create_table creates a table if it doesn't exist."""
        # Create a test table
        self.repo._create_table("test", "id INTEGER PRIMARY KEY, name TEXT")

        # Check that the table exists
        self.assertTrue(self.repo._table_exists("test"))

        # Try to create the table again (should not raise an error)
        self.repo._create_table("test", "id INTEGER PRIMARY KEY, name TEXT")

    def test_create_table_error(self):
        """Test that create_table raises AutoQliqError if the table creation fails."""
        # Try to create a table with invalid SQL
        with self.assertRaises(AutoQliqError):
            self.repo._create_table("test", "invalid SQL")

if __name__ == "__main__":
    unittest.main()
