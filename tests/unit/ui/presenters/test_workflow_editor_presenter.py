"""Tests for the workflow editor presenter."""
import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.core.interfaces import IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError

class TestWorkflowEditorPresenter(unittest.TestCase):
    """Test cases for the WorkflowEditorPresenter class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock view
        self.view = Mock()
        
        # Create a mock workflow repository
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        
        # Create a mock action factory
        self.action_factory = Mock()
        
        # Create the presenter
        self.presenter = WorkflowEditorPresenter(self.workflow_repo, self.action_factory)
        self.presenter.view = self.view

    def test_initialization(self):
        """Test that a WorkflowEditorPresenter can be initialized with the required parameters."""
        # Check that the presenter was initialized correctly
        self.assertEqual(self.presenter.workflow_repository, self.workflow_repo)
        self.assertEqual(self.presenter.action_factory, self.action_factory)
        self.assertEqual(self.presenter.view, self.view)

    def test_get_workflow_list(self):
        """Test that get_workflow_list returns a list of workflows from the repository."""
        # Set up the mock repository to return a list of workflows
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]
        
        # Call the method
        result = self.presenter.get_workflow_list()
        
        # Check the result
        self.assertEqual(result, ["workflow1", "workflow2"])
        
        # Check that the repository method was called
        self.workflow_repo.list_workflows.assert_called_once()

    def test_create_workflow_success(self):
        """Test that create_workflow creates a new workflow in the repository."""
        # Set up the mock repository
        self.workflow_repo.create_workflow.return_value = None
        
        # Call the method
        result = self.presenter.create_workflow("new_workflow")
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the repository method was called
        self.workflow_repo.create_workflow.assert_called_once_with("new_workflow")

    def test_create_workflow_failure(self):
        """Test that create_workflow returns False when the repository raises an exception."""
        # Set up the mock repository to raise an exception
        self.workflow_repo.create_workflow.side_effect = WorkflowError("Test error")
        
        # Call the method
        result = self.presenter.create_workflow("new_workflow")
        
        # Check the result
        self.assertFalse(result)
        
        # Check that the repository method was called
        self.workflow_repo.create_workflow.assert_called_once_with("new_workflow")

    def test_load_workflow_success(self):
        """Test that load_workflow loads a workflow from the repository."""
        # Create mock actions
        mock_action1 = Mock(spec=IAction)
        mock_action2 = Mock(spec=IAction)
        
        # Set up the mock repository to return the mock actions
        self.workflow_repo.load.return_value = [mock_action1, mock_action2]
        
        # Call the method
        result = self.presenter.load_workflow("test_workflow")
        
        # Check the result
        self.assertEqual(result, [mock_action1, mock_action2])
        
        # Check that the repository method was called
        self.workflow_repo.load.assert_called_once_with("test_workflow")

    def test_load_workflow_failure(self):
        """Test that load_workflow returns None when the repository raises an exception."""
        # Set up the mock repository to raise an exception
        self.workflow_repo.load.side_effect = WorkflowError("Test error")
        
        # Call the method
        result = self.presenter.load_workflow("test_workflow")
        
        # Check the result
        self.assertIsNone(result)
        
        # Check that the repository method was called
        self.workflow_repo.load.assert_called_once_with("test_workflow")

    def test_save_workflow_success(self):
        """Test that save_workflow saves a workflow to the repository."""
        # Create mock actions
        mock_action1 = Mock(spec=IAction)
        mock_action2 = Mock(spec=IAction)
        
        # Set up the mock repository
        self.workflow_repo.save.return_value = None
        
        # Call the method
        result = self.presenter.save_workflow("test_workflow", [mock_action1, mock_action2])
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the repository method was called
        self.workflow_repo.save.assert_called_once_with("test_workflow", [mock_action1, mock_action2])

    def test_save_workflow_failure(self):
        """Test that save_workflow returns False when the repository raises an exception."""
        # Create mock actions
        mock_action1 = Mock(spec=IAction)
        mock_action2 = Mock(spec=IAction)
        
        # Set up the mock repository to raise an exception
        self.workflow_repo.save.side_effect = WorkflowError("Test error")
        
        # Call the method
        result = self.presenter.save_workflow("test_workflow", [mock_action1, mock_action2])
        
        # Check the result
        self.assertFalse(result)
        
        # Check that the repository method was called
        self.workflow_repo.save.assert_called_once_with("test_workflow", [mock_action1, mock_action2])

    def test_add_action_success(self):
        """Test that add_action adds an action to a workflow."""
        # Create a mock action
        mock_action = Mock(spec=IAction)
        
        # Set up the mock action factory to return the mock action
        self.action_factory.create_action.return_value = mock_action
        
        # Set up the mock repository
        self.workflow_repo.load.return_value = []
        self.workflow_repo.save.return_value = None
        
        # Call the method
        result = self.presenter.add_action("test_workflow", {"type": "Navigate", "url": "https://example.com"})
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the repository methods were called
        self.workflow_repo.load.assert_called_once_with("test_workflow")
        self.workflow_repo.save.assert_called_once_with("test_workflow", [mock_action])
        
        # Check that the action factory was called
        self.action_factory.create_action.assert_called_once_with({"type": "Navigate", "url": "https://example.com"})

    def test_add_action_failure(self):
        """Test that add_action returns False when the repository raises an exception."""
        # Set up the mock repository to raise an exception
        self.workflow_repo.load.side_effect = WorkflowError("Test error")
        
        # Call the method
        result = self.presenter.add_action("test_workflow", {"type": "Navigate", "url": "https://example.com"})
        
        # Check the result
        self.assertFalse(result)
        
        # Check that the repository method was called
        self.workflow_repo.load.assert_called_once_with("test_workflow")
        
        # Check that the action factory was not called
        self.action_factory.create_action.assert_not_called()

if __name__ == "__main__":
    unittest.main()
