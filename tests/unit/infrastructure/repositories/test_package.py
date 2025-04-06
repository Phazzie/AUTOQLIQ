"""Tests for the repositories package structure."""
import unittest
import importlib

class TestRepositoriesPackage(unittest.TestCase):
    """Test cases for the repositories package structure."""

    def test_package_imports(self):
        """Test that all repository classes can be imported from the repositories package."""
        # Import the repositories package
        import src.infrastructure.repositories as repositories
        
        # Check that all repository classes are available
        self.assertTrue(hasattr(repositories, "FileSystemCredentialRepository"))
        self.assertTrue(hasattr(repositories, "FileSystemWorkflowRepository"))
        self.assertTrue(hasattr(repositories, "RepositoryFactory"))
        
        # Check that the classes are the correct types
        self.assertEqual(repositories.FileSystemCredentialRepository.__name__, "FileSystemCredentialRepository")
        self.assertEqual(repositories.FileSystemWorkflowRepository.__name__, "FileSystemWorkflowRepository")
        self.assertEqual(repositories.RepositoryFactory.__name__, "RepositoryFactory")

    def test_backward_compatibility(self):
        """Test that the old imports still work for backward compatibility."""
        # This should not raise an ImportError
        from src.infrastructure.persistence import FileSystemCredentialRepository
        from src.infrastructure.persistence import FileSystemWorkflowRepository
        from src.infrastructure.persistence import RepositoryFactory
        
        # Check that the classes are the correct types
        self.assertEqual(FileSystemCredentialRepository.__name__, "FileSystemCredentialRepository")
        self.assertEqual(FileSystemWorkflowRepository.__name__, "FileSystemWorkflowRepository")
        self.assertEqual(RepositoryFactory.__name__, "RepositoryFactory")

if __name__ == "__main__":
    unittest.main()
