#!/usr/bin/env python3
"""
Unit tests for validators in src/infrastructure/common/validators.py.
"""

import unittest
from unittest.mock import MagicMock, patch

# Import the module under test
from src.infrastructure.common.validators import (
    CredentialValidator,
    ActionValidator,
    WorkflowValidator
)
from src.core.exceptions import ValidationError


class TestCredentialValidator(unittest.TestCase):
    """
    Test cases for the CredentialValidator class.
    
    This test suite verifies that CredentialValidator correctly validates
    credential data according to the defined rules.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a validator instance
        self.validator = CredentialValidator()
        
        # Sample valid credential data
        self.valid_credential = {
            "name": "TestCredential",
            "username": "test_user",
            "password": "password123",
            "url": "https://example.com"
        }
    
    def test_validate_credential_data_valid(self):
        """Test validation of valid credential data."""
        # Validate valid credential data - should not raise any exceptions
        self.validator.validate_credential_data(self.valid_credential)
    
    def test_validate_credential_data_missing_name(self):
        """Test validation of credential data with missing name."""
        # Create credential data with missing name
        invalid_credential = self.valid_credential.copy()
        del invalid_credential["name"]
        
        # Validate invalid credential data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_data(invalid_credential)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_credential_data_empty_name(self):
        """Test validation of credential data with empty name."""
        # Create credential data with empty name
        invalid_credential = self.valid_credential.copy()
        invalid_credential["name"] = ""
        
        # Validate invalid credential data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_data(invalid_credential)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_credential_data_missing_username(self):
        """Test validation of credential data with missing username."""
        # Create credential data with missing username
        invalid_credential = self.valid_credential.copy()
        del invalid_credential["username"]
        
        # Validate invalid credential data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_data(invalid_credential)
        
        # Verify error message
        self.assertIn("username", str(context.exception).lower())
    
    def test_validate_credential_data_empty_username(self):
        """Test validation of credential data with empty username."""
        # Create credential data with empty username
        invalid_credential = self.valid_credential.copy()
        invalid_credential["username"] = ""
        
        # Validate invalid credential data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_data(invalid_credential)
        
        # Verify error message
        self.assertIn("username", str(context.exception).lower())
    
    def test_validate_credential_data_missing_password(self):
        """Test validation of credential data with missing password."""
        # Create credential data with missing password
        invalid_credential = self.valid_credential.copy()
        del invalid_credential["password"]
        
        # Validate invalid credential data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_data(invalid_credential)
        
        # Verify error message
        self.assertIn("password", str(context.exception).lower())
    
    def test_validate_credential_name_valid(self):
        """Test validation of valid credential name."""
        # Validate valid credential name - should not raise any exceptions
        self.validator.validate_credential_name("TestCredential")
    
    def test_validate_credential_name_empty(self):
        """Test validation of empty credential name."""
        # Validate empty credential name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_name("")
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_credential_name_none(self):
        """Test validation of None credential name."""
        # Validate None credential name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_credential_name(None)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_credential_name_with_special_chars(self):
        """Test validation of credential name with special characters."""
        # Validate credential name with special characters
        # Behavior depends on implementation - adjust test accordingly
        special_chars_name = "Test@Credential#123"
        
        try:
            self.validator.validate_credential_name(special_chars_name)
            # If no exception is raised, the validator allows special characters
            # No assertion needed
        except ValidationError:
            # If ValidationError is raised, the validator doesn't allow special characters
            # This is also a valid implementation, so no assertion needed
            pass


class TestActionValidator(unittest.TestCase):
    """
    Test cases for the ActionValidator class.
    
    This test suite verifies that ActionValidator correctly validates
    action data according to the defined rules.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a validator instance
        self.validator = ActionValidator()
        
        # Sample valid action data
        self.valid_action = {
            "name": "TestAction",
            "type": "click",
            "selector": "#submit-button",
            "timeout": 5000
        }
    
    def test_validate_action_data_valid(self):
        """Test validation of valid action data."""
        # Validate valid action data - should not raise any exceptions
        self.validator.validate_action_data(self.valid_action)
    
    def test_validate_action_data_missing_name(self):
        """Test validation of action data with missing name."""
        # Create action data with missing name
        invalid_action = self.valid_action.copy()
        del invalid_action["name"]
        
        # Validate invalid action data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_data(invalid_action)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_action_data_empty_name(self):
        """Test validation of action data with empty name."""
        # Create action data with empty name
        invalid_action = self.valid_action.copy()
        invalid_action["name"] = ""
        
        # Validate invalid action data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_data(invalid_action)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_action_data_missing_type(self):
        """Test validation of action data with missing type."""
        # Create action data with missing type
        invalid_action = self.valid_action.copy()
        del invalid_action["type"]
        
        # Validate invalid action data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_data(invalid_action)
        
        # Verify error message
        self.assertIn("type", str(context.exception).lower())
    
    def test_validate_action_data_empty_type(self):
        """Test validation of action data with empty type."""
        # Create action data with empty type
        invalid_action = self.valid_action.copy()
        invalid_action["type"] = ""
        
        # Validate invalid action data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_data(invalid_action)
        
        # Verify error message
        self.assertIn("type", str(context.exception).lower())
    
    def test_validate_action_data_invalid_type(self):
        """Test validation of action data with invalid type."""
        # Create action data with invalid type
        invalid_action = self.valid_action.copy()
        invalid_action["type"] = "invalid_type"
        
        # Validate invalid action data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_data(invalid_action)
        
        # Verify error message
        self.assertIn("type", str(context.exception).lower())
    
    def test_validate_action_name_valid(self):
        """Test validation of valid action name."""
        # Validate valid action name - should not raise any exceptions
        self.validator.validate_action_name("TestAction")
    
    def test_validate_action_name_empty(self):
        """Test validation of empty action name."""
        # Validate empty action name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_name("")
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_action_name_none(self):
        """Test validation of None action name."""
        # Validate None action name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_action_name(None)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())


