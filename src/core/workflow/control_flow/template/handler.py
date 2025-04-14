"""Template handler implementation.

This module implements the handler for template actions.
"""

import logging
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError, RepositoryError
from src.core.actions.template_action import TemplateAction
from src.core.workflow.control_flow.base import ControlFlowHandlerBase
from src.core.workflow.control_flow.template.loader import TemplateLoader
from src.core.workflow.control_flow.template.parameter_substitutor import ParameterSubstitutor

logger = logging.getLogger(__name__)


class TemplateHandler(ControlFlowHandlerBase):
    """Handler for TemplateAction expansion and execution."""
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the template handler.
        
        Args:
            *args: Arguments to pass to the parent constructor
            **kwargs: Keyword arguments to pass to the parent constructor
        """
        super().__init__(*args, **kwargs)
        self.parameter_substitutor = ParameterSubstitutor()
        self.template_loader = None
        if self.workflow_repo:
            self.template_loader = TemplateLoader(self.workflow_repo)
    
    def handle(self, action: IAction, context: Dict[str, Any], 
              workflow_name: str, log_prefix: str) -> ActionResult:
        """
        Handle a TemplateAction by expanding it and executing the resulting actions.
        
        Args:
            action: The TemplateAction to handle
            context: The execution context
            workflow_name: Name of the workflow being executed
            log_prefix: Prefix for log messages
            
        Returns:
            ActionResult: The result of handling the action
        """
        if not isinstance(action, TemplateAction):
            raise WorkflowError(f"TemplateHandler received non-TemplateAction: {type(action).__name__}")
        
        if not self.workflow_repo or not self.template_loader:
            raise WorkflowError(
                f"Cannot expand template '{action.template_name}': No workflow repository available",
                workflow_name=workflow_name
            )
        
        try:
            return self._process_template(action, context, workflow_name, log_prefix)
        except RepositoryError as e:
            raise ActionError(
                f"Failed to load template '{action.template_name}': {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            ) from e
        except ActionError:
            # Let the runner's error handling strategy deal with this
            raise
        except Exception as e:
            # Wrap other exceptions in ActionError
            raise ActionError(
                f"Error expanding template '{action.template_name}': {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            ) from e
    
    def _process_template(self, action: TemplateAction, context: Dict[str, Any],
                         workflow_name: str, log_prefix: str) -> ActionResult:
        """Process a template action."""
        # Load the template actions
        logger.info(f"{log_prefix}Expanding template '{action.template_name}'")
        template_actions = self.template_loader.load_template(action.template_name)
        
        if not template_actions:
            logger.warning(f"{log_prefix}Template '{action.template_name}' is empty")
            return ActionResult.success(f"Template '{action.template_name}' expanded to 0 actions")
        
        # Apply parameter substitutions if any
        if action.parameters:
            template_actions = self.parameter_substitutor.apply_parameters(
                template_actions, action.parameters
            )
        
        # Execute the expanded template actions
        template_prefix = f"{log_prefix}Template '{action.template_name}': "
        template_results = self.execute_actions(
            template_actions, context, workflow_name, template_prefix
        )
        
        # Return success if all template actions succeeded
        all_success = all(result.is_success() for result in template_results)
        if all_success:
            return ActionResult.success(
                f"Template '{action.template_name}' executed successfully ({len(template_results)} actions)"
            )
        else:
            # If we got here with failures, we must be using CONTINUE_ON_ERROR
            return ActionResult.failure(
                f"Template '{action.template_name}' had failures ({len(template_results)} actions)"
            )
