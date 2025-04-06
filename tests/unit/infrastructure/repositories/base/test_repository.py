"""Tests for the Repository base class."""
import unittest
from unittest.mock import MagicMock
from typing import Dict, Any, Optional, List

from src.infrastructure.repositories.base.repository import Repository
from src.core.exceptions import RepositoryError

class ConcreteRepository(Repository[Dict[str, Any]]):
    """Concrete implementation of Repository for testing."""

    def save(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """Save an entity to the repository."""
        pass

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity from the repository."""
        pass

    def delete(self, entity_id: str) -> None:
        """Delete an entity from the repository."""
        pass

    def list(self) -> List[str]:
        """List all entity IDs in the repository."""
        pass

class TestRepository(unittest.TestCase):
    """Test cases for the Repository base class."""

    def test_initialization(self):
        """Test that the repository initializes correctly."""
        repo = ConcreteRepository("test_logger")
        self.assertEqual(repo.logger.name, "test_logger")

    def test_abstract_methods(self):
        """Test that abstract methods are defined."""
        # This test verifies that the abstract methods are defined in the base class
        # We can't instantiate Repository directly because it's abstract
        self.assertTrue(hasattr(Repository, "save"))
        self.assertTrue(hasattr(Repository, "get"))
        self.assertTrue(hasattr(Repository, "delete"))
        self.assertTrue(hasattr(Repository, "list"))

        # Verify that the methods are abstract
        self.assertTrue(getattr(Repository.save, "__isabstractmethod__", False))
        self.assertTrue(getattr(Repository.get, "__isabstractmethod__", False))
        self.assertTrue(getattr(Repository.delete, "__isabstractmethod__", False))
        self.assertTrue(getattr(Repository.list, "__isabstractmethod__", False))

    def test_validate_entity_id_valid(self):
        """Test that validate_entity_id accepts valid IDs."""
        repo = ConcreteRepository("test_logger")

        # These should not raise exceptions
        repo._validate_entity_id("valid_id")
        repo._validate_entity_id("valid-id")
        repo._validate_entity_id("valid_id_123")

    def test_validate_entity_id_invalid(self):
        """Test that validate_entity_id rejects invalid IDs."""
        repo = ConcreteRepository("test_logger")

        # These should raise exceptions
        invalid_ids = [
            "",  # Empty string
            "invalid id",  # Contains spaces
            "invalid/id",  # Contains slashes
            "invalid\\id",  # Contains backslashes
            "invalid:id",  # Contains colons
            None,  # None
        ]

        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(RepositoryError):
                    repo._validate_entity_id(invalid_id)

    def test_log_operation(self):
        """Test that log_operation logs operations correctly."""
        repo = ConcreteRepository("test_logger")

        # Mock the logger
        repo.logger = MagicMock()

        # Call log_operation
        repo._log_operation("test_operation", "test_entity_id")

        # Verify that the logger was called
        repo.logger.debug.assert_called_once_with("test_operation: test_entity_id")

if __name__ == "__main__":
    unittest.main()
