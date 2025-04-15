"""Tests for sensitive data filter."""

import unittest
from typing import Dict, Any, List

from src.core.workflow.result_processing.sensitive_data_filter import SensitiveDataFilter


class TestSensitiveDataFilter(unittest.TestCase):
    """Test cases for sensitive data filter."""

    def setUp(self):
        """Set up test fixtures."""
        self.filter = SensitiveDataFilter()
        
        # Test data
        self.simple_data = {
            "username": "test_user",
            "password": "secret_password",
            "token": "secret_token",
            "api_key": "secret_key",
            "credential": "secret_credential",
            "auth_token": "secret_auth_token",
            "other_data": "not_sensitive"
        }
        
        self.nested_data = {
            "user": {
                "name": "test_user",
                "password": "secret_password",
                "settings": {
                    "api_key": "secret_key",
                    "theme": "dark"
                }
            },
            "session": {
                "token": "secret_token",
                "expires": "2023-12-31"
            }
        }
        
        self.list_data = [
            {"username": "user1", "password": "pass1"},
            {"username": "user2", "password": "pass2"},
            "not_sensitive"
        ]
        
        self.complex_data = {
            "users": [
                {"username": "user1", "password": "pass1"},
                {"username": "user2", "password": "pass2"}
            ],
            "settings": {
                "api_keys": [
                    {"name": "key1", "value": "secret1"},
                    {"name": "key2", "value": "secret2"}
                ],
                "general": {
                    "theme": "dark",
                    "language": "en"
                }
            },
            "credentials": {
                "database": {
                    "username": "db_user",
                    "password": "db_pass"
                }
            }
        }

    def test_filter_simple_data(self):
        """Test filtering simple data with sensitive fields."""
        filtered_data = self.filter.filter_data(self.simple_data)
        
        # Check that sensitive data is masked
        self.assertEqual(filtered_data["username"], "test_user")
        self.assertEqual(filtered_data["password"], "********")
        self.assertEqual(filtered_data["token"], "********")
        self.assertEqual(filtered_data["api_key"], "********")
        self.assertEqual(filtered_data["credential"], "********")
        self.assertEqual(filtered_data["auth_token"], "********")
        self.assertEqual(filtered_data["other_data"], "not_sensitive")
        
        # Check that the original data is not modified
        self.assertEqual(self.simple_data["password"], "secret_password")

    def test_filter_nested_data(self):
        """Test filtering nested data with sensitive fields."""
        filtered_data = self.filter.filter_data(self.nested_data)
        
        # Check that sensitive data is masked at all levels
        self.assertEqual(filtered_data["user"]["name"], "test_user")
        self.assertEqual(filtered_data["user"]["password"], "********")
        self.assertEqual(filtered_data["user"]["settings"]["api_key"], "********")
        self.assertEqual(filtered_data["user"]["settings"]["theme"], "dark")
        self.assertEqual(filtered_data["session"]["token"], "********")
        self.assertEqual(filtered_data["session"]["expires"], "2023-12-31")
        
        # Check that the original data is not modified
        self.assertEqual(self.nested_data["user"]["password"], "secret_password")

    def test_filter_list_data(self):
        """Test filtering list data with sensitive fields."""
        filtered_data = self.filter.filter_data(self.list_data)
        
        # Check that sensitive data is masked in lists
        self.assertEqual(filtered_data[0]["username"], "user1")
        self.assertEqual(filtered_data[0]["password"], "********")
        self.assertEqual(filtered_data[1]["username"], "user2")
        self.assertEqual(filtered_data[1]["password"], "********")
        self.assertEqual(filtered_data[2], "not_sensitive")
        
        # Check that the original data is not modified
        self.assertEqual(self.list_data[0]["password"], "pass1")

    def test_filter_complex_data(self):
        """Test filtering complex nested data with sensitive fields."""
        filtered_data = self.filter.filter_data(self.complex_data)
        
        # Check that sensitive data is masked at all levels
        self.assertEqual(filtered_data["users"][0]["username"], "user1")
        self.assertEqual(filtered_data["users"][0]["password"], "********")
        self.assertEqual(filtered_data["users"][1]["username"], "user2")
        self.assertEqual(filtered_data["users"][1]["password"], "********")
        
        self.assertEqual(filtered_data["settings"]["api_keys"][0]["name"], "key1")
        self.assertEqual(filtered_data["settings"]["api_keys"][0]["value"], "secret1")  # Not masked by default
        self.assertEqual(filtered_data["settings"]["api_keys"][1]["name"], "key2")
        self.assertEqual(filtered_data["settings"]["api_keys"][1]["value"], "secret2")  # Not masked by default
        
        self.assertEqual(filtered_data["settings"]["general"]["theme"], "dark")
        self.assertEqual(filtered_data["settings"]["general"]["language"], "en")
        
        self.assertEqual(filtered_data["credentials"]["database"]["username"], "db_user")
        self.assertEqual(filtered_data["credentials"]["database"]["password"], "********")
        
        # Check that the original data is not modified
        self.assertEqual(self.complex_data["credentials"]["database"]["password"], "db_pass")

    def test_custom_sensitive_words(self):
        """Test filtering with custom sensitive words."""
        custom_filter = SensitiveDataFilter(sensitive_words=["value", "secret"])
        
        data = {
            "name": "test",
            "value": "should_be_masked",
            "secret_data": "should_be_masked",
            "password": "should_not_be_masked"  # Not in custom list
        }
        
        filtered_data = custom_filter.filter_data(data)
        
        self.assertEqual(filtered_data["name"], "test")
        self.assertEqual(filtered_data["value"], "********")
        self.assertEqual(filtered_data["secret_data"], "********")
        self.assertEqual(filtered_data["password"], "should_not_be_masked")

    def test_custom_mask(self):
        """Test filtering with a custom mask."""
        custom_filter = SensitiveDataFilter(mask="[REDACTED]")
        
        data = {
            "password": "secret"
        }
        
        filtered_data = custom_filter.filter_data(data)
        
        self.assertEqual(filtered_data["password"], "[REDACTED]")


if __name__ == "__main__":
    unittest.main()
