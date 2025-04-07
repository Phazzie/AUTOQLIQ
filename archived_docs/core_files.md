# AutoQliq Core Files

**********ARCHIVED**********
Archived on: 2025-04-06


Generated on: 2025-04-06 21:13:02

## src/core/interfaces/action.py

```python
"""Action interface for AutoQliq.

This module defines the interface for action implementations that provide
workflow step capabilities.
"""
import abc
from typing import Dict, Any, Optional, List

# Assuming ActionResult and IWebDriver are defined elsewhere
from src.core.action_result import ActionResult
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.repository import ICredentialRepository
# ActionError likely defined in core.exceptions
# from src.core.exceptions import ActionError


class IAction(abc.ABC):
    """Interface for action implementations.

    Defines the contract for executable steps within a workflow.

    Attributes:
        name (str): A user-defined name for this specific action instance.
        action_type (str): The identifier for the action type (e.g., "Navigate", "Loop").
                           Must be defined as a class attribute in implementations.
    """
    name: str
    action_type: str

    @abc.abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Context added
    ) -> ActionResult:
        """Execute the action using the provided web driver and context.

        Args:
            driver: The web driver instance.
            credential_repo: Optional credential repository.
            context: Optional dictionary holding execution context (e.g., loop variables).

        Returns:
            An ActionResult indicating success or failure.

        Raises:
            ActionError: For action-specific execution failures.
            CredentialError: For credential-related failures.
            WebDriverError: For driver-related failures.
            ValidationError: If context needed is missing/invalid.
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary representation.

        Must include 'type' and 'name' keys, plus action-specific parameters.
        Nested actions (like in Loop or Conditional) should also be serialized.

        Returns:
            A dictionary representation of the action.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the action's configuration parameters.

        Checks if required parameters are present and have valid types/formats.
        Should also validate nested actions if applicable (e.g., Loop, Conditional).

        Returns:
            True if the action is configured correctly.

        Raises:
            ValidationError: If validation fails (recommended approach).
        """
        pass

    # Optional: Method to get nested actions, useful for editors/validation
    def get_nested_actions(self) -> List['IAction']:
        """Return any nested actions contained within this action."""
        return [] # Default implementation for actions that don't contain others
```

## src/core/interfaces/repository.py

```python
"""Repository interfaces for AutoQliq.

This module defines the interfaces for repository implementations that provide
storage and retrieval capabilities for workflows and credentials.
"""
import abc
from typing import List, Dict, Any, Optional

# Assuming IAction is defined elsewhere
from src.core.interfaces.action import IAction


class IWorkflowRepository(abc.ABC):
    """Interface for workflow repository implementations."""

    # --- Workflow Operations ---
    @abc.abstractmethod
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save (create or update) a workflow."""
        pass

    @abc.abstractmethod
    def load(self, name: str) -> List[IAction]:
        """Load a workflow by name. Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a workflow by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[str]:
        """List the names of all workflows."""
        pass

    @abc.abstractmethod
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow (e.g., created_at, modified_at). Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def create_workflow(self, name: str) -> None:
        """Create a new, empty workflow entry. Raises RepositoryError if name exists."""
        pass

    # --- Template Operations ---
    @abc.abstractmethod
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save (create or update) an action template. Stores serialized action data."""
        pass

    @abc.abstractmethod
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load the serialized action data for a template by name. Raises RepositoryError if not found."""
        pass

    @abc.abstractmethod
    def delete_template(self, name: str) -> bool:
        """Delete a template by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_templates(self) -> List[str]:
        """List the names of all saved templates."""
        pass


class ICredentialRepository(abc.ABC):
    """Interface for credential repository implementations."""

    @abc.abstractmethod
    def save(self, credential: Dict[str, str]) -> None:
        """Save (create or update) a credential. Assumes value for 'password' is prepared (e.g., hashed)."""
        pass

    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including stored password/hash) by name."""
        pass

    @abc.abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a credential by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_credentials(self) -> List[str]:
        """List the names of all stored credentials."""
        pass

# --- New Reporting Repository Interface ---
class IReportingRepository(abc.ABC):
    """Interface for storing and retrieving workflow execution logs/results."""

    @abc.abstractmethod
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """Saves the results and metadata of a single workflow execution."""
        pass

    @abc.abstractmethod
    def get_execution_log(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the log data for a specific execution ID."""
        pass

    @abc.abstractmethod
    def list_execution_summaries(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists summary information (ID, name, start time, status, duration) for past executions."""
        pass

    # Optional: Methods for querying based on date range, status, etc.
    # Optional: Method for cleaning up old logs
```

## src/core/interfaces/webdriver.py

```python
"""WebDriver interface for AutoQliq.

This module defines the interface for web driver implementations that provide
browser automation capabilities.
"""
import abc
from typing import Any, Union, List, Dict, Optional # Added List, Dict, Optional

# Assume WebDriverError is defined in core.exceptions
# from src.core.exceptions import WebDriverError

class IWebDriver(abc.ABC):
    """Interface for web driver implementations."""
    @abc.abstractmethod
    def get(self, url: str) -> None:
        """Navigate to the specified URL."""
        pass

    @abc.abstractmethod
    def quit(self) -> None:
        """Quit the WebDriver and close all associated windows."""
        pass

    @abc.abstractmethod
    def find_element(self, selector: str) -> Any:
        """Find a single element on the page using CSS selector."""
        pass

    @abc.abstractmethod
    def click_element(self, selector: str) -> None:
        """Click on an element identified by the CSS selector."""
        pass

    @abc.abstractmethod
    def type_text(self, selector: str, text: str) -> None:
        """Type text into an element identified by the CSS selector."""
        pass

    @abc.abstractmethod
    def take_screenshot(self, file_path: str) -> None:
        """Take a screenshot and save it to the specified file path."""
        pass

    @abc.abstractmethod
    def is_element_present(self, selector: str) -> bool:
        """Check if an element is present on the page without raising an error."""
        pass

    @abc.abstractmethod
    def get_current_url(self) -> str:
        """Get the current URL of the browser."""
        pass

    @abc.abstractmethod
    def execute_script(self, script: str, *args: Any) -> Any:
        """Executes JavaScript in the current window/frame.

        Args:
            script: The JavaScript code to execute.
            *args: Any arguments to pass to the script. These will be available
                   in the script as the 'arguments' array.

        Returns:
            The value returned by the script (if any), JSON-serializable.

        Raises:
            WebDriverError: If script execution fails.
        """
        pass

    # --- Optional but Recommended Methods ---

    @abc.abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10) -> Any:
        """Wait explicitly for an element to be present on the page."""
        pass

    @abc.abstractmethod
    def switch_to_frame(self, frame_reference: Union[str, int, Any]) -> None:
        """Switch focus to a frame or iframe."""
        pass

    @abc.abstractmethod
    def switch_to_default_content(self) -> None:
        """Switch back to the default content (main document)."""
        pass

    @abc.abstractmethod
    def accept_alert(self) -> None:
        """Accept an alert, confirm, or prompt dialog."""
        pass

    @abc.abstractmethod
    def dismiss_alert(self) -> None:
        """Dismiss an alert or confirm dialog."""
        pass

    @abc.abstractmethod
    def get_alert_text(self) -> str:
        """Get the text content of an alert, confirm, or prompt dialog."""
        pass
```

## src/core/interfaces/service.py

```python
"""Core Service interfaces for AutoQliq.

Defines the contracts for the application service layer, which orchestrates
business logic and use cases by coordinating repositories and domain objects.
Presenters should primarily interact with these service interfaces.
"""
import abc
from typing import List, Dict, Any, Optional, Callable # Added Callable
import threading # Added threading for stop_event hint

# Assuming core entities/interfaces are defined elsewhere
from src.core.interfaces.action import IAction
from src.core.interfaces.webdriver import IWebDriver
# Use BrowserType enum defined in infrastructure base, as it relates to implementation details
from src.infrastructure.webdrivers.base import BrowserType

# --- Base Service Interface (Optional) ---
class IService(abc.ABC):
    """Base marker interface for application services."""
    pass

# --- Specific Service Interfaces ---

class IWorkflowService(IService):
    """Interface for workflow management and execution services."""

    @abc.abstractmethod
    def create_workflow(self, name: str) -> bool:
        """Create a new empty workflow. Returns True on success."""
        pass

    @abc.abstractmethod
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[str]:
        """Get a list of available workflow names."""
        pass

    @abc.abstractmethod
    def get_workflow(self, name: str) -> List[IAction]:
        """Get the actions for a workflow by name. Raises WorkflowError if not found."""
        pass

    @abc.abstractmethod
    def save_workflow(self, name: str, actions: List[IAction]) -> bool:
        """Save a workflow with its actions. Returns True on success."""
        pass

    @abc.abstractmethod
    def run_workflow(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME,
        # Add callbacks for real-time updates if needed by presenter/view
        log_callback: Optional[Callable[[str], None]] = None,
        stop_event: Optional[threading.Event] = None # For cancellation
    ) -> Dict[str, Any]: # Return the full execution log dictionary
        """
        Run a workflow, returning detailed execution results.
        Manages WebDriver lifecycle internally.

        Args:
            name: Workflow name.
            credential_name: Optional credential name.
            browser_type: Browser to use.
            log_callback: Optional function to call with log messages during execution.
            stop_event: Optional threading.Event object to signal cancellation. Service/Runner should check this.

        Returns:
             A dictionary containing detailed execution results, including status,
             duration, error messages, and individual action results.

        Raises:
            WorkflowError: For general workflow execution issues.
            CredentialError: If the specified credential is required but not found.
            WebDriverError: If the WebDriver fails to start or during execution.
            ActionError: If a specific action fails during execution and isn't handled.
            ValidationError: If workflow name or credential name is invalid.
        """
        pass

    @abc.abstractmethod
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow (e.g., created_at, modified_at)."""
        pass


class ICredentialService(IService):
    """Interface for credential management services."""

    @abc.abstractmethod
    def create_credential(self, name: str, username: str, password: str) -> bool:
        """Create a new credential (handles hashing). Returns True on success."""
        pass

    @abc.abstractmethod
    def delete_credential(self, name: str) -> bool:
        """Delete a credential by name. Returns True if deleted, False if not found."""
        pass

    @abc.abstractmethod
    def get_credential(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including password hash) by name."""
        pass

    @abc.abstractmethod
    def list_credentials(self) -> List[str]:
        """Get a list of available credential names."""
        pass

    @abc.abstractmethod
    def verify_credential(self, name: str, password_to_check: str) -> bool:
        """Verify if the provided password matches the stored hash for the credential."""
        pass


class IWebDriverService(IService):
    """Interface for services managing WebDriver instances."""

    @abc.abstractmethod
    def create_web_driver(
        self,
        browser_type_str: Optional[str] = None, # Use string here, service converts to enum
        selenium_options: Optional[Any] = None,
        playwright_options: Optional[Dict[str, Any]] = None,
        driver_type: str = "selenium",
        **kwargs: Any # Allow passing implicit_wait, webdriver_path etc.
    ) -> IWebDriver:
        """Create a new WebDriver instance using configuration and passed options."""
        pass

    @abc.abstractmethod
    def dispose_web_driver(self, driver: IWebDriver) -> bool:
        """Dispose of (quit) a WebDriver instance. Returns True on success."""
        pass

    @abc.abstractmethod
    def get_available_browser_types(self) -> List[str]:
        """Get a list of supported browser type names (strings)."""
        pass


# --- New Service Interfaces ---

class ISchedulerService(IService):
    """Interface for services managing scheduled workflow runs."""

    @abc.abstractmethod
    def schedule_workflow(self, workflow_name: str, credential_name: Optional[str], schedule_config: Dict[str, Any]) -> str:
        """Schedule a workflow to run. Returns a unique job ID."""
        pass

    @abc.abstractmethod
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """List currently scheduled jobs and their details."""
        pass

    @abc.abstractmethod
    def cancel_scheduled_job(self, job_id: str) -> bool:
        """Cancel a scheduled job by its ID."""
        pass


class IReportingService(IService):
    """Interface for services managing workflow execution reporting."""

    @abc.abstractmethod
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """
        Saves the results and metadata of a single workflow execution.

        Args:
            execution_log: A dictionary containing execution details (status,
                           duration, action results, timestamps, etc.). Structure
                           determined by WorkflowRunner.
        """
        pass

    @abc.abstractmethod
    def generate_summary_report(self, since: Optional[Any] = None) -> Dict[str, Any]:
        """Generate a summary report of workflow executions."""
        pass

    @abc.abstractmethod
    def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a specific past execution."""
        pass

    @abc.abstractmethod
    def list_past_executions(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List past workflow execution records (summary info)."""
        pass
```

## src/core/interfaces/presenter.py

```python
"""Presenter interface for AutoQliq.

This module defines the interface for presenter implementations in the MVP pattern.
"""

import abc
from typing import TypeVar, Generic, Optional

# Define a type variable for the view
V = TypeVar('V')


class IPresenter(Generic[V], abc.ABC):
    """Interface for presenter implementations in the MVP pattern.
    
    Presenters handle the logic between models and views. They respond to
    user actions from the view, manipulate model data, and update the view.
    
    Type Parameters:
        V: The type of view this presenter is associated with.
    """
    
    @abc.abstractmethod
    def set_view(self, view: V) -> None:
        """Set the view for this presenter.
        
        Args:
            view: The view instance to associate with this presenter.
        """
        pass
```

## src/core/interfaces/view.py

```python
"""View interface for AutoQliq.

This module defines the interface for view implementations in the MVP pattern.
"""

import abc
from typing import TypeVar, Generic, Optional

# Define a type variable for the presenter
P = TypeVar('P')


class IView(Generic[P], abc.ABC):
    """Interface for view implementations in the MVP pattern.
    
    Views are responsible for displaying information to the user and
    capturing user input. They delegate business logic to presenters.
    
    Type Parameters:
        P: The type of presenter this view is associated with.
    """
    
    @abc.abstractmethod
    def set_presenter(self, presenter: P) -> None:
        """Set the presenter for this view.
        
        Args:
            presenter: The presenter instance to associate with this view.
        """
        pass
```

## src/core/actions/base.py

```python
"""Base action module for AutoQliq.

This module provides the abstract base class for all action implementations,
ensuring they adhere to the IAction interface and provide common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# Assuming these interfaces and classes are defined elsewhere
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.action_result import ActionResult
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ActionBase(IAction, ABC):
    """
    Abstract base class for all actions in the system.

    Provides common structure and enforces the IAction interface.

    Attributes:
        name (str): A descriptive name for the action instance.
        action_type (str): The type name of the action (e.g., "Navigate").
                           Must be defined as a class attribute in subclasses.
    """
    action_type: str = "Base" # Must be overridden by subclasses

    def __init__(self, name: Optional[str] = None, **kwargs):
        """
        Initialize an ActionBase.

        Args:
            name (Optional[str]): A descriptive name for this specific action instance.
                                  If None, defaults to the action_type.
            **kwargs: Catches potential extra parameters from deserialization
                      but doesn't use them by default. Subclasses should handle
                      their specific parameters.
        """
        if not hasattr(self, 'action_type') or self.action_type == "Base":
             raise NotImplementedError(f"Subclass {self.__class__.__name__} must define 'action_type' class attribute.")

        default_name = self.action_type
        if name is None:
            self.name = default_name
        elif not isinstance(name, str) or not name.strip(): # Check for non-empty stripped name
            logger.warning(f"Invalid or empty name '{name}' provided for {self.action_type} action. Defaulting to '{default_name}'.")
            self.name = default_name
        else:
            self.name = name.strip() # Store stripped name

        # Store unused kwargs for potential future use or debugging, but warn
        self._unused_kwargs = kwargs
        if kwargs:
            logger.warning(f"Unused parameters provided for {self.action_type} action '{self.name}': {list(kwargs.keys())}")

        logger.debug(f"Initialized action: {self.action_type} (Name: {self.name})")

    def validate(self) -> bool:
        """
        Validate that the action has the required configuration.

        Base implementation validates the 'name' attribute. Subclasses should
        call `super().validate()` and then add their specific parameter checks.

        Returns:
            bool: True if the action configuration is valid.

        Raises:
            ValidationError: If validation fails (recommended).
        """
        if not isinstance(self.name, str) or not self.name:
             raise ValidationError("Action name must be a non-empty string.", field_name="name")
        return True

    @abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Context added
    ) -> ActionResult:
        """
        Execute the action using the provided web driver and context.

        Args:
            driver (IWebDriver): The web driver instance to perform browser operations.
            credential_repo (Optional[ICredentialRepository]): Repository for credentials.
            context (Optional[Dict[str, Any]]): Dictionary holding execution context
                                                 (e.g., loop variables). Defaults to None.

        Returns:
            ActionResult: An object indicating the outcome (success/failure) and details.
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the action instance to a dictionary representation.

        Must include 'type' and 'name' keys. Subclasses must add their parameters.

        Returns:
            Dict[str, Any]: A dictionary representing the action.
        """
        # Ensure base implementation includes type and name
        return {"type": self.action_type, "name": self.name}

    def get_nested_actions(self) -> List['IAction']:
        """Return any nested actions contained within this action."""
        return []

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        attrs = []
        for key, value in self.__dict__.items():
             if key == 'name' or key.startswith('_'): continue
             if isinstance(value, list) and key.endswith("_actions"):
                 repr_val = f"[{len(value)} actions]"
             else:
                 try:
                      repr_val = repr(value); max_len=50
                      if len(repr_val) > max_len: repr_val = repr_val[:max_len-3] + "..."
                 except Exception: repr_val = "<repr error>"
             attrs.append(f"{key}={repr_val}")
        attr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}(name='{self.name}'{', ' + attr_str if attr_str else ''})"

    def __str__(self) -> str:
        """Return a user-friendly string representation for UI display."""
        return f"{self.action_type}: {self.name}"
```

## src/core/actions/factory.py

```python
"""Factory module for creating action instances."""

import logging
from typing import Dict, Any, Type, List # Added List

# Assuming IAction and ActionBase are defined
from src.core.interfaces import IAction
# Import specific action classes dynamically if possible, or explicitly
from src.core.actions.base import ActionBase
from src.core.actions.navigation import NavigateAction
from src.core.actions.interaction import ClickAction, TypeAction
from src.core.actions.utility import WaitAction, ScreenshotAction
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction # New

# Assuming ActionError is defined
from src.core.exceptions import ActionError, ValidationError, SerializationError

logger = logging.getLogger(__name__)


class ActionFactory:
    """
    Factory responsible for creating action instances from data.

    Uses a registry to map action type strings to action classes.
    Handles recursive deserialization for nested actions.
    """
    # Registry mapping type strings (from JSON/dict) to the corresponding class
    _registry: Dict[str, Type[ActionBase]] = {} # Start empty, register below

    @classmethod
    def register_action(cls, action_class: Type[ActionBase]) -> None:
        """Register a new action type using its class."""
        if not isinstance(action_class, type) or not issubclass(action_class, ActionBase):
            raise ValueError(f"Action class {getattr(action_class, '__name__', '<unknown>')} must inherit from ActionBase.")

        action_type = getattr(action_class, 'action_type', None)
        if not isinstance(action_type, str) or not action_type:
             raise ValueError(f"Action class {action_class.__name__} must define a non-empty string 'action_type' class attribute.")

        if action_type in cls._registry and cls._registry[action_type] != action_class:
            logger.warning(f"Action type '{action_type}' re-registered. Overwriting {cls._registry[action_type].__name__} with {action_class.__name__}.")
        elif action_type in cls._registry: return # Already registered

        cls._registry[action_type] = action_class
        logger.info(f"Registered action type '{action_type}' with class {action_class.__name__}")

    @classmethod
    def get_registered_action_types(cls) -> List[str]:
        """Returns a sorted list of registered action type names."""
        return sorted(list(cls._registry.keys()))

    @classmethod
    def create_action(cls, action_data: Dict[str, Any]) -> IAction:
        """
        Create an action instance from a dictionary representation.

        Handles deserialization of nested actions.
        Does NOT handle template expansion (runner does this).
        """
        if not isinstance(action_data, dict):
            raise TypeError(f"Action data must be a dictionary, got {type(action_data).__name__}.")

        action_type = action_data.get("type")
        action_name_from_data = action_data.get("name")

        if not action_type:
            raise ActionError("Action data must include a 'type' key.", action_type=None, action_name=action_name_from_data)
        if not isinstance(action_type, str):
             raise ActionError("Action 'type' key must be a string.", action_type=str(action_type), action_name=action_name_from_data)

        action_class = cls._registry.get(action_type)
        if not action_class:
            logger.error(f"Unknown action type encountered: '{action_type}'. Available: {list(cls._registry.keys())}")
            raise ActionError(f"Unknown action type: '{action_type}'", action_type=action_type, action_name=action_name_from_data)

        try:
            action_params = {k: v for k, v in action_data.items() if k != "type"}

            # --- Handle Nested Actions Deserialization ---
            nested_action_fields = {
                 ConditionalAction.action_type: ["true_branch", "false_branch"],
                 LoopAction.action_type: ["loop_actions"],
                 ErrorHandlingAction.action_type: ["try_actions", "catch_actions"],
            }
            # Note: TemplateAction does not have nested actions defined in its own data dict.

            if action_type in nested_action_fields:
                for field_name in nested_action_fields[action_type]:
                    nested_data_list = action_params.get(field_name)
                    if isinstance(nested_data_list, list):
                        try:
                            action_params[field_name] = [cls.create_action(nested_data) for nested_data in nested_data_list]
                            logger.debug(f"Deserialized {len(action_params[field_name])} nested actions for '{field_name}' in '{action_type}'.")
                        except (TypeError, ActionError, SerializationError, ValidationError) as nested_e:
                             err_msg = f"Invalid nested action data in field '{field_name}' for action type '{action_type}': {nested_e}"
                             logger.error(f"{err_msg} Parent Data: {action_data}")
                             raise SerializationError(err_msg, cause=nested_e) from nested_e
                    elif nested_data_list is not None:
                         raise SerializationError(f"Field '{field_name}' for action type '{action_type}' must be a list, got {type(nested_data_list).__name__}.")

            # Instantiate the action class
            action_instance = action_class(**action_params)
            logger.debug(f"Created action instance: {action_instance!r}")
            return action_instance
        except (TypeError, ValueError, ValidationError) as e:
            err_msg = f"Invalid parameters or validation failed for action type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}")
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e
        except SerializationError as e:
             raise ActionError(f"Failed to create nested action within '{action_type}': {e}", action_name=action_name_from_data, action_type=action_type, cause=e) from e
        except Exception as e:
            err_msg = f"Failed to create action of type '{action_type}': {e}"
            logger.error(f"{err_msg} Provided data: {action_data}", exc_info=True)
            raise ActionError(err_msg, action_name=action_name_from_data, action_type=action_type) from e

# --- Auto-register known actions ---
ActionFactory.register_action(NavigateAction)
ActionFactory.register_action(ClickAction)
ActionFactory.register_action(TypeAction)
ActionFactory.register_action(WaitAction)
ActionFactory.register_action(ScreenshotAction)
ActionFactory.register_action(ConditionalAction)
ActionFactory.register_action(LoopAction)
ActionFactory.register_action(ErrorHandlingAction)
ActionFactory.register_action(TemplateAction) # New
```

