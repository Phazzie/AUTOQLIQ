"""Tests for the actions package structure."""
import unittest
import importlib

class TestActionsPackage(unittest.TestCase):
    """Test cases for the actions package structure."""

    def test_package_imports(self):
        """Test that all action classes can be imported from the actions package."""
        # Import the actions package
        import src.core.actions as actions
        
        # Check that all action classes are available
        self.assertTrue(hasattr(actions, "NavigateAction"))
        self.assertTrue(hasattr(actions, "ClickAction"))
        self.assertTrue(hasattr(actions, "TypeAction"))
        self.assertTrue(hasattr(actions, "WaitAction"))
        self.assertTrue(hasattr(actions, "ScreenshotAction"))
        self.assertTrue(hasattr(actions, "ActionFactory"))
        
        # Check that the classes are the correct types
        self.assertEqual(actions.NavigateAction.__name__, "NavigateAction")
        self.assertEqual(actions.ClickAction.__name__, "ClickAction")
        self.assertEqual(actions.TypeAction.__name__, "TypeAction")
        self.assertEqual(actions.WaitAction.__name__, "WaitAction")
        self.assertEqual(actions.ScreenshotAction.__name__, "ScreenshotAction")
        self.assertEqual(actions.ActionFactory.__name__, "ActionFactory")

    def test_backward_compatibility(self):
        """Test that the old imports still work for backward compatibility."""
        # This should not raise an ImportError
        from src.core.actions import NavigateAction, ClickAction, TypeAction, WaitAction, ScreenshotAction, ActionFactory
        
        # Check that the classes are the correct types
        self.assertEqual(NavigateAction.__name__, "NavigateAction")
        self.assertEqual(ClickAction.__name__, "ClickAction")
        self.assertEqual(TypeAction.__name__, "TypeAction")
        self.assertEqual(WaitAction.__name__, "WaitAction")
        self.assertEqual(ScreenshotAction.__name__, "ScreenshotAction")
        self.assertEqual(ActionFactory.__name__, "ActionFactory")

if __name__ == "__main__":
    unittest.main()
