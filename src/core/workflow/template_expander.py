"""Template expander module for AutoQliq.

Provides functionality for expanding template actions.
"""

import logging
from typing import Dict, Any, List, Optional

from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import ActionError
from src.core.actions.template_action import TemplateAction
from src.core.actions.factory import ActionFactory

logger = logging.getLogger(__name__)


def expand_template(
    action: IAction,
    workflow_repo: Optional[IWorkflowRepository]
) -> List[IAction]:
    """
    Expand a template action.
    
    Args:
        action: The template action to expand
        workflow_repo: Repository for workflows/templates
        
    Returns:
        List[IAction]: The expanded actions
        
    Raises:
        ActionError: If the template cannot be expanded
    """
    if not workflow_repo:
        error_message = "Workflow repository required for template expansion."
        raise ActionError(error_message, action_name=action.name)
    
    try:
        template_action = action
        if not isinstance(template_action, TemplateAction):
            error_message = f"Expected TemplateAction, got {type(template_action).__name__}"
            raise TypeError(error_message)
        
        template_name = template_action.template_name
        actions_data = workflow_repo.load_template(template_name)
        
        if not actions_data:
            return []
        
        expanded_actions = [ActionFactory.create_action(data) for data in actions_data]
        
        # Apply parameter substitutions if any
        if template_action.parameters:
            # Use the template handler's parameter substitutor
            from src.core.workflow.control_flow.template.parameter_substitutor import (
                ParameterSubstitutor
            )
            parameter_substitutor = ParameterSubstitutor()
            expanded_actions = parameter_substitutor.apply_parameters(
                expanded_actions, template_action.parameters
            )
        
        return expanded_actions
        
    except Exception as error:
        error_message = f"Failed to expand template: {error}"
        raise ActionError(
            error_message,
            action_name=action.name,
            cause=error
        ) from error
