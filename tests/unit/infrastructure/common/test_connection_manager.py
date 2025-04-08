#!/usr/bin/env python3
"""
Unit tests for ConnectionManager class in src/infrastructure/common/connection_manager.py.
"""

import os
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch, MagicMock

# Import the module under test
from src.infrastructure.common.connection_manager import ConnectionManager
from src.core.exceptions import RepositoryError


class TestConnectionManager(unittest.TestCase):
    """
    Test cases for the ConnectionManager class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 6 main responsibilities of ConnectionManager:
    1. Managing database connections (creating, closing)
    2. Connection pooling per thread
    3. Executing queries (SELECT)
    4. Executing updates (INSERT, UPDATE, DELETE)
    5. Transaction management (begin, commit, rollback)
    6. Database schema validation (checking if tables exist)
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_db.sqlite')
        
        # Create the connection manager
        self.connection_manager = ConnectionManager(self.db_path)
        
        # Create a test table
        self.connection_manager.execute_script('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            );
        ''')
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Close the connection
        if hasattr(self, 'connection_manager'):
            self.connection_manager.close_connection()
        
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_init_with_invalid_path(self):
        """Test initialization with an invalid database path."""
        # Test with empty path
        with self.assertRaises(ValueError):
            ConnectionManager('')
        
        # Test with non-existent directory that cannot be created
        with patch('os.makedirs', side_effect=OSError('Permission denied')):
            with self.assertRaises(RepositoryError):
                ConnectionManager('/nonexistent/path/db.sqlite')
    
    def test_init_creates_directory(self):
        """Test that initialization creates the database directory if it doesn't exist."""
        # Create a path in a non-existent subdirectory of the temp dir
        new_db_path = os.path.join(self.temp_dir.name, 'subdir', 'new_db.sqlite')
        
        # Initialize connection manager with this path
        ConnectionManager(new_db_path)
        
        # Verify directory was created
        self.assertTrue(os.path.exists(os.path.dirname(new_db_path)))
    
    def test_get_connection(self):
        """Test getting a database connection."""
        # Get a connection
        connection = self.connection_manager.get_connection()
        
        # Verify it's a valid SQLite connection
        self.assertIsInstance(connection, sqlite3.Connection)
        
        # Verify it's the same connection on subsequent calls
        connection2 = self.connection_manager.get_connection()
        self.assertIs(connection, connection2)
    
    def test_close_connection(self):
        """Test closing a database connection."""
        # Get a connection
        connection = self.connection_manager.get_connection()
        
        # Close it
        self.connection_manager.close_connection()
        
        # Verify the connection is closed
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')
        
        # Verify getting a new connection works after closing
        new_connection = self.connection_manager.get_connection()
        self.assertIsInstance(new_connection, sqlite3.Connection)
        self.assertIsNot(connection, new_connection)
    
    def test_execute_query(self):
        """Test executing a SELECT query."""
        # Insert some test data
        self.connection_manager.execute_update(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test_name", 42)
        )
        
        # Execute a query
        rows = self.connection_manager.execute_query(
            "SELECT * FROM test_table WHERE name = ?",
            ("test_name",)
        )
        
        # Verify the result
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], "test_name")
        self.assertEqual(rows[0]['value'], 42)
        
        # Test with dict parameters
        rows = self.connection_manager.execute_query(
            "SELECT * FROM test_table WHERE name = :name",
            {"name": "test_name"}
        )
        
        # Verify the result
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], "test_name")
        
        # Test with no parameters
        rows = self.connection_manager.execute_query("SELECT COUNT(*) as count FROM test_table")
        self.assertEqual(rows[0]['count'], 1)
    
    def test_execute_query_error(self):
        """Test error handling in execute_query."""
        # Test with invalid SQL
        with self.assertRaises(RepositoryError):
            self.connection_manager.execute_query("SELECT * FROM nonexistent_table")
    
    def test_execute_update(self):
        """Test executing an INSERT, UPDATE, or DELETE query."""
        # Test INSERT
        rows_affected = self.connection_manager.execute_update(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("test_name", 42)
        )
        self.assertEqual(rows_affected, 1)
        
        # Test UPDATE
        rows_affected = self.connection_manager.execute_update(
            "UPDATE test_table SET value = ? WHERE name = ?",
            (43, "test_name")
        )
        self.assertEqual(rows_affected, 1)
        
        # Verify the update worked
        rows = self.connection_manager.execute_query("SELECT value FROM test_table WHERE name = ?", ("test_name",))
        self.assertEqual(rows[0]['value'], 43)
        
        # Test DELETE
        rows_affected = self.connection_manager.execute_update(
            "DELETE FROM test_table WHERE name = ?",
            ("test_name",)
        )
        self.assertEqual(rows_affected, 1)
        
        # Verify the delete worked
        rows = self.connection_manager.execute_query("SELECT * FROM test_table")
        self.assertEqual(len(rows), 0)
    
    def test_execute_update_error(self):
        """Test error handling in execute_update."""
        # Test with invalid SQL
        with self.assertRaises(RepositoryError):
            self.connection_manager.execute_update("UPDATE nonexistent_table SET x = 1")
    
    def test_execute_script(self):
        """Test executing a SQL script."""
        # Execute a script to create a new table and insert data
        self.connection_manager.execute_script('''
            CREATE TABLE IF NOT EXISTS another_table (
                id INTEGER PRIMARY KEY,
                description TEXT
            );
            
            INSERT INTO another_table (description) VALUES ('test1');
            INSERT INTO another_table (description) VALUES ('test2');
        ''')
        
        # Verify the table was created and data inserted
        rows = self.connection_manager.execute_query("SELECT * FROM another_table ORDER BY id")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['description'], 'test1')
        self.assertEqual(rows[1]['description'], 'test2')
    
    def test_execute_script_error(self):
        """Test error handling in execute_script."""
        # Test with invalid SQL
        with self.assertRaises(RepositoryError):
            self.connection_manager.execute_script("CREATE TABLE test (invalid syntax);")
    
    def test_table_exists(self):
        """Test checking if a table exists."""
        # Test with existing table
        self.assertTrue(self.connection_manager.table_exists("test_table"))
        
        # Test with non-existent table
        self.assertFalse(self.connection_manager.table_exists("nonexistent_table"))
    
    def test_transaction_management(self):
        """Test transaction management (begin, commit, rollback)."""
        # Begin a transaction
        self.connection_manager.begin_transaction()
        
        # Insert data
        self.connection_manager.execute_update(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("transaction_test", 100)
        )
        
        # Check data is there
        rows = self.connection_manager.execute_query(
            "SELECT * FROM test_table WHERE name = ?",
            ("transaction_test",)
        )
        self.assertEqual(len(rows), 1)
        
        # Rollback the transaction
        self.connection_manager.rollback_transaction()
        
        # Verify data is gone
        rows = self.connection_manager.execute_query(
            "SELECT * FROM test_table WHERE name = ?",
            ("transaction_test",)
        )
        self.assertEqual(len(rows), 0)
        
        # Begin a new transaction
        self.connection_manager.begin_transaction()
        
        # Insert data again
        self.connection_manager.execute_update(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ("transaction_test", 200)
        )
        
        # Commit the transaction
        self.connection_manager.commit_transaction()
        
        # Verify data persists
        rows = self.connection_manager.execute_query(
            "SELECT * FROM test_table WHERE name = ?",
            ("transaction_test",)
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['value'], 200)
    
    def test_transaction_error_handling(self):
        """Test error handling in transaction methods."""
        # Test begin transaction error
        with patch.object(self.connection_manager, 'get_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_conn.execute.side_effect = sqlite3.Error("Test error")
            mock_get_conn.return_value = mock_conn
            
            with self.assertRaises(RepositoryError):
                self.connection_manager.begin_transaction()
        
        # Test commit transaction error
        with patch.object(self.connection_manager, 'get_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_conn.commit.side_effect = sqlite3.Error("Test error")
            mock_get_conn.return_value = mock_conn
            
            with self.assertRaises(RepositoryError):
                self.connection_manager.commit_transaction()
        
        # Test rollback transaction error (should not raise)
        with patch.object(self.connection_manager, 'get_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_conn.rollback.side_effect = sqlite3.Error("Test error")
            mock_get_conn.return_value = mock_conn
            
            # Should not raise an exception
            self.connection_manager.rollback_transaction()
    
    def test_connection_pooling(self):
        """Test that connections are pooled per thread."""
        # Initialize connection manager with a real database file
        manager = ConnectionManager(self.db_path)
        
        # Store connections from different threads
        connections = {}
        threads_done = threading.Event()
        thread_count = 3
        threads_completed = 0
        
        def get_connection_in_thread():
            nonlocal threads_completed
            # Get a connection in this thread
            thread_name = threading.current_thread().name
            connections[thread_name] = manager.get_connection()
            
            # Signal completion
            threads_completed += 1
            if threads_completed == thread_count:
                threads_done.set()
        
        # Create and start threads
        threads = []
        for i in range(thread_count):
            thread = threading.Thread(target=get_connection_in_thread, name=f"TestThread-{i}")
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        threads_done.wait(timeout=5.0)
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        # Check that each thread got a different connection
        connection_ids = [id(conn) for conn in connections.values()]
        self.assertEqual(len(set(connection_ids)), thread_count)

if __name__ == '__main__':
    unittest.main()