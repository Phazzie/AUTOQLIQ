"""Tests for the enhanced FileSystemRepository base class."""
import unittest
import os
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from typing import Dict, Any, Optional, List

from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.core.exceptions import AutoQliqError, RepositoryError

class ConcreteFileSystemRepository(FileSystemRepository[Dict[str, Any]]):
    """Concrete implementation of FileSystemRepository for testing."""
    
    def __init__(self, directory_path: str):
        """Initialize a new ConcreteFileSystemRepository."""
        super().__init__("test_logger")
        self.directory_path = directory_path
        self._ensure_directory_exists(directory_path)
    
    def _get_entity_path(self, entity_id: str) -> str:
        """Get the path to an entity file."""
        return os.path.join(self.directory_path, f"{entity_id}.json")
    
    def _save_entity(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """Save an entity to a file."""
        file_path = self._get_entity_path(entity_id)
        self._write_json_file(file_path, entity)
    
    def _get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity from a file."""
        file_path = self._get_entity_path(entity_id)
        if not self._file_exists(file_path):
            return None
        return self._read_json_file(file_path)
    
    def _delete_entity(self, entity_id: str) -> None:
        """Delete an entity file."""
        file_path = self._get_entity_path(entity_id)
        if self._file_exists(file_path):
            os.remove(file_path)
    
    def _list_entities(self) -> List[str]:
        """List all entity IDs in the directory."""
        entities = []
        for file_name in os.listdir(self.directory_path):
            if file_name.endswith(".json"):
                entities.append(file_name[:-5])  # Remove .json extension
        return entities

class TestFileSystemRepositoryEnhanced(unittest.TestCase):
    """Test cases for the enhanced FileSystemRepository class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = ConcreteFileSystemRepository(self.temp_dir.name)
        
        # Sample entity for testing
        self.sample_entity = {"name": "test", "value": 123}
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_save(self):
        """Test that save saves an entity to a file."""
        # Save an entity
        self.repo.save("test", self.sample_entity)
        
        # Check that the file exists
        file_path = os.path.join(self.temp_dir.name, "test.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check that the file contains the correct data
        with open(file_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data, self.sample_entity)
    
    def test_save_invalid_id(self):
        """Test that save raises RepositoryError for invalid entity IDs."""
        # Try to save an entity with an invalid ID
        with self.assertRaises(RepositoryError):
            self.repo.save("invalid/id", self.sample_entity)
    
    def test_get(self):
        """Test that get retrieves an entity from a file."""
        # Save an entity
        file_path = os.path.join(self.temp_dir.name, "test.json")
        with open(file_path, "w") as f:
            json.dump(self.sample_entity, f)
        
        # Get the entity
        entity = self.repo.get("test")
        
        # Check that the entity is correct
        self.assertEqual(entity, self.sample_entity)
    
    def test_get_not_found(self):
        """Test that get returns None if the entity is not found."""
        # Get a nonexistent entity
        entity = self.repo.get("nonexistent")
        
        # Check that the entity is None
        self.assertIsNone(entity)
    
    def test_get_invalid_id(self):
        """Test that get raises RepositoryError for invalid entity IDs."""
        # Try to get an entity with an invalid ID
        with self.assertRaises(RepositoryError):
            self.repo.get("invalid/id")
    
    def test_delete(self):
        """Test that delete removes an entity file."""
        # Save an entity
        file_path = os.path.join(self.temp_dir.name, "test.json")
        with open(file_path, "w") as f:
            json.dump(self.sample_entity, f)
        
        # Delete the entity
        self.repo.delete("test")
        
        # Check that the file no longer exists
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_not_found(self):
        """Test that delete does not raise an error if the entity is not found."""
        # Delete a nonexistent entity
        self.repo.delete("nonexistent")
    
    def test_delete_invalid_id(self):
        """Test that delete raises RepositoryError for invalid entity IDs."""
        # Try to delete an entity with an invalid ID
        with self.assertRaises(RepositoryError):
            self.repo.delete("invalid/id")
    
    def test_list(self):
        """Test that list returns all entity IDs in the directory."""
        # Save some entities
        for i in range(3):
            file_path = os.path.join(self.temp_dir.name, f"test{i}.json")
            with open(file_path, "w") as f:
                json.dump(self.sample_entity, f)
        
        # List the entities
        entities = self.repo.list()
        
        # Check that the list contains the correct entity IDs
        self.assertEqual(set(entities), {"test0", "test1", "test2"})
    
    def test_list_empty(self):
        """Test that list returns an empty list if the directory is empty."""
        # List entities in an empty directory
        entities = self.repo.list()
        
        # Check that the list is empty
        self.assertEqual(entities, [])

if __name__ == "__main__":
    unittest.main()
