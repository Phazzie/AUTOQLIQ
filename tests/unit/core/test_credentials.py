"""Tests for the Credential entity module."""

import unittest
from src.core.credentials import Credential
from src.core.exceptions import ValidationError


class TestCredentialEntity(unittest.TestCase):
    """
    Tests for the Credential entity to ensure it properly handles
    credential data, validation, and serialization.
    """
    
    def test_initialization_with_valid_data(self):
        """Test that a Credential can be initialized with valid data."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        
        self.assertEqual(credential.name, "test_login")
        self.assertEqual(credential.username, "user@example.com")
        self.assertEqual(credential.password, "password123")
    
    def test_validation_empty_name(self):
        """Test that a Credential cannot be created with an empty name."""
        with self.assertRaises(ValidationError):
            Credential(name="", username="user@example.com", password="password123")
    
    def test_validation_empty_username(self):
        """Test that a Credential cannot be created with an empty username."""
        with self.assertRaises(ValidationError):
            Credential(name="test_login", username="", password="password123")
    
    def test_validation_empty_password(self):
        """Test that a Credential cannot be created with an empty password."""
        with self.assertRaises(ValidationError):
            Credential(name="test_login", username="user@example.com", password="")
    
    def test_validate_method(self):
        """Test that the validate method works correctly."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        self.assertTrue(credential.validate())
    
    def test_string_representation(self):
        """Test that a Credential has a meaningful string representation."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        expected_str = "Credential(name='test_login', username='user@example.com', password='********')"
        
        self.assertEqual(str(credential), expected_str)

    def test_repr_representation(self):
        """Test the repr representation."""
        credential = Credential(name="repr_test", username="user", password="pass")
        expected_repr = "Credential(name='repr_test', username='user', password='********')"
        self.assertEqual(repr(credential), expected_repr)


if __name__ == "__main__":
    unittest.main()
