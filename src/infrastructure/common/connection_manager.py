"""Database connection management for AutoQliq."""

import logging
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Union
import os
import threading

from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages database connections for repositories.
    
    Provides thread-safe access to SQLite database connections,
    with connection pooling and transaction management.
    
    Attributes:
        db_path (str): Path to the SQLite database file.
        _local (threading.local): Thread-local storage for connections.
        _lock (threading.Lock): Lock for thread safety.
    """
    
    def __init__(self, db_path: str):
        """Initialize the ConnectionManager.
        
        Args:
            db_path: Path to the SQLite database file.
            
        Raises:
            RepositoryError: If the database path is invalid or inaccessible.
        """
        if not db_path:
            raise ValueError("Database path cannot be empty")
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created directory for database: {db_dir}")
            except OSError as e:
                raise RepositoryError(f"Failed to create database directory: {e}", cause=e)
        
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        
        logger.info(f"ConnectionManager initialized with database: {db_path}")
        
        # Test connection
        try:
            with self.get_connection():
                pass
            logger.debug("Database connection test successful")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise RepositoryError(f"Failed to connect to database: {e}", cause=e)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection for the current thread.
        
        Returns:
            An SQLite connection object.
            
        Raises:
            RepositoryError: If connection fails.
        """
        # Check if connection exists for this thread
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            try:
                # Create new connection for this thread
                self._local.connection = sqlite3.connect(
                    self.db_path,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                )
                # Configure connection
                self._local.connection.row_factory = sqlite3.Row
                # Enable foreign keys
                self._local.connection.execute("PRAGMA foreign_keys = ON")
                logger.debug(f"Created new database connection for thread {threading.current_thread().name}")
            except sqlite3.Error as e:
                logger.error(f"Failed to connect to database: {e}")
                raise RepositoryError(f"Failed to connect to database: {e}", cause=e)
        
        return self._local.connection
    
    def close_connection(self) -> None:
        """Close the connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            try:
                self._local.connection.close()
                logger.debug(f"Closed database connection for thread {threading.current_thread().name}")
            except sqlite3.Error as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                self._local.connection = None
    
    def execute_query(self, query: str, params: Union[Tuple, Dict[str, Any], None] = None) -> List[sqlite3.Row]:
        """Execute a SELECT query and return the results.
        
        Args:
            query: SQL query string.
            params: Query parameters (tuple, dict, or None).
            
        Returns:
            List of sqlite3.Row objects.
            
        Raises:
            RepositoryError: If query execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {params}")
            raise RepositoryError(f"Query execution failed: {e}", cause=e)
    
    def execute_update(self, query: str, params: Union[Tuple, Dict[str, Any], None] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string.
            params: Query parameters (tuple, dict, or None).
            
        Returns:
            Number of rows affected.
            
        Raises:
            RepositoryError: If query execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            
            connection.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            connection.rollback()
            logger.error(f"Update execution failed: {e}\nQuery: {query}\nParams: {params}")
            raise RepositoryError(f"Update execution failed: {e}", cause=e)
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script.
        
        Args:
            script: SQL script string.
            
        Raises:
            RepositoryError: If script execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.executescript(script)
            connection.commit()
        except sqlite3.Error as e:
            connection.rollback()
            logger.error(f"Script execution failed: {e}\nScript: {script[:100]}...")
            raise RepositoryError(f"Script execution failed: {e}", cause=e)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check.
            
        Returns:
            True if the table exists, False otherwise.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        rows = self.execute_query(query, (table_name,))
        return len(rows) > 0
    
    def begin_transaction(self) -> None:
        """Begin a transaction."""
        connection = self.get_connection()
        try:
            connection.execute("BEGIN TRANSACTION")
            logger.debug("Transaction started")
        except sqlite3.Error as e:
            logger.error(f"Failed to begin transaction: {e}")
            raise RepositoryError(f"Failed to begin transaction: {e}", cause=e)
    
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        connection = self.get_connection()
        try:
            connection.commit()
            logger.debug("Transaction committed")
        except sqlite3.Error as e:
            logger.error(f"Failed to commit transaction: {e}")
            raise RepositoryError(f"Failed to commit transaction: {e}", cause=e)
    
    def rollback_transaction(self) -> None:
        """Roll back the current transaction."""
        connection = self.get_connection()
        try:
            connection.rollback()
            logger.debug("Transaction rolled back")
        except sqlite3.Error as e:
            logger.error(f"Failed to rollback transaction: {e}")
            # Don't raise here, as this is typically called in exception handlers
    
    def __del__(self) -> None:
        """Close connections when the manager is garbage collected."""
        self.close_connection()
