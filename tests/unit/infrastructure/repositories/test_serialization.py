"""Tests for the serialization module."""
import unittest
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.serialization import (
    serialize_actions,
    deserialize_actions,
    extract_workflow_actions,
    extract_workflow_metadata
)

class TestSerialization(unittest.TestCase):
    """Test cases for the serialization module."""

    def test_serialize_actions(self):
        """Test that serialize_actions converts actions to dictionaries."""
        # Create mock actions
        action1 = MagicMock()
        action1.to_dict.return_value = {"type": "action1", "param": "value1"}
        
        action2 = MagicMock()
        action2.to_dict.return_value = {"type": "action2", "param": "value2"}
        
        actions = [action1, action2]
        
        # Serialize actions
        result = serialize_actions(actions)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"type": "action1", "param": "value1"})
        self.assertEqual(result[1], {"type": "action2", "param": "value2"})
        
        # Verify to_dict was called on each action
        action1.to_dict.assert_called_once()
        action2.to_dict.assert_called_once()

    @patch("src.core.actions.ActionFactory.create_action")
    def test_deserialize_actions(self, mock_create_action):
        """Test that deserialize_actions converts dictionaries to actions."""
        # Set up mock return values
        action1 = MagicMock()
        action2 = MagicMock()
        mock_create_action.side_effect = [action1, action2]
        
        # Action data to deserialize
        action_data = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"}
        ]
        
        # Deserialize actions
        result = deserialize_actions(action_data)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], action1)
        self.assertEqual(result[1], action2)
        
        # Verify create_action was called with correct arguments
        mock_create_action.assert_any_call({"type": "action1", "param": "value1"})
        mock_create_action.assert_any_call({"type": "action2", "param": "value2"})

    def test_extract_workflow_actions_new_format(self):
        """Test that extract_workflow_actions extracts actions from new format workflow data."""
        # New format workflow data
        workflow_data = {
            "metadata": {
                "name": "test_workflow",
                "version": "1.0"
            },
            "actions": [
                {"type": "action1", "param": "value1"},
                {"type": "action2", "param": "value2"}
            ]
        }
        
        # Extract actions
        result = extract_workflow_actions(workflow_data)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"type": "action1", "param": "value1"})
        self.assertEqual(result[1], {"type": "action2", "param": "value2"})

    def test_extract_workflow_actions_legacy_format(self):
        """Test that extract_workflow_actions extracts actions from legacy format workflow data."""
        # Legacy format workflow data (just a list of actions)
        workflow_data = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"}
        ]
        
        # Extract actions
        result = extract_workflow_actions(workflow_data)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"type": "action1", "param": "value1"})
        self.assertEqual(result[1], {"type": "action2", "param": "value2"})

    def test_extract_workflow_metadata_new_format(self):
        """Test that extract_workflow_metadata extracts metadata from new format workflow data."""
        # New format workflow data
        workflow_data = {
            "metadata": {
                "name": "test_workflow",
                "version": "1.0",
                "description": "Test workflow"
            },
            "actions": [
                {"type": "action1", "param": "value1"},
                {"type": "action2", "param": "value2"}
            ]
        }
        
        # Extract metadata
        result = extract_workflow_metadata(workflow_data, "test_workflow")
        
        # Check result
        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["description"], "Test workflow")

    def test_extract_workflow_metadata_legacy_format(self):
        """Test that extract_workflow_metadata creates minimal metadata for legacy format workflow data."""
        # Legacy format workflow data (just a list of actions)
        workflow_data = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"}
        ]
        
        # Extract metadata
        result = extract_workflow_metadata(workflow_data, "test_workflow")
        
        # Check result
        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(result["version"], "unknown")
        self.assertTrue(result["legacy_format"])

if __name__ == "__main__":
    unittest.main()
