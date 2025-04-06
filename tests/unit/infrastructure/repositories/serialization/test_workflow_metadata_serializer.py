"""Tests for the workflow metadata serializer module."""
import unittest
from unittest.mock import patch, MagicMock

from src.infrastructure.repositories.serialization.workflow_metadata_serializer import (
    WorkflowMetadataSerializer,
    extract_workflow_metadata,
    extract_workflow_actions
)

class TestWorkflowMetadataSerializer(unittest.TestCase):
    """Test cases for the WorkflowMetadataSerializer class."""

    def test_extract_workflow_metadata_new_format(self):
        """Test that extract_workflow_metadata extracts metadata from new format workflow data."""
        # New format workflow data (with metadata)
        workflow_data = {
            "metadata": {
                "name": "test_workflow",
                "version": "1.0",
                "created": "2023-01-01T00:00:00Z",
                "modified": "2023-01-02T00:00:00Z"
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
        self.assertEqual(result["created"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["modified"], "2023-01-02T00:00:00Z")

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

    def test_extract_workflow_actions_new_format(self):
        """Test that extract_workflow_actions extracts actions from new format workflow data."""
        # New format workflow data (with metadata)
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
        """Test that extract_workflow_actions returns the workflow data for legacy format."""
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

    def test_workflow_metadata_serializer_extract_metadata(self):
        """Test that WorkflowMetadataSerializer.extract_metadata extracts metadata from workflow data."""
        # New format workflow data (with metadata)
        workflow_data = {
            "metadata": {
                "name": "test_workflow",
                "version": "1.0",
                "created": "2023-01-01T00:00:00Z",
                "modified": "2023-01-02T00:00:00Z"
            },
            "actions": [
                {"type": "action1", "param": "value1"},
                {"type": "action2", "param": "value2"}
            ]
        }
        
        # Create serializer
        serializer = WorkflowMetadataSerializer()
        
        # Extract metadata
        result = serializer.extract_metadata(workflow_data, "test_workflow")
        
        # Check result
        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["created"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["modified"], "2023-01-02T00:00:00Z")

    def test_workflow_metadata_serializer_extract_actions(self):
        """Test that WorkflowMetadataSerializer.extract_actions extracts actions from workflow data."""
        # New format workflow data (with metadata)
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
        
        # Create serializer
        serializer = WorkflowMetadataSerializer()
        
        # Extract actions
        result = serializer.extract_actions(workflow_data)
        
        # Check result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"type": "action1", "param": "value1"})
        self.assertEqual(result[1], {"type": "action2", "param": "value2"})

if __name__ == "__main__":
    unittest.main()
