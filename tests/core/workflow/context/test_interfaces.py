"""Tests for context management interfaces.

This module tests the implementation of context management interfaces.
"""

import unittest
from typing import Dict, Any, List, Optional, Set

from src.core.workflow.context.interfaces import (
    IContextProvider, IContextUpdater, IVariableResolver,
    IContextValidator, IContextSerializer, IWorkflowContextManager
)
from src.core.workflow.context.base import ContextManager
from src.core.workflow.context.variable_substitution import VariableSubstitutor
from src.core.workflow.context.validator import ContextValidator
from src.core.workflow.context.serializer import ContextSerializer
from src.core.workflow.context.manager import WorkflowContextManager


class TestContextInterfaces(unittest.TestCase):
    """Test the implementation of context management interfaces."""

    def test_context_manager_implements_interfaces(self):
        """Test that ContextManager implements IContextProvider and IContextUpdater."""
        context_manager = ContextManager()
        self.assertIsInstance(context_manager, IContextProvider)
        self.assertIsInstance(context_manager, IContextUpdater)

    def test_variable_substitutor_implements_interface(self):
        """Test that VariableSubstitutor implements IVariableResolver."""
        variable_substitutor = VariableSubstitutor()
        self.assertIsInstance(variable_substitutor, IVariableResolver)

    def test_context_validator_implements_interface(self):
        """Test that ContextValidator implements IContextValidator."""
        context_validator = ContextValidator()
        self.assertIsInstance(context_validator, IContextValidator)

    def test_context_serializer_implements_interface(self):
        """Test that ContextSerializer implements IContextSerializer."""
        context_serializer = ContextSerializer()
        self.assertIsInstance(context_serializer, IContextSerializer)

    def test_workflow_context_manager_implements_interface(self):
        """Test that WorkflowContextManager implements IWorkflowContextManager."""
        workflow_context_manager = WorkflowContextManager()
        self.assertIsInstance(workflow_context_manager, IWorkflowContextManager)

    def test_context_provider_methods(self):
        """Test that IContextProvider methods are implemented correctly."""
        context_manager = ContextManager()
        context = context_manager.create_context()
        self.assertIsInstance(context, dict)
        
        value = context_manager.get_value(context, "test_key", "default_value")
        self.assertEqual(value, "default_value")
        
        context_manager.set_value(context, "test_key", "test_value")
        value = context_manager.get_value(context, "test_key")
        self.assertEqual(value, "test_value")

    def test_variable_resolver_methods(self):
        """Test that IVariableResolver methods are implemented correctly."""
        variable_substitutor = VariableSubstitutor()
        context = {"name": "John", "age": 30}
        
        text = "Hello {{name}}, you are {{age}} years old."
        result = variable_substitutor.substitute_variables(text, context)
        self.assertEqual(result, "Hello John, you are 30 years old.")
        
        data_dict = {"greeting": "Hello {{name}}!", "info": "You are {{age}} years old."}
        result_dict = variable_substitutor.substitute_variables_in_dict(data_dict, context)
        self.assertEqual(result_dict["greeting"], "Hello John!")
        self.assertEqual(result_dict["info"], "You are 30 years old.")

    def test_context_validator_methods(self):
        """Test that IContextValidator methods are implemented correctly."""
        context_validator = ContextValidator()
        context = {"name": "John", "age": 30}
        
        self.assertTrue(context_validator.validate_context(context, ["name"]))
        self.assertFalse(context_validator.validate_context(context, ["name", "email"]))
        
        missing_keys = context_validator.get_missing_keys(context, ["name", "email"])
        self.assertEqual(missing_keys, ["email"])
        
        available_keys = context_validator.get_available_keys(context)
        self.assertEqual(available_keys, {"name", "age"})

    def test_context_serializer_methods(self):
        """Test that IContextSerializer methods are implemented correctly."""
        context_serializer = ContextSerializer()
        context = {"name": "John", "age": 30}
        
        serialized = context_serializer.serialize_context(context)
        self.assertIsInstance(serialized, str)
        
        deserialized = context_serializer.deserialize_context(serialized)
        self.assertEqual(deserialized, context)

    def test_workflow_context_manager_methods(self):
        """Test that IWorkflowContextManager methods are implemented correctly."""
        workflow_context_manager = WorkflowContextManager()
        
        # Test create_context and update_context
        context = workflow_context_manager.create_context()
        self.assertIsInstance(context, dict)
        
        updates = {"name": "John", "age": 30}
        updated_context = workflow_context_manager.update_context(context, updates)
        self.assertEqual(updated_context["name"], "John")
        self.assertEqual(updated_context["age"], 30)
        
        # Test get_value and set_value
        value = workflow_context_manager.get_value(context, "name")
        self.assertEqual(value, "John")
        
        workflow_context_manager.set_value(context, "email", "john@example.com")
        value = workflow_context_manager.get_value(context, "email")
        self.assertEqual(value, "john@example.com")
        
        # Test substitute_variables
        text = "Hello {{name}}, you are {{age}} years old."
        result = workflow_context_manager.substitute_variables(text, context)
        self.assertEqual(result, "Hello John, you are 30 years old.")
        
        # Test substitute_variables_in_dict
        data_dict = {"greeting": "Hello {{name}}!", "info": "You are {{age}} years old."}
        result_dict = workflow_context_manager.substitute_variables_in_dict(data_dict, context)
        self.assertEqual(result_dict["greeting"], "Hello John!")
        self.assertEqual(result_dict["info"], "You are 30 years old.")
        
        # Test validate_context
        self.assertTrue(workflow_context_manager.validate_context(context, ["name"]))
        self.assertFalse(workflow_context_manager.validate_context(context, ["name", "address"]))
        
        # Test serialize_context and deserialize_context
        serialized = workflow_context_manager.serialize_context(context)
        self.assertIsInstance(serialized, str)
        
        deserialized = workflow_context_manager.deserialize_context(serialized)
        self.assertEqual(deserialized["name"], "John")
        self.assertEqual(deserialized["age"], 30)
        self.assertEqual(deserialized["email"], "john@example.com")


if __name__ == "__main__":
    unittest.main()