## src/core/actions/conditional_action.py

```python
"""Conditional Action (If/Else) for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, WebDriverError

logger = logging.getLogger(__name__)


class ConditionalAction(ActionBase):
    """
    Action that executes one of two branches based on a condition.

    Supported Conditions:
        - 'element_present'
        - 'element_not_present'
        - 'variable_equals'
        - 'javascript_eval' (Executes JS, expects truthy/falsy return)

    Attributes:
        condition_type (str): Type of condition.
        selector (Optional[str]): CSS selector for element conditions.
        variable_name (Optional[str]): Context variable name for variable checks.
        expected_value (Optional[str]): Value to compare against for variable checks.
        script (Optional[str]): JavaScript code for JS conditions.
        true_branch (List[IAction]): Actions if condition is true.
        false_branch (List[IAction]): Actions if condition is false.
    """
    action_type: str = "Conditional"
    SUPPORTED_CONDITIONS = ["element_present", "element_not_present", "variable_equals", "javascript_eval"]

    def __init__(self,
                 name: Optional[str] = None,
                 condition_type: str = "element_present",
                 selector: Optional[str] = None,
                 variable_name: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 script: Optional[str] = None,
                 true_branch: Optional[List[IAction]] = None,
                 false_branch: Optional[List[IAction]] = None,
                 **kwargs):
        """Initialize a ConditionalAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(condition_type, str): raise ValidationError("condition_type must be str.", field_name="condition_type")
        if selector is not None and not isinstance(selector, str): raise ValidationError("selector must be str or None.", field_name="selector")
        if variable_name is not None and not isinstance(variable_name, str): raise ValidationError("variable_name must be str or None.", field_name="variable_name")
        if expected_value is not None and not isinstance(expected_value, str): raise ValidationError("expected_value must be str or None.", field_name="expected_value")
        if script is not None and not isinstance(script, str): raise ValidationError("script must be str or None.", field_name="script")

        self.condition_type = condition_type
        self.selector = selector
        self.variable_name = variable_name
        self.expected_value = expected_value
        self.script = script
        self.true_branch = true_branch or []
        self.false_branch = false_branch or []

        if not isinstance(self.true_branch, list) or not all(isinstance(a, IAction) for a in self.true_branch):
             raise ValidationError("true_branch must be list of IAction.", field_name="true_branch")
        if not isinstance(self.false_branch, list) or not all(isinstance(a, IAction) for a in self.false_branch):
             raise ValidationError("false_branch must be list of IAction.", field_name="false_branch")
        try: self.validate()
        except ValidationError as e: raise e from e

        logger.debug(f"{self.action_type} '{self.name}' initialized. Condition: {self.condition_type}")


    def validate(self) -> bool:
        """Validate the configuration of the conditional action and its nested actions."""
        super().validate()
        if self.condition_type not in self.SUPPORTED_CONDITIONS:
            raise ValidationError(f"Unsupported condition_type: '{self.condition_type}'. Supported: {self.SUPPORTED_CONDITIONS}", field_name="condition_type")

        if self.condition_type in ["element_present", "element_not_present"]:
            if not isinstance(self.selector, str) or not self.selector:
                raise ValidationError("Selector required for element conditions.", field_name="selector")
        elif self.condition_type == "variable_equals":
            if not isinstance(self.variable_name, str) or not self.variable_name:
                 raise ValidationError("variable_name required.", field_name="variable_name")
            if self.expected_value is None: logger.warning(f"Condition '{self.name}' compares against None.")
            elif not isinstance(self.expected_value, str): raise ValidationError("expected_value must be string or None.", field_name="expected_value")
        elif self.condition_type == "javascript_eval":
             if not isinstance(self.script, str) or not self.script:
                  raise ValidationError("Non-empty 'script' required.", field_name="script")

        for i, action in enumerate(self.true_branch):
            branch = "true_branch"; idx_disp = i + 1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx_disp} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx_disp} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e
        for i, action in enumerate(self.false_branch):
            branch = "false_branch"; idx_disp = i + 1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx_disp} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx_disp} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def _evaluate_condition(self, driver: IWebDriver, context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate the condition based on the driver state and context."""
        context = context or {}
        result = False

        try:
            if self.condition_type == "element_present":
                if not self.selector: raise ActionError("Selector missing.", self.name)
                logger.debug(f"Evaluating: element_present ('{self.selector}')?")
                result = driver.is_element_present(self.selector)
            elif self.condition_type == "element_not_present":
                 if not self.selector: raise ActionError("Selector missing.", self.name)
                 logger.debug(f"Evaluating: element_not_present ('{self.selector}')?")
                 result = not driver.is_element_present(self.selector)
            elif self.condition_type == "variable_equals":
                 if not self.variable_name: raise ActionError("variable_name missing.", self.name)
                 actual_value = context.get(self.variable_name)
                 actual_str = str(actual_value) if actual_value is not None else None
                 expected_str = str(self.expected_value) if self.expected_value is not None else None
                 logger.debug(f"Evaluating: variable_equals ('{self.variable_name}' == '{self.expected_value}')? Actual: '{actual_str}'")
                 result = actual_str == expected_str
            elif self.condition_type == "javascript_eval":
                 if not self.script: raise ActionError("Script missing.", self.name)
                 logger.debug(f"Evaluating: javascript_eval ('{self.script[:50]}...')?")
                 script_result = driver.execute_script(self.script) # Raises WebDriverError
                 logger.debug(f"JS script returned: {script_result} (type: {type(script_result).__name__})")
                 result = bool(script_result) # Evaluate truthiness
            else:
                raise ActionError(f"Condition evaluation not implemented for type: {self.condition_type}", self.name)
        except WebDriverError as e:
             # Wrap WebDriver errors occurring during condition evaluation
             raise ActionError(f"WebDriver error evaluating condition: {e}", action_name=self.name, cause=e) from e

        logger.debug(f"Condition result: {result}")
        return result


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute either the true or false branch based on the condition."""
        # This method is called by the runner's _execute_conditional helper.
        # It needs to evaluate condition and return success/failure.
        # Runner handles executing the chosen branch actions.
        # *** Correction: This action *should* execute its branch internally for encapsulation. ***
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Evaluating condition...")
        try:
            self.validate()
            condition_result = self._evaluate_condition(driver, context) # Can raise ActionError(WebDriverError)
            logger.info(f"Condition '{self.condition_type}' evaluated to: {condition_result}")

            branch_to_execute = self.true_branch if condition_result else self.false_branch
            branch_name = "true" if condition_result else "false"

            if not branch_to_execute:
                 logger.info(f"No actions in '{branch_name}' branch of '{self.name}'.")
                 return ActionResult.success(f"Condition {condition_result}, '{branch_name}' branch empty.")

            logger.info(f"Executing '{branch_name}' branch of '{self.name}'...")

            # --- Execute Chosen Branch ---
            # Need access to the runner's execution logic for nested actions
            # This creates a dependency. Alternative: Pass runner instance? Or duplicate logic?
            # Let's assume runner logic is needed here for now.
            from src.core.workflow.runner import WorkflowRunner # Local import
            temp_runner = WorkflowRunner(driver, credential_repo, None, None) # Temp runner for nested exec

            branch_results: List[ActionResult] = []
            for i, action in enumerate(branch_to_execute):
                 action_display = f"{action.name} ({action.action_type}, Step {i+1} in '{branch_name}' branch)"
                 logger.debug(f"Executing nested action: {action_display}")
                 # Use run_single_action to handle context and errors consistently
                 nested_result = temp_runner.run_single_action(action, context or {}) # Pass context
                 branch_results.append(nested_result)
                 if not nested_result.is_success():
                      error_msg = f"Nested action '{action_display}' failed: {nested_result.message}"
                      logger.error(error_msg)
                      return ActionResult.failure(f"Exec failed in '{branch_name}' branch of '{self.name}'. {error_msg}")
                 logger.debug(f"Nested action '{action_display}' succeeded.")

            logger.info(f"Successfully executed '{branch_name}' branch of '{self.name}'.")
            final_msg = f"Condition {condition_result}, '{branch_name}' branch ({len(branch_results)} actions) executed."
            return ActionResult.success(final_msg)

        except (ValidationError, ActionError) as e: # Catch errors from validate, _evaluate, or nested execute
            msg = f"Error during conditional execution '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e: # Catch unexpected errors
            error = ActionError(f"Unexpected error in conditional '{self.name}'", self.name, self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the conditional action and its branches."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "condition_type": self.condition_type,
            "true_branch": serialize_actions(self.true_branch),
            "false_branch": serialize_actions(self.false_branch),
        })
        # Add parameters based on type, only if they have values
        if self.condition_type in ["element_present", "element_not_present"] and self.selector:
             base_dict["selector"] = self.selector
        elif self.condition_type == "variable_equals":
             if self.variable_name: base_dict["variable_name"] = self.variable_name
             base_dict["expected_value"] = self.expected_value # Include None if that's the value
        elif self.condition_type == "javascript_eval" and self.script:
             base_dict["script"] = self.script
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from both branches, recursively."""
        nested = []
        for action in self.true_branch + self.false_branch:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        condition_detail = ""
        if self.condition_type in ["element_present", "element_not_present"]:
             condition_detail = f"selector='{self.selector}'"
        elif self.condition_type == "variable_equals":
             condition_detail = f"var[{self.variable_name}] == '{self.expected_value}'"
        elif self.condition_type == "javascript_eval":
             condition_detail = f"script='{self.script[:20]}...'" if self.script else "script=''"

        true_count = len(self.true_branch); false_count = len(self.false_branch)
        return f"{self.action_type}: {self.name} (if {self.condition_type} {condition_detail} ? {true_count} : {false_count})"
```

## src/core/actions/loop_action.py

```python
"""Loop Action for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, WebDriverError
# Need ConditionalAction._evaluate_condition helper for 'while' loop
from src.core.actions.conditional_action import ConditionalAction

logger = logging.getLogger(__name__)


class LoopAction(ActionBase):
    """
    Action that repeats a sequence of nested actions based on a condition or count.

    Supported Loop Types:
        - 'count': Repeats fixed number of times. Context: `loop_index`, `loop_iteration`, `loop_total`.
        - 'for_each': Iterates list from context var `list_variable_name`. Context: `loop_item`, + index/iter/total.
        - 'while': Repeats while a condition (like ConditionalAction's) is true. Uses condition parameters.

    Attributes:
        loop_type (str): 'count', 'for_each', or 'while'.
        count (Optional[int]): Iterations for 'count'.
        list_variable_name (Optional[str]): Context variable name holding list for 'for_each'.
        loop_actions (List[IAction]): Actions to execute in each iteration.
        # Attributes for 'while' loop
        condition_type (Optional[str]): Condition type for 'while' loop.
        selector (Optional[str]): CSS selector for element conditions in 'while'.
        variable_name (Optional[str]): Context variable name for variable checks in 'while'.
        expected_value (Optional[str]): Value to compare against for variable checks in 'while'.
        script (Optional[str]): JavaScript code for JS conditions in 'while'.
    """
    action_type: str = "Loop"
    SUPPORTED_TYPES = ["count", "for_each", "while"]

    def __init__(self,
                 name: Optional[str] = None,
                 loop_type: str = "count",
                 count: Optional[int] = None,
                 list_variable_name: Optional[str] = None,
                 condition_type: Optional[str] = None,
                 selector: Optional[str] = None,
                 variable_name: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 script: Optional[str] = None,
                 loop_actions: Optional[List[IAction]] = None,
                 **kwargs):
        """Initialize a LoopAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(loop_type, str) or loop_type not in self.SUPPORTED_TYPES:
             raise ValidationError(f"loop_type must be one of {self.SUPPORTED_TYPES}.", field_name="loop_type")
        self.loop_type = loop_type
        self.count = None
        self.list_variable_name = None
        self.condition_type = condition_type
        self.selector = selector
        self.variable_name = variable_name
        self.expected_value = expected_value
        self.script = script

        # Type-specific param validation & assignment
        if self.loop_type == "count":
             if count is None: raise ValidationError("'count' required.", field_name="count")
             try: self.count = int(count); assert self.count > 0
             except: raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(list_variable_name, str) or not list_variable_name:
                  raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
             self.list_variable_name = list_variable_name
        elif self.loop_type == "while":
             if not condition_type: raise ValidationError("'condition_type' required.", field_name="condition_type")
             # Detailed condition param validation happens in validate()

        self.loop_actions = loop_actions or []
        if not isinstance(self.loop_actions, list) or not all(isinstance(a, IAction) for a in self.loop_actions):
             raise ValidationError("loop_actions must be list of IAction.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Loop '{self.name}' initialized with no actions.")

        logger.debug(f"{self.action_type} '{self.name}' initialized. Type: {self.loop_type}")


    def validate(self) -> bool:
        """Validate the configuration of the loop action and its nested actions."""
        super().validate()
        if self.loop_type not in self.SUPPORTED_TYPES:
            raise ValidationError(f"Unsupported loop_type: '{self.loop_type}'.", field_name="loop_type")

        if self.loop_type == "count":
            if not isinstance(self.count, int) or self.count <= 0:
                raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(self.list_variable_name, str) or not self.list_variable_name:
                 raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
        elif self.loop_type == "while":
             # Validate condition parameters like ConditionalAction
             if not self.condition_type or self.condition_type not in ConditionalAction.SUPPORTED_CONDITIONS:
                  raise ValidationError(f"Invalid 'condition_type' for 'while' loop.", field_name="condition_type")
             if self.condition_type in ["element_present", "element_not_present"]:
                 if not isinstance(self.selector, str) or not self.selector: raise ValidationError("Selector required.", field_name="selector")
             elif self.condition_type == "variable_equals":
                 if not isinstance(self.variable_name, str) or not self.variable_name: raise ValidationError("variable_name required.", field_name="variable_name")
                 if self.expected_value is None: logger.warning(f"'while' loop '{self.name}' compares against None.")
                 elif not isinstance(self.expected_value, str): raise ValidationError("expected_value must be string or None.", field_name="expected_value")
             elif self.condition_type == "javascript_eval":
                  if not isinstance(self.script, str) or not self.script: raise ValidationError("Non-empty 'script' required.", field_name="script")

        # Validate nested actions
        if not isinstance(self.loop_actions, list): raise ValidationError("loop_actions must be list.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Validation: Loop '{self.name}' has no actions.")

        for i, action in enumerate(self.loop_actions):
            branch="loop_actions"; idx=i+1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def _evaluate_while_condition(self, driver: IWebDriver, context: Optional[Dict[str, Any]]) -> bool:
         """Evaluate the 'while' loop condition."""
         # Reuse ConditionalAction's evaluation logic by creating a temporary instance
         # This avoids duplicating the condition logic here.
         temp_cond_action = ConditionalAction(
              name=f"{self.name}_condition",
              condition_type=self.condition_type or "", # Ensure not None
              selector=self.selector,
              variable_name=self.variable_name,
              expected_value=self.expected_value,
              script=self.script
         )
         # Call the internal evaluation method of the temporary instance
         return temp_cond_action._evaluate_condition(driver, context)


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the nested actions repeatedly based on the loop type."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Type: {self.loop_type}")
        try:
            self.validate()
            context = context or {}

            if not self.loop_actions:
                 logger.warning(f"Loop '{self.name}' has no actions. Skipping.")
                 return ActionResult.success("Loop completed (no actions).")

            iterations_executed = 0
            max_while_iterations = 1000 # Safety break

            if self.loop_type == "count":
                iterations_total = self.count or 0
                for i in range(iterations_total):
                    iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Iter {iteration_num}: "
                    logger.info(f"{iter_log_prefix}Starting.")
                    iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total})
                    self._execute_nested_block(driver, credential_repo, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                    iterations_executed = iteration_num
            elif self.loop_type == "for_each":
                 if not self.list_variable_name: raise ActionError("list_variable_name missing", self.name)
                 target_list = context.get(self.list_variable_name)
                 if not isinstance(target_list, list): return ActionResult.failure(f"Context var '{self.list_variable_name}' not list.")

                 iterations_total = len(target_list)
                 logger.info(f"Loop '{self.name}' starting 'for_each' over '{self.list_variable_name}' ({iterations_total} items).")
                 for i, item in enumerate(target_list):
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Item {iteration_num}: "
                      logger.info(f"{iter_log_prefix}Starting.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total, 'loop_item': item})
                      self._execute_nested_block(driver, credential_repo, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
            elif self.loop_type == "while":
                 logger.info(f"Loop '{self.name}' starting 'while' loop.")
                 i = 0
                 while i < max_while_iterations:
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' While Iter {iteration_num}: "
                      logger.debug(f"{iter_log_prefix}Evaluating condition...")
                      condition_met = self._evaluate_while_condition(driver, context) # Raises ActionError on failure
                      if not condition_met: logger.info(f"{iter_log_prefix}Condition false. Exiting loop."); break
                      logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num})
                      self._execute_nested_block(driver, credential_repo, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
                      i += 1
                 else: raise ActionError(f"While loop exceeded max iterations ({max_while_iterations}).", self.name)
            else:
                raise ActionError(f"Loop execution not implemented for type: {self.loop_type}", self.name)

            logger.info(f"Loop '{self.name}' completed successfully after {iterations_executed} iterations.")
            return ActionResult.success(f"Loop '{self.name}' completed {iterations_executed} iterations successfully.")

        except (ValidationError, ActionError) as e:
            msg = f"Error during loop execution '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error in loop action '{self.name}'", self.name, self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def _execute_nested_block(self, driver: IWebDriver, credential_repo: Optional[ICredentialRepository], context: Dict[str, Any], workflow_name: str, log_prefix: str):
         """Internal helper to execute nested actions, raising ActionError on failure."""
         from src.core.workflow.runner import WorkflowRunner # Local import
         temp_runner = WorkflowRunner(driver, credential_repo, None, None) # No repo/stop needed for sub-run

         for j, action in enumerate(self.loop_actions):
              action_display = f"{action.name} ({action.action_type}, {log_prefix}Inner Step {j+1})"
              logger.debug(f"Executing nested action: {action_display}")
              nested_result = temp_runner.run_single_action(action, context) # Use runner's single action exec
              if not nested_result.is_success():
                   error_msg = f"Nested action '{action_display}' failed: {nested_result.message}"
                   raise ActionError(error_msg, action_name=action.name, action_type=action.action_type)
              logger.debug(f"Nested action '{action_display}' succeeded.")


    def to_dict(self) -> Dict[str, Any]:
        """Serialize the loop action and its nested actions."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "loop_type": self.loop_type,
            "loop_actions": serialize_actions(self.loop_actions),
        })
        if self.loop_type == "count": base_dict["count"] = self.count
        if self.loop_type == "for_each": base_dict["list_variable_name"] = self.list_variable_name
        if self.loop_type == "while":
             base_dict["condition_type"] = self.condition_type
             if self.condition_type in ["element_present", "element_not_present"]: base_dict["selector"] = self.selector
             elif self.condition_type == "variable_equals":
                  base_dict["variable_name"] = self.variable_name; base_dict["expected_value"] = self.expected_value
             elif self.condition_type == "javascript_eval": base_dict["script"] = self.script
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from the loop_actions list, recursively."""
        nested = []
        for action in self.loop_actions:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        detail = ""
        if self.loop_type == "count": detail = f"{self.count} times"
        elif self.loop_type == "for_each": detail = f"for each item in '{self.list_variable_name}'"
        elif self.loop_type == "while": detail = f"while {self.condition_type} (...)"
        action_count = len(self.loop_actions)
        return f"{self.action_type}: {self.name} ({detail}, {action_count} actions)"
```

