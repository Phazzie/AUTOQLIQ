"""Tests for the BaseRepository class."""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.base_repository import BaseRepository
from src.core.exceptions import AutoQliqError

class TestBaseRepository(unittest.TestCase):
    """Test cases for the BaseRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = BaseRepository("test_logger")

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_ensure_directory_exists_creates_directory(self):
        """Test that _ensure_directory_exists creates a directory if it doesn't exist."""
        test_dir = os.path.join(self.temp_dir.name, "test_dir")
        self.assertFalse(os.path.exists(test_dir))
        
        self.repo._ensure_directory_exists(test_dir)
        self.assertTrue(os.path.exists(test_dir))

    def test_ensure_directory_exists_no_error_if_exists(self):
        """Test that _ensure_directory_exists doesn't raise an error if the directory exists."""
        test_dir = os.path.join(self.temp_dir.name, "test_dir")
        os.makedirs(test_dir)
        
        # This should not raise an error
        self.repo._ensure_directory_exists(test_dir)

    @patch("os.makedirs")
    def test_ensure_directory_exists_raises_error(self, mock_makedirs):
        """Test that _ensure_directory_exists raises an error if the directory cannot be created."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        with self.assertRaises(AutoQliqError):
            self.repo._ensure_directory_exists("/nonexistent/dir")

    def test_read_json_file(self):
        """Test that _read_json_file reads and parses a JSON file."""
        test_file = os.path.join(self.temp_dir.name, "test.json")
        test_data = {"key": "value"}
        
        with open(test_file, "w") as f:
            json.dump(test_data, f)
        
        result = self.repo._read_json_file(test_file)
        self.assertEqual(result, test_data)

    def test_read_json_file_not_found(self):
        """Test that _read_json_file raises FileNotFoundError if the file doesn't exist."""
        test_file = os.path.join(self.temp_dir.name, "nonexistent.json")
        
        with self.assertRaises(FileNotFoundError):
            self.repo._read_json_file(test_file)

    def test_read_json_file_invalid_json(self):
        """Test that _read_json_file raises JSONDecodeError if the file contains invalid JSON."""
        test_file = os.path.join(self.temp_dir.name, "invalid.json")
        
        with open(test_file, "w") as f:
            f.write("invalid json")
        
        with self.assertRaises(json.JSONDecodeError):
            self.repo._read_json_file(test_file)

    def test_write_json_file(self):
        """Test that _write_json_file writes data to a JSON file."""
        test_file = os.path.join(self.temp_dir.name, "test.json")
        test_data = {"key": "value"}
        
        self.repo._write_json_file(test_file, test_data)
        
        with open(test_file, "r") as f:
            result = json.load(f)
        
        self.assertEqual(result, test_data)

    def test_file_exists(self):
        """Test that _file_exists returns True if the file exists."""
        test_file = os.path.join(self.temp_dir.name, "test.txt")
        
        with open(test_file, "w") as f:
            f.write("test")
        
        self.assertTrue(self.repo._file_exists(test_file))

    def test_file_exists_returns_false(self):
        """Test that _file_exists returns False if the file doesn't exist."""
        test_file = os.path.join(self.temp_dir.name, "nonexistent.txt")
        
        self.assertFalse(self.repo._file_exists(test_file))

if __name__ == "__main__":
    unittest.main()
