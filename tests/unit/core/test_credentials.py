import unittest
import json
from dataclasses import asdict
from src.core.credentials import Credential


class TestCredentialEntity(unittest.TestCase):
    """
    Tests for the Credential entity to ensure it properly handles
    credential data, validation, equality, and serialization.
    """
    
    def test_initialization_with_valid_data(self):
        """Test that a Credential can be initialized with valid data."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        
        self.assertEqual(credential.name, "test_login")
        self.assertEqual(credential.username, "user@example.com")
        self.assertEqual(credential.password, "password123")
    
    def test_validation_empty_name(self):
        """Test that a Credential cannot be created with an empty name."""
        with self.assertRaises(ValueError):
            Credential(name="", username="user@example.com", password="password123")
    
    def test_validation_empty_username(self):
        """Test that a Credential cannot be created with an empty username."""
        with self.assertRaises(ValueError):
            Credential(name="test_login", username="", password="password123")
    
    def test_validation_empty_password(self):
        """Test that a Credential cannot be created with an empty password."""
        with self.assertRaises(ValueError):
            Credential(name="test_login", username="user@example.com", password="")
    
    def test_equality_comparison(self):
        """Test that two Credentials with the same data are considered equal."""
        credential1 = Credential(name="test_login", username="user@example.com", password="password123")
        credential2 = Credential(name="test_login", username="user@example.com", password="password123")
        credential3 = Credential(name="different", username="other@example.com", password="otherpass")
        
        self.assertEqual(credential1, credential2)
        self.assertNotEqual(credential1, credential3)
    
    def test_serialization_to_dict(self):
        """Test that a Credential can be serialized to a dictionary."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        expected_dict = {
            "name": "test_login",
            "username": "user@example.com",
            "password": "password123"
        }
        
        self.assertEqual(asdict(credential), expected_dict)
    
    def test_serialization_to_json(self):
        """Test that a Credential can be serialized to JSON."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        expected_json = json.dumps({
            "name": "test_login",
            "username": "user@example.com",
            "password": "password123"
        })
        
        self.assertEqual(credential.to_json(), expected_json)
    
    def test_deserialization_from_dict(self):
        """Test that a Credential can be created from a dictionary."""
        data = {
            "name": "test_login",
            "username": "user@example.com",
            "password": "password123"
        }
        
        credential = Credential.from_dict(data)
        
        self.assertEqual(credential.name, "test_login")
        self.assertEqual(credential.username, "user@example.com")
        self.assertEqual(credential.password, "password123")
    
    def test_deserialization_from_json(self):
        """Test that a Credential can be created from JSON."""
        json_data = json.dumps({
            "name": "test_login",
            "username": "user@example.com",
            "password": "password123"
        })
        
        credential = Credential.from_json(json_data)
        
        self.assertEqual(credential.name, "test_login")
        self.assertEqual(credential.username, "user@example.com")
        self.assertEqual(credential.password, "password123")
    
    def test_string_representation(self):
        """Test that a Credential has a meaningful string representation."""
        credential = Credential(name="test_login", username="user@example.com", password="password123")
        expected_str = "Credential(name='test_login', username='user@example.com', password='********')"
        
        self.assertEqual(str(credential), expected_str)


if __name__ == "__main__":
    unittest.main()