## src/core/actions/template_action.py

```python
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
        logger.warning(f"TemplateAction '{self.name}' execute() called directly. Expansion should occur in runner.")
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
```

## src/core/workflow/runner.py

```python
"""Workflow Runner module for AutoQliq.

Provides the WorkflowRunner class responsible for executing a sequence of actions,
managing context, and handling control flow actions like Loop, Conditional,
and ErrorHandling, plus Template expansion.
"""

import logging
import time # For timing execution
from typing import List, Optional, Dict, Any
import threading # For stop event checking
from datetime import datetime # For timestamps in log

# Core components
from src.core.interfaces import IWebDriver, IAction, ICredentialRepository, IWorkflowRepository # Added IWorkflowRepository
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError, AutoQliqError, ValidationError, RepositoryError, SerializationError

# Import control flow actions to check types
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction # Added
# Need factory for deserializing templates
from src.core.actions.factory import ActionFactory

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """
    Executes a given sequence of actions using a web driver.

    Handles iterating through actions, passing context (driver, repo),
    managing execution context (e.g., loop variables), handling control flow actions,
    and expanding TemplateActions. Now returns a detailed execution log dictionary.

    Attributes:
        driver (IWebDriver): The web driver instance for browser interaction.
        credential_repo (Optional[ICredentialRepository]): Repository for credentials.
        workflow_repo (Optional[IWorkflowRepository]): Repository for workflows/templates (needed for template expansion).
        stop_event (Optional[threading.Event]): Event to signal graceful stop request.
    """

    def __init__(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        workflow_repo: Optional[IWorkflowRepository] = None, # Added repo for templates
        stop_event: Optional[threading.Event] = None # Added stop event
    ):
        """Initialize the WorkflowRunner."""
        if driver is None: raise ValueError("WebDriver instance cannot be None.")
        self.driver = driver
        self.credential_repo = credential_repo
        self.workflow_repo = workflow_repo # Store workflow repo reference
        self.stop_event = stop_event # Store stop event
        logger.info("WorkflowRunner initialized.")
        if credential_repo: logger.debug(f"Using credential repository: {type(credential_repo).__name__}")
        if workflow_repo: logger.debug(f"Using workflow repository: {type(workflow_repo).__name__}")
        if stop_event: logger.debug("Stop event provided for cancellation check.")


    def run_single_action(self, action: IAction, context: Dict[str, Any]) -> ActionResult:
         """Executes a single action within a given context, handling its exceptions."""
         # Check for stop request *before* executing the action
         if self.stop_event and self.stop_event.is_set():
              logger.info(f"Stop requested before executing action '{action.name}'")
              raise WorkflowError("Workflow execution stopped by request.")

         action_display_name = f"{action.name} ({action.action_type})"
         logger.debug(f"Runner executing single action: {action_display_name}")
         try:
              action.validate() # Validate before execution
              result = action.execute(self.driver, self.credential_repo, context) # Pass context
              if not isinstance(result, ActionResult):
                   logger.error(f"Action '{action_display_name}' did not return ActionResult (got {type(result).__name__}).")
                   return ActionResult.failure(f"Action '{action.name}' implementation error: Invalid return type.")
              if not result.is_success(): logger.warning(f"Action '{action_display_name}' returned failure: {result.message}")
              else: logger.debug(f"Action '{action_display_name}' returned success.")
              return result
         except ValidationError as e:
              logger.error(f"Validation failed for action '{action_display_name}': {e}")
              return ActionResult.failure(f"Action validation failed: {e}")
         except ActionError as e:
              logger.error(f"ActionError during execution of action '{action_display_name}': {e}")
              return ActionResult.failure(f"Action execution error: {e}")
         except Exception as e:
              logger.exception(f"Unexpected exception during execution of action '{action_display_name}'")
              wrapped_error = ActionError(f"Unexpected exception: {e}", action_name=action.name, action_type=action.action_type, cause=e)
              return ActionResult.failure(str(wrapped_error))


    def _expand_template(self, template_action: TemplateAction, context: Dict[str, Any]) -> List[IAction]:
        """Loads and deserializes actions from a named template."""
        template_name = template_action.template_name
        logger.info(f"Expanding template '{template_name}' within action '{template_action.name}'.")
        if not self.workflow_repo:
             raise ActionError("Workflow repository required for template expansion.", action_name=template_action.name)
        try:
             actions_data = self.workflow_repo.load_template(template_name) # Raises RepositoryError if not found
             if not actions_data: return []
             expanded_actions = [ActionFactory.create_action(data) for data in actions_data] # Raises ActionError/SerializationError
             logger.info(f"Expanded template '{template_name}' into {len(expanded_actions)} actions.")
             return expanded_actions
        except (RepositoryError, ActionError, SerializationError, ValidationError, TypeError) as e:
             raise ActionError(f"Failed to load/expand template '{template_name}': {e}", action_name=template_action.name, cause=e) from e
        except Exception as e:
             raise ActionError(f"Unexpected error expanding template '{template_name}': {e}", action_name=template_action.name, cause=e) from e


    def _execute_actions(self, actions: List[IAction], context: Dict[str, Any], workflow_name: str, log_prefix: str = "") -> List[ActionResult]:
        """Internal helper to execute actions, handling control flow, context, templates, stop events."""
        block_results: List[ActionResult] = []
        current_action_index = 0
        action_list_copy = list(actions) # Operate on a copy

        while current_action_index < len(action_list_copy):
            # Check stop flag before *every* action attempt
            if self.stop_event and self.stop_event.is_set():
                logger.info(f"{log_prefix}Stop requested before Step {current_action_index + 1}.")
                raise WorkflowError("Workflow execution stopped by request.")

            action = action_list_copy[current_action_index]
            step_num = current_action_index + 1
            action_display = f"{action.name} ({action.action_type}, {log_prefix}Step {step_num})"

            result: Optional[ActionResult] = None
            try:
                # --- Expand TemplateAction ---
                if isinstance(action, TemplateAction):
                    logger.debug(f"Runner expanding template: {action_display}")
                    expanded_actions = self._expand_template(action, context) # Raises ActionError
                    action_list_copy = action_list_copy[:current_action_index] + expanded_actions + action_list_copy[current_action_index+1:]
                    logger.debug(f"Replaced template with {len(expanded_actions)} actions. New total: {len(action_list_copy)}")
                    continue # Restart loop for first expanded action

                # --- Execute Action ---
                elif isinstance(action, ConditionalAction): result = self._execute_conditional(action, context, workflow_name, f"{log_prefix}Cond {step_num}: ")
                elif isinstance(action, LoopAction): result = self._execute_loop(action, context, workflow_name, f"{log_prefix}Loop {step_num}: ")
                elif isinstance(action, ErrorHandlingAction): result = self._execute_error_handler(action, context, workflow_name, f"{log_prefix}ErrH {step_num}: ")
                elif isinstance(action, IAction): result = self.run_single_action(action, context) # Handles internal errors -> ActionResult
                else: raise WorkflowError(f"Invalid item at {log_prefix}Step {step_num}: {type(action).__name__}.")

            except ActionError as e:
                 logger.error(f"ActionError during execution of {action_display}: {e}")
                 raise ActionError(f"Failure during {action_display}: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e
            except WorkflowError as e: # Catch stop requests or other runner issues
                 raise e
            except Exception as e:
                  logger.exception(f"Unexpected error processing {action_display}")
                  raise ActionError(f"Unexpected error processing {action_display}: {e}", action.name, action.action_type, cause=e) from e

            # --- Process Result ---
            if result is None: raise WorkflowError(f"Execution returned None for {action_display}", workflow_name)

            block_results.append(result) # Append result for logging
            if not result.is_success():
                 logger.error(f"Action '{action_display}' failed. Stopping block.")
                 raise ActionError(result.message or f"Action '{action.name}' failed.", action_name=action.name, action_type=action.action_type)

            current_action_index += 1 # Move to next action

        return block_results


    def _execute_conditional(self, action: ConditionalAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
         """Executes a ConditionalAction's appropriate branch."""
         try:
              condition_met = action._evaluate_condition(self.driver, context) # Raises ActionError(WebDriverError)
              logger.info(f"{log_prefix}Condition '{action.condition_type}' evaluated to {condition_met}")
              branch_to_run = action.true_branch if condition_met else action.false_branch
              branch_name = "'true'" if condition_met else "'false'"
              if not branch_to_run: return ActionResult.success(f"Cond {condition_met}, {branch_name} empty.")

              logger.info(f"{log_prefix}Executing {branch_name} branch...")
              # Recursively execute - raises ActionError on failure
              branch_results = self._execute_actions(branch_to_run, context, workflow_name, f"{log_prefix}{branch_name}: ")
              logger.info(f"{log_prefix}Successfully executed {branch_name} branch.")
              return ActionResult.success(f"Cond {condition_met}, {branch_name} executed ({len(branch_results)} actions).")
         except Exception as e:
               # Catch errors during condition eval or branch exec
               logger.error(f"{log_prefix}Conditional failed: {e}", exc_info=False)
               raise ActionError(f"Conditional failed: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e


    def _execute_loop(self, action: LoopAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
         """Executes a LoopAction."""
         iterations_executed = 0
         try:
             if action.loop_type == "count":
                 iterations_total = action.count or 0
                 logger.info(f"{log_prefix}Starting 'count' loop for {iterations_total} iterations.")
                 for i in range(iterations_total):
                     iteration_num = i + 1; iter_log_prefix = f"{log_prefix}Iter {iteration_num}: "
                     logger.info(f"{iter_log_prefix}Starting.")
                     iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total})
                     self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix) # Raises ActionError
                     iterations_executed = iteration_num
             elif action.loop_type == "for_each":
                 if not action.list_variable_name: raise ActionError("list_variable_name missing", action.name)
                 target_list = context.get(action.list_variable_name)
                 if not isinstance(target_list, list): raise ActionError(f"Context var '{action.list_variable_name}' not list.", action.name)
                 iterations_total = len(target_list)
                 logger.info(f"{log_prefix}Starting 'for_each' over '{action.list_variable_name}' ({iterations_total} items).")
                 for i, item in enumerate(target_list):
                      iteration_num = i + 1; iter_log_prefix = f"{log_prefix}Item {iteration_num}: "
                      logger.info(f"{iter_log_prefix}Starting.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total, 'loop_item': item})
                      self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
             elif action.loop_type == "while":
                  logger.info(f"{log_prefix}Starting 'while' loop.")
                  max_while = 1000; i = 0
                  while i < max_while:
                       iteration_num = i + 1; iter_log_prefix = f"{log_prefix}While Iter {iteration_num}: "
                       logger.debug(f"{iter_log_prefix}Evaluating condition...")
                       condition_met = action._evaluate_while_condition(self.driver, context) # Raises ActionError
                       if not condition_met: logger.info(f"{iter_log_prefix}Condition false. Exiting loop."); break
                       logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                       iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num})
                       self._execute_actions(action.loop_actions, iter_context, workflow_name, iter_log_prefix) # Raises ActionError
                       iterations_executed = iteration_num
                       i += 1
                  else: raise ActionError(f"While loop exceeded max iterations ({max_while}).", action.name)
             else:
                 raise ActionError(f"Unsupported loop_type '{action.loop_type}'", action.name)

             logger.info(f"{log_prefix}Loop completed {iterations_executed} iterations.")
             return ActionResult.success(f"Loop completed {iterations_executed} iterations.")
         except Exception as e:
              # Catch errors from condition eval or nested block exec
              logger.error(f"{log_prefix}Loop failed: {e}", exc_info=False)
              raise ActionError(f"Loop failed: {e}", action_name=action.name, action_type=action.action_type, cause=e) from e


    def _execute_error_handler(self, action: ErrorHandlingAction, context: Dict[str, Any], workflow_name: str, log_prefix: str) -> ActionResult:
         """Executes an ErrorHandlingAction (Try/Catch)."""
         logger.info(f"{log_prefix}Entering 'try' block.")
         original_error: Optional[Exception] = None
         try:
              # Execute try block. Raises ActionError on failure.
              self._execute_actions(action.try_actions, context, workflow_name, f"{log_prefix}Try: ")
              logger.info(f"{log_prefix}'try' block succeeded.")
              return ActionResult.success("Try block succeeded.")
         except Exception as try_error:
              original_error = try_error
              logger.warning(f"{log_prefix}'try' block failed: {try_error}", exc_info=False)
              if not action.catch_actions:
                   logger.warning(f"{log_prefix}No 'catch' block. Error not handled.")
                   raise # Re-raise original error
              else:
                   logger.info(f"{log_prefix}Executing 'catch' block...")
                   catch_context = context.copy()
                   catch_context['try_block_error_message'] = str(try_error)
                   catch_context['try_block_error_type'] = type(try_error).__name__
                   try:
                        # Execute catch block. Raises ActionError on failure.
                        self._execute_actions(action.catch_actions, catch_context, workflow_name, f"{log_prefix}Catch: ")
                        logger.info(f"{log_prefix}'catch' block succeeded after handling error.")
                        return ActionResult.success(f"Error handled by 'catch': {str(try_error)[:100]}")
                   except Exception as catch_error:
                        logger.error(f"{log_prefix}'catch' block failed: {catch_error}", exc_info=True)
                        # Raise new error indicating catch failure
                        raise ActionError(f"'catch' block failed after 'try' error ({try_error}): {catch_error}",
                                          action_name=action.name, cause=catch_error) from catch_error


    def run(self, actions: List[IAction], workflow_name: str = "Unnamed Workflow") -> Dict[str, Any]:
        """
        Execute actions sequentially, returning detailed log data.

        Args:
            actions: Sequence of actions.
            workflow_name: Name of the workflow.

        Returns:
            Execution log dictionary.
        """
        if not isinstance(actions, list): raise TypeError("Actions must be list.")
        if not workflow_name: workflow_name = "Unnamed Workflow"

        logger.info(f"RUNNER: Starting workflow '{workflow_name}' with {len(actions)} top-level actions.")
        execution_context: Dict[str, Any] = {}
        all_action_results: List[ActionResult] = []
        start_time = time.time()
        final_status = "UNKNOWN"
        error_message: Optional[str] = None

        try:
            all_action_results = self._execute_actions(actions, execution_context, workflow_name, log_prefix="")
            final_status = "SUCCESS"
            logger.info(f"RUNNER: Workflow '{workflow_name}' completed successfully.")
        except ActionError as e:
             final_status = "FAILED"; error_message = str(e)
             logger.error(f"RUNNER: Workflow '{workflow_name}' failed. Last error in action '{e.action_name}': {e}", exc_info=False)
             # Append failure result if possible? The block execution stops on raise.
             # We only have results up to the point of failure.
        except WorkflowError as e: # Catch stop requests or other runner issues
             if "stopped by request" in str(e).lower(): final_status = "STOPPED"; error_message = "Execution stopped by user request."
             else: final_status = "FAILED"; error_message = str(e)
             logger.error(f"RUNNER: Workflow '{workflow_name}' stopped or failed: {error_message}")
        except Exception as e:
             final_status = "FAILED"; error_message = f"Unexpected runner error: {e}"
             logger.exception(f"RUNNER: Unexpected error during workflow '{workflow_name}' execution.")
        finally:
            end_time = time.time(); duration = end_time - start_time
            logger.info(f"RUNNER: Workflow '{workflow_name}' finished. Status: {final_status}, Duration: {duration:.2f}s")
            execution_log = {
                 "workflow_name": workflow_name,
                 "start_time_iso": datetime.fromtimestamp(start_time).isoformat(),
                 "end_time_iso": datetime.fromtimestamp(end_time).isoformat(),
                 "duration_seconds": round(duration, 2),
                 "final_status": final_status,
                 "error_message": error_message,
                 "action_results": [{"status": res.status.value, "message": res.message} for res in all_action_results]
            }
            return execution_log
```

## src/core/workflow/workflow.py

```python
"""Workflow module for AutoQliq.

Provides the Workflow class that represents a sequence of actions to be executed.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

from src.core.interfaces.action import IAction
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Workflow:
    """
    Represents a sequence of actions to be executed.
    
    A workflow is the core entity in AutoQliq, consisting of a sequence of actions
    that will be executed in order by the WorkflowRunner.
    
    Attributes:
        id (str): Unique identifier for the workflow.
        name (str): User-friendly name for the workflow.
        description (str): Optional description of the workflow's purpose.
        actions (List[IAction]): Sequence of actions to be executed.
        metadata (Dict[str, Any]): Additional metadata about the workflow.
    """
    
    def __init__(
        self,
        name: str,
        actions: Optional[List[IAction]] = None,
        description: str = "",
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a new Workflow instance.
        
        Args:
            name: User-friendly name for the workflow.
            actions: List of actions to be executed (default empty list).
            description: Optional description of the workflow's purpose.
            workflow_id: Optional unique identifier (generated if not provided).
            metadata: Optional additional metadata.
        
        Raises:
            ValidationError: If name is empty or actions contains non-IAction objects.
        """
        if not name:
            raise ValidationError("Workflow name cannot be empty.")
        
        self.id = workflow_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.actions = actions or []
        self.metadata = metadata or {}
        
        # Validate actions
        for i, action in enumerate(self.actions):
            if not isinstance(action, IAction):
                raise ValidationError(f"Item at index {i} is not an IAction: {type(action).__name__}")
    
    def add_action(self, action: IAction) -> None:
        """Add an action to the workflow.
        
        Args:
            action: The action to add.
            
        Raises:
            ValidationError: If action is not an IAction.
        """
        if not isinstance(action, IAction):
            raise ValidationError(f"Cannot add non-IAction object: {type(action).__name__}")
        
        self.actions.append(action)
        logger.debug(f"Added action '{action.name}' to workflow '{self.name}'")
    
    def remove_action(self, index: int) -> IAction:
        """Remove an action from the workflow by index.
        
        Args:
            index: The index of the action to remove.
            
        Returns:
            The removed action.
            
        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self.actions):
            raise IndexError(f"Action index {index} out of range (0-{len(self.actions)-1})")
        
        action = self.actions.pop(index)
        logger.debug(f"Removed action '{action.name}' from workflow '{self.name}'")
        return action
    
    def move_action(self, from_index: int, to_index: int) -> None:
        """Move an action from one position to another.
        
        Args:
            from_index: The current index of the action.
            to_index: The target index for the action.
            
        Raises:
            IndexError: If either index is out of range.
        """
        if from_index < 0 or from_index >= len(self.actions):
            raise IndexError(f"Source index {from_index} out of range (0-{len(self.actions)-1})")
        
        # Allow to_index to be equal to len(self.actions) to move to the end
        if to_index < 0 or to_index > len(self.actions):
            raise IndexError(f"Target index {to_index} out of range (0-{len(self.actions)})")
        
        if from_index == to_index:
            return  # No change needed
        
        action = self.actions.pop(from_index)
        self.actions.insert(to_index, action)
        logger.debug(f"Moved action '{action.name}' from position {from_index} to {to_index}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the workflow to a dictionary.
        
        Returns:
            A dictionary representation of the workflow.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], actions: List[IAction]) -> 'Workflow':
        """Create a Workflow instance from a dictionary and pre-deserialized actions.
        
        Args:
            data: Dictionary containing workflow data.
            actions: List of already deserialized IAction objects.
            
        Returns:
            A new Workflow instance.
            
        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict, got {type(data).__name__}")
        
        required_fields = ["name"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        return cls(
            name=data["name"],
            actions=actions,
            description=data.get("description", ""),
            workflow_id=data.get("id"),
            metadata=data.get("metadata", {})
        )
    
    def validate(self) -> bool:
        """Validate the workflow and all its actions.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not self.name:
            raise ValidationError("Workflow name cannot be empty.")
        
        for i, action in enumerate(self.actions):
            try:
                action.validate()
            except ValidationError as e:
                raise ValidationError(f"Action at index {i} ({action.name}) failed validation: {e}")
        
        return True
    
    def __str__(self) -> str:
        """Return a string representation of the workflow."""
        return f"Workflow(id={self.id}, name={self.name}, actions={len(self.actions)})"
```

