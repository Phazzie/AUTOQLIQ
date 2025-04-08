################################################################################
"""Template Action for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError

logger = logging.getLogger(__name__)


class TemplateAction(ActionBase):
    """
    Action that represents a placeholder for a saved sequence of actions (a template).

    The actual expansion of this action into its underlying sequence happens
    during workflow execution by the WorkflowRunner. This action itself doesn't
    perform WebDriver operations during its 'execute' method.

    Attributes:
        template_name (str): The name of the saved template to execute.
        action_type (str): Static type name ("Template").
    """
    action_type: str = "Template"

    def __init__(self,
                 name: Optional[str] = None,
                 template_name: Optional[str] = None,
                 **kwargs):
        """Initialize a TemplateAction."""
        # Default name includes template name if base name is not provided
        default_name = f"{self.action_type}: {template_name or 'Unnamed'}"
        super().__init__(name or default_name, **kwargs)

        if not isinstance(template_name, str) or not template_name:
             raise ValidationError("template_name is required and must be a non-empty string.", field_name="template_name")
        self.template_name = template_name
        logger.debug(f"{self.action_type} '{self.name}' initialized for template: '{self.template_name}'")


    def validate(self) -> bool:
        """Validate the configuration of the template action."""
        super().validate() # Validate base name
        if not isinstance(self.template_name, str) or not self.template_name:
            raise ValidationError("template_name is required and must be a non-empty string.", field_name="template_name")
        # Cannot validate template existence here. Runner does it at runtime.
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute method placeholder for TemplateAction."""
        # This method should ideally NOT be called directly if the runner expands templates.
        # If it is called, it means expansion didn't happen or it's used unexpectedly.
        logger.warning(f"TemplateAction '{self.name}' (template '{self.template_name}') execute() called directly. "
                       "Expansion should occur in runner. Returning success as placeholder.")
        return ActionResult.success(f"Placeholder for template '{self.template_name}' reached.")


    def to_dict(self) -> Dict[str, Any]:
        """Serialize the template action."""
        base_dict = super().to_dict()
        base_dict["template_name"] = self.template_name
        return base_dict

    # TemplateAction does not contain nested actions itself
    # def get_nested_actions(self) -> List[IAction]: return []

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.action_type}: {self.name} (Uses '{self.template_name}')"

################################################################################