"""Tests for the file system repository base class."""
import unittest
import os
import json
from unittest.mock import patch, mock_open, MagicMock

from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.core.exceptions import AutoQliqError

class TestFileSystemRepository(unittest.TestCase):
    """Test cases for the FileSystemRepository class."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo = FileSystemRepository("test_logger")

    def test_ensure_directory_exists_already_exists(self):
        """Test that _ensure_directory_exists does nothing if the directory already exists."""
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs") as mock_makedirs:
                self.repo._ensure_directory_exists("test_dir")
                mock_makedirs.assert_not_called()

    def test_ensure_directory_exists_create_success(self):
        """Test that _ensure_directory_exists creates the directory if it doesn't exist."""
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs") as mock_makedirs:
                self.repo._ensure_directory_exists("test_dir")
                mock_makedirs.assert_called_once_with("test_dir", exist_ok=True)

    def test_ensure_directory_exists_create_error(self):
        """Test that _ensure_directory_exists raises AutoQliqError if the directory cannot be created."""
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
                with self.assertRaises(AutoQliqError):
                    self.repo._ensure_directory_exists("test_dir")

    def test_file_exists(self):
        """Test that _file_exists returns True if the file exists."""
        with patch("os.path.exists", return_value=True):
            self.assertTrue(self.repo._file_exists("test_file"))

    def test_file_not_exists(self):
        """Test that _file_exists returns False if the file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            self.assertFalse(self.repo._file_exists("test_file"))

    def test_read_json_file_success(self):
        """Test that _read_json_file reads and parses a JSON file."""
        test_data = {"key": "value"}
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            result = self.repo._read_json_file("test_file")
            self.assertEqual(result, test_data)

    def test_read_json_file_not_found(self):
        """Test that _read_json_file raises FileNotFoundError if the file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                self.repo._read_json_file("test_file")

    def test_read_json_file_invalid_json(self):
        """Test that _read_json_file raises JSONDecodeError if the file contains invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with self.assertRaises(json.JSONDecodeError):
                self.repo._read_json_file("test_file")

    def test_write_json_file_success(self):
        """Test that _write_json_file writes data to a JSON file."""
        test_data = {"key": "value"}
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            self.repo._write_json_file("test_file", test_data)
            mock_file.assert_called_once_with("test_file", "w")
            # We can't easily check the exact write calls because json.dump breaks it into multiple writes

    def test_write_json_file_permission_error(self):
        """Test that _write_json_file raises IOError if the file cannot be written."""
        test_data = {"key": "value"}
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(IOError):
                self.repo._write_json_file("test_file", test_data)

    def test_write_json_file_json_error(self):
        """Test that _write_json_file raises TypeError if the data cannot be serialized to JSON."""
        test_data = {"key": object()}  # object() is not JSON serializable
        with patch("builtins.open", mock_open()):
            with self.assertRaises(TypeError):
                self.repo._write_json_file("test_file", test_data)

if __name__ == "__main__":
    unittest.main()
