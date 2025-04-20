"""Tests for advanced action implementations.

This module tests the ConditionalAction, LoopAction, ErrorHandlingAction, and TemplateAction classes.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import ValidationError

class TestConditionalAction(unittest.TestCase):
    """Test case for ConditionalAction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MagicMock()
        self.context = {}
    
    def test_validate_element_present(self):
        """Test validation for element_present condition."""
        # Valid
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="element_present",
            selector="#test",
            true_branch=[],
            false_branch=[]
        )
        action.validate()  # Should not raise
        
        # Invalid - missing selector
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="element_present",
            true_branch=[],
            false_branch=[]
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_validate_variable_equals(self):
        """Test validation for variable_equals condition."""
        # Valid
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="variable_equals",
            variable_name="test_var",
            expected_value="test_value",
            true_branch=[],
            false_branch=[]
        )
        action.validate()  # Should not raise
        
        # Invalid - missing variable_name
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="variable_equals",
            expected_value="test_value",
            true_branch=[],
            false_branch=[]
        )
        with self.assertRaises(ValidationError):
            action.validate()
        
        # Invalid - missing expected_value
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="variable_equals",
            variable_name="test_var",
            true_branch=[],
            false_branch=[]
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_execute_element_present_true(self):
        """Test execution with element_present condition that evaluates to true."""
        # Mock driver.element_exists to return True
        self.driver.element_exists.return_value = True
        
        # Create action
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="element_present",
            selector="#test",
            true_branch=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ],
            false_branch=[]
        )
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.name = "Navigate Action"
        mock_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
            # Execute action
            result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 1)
        self.assertEqual(result.sub_results[0].action_name, "Navigate Action")
        
        # Verify driver.element_exists was called with correct selector
        self.driver.element_exists.assert_called_once_with("#test")
    
    def test_execute_element_present_false(self):
        """Test execution with element_present condition that evaluates to false."""
        # Mock driver.element_exists to return False
        self.driver.element_exists.return_value = False
        
        # Create action
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="element_present",
            selector="#test",
            true_branch=[],
            false_branch=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.name = "Navigate Action"
        mock_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
            # Execute action
            result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 1)
        self.assertEqual(result.sub_results[0].action_name, "Navigate Action")
        
        # Verify driver.element_exists was called with correct selector
        self.driver.element_exists.assert_called_once_with("#test")
    
    def test_execute_variable_equals_true(self):
        """Test execution with variable_equals condition that evaluates to true."""
        # Set variable in context
        context = {"test_var": "test_value"}
        
        # Create action
        action = ConditionalAction(
            name="Test Conditional",
            condition_type="variable_equals",
            variable_name="test_var",
            expected_value="test_value",
            true_branch=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ],
            false_branch=[]
        )
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.name = "Navigate Action"
        mock_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
            # Execute action
            result = action.execute(self.driver, context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 1)
        self.assertEqual(result.sub_results[0].action_name, "Navigate Action")

