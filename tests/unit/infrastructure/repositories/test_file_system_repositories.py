"""Tests for file system repository implementations.

This module tests the FileSystemWorkflowRepository and FileSystemCredentialRepository classes.
"""

import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import MagicMock, patch

from src.infrastructure.repositories.file_system_workflow_repository import FileSystemWorkflowRepository
from src.infrastructure.repositories.file_system_credential_repository import FileSystemCredentialRepository
from src.core.workflow.workflow_entity import Workflow
from src.core.credentials import Credential
from src.core.exceptions import RepositoryError

class TestFileSystemWorkflowRepository(unittest.TestCase):
    """Test case for FileSystemWorkflowRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.repository = FileSystemWorkflowRepository(self.temp_dir)
        
        # Create a test workflow
        self.test_workflow = Workflow(
            id="test-id",
            name="Test Workflow",
            description="Test Description",
            actions=[]
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_workflow(self):
        """Test saving a workflow."""
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir, f"{self.test_workflow.id}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check the file contents
        with open(file_path, 'r') as f:
            workflow_dict = json.load(f)
        
        self.assertEqual(workflow_dict["id"], self.test_workflow.id)
        self.assertEqual(workflow_dict["name"], self.test_workflow.name)
        self.assertEqual(workflow_dict["description"], self.test_workflow.description)
    
    def test_save_workflow_with_actions(self):
        """Test saving a workflow with actions."""
        # Create a mock action
        mock_action = MagicMock()
        mock_action.to_dict.return_value = {"type": "MockAction", "name": "Mock Action"}
        
        # Add the action to the workflow
        self.test_workflow.actions = [mock_action]
        
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir, f"{self.test_workflow.id}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check the file contents
        with open(file_path, 'r') as f:
            workflow_dict = json.load(f)
        
        self.assertEqual(len(workflow_dict["actions"]), 1)
        self.assertEqual(workflow_dict["actions"][0]["type"], "MockAction")
        self.assertEqual(workflow_dict["actions"][0]["name"], "Mock Action")
    
    def test_save_workflow_without_id(self):
        """Test saving a workflow without an ID."""
        # Create a workflow without an ID
        workflow = Workflow(
            id=None,
            name="Test Workflow",
            description="Test Description",
            actions=[]
        )
        
        # Save the workflow
        self.repository.save(workflow)
        
        # Check that the workflow now has an ID
        self.assertIsNotNone(workflow.id)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir, f"{workflow.id}.json")
        self.assertTrue(os.path.exists(file_path))
    
    def test_get_workflow(self):
        """Test getting a workflow."""
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Get the workflow
        workflow = self.repository.get(self.test_workflow.id)
        
        # Check the workflow
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.id, self.test_workflow.id)
        self.assertEqual(workflow.name, self.test_workflow.name)
        self.assertEqual(workflow.description, self.test_workflow.description)
    
    def test_get_workflow_not_found(self):
        """Test getting a workflow that doesn't exist."""
        # Get a non-existent workflow
        workflow = self.repository.get("non-existent-id")
        
        # Check that the workflow is None
        self.assertIsNone(workflow)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        # Save multiple workflows
        workflow1 = Workflow(id="id1", name="Workflow 1", description="Description 1", actions=[])
        workflow2 = Workflow(id="id2", name="Workflow 2", description="Description 2", actions=[])
        
        self.repository.save(workflow1)
        self.repository.save(workflow2)
        
        # List workflows
        workflows = self.repository.list()
        
        # Check the workflows
        self.assertEqual(len(workflows), 2)
        
        # Check that both workflows are in the list
        workflow_ids = [w.id for w in workflows]
        self.assertIn(workflow1.id, workflow_ids)
        self.assertIn(workflow2.id, workflow_ids)
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Check that the file exists
        file_path = os.path.join(self.temp_dir, f"{self.test_workflow.id}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Delete the workflow
        self.repository.delete(self.test_workflow.id)
        
        # Check that the file was deleted
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_workflow_not_found(self):
        """Test deleting a workflow that doesn't exist."""
        # Delete a non-existent workflow
        self.repository.delete("non-existent-id")
        
        # No assertion needed, just checking that it doesn't raise an exception
    
    def test_save_workflow_error(self):
        """Test error handling when saving a workflow."""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Save the workflow
            with self.assertRaises(RepositoryError):
                self.repository.save(self.test_workflow)
    
    def test_get_workflow_error(self):
        """Test error handling when getting a workflow."""
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Get the workflow
            with self.assertRaises(RepositoryError):
                self.repository.get(self.test_workflow.id)
    
    def test_list_workflows_error(self):
        """Test error handling when listing workflows."""
        # Mock os.listdir to raise an exception
        with patch('os.listdir', side_effect=Exception("Test exception")):
            # List workflows
            with self.assertRaises(RepositoryError):
                self.repository.list()
    
    def test_delete_workflow_error(self):
        """Test error handling when deleting a workflow."""
        # Save the workflow
        self.repository.save(self.test_workflow)
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=Exception("Test exception")):
            # Delete the workflow
            with self.assertRaises(RepositoryError):
                self.repository.delete(self.test_workflow.id)

