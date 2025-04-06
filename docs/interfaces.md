# Core Interfaces Documentation

This document provides detailed information about the core interfaces in the AutoQliq application.

## Table of Contents

1. [IWebDriver Interface](#iwebdriver-interface)
2. [IAction Interface](#iaction-interface)
3. [IWorkflowRepository Interface](#iworkflowrepository-interface)
4. [ICredentialRepository Interface](#icredentialrepository-interface)

## IWebDriver Interface

The `IWebDriver` interface defines the contract for browser automation in the AutoQliq application. It abstracts the underlying web driver implementation, allowing the application to work with different browser automation libraries.

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `get` | `url: str` | `None` | Navigates to the specified URL |
| `quit` | None | `None` | Closes the browser and releases resources |
| `find_element` | `selector: str` | `Any` | Finds an element on the page using the specified selector |
| `click_element` | `selector: str` | `None` | Clicks on the element identified by the selector |
| `type_text` | `selector: str, text: str` | `None` | Types the specified text into the element identified by the selector |
| `take_screenshot` | `file_path: str` | `None` | Takes a screenshot and saves it to the specified file path |
| `is_element_present` | `selector: str` | `bool` | Checks if an element is present on the page |
| `get_current_url` | None | `str` | Returns the current URL of the browser |

### Usage Example

```python
from src.core.interfaces import IWebDriver
from src.infrastructure.webdrivers import ChromeWebDriver

# Create a web driver instance
driver: IWebDriver = ChromeWebDriver()

# Navigate to a website
driver.get("https://example.com")

# Interact with elements
if driver.is_element_present("#login-button"):
    driver.click_element("#login-button")
    driver.type_text("#username", "user@example.com")
    driver.type_text("#password", "password123")
    driver.click_element("#submit-button")

# Take a screenshot
driver.take_screenshot("login_success.png")

# Close the browser
driver.quit()
```

## IAction Interface

The `IAction` interface defines the contract for actions that can be executed as part of a workflow. Actions represent discrete steps in a browser automation workflow, such as navigating to a URL, clicking a button, or typing text.

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `execute` | `driver: IWebDriver` | `Any` | Executes the action using the provided web driver |
| `to_dict` | None | `Dict[str, Any]` | Converts the action to a dictionary representation for serialization |

### Usage Example

```python
from src.core.interfaces import IAction, IWebDriver
from src.core.actions import NavigateAction, ClickAction, TypeAction

# Create actions
navigate_action: IAction = NavigateAction(url="https://example.com")
click_action: IAction = ClickAction(selector="#login-button")
type_action: IAction = TypeAction(selector="#username", value_type="text", value_key="user@example.com")

# Execute actions with a web driver
driver: IWebDriver = get_web_driver()
navigate_action.execute(driver)
click_action.execute(driver)
type_action.execute(driver)

# Serialize actions to dictionaries
navigate_dict = navigate_action.to_dict()
click_dict = click_action.to_dict()
type_dict = type_action.to_dict()
```

## IWorkflowRepository Interface

The `IWorkflowRepository` interface defines the contract for storing and retrieving workflows. A workflow is a sequence of actions that can be executed together to automate a specific task.

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `save` | `name: str, workflow_actions: List[IAction]` | `None` | Saves a workflow with the specified name and actions |
| `load` | `name: str` | `List[IAction]` | Loads a workflow with the specified name |
| `list_workflows` | None | `List[str]` | Returns a list of all available workflow names |

### Usage Example

```python
from src.core.interfaces import IWorkflowRepository, IAction
from src.infrastructure.persistence import JsonWorkflowRepository
from src.core.actions import NavigateAction, ClickAction, TypeAction

# Create a workflow repository
repo: IWorkflowRepository = JsonWorkflowRepository("workflows.json")

# Create actions for a workflow
actions: List[IAction] = [
    NavigateAction(url="https://example.com"),
    ClickAction(selector="#login-button"),
    TypeAction(selector="#username", value_type="credential", value_key="example_login.username")
]

# Save the workflow
repo.save("login_workflow", actions)

# List all workflows
workflow_names = repo.list_workflows()
print(f"Available workflows: {workflow_names}")

# Load a workflow
loaded_actions = repo.load("login_workflow")
```

## ICredentialRepository Interface

The `ICredentialRepository` interface defines the contract for storing and retrieving credentials. Credentials are used to authenticate with websites and services during workflow execution.

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `get_all` | None | `List[Dict[str, str]]` | Returns a list of all available credentials |
| `get_by_name` | `name: str` | `Optional[Dict[str, str]]` | Returns the credential with the specified name, or None if not found |

### Usage Example

```python
from src.core.interfaces import ICredentialRepository
from src.infrastructure.persistence import JsonCredentialRepository

# Create a credential repository
repo: ICredentialRepository = JsonCredentialRepository("credentials.json")

# Get all credentials
all_credentials = repo.get_all()
for credential in all_credentials:
    print(f"Credential: {credential['name']}")

# Get a specific credential
login_credential = repo.get_by_name("example_login")
if login_credential:
    username = login_credential["username"]
    password = login_credential["password"]
    print(f"Found credential: {username}")
else:
    print("Credential not found")
```