class TestLoopAction(unittest.TestCase):
    """Test case for LoopAction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MagicMock()
        self.context = {}
    
    def test_validate_count(self):
        """Test validation for count loop."""
        # Valid
        action = LoopAction(
            name="Test Loop",
            loop_type="count",
            count=5,
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        action.validate()  # Should not raise
        
        # Invalid - negative count
        action = LoopAction(
            name="Test Loop",
            loop_type="count",
            count=-1,
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        with self.assertRaises(ValidationError):
            action.validate()
        
        # Invalid - empty loop_actions
        action = LoopAction(
            name="Test Loop",
            loop_type="count",
            count=5,
            loop_actions=[]
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_validate_for_each(self):
        """Test validation for for_each loop."""
        # Valid
        action = LoopAction(
            name="Test Loop",
            loop_type="for_each",
            list_variable_name="test_list",
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        action.validate()  # Should not raise
        
        # Invalid - missing list_variable_name
        action = LoopAction(
            name="Test Loop",
            loop_type="for_each",
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_execute_count(self):
        """Test execution with count loop."""
        # Create action
        action = LoopAction(
            name="Test Loop",
            loop_type="count",
            count=3,
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.name = "Navigate Action"
        mock_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
            # Execute action
            result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 3)  # 3 iterations
        
        # Verify each iteration
        for i, iteration_result in enumerate(result.sub_results):
            self.assertEqual(iteration_result.action_name, f"Test Loop (Iteration {i+1})")
            self.assertEqual(iteration_result.status, ActionStatus.SUCCESS)
            self.assertEqual(len(iteration_result.sub_results), 1)
            self.assertEqual(iteration_result.sub_results[0].action_name, "Navigate Action")
        
        # Verify mock_action.execute was called 3 times
        self.assertEqual(mock_action.execute.call_count, 3)
    
    def test_execute_for_each(self):
        """Test execution with for_each loop."""
        # Set list in context
        context = {"test_list": ["item1", "item2", "item3"]}
        
        # Create action
        action = LoopAction(
            name="Test Loop",
            loop_type="for_each",
            list_variable_name="test_list",
            loop_variable_name="current_item",
            loop_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ]
        )
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.name = "Navigate Action"
        mock_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
            # Execute action
            result = action.execute(self.driver, context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 3)  # 3 items in list
        
        # Verify each iteration
        for i, iteration_result in enumerate(result.sub_results):
            self.assertEqual(iteration_result.action_name, f"Test Loop (Iteration {i+1})")
            self.assertEqual(iteration_result.status, ActionStatus.SUCCESS)
            self.assertEqual(len(iteration_result.sub_results), 1)
            self.assertEqual(iteration_result.sub_results[0].action_name, "Navigate Action")
        
        # Verify mock_action.execute was called 3 times
        self.assertEqual(mock_action.execute.call_count, 3)
        
        # Verify context was updated correctly for each iteration
        expected_contexts = [
            {"test_list": ["item1", "item2", "item3"], "current_item": "item1", "loop_index": 0},
            {"test_list": ["item1", "item2", "item3"], "current_item": "item2", "loop_index": 1},
            {"test_list": ["item1", "item2", "item3"], "current_item": "item3", "loop_index": 2}
        ]
        
        for i, call_args in enumerate(mock_action.execute.call_args_list):
            _, call_context = call_args[0]
            self.assertEqual(call_context["current_item"], expected_contexts[i]["current_item"])
            self.assertEqual(call_context["loop_index"], expected_contexts[i]["loop_index"])

class TestErrorHandlingAction(unittest.TestCase):
    """Test case for ErrorHandlingAction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MagicMock()
        self.context = {}
    
    def test_validate(self):
        """Test validation."""
        # Valid
        action = ErrorHandlingAction(
            name="Test Error Handling",
            try_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ],
            catch_actions=[
                {"type": "Navigate", "name": "Error Action", "url": "https://error.com"}
            ]
        )
        action.validate()  # Should not raise
        
        # Invalid - empty try_actions
        action = ErrorHandlingAction(
            name="Test Error Handling",
            try_actions=[],
            catch_actions=[
                {"type": "Navigate", "name": "Error Action", "url": "https://error.com"}
            ]
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_execute_success(self):
        """Test execution with successful try block."""
        # Create action
        action = ErrorHandlingAction(
            name="Test Error Handling",
            try_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ],
            catch_actions=[
                {"type": "Navigate", "name": "Error Action", "url": "https://error.com"}
            ]
        )
        
        # Mock ActionFactory.create_action for try block
        mock_try_action = MagicMock()
        mock_try_action.name = "Navigate Action"
        mock_try_action.execute.return_value = ActionResult(
            action_name="Navigate Action",
            status=ActionStatus.SUCCESS,
            message="Navigation successful"
        )
        
        with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_try_action):
            # Execute action
            result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 1)  # Only try block executed
        self.assertEqual(result.sub_results[0].action_name, "Test Error Handling (Try)")
        self.assertEqual(result.sub_results[0].status, ActionStatus.SUCCESS)
        
        # Verify mock_try_action.execute was called once
        mock_try_action.execute.assert_called_once()
    
    def test_execute_failure(self):
        """Test execution with failing try block."""
        # Create action
        action = ErrorHandlingAction(
            name="Test Error Handling",
            try_actions=[
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com"}
            ],
            catch_actions=[
                {"type": "Navigate", "name": "Error Action", "url": "https://error.com"}
            ]
        )
        
        # Mock ActionFactory.create_action for try and catch blocks
        def mock_create_action(action_data):
            if action_data["name"] == "Navigate Action":
                mock_action = MagicMock()
                mock_action.name = "Navigate Action"
                mock_action.execute.return_value = ActionResult(
                    action_name="Navigate Action",
                    status=ActionStatus.FAILURE,
                    message="Navigation failed"
                )
                return mock_action
            else:
                mock_action = MagicMock()
                mock_action.name = "Error Action"
                mock_action.execute.return_value = ActionResult(
                    action_name="Error Action",
                    status=ActionStatus.SUCCESS,
                    message="Error handled"
                )
                return mock_action
        
        with patch("src.core.actions.factory.ActionFactory.create_action", side_effect=mock_create_action):
            # Execute action
            result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 2)  # Both try and catch blocks executed
        
        # Verify try block result
        self.assertEqual(result.sub_results[0].action_name, "Test Error Handling (Try)")
        self.assertEqual(result.sub_results[0].status, ActionStatus.FAILURE)
        
        # Verify catch block result
        self.assertEqual(result.sub_results[1].action_name, "Test Error Handling (Catch)")
        self.assertEqual(result.sub_results[1].status, ActionStatus.SUCCESS)