## src/core/workflow/errors.py

```python
"""Workflow-specific error classes for AutoQliq."""

from src.core.exceptions import AutoQliqError


class WorkflowError(AutoQliqError):
    """Base class for workflow-related errors."""
    
    def __init__(self, message: str, workflow_name: str = None, cause: Exception = None):
        """Initialize a WorkflowError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow where the error occurred.
            cause: Optional exception that caused this error.
        """
        self.workflow_name = workflow_name
        super().__init__(message, cause)
        
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.workflow_name:
            return f"Workflow '{self.workflow_name}': {self.message}"
        return self.message


class WorkflowNotFoundError(WorkflowError):
    """Error raised when a workflow cannot be found."""
    
    def __init__(self, workflow_id: str, cause: Exception = None):
        """Initialize a WorkflowNotFoundError.
        
        Args:
            workflow_id: ID of the workflow that could not be found.
            cause: Optional exception that caused this error.
        """
        super().__init__(f"Workflow not found: {workflow_id}", cause=cause)
        self.workflow_id = workflow_id


class WorkflowValidationError(WorkflowError):
    """Error raised when a workflow fails validation."""
    
    def __init__(self, message: str, workflow_name: str = None, cause: Exception = None):
        """Initialize a WorkflowValidationError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow that failed validation.
            cause: Optional exception that caused this error.
        """
        super().__init__(f"Validation error: {message}", workflow_name, cause)


class WorkflowExecutionError(WorkflowError):
    """Error raised during workflow execution."""
    
    def __init__(self, message: str, workflow_name: str = None, action_name: str = None, cause: Exception = None):
        """Initialize a WorkflowExecutionError.
        
        Args:
            message: Error message.
            workflow_name: Optional name of the workflow being executed.
            action_name: Optional name of the action that failed.
            cause: Optional exception that caused this error.
        """
        self.action_name = action_name
        if action_name:
            full_message = f"Execution error in action '{action_name}': {message}"
        else:
            full_message = f"Execution error: {message}"
        super().__init__(full_message, workflow_name, cause)
```

## src/core/exceptions.py

```python
"""Custom exceptions for the AutoQliq application."""

from typing import Optional


class AutoQliqError(Exception):
    """Base exception for all AutoQliq-specific errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.message = message
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.cause:
            # Ensure cause message is included, especially for wrapped standard exceptions
            cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
            return f"{self.message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return self.message

    def __str__(self) -> str:
        return self._format_message()

    def __repr__(self) -> str:
        cause_repr = f", cause={self.cause!r}" if self.cause else ""
        return f"{self.__class__.__name__}(message={self.message!r}{cause_repr})"


class ConfigError(AutoQliqError):
    """Raised for configuration-related errors."""
    pass


class WorkflowError(AutoQliqError):
    """Raised for errors during workflow definition or execution."""
    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        action_name: Optional[str] = None,
        action_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.workflow_name = workflow_name
        self.action_name = action_name
        self.action_type = action_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.workflow_name: context.append(f"workflow='{self.workflow_name}'")
        if self.action_name: context.append(f"action='{self.action_name}'")
        if self.action_type: context.append(f"type='{self.action_type}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class ActionError(AutoQliqError):
    """Raised for errors during the execution or configuration of a specific action."""
    def __init__(
        self,
        message: str,
        action_name: Optional[str] = None,
        action_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.action_name = action_name
        self.action_type = action_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.action_name: context.append(f"action='{self.action_name}'")
        if self.action_type: context.append(f"type='{self.action_type}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class WebDriverError(AutoQliqError):
    """Raised for errors related to WebDriver operations."""
    def __init__(
        self,
        message: str,
        driver_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.driver_type = driver_type
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (driver: {self.driver_type})" if self.driver_type else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class RepositoryError(AutoQliqError):
    """Raised for errors related to repository operations (persistence)."""
    def __init__(
        self,
        message: str,
        repository_name: Optional[str] = None,
        entity_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.repository_name = repository_name
        self.entity_id = entity_id
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = []
        if self.repository_name: context.append(f"repository='{self.repository_name}'")
        if self.entity_id: context.append(f"id='{self.entity_id}'")
        context_str = f" ({', '.join(context)})" if context else ""
        base_message = f"{self.message}{context_str}"

        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class CredentialError(RepositoryError):
    """Raised specifically for errors related to credential storage or retrieval."""
    def __init__(
        self,
        message: str,
        credential_name: Optional[str] = None, # Specific alias for entity_id
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message,
            repository_name="CredentialRepository",
            entity_id=credential_name,
            cause=cause
        )
        self.credential_name = credential_name # Keep specific attribute if needed


class SerializationError(AutoQliqError):
    """Raised for errors during serialization or deserialization."""
    pass


class ValidationError(AutoQliqError):
    """Raised when data validation fails."""
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.field_name = field_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (field: {self.field_name})" if self.field_name else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


class UIError(AutoQliqError):
    """Raised for errors originating from the UI layer."""
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        self.component_name = component_name
        super().__init__(message, cause)

    def _format_message(self) -> str:
        context = f" (component: {self.component_name})" if self.component_name else ""
        base_message = f"{self.message}{context}"
        if self.cause:
             # Ensure cause message is included
             cause_msg = str(self.cause) if str(self.cause) else type(self.cause).__name__
             return f"{base_message} (Caused by: {type(self.cause).__name__}: {cause_msg})"
        return base_message


# --- Deprecated / Compatibility ---
class LoginFailedError(ActionError):
    """Raised when login fails due to incorrect credentials or other issues.
    Deprecated: Prefer raising ActionError or WorkflowError with appropriate context.
    """
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message, action_name="Login", cause=cause)
```

## src/core/action_result.py

```python
from enum import Enum
from typing import Optional


class ActionStatus(Enum):
    """
    Enum representing the status of an action execution.
    """
    SUCCESS = "success"
    FAILURE = "failure"


class ActionResult:
    """
    Represents the result of an action execution.

    Attributes:
        status: The status of the action execution (SUCCESS or FAILURE)
        message: An optional message providing details about the result
    """

    def __init__(self, status: ActionStatus, message: Optional[str] = None):
        """
        Initialize an ActionResult.

        Args:
            status: The status of the action execution
            message: An optional message providing details about the result
        """
        if not isinstance(status, ActionStatus):
            raise TypeError("status must be an instance of ActionStatus Enum")
        self.status = status
        self.message = message

    def is_success(self) -> bool:
        """
        Check if the result represents a successful execution.

        Returns:
            True if the status is SUCCESS, False otherwise
        """
        return self.status == ActionStatus.SUCCESS

    @classmethod
    def success(cls, message: Optional[str] = None) -> 'ActionResult':
        """
        Create a success result.

        Args:
            message: An optional message providing details about the result

        Returns:
            An ActionResult with SUCCESS status
        """
        return cls(ActionStatus.SUCCESS, message)

    @classmethod
    def failure(cls, message: str = "Action failed") -> 'ActionResult':
        """
        Create a failure result.

        Args:
            message: A message providing details about the failure

        Returns:
            An ActionResult with FAILURE status
        """
        return cls(ActionStatus.FAILURE, message)

    def __str__(self) -> str:
        """
        Get a string representation of the result.

        Returns:
            A string representation of the result
        """
        status_str = "Success" if self.is_success() else "Failure"
        if self.message:
            return f"{status_str}: {self.message}"
        return status_str

    def __repr__(self) -> str:
        """
        Get a developer-friendly string representation of the result.

        Returns:
            A string representation of the result instance.
        """
        return f"ActionResult(status={self.status}, message='{self.message}')"
```

## src/application/services/credential_service.py

```python
"""Credential service implementation for AutoQliq."""
import logging
from typing import Dict, List, Any, Optional

# Use werkzeug for hashing - ensure it's in requirements.txt
try:
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).critical(
        "Werkzeug library not found. Password hashing disabled. Install using: pip install werkzeug"
    )
    WERKZEUG_AVAILABLE = False
    # Define dummy functions if werkzeug is not installed to avoid crashing
    # WARNING: This is insecure and only for preventing startup failure.
    def generate_password_hash(password: str, method: str = 'plaintext', salt_length: int = 0) -> str: # type: ignore
        logging.error("Werkzeug not found. Storing password as plain text (INSECURE).")
        return f"plaintext:{password}"
    def check_password_hash(pwhash: Optional[str], password: str) -> bool: # type: ignore
        logging.error("Werkzeug not found. Checking password against plain text (INSECURE).")
        if pwhash is None: return False
        if pwhash.startswith("plaintext:"):
             return pwhash[len("plaintext:"):] == password
        return False # Cannot check real hashes without werkzeug

# Core dependencies
from src.core.interfaces import ICredentialRepository
from src.core.interfaces.service import ICredentialService
from src.core.exceptions import CredentialError, ValidationError, AutoQliqError, RepositoryError

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
# Configuration
from src.config import config # Import configured instance

logger = logging.getLogger(__name__)


class CredentialService(ICredentialService):
    """
    Implementation of ICredentialService. Manages credential lifecycle including hashing.
    Uses werkzeug for password hashing if available.
    """

    def __init__(self, credential_repository: ICredentialRepository):
        """Initialize a new CredentialService."""
        if credential_repository is None:
            raise ValueError("Credential repository cannot be None.")
        self.credential_repository = credential_repository
        # Load hashing config only if werkzeug is available
        self.hash_method = config.password_hash_method if WERKZEUG_AVAILABLE else 'plaintext'
        self.salt_length = config.password_salt_length if WERKZEUG_AVAILABLE else 0
        logger.info(f"CredentialService initialized. Hashing available: {WERKZEUG_AVAILABLE}")
        if not WERKZEUG_AVAILABLE:
             logger.critical("SECURITY WARNING: Werkzeug not installed, passwords stored/checked as plaintext.")

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to create credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def create_credential(self, name: str, username: str, password: str) -> bool:
        """Create a new credential, storing a hashed password."""
        logger.info(f"Attempting to create credential: {name}")
        if not name or not username or not password:
             raise ValidationError("Credential name, username, and password cannot be empty.")

        # Check if credential already exists
        existing = self.credential_repository.get_by_name(name) # Repo handles name validation
        if existing:
             raise CredentialError(f"Credential '{name}' already exists.", credential_name=name)

        try:
            # Hash the password before saving
            hashed_password = generate_password_hash(password, method=self.hash_method, salt_length=self.salt_length)
            logger.debug(f"Password hashed for credential '{name}'.")
        except Exception as hash_e:
             logger.error(f"Password hashing failed for credential '{name}': {hash_e}", exc_info=True)
             raise CredentialError(f"Failed to secure password for credential '{name}'.", credential_name=name, cause=hash_e) from hash_e

        credential_data = {"name": name, "username": username, "password": hashed_password}
        # Repository save handles actual storage and potential underlying errors
        self.credential_repository.save(credential_data)
        logger.info(f"Credential '{name}' created successfully.")
        return True

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to delete credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def delete_credential(self, name: str) -> bool:
        """Delete a credential by name."""
        logger.info(f"Attempting to delete credential: {name}")
        deleted = self.credential_repository.delete(name) # Repo handles validation and storage
        if deleted:
            logger.info(f"Credential '{name}' deleted successfully.")
        else:
            logger.warning(f"Credential '{name}' not found for deletion.")
        return deleted

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to retrieve credential details", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def get_credential(self, name: str) -> Optional[Dict[str, str]]:
        """Get credential details (including password hash) by name."""
        logger.debug(f"Retrieving credential details (incl. hash): {name}")
        credential = self.credential_repository.get_by_name(name) # Repo handles validation
        if credential:
             logger.debug(f"Credential '{name}' details found.")
        else:
             logger.debug(f"Credential '{name}' not found.")
        # WARNING: Returns the HASH, not the plain password
        return credential

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to list credentials", reraise_types=(RepositoryError,))
    def list_credentials(self) -> List[str]:
        """Get a list of available credential names."""
        logger.debug("Listing all credentials.")
        names = self.credential_repository.list_credentials() # Repo handles storage interaction
        logger.debug(f"Found {len(names)} credentials.")
        return names

    @log_method_call(logger)
    @handle_exceptions(CredentialError, "Failed to verify credential", reraise_types=(CredentialError, ValidationError, RepositoryError))
    def verify_credential(self, name: str, password_to_check: str) -> bool:
        """Verify if the provided password matches the stored hash for the credential."""
        logger.info(f"Verifying password for credential: {name}")
        if not password_to_check:
             logger.warning(f"Password check for '{name}' attempted with empty password.")
             return False

        # Get the stored credential (contains the hash)
        credential_data = self.credential_repository.get_by_name(name) # Repo handles name validation
        if not credential_data:
             logger.warning(f"Credential '{name}' not found for verification.")
             return False

        stored_hash = credential_data.get("password")
        if not stored_hash:
             logger.error(f"Stored credential '{name}' is missing password hash.")
             return False

        try:
             # Use check_password_hash to compare
             is_match = check_password_hash(stored_hash, password_to_check)
             if is_match:
                 logger.info(f"Password verification successful for credential '{name}'.")
             else:
                 logger.warning(f"Password verification failed for credential '{name}'.")
             return is_match
        except Exception as check_e:
            # Handle potential errors during hash checking (e.g., malformed hash, library errors)
            logger.error(f"Error during password hash check for credential '{name}': {check_e}", exc_info=True)
            # Treat check errors as verification failure
            return False
```

## src/application/services/workflow_service.py

```python
"""Workflow service implementation for AutoQliq."""
import logging
import time
from typing import Dict, List, Any, Optional

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository, ICredentialRepository, IWebDriver
from src.core.interfaces.service import IWorkflowService, IWebDriverService # Use Service Interfaces
from src.core.workflow.runner import WorkflowRunner
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, ValidationError, AutoQliqError, ActionError, RepositoryError, SerializationError

# Infrastructure dependencies (Only WebDriverService interface needed here)

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
# Need BrowserType for run_workflow signature
from src.infrastructure.webdrivers.base import BrowserType

logger = logging.getLogger(__name__)


class WorkflowService(IWorkflowService):
    """
    Implementation of IWorkflowService. Orchestrates workflow creation, management, and execution.

    Connects repositories, WebDriver service, and the workflow runner.
    """

    def __init__(
        self,
        workflow_repository: IWorkflowRepository,
        credential_repository: ICredentialRepository,
        webdriver_service: IWebDriverService # Inject WebDriver service
    ):
        """Initialize a new WorkflowService."""
        if workflow_repository is None: raise ValueError("Workflow repository cannot be None.")
        if credential_repository is None: raise ValueError("Credential repository cannot be None.")
        if webdriver_service is None: raise ValueError("WebDriver service cannot be None.")

        self.workflow_repository = workflow_repository
        self.credential_repository = credential_repository
        self.webdriver_service = webdriver_service # Store the service
        logger.info("WorkflowService initialized.")

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to create workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> bool:
        """Create a new empty workflow."""
        logger.info(f"SERVICE: Attempting to create workflow: {name}")
        self.workflow_repository.create_workflow(name) # Raises error if exists or invalid
        logger.info(f"SERVICE: Workflow '{name}' created successfully.")
        return True

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to delete workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow by name."""
        logger.info(f"SERVICE: Attempting to delete workflow: {name}")
        deleted = self.workflow_repository.delete(name) # Raises error if invalid name
        if deleted: logger.info(f"SERVICE: Workflow '{name}' deleted successfully.")
        else: logger.warning(f"SERVICE: Workflow '{name}' not found for deletion.")
        return deleted

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to list workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]:
        """Get a list of available workflow names."""
        logger.debug("SERVICE: Listing all workflows.")
        workflows = self.workflow_repository.list_workflows()
        logger.debug(f"SERVICE: Found {len(workflows)} workflows.")
        return workflows

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to get workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def get_workflow(self, name: str) -> List[IAction]:
        """Get the actions for a workflow by name."""
        logger.debug(f"SERVICE: Retrieving workflow: {name}")
        actions = self.workflow_repository.load(name) # Raises error if not found etc.
        logger.debug(f"SERVICE: Workflow '{name}' retrieved with {len(actions)} actions.")
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to save workflow", reraise_types=(WorkflowError, ValidationError, SerializationError, RepositoryError))
    def save_workflow(self, name: str, actions: List[IAction]) -> bool:
        """Save a workflow with its actions."""
        logger.info(f"SERVICE: Attempting to save workflow: {name} with {len(actions)} actions.")
        self.workflow_repository.save(name, actions) # Raises errors on failure
        logger.info(f"SERVICE: Workflow '{name}' saved successfully.")
        return True

    @log_method_call(logger)
    # NOTE: run_workflow handles its own complex error handling/cleanup, so no @handle_exceptions here
    def run_workflow(
        self,
        name: str,
        credential_name: Optional[str] = None,
        browser_type: BrowserType = BrowserType.CHROME
        # Add callback for progress/logging?
        # log_callback: Optional[Callable[[str], None]] = None
    ) -> List[Dict[str, Any]]:
        """Run a workflow, managing WebDriver lifecycle via WebDriverService."""
        logger.info(f"SERVICE: Preparing to run workflow '{name}' with credential '{credential_name}' using {browser_type.value}")
        driver: Optional[IWebDriver] = None # Initialize driver to None
        start_time = time.time()
        action_results: List[Dict[str, Any]] = [] # Use specific type

        try:
            # 1. Load Workflow Actions (using self method which has error handling)
            logger.debug(f"SERVICE: Loading actions for workflow '{name}'")
            actions = self.get_workflow(name) # Raises WorkflowError if fails

            # 2. Validate Credential Name (basic check, repo checks existence later)
            if credential_name:
                if not isinstance(credential_name, str) or not credential_name:
                     raise ValidationError("Credential name must be a non-empty string if provided.", field_name="credential_name")
                 # Optionally check if credential exists here using CredentialService?
                 # if not self.credential_service.get_credential(credential_name):
                 #     raise CredentialError(...)

            # 3. Create WebDriver using WebDriverService
            logger.debug(f"SERVICE: Creating {browser_type.value} WebDriver via service...")
            # Pass browser type as string name to service
            driver = self.webdriver_service.create_web_driver(browser_type_str=browser_type.value) # Raises WebDriverError/ConfigError

            # 4. Create and Run Workflow Runner
            # WorkflowRunner needs the driver instance and the Credential Repository
            runner = WorkflowRunner(driver, self.credential_repository)
            logger.info(f"SERVICE: Executing {len(actions)} actions for workflow '{name}'...")
            # WorkflowRunner's run method now raises WorkflowError/ActionError on failure
            results_list = runner.run(actions, workflow_name=name) # Pass name for context

            # 5. Convert ActionResult objects to simple dictionaries for return
            action_results = [{"status": res.status.value, "message": res.message} for res in results_list]
            logger.info(f"SERVICE: Workflow '{name}' completed successfully.")
            return action_results

        # Specific exceptions are caught first
        except (ActionError, CredentialError, WebDriverError, ValidationError, SerializationError, RepositoryError, ConfigError) as e:
             error_msg = f"Workflow '{name}' failed: {str(e)}"
             logger.error(f"SERVICE: {error_msg}", exc_info=isinstance(e, RepositoryError)) # Include traceback for repo errors potentially
             # Wrap in WorkflowError if not already one, preserving cause
             if not isinstance(e, WorkflowError):
                  raise WorkflowError(error_msg, workflow_name=name, cause=e) from e
             else:
                  raise # Re-raise original specific error
        # Catch any other unexpected errors
        except Exception as e:
             error_msg = f"Unexpected error running workflow '{name}': {str(e)}"
             logger.exception(f"SERVICE: {error_msg}") # Log full traceback
             raise WorkflowError(error_msg, workflow_name=name, cause=e) from e
        finally:
            # 6. Ensure WebDriver Cleanup via WebDriverService
            if driver:
                try:
                    logger.info(f"SERVICE: Disposing WebDriver for workflow '{name}'.")
                    self.webdriver_service.dispose_web_driver(driver)
                    # dispose_web_driver logs success/failure internally
                except Exception as q_e:
                    # Log error during cleanup, but don't mask original execution error
                    logger.error(f"SERVICE: Error disposing WebDriver after workflow '{name}': {q_e}", exc_info=True)
            duration = time.time() - start_time
            logger.info(f"SERVICE: Workflow '{name}' execution attempt finished in {duration:.2f}s.")


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Failed to get workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_workflow_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a workflow."""
        logger.debug(f"SERVICE: Retrieving metadata for workflow: {name}")
        # Repository handles validation and retrieval
        metadata = self.workflow_repository.get_metadata(name) # Raises error if not found etc.
        logger.debug(f"SERVICE: Metadata retrieved for workflow '{name}'.")
        return metadata
```