class TestFileSystemCredentialRepository(unittest.TestCase):
    """Test case for FileSystemCredentialRepository."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.repository = FileSystemCredentialRepository(self.temp_dir)
        
        # Create a test credential
        self.test_credential = Credential(
            name="test-credential",
            username="test-user",
            password="test-password"
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_credential(self):
        """Test saving a credential."""
        # Save the credential
        self.repository.save(self.test_credential)
        
        # Check that the file was created
        file_path = os.path.join(self.temp_dir, f"{self.test_credential.name}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Check the file contents
        with open(file_path, 'r') as f:
            credential_dict = json.load(f)
        
        self.assertEqual(credential_dict["name"], self.test_credential.name)
        self.assertEqual(credential_dict["username"], self.test_credential.username)
        self.assertEqual(credential_dict["password"], self.test_credential.password)
    
    def test_get_credential(self):
        """Test getting a credential."""
        # Save the credential
        self.repository.save(self.test_credential)
        
        # Get the credential
        credential = self.repository.get(self.test_credential.name)
        
        # Check the credential
        self.assertIsNotNone(credential)
        self.assertEqual(credential.name, self.test_credential.name)
        self.assertEqual(credential.username, self.test_credential.username)
        self.assertEqual(credential.password, self.test_credential.password)
    
    def test_get_credential_not_found(self):
        """Test getting a credential that doesn't exist."""
        # Get a non-existent credential
        credential = self.repository.get("non-existent-credential")
        
        # Check that the credential is None
        self.assertIsNone(credential)
    
    def test_list_credentials(self):
        """Test listing credentials."""
        # Save multiple credentials
        credential1 = Credential(name="credential1", username="user1", password="pass1")
        credential2 = Credential(name="credential2", username="user2", password="pass2")
        
        self.repository.save(credential1)
        self.repository.save(credential2)
        
        # List credentials
        credentials = self.repository.list()
        
        # Check the credentials
        self.assertEqual(len(credentials), 2)
        
        # Check that both credentials are in the list
        credential_names = [c.name for c in credentials]
        self.assertIn(credential1.name, credential_names)
        self.assertIn(credential2.name, credential_names)
    
    def test_delete_credential(self):
        """Test deleting a credential."""
        # Save the credential
        self.repository.save(self.test_credential)
        
        # Check that the file exists
        file_path = os.path.join(self.temp_dir, f"{self.test_credential.name}.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Delete the credential
        self.repository.delete(self.test_credential.name)
        
        # Check that the file was deleted
        self.assertFalse(os.path.exists(file_path))
    
    def test_delete_credential_not_found(self):
        """Test deleting a credential that doesn't exist."""
        # Delete a non-existent credential
        self.repository.delete("non-existent-credential")
        
        # No assertion needed, just checking that it doesn't raise an exception
    
    def test_save_credential_error(self):
        """Test error handling when saving a credential."""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Save the credential
            with self.assertRaises(RepositoryError):
                self.repository.save(self.test_credential)
    
    def test_get_credential_error(self):
        """Test error handling when getting a credential."""
        # Save the credential
        self.repository.save(self.test_credential)
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=Exception("Test exception")):
            # Get the credential
            with self.assertRaises(RepositoryError):
                self.repository.get(self.test_credential.name)
    
    def test_list_credentials_error(self):
        """Test error handling when listing credentials."""
        # Mock os.listdir to raise an exception
        with patch('os.listdir', side_effect=Exception("Test exception")):
            # List credentials
            with self.assertRaises(RepositoryError):
                self.repository.list()
    
    def test_delete_credential_error(self):
        """Test error handling when deleting a credential."""
        # Save the credential
        self.repository.save(self.test_credential)
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=Exception("Test exception")):
            # Delete the credential
            with self.assertRaises(RepositoryError):
                self.repository.delete(self.test_credential.name)

if __name__ == "__main__":
    unittest.main()
