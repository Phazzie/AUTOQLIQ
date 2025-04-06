"""Logger factory for infrastructure layer."""
import logging
from typing import Dict, Any


class LoggerFactory:
    """Factory for creating loggers."""

    @staticmethod
    def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
        """Create a logger.
        
        Args:
            name: The name of the logger
            level: The logging level
            
        Returns:
            A configured logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        return logger
    
    @staticmethod
    def create_repository_logger(repository_name: str) -> logging.Logger:
        """Create a logger for a repository.
        
        Args:
            repository_name: The name of the repository
            
        Returns:
            A configured logger
        """
        logger = LoggerFactory.create_logger(f"repository.{repository_name}")
        return logger
    
    @staticmethod
    def log_repository_operation(logger: logging.Logger, operation: str, entity_id: str) -> None:
        """Log a repository operation.
        
        Args:
            logger: The logger to use
            operation: The operation being performed
            entity_id: The ID of the entity
        """
        logger.debug(f"{operation}: {entity_id}")
