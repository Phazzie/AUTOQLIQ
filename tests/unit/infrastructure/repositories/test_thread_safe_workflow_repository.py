"""Unit tests for the ThreadSafeWorkflowRepository."""

import unittest
import os
import json
import tempfile
import shutil
import threading
from unittest.mock import MagicMock, patch

from src.core.exceptions import WorkflowError, ValidationError, RepositoryError, SerializationError
from src.core.interfaces import IAction
from src.infrastructure.repositories.thread_safe_workflow_repository import ThreadSafeWorkflowRepository


class MockAction(IAction):
    """Mock action for testing."""
    
    def __init__(self, name, action_type="Mock", **kwargs):
        self.name = name
        self.action_type = action_type
        self.kwargs = kwargs
    
    def validate(self):
        """Validate the action."""
        return True
    
    def execute(self, driver=None, credential_repo=None, context=None):
        """Execute the action."""
        return {"success": True, "message": f"Executed {self.name}"}


class TestThreadSafeWorkflowRepository(unittest.TestCase):
    """Test cases for the ThreadSafeWorkflowRepository."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create the repository
        self.repo = ThreadSafeWorkflowRepository(
            directory_path=self.test_dir,
            create_if_missing=True
        )
        
        # Sample workflow actions
        self.sample_actions = [
            MockAction("action1", action_type="Click", selector="#button"),
            MockAction("action2", action_type="Type", selector="#input", text="Hello")
        ]
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_init_creates_directories(self):
        """Test that the repository creates directories if they don't exist."""
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "templates")))
    
    def test_create_workflow(self):
        """Test creating a new workflow."""
        # Create a workflow
        self.repo.create_workflow("test_workflow")
        
        # Check that the file was created
        file_path = os.path.join(self.test_dir, "test_workflow.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check that the file contains an empty list
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, [])
    
    def test_create_workflow_already_exists(self):
        """Test creating a workflow that already exists."""
        # Create a workflow
        self.repo.create_workflow("test_workflow")
        
        # Try to create it again
        with self.assertRaises(RepositoryError):
            self.repo.create_workflow("test_workflow")
    
    def test_save_and_load_workflow(self):
        """Test saving and loading a workflow."""
        # Save a workflow
        self.repo.save("test_workflow", self.sample_actions)
        
        # Check that the file was created
        file_path = os.path.join(self.test_dir, "test_workflow.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Load the workflow
        actions = self.repo.load("test_workflow")
        
        # Check that the actions were loaded correctly
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].name, "action1")
        self.assertEqual(actions[0].action_type, "Click")
        self.assertEqual(actions[1].name, "action2")
        self.assertEqual(actions[1].action_type, "Type")
    
    def test_load_nonexistent_workflow(self):
        """Test loading a nonexistent workflow."""
        # Try to load a nonexistent workflow
        with self.assertRaises(RepositoryError):
            self.repo.load("nonexistent")
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Create a workflow
        self.repo.create_workflow("test_workflow")
        
        # Delete the workflow
        result = self.repo.delete("test_workflow")
        
        # Check that the workflow was deleted
        self.assertTrue(result)
        file_path = os.path.join(self.test_dir, "test_workflow.json")
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_nonexistent_workflow(self):
        """Test deleting a nonexistent workflow."""
        # Try to delete a nonexistent workflow
        result = self.repo.delete("nonexistent")
        
        # Check that False was returned
        self.assertFalse(result)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        # Create multiple workflows
        self.repo.create_workflow("workflow1")
        self.repo.create_workflow("workflow2")
        
        # List the workflows
        workflows = self.repo.list_workflows()
        
        # Check that the workflows were listed
        self.assertEqual(len(workflows), 2)
        self.assertIn("workflow1", workflows)
        self.assertIn("workflow2", workflows)
    
    def test_list_workflows_empty(self):
        """Test listing workflows when there are none."""
        # List the workflows
        workflows = self.repo.list_workflows()
        
        # Check that an empty list was returned
        self.assertEqual(workflows, [])
    
    def test_get_metadata(self):
        """Test getting workflow metadata."""
        # Save a workflow
        self.repo.save("test_workflow", self.sample_actions)
        
        # Get the metadata
        metadata = self.repo.get_metadata("test_workflow")
        
        # Check that the metadata was retrieved
        self.assertEqual(metadata["name"], "test_workflow")
        self.assertEqual(metadata["source"], "file_system")
        self.assertEqual(metadata["action_count"], 2)
        self.assertIn("path", metadata)
        self.assertIn("size_bytes", metadata)
        self.assertIn("created_at", metadata)
        self.assertIn("modified_at", metadata)
    
    def test_get_metadata_nonexistent(self):
        """Test getting metadata for a nonexistent workflow."""
        # Try to get metadata for a nonexistent workflow
        with self.assertRaises(RepositoryError):
            self.repo.get_metadata("nonexistent")
    
    def test_save_and_load_template(self):
        """Test saving and loading a template."""
        # Create template data
        template_data = [
            {"action_type": "Click", "name": "template_action1", "selector": "#button"},
            {"action_type": "Type", "name": "template_action2", "selector": "#input", "text": "Hello"}
        ]
        
        # Save the template
        self.repo.save_template("test_template", template_data)
        
        # Check that the file was created
        file_path = os.path.join(self.test_dir, "templates", "test_template.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Load the template
        loaded_data = self.repo.load_template("test_template")
        
        # Check that the data was loaded correctly
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["name"], "template_action1")
        self.assertEqual(loaded_data[0]["action_type"], "Click")
        self.assertEqual(loaded_data[1]["name"], "template_action2")
        self.assertEqual(loaded_data[1]["action_type"], "Type")
    
    def test_load_nonexistent_template(self):
        """Test loading a nonexistent template."""
        # Try to load a nonexistent template
        with self.assertRaises(RepositoryError):
            self.repo.load_template("nonexistent")
    
    def test_delete_template(self):
        """Test deleting a template."""
        # Create template data
        template_data = [{"action_type": "Click", "name": "template_action"}]
        
        # Save the template
        self.repo.save_template("test_template", template_data)
        
        # Delete the template
        result = self.repo.delete_template("test_template")
        
        # Check that the template was deleted
        self.assertTrue(result)
        file_path = os.path.join(self.test_dir, "templates", "test_template.json")
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_nonexistent_template(self):
        """Test deleting a nonexistent template."""
        # Try to delete a nonexistent template
        result = self.repo.delete_template("nonexistent")
        
        # Check that False was returned
        self.assertFalse(result)
    
    def test_list_templates(self):
        """Test listing templates."""
        # Create multiple templates
        self.repo.save_template("template1", [{"action_type": "Click", "name": "action1"}])
        self.repo.save_template("template2", [{"action_type": "Type", "name": "action2"}])
        
        # List the templates
        templates = self.repo.list_templates()
        
        # Check that the templates were listed
        self.assertEqual(len(templates), 2)
        self.assertIn("template1", templates)
        self.assertIn("template2", templates)
    
    def test_list_templates_empty(self):
        """Test listing templates when there are none."""
        # List the templates
        templates = self.repo.list_templates()
        
        # Check that an empty list was returned
        self.assertEqual(templates, [])
    
    def test_thread_safety(self):
        """Test thread safety by simulating concurrent access."""
        # Function to save a workflow in a thread
        def save_workflow(name):
            actions = [MockAction(f"{name}_action")]
            self.repo.save(name, actions)
        
        # Create and start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_workflow, args=(f"thread_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all workflows were saved
        workflows = self.repo.list_workflows()
        self.assertEqual(len(workflows), 10)
        for i in range(10):
            self.assertIn(f"thread_{i}", workflows)
    
    def test_invalid_workflow_name(self):
        """Test handling of invalid workflow names."""
        # Try to create a workflow with an invalid name
        with self.assertRaises(ValidationError):
            self.repo.create_workflow("")
        
        # Try to save a workflow with an invalid name
        with self.assertRaises(ValidationError):
            self.repo.save("", self.sample_actions)
        
        # Try to load a workflow with an invalid name
        with self.assertRaises(ValidationError):
            self.repo.load("")
    
    def test_invalid_actions(self):
        """Test handling of invalid actions."""
        # Try to save a workflow with invalid actions
        with self.assertRaises(ValidationError):
            self.repo.save("test_workflow", "not_a_list")
        
        # Try to save a workflow with a list containing non-IAction items
        with self.assertRaises(ValidationError):
            self.repo.save("test_workflow", [{"not": "an_action"}])
    
    def test_file_io_error_handling(self):
        """Test handling of file I/O errors."""
        # Create a directory with the same name as a workflow file to cause an I/O error
        workflow_path = os.path.join(self.test_dir, "test_workflow.json")
        os.makedirs(workflow_path, exist_ok=True)
        
        # Try to save a workflow
        with self.assertRaises(RepositoryError):
            self.repo.save("test_workflow", self.sample_actions)


if __name__ == '__main__':
    unittest.main()