## src/application/services/webdriver_service.py

```python
"""WebDriver service implementation for AutoQliq."""
import logging
from typing import Dict, Any, Optional, List

# Core dependencies
from src.core.interfaces import IWebDriver
from src.core.interfaces.service import IWebDriverService
from src.core.exceptions import WebDriverError, ConfigError, AutoQliqError

# Infrastructure dependencies
from src.infrastructure.webdrivers.factory import WebDriverFactory
from src.infrastructure.webdrivers.base import BrowserType

# Common utilities
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
# Configuration
from src.config import config # Import configured instance

logger = logging.getLogger(__name__)


class WebDriverService(IWebDriverService):
    """
    Implementation of IWebDriverService. Manages WebDriver instances via a factory.

    Acts primarily as a facade over the WebDriverFactory, integrating configuration
    and ensuring consistent error handling and logging at the service layer.
    """

    def __init__(self, webdriver_factory: WebDriverFactory):
        """Initialize a new WebDriverService."""
        if webdriver_factory is None:
            raise ValueError("WebDriver factory cannot be None.")
        self.webdriver_factory = webdriver_factory
        logger.info("WebDriverService initialized.")

    @log_method_call(logger)
    @handle_exceptions(WebDriverError, "Failed to create web driver", reraise_types=(WebDriverError, ConfigError))
    def create_web_driver(
        self,
        browser_type_str: Optional[str] = None, # Make optional, use config default
        selenium_options: Optional[Any] = None, # Specific options object
        playwright_options: Optional[Dict[str, Any]] = None, # Specific options dict
        driver_type: str = "selenium", # 'selenium' or 'playwright'
        **kwargs: Any # Allow passing other factory options like implicit_wait_seconds
    ) -> IWebDriver:
        """Create a new web driver instance using the factory and configuration.

        Args:
            browser_type_str: Optional name of the browser type (e.g., "chrome").
                              If None, uses default from config.
            selenium_options: Specific Selenium options object (e.g., ChromeOptions).
            playwright_options: Specific Playwright launch options dictionary.
            driver_type: The driver backend ('selenium' or 'playwright').
            **kwargs: Additional arguments passed to the factory (e.g., `implicit_wait_seconds`, `webdriver_path`).

        Returns:
            A configured web driver instance conforming to IWebDriver.
        """
        browser_to_use_str = browser_type_str or config.default_browser
        logger.info(f"SERVICE: Requesting creation of {driver_type} driver for browser '{browser_to_use_str}'")

        try:
            # Convert string to BrowserType enum
            browser_enum = BrowserType.from_string(browser_to_use_str) # Raises ValueError
        except ValueError as e:
            # Convert ValueError to ConfigError
            raise ConfigError(str(e), cause=e) from e

        # Prepare factory arguments from config and kwargs
        factory_args = {}
        factory_args['implicit_wait_seconds'] = kwargs.get('implicit_wait_seconds', config.implicit_wait)

        webdriver_path_kwarg = kwargs.get('webdriver_path')
        if webdriver_path_kwarg:
             factory_args['webdriver_path'] = webdriver_path_kwarg
             logger.debug(f"Using provided webdriver_path: {webdriver_path_kwarg}")
        else:
             config_path = config.get_driver_path(browser_enum.value)
             if config_path:
                  factory_args['webdriver_path'] = config_path
                  logger.debug(f"Using configured webdriver_path: {config_path}")

        # Delegate creation to the factory
        driver = self.webdriver_factory.create_driver(
            browser_type=browser_enum,
            driver_type=driver_type,
            selenium_options=selenium_options,
            playwright_options=playwright_options,
            **factory_args
        )
        logger.info(f"SERVICE: Successfully created {driver_type} driver for {browser_to_use_str}.")
        return driver

    @log_method_call(logger)
    @handle_exceptions(WebDriverError, "Failed to dispose web driver")
    def dispose_web_driver(self, driver: IWebDriver) -> bool:
        """Dispose of (quit) a web driver instance."""
        if driver is None:
            logger.warning("SERVICE: dispose_web_driver called with None driver.")
            return False

        logger.info(f"SERVICE: Attempting to dispose of WebDriver instance: {type(driver).__name__}")
        try:
            driver.quit() # IWebDriver interface defines quit()
            logger.info("SERVICE: WebDriver disposed successfully.")
            return True
        except Exception as e:
             logger.error(f"SERVICE: Error disposing WebDriver: {e}", exc_info=True)
             raise # Let decorator wrap


    @log_method_call(logger)
    # No specific error handling needed here usually
    def get_available_browser_types(self) -> List[str]:
        """Get a list of available browser type names supported by the service/factory."""
        # Get names from the BrowserType enum
        available_types = [bt.value for bt in BrowserType]
        logger.debug(f"SERVICE: Returning available browser types: {available_types}")
        return available_types
```

## src/application/services/reporting_service.py

```python
"""Reporting service implementation for AutoQliq using simple file storage."""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Core interfaces
from src.core.interfaces.service import IReportingService
from src.core.exceptions import AutoQliqError, RepositoryError # Use RepositoryError for file issues

# Common utilities
from src.infrastructure.common.logging_utils import log_method_call
# Configuration needed for log path? Or hardcode? Let's hardcode 'logs/' for now.
# from src.config import config

logger = logging.getLogger(__name__)
LOG_DIRECTORY = "logs" # Directory to store execution logs

class ReportingService(IReportingService):
    """
    Basic implementation of IReportingService using simple JSON file storage.

    Stores each workflow execution log as a separate JSON file in the LOG_DIRECTORY.
    Provides methods for saving logs and basic retrieval (listing, getting details).
    """

    def __init__(self):
        """Initialize the ReportingService."""
        logger.info("ReportingService initialized.")
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Create the log directory if it doesn't exist."""
        try:
            os.makedirs(LOG_DIRECTORY, exist_ok=True)
            logger.debug(f"Ensured log directory exists: {LOG_DIRECTORY}")
        except OSError as e:
             logger.error(f"Failed to create log directory '{LOG_DIRECTORY}': {e}", exc_info=True)
             # Allow service to continue, but saving logs will fail

    def _generate_execution_id(self, workflow_name: str, start_time_iso: str) -> str:
        """Generates a unique filename based on workflow name and start time."""
        try:
            start_dt = datetime.fromisoformat(start_time_iso)
            ts_str = start_dt.strftime("%Y%m%d_%H%M%S")
        except ValueError:
             ts_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Fallback timestamp
        safe_wf_name = "".join(c if c.isalnum() else "_" for c in workflow_name)
        # Include status in filename? Maybe not in ID, but useful for listing.
        # Let's keep ID simple for now.
        return f"exec_{safe_wf_name}_{ts_str}.json"

    # --- Methods required by IReportingService ---

    def log_execution_start(self, workflow_name: str) -> str:
        """Generates and returns a unique ID for a new execution (doesn't save yet)."""
        # In this file-based approach, the ID is essentially the filename generated later.
        # We generate a *potential* ID here, but the actual filename depends on the final log data.
        # For simplicity, let's just return a timestamp-based ID for now.
        execution_id = f"exec_{int(time.time() * 1000)}" # Simple timestamp ID
        logger.info(f"Generated potential Execution ID for '{workflow_name}': {execution_id}")
        return execution_id

    def log_action_result(self, execution_id: str, action_index: int, action_name: str, result: Dict[str, Any]) -> None:
        """Currently NO-OP. Full log saved at end."""
        logger.debug(f"Placeholder: Log action result for ExecID '{execution_id}'. Not saving individually.")
        pass

    def log_execution_end(self, execution_id: str, final_status: str, duration: float, error_message: Optional[str] = None) -> None:
        """Currently NO-OP. Full log saved via save_execution_log."""
        logger.debug(f"Placeholder: Log execution end for ExecID '{execution_id}'. Not saving individually.")
        pass

    @log_method_call(logger)
    def save_execution_log(self, execution_log: Dict[str, Any]) -> None:
        """Saves the full execution log data to a unique JSON file."""
        if not isinstance(execution_log, dict) or not execution_log.get('workflow_name') or not execution_log.get('start_time_iso'):
            logger.error("Attempted to save invalid execution log data (missing required keys).")
            # Optionally raise an error? For now, just log and return.
            return

        try:
            # Generate filename based on content
            start_dt = datetime.fromisoformat(execution_log['start_time_iso'])
            ts_str = start_dt.strftime("%Y%m%d_%H%M%S")
            safe_wf_name = "".join(c if c.isalnum() else "_" for c in execution_log['workflow_name'])
            status = execution_log.get('final_status', 'UNKNOWN')
            # Use start time for uniqueness, status for easier browsing
            filename = f"exec_{safe_wf_name}_{ts_str}_{status}.json"
            filepath = os.path.join(LOG_DIRECTORY, filename)

            logger.info(f"Saving execution log to: {filepath}")
            try:
                # Ensure directory exists just before writing
                self._ensure_log_directory()
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(execution_log, f, indent=2)
                logger.debug(f"Successfully saved execution log: {filename}")
            except (IOError, TypeError, PermissionError) as e:
                 logger.error(f"Failed to write execution log file '{filepath}': {e}", exc_info=True)
                 raise RepositoryError(f"Failed to write execution log '{filepath}'", cause=e) from e

        except Exception as e:
             logger.error(f"Error processing execution log for saving: {e}", exc_info=True)
             # Don't crash originating workflow, but raise error to indicate logging failure
             raise AutoQliqError(f"Failed to process execution log: {e}", cause=e) from e


    @log_method_call(logger)
    def generate_summary_report(self, since: Optional[Any] = None) -> Dict[str, Any]:
        """Generate a summary report (Placeholder - requires reading/aggregating logs)."""
        logger.warning("Placeholder: Generate summary report called. Reading/aggregating logs not implemented.")
        return { "message": "Reporting logic not implemented." }

    @log_method_call(logger)
    def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results by reading the corresponding log file."""
        # Assume execution_id is the filename for this implementation
        filename = execution_id
        filepath = os.path.join(LOG_DIRECTORY, filename)
        logger.info(f"Attempting to load execution details from: {filepath}")

        if not filename.startswith("exec_") or not filename.endswith(".json"):
             logger.warning(f"Invalid execution ID format provided: {execution_id}")
             return None

        try:
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                logger.warning(f"Execution log file not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            logger.debug(f"Successfully loaded execution details for ID: {execution_id}")
            return log_data
        except json.JSONDecodeError as e:
             logger.error(f"Invalid JSON in execution log file '{filepath}': {e}")
             raise RepositoryError(f"Failed to parse execution log '{filename}'", cause=e) from e
        except (IOError, PermissionError, OSError) as e:
             logger.error(f"Error reading execution log file '{filepath}': {e}")
             raise RepositoryError(f"Failed to read execution log '{filename}'", cause=e) from e
        except Exception as e:
             logger.exception(f"Unexpected error getting execution details for '{execution_id}'")
             raise AutoQliqError(f"Unexpected error retrieving execution log '{filename}'", cause=e) from e


    @log_method_call(logger)
    def list_past_executions(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List past workflow execution summaries from log files."""
        logger.info(f"Listing past executions (Workflow: {workflow_name}, Limit: {limit}).")
        summaries = []
        try:
            if not os.path.exists(LOG_DIRECTORY) or not os.path.isdir(LOG_DIRECTORY):
                 logger.warning(f"Log directory not found: {LOG_DIRECTORY}")
                 return []

            log_files = [f for f in os.listdir(LOG_DIRECTORY) if f.startswith("exec_") and f.endswith(".json")]

            # Filter by workflow name if provided
            if workflow_name:
                 safe_filter_name = "".join(c if c.isalnum() else "_" for c in workflow_name)
                 log_files = [f for f in log_files if f.startswith(f"exec_{safe_filter_name}_")]

            # Sort by timestamp in filename (descending - newest first)
            log_files.sort(reverse=True)

            # Limit results
            log_files = log_files[:limit]

            # Read summary info from each file
            for filename in log_files:
                filepath = os.path.join(LOG_DIRECTORY, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    # Extract summary fields
                    summary = {
                        "execution_id": filename, # Use filename as ID for this impl
                        "workflow_name": log_data.get("workflow_name", "Unknown"),
                        "start_time_iso": log_data.get("start_time_iso"),
                        "duration_seconds": log_data.get("duration_seconds"),
                        "final_status": log_data.get("final_status", "UNKNOWN"),
                    }
                    summaries.append(summary)
                except Exception as e:
                     logger.error(f"Failed to read or parse summary from log file '{filename}': {e}")
                     # Skip this file on error

            logger.debug(f"Found {len(summaries)} execution summaries.")
            return summaries

        except Exception as e:
             logger.error(f"Error listing past executions: {e}", exc_info=True)
             raise RepositoryError(f"Failed to list execution logs: {e}", cause=e) from e
```

## src/application/services/scheduler_service.py

```python
"""Scheduler service stub implementation for AutoQliq."""

import logging
import time # For job ID generation example
from typing import Dict, List, Any, Optional

# Core interfaces
from src.core.interfaces.service import ISchedulerService, IWorkflowService # Need IWorkflowService to run
from src.core.exceptions import AutoQliqError, ConfigError, WorkflowError # Use specific errors
# Need BrowserType for run call
from src.infrastructure.webdrivers.base import BrowserType

# External libraries (optional import)
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.jobstores.base import JobLookupError
    from apscheduler.jobstores.memory import MemoryJobStore
    APS_AVAILABLE = True
except ImportError:
    logging.getLogger(__name__).warning("APScheduler not found. Scheduling functionality disabled. Install using: pip install apscheduler")
    APS_AVAILABLE = False
    class BackgroundScheduler: # type: ignore
        def add_job(self,*a,**kw): pass; def get_jobs(self,*a,**kw): return []; def remove_job(self,*a,**kw): raise JobLookupError(); def start(self): pass; def shutdown(self): pass
    class CronTrigger: pass # type: ignore
    class IntervalTrigger: pass # type: ignore
    class JobLookupError(Exception): pass # type: ignore
    class MemoryJobStore: pass # type: ignore

# Common utilities
from src.infrastructure.common.logging_utils import log_method_call

logger = logging.getLogger(__name__)


class SchedulerService(ISchedulerService):
    """
    Basic implementation of ISchedulerService using APScheduler (if available).

    Manages scheduled workflow runs using a background scheduler.
    Requires WorkflowService instance to execute the actual workflows.
    Uses MemoryJobStore by default (jobs lost on restart).
    """

    def __init__(self, workflow_service: IWorkflowService):
        """Initialize the SchedulerService."""
        self.scheduler: Optional[BackgroundScheduler] = None
        if workflow_service is None:
             raise ValueError("WorkflowService instance is required for SchedulerService.")
        self.workflow_service = workflow_service

        if APS_AVAILABLE:
            try:
                # TODO: Configure persistent job store (e.g., SQLAlchemyJobStore) via config
                jobstores = {'default': MemoryJobStore()}
                executors = {'default': {'type': 'threadpool', 'max_workers': 5}}
                job_defaults = {'coalesce': False, 'max_instances': 1}

                self.scheduler = BackgroundScheduler( # type: ignore
                    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='UTC'
                )
                self.scheduler.start()
                logger.info("SchedulerService initialized with APScheduler BackgroundScheduler.")
            except Exception as e:
                logger.error(f"Failed to initialize APScheduler: {e}. Scheduling disabled.", exc_info=True)
                self.scheduler = None
        else:
            logger.warning("SchedulerService initialized (APScheduler not available). Scheduling disabled.")

    def _run_scheduled_workflow(self, job_id: str, workflow_name: str, credential_name: Optional[str]):
         """Internal function called by the scheduler to run a workflow."""
         logger.info(f"SCHEDULER: Triggering run for job '{job_id}' (Workflow: {workflow_name})")
         try:
              # Use the injected WorkflowService instance
              # TODO: Determine browser type from job config or global config
              from src.config import config # Import config locally if needed
              browser_type = BrowserType.from_string(config.default_browser)

              # WorkflowService.run_workflow handles its own logging and error reporting (via ReportingService)
              self.workflow_service.run_workflow(
                   name=workflow_name,
                   credential_name=credential_name,
                   browser_type=browser_type
                   # Pass stop_event? Not applicable for scheduled runs usually.
                   # Pass log_callback? Could integrate with APScheduler logging.
              )
              # run_workflow raises exceptions on failure, caught below
              logger.info(f"SCHEDULER: Scheduled job '{job_id}' completed successfully.")
         except Exception as e:
              # Log errors from the scheduled run prominently
              logger.error(f"SCHEDULER: Error running scheduled job '{job_id}' for workflow '{workflow_name}': {e}", exc_info=True)
              # TODO: Add logic for handling repeated failures (e.g., disable job)


    @log_method_call(logger)
    def schedule_workflow(self, workflow_name: str, credential_name: Optional[str], schedule_config: Dict[str, Any]) -> str:
        """Schedule a workflow to run based on APScheduler trigger config."""
        if not self.scheduler: raise AutoQliqError("Scheduler not available or failed to initialize.")

        logger.info(f"Attempting schedule workflow '{workflow_name}' config: {schedule_config}")
        trigger = None
        # Use provided ID or generate one
        job_id = schedule_config.get("id", f"wf_{workflow_name}_{int(time.time())}")

        try:
            trigger_type = schedule_config.get("trigger", "interval")
            # Filter out non-trigger args before passing to trigger constructor
            trigger_args = {k:v for k,v in schedule_config.items() if k not in ['trigger', 'id', 'name']}

            if trigger_type == "cron": trigger = CronTrigger(**trigger_args)
            elif trigger_type == "interval": trigger = IntervalTrigger(**trigger_args)
            # Add 'date' trigger support if needed

            if trigger is None: raise ValueError(f"Unsupported trigger type: {trigger_type}")

            # Add the job
            added_job = self.scheduler.add_job(
                 func=self._run_scheduled_workflow,
                 trigger=trigger,
                 args=[job_id, workflow_name, credential_name],
                 id=job_id,
                 name=schedule_config.get('name', f"Run '{workflow_name}' ({trigger_type})"),
                 replace_existing=True # Update if job with same ID exists
            )
            if added_job is None: # Should not happen with replace_existing=True unless error
                 raise AutoQliqError(f"Scheduler returned None for job '{job_id}'. Scheduling might have failed silently.")

            logger.info(f"Successfully scheduled job '{added_job.id}' for workflow '{workflow_name}'.")
            return added_job.id

        except (ValueError, TypeError) as e: # Catch errors creating trigger
             logger.error(f"Invalid schedule configuration for '{workflow_name}': {e}", exc_info=True)
             raise ConfigError(f"Invalid schedule config for '{workflow_name}': {e}", cause=e) from e
        except Exception as e: # Catch errors from scheduler.add_job
             logger.error(f"Failed schedule job for '{workflow_name}': {e}", exc_info=True)
             raise AutoQliqError(f"Failed schedule workflow '{workflow_name}': {e}", cause=e) from e


    @log_method_call(logger)
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """List currently scheduled jobs from APScheduler."""
        if not self.scheduler: return []
        logger.debug("Listing scheduled jobs.")
        try:
            jobs = self.scheduler.get_jobs()
            job_list = []
            for job in jobs:
                 # Extract args safely
                 job_args = job.args if isinstance(job.args, (list, tuple)) else []
                 wf_name = job_args[1] if len(job_args) > 1 else "Unknown WF"
                 cred_name = job_args[2] if len(job_args) > 2 else None

                 job_list.append({
                      "id": job.id,
                      "name": job.name,
                      "workflow_name": wf_name, # Add workflow name from args
                      "credential_name": cred_name, # Add credential name from args
                      "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                      "trigger": str(job.trigger)
                 })
            return job_list
        except Exception as e:
             logger.error(f"Failed list scheduled jobs: {e}", exc_info=True)
             raise AutoQliqError(f"Failed list jobs: {e}", cause=e) from e


    @log_method_call(logger)
    def cancel_scheduled_job(self, job_id: str) -> bool:
        """Cancel a scheduled job by its ID using APScheduler."""
        if not self.scheduler: return False
        logger.info(f"Attempting cancel scheduled job '{job_id}'.")
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Successfully cancelled scheduled job '{job_id}'.")
            return True
        except JobLookupError:
             logger.warning(f"Scheduled job ID '{job_id}' not found.")
             return False
        except Exception as e:
             logger.error(f"Failed cancel scheduled job '{job_id}': {e}", exc_info=True)
             raise AutoQliqError(f"Failed cancel job '{job_id}': {e}", cause=e) from e


    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler and hasattr(self.scheduler, 'running') and self.scheduler.running:
            try:
                 self.scheduler.shutdown()
                 logger.info("SchedulerService shut down.")
            except Exception as e: logger.error(f"Error shutting down scheduler: {e}", exc_info=True)
        else: logger.info("SchedulerService shutdown (scheduler not running or unavailable).")
```