class TestTemplateAction(unittest.TestCase):
    """Test case for TemplateAction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MagicMock()
        self.context = {}
    
    def test_validate(self):
        """Test validation."""
        # Valid
        action = TemplateAction(
            name="Test Template",
            template_name="login_template",
            parameters={"username": "test_user", "password": "test_pass"}
        )
        action.validate()  # Should not raise
        
        # Invalid - missing template_name
        action = TemplateAction(
            name="Test Template",
            parameters={"username": "test_user", "password": "test_pass"}
        )
        with self.assertRaises(ValidationError):
            action.validate()
    
    def test_execute(self):
        """Test execution."""
        # Create action
        action = TemplateAction(
            name="Test Template",
            template_name="login_template",
            parameters={"username": "test_user", "password": "test_pass"}
        )
        
        # Mock template repository
        mock_template = {
            "name": "login_template",
            "description": "Login template",
            "actions": [
                {"type": "Navigate", "name": "Navigate Action", "url": "https://example.com/login"},
                {"type": "Type", "name": "Type Username", "selector": "#username", "value": "{{username}}"},
                {"type": "Type", "name": "Type Password", "selector": "#password", "value": "{{password}}"},
                {"type": "Click", "name": "Click Login", "selector": "#login-button"}
            ]
        }
        
        mock_repository = MagicMock()
        mock_repository.get_template.return_value = mock_template
        
        # Mock ActionFactory.create_action
        mock_action = MagicMock()
        mock_action.execute.return_value = ActionResult(
            action_name="Mock Action",
            status=ActionStatus.SUCCESS,
            message="Action successful"
        )
        
        with patch("src.core.template.repository.TemplateRepository", return_value=mock_repository):
            with patch("src.core.actions.factory.ActionFactory.create_action", return_value=mock_action):
                # Execute action
                result = action.execute(self.driver, self.context)
        
        # Verify result
        self.assertEqual(result.status, ActionStatus.SUCCESS)
        self.assertEqual(len(result.sub_results), 4)  # 4 actions in template
        
        # Verify template repository was called
        mock_repository.get_template.assert_called_once_with("login_template")
        
        # Verify ActionFactory.create_action was called 4 times
        self.assertEqual(mock_action.execute.call_count, 4)
        
        # Verify parameters were passed to context
        for i, call_args in enumerate(mock_action.execute.call_args_list):
            _, call_context = call_args[0]
            self.assertEqual(call_context["username"], "test_user")
            self.assertEqual(call_context["password"], "test_pass")

if __name__ == "__main__":
    unittest.main()
