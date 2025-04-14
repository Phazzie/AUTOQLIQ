"""Tests for template expander."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import ActionError
from src.core.actions.template_action import TemplateAction
from src.core.workflow.template_expander import expand_template


class TestTemplateExpander(unittest.TestCase):
    """Test cases for template expander."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_workflow_repo = MagicMock(spec=IWorkflowRepository)
        
        self.mock_template_action = MagicMock(spec=TemplateAction)
        self.mock_template_action.name = "TestTemplate"
        self.mock_template_action.action_type = "template"
        self.mock_template_action.template_name = "test_template"
        self.mock_template_action.parameters = {"param1": "value1", "param2": "value2"}
        
        self.mock_action_data = [
            {"name": "Action1", "action_type": "test", "param": "{{param1}}"},
            {"name": "Action2", "action_type": "test", "param": "{{param2}}"}
        ]
        
        self.mock_workflow_repo.load_template.return_value = self.mock_action_data

    def test_expand_template_success(self):
        """Test expanding a template successfully."""
        with patch("src.core.actions.factory.ActionFactory.create_action") as mock_create_action:
            mock_action1 = MagicMock(spec=IAction)
            mock_action2 = MagicMock(spec=IAction)
            mock_create_action.side_effect = [mock_action1, mock_action2]
            
            with patch("src.core.workflow.control_flow.template.parameter_substitutor.ParameterSubstitutor") as mock_substitutor_class:
                mock_substitutor = MagicMock()
                mock_substitutor_class.return_value = mock_substitutor
                mock_substitutor.apply_parameters.return_value = [mock_action1, mock_action2]
                
                result = expand_template(self.mock_template_action, self.mock_workflow_repo)
                
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0], mock_action1)
                self.assertEqual(result[1], mock_action2)
                
                self.mock_workflow_repo.load_template.assert_called_once_with("test_template")
                mock_substitutor.apply_parameters.assert_called_once()

    def test_expand_template_no_workflow_repo(self):
        """Test expanding a template with no workflow repository."""
        with self.assertRaises(ActionError):
            expand_template(self.mock_template_action, None)

    def test_expand_template_not_template_action(self):
        """Test expanding a non-template action."""
        mock_action = MagicMock(spec=IAction)
        mock_action.name = "TestAction"
        mock_action.action_type = "test"
        
        with self.assertRaises(ActionError):
            expand_template(mock_action, self.mock_workflow_repo)

    def test_expand_template_empty_template(self):
        """Test expanding an empty template."""
        self.mock_workflow_repo.load_template.return_value = []
        
        result = expand_template(self.mock_template_action, self.mock_workflow_repo)
        
        self.assertEqual(len(result), 0)
        self.mock_workflow_repo.load_template.assert_called_once_with("test_template")

    def test_expand_template_load_error(self):
        """Test expanding a template with a load error."""
        self.mock_workflow_repo.load_template.side_effect = Exception("Test error")
        
        with self.assertRaises(ActionError):
            expand_template(self.mock_template_action, self.mock_workflow_repo)


if __name__ == "__main__":
    unittest.main()
