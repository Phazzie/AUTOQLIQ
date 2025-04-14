"""Tests for the Workflow entity module."""

import unittest
from unittest.mock import Mock, patch
import json
from typing import List, Dict, Any

from src.core.interfaces import IAction, IWorkflow
from src.core.workflow.workflow_entity import Workflow
from src.core.exceptions import ValidationError


class TestWorkflowEntity(unittest.TestCase):
    """
    Tests for the Workflow entity to ensure it properly manages
    a sequence of actions.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Create mock actions
        self.action1 = Mock(spec=IAction)
        self.action1.name = "Action1"
        self.action1.to_dict.return_value = {"type": "TestAction", "name": "Action1"}
        self.action1.validate.return_value = True

        self.action2 = Mock(spec=IAction)
        self.action2.name = "Action2"
        self.action2.to_dict.return_value = {"type": "TestAction", "name": "Action2"}
        self.action2.validate.return_value = True

    def test_initialization_with_name_and_actions(self):
        """Test that a Workflow can be initialized with a name and actions."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(len(workflow.actions), 2)
        self.assertEqual(workflow.actions[0], self.action1)
        self.assertEqual(workflow.actions[1], self.action2)

    def test_initialization_with_empty_actions(self):
        """Test that a Workflow can be initialized with an empty actions list."""
        workflow = Workflow(name="empty_workflow")

        self.assertEqual(workflow.name, "empty_workflow")
        self.assertEqual(len(workflow.actions), 0)

    def test_initialization_with_description_and_metadata(self):
        """Test that a Workflow can be initialized with description and metadata."""
        metadata = {"created_by": "test_user", "tags": ["test", "example"]}
        workflow = Workflow(
            name="test_workflow",
            actions=[self.action1],
            description="Test workflow description",
            metadata=metadata
        )

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.description, "Test workflow description")
        self.assertEqual(workflow.metadata, metadata)

    def test_validation_empty_name(self):
        """Test that a Workflow cannot be created with an empty name."""
        with self.assertRaises(ValidationError):
            Workflow(name="", actions=[self.action1])

    def test_validation_non_action_object(self):
        """Test that a Workflow cannot be created with non-IAction objects."""
        with self.assertRaises(ValidationError):
            Workflow(name="test_workflow", actions=[self.action1, "not_an_action"])

    def test_add_action(self):
        """Test that actions can be added to a workflow."""
        workflow = Workflow(name="test_workflow", actions=[self.action1])

        # Add another action
        workflow.add_action(self.action2)

        self.assertEqual(len(workflow.actions), 2)
        self.assertEqual(workflow.actions[0], self.action1)
        self.assertEqual(workflow.actions[1], self.action2)

    def test_add_non_action(self):
        """Test that non-IAction objects cannot be added to a workflow."""
        workflow = Workflow(name="test_workflow", actions=[self.action1])

        with self.assertRaises(ValidationError):
            workflow.add_action("not_an_action")

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

    def test_validate(self):
        """Test that a workflow can validate itself and its actions."""
        workflow = Workflow(name="test_workflow", actions=[self.action1, self.action2])

        # Validate the workflow
        self.assertTrue(workflow.validate())

        # Test validation with a failing action
        self.action2.validate.side_effect = ValidationError("Action validation failed")

        with self.assertRaises(ValidationError) as context:
            workflow.validate()

        self.assertIn("Action at index 1", str(context.exception))
        self.assertIn("Action validation failed", str(context.exception))

    def test_to_dict(self):
        """Test that a workflow can be serialized to a dictionary."""
        workflow = Workflow(
            name="test_workflow",
            actions=[self.action1, self.action2],
            description="Test description",
            workflow_id="test-id",
            metadata={"key": "value"}
        )

        result = workflow.to_dict()

        self.assertEqual(result["id"], "test-id")
        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["metadata"], {"key": "value"})
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

    def test_from_dict_with_factory(self):
        """Test that a workflow can be created from a dictionary using a factory."""
        # Create a mock action factory
        mock_factory = Mock()
        mock_factory.create_action.side_effect = [self.action1, self.action2]

        data = {
            "name": "test_workflow",
            "description": "Test description",
            "id": "test-id",
            "actions": [
                {"type": "TestAction", "name": "Action1"},
                {"type": "TestAction", "name": "Action2"}
            ],
            "metadata": {"key": "value"}
        }

        workflow = Workflow.from_dict(data, action_factory=mock_factory)

        self.assertEqual(workflow.id, "test-id")
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.description, "Test description")
        self.assertEqual(workflow.metadata, {"key": "value"})
        self.assertEqual(len(workflow.actions), 2)

        # Verify that ActionFactory was called correctly
        mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action1"})
        mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action2"})

    def test_from_dict_without_factory(self):
        """Test that a workflow can be created from a dictionary with pre-instantiated actions."""
        data = {
            "name": "test_workflow",
            "actions": [self.action1, self.action2],
            "description": "Test description",
            "id": "test-id",
            "metadata": {"key": "value"}
        }

        workflow = Workflow.from_dict(data)

        self.assertEqual(workflow.id, "test-id")
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.description, "Test description")
        self.assertEqual(workflow.metadata, {"key": "value"})
        self.assertEqual(len(workflow.actions), 2)
        self.assertEqual(workflow.actions[0], self.action1)
        self.assertEqual(workflow.actions[1], self.action2)

    def test_from_dict_missing_name(self):
        """Test that from_dict raises ValidationError when name is missing."""
        data = {
            "actions": [self.action1, self.action2]
        }

        with self.assertRaises(ValidationError):
            Workflow.from_dict(data)

    def test_from_dict_missing_factory(self):
        """Test that from_dict raises ValidationError when factory is needed but not provided."""
        data = {
            "name": "test_workflow",
            "actions": [
                {"type": "TestAction", "name": "Action1"},
                {"type": "TestAction", "name": "Action2"}
            ]
        }

        with self.assertRaises(ValidationError):
            Workflow.from_dict(data)

    def test_from_json(self):
        """Test that a workflow can be created from JSON."""
        # Create a mock action factory
        mock_factory = Mock()
        mock_factory.create_action.side_effect = [self.action1, self.action2]

        json_str = json.dumps({
            "name": "test_workflow",
            "actions": [
                {"type": "TestAction", "name": "Action1"},
                {"type": "TestAction", "name": "Action2"}
            ]
        })

        workflow = Workflow.from_json(json_str, action_factory=mock_factory)

        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(len(workflow.actions), 2)

        # Verify that ActionFactory was called correctly
        mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action1"})
        mock_factory.create_action.assert_any_call({"type": "TestAction", "name": "Action2"})

    def test_string_representation(self):
        """Test that a workflow has a meaningful string representation."""
        workflow = Workflow(
            name="test_workflow",
            actions=[self.action1, self.action2],
            workflow_id="test-id"
        )

        expected_str = "Workflow(id=test-id, name=test_workflow, actions=2)"
        self.assertEqual(str(workflow), expected_str)


if __name__ == "__main__":
    unittest.main()
