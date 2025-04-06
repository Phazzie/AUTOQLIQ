"""Database connection management for infrastructure layer."""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional, Tuple

# Assuming AutoQliqError is defined in core exceptions
from src.core.exceptions import AutoQliqError, RepositoryError

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages SQLite database connections and transactions.

    Provides a consistent way to obtain connections and execute queries,
    including context management for transactions.

    Attributes:
        db_path (str): The file path to the SQLite database.
    """

    def __init__(self, db_path: str):
        """
        Initialize a new ConnectionManager.

        Args:
            db_path (str): Path to the SQLite database file.

        Raises:
            ValueError: If db_path is empty.
        """
        if not db_path:
            raise ValueError("Database path cannot be empty.")
        self.db_path = db_path
        logger.info(f"ConnectionManager initialized for database: {db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Establish and return a new database connection.

        Configures the connection to use `sqlite3.Row` for row factory,
        allowing dictionary-like access to columns. Enables foreign key constraints.

        Returns:
            sqlite3.Connection: An active database connection.

        Raises:
            RepositoryError: If the connection cannot be established.
        """
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False) # Allow multi-thread access if needed
            conn.row_factory = sqlite3.Row # Access rows like dictionaries
            conn.execute("PRAGMA foreign_keys = ON;") # Enable foreign key support
            logger.debug(f"Database connection established: {self.db_path}")
            return conn
        except sqlite3.Error as e:
            error_msg = f"Failed to connect to database: {self.db_path}"
            logger.error(error_msg, exc_info=True)
            # Raise a more specific infrastructure/repository error
            raise RepositoryError(error_msg, cause=e) from e

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Provide a transactional context using a database connection.

        Ensures that the transaction is committed upon successful exit of the
        context block, or rolled back if an exception occurs within the block.
        The connection is automatically closed afterwards.

        Yields:
            sqlite3.Connection: A database connection with an active transaction.

        Raises:
            RepositoryError: If the transaction cannot be started or managed.
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = self.get_connection()
            logger.debug("Starting database transaction.")
            # Begin transaction implicitly (or explicitly if needed: conn.execute("BEGIN"))
            yield conn
            conn.commit()
            logger.debug("Database transaction committed.")
        except Exception as e:
            logger.error("Database transaction failed. Rolling back.", exc_info=True)
            if conn:
                try:
                    conn.rollback()
                    logger.debug("Database transaction rolled back.")
                except sqlite3.Error as rb_e:
                    logger.error(f"Failed to rollback transaction: {rb_e}", exc_info=True)
            # Re-raise the original exception, wrapping if necessary
            if not isinstance(e, AutoQliqError):
                 # Wrap non-AutoQliq errors
                 raise RepositoryError("Database transaction failed", cause=e) from e
            raise # Re-raise AutoQliqError directly
        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Database connection closed after transaction.")
                except sqlite3.Error as close_e:
                     logger.error(f"Error closing database connection: {close_e}", exc_info=True)

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query within its own transaction.

        Suitable for single SELECT queries. For INSERT/UPDATE/DELETE, it's generally
        better to use the `transaction` context manager explicitly to control commit/rollback.
        This method *will* commit changes for non-SELECT queries.

        Args:
            query (str): The SQL query string (can contain placeholders like ?).
            params (Tuple): A tuple of parameters to bind to the query placeholders.

        Returns:
            List[Dict[str, Any]]: The query results as a list of dictionaries
                                  (empty list for non-SELECT queries or if no rows found).

        Raises:
            RepositoryError: If the query execution fails.
        """
        logger.debug(f"Executing query: {query} with params: {params}")
        try:
            # Use the transaction context manager for automatic commit/rollback/close
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                # Fetch results only if it's likely a SELECT query
                # Check first word case-insensitively
                if query.strip().upper().startswith("SELECT"):
                    results = [dict(row) for row in cursor.fetchall()]
                    logger.debug(f"Query returned {len(results)} rows.")
                    return results
                else:
                    # For INSERT/UPDATE/DELETE, report rows affected but return empty list
                    affected = cursor.rowcount
                    logger.debug(f"Query affected {affected} rows.")
                    return [] # Return empty list for non-select queries
        except sqlite3.Error as e:
            # Specific database errors
            error_msg = f"Database error executing query: {query}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e
        except RepositoryError:
             # Re-raise errors from the transaction context manager
             raise
        except Exception as e:
            # Catch any other unexpected error
            error_msg = f"Unexpected error executing query: {query}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e

    def execute_modification(self, query: str, params: Tuple = ()) -> int:
        """
        Execute a modification query (INSERT, UPDATE, DELETE) and return affected rows.

        Uses a transaction internally.

        Args:
            query: The SQL query string.
            params: Parameters for the query.

        Returns:
            The number of rows affected.

        Raises:
            RepositoryError: If execution fails.
        """
        logger.debug(f"Executing modification: {query} with params: {params}")
        try:
            with self.transaction() as conn:
                 cursor = conn.cursor()
                 cursor.execute(query, params)
                 affected_rows = cursor.rowcount
                 logger.debug(f"Modification affected {affected_rows} rows.")
                 return affected_rows
        except sqlite3.Error as e:
            error_msg = f"Database error executing modification: {query}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e
        except RepositoryError:
            raise # Errors from transaction context
        except Exception as e:
            error_msg = f"Unexpected error executing modification: {query}"
            logger.error(error_msg, exc_info=True)
            raise RepositoryError(error_msg, cause=e) from e


    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.

        Raises:
            RepositoryError: If the check fails.
        """
        if not table_name or not isinstance(table_name, str):
            logger.warning("Invalid table name provided for existence check.")
            return False
        logger.debug(f"Checking existence of table: {table_name}")
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        try:
            # Use execute_query as it's just a SELECT
            rows = self.execute_query(query, (table_name,))
            exists = len(rows) > 0
            logger.debug(f"Table '{table_name}' exists: {exists}")
            return exists
        except RepositoryError as e:
            # Let execute_query handle logging, just re-raise with context
            raise RepositoryError(f"Failed to check existence of table '{table_name}'", cause=e.cause) from e

    def create_table(self, table_name: str, columns_sql: str) -> None:
        """
        Create a table if it doesn't already exist.

        Args:
            table_name (str): The name of the table to create.
            columns_sql (str): The SQL fragment defining the columns (e.g., "id INTEGER PRIMARY KEY, name TEXT").

        Raises:
            RepositoryError: If the table cannot be created or verified.
            ValueError: If table_name or columns_sql is invalid.
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")
        if not columns_sql or not isinstance(columns_sql, str):
            raise ValueError("Column definition SQL must be a non-empty string.")

        logger.info(f"Attempting to create table if not exists: {table_name}")
        # Use execute_modification as CREATE TABLE is a DDL statement
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        try:
            self.execute_modification(query) # Use modification method
            # Verify that the table was created
            if not self.table_exists(table_name):
                # This case should be rare if execute_modification didn't raise an error
                error_msg = f"Table '{table_name}' was not created despite successful query execution."
                logger.error(error_msg)
                raise RepositoryError(error_msg)
            logger.info(f"Table '{table_name}' created or already exists.")
        except RepositoryError as e:
             # Let execute_modification or table_exists handle logging, just re-raise with context
             raise RepositoryError(f"Failed to create table '{table_name}'", cause=e.cause) from e