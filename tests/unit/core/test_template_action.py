"""Unit tests for the TemplateAction."""

import unittest
from unittest.mock import MagicMock

# Assuming correct paths for imports
from src.core.actions.template_action import TemplateAction
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ValidationError

class TestTemplateAction(unittest.TestCase):
    """Tests for TemplateAction."""

    def test_init_success(self):
        """Test successful initialization."""
        action = TemplateAction(name="UseMyTemplate", template_name="my_template")
        self.assertEqual(action.name, "UseMyTemplate")
        self.assertEqual(action.template_name, "my_template")
        self.assertEqual(action.action_type, "Template")

    def test_init_default_name(self):
         """Test name defaults correctly."""
         action = TemplateAction(template_name="my_template")
         self.assertEqual(action.name, "Template: my_template") # Check default name format

    def test_init_missing_template_name(self):
        """Test error if template_name is missing."""
        with self.assertRaisesRegex(ValidationError, "template_name is required"): TemplateAction(name="MissingTmpl")
        with self.assertRaisesRegex(ValidationError, "template_name is required"): TemplateAction(template_name="")
        with self.assertRaisesRegex(ValidationError, "template_name is required"): TemplateAction(template_name=None) # type: ignore

    def test_validate_success(self):
        """Test validation passes with valid name and template_name."""
        action = TemplateAction(name="Valid", template_name="tmpl_name"); self.assertTrue(action.validate())

    def test_validate_fails_invalid_name(self):
        """Test validation fails with invalid base name."""
        action = TemplateAction(template_name="tmpl"); action.name = ""
        with self.assertRaisesRegex(ValidationError, "Action name must be a non-empty string"): action.validate()

    def test_validate_fails_invalid_template_name(self):
        """Test validation fails with invalid template name."""
        action = TemplateAction(template_name="tmpl"); action.template_name = ""
        with self.assertRaisesRegex(ValidationError, "template_name is required"): action.validate()

    def test_execute_returns_success_and_logs_warning(self):
        """Test execute does nothing but returns success and logs."""
        action = TemplateAction(template_name="tmpl"); mock_driver = MagicMock(); mock_repo = MagicMock(); mock_context = {}
        with self.assertLogs(level='WARNING') as log: result = action.execute(mock_driver, mock_repo, mock_context)
        self.assertTrue(result.is_success()); self.assertIn("execute method called directly", log.output[0])
        self.assertIn("Expansion should happen", log.output[0]); self.assertIn("Placeholder for template 'tmpl'", result.message)
        mock_driver.mock_calls = []

    def test_to_dict(self):
        """Test serialization to dictionary."""
        action = TemplateAction(name="MyPlaceholder", template_name="the_real_deal")
        expected = {"type": "Template", "name": "MyPlaceholder", "template_name": "the_real_deal"}
        self.assertEqual(action.to_dict(), expected)

    def test_get_nested_actions_returns_empty(self):
         """Test get_nested_actions returns an empty list."""
         action = TemplateAction(template_name="tmpl"); self.assertEqual(action.get_nested_actions(), [])

    def test_str_representation(self):
        """Test the user-friendly string representation."""
        action = TemplateAction(name="Run Setup", template_name="common_setup")
        self.assertEqual(str(action), "Template: Run Setup (Uses Template: 'common_setup')")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)