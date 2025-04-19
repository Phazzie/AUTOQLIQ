# AutoQliq Developer Guide

## Architecture Overview

AutoQliq follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Views    │  │  Presenters │  │     UI Factory      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────┼───────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Services   │  │  Executors  │  │    Factories        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────┼───────────────────────────────────┐
│                      Core Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Interfaces │  │   Models    │  │     Actions         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────┼───────────────────────────────────┐
│                  Infrastructure Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Repositories│  │ WebDrivers  │  │     Utilities       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layers

1. **UI Layer**: Handles user interaction using Tkinter
   - Views: UI components that display information and capture user input
   - Presenters: Coordinate between views and services
   - UI Factory: Creates UI components with consistent styling

2. **Application Layer**: Contains application logic
   - Services: Implement business logic and orchestrate operations
   - Executors: Handle specific execution flows
   - Factories: Create domain objects

3. **Core Layer**: Defines the domain model
   - Interfaces: Define contracts for components
   - Models: Represent domain entities
   - Actions: Encapsulate operations that can be performed

4. **Infrastructure Layer**: Provides technical capabilities
   - Repositories: Handle data persistence
   - WebDrivers: Interact with web browsers
   - Utilities: Provide common functionality

## Design Patterns

AutoQliq uses several design patterns:

1. **Model-View-Presenter (MVP)**: Separates UI from business logic
   - Model: Domain entities and business logic
   - View: UI components
   - Presenter: Mediates between Model and View

2. **Repository Pattern**: Abstracts data access
   - Provides a collection-like interface for domain objects
   - Hides data access implementation details

3. **Factory Pattern**: Creates objects
   - ActionFactory: Creates action objects
   - UIFactory: Creates UI components

4. **Strategy Pattern**: Defines a family of algorithms
   - Different WebDriver implementations
   - Different repository implementations

5. **Command Pattern**: Encapsulates actions as objects
   - Actions represent operations that can be performed
   - Actions can be composed and sequenced

## Key Components

### Core Components

#### Interfaces

The `src/core/interfaces.py` file defines the core interfaces:

- `IAction`: Represents an action that can be executed
- `IWebDriver`: Abstracts web browser interaction
- `IWorkflowRepository`: Manages workflow storage
- `ICredentialRepository`: Manages credential storage

#### Actions

Actions are the building blocks of workflows:

- `ActionBase`: Base class for all actions
- `NavigateAction`: Navigates to a URL
- `ClickAction`: Clicks on an element
- `TypeAction`: Types text into an element
- `WaitAction`: Pauses execution
- `ScreenshotAction`: Takes a screenshot
- `ConditionalAction`: Executes actions based on a condition
- `JavaScriptConditionAction`: Evaluates JavaScript expressions

### Application Components

#### Services

Services implement business logic:

- `WorkflowService`: Manages workflows
- `WebDriverService`: Creates and manages web drivers
- `CredentialService`: Manages credentials

#### Executors

Executors handle specific execution flows:

- `WorkflowExecutor`: Orchestrates workflow execution

### Infrastructure Components

#### Repositories

Repositories handle data persistence:

- `FileWorkflowRepository`: Stores workflows in files
- `FileCredentialRepository`: Stores credentials in files

#### WebDrivers

WebDrivers interact with web browsers:

- `SeleniumWebDriver`: Uses Selenium for browser automation

#### Utilities

Utilities provide common functionality:

- `error_handling.py`: Decorators for error handling
- `logging_utils.py`: Utilities for logging

### UI Components

#### Views

Views display information and capture user input:

- `MainView`: Main application window
- `WorkflowEditorView`: Edits workflows
- `WorkflowRunnerView`: Runs workflows
- `SettingsView`: Configures application settings

#### Presenters

Presenters coordinate between views and services:

- `EditorPresenter`: Manages workflow editing
- `RunnerPresenter`: Manages workflow execution
- `SettingsPresenter`: Manages application settings

## Workflow Execution

Workflow execution follows these steps:

1. User selects a workflow and clicks "Run"
2. `RunnerPresenter` calls `WorkflowService.run_workflow()`
3. `WorkflowService` creates a `WorkflowExecutor`
4. `WorkflowExecutor` loads the workflow and creates a `WebDriver`
5. `WorkflowExecutor` creates a `WorkflowRunner`
6. `WorkflowRunner` executes each action in sequence
7. Results are returned to the `RunnerPresenter`
8. `RunnerPresenter` updates the view with the results

## Error Handling

Error handling is implemented at multiple levels:

1. **UI Level**: Presenters catch exceptions and display error messages
2. **Service Level**: Services use error handling decorators
3. **Execution Level**: Executors catch and log exceptions
4. **Action Level**: Actions report errors through `ActionResult`

## Logging

Logging is implemented using Python's standard logging module:

1. **Application Logging**: General application events
2. **Execution Logging**: Detailed workflow execution events
3. **Error Logging**: Error events with stack traces

## Configuration

Configuration is managed through `config.ini` and the `Config` class:

1. **Repository Configuration**: Paths for workflows and credentials
2. **WebDriver Configuration**: Browser settings
3. **Logging Configuration**: Log levels and file paths
4. **Security Configuration**: Password hashing settings

## Testing

Testing is implemented using Python's unittest framework:

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **UI Tests**: Test UI components

## Adding New Features

### Adding a New Action Type

1. Create a new action class that inherits from `ActionBase`
2. Implement the required methods:
   - `__init__`: Initialize the action
   - `validate`: Validate action parameters
   - `execute`: Execute the action
3. Register the action in `ActionFactory`
4. Add the action to the UI in `ActionSelectionDialog` and `ActionEditorDialog`

### Adding a New Repository Type

1. Create a new repository class that implements the appropriate interface
2. Implement the required methods
3. Update the repository factory to create the new repository type

### Adding a New UI Component

1. Create a new view class
2. Create a new presenter class
3. Update the main view to include the new component

## Best Practices

1. **Follow SOLID Principles**:
   - Single Responsibility Principle
   - Open/Closed Principle
   - Liskov Substitution Principle
   - Interface Segregation Principle
   - Dependency Inversion Principle

2. **Use Dependency Injection**:
   - Pass dependencies through constructors
   - Avoid creating dependencies inside classes

3. **Write Clean Code**:
   - Use meaningful names
   - Keep methods small and focused
   - Follow consistent coding style

4. **Write Tests**:
   - Write unit tests for new components
   - Test edge cases and error conditions
   - Keep tests independent and repeatable

5. **Document Your Code**:
   - Add docstrings to classes and methods
   - Update documentation for new features
   - Include examples where appropriate