## src/infrastructure/repositories/workflow_repository.py

```python
"""Workflow repository implementation for AutoQliq."""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime # Needed for metadata

# Core dependencies
from src.core.exceptions import WorkflowError, RepositoryError, ValidationError, SerializationError
from src.core.interfaces import IAction, IWorkflowRepository

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator
from src.infrastructure.repositories.base.file_system_repository import FileSystemRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)

class FileSystemWorkflowRepository(FileSystemRepository[List[IAction]], IWorkflowRepository):
    """Implementation of IWorkflowRepository that stores workflows and templates in JSON files."""
    WORKFLOW_EXTENSION = ".json"
    TEMPLATE_SUBDIR = "templates"

    def __init__(self, directory_path: str, **options):
        """Initialize FileSystemWorkflowRepository."""
        super().__init__(logger_name=__name__)
        if not directory_path: raise ValueError("Directory path cannot be empty.")
        self.directory_path = directory_path
        # Ensure template path is absolute or relative to CWD if base path is just filename
        base_dir = os.path.dirname(directory_path) if os.path.dirname(directory_path) else "."
        self.template_dir_path = os.path.join(base_dir, self.TEMPLATE_SUBDIR) # Place templates dir relative to main dir's parent or CWD
        # Corrected: Place templates inside the workflow directory
        self.template_dir_path = os.path.join(self.directory_path, self.TEMPLATE_SUBDIR)

        self._create_if_missing = options.get('create_if_missing', True)

        if self._create_if_missing:
            try:
                super()._ensure_directory_exists(self.directory_path)
                super()._ensure_directory_exists(self.template_dir_path)
            except AutoQliqError as e:
                raise RepositoryError(f"Failed ensure directories exist: {directory_path}", cause=e) from e


    def _get_workflow_path(self, name: str) -> str:
        """Get file path for a workflow."""
        return os.path.join(self.directory_path, f"{name}{self.WORKFLOW_EXTENSION}")

    def _get_template_path(self, name: str) -> str:
        """Get file path for a template."""
        return os.path.join(self.template_dir_path, f"{name}{self.WORKFLOW_EXTENSION}")


    # --- IWorkflowRepository Implementation ---

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        """Create a new empty workflow file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        file_path = self._get_workflow_path(name)
        if super()._file_exists(file_path):
            raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
        try:
            super()._write_json_file(file_path, []) # Write empty list
        except (IOError, TypeError) as e:
            raise RepositoryError(f"Failed create empty file for workflow '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None:
        """Save a workflow (list of actions) to a JSON file."""
        WorkflowValidator.validate_workflow_name(name)
        WorkflowValidator.validate_actions(workflow_actions)
        self._log_operation("Saving workflow", name)
        try:
            action_data_list = serialize_actions(workflow_actions) # Raises SerializationError
            file_path = self._get_workflow_path(name)
            super()._write_json_file(file_path, action_data_list) # Raises IOError, TypeError
        except (IOError, TypeError, SerializationError) as e:
             raise RepositoryError(f"Failed save workflow '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        """Load a workflow (list of actions) from a JSON file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading workflow", name)
        file_path = self._get_workflow_path(name)
        try:
            action_data_list = super()._read_json_file(file_path) # Raises FileNotFoundError, JSONDecodeError, IOError
            if not isinstance(action_data_list, list):
                 raise SerializationError(f"Workflow file '{name}' not JSON list.", entity_id=name)
            actions = deserialize_actions(action_data_list) # Raises SerializationError, ActionError
            return actions
        except FileNotFoundError as e: raise RepositoryError(f"Workflow file not found: {name}", entity_id=name, cause=e) from e
        except (json.JSONDecodeError, SerializationError, ActionError) as e: raise SerializationError(f"Failed load/deserialize workflow '{name}'", entity_id=name, cause=e) from e
        except (IOError, PermissionError) as e: raise RepositoryError(f"Failed read workflow file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool:
        """Delete a workflow file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting workflow", name)
        file_path = self._get_workflow_path(name)
        if not super()._file_exists(file_path): return False
        try: os.remove(file_path); return True
        except (IOError, OSError, PermissionError) as e: raise RepositoryError(f"Failed delete workflow file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]:
        """List workflow files in the directory."""
        self._log_operation("Listing workflows")
        try:
            names = [ f[:-len(self.WORKFLOW_EXTENSION)]
                      for f in os.listdir(self.directory_path)
                      if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.directory_path, f)) ]
            return sorted(names)
        except (FileNotFoundError, PermissionError, OSError) as e: raise RepositoryError(f"Failed list workflows in '{self.directory_path}'", cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get file system metadata for a workflow."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Getting metadata", name)
        file_path = self._get_workflow_path(name)
        try:
            if not super()._file_exists(file_path): raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
            stat_result = os.stat(file_path)
            return { "name": name, "source": "file_system", "path": file_path, "size_bytes": stat_result.st_size,
                     "created_at": datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                     "modified_at": datetime.fromtimestamp(stat_result.st_mtime).isoformat() }
        except (FileNotFoundError, OSError, PermissionError) as e: raise RepositoryError(f"Failed get metadata for workflow '{name}'", entity_id=name, cause=e) from e

    # --- Template Methods ---

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save an action template (serialized list) to a JSON file in templates subdir."""
        WorkflowValidator.validate_workflow_name(name) # Use same validation for names
        self._log_operation("Saving template", name)
        if not isinstance(actions_data, list): raise SerializationError("Template actions data must be list of dicts.")
        if not all(isinstance(item, dict) for item in actions_data): raise SerializationError("Template actions data list must only contain dicts.")
        try:
            file_path = self._get_template_path(name)
            super()._write_json_file(file_path, actions_data)
        except (IOError, TypeError) as e: raise RepositoryError(f"Failed save template '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load serialized action data for a template."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Loading template", name)
        file_path = self._get_template_path(name)
        try:
            actions_data = super()._read_json_file(file_path) # Raises FileNotFoundError, JSONDecodeError, IOError
            if not isinstance(actions_data, list): raise SerializationError(f"Template file '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data): raise SerializationError(f"Template file '{name}' contains non-dict items.", entity_id=name)
            return actions_data
        except FileNotFoundError as e: raise RepositoryError(f"Template file not found: {name}", entity_id=name, cause=e) from e
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in template file '{name}'", entity_id=name, cause=e) from e
        except (IOError, PermissionError) as e: raise RepositoryError(f"Failed read template file '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """Delete a template file."""
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Deleting template", name)
        file_path = self._get_template_path(name)
        if not super()._file_exists(file_path): return False
        try: os.remove(file_path); return True
        except (IOError, OSError, PermissionError) as e: raise RepositoryError(f"Failed delete template file '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates")
    def list_templates(self) -> List[str]:
        """List template files in the template subdirectory."""
        self._log_operation("Listing templates")
        if not os.path.exists(self.template_dir_path): return []
        try:
            names = [ f[:-len(self.WORKFLOW_EXTENSION)]
                      for f in os.listdir(self.template_dir_path)
                      if f.endswith(self.WORKFLOW_EXTENSION) and os.path.isfile(os.path.join(self.template_dir_path, f)) ]
            return sorted(names)
        except (FileNotFoundError, PermissionError, OSError) as e: raise RepositoryError(f"Failed list templates in '{self.template_dir_path}'", cause=e) from e
```

## src/infrastructure/repositories/database_workflow_repository.py

```python
"""Database workflow repository implementation for AutoQliq."""
import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import WorkflowError, RepositoryError, SerializationError, ValidationError

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator
from src.infrastructure.repositories.base.database_repository import DatabaseRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)

class DatabaseWorkflowRepository(DatabaseRepository[List[IAction]], IWorkflowRepository):
    """
    Implementation of IWorkflowRepository storing workflows and templates in SQLite.
    """
    _WF_TABLE_NAME = "workflows"
    _WF_PK_COLUMN = "name"
    _TMPL_TABLE_NAME = "templates"
    _TMPL_PK_COLUMN = "name"

    def __init__(self, db_path: str, **options: Any):
        """Initialize DatabaseWorkflowRepository."""
        super().__init__(db_path=db_path, table_name=self._WF_TABLE_NAME, logger_name=__name__)
        self._create_templates_table_if_not_exists()

    # --- Configuration for Workflows Table (via Base Class) ---
    def _get_primary_key_col(self) -> str: return self._WF_PK_COLUMN
    def _get_table_creation_sql(self) -> str:
        return f"{self._WF_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL"

    # --- Configuration and Creation for Templates Table ---
    def _get_templates_table_creation_sql(self) -> str:
         """Return SQL for creating the templates table."""
         return f"{self._TMPL_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL"

    def _create_templates_table_if_not_exists(self) -> None:
        """Create the templates table."""
        logger.debug("Ensuring templates table exists.")
        sql = self._get_templates_table_creation_sql()
        try: self.connection_manager.create_table(self._TMPL_TABLE_NAME, sql)
        except Exception as e: logger.error(f"Failed ensure table '{self._TMPL_TABLE_NAME}': {e}", exc_info=True)


    # --- Mapping for Workflows (Base Class uses these) ---
    def _map_row_to_entity(self, row: Dict[str, Any]) -> List[IAction]:
        """Convert a workflow table row to a list of IAction."""
        actions_json = row.get("actions_json"); name = row.get(self._WF_PK_COLUMN, "<unknown>")
        if actions_json is None: raise RepositoryError(f"Missing action data for workflow '{name}'.", entity_id=name)
        try:
            action_data_list = json.loads(actions_json)
            if not isinstance(action_data_list, list): raise json.JSONDecodeError("Not JSON list.", actions_json, 0)
            return deserialize_actions(action_data_list) # Raises SerializationError
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in workflow '{name}': {e}", entity_id=name, cause=e) from e
        except Exception as e:
             if isinstance(e, SerializationError): raise
             raise RepositoryError(f"Error processing actions for workflow '{name}': {e}", entity_id=name, cause=e) from e

    def _map_entity_to_params(self, entity_id: str, entity: List[IAction]) -> Dict[str, Any]:
        """Convert list of IAction to workflow DB parameters."""
        WorkflowValidator.validate_workflow_name(entity_id)
        WorkflowValidator.validate_actions(entity)
        try:
            action_data_list = serialize_actions(entity) # Raises SerializationError
            actions_json = json.dumps(action_data_list)
        except (SerializationError, TypeError) as e: raise SerializationError(f"Failed serialize actions for workflow '{entity_id}'", entity_id=entity_id, cause=e) from e
        now = datetime.now().isoformat()
        return { self._WF_PK_COLUMN: entity_id, "actions_json": actions_json, "created_at": now, "modified_at": now }

    # --- IWorkflowRepository Implementation (using Base Class methods) ---
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None: super().save(name, workflow_actions)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        actions = super().get(name)
        if actions is None: raise RepositoryError(f"Workflow not found: '{name}'", entity_id=name)
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool: return super().delete(name)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]: return super().list()

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        self._validate_entity_id(name, entity_type="Workflow")
        self._log_operation("Getting metadata", name)
        try:
            query = f"SELECT {self._WF_PK_COLUMN}, created_at, modified_at FROM {self._WF_TABLE_NAME} WHERE {self._WF_PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
            metadata = dict(rows[0]); metadata["source"] = "database"
            return metadata
        except RepositoryError: raise
        except Exception as e: raise RepositoryError(f"Failed get metadata for workflow '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating empty workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        if super().get(name) is not None: raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
        try: super().save(name, []) # Save empty list
        except Exception as e: raise WorkflowError(f"Failed create empty workflow '{name}'", workflow_name=name, cause=e) from e

    # --- Template Methods (DB Implementation) ---

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save/Update an action template (serialized list) to the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Saving template", name)
        if not isinstance(actions_data, list) or not all(isinstance(item, dict) for item in actions_data):
             raise SerializationError("Template actions data must be list of dicts.")
        try: actions_json = json.dumps(actions_data)
        except TypeError as e: raise SerializationError(f"Data for template '{name}' not JSON serializable", entity_id=name, cause=e) from e

        now = datetime.now().isoformat()
        pk_col = self._TMPL_PK_COLUMN
        params = {pk_col: name, "actions_json": actions_json, "created_at": now}
        columns = list(params.keys()); placeholders = ", ".join("?" * len(params))
        # Only update actions_json on conflict
        query = f"""
            INSERT INTO {self._TMPL_TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders})
            ON CONFLICT({pk_col}) DO UPDATE SET actions_json = excluded.actions_json
        """
        try:
            self.connection_manager.execute_modification(query, tuple(params.values()))
            self.logger.info(f"Successfully saved template: '{name}'")
        except Exception as e: raise RepositoryError(f"DB error saving template '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load serialized action data for a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Loading template", name)
        query = f"SELECT actions_json FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Template not found: {name}", entity_id=name)
            actions_json = rows[0]["actions_json"]
            actions_data = json.loads(actions_json) # Raises JSONDecodeError
            if not isinstance(actions_data, list): raise SerializationError(f"Stored template '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data): raise SerializationError(f"Stored template '{name}' contains non-dict items.", entity_id=name)
            return actions_data
        except RepositoryError: raise
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in template '{name}'", entity_id=name, cause=e) from e
        except Exception as e: raise RepositoryError(f"DB error loading template '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """Delete a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Deleting template", name)
        query = f"DELETE FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            affected_rows = self.connection_manager.execute_modification(query, (name,))
            deleted = affected_rows > 0
            if deleted: self.logger.info(f"Successfully deleted template: '{name}'")
            else: self.logger.warning(f"Template not found for deletion: '{name}'")
            return deleted
        except Exception as e: raise RepositoryError(f"DB error deleting template '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates")
    def list_templates(self) -> List[str]:
        """List the names of all saved templates."""
        self._log_operation("Listing templates")
        query = f"SELECT {self._TMPL_PK_COLUMN} FROM {self._TMPL_TABLE_NAME} ORDER BY {self._TMPL_PK_COLUMN}"
        try:
            rows = self.connection_manager.execute_query(query)
            names = [row[self._TMPL_PK_COLUMN] for row in rows]
            return names
        except Exception as e: raise RepositoryError(f"DB error listing templates", cause=e) from e
```

## src/infrastructure/common/connection_manager.py

```python
"""Database connection management for AutoQliq."""

import logging
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Union
import os
import threading

from src.core.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages database connections for repositories.
    
    Provides thread-safe access to SQLite database connections,
    with connection pooling and transaction management.
    
    Attributes:
        db_path (str): Path to the SQLite database file.
        _local (threading.local): Thread-local storage for connections.
        _lock (threading.Lock): Lock for thread safety.
    """
    
    def __init__(self, db_path: str):
        """Initialize the ConnectionManager.
        
        Args:
            db_path: Path to the SQLite database file.
            
        Raises:
            RepositoryError: If the database path is invalid or inaccessible.
        """
        if not db_path:
            raise ValueError("Database path cannot be empty")
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created directory for database: {db_dir}")
            except OSError as e:
                raise RepositoryError(f"Failed to create database directory: {e}", cause=e)
        
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        
        logger.info(f"ConnectionManager initialized with database: {db_path}")
        
        # Test connection
        try:
            with self.get_connection():
                pass
            logger.debug("Database connection test successful")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise RepositoryError(f"Failed to connect to database: {e}", cause=e)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection for the current thread.
        
        Returns:
            An SQLite connection object.
            
        Raises:
            RepositoryError: If connection fails.
        """
        # Check if connection exists for this thread
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            try:
                # Create new connection for this thread
                self._local.connection = sqlite3.connect(
                    self.db_path,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                )
                # Configure connection
                self._local.connection.row_factory = sqlite3.Row
                # Enable foreign keys
                self._local.connection.execute("PRAGMA foreign_keys = ON")
                logger.debug(f"Created new database connection for thread {threading.current_thread().name}")
            except sqlite3.Error as e:
                logger.error(f"Failed to connect to database: {e}")
                raise RepositoryError(f"Failed to connect to database: {e}", cause=e)
        
        return self._local.connection
    
    def close_connection(self) -> None:
        """Close the connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            try:
                self._local.connection.close()
                logger.debug(f"Closed database connection for thread {threading.current_thread().name}")
            except sqlite3.Error as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                self._local.connection = None
    
    def execute_query(self, query: str, params: Union[Tuple, Dict[str, Any], None] = None) -> List[sqlite3.Row]:
        """Execute a SELECT query and return the results.
        
        Args:
            query: SQL query string.
            params: Query parameters (tuple, dict, or None).
            
        Returns:
            List of sqlite3.Row objects.
            
        Raises:
            RepositoryError: If query execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {params}")
            raise RepositoryError(f"Query execution failed: {e}", cause=e)
    
    def execute_update(self, query: str, params: Union[Tuple, Dict[str, Any], None] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string.
            params: Query parameters (tuple, dict, or None).
            
        Returns:
            Number of rows affected.
            
        Raises:
            RepositoryError: If query execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            
            connection.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            connection.rollback()
            logger.error(f"Update execution failed: {e}\nQuery: {query}\nParams: {params}")
            raise RepositoryError(f"Update execution failed: {e}", cause=e)
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script.
        
        Args:
            script: SQL script string.
            
        Raises:
            RepositoryError: If script execution fails.
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            cursor.executescript(script)
            connection.commit()
        except sqlite3.Error as e:
            connection.rollback()
            logger.error(f"Script execution failed: {e}\nScript: {script[:100]}...")
            raise RepositoryError(f"Script execution failed: {e}", cause=e)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check.
            
        Returns:
            True if the table exists, False otherwise.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        rows = self.execute_query(query, (table_name,))
        return len(rows) > 0
    
    def begin_transaction(self) -> None:
        """Begin a transaction."""
        connection = self.get_connection()
        try:
            connection.execute("BEGIN TRANSACTION")
            logger.debug("Transaction started")
        except sqlite3.Error as e:
            logger.error(f"Failed to begin transaction: {e}")
            raise RepositoryError(f"Failed to begin transaction: {e}", cause=e)
    
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        connection = self.get_connection()
        try:
            connection.commit()
            logger.debug("Transaction committed")
        except sqlite3.Error as e:
            logger.error(f"Failed to commit transaction: {e}")
            raise RepositoryError(f"Failed to commit transaction: {e}", cause=e)
    
    def rollback_transaction(self) -> None:
        """Roll back the current transaction."""
        connection = self.get_connection()
        try:
            connection.rollback()
            logger.debug("Transaction rolled back")
        except sqlite3.Error as e:
            logger.error(f"Failed to rollback transaction: {e}")
            # Don't raise here, as this is typically called in exception handlers
    
    def __del__(self) -> None:
        """Close connections when the manager is garbage collected."""
        self.close_connection()
```

## src/ui/presenters/base_presenter.py

