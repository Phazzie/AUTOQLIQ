################################################################################

# AutoQliq Application

## Overview

AutoQliq is a Python-based desktop application designed to automate web tasks using Selenium and Tkinter. The application follows SOLID, DRY, and KISS principles with an MVP (Model-View-Presenter) architecture for the UI and a layered approach for backend components. The core functionality allows users to create, edit, save, and run automated web workflows. Workflows are stored as JSON files in the file system. Basic control flow (conditionals) is supported.

## Project Structure

```
AutoQliq/
├── requirements.txt              # Python package dependencies
├── config.ini                    # Application configuration settings
├── README.md                     # This file
├── credentials.json              # Credential file
├── workflows/                    # Workflow directory
│   └── example_workflow.json     # Example workflow definition
├── logs/                         # Directory where execution logs are saved
├── exports/                      # Directory where context exports are saved
├── test_data/                    # Directory for test data and samples
├── archive/                      # Directory for archived content

├── src/
│   ├── __init__.py
│   ├── config.py                 # Loads and provides config.ini settings
│   ├── core/                     # Core domain logic and interfaces
│   │   ├── interfaces/           # Core interfaces (Action, Repository, WebDriver, Service)
│   │   ├── actions/              # Concrete Action implementations (incl. Conditional)
│   │   ├── workflow/             # Workflow execution logic (Runner)
│   │   ├── exceptions.py         # Custom application exceptions
│   │   └── action_result.py      # ActionResult class
│   ├── infrastructure/           # Implementation of external concerns
│   │   ├── common/               # Shared utilities
│   │   ├── repositories/         # Persistence implementations (File System for Workflows, Credentials)
│   │   └── webdrivers/           # WebDriver implementations (Selenium)
│   ├── application/              # Application service layer
│   │   ├── services/             # Service implementations (Credential, Workflow, WebDriver, Scheduler[stub], Reporting[basic])
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

- `[Repository] paths`: Set `workflows_path` and `credentials_path` for file storage locations.
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
2.  **Manage Credentials**: Use the "Manage" -> "Credentials..." menu item. Passwords are hashed on save.
3.  **Manage Workflows**: Use the "Workflow Editor" tab.
    - Create/Edit/Delete workflows with basic and conditional actions.
    - Build sequences of actions to automate web tasks.
4.  **Run Workflows**: Use the "Workflow Runner" tab. Select workflow/credential, click "Run". Execution is backgrounded; logs appear. Use "Stop" to request cancellation.
5.  **Manage Settings**: Use the "Settings" tab to view/modify configuration. Click "Save Settings" to persist changes.
6.  **Execution Logs**: Execution logs are saved in the `logs/` directory.

## Workflow Action Types

Workflows are lists of action dictionaries. Supported `type` values:

- `Navigate`: Goes to a URL (`url`).
- `Click`: Clicks an element (`selector`).
- `Type`: Types text (`value_key`) based on `value_type` ('text' or 'credential') into an element (`selector`).
- `Wait`: Pauses execution (`duration_seconds`).
- `Screenshot`: Takes a screenshot (`file_path`).
- `Conditional`: Executes actions based on a condition.
  - `condition_type`: 'element_present', 'element_not_present', 'variable_equals'.
  - Requires parameters like `selector`, `variable_name`, `expected_value` based on `condition_type`.
  - `true_branch`: List of actions if condition is true.
  - `false_branch`: List of actions if condition is false.

_(See `ActionEditorDialog` or action class docstrings for specific parameters)_

## Testing

- **Unit Tests:** `pytest tests/unit`
- **Integration Tests:** `pytest tests/integration` (Requires WebDriver setup, uses in-memory DB)

## Contributing

Contributions welcome!

## License

MIT License.
################################################################################
