"""JavaScript Condition Action for AutoQliq."""

import logging
from typing import Dict, Any, Optional

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError

logger = logging.getLogger(__name__)


class JavaScriptCondition(ActionBase):
    """
    Action that executes a JavaScript snippet and returns a boolean result.

    The script is executed in the browser context and should return a boolean value.
    The workflow context is passed as the first argument (arguments[0]) to the script.

    Attributes:
        script (str): The JavaScript code to execute.
        action_type (str): Static type name ("JavaScriptCondition").
    """
    action_type: str = "JavaScriptCondition"

    def __init__(self, name: Optional[str] = None, script: Optional[str] = None, **kwargs):
        """Initialize JavaScriptCondition."""
        super().__init__(name, **kwargs)
        if not script or not isinstance(script, str):
            raise ValidationError("The 'script' parameter is required and must be a non-empty string.",
                                  action_name=self.name, action_type=self.action_type, field_name="script")
        self.script = script
        logger.debug(f"Initialized {self.action_type} action (Name: {self.name})")

    def validate(self) -> bool:
        """Validate the configuration of the action."""
        super().validate() # Validate base class requirements (e.g., name)
        if not self.script or not isinstance(self.script, str):
            raise ValidationError("The 'script' parameter must be a non-empty string.",
                                  action_name=self.name, action_type=self.action_type, field_name="script")
        # Basic validation, more complex JS parsing is out of scope here
        logger.debug(f"Validation successful for {self.action_type} action (Name: {self.name})")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the JavaScript script and return its boolean result."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}).")
        context = context or {}
        try:
            self.validate()
            logger.debug(f"Executing script for {self.name}: '{self.script[:100]}{"..." if len(self.script) > 100 else ""}'")

            # Execute script, passing context as the first argument
            # Ensure context is serializable if passing complex objects
            result = driver.execute_script(f"return (function(ctx) {{ {self.script} }})(arguments[0]);", context)

            if not isinstance(result, bool):
                msg = f"JavaScript script for action '{self.name}' did not return a boolean value (returned {type(result).__name__}: {result})."
                logger.error(msg)
                return ActionResult.failure(msg)

            logger.info(f"{self.action_type} '{self.name}' evaluated to: {result}")
            # Store the boolean result in the data field for potential use by WhileLoopAction
            return ActionResult.success(f"Script evaluated to {result}", data=result)

        except ValidationError as e:
            logger.error(f"Validation failed for {self.action_type} '{self.name}': {e}")
            return ActionResult.failure(f"Validation failed: {e}")
        except WebDriverError as e:
            msg = f"WebDriver error executing script for action '{self.name}': {e}"
            logger.error(msg)
            # Wrap WebDriverError in ActionError for consistency?
            # Or return failure directly? Returning failure for now.
            return ActionResult.failure(msg)
        except Exception as e:
            # Catch potential JS errors (syntax, runtime) reported by WebDriver
            msg = f"Error executing JavaScript for action '{self.name}': {e}"
            logger.exception(msg) # Use exception for stack trace
            return ActionResult.failure(msg)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["script"] = self.script
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', script='{self.script[:50]}...')"

# STATUS: COMPLETE ✓
