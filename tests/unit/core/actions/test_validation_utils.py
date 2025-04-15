"""Tests for validation utilities."""

import unittest

from src.core.actions.validation_utils import validate_locator_type
from src.core.exceptions import ValidationError


class TestValidationUtils(unittest.TestCase):
    """Test cases for validation utilities."""

    def test_validate_locator_type_valid(self):
        """Test validating a valid locator type."""
        # Should not raise an exception
        validate_locator_type("id")
        validate_locator_type("xpath")
        validate_locator_type("css")
        
    def test_validate_locator_type_invalid(self):
        """Test validating an invalid locator type."""
        with self.assertRaises(ValidationError):
            validate_locator_type("invalid_type")
            
    def test_validate_locator_type_custom_types(self):
        """Test validating a locator type with custom valid types."""
        custom_types = ["custom1", "custom2"]
        
        # Should not raise an exception
        validate_locator_type("custom1", custom_types)
        
        # Should raise an exception
        with self.assertRaises(ValidationError):
            validate_locator_type("id", custom_types)  # "id" is not in custom_types
