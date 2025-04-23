"""Reporting repository interface for AutoQliq.

This module defines the reporting repository interface that all reporting
repository implementations must adhere to. It extends the base repository
interface with reporting-specific operations.

IMPORTANT: This is the new consolidated repository interface. Use this
instead of the deprecated interfaces in repository.py and repository_interfaces.py.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from src.core.interfaces.repository.base import IBaseRepository

class IReportingRepository(IBaseRepository[Dict[str, Any]]):
    """Interface for reporting repository implementations.
    
    This interface extends the base repository interface with reporting-specific
    operations. It provides methods for storing and retrieving execution logs
    and results.
    
    All reporting repository implementations should inherit from this interface
    to ensure a consistent API across the application.
    """
    
    @abstractmethod
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """Save an execution log to the repository.
        
        Args:
            execution_log: Dictionary containing execution log data
                Must include an 'id' key with a unique identifier
            
        Raises:
            ValidationError: If the execution log is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get_execution_log(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get an execution log from the repository by ID.
        
        Args:
            execution_id: Unique identifier for the execution log
            
        Returns:
            The execution log if found, None otherwise
            
        Raises:
            ValidationError: If the execution ID is invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def list_execution_summaries(
        self, 
        workflow_name: Optional[str] = None, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List execution summaries with basic information.
        
        Args:
            workflow_name: Optional filter by workflow name
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of dictionaries containing execution summary data
            
        Raises:
            ValidationError: If any parameters are invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def get_execution_stats(
        self, 
        workflow_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get execution statistics.
        
        Args:
            workflow_name: Optional filter by workflow name
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            Dictionary containing execution statistics
            
        Raises:
            ValidationError: If any parameters are invalid
            RepositoryError: If the operation fails
        """
        pass
    
    @abstractmethod
    def delete_old_logs(self, days_to_keep: int = 30) -> int:
        """Delete execution logs older than the specified number of days.
        
        Args:
            days_to_keep: Number of days of logs to keep
            
        Returns:
            Number of logs deleted
            
        Raises:
            ValidationError: If days_to_keep is invalid
            RepositoryError: If the operation fails
        """
        pass
