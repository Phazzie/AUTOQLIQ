"""Template handler implementation.

This module implements the handler for template actions.
"""

import logging
from typing import Dict, Any, List

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.exceptions import ActionError, WorkflowError, RepositoryError
from src.core.actions.template_action import TemplateAction
from src.core.actions.factory import ActionFactory
from src.core.workflow.control_flow.base import ControlFlowHandlerBase

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
        self.action_factory = ActionFactory()
    
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
            
        Raises:
            ActionError: If an error occurs during handling
            WorkflowError: If action is not a TemplateAction or workflow_repo is None
        """
        if not isinstance(action, TemplateAction):
            raise WorkflowError(f"TemplateHandler received non-TemplateAction: {type(action).__name__}")
        
        if not self.workflow_repo:
            raise WorkflowError(
                f"Cannot expand template '{action.template_name}': No workflow repository available",
                workflow_name=workflow_name
            )
        
        try:
            # Load the template actions
            logger.info(f"{log_prefix}Expanding template '{action.template_name}'")
            template_actions = self._load_template(action.template_name)
            
            if not template_actions:
                logger.warning(f"{log_prefix}Template '{action.template_name}' is empty")
                return ActionResult.success(f"Template '{action.template_name}' expanded to 0 actions")
            
            # Apply parameter substitutions if any
            if action.parameters:
                template_actions = self._apply_parameters(template_actions, action.parameters)
            
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
                
        except RepositoryError as e:
            raise ActionError(
                f"Failed to load template '{action.template_name}': {e}",
                action_name=action.name,
                action_type=action.action_type,
                cause=e
            ) from e
        except ActionError as e:
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
    
    def _load_template(self, template_name: str) -> List[IAction]:
        """
        Load a template from the workflow repository.
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            List[IAction]: The actions in the template
            
        Raises:
            RepositoryError: If the template cannot be loaded
        """
        try:
            return self.workflow_repo.load(template_name)
        except Exception as e:
            raise RepositoryError(
                f"Failed to load template '{template_name}': {e}",
                cause=e
            ) from e
    
    def _apply_parameters(self, actions: List[IAction], parameters: Dict[str, Any]) -> List[IAction]:
        """
        Apply parameter substitutions to template actions.
        
        Args:
            actions: The actions to apply parameters to
            parameters: The parameters to apply
            
        Returns:
            List[IAction]: The actions with parameters applied
            
        Raises:
            ActionError: If parameter substitution fails
        """
        # Serialize actions to dictionaries
        action_dicts = [action.to_dict() for action in actions]
        
        # Apply parameter substitutions to serialized actions
        for action_dict in action_dicts:
            self._substitute_parameters_in_dict(action_dict, parameters)
        
        # Deserialize back to actions
        try:
            return [self.action_factory.create_action(action_dict) for action_dict in action_dicts]
        except Exception as e:
            raise ActionError(f"Failed to apply template parameters: {e}", cause=e) from e
    
    def _substitute_parameters_in_dict(self, data: Dict[str, Any], parameters: Dict[str, Any]) -> None:
        """
        Recursively substitute parameters in a dictionary.
        
        Args:
            data: The dictionary to apply substitutions to
            parameters: The parameters to apply
        """
        for key, value in data.items():
            if isinstance(value, str):
                # Replace {{param}} with parameters["param"]
                for param_name, param_value in parameters.items():
                    placeholder = f"{{{{{param_name}}}}}"
                    if placeholder in value:
                        data[key] = value.replace(placeholder, str(param_value))
            elif isinstance(value, dict):
                self._substitute_parameters_in_dict(value, parameters)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._substitute_parameters_in_dict(item, parameters)
                    elif isinstance(item, str):
                        for param_name, param_value in parameters.items():
                            placeholder = f"{{{{{param_name}}}}}"
                            if placeholder in item:
                                value[i] = item.replace(placeholder, str(param_value))
