"""Unit tests for FileSystemWorkflowRepository template methods."""

import unittest
import os
import json
import shutil
from unittest.mock import patch, mock_open, MagicMock, call

# Assuming correct paths for imports
from src.infrastructure.repositories.workflow_repository import FileSystemWorkflowRepository
from src.core.exceptions import RepositoryError, ValidationError, SerializationError

class TestFileSystemTemplatePersistence(unittest.TestCase):
    """Tests for FileSystemWorkflowRepository template persistence methods."""

    BASE_DIR = "_test_fs_repo_template_persistence"
    WF_DIR = os.path.join(BASE_DIR, "workflows_main")
    TMPL_DIR = os.path.join(WF_DIR, "templates") # Template subdir

    def setUp(self):
        """Create test directories."""
        if os.path.exists(self.BASE_DIR): shutil.rmtree(self.BASE_DIR)
        os.makedirs(self.WF_DIR, exist_ok=True)
        # Instantiate repo, allow it to create template dir
        self.repo = FileSystemWorkflowRepository(self.WF_DIR, create_if_missing=True)
        self.assertTrue(os.path.isdir(self.TMPL_DIR))

    def tearDown(self):
        """Remove test directory and its contents."""
        if os.path.exists(self.BASE_DIR): shutil.rmtree(self.BASE_DIR)

    # --- save_template ---
    def test_save_template_success(self):
        """Test saving a valid template creates the correct JSON file."""
        name="tmpl1"; data=[{"type":"A"}]; path=os.path.join(self.TMPL_DIR, f"{name}.json")
        self.repo.save_template(name, data)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f: saved = json.load(f); self.assertEqual(saved, data)

    def test_save_template_overwrite(self):
        """Test saving overwrites an existing template file."""
        name="ovr"; d1=[{"t":1}]; d2=[{"t":2}]; path=os.path.join(self.TMPL_DIR, f"{name}.json")
        self.repo.save_template(name, d1); self.repo.save_template(name, d2)
        with open(path, 'r') as f: saved = json.load(f); self.assertEqual(saved, d2)

    def test_save_template_invalid_name(self):
        with self.assertRaises(ValidationError): self.repo.save_template("inv name", [])
        with self.assertRaises(ValidationError): self.repo.save_template("", [])

    def test_save_template_invalid_data_type(self):
         with self.assertRaises(SerializationError): self.repo.save_template("bad1", "s") # type: ignore
         with self.assertRaises(SerializationError): self.repo.save_template("bad2", [{}, "s"]) # type: ignore

    @patch('src.infrastructure.repositories.base.file_system_repository.FileSystemRepository._write_json_file', side_effect=IOError("Disk full"))
    def test_save_template_io_error(self, mock_write):
         with self.assertRaisesRegex(RepositoryError, "Failed save template.*Disk full"):
              self.repo.save_template("io_fail", [{"type":"OK"}])

    # --- load_template ---
    def test_load_template_success(self):
        name="load"; data=[{"type":"T"}]; path=os.path.join(self.TMPL_DIR, f"{name}.json")
        with open(path, 'w') as f: json.dump(data, f)
        loaded = self.repo.load_template(name); self.assertEqual(loaded, data)

    def test_load_template_not_found(self):
        with self.assertRaisesRegex(RepositoryError, "Template file not found"): self.repo.load_template("not_found")

    def test_load_template_invalid_json(self):
        name="bad_json"; path=os.path.join(self.TMPL_DIR, f"{name}.json"); f=open(path,'w'); f.write("{bad"); f.close()
        with self.assertRaisesRegex(SerializationError, "Invalid JSON"): self.repo.load_template(name)

    def test_load_template_not_a_list(self):
         name="not_list"; path=os.path.join(self.TMPL_DIR, f"{name}.json"); f=open(path,'w'); json.dump({}, f); f.close()
         with self.assertRaisesRegex(SerializationError, "not JSON list"): self.repo.load_template(name)

    def test_load_template_contains_non_dict(self):
         name="non_dict"; path=os.path.join(self.TMPL_DIR, f"{name}.json"); f=open(path,'w'); json.dump([{},"s"], f); f.close()
         with self.assertRaisesRegex(SerializationError, "contains non-dict items"): self.repo.load_template(name)

    # --- list_templates ---
    def test_list_templates(self):
        f=open(os.path.join(self.TMPL_DIR, "b.json"),'w');f.write("[]");f.close()
        f=open(os.path.join(self.TMPL_DIR, "a.json"),'w');f.write("[]");f.close()
        f=open(os.path.join(self.TMPL_DIR, "c.txt"),'w');f.write("t");f.close()
        f=open(os.path.join(self.WF_DIR, "w.json"),'w');f.write("[]");f.close() # Should ignore
        templates = self.repo.list_templates(); self.assertEqual(templates, ["a", "b"]) # Sorted

    def test_list_templates_empty(self): self.assertEqual(self.repo.list_templates(), [])
    def test_list_templates_dir_missing(self): shutil.rmtree(self.TMPL_DIR); self.assertEqual(self.repo.list_templates(), [])

    # --- delete_template ---
    def test_delete_template_found(self):
        name="del"; path=os.path.join(self.TMPL_DIR, f"{name}.json"); f=open(path,'w');f.write("[]");f.close()
        self.assertTrue(os.path.exists(path)); result = self.repo.delete_template(name)
        self.assertTrue(result); self.assertFalse(os.path.exists(path))

    def test_delete_template_not_found(self): self.assertFalse(self.repo.delete_template("not_there"))

    @patch('os.remove', side_effect=PermissionError("Denied"))
    def test_delete_template_permission_error(self, mock_remove):
         name="perm"; path=os.path.join(self.TMPL_DIR, f"{name}.json"); f=open(path,'w');f.write("[]");f.close()
         with self.assertRaisesRegex(RepositoryError, "Failed delete template.*Denied"): self.repo.delete_template(name)
         mock_remove.assert_called_once_with(path)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)