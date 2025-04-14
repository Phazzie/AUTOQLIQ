"""Tests for variable substitution."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.workflow.context.variable_substitution import VariableSubstitutor


class TestVariableSubstitutor(unittest.TestCase):
    """Test cases for variable substitutor."""

    def setUp(self):
        """Set up test fixtures."""
        self.substitutor = VariableSubstitutor()
        self.context = {
            "string_var": "string_value",
            "int_var": 42,
            "bool_var": True,
            "list_var": ["item1", "item2"],
            "dict_var": {"key1": "value1", "key2": "value2"},
            "nested_var": {
                "nested_key1": "nested_value1",
                "nested_key2": ["nested_item1", "nested_item2"],
                "nested_key3": {"nested_nested_key": "nested_nested_value"}
            }
        }

    def test_substitute_variables_in_string(self):
        """Test substituting variables in a string."""
        # Test with a single variable
        result = self.substitutor.substitute_variables(
            "The value is {{string_var}}",
            self.context
        )
        self.assertEqual(result, "The value is string_value")
        
        # Test with multiple variables
        result = self.substitutor.substitute_variables(
            "The values are {{string_var}} and {{int_var}}",
            self.context
        )
        self.assertEqual(result, "The values are string_value and 42")
        
        # Test with a non-existent variable
        result = self.substitutor.substitute_variables(
            "The value is {{non_existent_var}}",
            self.context
        )
        self.assertEqual(result, "The value is {{non_existent_var}}")
        
        # Test with a non-string value
        result = self.substitutor.substitute_variables(
            "The value is {{int_var}}",
            self.context
        )
        self.assertEqual(result, "The value is 42")
        
        # Test with a boolean value
        result = self.substitutor.substitute_variables(
            "The value is {{bool_var}}",
            self.context
        )
        self.assertEqual(result, "The value is True")

    def test_substitute_variables_in_dict(self):
        """Test substituting variables in a dictionary."""
        test_dict = {
            "key1": "The value is {{string_var}}",
            "key2": "The value is {{int_var}}",
            "key3": {
                "nested_key1": "The value is {{string_var}}",
                "nested_key2": "The value is {{int_var}}"
            },
            "key4": ["The value is {{string_var}}", "The value is {{int_var}}"]
        }
        
        result = self.substitutor.substitute_variables_in_dict(test_dict, self.context)
        
        self.assertEqual(result["key1"], "The value is string_value")
        self.assertEqual(result["key2"], "The value is 42")
        self.assertEqual(result["key3"]["nested_key1"], "The value is string_value")
        self.assertEqual(result["key3"]["nested_key2"], "The value is 42")
        self.assertEqual(result["key4"][0], "The value is string_value")
        self.assertEqual(result["key4"][1], "The value is 42")

    def test_substitute_variables_in_list(self):
        """Test substituting variables in a list."""
        test_list = [
            "The value is {{string_var}}",
            "The value is {{int_var}}",
            ["The value is {{string_var}}", "The value is {{int_var}}"],
            {"key1": "The value is {{string_var}}", "key2": "The value is {{int_var}}"}
        ]
        
        result = self.substitutor.substitute_variables_in_list(test_list, self.context)
        
        self.assertEqual(result[0], "The value is string_value")
        self.assertEqual(result[1], "The value is 42")
        self.assertEqual(result[2][0], "The value is string_value")
        self.assertEqual(result[2][1], "The value is 42")
        self.assertEqual(result[3]["key1"], "The value is string_value")
        self.assertEqual(result[3]["key2"], "The value is 42")

    def test_substitute_variables_with_non_string_input(self):
        """Test substituting variables with non-string input."""
        # Test with None
        result = self.substitutor.substitute_variables(None, self.context)
        self.assertIsNone(result)
        
        # Test with an integer
        result = self.substitutor.substitute_variables(42, self.context)
        self.assertEqual(result, 42)
        
        # Test with a boolean
        result = self.substitutor.substitute_variables(True, self.context)
        self.assertEqual(result, True)
        
        # Test with a list
        test_list = ["item1", "item2"]
        result = self.substitutor.substitute_variables(test_list, self.context)
        self.assertEqual(result, test_list)
        
        # Test with a dictionary
        test_dict = {"key1": "value1", "key2": "value2"}
        result = self.substitutor.substitute_variables(test_dict, self.context)
        self.assertEqual(result, test_dict)


if __name__ == "__main__":
    unittest.main()
