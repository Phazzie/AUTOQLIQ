"""Tests for the ActionBase abstract class."""

import unittest
from unittest.mock import MagicMock, patch
import logging
import pytest  # type: ignore

from src.core.actions.base import ActionBase
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError


# Concrete implementation of ActionBase for testing
class ConcreteAction(ActionBase):
    """Concrete implementation of ActionBase for testing."""
    
    action_type = "ConcreteTest"
    
    def __init__(self, name=None, test_param=None, **kwargs):
        """Initialize with test parameters."""
        self.test_param = test_param
        super().__init__(name=name, **kwargs)
    
    def execute(self, driver, credential_repo=None, context=None):
        """Implement abstract method."""
        # Just return a simple success for testing
        return ActionResult.success(f"Test execution of {self.name}")
    
    def to_dict(self):
        """Implement abstract method."""
        return {
            "type": self.action_type,
            "name": self.name,
            "test_param": self.test_param
        }
    
    def validate(self):
        """Override validate to add parameter checks."""
        super().validate()  # Call base validation first
        if self.test_param is not None and not isinstance(self.test_param, str):
            raise ValidationError("test_param must be a string if provided", field_name="test_param")
        return True


# Dummy subclass for testing
class DummyAction(ActionBase):
    action_type = "Dummy"

    def __init__(self, name=None):
        super().__init__(name or self.action_type)

    def execute(self, driver):
        return ActionResult.success("ok")

    def to_dict(self):
        return {"type": self.action_type, "name": self.name}


def test_validate_success():
    action = DummyAction("TestAction")
    assert action.validate() is True


def test_init_empty_name_raises():
    with pytest.raises(ValidationError):
        DummyAction("")


def test_execute_returns_success():
    action = DummyAction()
    result = action.execute(None)
    assert isinstance(result, ActionResult)
    assert result.is_success()


class TestActionBase(unittest.TestCase):
    """Test cases for the ActionBase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Capture logs for testing
        self.log_capture = MagicMock()
        self.log_patcher = patch('src.core.actions.base.logger')
        self.mock_logger = self.log_patcher.start()
        
        # Create mock objects
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.log_patcher.stop()

    def test_init_with_name(self):
        """Test initialization with a name."""
        action = ConcreteAction(name="TestAction")
        self.assertEqual(action.name, "TestAction")
        self.assertEqual(action.action_type, "ConcreteTest")
    
    def test_init_without_name_uses_action_type(self):
        """Test initialization without a name uses action_type as default."""
        action = ConcreteAction()
        self.assertEqual(action.name, "ConcreteTest")
    
    def test_init_with_empty_name_uses_default(self):
        """Test initialization with empty string uses action_type as default."""
        action = ConcreteAction(name="  ")  # Whitespace name
        self.assertEqual(action.name, "ConcreteTest")
        self.mock_logger.warning.assert_called_once()  # Should log a warning
    
    def test_init_stores_unused_kwargs(self):
        """Test initialization stores unused kwargs."""
        action = ConcreteAction(name="Test", unused_param=123)
        self.assertEqual(action._unused_kwargs, {"unused_param": 123})
        self.mock_logger.warning.assert_called_once()  # Should log a warning about unused params
    
    def test_validate_with_valid_name(self):
        """Test validation passes with valid name."""
        action = ConcreteAction(name="Valid")
        self.assertTrue(action.validate())
    
    def test_validate_with_empty_name_raises_error(self):
        """Test validation fails with empty name."""
        # Create with valid name but then force invalid state
        action = ConcreteAction(name="Valid")
        action.name = ""
        
        with self.assertRaises(ValidationError) as context:
            action.validate()
        
        self.assertIn("name", str(context.exception).lower())
    
    def test_inherited_validate_checks_parameters(self):
        """Test that inherited validate method checks additional parameters."""
        # This should pass
        action = ConcreteAction(name="Test", test_param="valid_string")
        self.assertTrue(action.validate())
        
        # This should fail - invalid test_param type
        action = ConcreteAction(name="Test", test_param=123)
        with self.assertRaises(ValidationError) as context:
            action.validate()
        
        self.assertIn("test_param", str(context.exception))
    
    def test_missing_action_type_raises_error(self):
        """Test that missing action_type raises NotImplementedError."""
        # Create a new class without overriding action_type
        class BadAction(ActionBase):
            action_type = "Base"  # Same as parent, which is not allowed
            
            def execute(self, driver, credential_repo=None, context=None):
                return ActionResult.success()
                
            def to_dict(self):
                return {}
        
        with self.assertRaises(NotImplementedError) as context:
            BadAction()
        
        self.assertIn("action_type", str(context.exception))
    
    def test_execute_is_abstract(self):
        """Test that execute method must be implemented."""
        # Should not be able to instantiate ActionBase directly
        with self.assertRaises(TypeError):
            ActionBase(name="TestBase")  # type: ignore
    
    def test_to_dict_is_abstract(self):
        """Test that to_dict method must be implemented."""
        # Create a class with execute but no to_dict
        class IncompleteAction(ActionBase):
            action_type = "Incomplete"
            
            def execute(self, driver, credential_repo=None, context=None):
                return ActionResult.success()
        
        # Should not be able to instantiate
        with self.assertRaises(TypeError):
            IncompleteAction(name="TestIncomplete")


if __name__ == "__main__":
    unittest.main()