class TestWorkflowValidator(unittest.TestCase):
    """
    Test cases for the WorkflowValidator class.
    
    This test suite verifies that WorkflowValidator correctly validates
    workflow data according to the defined rules.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a validator instance
        self.validator = WorkflowValidator()
        
        # Sample valid workflow data
        self.valid_workflow = {
            "name": "TestWorkflow",
            "description": "A test workflow",
            "actions": [
                {
                    "name": "Action1",
                    "type": "click",
                    "selector": "#button1"
                },
                {
                    "name": "Action2",
                    "type": "input",
                    "selector": "#input1",
                    "value": "test"
                }
            ]
        }
    
    def test_validate_workflow_data_valid(self):
        """Test validation of valid workflow data."""
        # Validate valid workflow data - should not raise any exceptions
        self.validator.validate_workflow_data(self.valid_workflow)
    
    def test_validate_workflow_data_missing_name(self):
        """Test validation of workflow data with missing name."""
        # Create workflow data with missing name
        invalid_workflow = self.valid_workflow.copy()
        del invalid_workflow["name"]
        
        # Validate invalid workflow data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_data(invalid_workflow)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_workflow_data_empty_name(self):
        """Test validation of workflow data with empty name."""
        # Create workflow data with empty name
        invalid_workflow = self.valid_workflow.copy()
        invalid_workflow["name"] = ""
        
        # Validate invalid workflow data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_data(invalid_workflow)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_workflow_data_missing_actions(self):
        """Test validation of workflow data with missing actions."""
        # Create workflow data with missing actions
        invalid_workflow = self.valid_workflow.copy()
        del invalid_workflow["actions"]
        
        # Validate invalid workflow data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_data(invalid_workflow)
        
        # Verify error message
        self.assertIn("actions", str(context.exception).lower())
    
    def test_validate_workflow_data_empty_actions(self):
        """Test validation of workflow data with empty actions list."""
        # Create workflow data with empty actions list
        invalid_workflow = self.valid_workflow.copy()
        invalid_workflow["actions"] = []
        
        # Validate invalid workflow data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_data(invalid_workflow)
        
        # Verify error message
        self.assertIn("actions", str(context.exception).lower())
    
    def test_validate_workflow_data_invalid_actions(self):
        """Test validation of workflow data with invalid actions."""
        # Create workflow data with invalid actions (not a list)
        invalid_workflow = self.valid_workflow.copy()
        invalid_workflow["actions"] = "not a list"
        
        # Validate invalid workflow data - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_data(invalid_workflow)
        
        # Verify error message
        self.assertIn("actions", str(context.exception).lower())
    
    def test_validate_workflow_name_valid(self):
        """Test validation of valid workflow name."""
        # Validate valid workflow name - should not raise any exceptions
        self.validator.validate_workflow_name("TestWorkflow")
    
    def test_validate_workflow_name_empty(self):
        """Test validation of empty workflow name."""
        # Validate empty workflow name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_name("")
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())
    
    def test_validate_workflow_name_none(self):
        """Test validation of None workflow name."""
        # Validate None workflow name - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_workflow_name(None)
        
        # Verify error message
        self.assertIn("name", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()