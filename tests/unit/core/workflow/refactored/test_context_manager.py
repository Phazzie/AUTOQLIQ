"""Tests for the WorkflowContextManager class."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.workflow.context.manager import WorkflowContextManager
from src.core.workflow.context.base import ContextManager
from src.core.workflow.context.variable_substitution import VariableSubstitutor
from src.core.workflow.context.validator import ContextValidator
from src.core.workflow.context.serializer import ContextSerializer


class TestWorkflowContextManager(unittest.TestCase):
    """Test cases for the WorkflowContextManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context_manager = WorkflowContextManager()
    
    def test_init(self):
        """Test initialization."""
        self.assertIsInstance(self.context_manager.base_manager, ContextManager)
        self.assertIsInstance(self.context_manager.variable_substitutor, VariableSubstitutor)
        self.assertIsInstance(self.context_manager.validator, ContextValidator)
        self.assertIsInstance(self.context_manager.serializer, ContextSerializer)
    
    def test_create_context(self):
        """Test creating a new context."""
        context = self.context_manager.create_context()
        self.assertEqual(context, {})
    
    def test_update_context(self):
        """Test updating a context."""
        context = {"key1": "value1"}
        updates = {"key2": "value2", "key3": "value3"}
        
        updated_context = self.context_manager.update_context(context, updates)
        
        self.assertEqual(updated_context, {"key1": "value1", "key2": "value2", "key3": "value3"})
        self.assertEqual(context, {"key1": "value1", "key2": "value2", "key3": "value3"})
    
    def test_get_value(self):
        """Test getting a value from a context."""
        context = {"key1": "value1", "key2": "value2"}
        
        value = self.context_manager.get_value(context, "key1")
        self.assertEqual(value, "value1")
        
        value = self.context_manager.get_value(context, "key3", "default")
        self.assertEqual(value, "default")
    
    def test_set_value(self):
        """Test setting a value in a context."""
        context = {"key1": "value1"}
        
        self.context_manager.set_value(context, "key2", "value2")
        self.assertEqual(context, {"key1": "value1", "key2": "value2"})
        
        self.context_manager.set_value(context, "key1", "new_value")
        self.assertEqual(context, {"key1": "new_value", "key2": "value2"})
    
    def test_substitute_variables(self):
        """Test substituting variables in a string."""
        context = {"var1": "value1", "var2": "value2"}
        
        text = "This is a {{var1}} with {{var2}}"
        result = self.context_manager.substitute_variables(text, context)
        self.assertEqual(result, "This is a value1 with value2")
        
        text = "This has no variables"
        result = self.context_manager.substitute_variables(text, context)
        self.assertEqual(result, "This has no variables")
        
        text = "This has {{unknown}} variables"
        result = self.context_manager.substitute_variables(text, context)
        self.assertEqual(result, "This has {{unknown}} variables")
    
    def test_substitute_variables_in_dict(self):
        """Test substituting variables in a dictionary."""
        context = {"var1": "value1", "var2": "value2"}
        
        data = {
            "key1": "This is a {{var1}}",
            "key2": {
                "nested_key": "This is a {{var2}}"
            }
        }
        
        result = self.context_manager.substitute_variables_in_dict(data, context)
        
        self.assertEqual(result["key1"], "This is a value1")
        self.assertEqual(result["key2"]["nested_key"], "This is a value2")


class TestVariableSubstitutor(unittest.TestCase):
    """Test cases for the VariableSubstitutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.substitutor = VariableSubstitutor()
    
    def test_substitute_variables(self):
        """Test substituting variables in a string."""
        context = {"var1": "value1", "var2": "value2"}
        
        text = "This is a {{var1}} with {{var2}}"
        result = self.substitutor.substitute_variables(text, context)
        self.assertEqual(result, "This is a value1 with value2")
        
        text = "This has no variables"
        result = self.substitutor.substitute_variables(text, context)
        self.assertEqual(result, "This has no variables")
        
        text = "This has {{unknown}} variables"
        result = self.substitutor.substitute_variables(text, context)
        self.assertEqual(result, "This has {{unknown}} variables")
    
    def test_substitute_variables_in_dict(self):
        """Test substituting variables in a dictionary."""
        context = {"var1": "value1", "var2": "value2"}
        
        data = {
            "key1": "This is a {{var1}}",
            "key2": {
                "nested_key": "This is a {{var2}}"
            }
        }
        
        result = self.substitutor.substitute_variables_in_dict(data, context)
        
        self.assertEqual(result["key1"], "This is a value1")
        self.assertEqual(result["key2"]["nested_key"], "This is a value2")
    
    def test_substitute_variables_in_list(self):
        """Test substituting variables in a list."""
        context = {"var1": "value1", "var2": "value2"}
        
        data = [
            "This is a {{var1}}",
            {
                "nested_key": "This is a {{var2}}"
            },
            ["Nested list with {{var1}}"]
        ]
        
        result = self.substitutor.substitute_variables_in_list(data, context)
        
        self.assertEqual(result[0], "This is a value1")
        self.assertEqual(result[1]["nested_key"], "This is a value2")
        self.assertEqual(result[2][0], "Nested list with value1")


if __name__ == "__main__":
    unittest.main()
