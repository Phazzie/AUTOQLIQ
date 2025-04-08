################################################################################
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

-   `[Repository] type`: `file_system` or `database`.
-   `[Repository] paths`: Set `workflows_path`, `credentials_path`, `db_path` as needed for the chosen type. Templates use a `templates` subdir relative to `workflows_path` (FS) or a `templates` table (DB).
-   `[WebDriver] default_browser`: `chrome`, `firefox`, `edge`, `safari`.
-   `[WebDriver] *_driver_path`: Optional explicit paths to WebDriver executables.
-   `[WebDriver] implicit_wait`: Default implicit wait time (seconds).
-   `[Security]`: Configure password hashing method and salt length (requires `werkzeug`).

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
    *   Create/Edit/Delete workflows.
    *   Save reusable sequences as templates (currently requires manual file/DB operation - UI needed).
    *   Use the `TemplateAction` type in the Action Editor to reference a saved template by name.
4.  **Run Workflows**: Use the "Workflow Runner" tab. Select workflow/credential, click "Run". Execution is backgrounded; logs appear. Use "Stop" to request cancellation.
5.  **Manage Settings**: Use the "Settings" tab to view/modify configuration. Click "Save Settings" to persist changes.
6.  **Execution Logs**: Basic execution logs (status, duration, results) are saved as JSON files in the `logs/` directory.

## Workflow Action Types

Workflows are lists of action dictionaries. Supported `type` values:

*   `Navigate`: Goes to a URL (`url`).
*   `Click`: Clicks an element (`selector`).
*   `Type`: Types text (`value_key`) based on `value_type` ('text' or 'credential') into an element (`selector`).
*   `Wait`: Pauses execution (`duration_seconds`).
*   `Screenshot`: Takes a screenshot (`file_path`).
*   `Conditional`: Executes actions based on a condition.
    *   `condition_type`: 'element_present', 'element_not_present', 'variable_equals', 'javascript_eval'.
    *   Requires parameters like `selector`, `variable_name`, `expected_value`, `script` based on `condition_type`.
    *   `true_branch`: List of actions if condition is true.
    *   `false_branch`: List of actions if condition is false.
*   `Loop`: Repeats actions.
    *   `loop_type`: 'count', 'for_each', 'while'.
    *   Requires parameters like `count`, `list_variable_name`, or condition parameters based on `loop_type`.
    *   `loop_actions`: List of actions to repeat. Context variables `loop_index`, `loop_iteration`, `loop_total`, `loop_item` are available to nested actions.
*   `ErrorHandling`: Executes 'try' actions, runs 'catch' actions on failure.
    *   `try_actions`: List of actions to attempt.
    *   `catch_actions`: List of actions to run if try block fails. Context variables `try_block_error_message`, `try_block_error_type` available in catch.
*   `Template`: Executes a saved template.
    *   `template_name`: The name of the saved template to execute.

*(See `ActionEditorDialog` or action class docstrings for specific parameters)*

## Testing

-   **Unit Tests:** `pytest tests/unit`
-   **Integration Tests:** `pytest tests/integration` (Requires WebDriver setup, uses in-memory DB)

## Contributing

Contributions welcome!

## License

MIT License.
################################################################################