# Custom Exceptions Documentation

This document provides detailed information about the custom exceptions in the AutoQliq application.

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [AutoQliqError](#autoqliqerror)
3. [WorkflowError](#workflowerror)
4. [ActionError](#actionerror)
5. [ValidationError](#validationerror)
6. [CredentialError](#credentialerror)
7. [WebDriverError](#webdrivererror)
8. [Best Practices](#best-practices)

## Exception Hierarchy

The AutoQliq application uses a hierarchical exception system to provide structured error handling:

```
Exception
└── AutoQliqError (Base exception for all AutoQliq-specific errors)
    ├── WorkflowError (Errors related to workflow execution)
    ├── ActionError (Errors related to action execution)
    │   └── LoginFailedError (Specialized error for login failures)
    ├── ValidationError (Errors related to validation)
    ├── CredentialError (Errors related to credentials)
    └── WebDriverError (Errors related to web driver operations)
```

This hierarchy allows for both specific and general exception handling, depending on the needs of the calling code.

## AutoQliqError

The `AutoQliqError` class is the base exception for all AutoQliq-specific errors. It provides common functionality for all custom exceptions in the application.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Methods

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `_format_message` | None | `str` | Formats the error message, including cause information if available |

### Usage Example

```python
from src.core.exceptions import AutoQliqError

# Create a basic error
error = AutoQliqError("Something went wrong")
print(str(error))  # Output: "Something went wrong"

# Create an error with a cause
try:
    # Some operation that might fail
    result = 1 / 0
except Exception as e:
    # Wrap the original exception
    error = AutoQliqError("Failed to perform calculation", cause=e)
    print(str(error))  # Output: "Failed to perform calculation (caused by: ZeroDivisionError - division by zero)"
```

## WorkflowError

The `WorkflowError` class represents errors that occur during workflow execution.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `workflow_name` | `Optional[str]` | The name of the workflow that encountered the error |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Usage Example

```python
from src.core.exceptions import WorkflowError

# Create a basic workflow error
error = WorkflowError("Failed to execute workflow")
print(str(error))  # Output: "Failed to execute workflow"

# Create a workflow error with workflow name
error = WorkflowError("Failed to execute workflow", workflow_name="login_workflow")
print(str(error))  # Output: "Failed to execute workflow (workflow: login_workflow)"

# Create a workflow error with a cause
try:
    # Some operation that might fail
    result = 1 / 0
except Exception as e:
    # Wrap the original exception
    error = WorkflowError("Failed to execute workflow", workflow_name="login_workflow", cause=e)
    print(str(error))  # Output: "Failed to execute workflow (workflow: login_workflow) (caused by: ZeroDivisionError - division by zero)"
```

## ActionError

The `ActionError` class represents errors that occur during action execution.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `action_name` | `Optional[str]` | The name of the action that encountered the error |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Usage Example

```python
from src.core.exceptions import ActionError

# Create a basic action error
error = ActionError("Failed to execute action")
print(str(error))  # Output: "Failed to execute action"

# Create an action error with action name
error = ActionError("Failed to execute action", action_name="ClickLoginButton")
print(str(error))  # Output: "Failed to execute action (action: ClickLoginButton)"

# Create an action error with a cause
try:
    # Some operation that might fail
    result = 1 / 0
except Exception as e:
    # Wrap the original exception
    error = ActionError("Failed to execute action", action_name="ClickLoginButton", cause=e)
    print(str(error))  # Output: "Failed to execute action (action: ClickLoginButton) (caused by: ZeroDivisionError - division by zero)"
```

## ValidationError

The `ValidationError` class represents errors that occur during validation of entities or inputs.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `field_name` | `Optional[str]` | The name of the field that failed validation |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Usage Example

```python
from src.core.exceptions import ValidationError

# Create a basic validation error
error = ValidationError("Validation failed")
print(str(error))  # Output: "Validation failed"

# Create a validation error with field name
error = ValidationError("Value cannot be empty", field_name="username")
print(str(error))  # Output: "Value cannot be empty (field: username)"

# Create a validation error with a cause
try:
    # Some operation that might fail
    int("not_a_number")
except Exception as e:
    # Wrap the original exception
    error = ValidationError("Invalid number format", field_name="age", cause=e)
    print(str(error))  # Output: "Invalid number format (field: age) (caused by: ValueError - invalid literal for int() with base 10: 'not_a_number')"
```

## CredentialError

The `CredentialError` class represents errors related to credentials.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `credential_name` | `Optional[str]` | The name of the credential that encountered the error |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Usage Example

```python
from src.core.exceptions import CredentialError

# Create a basic credential error
error = CredentialError("Failed to load credential")
print(str(error))  # Output: "Failed to load credential"

# Create a credential error with credential name
error = CredentialError("Credential not found", credential_name="example_login")
print(str(error))  # Output: "Credential not found (credential: example_login)"

# Create a credential error with a cause
try:
    # Some operation that might fail
    with open("non_existent_file.json", "r") as f:
        pass
except Exception as e:
    # Wrap the original exception
    error = CredentialError("Failed to load credentials file", cause=e)
    print(str(error))  # Output: "Failed to load credentials file (caused by: FileNotFoundError - [Errno 2] No such file or directory: 'non_existent_file.json')"
```

## WebDriverError

The `WebDriverError` class represents errors related to web driver operations.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `message` | `str` | The error message |
| `driver_type` | `Optional[str]` | The type of web driver that encountered the error |
| `cause` | `Optional[Exception]` | The original exception that caused this error, if any |

### Usage Example

```python
from src.core.exceptions import WebDriverError

# Create a basic web driver error
error = WebDriverError("Failed to initialize web driver")
print(str(error))  # Output: "Failed to initialize web driver"

# Create a web driver error with driver type
error = WebDriverError("Failed to initialize web driver", driver_type="Chrome")
print(str(error))  # Output: "Failed to initialize web driver (driver: Chrome)"

# Create a web driver error with a cause
try:
    # Some operation that might fail
    raise RuntimeError("Driver executable not found")
except Exception as e:
    # Wrap the original exception
    error = WebDriverError("Failed to initialize web driver", driver_type="Chrome", cause=e)
    print(str(error))  # Output: "Failed to initialize web driver (driver: Chrome) (caused by: RuntimeError - Driver executable not found)"
```

## Best Practices

Here are some best practices for using exceptions in the AutoQliq application:

### 1. Use the Most Specific Exception Type

Always use the most specific exception type that applies to the error situation:

```python
# Good: Using specific exception types
if not credential:
    raise CredentialError(f"Credential not found: {name}", credential_name=name)

if not element:
    raise ActionError(f"Element not found: {selector}", action_name="ClickAction")

# Bad: Using generic exception types
if not credential:
    raise Exception(f"Credential not found: {name}")

if not element:
    raise AutoQliqError(f"Element not found: {selector}")
```

### 2. Include Context Information

Always include relevant context information in the exception:

```python
# Good: Including context information
raise WorkflowError("Failed to execute workflow", workflow_name=workflow_name)
raise ActionError("Failed to click element", action_name=self.name)

# Bad: Missing context information
raise WorkflowError("Failed to execute workflow")
raise ActionError("Failed to click element")
```

### 3. Preserve the Original Exception

When catching and re-raising exceptions, preserve the original exception as the cause:

```python
# Good: Preserving the original exception
try:
    driver.click_element(selector)
except Exception as e:
    raise ActionError(f"Failed to click element: {selector}", action_name=self.name, cause=e)

# Bad: Losing the original exception
try:
    driver.click_element(selector)
except Exception:
    raise ActionError(f"Failed to click element: {selector}", action_name=self.name)
```

### 4. Use Exception Hierarchies for Handling

Take advantage of the exception hierarchy for handling exceptions at different levels:

```python
try:
    workflow.execute(driver)
except LoginFailedError as e:
    # Handle login failure specifically
    print(f"Login failed: {e}")
except ActionError as e:
    # Handle any action error
    print(f"Action failed: {e}")
except WorkflowError as e:
    # Handle any workflow error
    print(f"Workflow failed: {e}")
except AutoQliqError as e:
    # Handle any AutoQliq error
    print(f"AutoQliq error: {e}")
except Exception as e:
    # Handle any other exception
    print(f"Unexpected error: {e}")
```