```python
"""Base presenter class for AutoQliq UI."""
import logging
from typing import Any, Optional, Dict, List, Callable, TypeVar, Generic

from src.core.exceptions import AutoQliqError, ValidationError
from src.ui.common.error_handler import ErrorHandler
from src.ui.interfaces.presenter import IPresenter
# Import base view interface for type hinting
from src.ui.interfaces.view import IView

# Type variable for the view type
V = TypeVar('V', bound=IView)


class BasePresenter(Generic[V], IPresenter):
    """Base class for all presenters.

    Provides common functionality like view management, logging, and error handling.

    Attributes:
        _view: The view component associated with this presenter. Use property `view`.
        logger: Logger instance specific to the presenter subclass.
        error_handler: Handler for logging and potentially showing errors in the view.
    """

    def __init__(self, view: Optional[V] = None):
        """Initialize a BasePresenter.

        Args:
            view: The view component (optional at init, can be set later).
        """
        self._view: Optional[V] = view
        self.logger = logging.getLogger(f"presenter.{self.__class__.__name__}")
        # ErrorHandler can use the same logger or a dedicated one
        self.error_handler = ErrorHandler(self.logger)
        self.logger.debug(f"{self.__class__.__name__} initialized.")

    @property
    def view(self) -> Optional[V]:
        """Get the associated view instance."""
        return self._view

    def set_view(self, view: V) -> None:
        """Set the view component associated with this presenter.

        Args:
            view: The view component instance.
        """
        if not isinstance(view, IView):
            # Basic check, could be more specific if V had stricter bounds
            raise TypeError("View must implement the IView interface.")
        self._view = view
        self.logger.debug(f"View {type(view).__name__} set for presenter {self.__class__.__name__}")
        # Optionally call initialize_view after setting
        # self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view with data. Should be overridden by subclasses."""
        self.logger.debug(f"Base initialize_view called for {self.__class__.__name__}. Subclass should implement.")
        pass # Subclasses override to populate view on startup or after view is set

    def _handle_error(self, error: Exception, context: str) -> None:
        """Internal helper to handle errors using the error_handler and update the view."""
        self.error_handler.handle_error(error, context, show_message=False) # Log first

        # Show the error in the view if available
        if self.view:
             # Extract a user-friendly title and message
             title = "Error"
             message = str(error)
             if isinstance(error, AutoQliqError):
                 # Use more specific titles for known error types
                 error_type_name = type(error).__name__.replace("Error", " Error") # Add space
                 title = error_type_name
             elif isinstance(error, FileNotFoundError):
                 title = "File Not Found"
             elif isinstance(error, PermissionError):
                 title = "Permission Error"
             else: # Unexpected errors
                 title = "Unexpected Error"
                 message = f"An unexpected error occurred: {message}"

             try:
                self.view.display_error(title, message)
             except Exception as view_e:
                  self.logger.error(f"Failed to display error in view: {view_e}")
        else:
             self.logger.warning(f"Cannot display error in view (view not set) for context: {context}")

    # Optional: Decorator within the base class for convenience
    @classmethod
    def handle_errors(cls, context: str) -> Callable[[Callable], Callable]:
        """
        Class method decorator to automatically handle errors in presenter methods.

        Logs errors and displays them in the associated view (if set).

        Args:
            context: Description of the operation being performed (for error messages).

        Returns:
            A decorator.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(presenter_instance: 'BasePresenter', *args, **kwargs) -> Any:
                try:
                    # Execute the original presenter method
                    return func(presenter_instance, *args, **kwargs)
                except Exception as e:
                    # Use the instance's error handling method
                    presenter_instance._handle_error(e, context)
                    # Decide what to return on error. Often None or False for actions.
                    # Returning None might require callers to check.
                    # Returning False might be suitable for boolean methods.
                    # Re-raising might be needed if the caller needs to react specifically.
                    # Defaulting to returning None here.
                    return None # Or False, or re-raise specific types if needed
            # Need functools for wraps
            import functools
            return wrapper
        return decorator
```

## src/ui/presenters/workflow_runner_presenter.py

```python
"""Workflow runner presenter implementation for AutoQliq."""

import logging
import threading
import time
import tkinter as tk # Only needed for type hints potentially, avoid direct use
from typing import List, Optional, Dict, Any

# Core dependencies
from src.core.exceptions import WorkflowError, CredentialError, WebDriverError, AutoQliqError, ValidationError, ActionError
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService # Use Service Interfaces
from src.infrastructure.webdrivers.base import BrowserType # Use BrowserType enum
# Configuration
from src.config import config

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowRunnerPresenter
from src.ui.interfaces.view import IWorkflowRunnerView
from src.ui.presenters.base_presenter import BasePresenter

class WorkflowRunnerPresenter(BasePresenter[IWorkflowRunnerView], IWorkflowRunnerPresenter):
    """
    Presenter for the workflow runner view. Handles logic for listing workflows/credentials,
    initiating, and stopping workflow execution via application services.
    Manages background execution thread.
    """

    def __init__(
        self,
        workflow_service: IWorkflowService,
        credential_service: ICredentialService,
        webdriver_service: IWebDriverService, # Expect the service now
        view: Optional[IWorkflowRunnerView] = None
    ):
        """Initialize the presenter."""
        super().__init__(view)
        if workflow_service is None: raise ValueError("Workflow service cannot be None.")
        if credential_service is None: raise ValueError("Credential service cannot be None.")
        if webdriver_service is None: raise ValueError("WebDriver service cannot be None.")

        self.workflow_service = workflow_service
        self.credential_service = credential_service
        self.webdriver_service = webdriver_service

        # State management for execution thread
        self._is_running = False
        self._stop_event = threading.Event() # Use Event for clearer stop signal
        self._execution_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock() # For thread safety accessing state
        self.logger.info("WorkflowRunnerPresenter initialized.")

    def set_view(self, view: IWorkflowRunnerView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing runner view")
    def initialize_view(self) -> None:
        """Populate the view with initial data using services."""
        if not self.view: return
        self.logger.debug("Initializing runner view...")
        workflows = self._get_workflows_from_service()
        credentials = self._get_credentials_from_service()
        self.view.set_workflow_list(workflows or [])
        self.view.set_credential_list(credentials or [])
        self.view.set_running_state(self._is_running) # Ensure UI reflects initial state
        self.view.set_status("Ready. Select workflow and credential.")
        self.logger.debug("Runner view initialized.")

    def get_workflow_list(self) -> List[str]:
         return self._get_workflows_from_service()

    def get_credential_list(self) -> List[str]:
         return self._get_credentials_from_service()

    @BasePresenter.handle_errors("Getting workflow list")
    def _get_workflows_from_service(self) -> List[str]:
        self.logger.debug("Fetching workflow list from service.")
        return self.workflow_service.list_workflows()

    @BasePresenter.handle_errors("Getting credential list")
    def _get_credentials_from_service(self) -> List[str]:
        self.logger.debug("Fetching credential list from service.")
        return self.credential_service.list_credentials()


    # --- Workflow Execution ---

    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Start executing the specified workflow in a background thread via the WorkflowService."""
        if not self.view: return

        with self._lock:
             if self._is_running:
                  self.logger.warning("Run requested while already running.")
                  self._schedule_ui_update(lambda: self.view.display_message("Busy", "A workflow is already running."))
                  return
             self._is_running = True
             self._stop_event.clear() # Reset stop flag for new run

        if not workflow_name:
             self.logger.warning("Run workflow called with empty workflow name.")
             self._handle_error(ValidationError("Workflow name must be selected."), "starting workflow run")
             with self._lock: self._is_running = False # Reset flag
             return

        log_cred = f"with credential '{credential_name}'" if credential_name else "without specific credentials"
        self.logger.info(f"Initiating run for workflow '{workflow_name}' {log_cred}.")

        # --- Update UI immediately ---
        self._schedule_ui_update(self.view.clear_log)
        self._schedule_ui_update(lambda: self.view.log_message(f"Starting workflow '{workflow_name}'..."))
        self._schedule_ui_update(lambda: self.view.set_running_state(True))

        # --- Launch Thread ---
        self._execution_thread = threading.Thread(
            target=self._execute_workflow_thread, # Target the internal method
            args=(workflow_name, credential_name),
            daemon=True
        )
        self._execution_thread.start()
        self.logger.info(f"Execution thread started for workflow '{workflow_name}'.")

    def _execute_workflow_thread(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Target function for background thread. Calls WorkflowService.run_workflow."""
        start_time = time.time()
        final_status = "UNKNOWN"
        error_occurred: Optional[Exception] = None
        execution_log: Optional[Dict[str, Any]] = None

        try:
            # --- Call the Service ---
            browser_type_str = config.default_browser
            browser_enum = BrowserType.from_string(browser_type_str)

            # Pass the stop event to the service call
            # The service now returns the full log dictionary
            execution_log = self.workflow_service.run_workflow(
                name=workflow_name,
                credential_name=credential_name,
                browser_type=browser_enum,
                stop_event=self._stop_event, # Pass the event
                log_callback=lambda msg: self._schedule_ui_update(lambda m=msg: self.view.log_message(m)) if self.view else None
            )
            # Extract final status from the returned log
            final_status = execution_log.get("final_status", "UNKNOWN")
            if final_status == "SUCCESS":
                 self.logger.info(f"[Thread] Workflow service call for '{workflow_name}' completed successfully.")
            elif final_status == "STOPPED":
                 self.logger.info(f"[Thread] Workflow '{workflow_name}' execution stopped by request.")
                 error_occurred = WorkflowError("Workflow execution stopped by user.") # Set error for logging
            else: # FAILED or UNKNOWN
                 error_message = execution_log.get("error_message", "Unknown error from service.")
                 error_occurred = WorkflowError(error_message) # Create error object
                 self.logger.error(f"[Thread] Workflow service call failed for '{workflow_name}': {error_message}")

        # Catch exceptions raised *by the service call itself* (e.g., if service init failed, config error)
        except (WorkflowError, CredentialError, WebDriverError, ActionError, ValidationError, ConfigError, AutoQliqError) as e:
            error_occurred = e
            final_status = "FAILED"
            if self._stop_event.is_set(): final_status = "STOPPED"
            error_msg = f"Workflow '{workflow_name}' failed: {str(e)}"
            self.logger.error(f"[Thread] {error_msg}")
            self._schedule_ui_update(lambda msg=f"ERROR: {error_msg}": self.view.log_message(msg))
        except Exception as e:
            error_occurred = e
            final_status = "UNEXPECTED ERROR"
            if self._stop_event.is_set(): final_status = "STOPPED"
            error_msg = f"Unexpected error during service call for workflow '{workflow_name}': {str(e)}"
            self.logger.exception(f"[Thread] {error_msg}")
            self._schedule_ui_update(lambda msg=f"CRITICAL ERROR: {error_msg}": self.view.log_message(msg))
        finally:
            # --- Final State Reset & UI Update ---
            with self._lock: self._is_running = False # Reset running flag

            end_time = time.time()
            duration = end_time - start_time
            final_log_msg = f"Workflow execution finished. Status: {final_status}. Duration: {duration:.2f}s"

            # Log final message and update UI state via scheduler
            self._schedule_ui_update(lambda msg=final_log_msg: self.view.log_message(msg))
            self._schedule_ui_update(lambda: self.view.set_running_state(False))

            self.logger.info(f"[Thread] {final_log_msg}")


    def stop_workflow(self) -> None:
        """Request to stop the currently running workflow by setting the event."""
        with self._lock:
             if not self._is_running:
                  self.logger.warning("Stop requested but no workflow is running.")
                  self._schedule_ui_update(lambda: self.view.display_message("Info", "No workflow is currently running."))
                  return
             if self._stop_event.is_set(): # Already requested
                  self.logger.warning("Stop already requested.")
                  return
             self.logger.info("Requesting workflow stop via event...")
             self._stop_event.set() # Signal the event

        if self.view:
             self._schedule_ui_update(lambda: self.view.log_message("Stop requested... (Signaling running workflow)"))
             if self.view.stop_button:
                  self._schedule_ui_update(lambda: self.view.stop_button.config(state=tk.DISABLED))


    def _schedule_ui_update(self, callback: Callable):
        """Safely schedule a callback to run on the main Tkinter thread."""
        if self.view and hasattr(self.view, 'widget') and self.view.widget.winfo_exists():
            try: self.view.widget.after(0, callback)
            except Exception as e: self.logger.error(f"Failed to schedule UI update: {e}")
        else: self.logger.warning("Cannot schedule UI update: View/widget not available.")
```

## src/ui/views/base_view.py

```python
"""Base view class for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Optional, Any

from src.ui.interfaces.view import IView
from src.ui.common.error_handler import ErrorHandler
from src.ui.common.status_bar import StatusBar # Import StatusBar

class BaseView(IView):
    """
    Base class for all view components in the application.

    Provides common functionality like holding the root widget, presenter reference,
    logger, error handler, status bar integration, and basic UI interaction methods.

    Attributes:
        root (tk.Widget): The parent widget for this view (e.g., a tab frame).
        presenter (Any): The presenter associated with this view.
        logger (logging.Logger): Logger instance for the view subclass.
        error_handler (ErrorHandler): Utility for displaying errors.
        main_frame (ttk.Frame): The primary frame holding the view's specific content.
        status_bar (Optional[StatusBar]): Reference to the status bar instance (shared via root).
    """
    def __init__(self, root: tk.Widget, presenter: Any):
        """
        Initialize the BaseView.

        Args:
            root (tk.Widget): The parent widget (e.g., a frame within a tab).
            presenter (Any): The presenter instance handling the logic for this view.
        """
        if root is None:
            raise ValueError("Root widget cannot be None for BaseView.")
        if presenter is None:
             raise ValueError("Presenter cannot be None for BaseView.")

        self.root = root
        self.presenter = presenter
        self.logger = logging.getLogger(f"view.{self.__class__.__name__}")
        self.error_handler = ErrorHandler(self.logger)
        self.status_bar: Optional[StatusBar] = None # Initialize status_bar attribute

        # --- Main Frame Setup ---
        # This frame fills the parent widget (e.g., the tab frame provided by main_ui)
        # Subclasses will add their widgets to this frame.
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Find the status bar - assumes status bar is attached to the toplevel window
        # and registered on it by main_ui.py
        self._find_status_bar()

        self.logger.debug(f"{self.__class__.__name__} initialized.")

    def _find_status_bar(self):
        """Tries to find a StatusBar instance attached to the toplevel window."""
        try:
             toplevel = self.main_frame.winfo_toplevel() # Get the main Tk window
             if hasattr(toplevel, 'status_bar_instance') and isinstance(toplevel.status_bar_instance, StatusBar):
                  self.status_bar = toplevel.status_bar_instance
                  self.logger.debug("Found StatusBar instance on toplevel window.")
             else:
                  self.logger.warning("StatusBar instance not found on toplevel window.")
        except Exception as e:
             self.logger.warning(f"Could not find status bar: {e}")


    @property
    def widget(self) -> tk.Widget:
        """Returns the main content widget managed by this view (the main_frame)."""
        return self.main_frame

    def display_error(self, title: str, message: str) -> None:
        """Display an error message box."""
        self.logger.warning(f"Displaying error: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showerror(title, message, parent=parent_window)
        except Exception as e:
             self.logger.error(f"Failed to display error message box: {e}")
        # Also update status bar
        self.set_status(f"Error: {message[:100]}")

    def display_message(self, title: str, message: str) -> None:
        """Display an informational message box."""
        self.logger.info(f"Displaying message: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showinfo(title, message, parent=parent_window)
            self.set_status(message)
        except Exception as e:
            self.logger.error(f"Failed to display info message box: {e}")

    def confirm_action(self, title: str, message: str) -> bool:
        """Display a confirmation dialog and return the user's choice."""
        self.logger.debug(f"Requesting confirmation: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            response = messagebox.askyesno(title, message, parent=parent_window)
            self.logger.debug(f"Confirmation response: {response}")
            return response
        except Exception as e:
             self.logger.error(f"Failed to display confirmation dialog: {e}")
             return False

    def prompt_for_input(self, title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Display a simple input dialog and return the user's input."""
        self.logger.debug(f"Requesting input: Title='{title}', Prompt='{prompt}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            result = simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=parent_window)
            log_result = '<cancelled>' if result is None else '<input provided>'
            self.logger.debug(f"Input dialog result: {log_result}")
            return result
        except Exception as e:
             self.logger.error(f"Failed to display input dialog: {e}")
             return None

    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        if not self.status_bar: self._find_status_bar() # Try finding again

        if self.status_bar:
            # Schedule the update using 'after' to ensure it runs on the main thread
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, lambda msg=message: self.status_bar.set_message(msg))
                 else: self.logger.warning("StatusBar frame no longer exists.")
            except Exception as e: self.logger.error(f"Failed to schedule status update: {e}")
        else: self.logger.debug(f"Status update requested (no status bar found): {message}")


    def clear(self) -> None:
        """Clear or reset the view's state. Needs implementation in subclasses."""
        self.logger.debug(f"Base clear called for {self.__class__.__name__}.")
        self.set_status("Ready.") # Reset status bar
        if self.status_bar:
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, self.status_bar.stop_progress)
            except Exception as e: self.logger.error(f"Error stopping progress bar during clear: {e}")


    def update(self) -> None:
        """Force an update of the UI. Generally not needed unless managing complex state."""
        try:
             # Use the main_frame's toplevel window for update_idletasks
             toplevel = self.main_frame.winfo_toplevel()
             if toplevel.winfo_exists():
                  toplevel.update_idletasks()
                  # self.logger.debug(f"Base update called for {self.__class__.__name__}.") # Can be noisy
        except Exception as e:
             self.logger.error(f"Error during UI update: {e}")
```

## src/main_ui.py

```python
import tkinter as tk
from tkinter import ttk, messagebox, Menu
import logging
import os

# Configuration
from src.config import config # Import the configured instance

# Core components (interfaces needed for type hinting)
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService

# Infrastructure components
from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory

# Application Services
from src.application.services import (
    CredentialService, WorkflowService, WebDriverService,
    SchedulerService, ReportingService # Include stubs
)

# UI components (use final names)
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.ui.views.settings_view import SettingsView # Import new Settings View
from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.ui.presenters.settings_presenter import SettingsPresenter # Import new Settings Presenter
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog # Import Credential Manager Dialog

# Common utilities
# LoggerFactory configures root logger based on AppConfig now
# from src.infrastructure.common.logger_factory import LoggerFactory


def setup_logging():
    """Configure logging based on AppConfig."""
    # BasicConfig is handled by config.py loading now
    # Just get the root logger and ensure level is set
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    # Add file handler if specified in config and not already added
    if config.log_file and not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
         try:
              file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
              formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
              file_handler.setFormatter(formatter)
              root_logger.addHandler(file_handler)
              logging.info(f"Added FileHandler for {config.log_file}")
         except Exception as e:
              logging.error(f"Failed to add FileHandler based on config: {e}")

    logging.info(f"Logging configured. Level: {logging.getLevelName(config.log_level)}")

# --- Global variable for Credential Dialog to prevent multiple instances ---
# (Alternatively, manage dialog lifecycle within a main controller/app class)
credential_dialog_instance: Optional[tk.Toplevel] = None

def main():
    """Main application entry point."""
    # Setup logging first using config values
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"--- Starting {config.WINDOW_TITLE} ---")
    logger.info(f"Using Repository Type: {config.repository_type}")
    logger.info(f"Workflows Path: {config.workflows_path}")
    logger.info(f"Credentials Path: {config.credentials_path}")

    root = tk.Tk()
    root.title(config.WINDOW_TITLE)
    root.geometry(config.WINDOW_GEOMETRY)

    # --- Dependency Injection Setup ---
    try:
        repo_factory = RepositoryFactory()
        webdriver_factory = WebDriverFactory()

        # Ensure directories/files exist for file system repo if selected
        if config.repository_type == "file_system":
            wf_path = config.workflows_path
            cred_path = config.credentials_path
            if not os.path.exists(wf_path):
                os.makedirs(wf_path, exist_ok=True)
                logger.info(f"Created workflows directory: {wf_path}")
            if not os.path.exists(cred_path) and config.repo_create_if_missing:
                with open(cred_path, 'w', encoding='utf-8') as f:
                    f.write("[]") # Create empty JSON list
                logger.info(f"Created empty credentials file: {cred_path}")

        # Create repositories using the factory and config
        workflow_repo: IWorkflowRepository = repo_factory.create_workflow_repository(
            repository_type=config.repository_type,
            path=config.workflows_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        credential_repo: ICredentialRepository = repo_factory.create_credential_repository(
            repository_type=config.repository_type,
            path=config.credentials_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        logger.info("Repositories initialized.")

        # Create Application Services, injecting dependencies
        credential_service = CredentialService(credential_repo)
        webdriver_service = WebDriverService(webdriver_factory)
        workflow_service = WorkflowService(workflow_repo, credential_repo, webdriver_service)
        # Initialize placeholder services (they don't do anything yet)
        scheduler_service = SchedulerService()
        reporting_service = ReportingService()
        logger.info("Application services initialized.")

        # Create Presenters, injecting Service interfaces
        editor_presenter = WorkflowEditorPresenter(workflow_service)
        runner_presenter = WorkflowRunnerPresenter(workflow_service, credential_service, webdriver_service)
        settings_presenter = SettingsPresenter(config) # Settings presenter interacts with config directly
        logger.info("Presenters initialized.")

    except Exception as e:
         logger.exception("FATAL: Failed to initialize core components. Application cannot start.")
         messagebox.showerror("Initialization Error", f"Failed to initialize application components: {e}\n\nPlease check configuration (`config.ini`) and file permissions.\nSee log file '{config.log_file}' for details.")
         root.destroy()
         return

    # --- UI Setup ---
    try:
        # Use themed widgets
        style = ttk.Style(root)
        available_themes = style.theme_names()
        logger.debug(f"Available ttk themes: {available_themes}")
        preferred_themes = ['clam', 'alt', 'vista', 'xpnative', 'aqua', 'default']
        for theme in preferred_themes:
            if theme in available_themes:
                 try: style.theme_use(theme); logger.info(f"Using ttk theme: {theme}"); break
                 except tk.TclError: logger.warning(f"Failed theme: '{theme}'.")
        else: logger.warning("Could not find preferred theme.")

        # --- Menu Bar ---
        menubar = Menu(root)
        root.config(menu=menubar)

        manage_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=manage_menu)

        def open_credential_manager():
             global credential_dialog_instance
             # Prevent multiple instances
             if credential_dialog_instance is not None and credential_dialog_instance.winfo_exists():
                  credential_dialog_instance.lift()
                  credential_dialog_instance.focus_set()
                  logger.debug("Credential Manager dialog already open, focusing.")
                  return
             logger.debug("Opening Credential Manager dialog.")
             # Pass the service to the dialog
             dialog = CredentialManagerDialog(root, credential_service)
             credential_dialog_instance = dialog.window # Store reference to Toplevel
             # Dialog runs its own loop implicitly via wait_window() called by show() if needed
             # For a non-blocking approach, dialog would need different handling.

        manage_menu.add_command(label="Credentials...", command=open_credential_manager)
        # Add other management options later if needed

        # --- Main Content Area (Notebook) ---
        notebook = ttk.Notebook(root)

        # Create Frames for each tab content area
        editor_tab_frame = ttk.Frame(notebook)
        runner_tab_frame = ttk.Frame(notebook)
        settings_tab_frame = ttk.Frame(notebook) # Frame for Settings tab

        notebook.add(editor_tab_frame, text="Workflow Editor")
        notebook.add(runner_tab_frame, text="Workflow Runner")
        notebook.add(settings_tab_frame, text="Settings") # Add Settings tab

        # --- Create Views, injecting presenters ---
        # Views are now created with the tab frame as their parent root
        editor_view = WorkflowEditorView(editor_tab_frame, editor_presenter)
        runner_view = WorkflowRunnerView(runner_tab_frame, runner_presenter)
        settings_view = SettingsView(settings_tab_frame, settings_presenter) # Create Settings view
        logger.info("Views initialized.")

        # --- Link Views and Presenters ---
        editor_presenter.set_view(editor_view)
        runner_presenter.set_view(runner_view)
        settings_presenter.set_view(settings_view) # Link Settings presenter and view
        logger.info("Views linked to presenters.")

        # --- Pack the Notebook ---
        # Pack notebook *after* creating views inside their frames
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Start Application ---
        logger.info("Starting Tkinter main loop.")
        root.mainloop()

    except Exception as e:
         logger.exception("An error occurred during application run.")
         if root.winfo_exists():
              messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\n\nPlease check the log file '{config.log_file}'.")
    finally:
         logger.info("--- Application exiting ---")
         # Cleanup handled within presenter/service threads now.
         # Any final cleanup needed? e.g. saving config explicitly?
         # config.save_config_to_file() # Uncomment if auto-save on exit is desired


if __name__ == "__main__":
    # Import Literal for type hinting if used directly here (it's used in RepositoryFactory)
    from typing import Literal
    main()
```

