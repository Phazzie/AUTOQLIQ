# AutoQliq Documentation

Welcome to the AutoQliq documentation! This documentation provides detailed information about the AutoQliq application, a browser automation tool designed to simplify repetitive web tasks.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [Getting Started](#getting-started)
4. [Advanced Usage](#advanced-usage)
5. [API Reference](#api-reference)

## Introduction

AutoQliq is a browser automation tool that allows you to create, save, and execute workflows for repetitive web tasks. It provides a simple, intuitive interface for defining actions such as navigating to URLs, clicking buttons, typing text, and taking screenshots.

Key features of AutoQliq include:

- **Workflow Creation**: Create sequences of actions that can be executed together
- **Credential Management**: Securely store and use login credentials
- **Browser Automation**: Automate browser interactions using a simple, consistent interface
- **Error Handling**: Robust error handling with detailed error messages
- **Extensibility**: Easily extend the application with new action types and browser drivers

## Core Components

AutoQliq is built around several core components:

- **Interfaces**: Define the contracts for browser automation, actions, and repositories
- **Domain Entities**: Represent the core concepts of the application, such as credentials, actions, and workflows
- **Custom Exceptions**: Provide structured error handling throughout the application
- **Infrastructure**: Implement the interfaces for specific technologies (e.g., Selenium for browser automation)
- **UI**: Provide a user interface for creating and executing workflows

For detailed information about each component, see the following documentation:

- [Core Interfaces](interfaces.md)
- [Domain Entities](entities.md)
- [Custom Exceptions](exceptions.md)

## Getting Started

### Installation

To install AutoQliq, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/autoqliq.git
   cd autoqliq
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

### Creating Your First Workflow

1. **Define Credentials**:
   Create a `credentials.json` file with your login credentials:
   ```json
   [
     {
       "name": "example_login",
       "username": "user@example.com",
       "password": "password123"
     }
   ]
   ```

2. **Create a Workflow**:
   ```python
   from src.core.workflow_entity import Workflow
   from src.core.actions import NavigateAction, ClickAction, TypeAction

   # Create actions
   actions = [
       NavigateAction(url="https://example.com"),
       ClickAction(selector="#login-button"),
       TypeAction(selector="#username", value_type="credential", value_key="example_login.username"),
       TypeAction(selector="#password", value_type="credential", value_key="example_login.password"),
       ClickAction(selector="#submit-button")
   ]

   # Create workflow
   workflow = Workflow(name="login_workflow", actions=actions)

   # Save workflow
   from src.infrastructure.persistence import JsonWorkflowRepository
   repo = JsonWorkflowRepository("workflows.json")
   repo.save(workflow.name, workflow.actions)
   ```

3. **Execute a Workflow**:
   ```python
   from src.core.workflow import WorkflowRunner
   from src.infrastructure.webdrivers import ChromeWebDriver
   from src.infrastructure.persistence import JsonWorkflowRepository, JsonCredentialRepository

   # Create repositories
   workflow_repo = JsonWorkflowRepository("workflows.json")
   credential_repo = JsonCredentialRepository("credentials.json")

   # Create web driver
   driver = ChromeWebDriver()

   # Create workflow runner
   runner = WorkflowRunner(driver, workflow_repo, credential_repo)

   # Run workflow
   runner.run_workflow("login_workflow")
   ```

## Advanced Usage

### Creating Custom Actions

You can create custom actions by extending the `ActionBase` class:

```python
from src.core.action_base import ActionBase, ActionResult
from src.core.interfaces import IWebDriver
from typing import Dict, Any

class CustomAction(ActionBase):
    def __init__(self, name: str, custom_param: str):
        super().__init__(name)
        self.custom_param = custom_param
        
    def validate(self) -> bool:
        return bool(self.custom_param)
        
    def execute(self, driver: IWebDriver) -> ActionResult:
        try:
            # Custom action implementation
            print(f"Executing custom action with param: {self.custom_param}")
            return ActionResult.success(f"Custom action completed successfully")
        except Exception as e:
            return ActionResult.failure(f"Custom action failed: {str(e)}")
            
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CustomAction",
            "name": self.name,
            "custom_param": self.custom_param
        }
```

### Implementing Custom Web Drivers

You can implement custom web drivers by implementing the `IWebDriver` interface:

```python
from src.core.interfaces import IWebDriver
from typing import Any

class CustomWebDriver(IWebDriver):
    def __init__(self):
        # Initialize your custom web driver
        pass
        
    def get(self, url: str) -> None:
        # Navigate to the specified URL
        pass
        
    def quit(self) -> None:
        # Close the browser and release resources
        pass
        
    def find_element(self, selector: str) -> Any:
        # Find an element on the page
        pass
        
    def click_element(self, selector: str) -> None:
        # Click on an element
        pass
        
    def type_text(self, selector: str, text: str) -> None:
        # Type text into an element
        pass
        
    def take_screenshot(self, file_path: str) -> None:
        # Take a screenshot
        pass
        
    def is_element_present(self, selector: str) -> bool:
        # Check if an element is present
        pass
        
    def get_current_url(self) -> str:
        # Get the current URL
        pass
```

## API Reference

For detailed information about the API, see the following documentation:

- [Core Interfaces](interfaces.md)
- [Domain Entities](entities.md)
- [Custom Exceptions](exceptions.md)
