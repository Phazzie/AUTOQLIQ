"""Tests for the action serializer module."""
import unittest
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.serialization.action_serializer import (
    ActionSerializer,
    serialize_actions,
    deserialize_actions
)

class TestActionSerializer(unittest.TestCase):
    """Test cases for the ActionSerializer class."""

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
        
        # Verify create_action was called for each action
        self.assertEqual(mock_create_action.call_count, 2)
        mock_create_action.assert_any_call({"type": "action1", "param": "value1"})
        mock_create_action.assert_any_call({"type": "action2", "param": "value2"})

    def test_action_serializer_serialize(self):
        """Test that ActionSerializer.serialize converts actions to dictionaries."""
        # Create mock actions
        action1 = MagicMock()
        action1.to_dict.return_value = {"type": "action1", "param": "value1"}
        
        action2 = MagicMock()
        action2.to_dict.return_value = {"type": "action2", "param": "value2"}
        
        actions = [action1, action2]
        
        # Create serializer
        serializer = ActionSerializer()
        
        # Serialize actions
        result = serializer.serialize(actions)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"type": "action1", "param": "value1"})
        self.assertEqual(result[1], {"type": "action2", "param": "value2"})
        
        # Verify to_dict was called on each action
        action1.to_dict.assert_called_once()
        action2.to_dict.assert_called_once()

    @patch("src.core.actions.ActionFactory.create_action")
    def test_action_serializer_deserialize(self, mock_create_action):
        """Test that ActionSerializer.deserialize converts dictionaries to actions."""
        # Set up mock return values
        action1 = MagicMock()
        action2 = MagicMock()
        mock_create_action.side_effect = [action1, action2]
        
        # Action data to deserialize
        action_data = [
            {"type": "action1", "param": "value1"},
            {"type": "action2", "param": "value2"}
        ]
        
        # Create serializer
        serializer = ActionSerializer()
        
        # Deserialize actions
        result = serializer.deserialize(action_data)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], action1)
        self.assertEqual(result[1], action2)
        
        # Verify create_action was called for each action
        self.assertEqual(mock_create_action.call_count, 2)
        mock_create_action.assert_any_call({"type": "action1", "param": "value1"})
        mock_create_action.assert_any_call({"type": "action2", "param": "value2"})

if __name__ == "__main__":
    unittest.main()