## src/config.py

```python
"""Handles loading and accessing application configuration from config.ini."""

import configparser
import os
import logging
from typing import Literal, Optional, List

# Define allowed repository types
RepositoryType = Literal["file_system", "database"]
# Define allowed browser types (should align with BrowserType enum if possible)
BrowserTypeStr = Literal["chrome", "firefox", "edge", "safari"]

# Default values in case config.ini is missing or incomplete
DEFAULT_CONFIG = {
    'General': {
        'log_level': 'INFO',
        'log_file': 'autoqliq_app.log',
    },
    'Repository': {
        'type': 'file_system',
        'workflows_path': 'workflows',
        'credentials_path': 'credentials.json',
        'create_if_missing': 'true',
        'db_path': 'autoqliq_data.db'
    },
    'WebDriver': {
        'default_browser': 'chrome',
        'chrome_driver_path': '',
        'firefox_driver_path': '',
        'edge_driver_path': '',
        'implicit_wait': '5',
    },
    'Security': {
        'password_hash_method': 'pbkdf2:sha256:600000',
        'password_salt_length': '16'
    }
}

CONFIG_FILE_NAME = "config.ini" # Standard name

class AppConfig:
    """Loads and provides typed access to application configuration settings."""

    def __init__(self, config_file_path: str = CONFIG_FILE_NAME):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config_file_path = config_file_path
        # Use a temporary basic logger until config is loaded
        self._temp_logger = logging.getLogger(__name__)
        self._load_config()
        # Replace temp logger with one configured according to loaded settings
        self.logger = logging.getLogger(__name__)
        try:
             self.logger.setLevel(self.log_level)
        except Exception:
             self.logger.setLevel(logging.INFO) # Fallback

    def _load_config(self):
        """Loads configuration from the INI file, using defaults."""
        self.config = configparser.ConfigParser(interpolation=None) # Re-initialize parser
        self.config.read_dict(DEFAULT_CONFIG) # Set defaults first
        if os.path.exists(self.config_file_path):
            try:
                read_files = self.config.read(self.config_file_path, encoding='utf-8')
                if read_files: self._temp_logger.info(f"Configuration loaded successfully from: {self.config_file_path}")
                else: self._temp_logger.warning(f"Config file found '{self.config_file_path}' but empty/unreadable. Using defaults.")
            except configparser.Error as e: self._temp_logger.error(f"Error parsing config '{self.config_file_path}': {e}. Using defaults.")
            except Exception as e: self._temp_logger.error(f"Error loading config '{self.config_file_path}': {e}. Using defaults.", exc_info=True)
        else:
            self._temp_logger.warning(f"Config file not found: '{self.config_file_path}'. Using default settings.")
            self._create_default_config()

    def reload_config(self):
        """Reloads the configuration from the file."""
        self.logger.info(f"Reloading configuration from {self.config_file_path}")
        self._load_config()
        # Re-apply logger level after reload
        logging.getLogger().setLevel(self.log_level)
        self.logger.setLevel(self.log_level)
        self.logger.info(f"Configuration reloaded. Log level set to {logging.getLevelName(self.log_level)}.")


    def _create_default_config(self):
        """Creates a default config.ini file if it doesn't exist."""
        try:
            # Ensure directory exists if config_file_path includes directories
            config_dir = os.path.dirname(self.config_file_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                self._temp_logger.info(f"Created directory for config file: {config_dir}")

            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                # Write defaults to the file
                temp_config = configparser.ConfigParser(interpolation=None)
                temp_config.read_dict(DEFAULT_CONFIG)
                temp_config.write(configfile)
            self._temp_logger.info(f"Created default config file: {self.config_file_path}")
        except Exception as e:
            self._temp_logger.error(f"Failed to create default config file '{self.config_file_path}': {e}", exc_info=True)


    def _get_value(self, section: str, key: str, fallback_override: Optional[str] = None) -> Optional[str]:
        """Helper to get value, using internal defaults as ultimate fallback."""
        try:
             if not self.config.has_section(section):
                  self.logger.warning(f"Config section [{section}] not found. Returning fallback '{fallback_override}'.")
                  return fallback_override
             # Use fallback kwarg in get()
             return self.config.get(section, key, fallback=fallback_override)
        except (configparser.NoOptionError):
            self.logger.warning(f"Config key [{section}]{key} not found. Returning fallback '{fallback_override}'.")
            return fallback_override
        except Exception as e:
            self.logger.error(f"Error reading config [{section}]{key}: {e}. Returning fallback '{fallback_override}'.")
            return fallback_override


    def save_setting(self, section: str, key: str, value: str) -> bool:
        """Saves a single setting to the config object (does not write to file yet)."""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value)) # Ensure value is string
            self.logger.info(f"Config setting updated in memory: [{section}]{key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update setting [{section}]{key} in memory: {e}")
            return False

    def save_config_to_file(self) -> bool:
        """Writes the current config object state back to the INI file."""
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved successfully to: {self.config_file_path}")
            # Optionally reload after saving to ensure consistency?
            # self.reload_config()
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration file '{self.config_file_path}': {e}", exc_info=True)
            return False

    # --- Typed Property Accessors ---

    @property
    def log_level(self) -> int:
        level_str = self._get_value('General', 'log_level', DEFAULT_CONFIG['General']['log_level']).upper()
        level = getattr(logging, level_str, logging.INFO)
        if not isinstance(level, int):
             self.logger.warning(f"Invalid log level '{level_str}' in config. Defaulting to INFO.")
             return logging.INFO
        return level

    @property
    def log_file(self) -> str:
        return self._get_value('General', 'log_file', DEFAULT_CONFIG['General']['log_file'])

    @property
    def repository_type(self) -> RepositoryType:
        repo_type = self._get_value('Repository', 'type', DEFAULT_CONFIG['Repository']['type']).lower()
        if repo_type not in ('file_system', 'database'):
            self.logger.warning(f"Invalid repository type '{repo_type}'. Defaulting to '{DEFAULT_CONFIG['Repository']['type']}'.")
            return DEFAULT_CONFIG['Repository']['type'] # type: ignore
        return repo_type # type: ignore

    @property
    def workflows_path(self) -> str:
        # Return path based on type, falling back to defaults if key missing
        repo_type = self.repository_type
        # Determine key and fallback based on repo type
        key = 'db_path' if repo_type == 'database' else 'workflows_path'
        fallback = DEFAULT_CONFIG['Repository'][key]
        return self._get_value('Repository', key, fallback)

    @property
    def credentials_path(self) -> str:
        repo_type = self.repository_type
        key = 'db_path' if repo_type == 'database' else 'credentials_path'
        fallback = DEFAULT_CONFIG['Repository'][key]
        return self._get_value('Repository', key, fallback)

    @property
    def db_path(self) -> str:
         return self._get_value('Repository', 'db_path', DEFAULT_CONFIG['Repository']['db_path'])

    @property
    def repo_create_if_missing(self) -> bool:
        try:
            # Use getboolean which handles true/false, yes/no, 1/0
            return self.config.getboolean('Repository', 'create_if_missing', fallback=True)
        except ValueError:
            fallback = DEFAULT_CONFIG['Repository']['create_if_missing'].lower() == 'true'
            self.logger.warning(f"Invalid boolean value for 'create_if_missing'. Using default: {fallback}.")
            return fallback

    @property
    def default_browser(self) -> BrowserTypeStr:
        browser = self._get_value('WebDriver', 'default_browser', DEFAULT_CONFIG['WebDriver']['default_browser']).lower()
        # Validate against allowed types
        allowed_browsers: List[BrowserTypeStr] = ["chrome", "firefox", "edge", "safari"]
        if browser not in allowed_browsers:
             default_b = DEFAULT_CONFIG['WebDriver']['default_browser']
             self.logger.warning(f"Invalid default browser '{browser}'. Defaulting to '{default_b}'.")
             return default_b # type: ignore
        return browser # type: ignore

    def get_driver_path(self, browser_type: str) -> Optional[str]:
        """Gets the configured path for a specific browser driver, or None."""
        key = f"{browser_type.lower()}_driver_path"
        # Check if key exists before getting, return None if it doesn't
        if self.config.has_option('WebDriver', key):
            path = self.config.get('WebDriver', key)
            return path if path else None # Return None if empty string in config
        return None

    @property
    def implicit_wait(self) -> int:
        try:
            wait_str = self._get_value('WebDriver', 'implicit_wait', DEFAULT_CONFIG['WebDriver']['implicit_wait'])
            wait = int(wait_str or '0') # Default to 0 if empty string
            return max(0, wait) # Ensure non-negative
        except (ValueError, TypeError):
            fallback_wait = int(DEFAULT_CONFIG['WebDriver']['implicit_wait'])
            self.logger.warning(f"Invalid integer value for 'implicit_wait'. Using default: {fallback_wait}.")
            return fallback_wait

    @property
    def password_hash_method(self) -> str:
        return self._get_value('Security', 'password_hash_method', DEFAULT_CONFIG['Security']['password_hash_method'])

    @property
    def password_salt_length(self) -> int:
        try:
            length_str = self._get_value('Security', 'password_salt_length', DEFAULT_CONFIG['Security']['password_salt_length'])
            length = int(length_str or '0') # Default to 0 if empty
            return max(8, length) # Ensure a minimum reasonable salt length (e.g., 8)
        except (ValueError, TypeError):
             fallback_len = int(DEFAULT_CONFIG['Security']['password_salt_length'])
             self.logger.warning(f"Invalid integer value for 'password_salt_length'. Using default: {fallback_len}.")
             return fallback_len


# --- Global Singleton Instance ---
try:
    config = AppConfig()
    # Apply logging level immediately after loading
    logging.getLogger().setLevel(config.log_level) # Set root logger level
    config.logger.info(f"--- Application Configuration Loaded (Level: {logging.getLevelName(config.log_level)}) ---")
    config.logger.info(f"Repository Type: {config.repository_type}")
    if config.repository_type == 'database': config.logger.info(f"Database Path: {config.db_path}")
    else:
        config.logger.info(f"Workflows Path: {config.workflows_path}")
        config.logger.info(f"Credentials Path: {config.credentials_path}")
    config.logger.info(f"Default Browser: {config.default_browser}")
    config.logger.info(f"Implicit Wait: {config.implicit_wait}s")
    config.logger.debug(f"Password Hash Method: {config.password_hash_method}")
except Exception as e:
     logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     logging.critical(f"CRITICAL ERROR: Failed to initialize AppConfig: {e}", exc_info=True)
     raise RuntimeError("Failed to load application configuration. Cannot continue.") from e
```

## config.ini

```ini
[General]
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = DEBUG
log_file = autoqliq_app.log

[Repository]
# Persistence type: file_system or database
type = file_system
# create_if_missing = true ; Option primarily for file system repos, ensures files/dirs are created if not found on startup

# Paths used depend on the 'type' setting above
# If type=file_system:
workflows_path = workflows
credentials_path = credentials.json
# If type=database:
db_path = autoqliq_data.db

[WebDriver]
# Default browser type if not specified elsewhere: chrome, firefox, edge, safari
default_browser = chrome
# Optional explicit path to the webdriver executable (leave blank to use Selenium Manager or system PATH)
chrome_driver_path =
firefox_driver_path =
edge_driver_path =
# Default implicit wait time in seconds for WebDriver find operations
implicit_wait = 5

[Security]
# Hashing method and parameters used by werkzeug.security.generate_password_hash
# pbkdf2:sha256:<iterations> is a common format. Higher iterations = more secure but slower.
# Argon2 ('argon2') is generally preferred if available (`pip install argon2-cffi`).
# Ensure the method string is valid for your werkzeug version.
password_hash_method = pbkdf2:sha256:600000
# Length of the salt used for hashing. 16 is a reasonable default.
password_salt_length = 16
```

## README.md

```markdown
# AutoQliq Application

## Overview

AutoQliq is a Python-based desktop application designed to automate web tasks using Selenium and Tkinter. The application follows SOLID, DRY, and KISS principles with an MVP (Model-View-Presenter) architecture for the UI and a layered approach for backend components. The core functionality allows users to create, edit, save, and run automated web workflows. Persistence can be configured to use either JSON files or an SQLite database. Control flow (conditionals, loops), error handling (try/catch), and action templates are supported.

## Project Structure

```
AutoQliq/
├── requirements.txt              # Python package dependencies
├── config.ini                    # Application configuration settings
├── README.md                     # This file
├── credentials.json              # Example credential file (if using file_system repo)
├── workflows/                    # Example workflow directory (if using file_system repo)
│   └── example_workflow.json     # Example workflow definition
├── templates/                    # Example template directory (if using file_system repo)
│   └── example_template.json   # Example template definition
├── logs/                         # Directory where execution logs are saved (JSON format)
├── autoqliq_data.db              # Example database file (if using database repo)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Loads and provides config.ini settings
│   ├── core/                     # Core domain logic and interfaces
│   │   ├── interfaces/           # Core interfaces (Action, Repository, WebDriver, Service)
│   │   ├── actions/              # Concrete Action implementations (incl. Conditional, Loop, ErrorHandling, Template)
│   │   ├── workflow/             # Workflow execution logic (Runner)
│   │   ├── exceptions.py         # Custom application exceptions
│   │   └── action_result.py      # ActionResult class
│   ├── infrastructure/           # Implementation of external concerns
│   │   ├── common/               # Shared utilities
│   │   ├── repositories/         # Persistence implementations (FS, DB for Workflows, Credentials, Templates)
│   │   └── webdrivers/           # WebDriver implementations (Selenium)
│   ├── application/              # Application service layer
│   │   ├── services/             # Service implementations (Credential, Workflow, WebDriver, Scheduler[stub], Reporting[stub+log])
│   │   └── interfaces/           # Deprecated - imports from core.interfaces.service
│   ├── ui/                       # User Interface (Tkinter MVP)
│   │   ├── common/               # Common UI utilities
│   │   ├── dialogs/              # Custom dialog windows (ActionEditor, CredentialManager)
│   │   ├── interfaces/           # UI layer interfaces (IView, IPresenter)
│   │   ├── presenters/           # Presenter implementations (Editor, Runner, Settings)
│   │   └── views/                # View implementations (Editor, Runner, Settings)
│   └── main_ui.py                # Main application entry point, DI, starts UI loop
└── tests/
    ├── __init__.py
    ├── unit/                     # Unit tests (mock external dependencies)
    │   ├── application/          # Tests for application services
    │   ├── core/                 # Tests for core actions, runner
    │   ├── infrastructure/       # Tests for repositories (FS, DB with mocks)
    │   └── ui/                   # Tests for presenters
    └── integration/              # Integration tests (interact with real DB/WebDriver/FS)
        ├── __init__.py
        ├── test_database_repository_integration.py
        ├── test_webdriver_integration.py
        ├── test_service_repository_integration.py # New
        └── test_workflow_execution.py             # Placeholder

```

## Configuration (`config.ini`)

Application behavior is configured via `config.ini`. Key settings:

- `[Repository] type`: `file_system` or `database`.
- `[Repository] paths`: Set `workflows_path`, `credentials_path`, `db_path` as needed for the chosen type. Templates use a `templates` subdir relative to `workflows_path` (FS) or a `templates` table (DB).
- `[WebDriver] default_browser`: `chrome`, `firefox`, `edge`, `safari`.
- `[WebDriver] *_driver_path`: Optional explicit paths to WebDriver executables.
- `[WebDriver] implicit_wait`: Default implicit wait time (seconds).
- `[Security]`: Configure password hashing method and salt length (requires `werkzeug`).

A default `config.ini` is created if missing. Settings can be modified via the "Settings" tab in the UI.

## Installation

1.  Clone the repository.
2.  Create/activate a Python virtual environment (`>=3.8` recommended).
3.  Install dependencies: `pip install -r requirements.txt`
4.  Install necessary WebDriver executables (e.g., `chromedriver`) if not using Selenium Manager or if specifying explicit paths in `config.ini`.

## Usage

1.  **Configure `config.ini`** (or use defaults/Settings tab).
2.  **Manage Credentials**: Use the "Manage" -> "Credentials..." menu item. Passwords are hashed on save. **Note:** Existing plaintext passwords need re-saving via UI.
3.  **Manage Workflows/Templates**: Use the "Workflow Editor" tab.
    - Create/Edit/Delete workflows.
    - Save reusable sequences as templates (currently requires manual file/DB operation - UI needed).
    - Use the `TemplateAction` type in the Action Editor to reference a saved template by name.
4.  **Run Workflows**: Use the "Workflow Runner" tab. Select workflow/credential, click "Run". Execution is backgrounded; logs appear. Use "Stop" to request cancellation.
5.  **Manage Settings**: Use the "Settings" tab to view/modify configuration. Click "Save Settings" to persist changes.
6.  **Execution Logs**: Basic execution logs (status, duration, results) are saved as JSON files in the `logs/` directory.

## Workflow Action Types

Workflows are lists of action dictionaries. Supported `type` values:

- `Navigate`: Goes to a URL (`url`).
- `Click`: Clicks an element (`selector`).
- `Type`: Types text (`value_key`) based on `value_type` ('text' or 'credential') into an element (`selector`).
- `Wait`: Pauses execution (`duration_seconds`).
- `Screenshot`: Takes a screenshot (`file_path`).
- `Conditional`: Executes actions based on a condition.
  - `condition_type`: 'element_present', 'element_not_present', 'variable_equals', 'javascript_eval'.
  - Requires parameters like `selector`, `variable_name`, `expected_value`, `script` based on `condition_type`.
  - `true_branch`: List of actions if condition is true.
  - `false_branch`: List of actions if condition is false.
- `Loop`: Repeats actions.
  - `loop_type`: 'count', 'for_each', 'while'.
  - Requires parameters like `count`, `list_variable_name`, or condition parameters based on `loop_type`.
  - `loop_actions`: List of actions to repeat. Context variables `loop_index`, `loop_iteration`, `loop_total`, `loop_item` are available to nested actions.
- `ErrorHandling`: Executes 'try' actions, runs 'catch' actions on failure.
  - `try_actions`: List of actions to attempt.
  - `catch_actions`: List of actions to run if try block fails. Context variables `try_block_error_message`, `try_block_error_type` available in catch.
- `Template`: Executes a saved template.
  - `template_name`: The name of the saved template to execute.

_(See `ActionEditorDialog` or action class docstrings for specific parameters)_

## Testing

- **Unit Tests:** `pytest tests/unit`
- **Integration Tests:** `pytest tests/integration` (Requires WebDriver setup, uses in-memory DB)

## Contributing

Contributions welcome!

## License

MIT License.
```

