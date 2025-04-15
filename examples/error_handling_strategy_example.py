"""Example demonstrating the WorkflowRunner error handling strategies."""

import sys
import os
import logging
from typing import List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.interfaces import IAction
from src.core.action_result import ActionResult
from src.core.workflow.runner import WorkflowRunner, ErrorHandlingStrategy
# Create a simple mock driver for the example
from src.core.interfaces import IWebDriver


class MockWebDriver(IWebDriver):
    """A simple mock implementation of IWebDriver for the example."""

    def __init__(self):
        self.browser_type = "mock"

    # Basic browser operations
    def open(self) -> None: pass
    def close(self) -> None: pass
    def quit(self) -> None: pass
    def navigate(self, url: str) -> None: pass
    def get(self, url: str) -> None: pass
    def get_current_url(self) -> str: return "https://example.com"
    def get_page_source(self) -> str: return "<html><body>Mock page</body></html>"
    def get_title(self) -> str: return "Mock Browser"

    # Element operations
    def find_element(self, selector: str) -> object: return None
    def find_elements(self, selector: str) -> list: return []
    def is_element_present(self, selector: str) -> bool: return True
    def click_element(self, selector: str) -> None: pass
    def type_text(self, selector: str, text: str) -> None: pass

    # JavaScript and advanced operations
    def execute_script(self, script: str, *args) -> any: return None
    def take_screenshot(self, file_path: str) -> bool: return True

    # Wait operations
    def wait_for_element(self, selector: str, timeout: int = 10) -> object: return None
    def wait_for_element_visible(self, selector: str, timeout: int = 10) -> object: return None
    def wait_for_element_clickable(self, selector: str, timeout: int = 10) -> object: return None

    # Frame and alert operations
    def switch_to_frame(self, frame_reference) -> None: pass
    def switch_to_default_content(self) -> None: pass
    def accept_alert(self) -> None: pass
    def dismiss_alert(self) -> None: pass
    def get_alert_text(self) -> str: return "Mock Alert Text"


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class SimpleAction(IAction):
    """A simple action for demonstration purposes."""

    def __init__(self, name: str, should_succeed: bool = True):
        self.name = name
        self.action_type = "SimpleAction"
        self.should_succeed = should_succeed

    def validate(self) -> None:
        """Validate the action."""
        pass

    def execute(self, driver, credential_repo, context=None):
        """Execute the action."""
        if self.should_succeed:
            print(f"Action '{self.name}' succeeded")
            return ActionResult.success(f"Action '{self.name}' succeeded")
        else:
            print(f"Action '{self.name}' failed")
            return ActionResult.failure(f"Action '{self.name}' failed")

    def to_dict(self):
        """Convert the action to a dictionary."""
        return {
            "name": self.name,
            "action_type": self.action_type,
            "should_succeed": self.should_succeed
        }


def run_with_strategy(actions: List[IAction], strategy: ErrorHandlingStrategy):
    """Run a workflow with the specified error handling strategy."""
    print(f"\nRunning with {strategy.name} strategy:")
    print("-" * 50)

    # Create a mock driver
    driver = MockWebDriver()

    # Create a workflow runner with the specified strategy
    runner = WorkflowRunner(driver, error_strategy=strategy)

    # Run the workflow
    result = runner.run(actions, f"Example Workflow ({strategy.name})")

    # Print the results
    print(f"Final status: {result['final_status']}")
    print(f"Error message: {result.get('error_message', 'None')}")
    print(f"Summary: {result.get('summary', 'None')}")
    print(f"Action results:")
    for i, action_result in enumerate(result["action_results"]):
        print(f"  {i+1}. Status: {action_result['status']}, Message: {action_result['message']}")
    print("-" * 50)

    return result


def main():
    """Run the example."""
    # Create a list of actions with one failing action
    actions = [
        SimpleAction("Action1", True),
        SimpleAction("Action2", False),  # This action will fail
        SimpleAction("Action3", True)
    ]

    # Run with STOP_ON_ERROR strategy
    stop_result = run_with_strategy(actions, ErrorHandlingStrategy.STOP_ON_ERROR)

    # Run with CONTINUE_ON_ERROR strategy
    continue_result = run_with_strategy(actions, ErrorHandlingStrategy.CONTINUE_ON_ERROR)

    # Compare the results
    print("\nComparison:")
    print(f"STOP_ON_ERROR executed {len(stop_result['action_results'])} actions")
    print(f"CONTINUE_ON_ERROR executed {len(continue_result['action_results'])} actions")


if __name__ == "__main__":
    main()
