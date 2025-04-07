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
        """
        Schedule a workflow to run based on the configuration.

        Args:
            workflow_name: Name of the workflow to schedule.
            credential_name: Optional credential name to use for the run.
            schedule_config: Dictionary defining the schedule (e.g., {'trigger': 'cron', 'hour': '3', 'minute': '0'}).
                             Format depends on the underlying scheduler library (e.g., APScheduler).

        Returns:
            A unique job ID for the scheduled task.

        Raises:
            SchedulerError: If scheduling fails (e.g., invalid config, scheduler not running).
            WorkflowError: If the specified workflow doesn't exist.
            CredentialError: If the specified credential doesn't exist (optional check).
        """
        pass

    @abc.abstractmethod
    def list_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """
        List currently scheduled jobs and their details.
        Details might include job ID, workflow name, next run time, schedule config.
        """
        pass

    @abc.abstractmethod
    def cancel_scheduled_job(self, job_id: str) -> bool:
        """
        Cancel (remove) a scheduled job by its ID.
        Returns True if cancelled, False if job_id not found.
        """
        pass

    # Optional methods: pause_job, resume_job, modify_job, get_job_details


class IReportingService(IService):
    """Interface for services managing workflow execution reporting."""
    # This interface assumes some mechanism exists for logging execution results.

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
        """Generate a summary report of workflow executions (counts, success rates)."""
        pass

    @abc.abstractmethod
    def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results (including action results) for a specific past execution."""
        pass

    @abc.abstractmethod
    def list_past_executions(self, workflow_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List past workflow execution records (summary info)."""
        pass

    # Optional: methods for cleaning up old execution logs