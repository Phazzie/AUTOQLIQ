"""File locking utilities for AutoQliq."""

import os
import time
import logging
import threading
from typing import Optional, Dict, Any, Callable, TypeVar, Generic
from contextlib import contextmanager

# For type hints
T = TypeVar('T')

logger = logging.getLogger(__name__)

# Global lock registry to prevent deadlocks between threads
_file_locks: Dict[str, threading.RLock] = {}
_registry_lock = threading.RLock()


@contextmanager
def file_lock(file_path: str, timeout: float = 10.0):
    """
    Context manager for thread-safe file access.
    
    Args:
        file_path: Path to the file to lock
        timeout: Maximum time to wait for the lock in seconds
        
    Raises:
        TimeoutError: If the lock cannot be acquired within the timeout
        
    Yields:
        None
    """
    # Get absolute path to ensure consistent keys in the registry
    abs_path = os.path.abspath(file_path)
    
    # Get or create a lock for this file
    with _registry_lock:
        if abs_path not in _file_locks:
            _file_locks[abs_path] = threading.RLock()
        lock = _file_locks[abs_path]
    
    # Try to acquire the lock with timeout
    start_time = time.time()
    acquired = False
    
    try:
        while not acquired and (time.time() - start_time) < timeout:
            acquired = lock.acquire(blocking=False)
            if acquired:
                logger.debug(f"Acquired lock for file: {file_path}")
                break
            time.sleep(0.01)  # Small sleep to prevent CPU spinning
        
        if not acquired:
            logger.error(f"Timeout acquiring lock for file: {file_path}")
            raise TimeoutError(f"Could not acquire lock for file: {file_path} within {timeout} seconds")
        
        # Yield control back to the caller
        yield
    finally:
        # Release the lock if we acquired it
        if acquired:
            lock.release()
            logger.debug(f"Released lock for file: {file_path}")
            
            # Clean up the registry if no one is using this lock anymore
            with _registry_lock:
                if abs_path in _file_locks and not _file_locks[abs_path]._is_owned():
                    # Only remove if no one else is waiting for this lock
                    if _file_locks[abs_path]._RLock__count == 0:
                        del _file_locks[abs_path]
                        logger.debug(f"Removed lock from registry for file: {file_path}")


class LockedFile(Generic[T]):
    """
    A wrapper class that provides thread-safe access to a file.
    
    This class ensures that file operations are performed atomically
    by using a lock to prevent concurrent access.
    """
    
    def __init__(self, file_path: str, read_func: Callable[[str], T], write_func: Callable[[str, T], None]):
        """
        Initialize a new LockedFile.
        
        Args:
            file_path: Path to the file
            read_func: Function to read the file content
            write_func: Function to write content to the file
        """
        self.file_path = file_path
        self._read_func = read_func
        self._write_func = write_func
    
    def read(self, default: Optional[T] = None) -> T:
        """
        Read the file content in a thread-safe manner.
        
        Args:
            default: Default value to return if the file doesn't exist
            
        Returns:
            The file content
            
        Raises:
            Exception: If the file cannot be read
        """
        with file_lock(self.file_path):
            if not os.path.exists(self.file_path):
                if default is not None:
                    return default
                raise FileNotFoundError(f"File not found: {self.file_path}")
            return self._read_func(self.file_path)
    
    def write(self, content: T) -> None:
        """
        Write content to the file in a thread-safe manner.
        
        Args:
            content: Content to write to the file
            
        Raises:
            Exception: If the file cannot be written
        """
        with file_lock(self.file_path):
            # Ensure the directory exists
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write the content
            self._write_func(self.file_path, content)
    
    def update(self, update_func: Callable[[T], T], default: Optional[T] = None) -> T:
        """
        Update the file content in a thread-safe manner.
        
        Args:
            update_func: Function to update the content
            default: Default value to use if the file doesn't exist
            
        Returns:
            The updated content
            
        Raises:
            Exception: If the file cannot be read or written
        """
        with file_lock(self.file_path):
            # Read the current content
            try:
                current = self._read_func(self.file_path)
            except FileNotFoundError:
                if default is not None:
                    current = default
                else:
                    raise
            
            # Update the content
            updated = update_func(current)
            
            # Write the updated content
            self._write_func(self.file_path, updated)
            
            return updated
