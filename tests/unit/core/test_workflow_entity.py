import unittest
from unittest.mock import Mock, patch
import json
from typing import List, Dict, Any

from src.core.interfaces import IAction, IWebDriver
from src.core.workflow_entity import Workflow
from src.core.action_result import ActionResult, ActionStatus


class TestWorkflowEntity(unittest.TestCase):
    """
    Tests for the Workflow entity to ensure it properly manages
    a sequence of actions and their execution.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Create mock actions
        self.action1 = Mock(spec=IAction)
        self.action1.name = "Action1"
        self.action1.to_dict.return_value = {"type": "TestAction", "name": "Action1"}
        self.action1.execute.return_value = ActionResult(ActionStatus.SUCCESS)

        self.action2 = Mock(spec=IAction)
        self.action2.name = "Action2"
        self.action2.to_dict.return_value = {"type": "TestAction", "name": "Action2"}
        self.action2.execute.return_value = ActionResult(ActionStatus.SUCCESS)

        # Create a mock driver
        self.driver = Mock(spec=IWebDriver)

    def test_initialization_with_name_and_actions(self):
        """Test that a Workflow can be initialized with a name and actions."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(len(workflow.actions), 2)
        self.assertEqual(workflow.actions[0], self.action1)
        self.assertEqual(workflow.actions[1], self.action2)

    def test_initialization_with_empty_actions(self):
        """Test that a Workflow can be initialized with an empty actions list."""
        workflow = Workflow(name="empty_workflow", actions=[])

        self.assertEqual(workflow.name, "empty_workflow")
        self.assertEqual(len(workflow.actions), 0)

    def test_validation_empty_name(self):
        """Test that a Workflow cannot be created with an empty name."""
        with self.assertRaises(ValueError):
            Workflow(name="", actions=[self.action1])

    def test_add_action(self):
        """Test that actions can be added to a workflow."""
        workflow = Workflow(name="test_workflow", actions=[self.action1])

        # Add another action
        workflow.add_action(self.action2)

        self.assertEqual(len(workflow.actions), 2)
        self.assertEqual(workflow.actions[0], self.action1)
        self.assertEqual(workflow.actions[1], self.action2)

    def test_remove_action(self):
        """Test that actions can be removed from a workflow."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        # Remove an action
        workflow.remove_action(0)

        self.assertEqual(len(workflow.actions), 1)
        self.assertEqual(workflow.actions[0], self.action2)

        # Test removing an action with an invalid index
        with self.assertRaises(IndexError):
            workflow.remove_action(10)

    def test_execute(self):
        """Test that a workflow can execute all its actions."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        # Execute the workflow
        results = workflow.execute(self.driver)

        # Verify that all actions were executed
        self.action1.execute.assert_called_once_with(self.driver)
        self.action2.execute.assert_called_once_with(self.driver)

        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_success())
        self.assertTrue(results[1].is_success())

    def test_execute_with_failure(self):
        """Test that a workflow stops execution when an action fails."""
        # Make the second action fail
        self.action2.execute.return_value = ActionResult(ActionStatus.FAILURE, "Action failed")

        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        # Execute the workflow
        results = workflow.execute(self.driver)

        # Verify that all actions were executed
        self.action1.execute.assert_called_once_with(self.driver)
        self.action2.execute.assert_called_once_with(self.driver)

        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_success())
        self.assertFalse(results[1].is_success())
        self.assertEqual(results[1].message, "Action failed")

    def test_to_dict(self):
        """Test that a workflow can be serialized to a dictionary."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        result = workflow.to_dict()

        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(len(result["actions"]), 2)
        self.assertEqual(result["actions"][0], {"type": "TestAction", "name": "Action1"})
        self.assertEqual(result["actions"][1], {"type": "TestAction", "name": "Action2"})

    def test_to_json(self):
        """Test that a workflow can be serialized to JSON."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        json_str = workflow.to_json()
        data = json.loads(json_str)

        self.assertEqual(data["name"], "test_workflow")
        self.assertEqual(len(data["actions"]), 2)
        self.assertEqual(data["actions"][0], {"type": "TestAction", "name": "Action1"})
        self.assertEqual(data["actions"][1], {"type": "TestAction", "name": "Action2"})

    def test_from_dict(self):
        """Test that a workflow can be created from a dictionary."""
        # We need to patch the ActionFactory to return our mock actions
        with patch("src.core.workflow_entity.ActionFactory") as mock_factory:
            mock_factory.create_action.side_effect = [self.action1, self.action2]

            data = {
                "name": "test_workflow",
                "actions": [
                    {"type": "TestAction", "name": "Action1"},
                    {"type": "TestAction", "name": "Action2"}
                ]
            }

            workflow = Workflow.from_dict(data)

            self.assertEqual(workflow.name, "test_workflow")
            self.assertEqual(len(workflow.actions), 2)
            # Verify that ActionFactory was called correctly
            mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action1"})
            mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action2"})

    def test_from_json(self):
        """Test that a workflow can be created from JSON."""
        # We need to patch the ActionFactory to return our mock actions
        with patch("src.core.workflow_entity.ActionFactory") as mock_factory:
            mock_factory.create_action.side_effect = [self.action1, self.action2]

            json_str = json.dumps({
                "name": "test_workflow",
                "actions": [
                    {"type": "TestAction", "name": "Action1"},
                    {"type": "TestAction", "name": "Action2"}
                ]
            })

            workflow = Workflow.from_json(json_str)

            self.assertEqual(workflow.name, "test_workflow")
            self.assertEqual(len(workflow.actions), 2)
            # Verify that ActionFactory was called correctly
            mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action1"})
            mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action2"})

    def test_string_representation(self):
        """Test that a workflow has a meaningful string representation."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        expected_str = "Workflow(name='test_workflow', actions=2)"

        self.assertEqual(str(workflow), expected_str)


if __name__ == "__main__":
    unittest.main()
