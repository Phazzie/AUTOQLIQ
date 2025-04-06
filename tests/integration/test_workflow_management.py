import unittest
import os
import tempfile
import shutil
import json
from typing import List, Dict, Any

from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.actions import ActionFactory
from src.infrastructure.persistence import FileSystemWorkflowRepository, FileSystemCredentialRepository
from src.presenters.workflow_editor_presenter import WorkflowEditorPresenter


class TestWorkflowManagement(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for test data
        self.test_dir = tempfile.mkdtemp()
        self.workflows_dir = os.path.join(self.test_dir, "workflows")
        self.credentials_file = os.path.join(self.test_dir, "credentials.json")
        
        # Create the workflows directory
        os.makedirs(self.workflows_dir, exist_ok=True)
        
        # Create an empty credentials file
        with open(self.credentials_file, 'w') as f:
            json.dump([], f)
        
        # Create repositories
        self.workflow_repository = FileSystemWorkflowRepository(self.workflows_dir)
        self.credential_repository = FileSystemCredentialRepository(self.credentials_file)
        
        # Create action factory
        self.action_factory = ActionFactory()
        
        # Create presenter
        self.presenter = WorkflowEditorPresenter(self.workflow_repository, self.action_factory)
        
        # Test data
        self.test_workflow_name = "test_workflow"
        self.test_actions = [
            {"type": "Navigate", "url": "https://example.com"},
            {"type": "Click", "selector": "#button"},
            {"type": "Type", "selector": "#input", "text": "test"}
        ]
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_create_workflow(self):
        # Act
        result = self.presenter.create_workflow(self.test_workflow_name)
        
        # Assert
        self.assertTrue(result)
        
        # Verify the workflow file was created
        workflow_file = os.path.join(self.workflows_dir, f"{self.test_workflow_name}.json")
        self.assertTrue(os.path.exists(workflow_file))
        
        # Verify the workflow file contains an empty list of actions
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
            self.assertEqual(workflow_data, [])
    
    def test_get_workflow_list(self):
        # Arrange
        # Create a few test workflows
        self.presenter.create_workflow("workflow1")
        self.presenter.create_workflow("workflow2")
        self.presenter.create_workflow("workflow3")
        
        # Act
        result = self.presenter.get_workflow_list()
        
        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("workflow1", result)
        self.assertIn("workflow2", result)
        self.assertIn("workflow3", result)
    
    def test_add_action(self):
        # Arrange
        self.presenter.create_workflow(self.test_workflow_name)
        
        # Act
        for action in self.test_actions:
            result = self.presenter.add_action(self.test_workflow_name, action)
            self.assertTrue(result)
        
        # Assert
        # Load the workflow and verify the actions were added
        actions = self.presenter.load_workflow(self.test_workflow_name)
        self.assertEqual(len(actions), len(self.test_actions))
        
        # Verify each action
        for i, action in enumerate(actions):
            action_dict = action.to_dict()
            self.assertEqual(action_dict["type"], self.test_actions[i]["type"])
            
            if action_dict["type"] == "Navigate":
                self.assertEqual(action_dict["url"], self.test_actions[i]["url"])
            elif action_dict["type"] == "Click":
                self.assertEqual(action_dict["selector"], self.test_actions[i]["selector"])
            elif action_dict["type"] == "Type":
                self.assertEqual(action_dict["selector"], self.test_actions[i]["selector"])
                self.assertEqual(action_dict["text"], self.test_actions[i]["text"])
    
    def test_update_action(self):
        # Arrange
        self.presenter.create_workflow(self.test_workflow_name)
        
        # Add an action
        self.presenter.add_action(self.test_workflow_name, self.test_actions[0])
        
        # Create updated action
        updated_action = {"type": "Navigate", "url": "https://updated.com"}
        
        # Act
        result = self.presenter.update_action(self.test_workflow_name, 0, updated_action)
        
        # Assert
        self.assertTrue(result)
        
        # Load the workflow and verify the action was updated
        actions = self.presenter.load_workflow(self.test_workflow_name)
        self.assertEqual(len(actions), 1)
        
        # Verify the action was updated
        action_dict = actions[0].to_dict()
        self.assertEqual(action_dict["type"], updated_action["type"])
        self.assertEqual(action_dict["url"], updated_action["url"])
    
    def test_delete_action(self):
        # Arrange
        self.presenter.create_workflow(self.test_workflow_name)
        
        # Add actions
        for action in self.test_actions:
            self.presenter.add_action(self.test_workflow_name, action)
        
        # Act
        result = self.presenter.delete_action(self.test_workflow_name, 1)  # Delete the second action
        
        # Assert
        self.assertTrue(result)
        
        # Load the workflow and verify the action was deleted
        actions = self.presenter.load_workflow(self.test_workflow_name)
        self.assertEqual(len(actions), 2)
        
        # Verify the remaining actions
        action_dict_0 = actions[0].to_dict()
        self.assertEqual(action_dict_0["type"], self.test_actions[0]["type"])
        self.assertEqual(action_dict_0["url"], self.test_actions[0]["url"])
        
        action_dict_1 = actions[1].to_dict()
        self.assertEqual(action_dict_1["type"], self.test_actions[2]["type"])
        self.assertEqual(action_dict_1["selector"], self.test_actions[2]["selector"])
        self.assertEqual(action_dict_1["text"], self.test_actions[2]["text"])
    
    def test_save_and_load_workflow(self):
        # Arrange
        self.presenter.create_workflow(self.test_workflow_name)
        
        # Add actions
        for action in self.test_actions:
            self.presenter.add_action(self.test_workflow_name, action)
        
        # Act - Save the workflow
        save_result = self.presenter.save_workflow(self.test_workflow_name)
        
        # Assert
        self.assertTrue(save_result)
        
        # Act - Load the workflow
        actions = self.presenter.load_workflow(self.test_workflow_name)
        
        # Assert
        self.assertEqual(len(actions), len(self.test_actions))
        
        # Verify each action
        for i, action in enumerate(actions):
            action_dict = action.to_dict()
            self.assertEqual(action_dict["type"], self.test_actions[i]["type"])
            
            if action_dict["type"] == "Navigate":
                self.assertEqual(action_dict["url"], self.test_actions[i]["url"])
            elif action_dict["type"] == "Click":
                self.assertEqual(action_dict["selector"], self.test_actions[i]["selector"])
            elif action_dict["type"] == "Type":
                self.assertEqual(action_dict["selector"], self.test_actions[i]["selector"])
                self.assertEqual(action_dict["text"], self.test_actions[i]["text"])
    
    def test_delete_workflow(self):
        # Arrange
        self.presenter.create_workflow(self.test_workflow_name)
        
        # Verify the workflow file exists
        workflow_file = os.path.join(self.workflows_dir, f"{self.test_workflow_name}.json")
        self.assertTrue(os.path.exists(workflow_file))
        
        # Act
        result = self.presenter.delete_workflow(self.test_workflow_name)
        
        # Assert
        self.assertTrue(result)
        
        # Verify the workflow file was deleted
        self.assertFalse(os.path.exists(workflow_file))
        
        # Verify the workflow is no longer in the list
        workflows = self.presenter.get_workflow_list()
        self.assertNotIn(self.test_workflow_name, workflows)


if __name__ == "__main__":
    unittest.main()
