"""Tests for the UI package structure."""
import unittest
import importlib

class TestUIPackage(unittest.TestCase):
    """Test cases for the UI package structure."""

    def test_package_imports(self):
        """Test that all UI classes can be imported from the UI package."""
        # Import the UI package
        import src.ui as ui
        
        # Check that all UI classes are available
        self.assertTrue(hasattr(ui, "WorkflowEditorView"))
        self.assertTrue(hasattr(ui, "WorkflowRunnerView"))
        self.assertTrue(hasattr(ui, "WorkflowEditorPresenter"))
        self.assertTrue(hasattr(ui, "WorkflowRunnerPresenter"))
        
        # Check that the classes are the correct types
        self.assertEqual(ui.WorkflowEditorView.__name__, "WorkflowEditorView")
        self.assertEqual(ui.WorkflowRunnerView.__name__, "WorkflowRunnerView")
        self.assertEqual(ui.WorkflowEditorPresenter.__name__, "WorkflowEditorPresenter")
        self.assertEqual(ui.WorkflowRunnerPresenter.__name__, "WorkflowRunnerPresenter")

    def test_backward_compatibility(self):
        """Test that the old imports still work for backward compatibility."""
        # These should not raise ImportErrors
        from src.ui.editor_view import EditorView
        from src.ui.runner_view import RunnerView
        from src.ui.editor_presenter import EditorPresenter
        from src.ui.runner_presenter import RunnerPresenter
        
        # Check that the classes are the correct types
        self.assertEqual(EditorView.__name__, "EditorView")
        self.assertEqual(RunnerView.__name__, "RunnerView")
        self.assertEqual(EditorPresenter.__name__, "EditorPresenter")
        self.assertEqual(RunnerPresenter.__name__, "RunnerPresenter")

if __name__ == "__main__":
    unittest.main()
