"""Tests for the TemplateRepository.

This module tests the TemplateRepository class.
"""

import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import patch

from src.core.template.repository import TemplateRepository
from src.core.exceptions import RepositoryError

class TestTemplateRepository(unittest.TestCase):
    """Test case for TemplateRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.repository = TemplateRepository(self.temp_dir)
        
        # Create a test template
        self.test_template = {
            "name": "test-template",
            "description": "Test Template",
            "actions": [
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"},
                {"type": "Click", "name": "Click Action", "selector": "#test-button"}
            ]
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_template(self):
        """Test saving a template."""
        # Save the template
        self.repository.save_template(self.test_template)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir, f"{self.test_template['name']}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check the file contents
        with open(file_path, 'r') as f:
            template_dict = json.load(f)
        
        self.assertEqual(template_dict["name"], self.test_template["name"])
        self.assertEqual(template_dict["description"], self.test_template["description"])
        self.assertEqual(len(template_dict["actions"]), 2)
    
    def test_save_template_without_name(self):
        """Test saving a template without a name."""
        # Create a template without a name
        template = {
            "description": "Test Template",
            "actions": []
        }
        
        # Save the template
        with self.assertRaises(ValueError):
            self.repository.save_template(template)
    
    def test_get_template(self):
        """Test getting a template."""
        # Save the template
        self.repository.save_template(self.test_template)
        
        # Get the template
        template = self.repository.get_template(self.test_template["name"])
        
        # Check the template
        self.assertIsNotNone(template)
        self.assertEqual(template["name"], self.test_template["name"])
        self.assertEqual(template["description"], self.test_template["description"])
        self.assertEqual(len(template["actions"]), 2)
    
    def test_get_template_not_found(self):
        """Test getting a template that doesn't exist."""
        # Get a non-existent template
        template = self.repository.get_template("non-existent-template")
        
        # Check that the template is None
        self.assertIsNone(template)
    
    def test_list_templates(self):
        """Test listing templates."""
        # Save multiple templates
        template1 = {
            "name": "template1",
            "description": "Template 1",
            "actions": []
        }
        template2 = {
            "name": "template2",
            "description": "Template 2",
            "actions": []
        }
        
        self.repository.save_template(template1)
        self.repository.save_template(template2)
        
        # List templates
        templates = self.repository.list_templates()
        
        # Check the templates
        self.assertEqual(len(templates), 2)
        
        # Check that both templates are in the list
        template_names = [t["name"] for t in templates]
        self.assertIn(template1["name"], template_names)
        self.assertIn(template2["name"], template_names)
    
    def test_delete_template(self):
        """Test deleting a template."""
        # Save the template
        self.repository.save_template(self.test_template)
        
        # Check that the file exists
        file_path = os.path.join(self.temp_dir, f"{self.test_template['name']}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Delete the template
        self.repository.delete_template(self.test_template["name"])
        
        # Check that the file was deleted
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_template_not_found(self):
        """Test deleting a template that doesn't exist."""
        # Delete a non-existent template
        self.repository.delete_template("non-existent-template")
        
        # No assertion needed, just checking that it doesn't raise an exception
    
    def test_save_template_error(self):
        """Test error handling when saving a template."""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Save the template
            with self.assertRaises(RepositoryError):
                self.repository.save_template(self.test_template)
    
    def test_get_template_error(self):
        """Test error handling when getting a template."""
        # Save the template
        self.repository.save_template(self.test_template)
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Get the template
            with self.assertRaises(RepositoryError):
                self.repository.get_template(self.test_template["name"])
    
    def test_list_templates_error(self):
        """Test error handling when listing templates."""
        # Mock os.listdir to raise an exception
        with patch('os.listdir', side_effect=Exception("Test exception")):
            # List templates
            with self.assertRaises(RepositoryError):
                self.repository.list_templates()
    
    def test_delete_template_error(self):
        """Test error handling when deleting a template."""
        # Save the template
        self.repository.save_template(self.test_template)
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=Exception("Test exception")):
            # Delete the template
            with self.assertRaises(RepositoryError):
                self.repository.delete_template(self.test_template["name"])
    
    def test_default_directory(self):
        """Test that the default directory is created if not specified."""
        # Mock os.path.expanduser to return a known path
        with patch('os.path.expanduser', return_value='/mock/home'):
            # Mock os.makedirs to check the path
            with patch('os.makedirs') as mock_makedirs:
                # Create repository with default path
                repository = TemplateRepository()
                
                # Check that the default path was used
                expected_path = '/mock/home/.autoqliq/templates'
                self.assertEqual(repository.directory_path, expected_path)
                
                # Check that the directory was created
                mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)

if __name__ == "__main__":
    unittest.main()
