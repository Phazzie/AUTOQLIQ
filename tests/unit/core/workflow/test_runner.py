"""Tests for the workflow runner module."""
import unittest
from unittest.mock import Mock, patch

from src.core.interfaces import IWebDriver, ICredentialRepository, IWorkflowRepository, IAction
from src.core.exceptions import WorkflowError
from src.core.action_result import ActionResult, ActionStatus
from src.core.workflow.runner import WorkflowRunner

class TestWorkflowRunner(unittest.TestCase):
    """Test cases for the WorkflowRunner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.driver = Mock(spec=IWebDriver)
        self.credential_repo = Mock(spec=ICredentialRepository)
        self.workflow_repo = Mock(spec=IWorkflowRepository)
        self.runner = WorkflowRunner(self.driver, self.credential_repo, self.workflow_repo)

    def test_initialization(self):
        """Test that a WorkflowRunner can be initialized with the required parameters."""
        self.assertEqual(self.runner.driver, self.driver)
        self.assertEqual(self.runner.credential_repo, self.credential_repo)
        self.assertEqual(self.runner.workflow_repo, self.workflow_repo)

    def test_run_workflow_success(self):
        """Test that run_workflow executes all actions in a workflow."""
        # Create mock actions
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        action1.name = "Action1"
        action2.name = "Action2"
        action1.execute.return_value = ActionResult(ActionStatus.SUCCESS)
        action2.execute.return_value = ActionResult(ActionStatus.SUCCESS)
        
        # Set up the workflow repository to return the mock actions
        self.workflow_repo.load.return_value = [action1, action2]
        
        # Run the workflow
        results = self.runner.run_workflow("test_workflow")
        
        # Check that the workflow was loaded
        self.workflow_repo.load.assert_called_once_with("test_workflow")
        
        # Check that both actions were executed
        action1.execute.assert_called_once_with(self.driver)
        action2.execute.assert_called_once_with(self.driver)
        
        # Check the results
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_success())
        self.assertTrue(results[1].is_success())

    def test_run_workflow_with_type_action(self):
        """Test that run_workflow passes the credential repository to TypeAction."""
        # Create a mock TypeAction
        type_action = Mock(spec=IAction)
        type_action.name = "TypeAction"
        type_action.execute.return_value = ActionResult(ActionStatus.SUCCESS)
        
        # Set up the workflow repository to return the mock action
        self.workflow_repo.load.return_value = [type_action]
        
        # Patch the isinstance check to return True for our mock
        with patch("src.core.workflow.runner.isinstance") as mock_isinstance:
            mock_isinstance.return_value = True
            
            # Run the workflow
            results = self.runner.run_workflow("test_workflow")
            
            # Check that the action was executed with the credential repository
            type_action.execute.assert_called_once_with(self.driver, self.credential_repo)
            
            # Check the results
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].is_success())

    def test_run_workflow_failure(self):
        """Test that run_workflow raises WorkflowError when an action fails."""
        # Create mock actions
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        action1.name = "Action1"
        action2.name = "Action2"
        action1.execute.return_value = ActionResult(ActionStatus.FAILURE, "Action failed")
        
        # Set up the workflow repository to return the mock actions
        self.workflow_repo.load.return_value = [action1, action2]
        
        # Run the workflow and check that it raises WorkflowError
        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("test_workflow")
        
        # Check the error message
        self.assertIn("Action 'Action1' failed", str(context.exception))
        
        # Check that only the first action was executed
        action1.execute.assert_called_once_with(self.driver)
        action2.execute.assert_not_called()

    def test_run_workflow_repository_error(self):
        """Test that run_workflow handles WorkflowError from the repository."""
        # Set up the workflow repository to raise WorkflowError
        self.workflow_repo.load.side_effect = WorkflowError("Workflow not found")
        
        # Run the workflow and check that it raises WorkflowError
        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("test_workflow")
        
        # Check the error message
        self.assertIn("Workflow not found", str(context.exception))

    def test_run_workflow_unexpected_error(self):
        """Test that run_workflow handles unexpected errors."""
        # Set up the workflow repository to raise an unexpected error
        self.workflow_repo.load.side_effect = Exception("Unexpected error")
        
        # Run the workflow and check that it raises WorkflowError
        with self.assertRaises(WorkflowError) as context:
            self.runner.run_workflow("test_workflow")
        
        # Check the error message
        self.assertIn("An unexpected error occurred", str(context.exception))
        self.assertIn("test_workflow", str(context.exception))
        self.assertIn("Unexpected error", str(context.exception))

    def test_save_workflow(self):
        """Test that save_workflow saves a workflow to the repository."""
        # Create mock actions
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        
        # Save the workflow
        self.runner.save_workflow("test_workflow", [action1, action2])
        
        # Check that the workflow was saved
        self.workflow_repo.save.assert_called_once_with("test_workflow", [action1, action2])

    def test_list_workflows(self):
        """Test that list_workflows returns a list of workflows from the repository."""
        # Set up the workflow repository to return a list of workflows
        self.workflow_repo.list_workflows.return_value = ["workflow1", "workflow2"]
        
        # Get the list of workflows
        result = self.runner.list_workflows()
        
        # Check the result
        self.assertEqual(result, ["workflow1", "workflow2"])
        
        # Check that the repository method was called
        self.workflow_repo.list_workflows.assert_called_once()

    def test_load_workflow(self):
        """Test that load_workflow loads a workflow from the repository."""
        # Create mock actions
        action1 = Mock(spec=IAction)
        action2 = Mock(spec=IAction)
        
        # Set up the workflow repository to return the mock actions
        self.workflow_repo.load.return_value = [action1, action2]
        
        # Load the workflow
        result = self.runner.load_workflow("test_workflow")
        
        # Check the result
        self.assertEqual(result, [action1, action2])
        
        # Check that the repository method was called
        self.workflow_repo.load.assert_called_once_with("test_workflow")

if __name__ == "__main__":
    unittest.main()
