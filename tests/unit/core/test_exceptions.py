import unittest
from src.core.exceptions import (
    AutoQliqError,
    WorkflowError,
    ActionError,
    ValidationError,
    CredentialError,
    WebDriverError
)


class TestExceptionHierarchy(unittest.TestCase):
    """
    Tests for the exception hierarchy to ensure proper inheritance
    and behavior of custom exceptions.
    """

    def test_base_exception_inheritance(self):
        """Test that AutoQliqError inherits from Exception."""
        self.assertTrue(issubclass(AutoQliqError, Exception))

    def test_workflow_error_inheritance(self):
        """Test that WorkflowError inherits from AutoQliqError."""
        self.assertTrue(issubclass(WorkflowError, AutoQliqError))

    def test_action_error_inheritance(self):
        """Test that ActionError inherits from AutoQliqError."""
        self.assertTrue(issubclass(ActionError, AutoQliqError))

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from AutoQliqError."""
        self.assertTrue(issubclass(ValidationError, AutoQliqError))

    def test_credential_error_inheritance(self):
        """Test that CredentialError inherits from AutoQliqError."""
        self.assertTrue(issubclass(CredentialError, AutoQliqError))

    def test_webdriver_error_inheritance(self):
        """Test that WebDriverError inherits from AutoQliqError."""
        self.assertTrue(issubclass(WebDriverError, AutoQliqError))


class TestExceptionInstantiation(unittest.TestCase):
    """
    Tests for exception instantiation and message handling.
    """

    def test_autoqliq_error_message(self):
        """Test that AutoQliqError can be instantiated with a message."""
        error = AutoQliqError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_workflow_error_message(self):
        """Test that WorkflowError can be instantiated with a message."""
        error = WorkflowError("Workflow failed")
        self.assertEqual(str(error), "Workflow failed")

    def test_action_error_message(self):
        """Test that ActionError can be instantiated with a message."""
        error = ActionError("Action failed")
        self.assertEqual(str(error), "Action failed")

    def test_validation_error_message(self):
        """Test that ValidationError can be instantiated with a message."""
        error = ValidationError("Validation failed")
        self.assertEqual(str(error), "Validation failed")

    def test_credential_error_message(self):
        """Test that CredentialError can be instantiated with a message."""
        error = CredentialError("Credential error")
        self.assertEqual(str(error), "Credential error")

    def test_webdriver_error_message(self):
        """Test that WebDriverError can be instantiated with a message."""
        error = WebDriverError("WebDriver error")
        self.assertEqual(str(error), "WebDriver error")


class TestExceptionWithContext(unittest.TestCase):
    """
    Tests for exceptions with additional context information.
    """

    def test_action_error_with_action_name(self):
        """Test that ActionError can include action name in context."""
        error = ActionError("Click failed", action_name="ClickLoginButton")
        self.assertEqual(str(error), "Click failed (action: ClickLoginButton)")
        self.assertEqual(error.action_name, "ClickLoginButton")

    def test_workflow_error_with_workflow_name(self):
        """Test that WorkflowError can include workflow name in context."""
        error = WorkflowError("Execution failed", workflow_name="LoginWorkflow")
        self.assertEqual(str(error), "Execution failed (workflow: LoginWorkflow)")
        self.assertEqual(error.workflow_name, "LoginWorkflow")

    def test_validation_error_with_field_name(self):
        """Test that ValidationError can include field name in context."""
        error = ValidationError("Value cannot be empty", field_name="username")
        self.assertEqual(str(error), "Value cannot be empty (field: username)")
        self.assertEqual(error.field_name, "username")

    def test_credential_error_with_credential_name(self):
        """Test that CredentialError can include credential name in context."""
        error = CredentialError("Not found", credential_name="login_creds")
        self.assertEqual(str(error), "Not found (credential: login_creds)")
        self.assertEqual(error.credential_name, "login_creds")

    def test_webdriver_error_with_driver_type(self):
        """Test that WebDriverError can include driver type in context."""
        error = WebDriverError("Failed to initialize", driver_type="Chrome")
        self.assertEqual(str(error), "Failed to initialize (driver: Chrome)")
        self.assertEqual(error.driver_type, "Chrome")


class TestExceptionWithCause(unittest.TestCase):
    """
    Tests for exceptions that wrap other exceptions.
    """

    def test_exception_with_cause(self):
        """Test that exceptions can wrap other exceptions."""
        original_error = ValueError("Original error")
        wrapped_error = AutoQliqError("Wrapped error", cause=original_error)

        self.assertEqual(str(wrapped_error), "Wrapped error (caused by: ValueError - Original error)")
        self.assertEqual(wrapped_error.cause, original_error)

    def test_nested_exception_causes(self):
        """Test that exceptions can have nested causes."""
        level3_error = ValueError("Level 3 error")
        level2_error = AutoQliqError("Level 2 error", cause=level3_error)
        level1_error = AutoQliqError("Level 1 error", cause=level2_error)

        expected_message = "Level 1 error (caused by: AutoQliqError - Level 2 error (caused by: ValueError - Level 3 error))"
        self.assertEqual(str(level1_error), expected_message)


if __name__ == "__main__":
    unittest.main()
