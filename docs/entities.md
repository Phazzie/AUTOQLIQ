# Domain Entities Documentation

This document provides detailed information about the domain entities in the AutoQliq application.

## Table of Contents

1. [Credential Entity](#credential-entity)
2. [ActionBase Class](#actionbase-class)
3. [ActionResult Entity](#actionresult-entity)
4. [Workflow Entity](#workflow-entity)
5. [Action Implementations](#action-implementations)

## Credential Entity

The `Credential` entity represents a set of login credentials for a website or service. It encapsulates a name, username, and password, and provides methods for validation, serialization, and deserialization.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | A unique identifier for this credential set |
| `username` | `str` | The username or email for login |
| `password` | `str` | The password for login |

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `__post_init__` | None | `None` | Validates the credential data after initialization |
| `to_json` | None | `str` | Serializes the credential to a JSON string |
| `from_dict` (class method) | `data: Dict[str, Any]` | `Credential` | Creates a Credential instance from a dictionary |
| `from_json` (class method) | `json_data: str` | `Credential` | Creates a Credential instance from a JSON string |

### Usage Example

```python
from src.core.credentials import Credential

# Create a credential
credential = Credential(
    name="example_login",
    username="user@example.com",
    password="password123"
)

# Serialize to JSON
json_str = credential.to_json()
print(f"JSON: {json_str}")

# Deserialize from JSON
deserialized = Credential.from_json(json_str)
print(f"Deserialized: {deserialized}")

# Deserialize from dictionary
data = {
    "name": "another_login",
    "username": "another@example.com",
    "password": "another123"
}
from_dict = Credential.from_dict(data)
print(f"From dict: {from_dict}")
```

## ActionBase Class

The `ActionBase` abstract class provides a common base for all action implementations. It implements the `IAction` interface and provides shared functionality for action validation and execution.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | A descriptive name for the action |

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `validate` | None | `bool` | Validates that the action is properly configured |
| `execute` (abstract) | `driver: IWebDriver` | `ActionResult` | Executes the action using the provided web driver |
| `to_dict` (abstract) | None | `Dict[str, Any]` | Converts the action to a dictionary representation |

### Usage Example

```python
from src.core.action_base import ActionBase, ActionResult
from src.core.interfaces import IWebDriver

# Create a concrete action class
class MyAction(ActionBase):
    def __init__(self, name: str, param: str):
        super().__init__(name)
        self.param = param
        
    def validate(self) -> bool:
        # Custom validation logic
        return bool(self.param)
        
    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            # Action implementation
            print(f"Executing {self.name} with param {self.param}")
            return ActionResult.success(f"Action {self.name} completed successfully")
        except Exception as e:
            return ActionResult.failure(f"Action {self.name} failed: {str(e)}")
            
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MyAction",
            "name": self.name,
            "param": self.param
        }

# Create and use the action
action = MyAction("test_action", "test_param")
if action.validate():
    result = action.execute(driver)
    if result.is_success():
        print(f"Success: {result.message}")
    else:
        print(f"Failure: {result.message}")
```

## ActionResult Entity

The `ActionResult` entity represents the result of an action execution. It encapsulates a status (success or failure) and an optional message providing details about the result.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `status` | `ActionStatus` | The status of the action execution (SUCCESS or FAILURE) |
| `message` | `Optional[str]` | An optional message providing details about the result |

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `is_success` | None | `bool` | Checks if the result represents a successful execution |
| `success` (class method) | `message: Optional[str] = None` | `ActionResult` | Creates a success result |
| `failure` (class method) | `message: str = "Action failed"` | `ActionResult` | Creates a failure result |

### Usage Example

```python
from src.core.action_base import ActionResult, ActionStatus

# Create success result
success_result = ActionResult.success("Operation completed successfully")
print(f"Success result: {success_result}")
print(f"Is success: {success_result.is_success()}")

# Create failure result
failure_result = ActionResult.failure("Operation failed due to network error")
print(f"Failure result: {failure_result}")
print(f"Is success: {failure_result.is_success()}")

# Create result with explicit status
custom_result = ActionResult(ActionStatus.SUCCESS, "Custom message")
print(f"Custom result: {custom_result}")
```

## Workflow Entity

The `Workflow` entity represents a sequence of actions that can be executed together to automate a specific task. It provides methods for managing actions, execution, and serialization/deserialization.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | A unique identifier for this workflow |
| `actions` | `List[IAction]` | A list of actions to be executed in sequence |

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `add_action` | `action: IAction` | `None` | Adds an action to the workflow |
| `remove_action` | `index: int` | `None` | Removes an action from the workflow |
| `execute` | `driver: IWebDriver` | `List[ActionResult]` | Executes all actions in the workflow |
| `to_dict` | None | `Dict[str, Any]` | Converts the workflow to a dictionary representation |
| `to_json` | None | `str` | Converts the workflow to a JSON string |
| `from_dict` (class method) | `data: Dict[str, Any]` | `Workflow` | Creates a Workflow instance from a dictionary |
| `from_json` (class method) | `json_str: str` | `Workflow` | Creates a Workflow instance from a JSON string |

### Usage Example

```python
from src.core.workflow_entity import Workflow
from src.core.actions import NavigateAction, ClickAction, TypeAction
from src.core.interfaces import IWebDriver

# Create actions
actions = [
    NavigateAction(url="https://example.com"),
    ClickAction(selector="#login-button"),
    TypeAction(selector="#username", value_type="credential", value_key="example_login.username")
]

# Create workflow
workflow = Workflow(name="login_workflow", actions=actions)

# Add another action
workflow.add_action(TypeAction(selector="#password", value_type="credential", value_key="example_login.password"))

# Remove an action
workflow.remove_action(0)  # Remove the first action

# Execute workflow
driver: IWebDriver = get_web_driver()
results = workflow.execute(driver)
for i, result in enumerate(results):
    print(f"Action {i}: {'Success' if result.is_success() else 'Failure'} - {result.message}")

# Serialize to JSON
json_str = workflow.to_json()
print(f"JSON: {json_str}")

# Deserialize from JSON
deserialized = Workflow.from_json(json_str)
print(f"Deserialized: {deserialized}")
```

## Action Implementations

AutoQliq provides several concrete action implementations that can be used in workflows:

### NavigateAction

Navigates to a specified URL.

```python
from src.core.actions import NavigateAction

# Create a navigate action
action = NavigateAction(url="https://example.com")
```

### ClickAction

Clicks on an element identified by a selector.

```python
from src.core.actions import ClickAction

# Create a click action
action = ClickAction(selector="#login-button")

# Create a click action with success/failure checks
action = ClickAction(
    selector="#login-button",
    check_success_selector="#dashboard",
    check_failure_selector="#login-error"
)
```

### TypeAction

Types text into an element identified by a selector.

```python
from src.core.actions import TypeAction

# Create a type action with static text
action = TypeAction(selector="#username", value_type="text", value_key="user@example.com")

# Create a type action with credential reference
action = TypeAction(selector="#password", value_type="credential", value_key="example_login.password")
```

### WaitAction

Waits for a specified duration.

```python
from src.core.actions import WaitAction

# Create a wait action (wait for 3 seconds)
action = WaitAction(duration_seconds=3)
```

### ScreenshotAction

Takes a screenshot and saves it to a specified file path.

```python
from src.core.actions import ScreenshotAction

# Create a screenshot action
action = ScreenshotAction(file_path="login_screen.png")
```

### ActionFactory

The `ActionFactory` class provides a factory method for creating actions from dictionaries:

```python
from src.core.actions import ActionFactory

# Create an action from a dictionary
action_dict = {
    "type": "Navigate",
    "url": "https://example.com"
}
action = ActionFactory.create_action(action_dict)

# Create multiple actions
action_dicts = [
    {"type": "Navigate", "url": "https://example.com"},
    {"type": "Click", "selector": "#login-button"},
    {"type": "Type", "selector": "#username", "value_type": "text", "value_key": "user@example.com"}
]
actions = [ActionFactory.create_action(action_dict) for action_dict in action_dicts]
```
