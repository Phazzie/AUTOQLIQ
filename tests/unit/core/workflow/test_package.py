"""Tests for the workflow package structure."""
import unittest
import importlib

class TestWorkflowPackage(unittest.TestCase):
    """Test cases for the workflow package structure."""

    def test_package_imports(self):
        """Test that all workflow classes can be imported from the workflow package."""
        # Import the workflow package
        import src.core.workflow as workflow
        
        # Check that all workflow classes are available
        self.assertTrue(hasattr(workflow, "Workflow"))
        self.assertTrue(hasattr(workflow, "WorkflowRunner"))
        
        # Check that the classes are the correct types
        self.assertEqual(workflow.Workflow.__name__, "Workflow")
        self.assertEqual(workflow.WorkflowRunner.__name__, "WorkflowRunner")

    def test_backward_compatibility(self):
        """Test that the old imports still work for backward compatibility."""
        # This should not raise an ImportError
        from src.core.workflow import WorkflowRunner
        from src.core.workflow_entity import Workflow
        
        # Check that the classes are the correct types
        self.assertEqual(WorkflowRunner.__name__, "WorkflowRunner")
        self.assertEqual(Workflow.__name__, "Workflow")

if __name__ == "__main__":
    unittest.main()
