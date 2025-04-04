# AUTOCLICK Application

## Overview

AUTOCLICK is a Python-based desktop application designed to automate web tasks using Selenium and Tkinter. The application follows SOLID, DRY, and YAGNI principles to ensure a robust and maintainable codebase. The core functionality is driven by external JSON configuration files for workflows and credentials.

## Project Structure

```
AUTOCLICK/
├── requirements.txt              # Lists Python package dependencies
├── README.md                     # Project documentation and usage instructions
├── credentials.json              # Stores user credentials (unencrypted)
├── workflows/                    # Directory to hold workflow definition files
│   └── example_workflow.json     # Example workflow definition based on core example
├── src/
│   ├── __init__.py               # Marks 'src' as a Python package
│   ├── core/
│   │   ├── __init__.py           # Marks 'core' as a Python package
│   │   ├── interfaces.py         # Defines core business logic interfaces (IWebDriver, IAction, Repositories)
│   │   ├── credentials.py        # Defines the Credential data structure (e.g., dataclass)
│   │   ├── exceptions.py         # Defines custom application exceptions (LoginFailedError etc.)
│   │   ├── actions.py            # Implements concrete Action classes and the ActionFactory
│   │   └── workflow.py           # Implements the WorkflowRunner for orchestrating actions
│   ├── infrastructure/
│   │   ├── __init__.py           # Marks 'infrastructure' as a Python package
│   │   ├── webdrivers.py         # Implements IWebDriver using Selenium
│   │   └── persistence.py        # Implements Repository interfaces for file system (Credentials & Workflows)
│   ├── application/              # Optional layer for application services (leave empty initially)
│   │   └── __init__.py           # Marks 'application' as a Python package
│   ├── ui/
│   │   ├── __init__.py           # Marks 'ui' as a Python package
│   │   ├── editor_view.py        # Implements the Tkinter View for the workflow editor
│   │   ├── editor_presenter.py   # Implements the Presenter logic for the workflow editor
│   │   ├── runner_view.py        # Implements the Tkinter View for the workflow runner
│   │   └── runner_presenter.py   # Implements the Presenter logic for the workflow runner
│   └── main_ui.py                # Main application entry point, dependency injection, starts UI loop
└── tests/
    ├── __init__.py               # Marks 'tests' as a Python package
    ├── unit/
    │   ├── __init__.py           # Marks 'unit' tests subpackage
    │   ├── core/
    │   │   ├── __init__.py       # Marks 'core' unit tests subpackage
    │   │   ├── test_actions.py   # Unit tests for Action classes and Factory
    │   │   └── test_workflow.py  # Unit tests for WorkflowRunner
    │   ├── infrastructure/
    │   │   ├── __init__.py       # Marks 'infrastructure' unit tests subpackage
    │   │   └── test_persistence.py # Unit tests for Repository implementations
    │   ├── ui/
    │   │   ├── __init__.py       # Marks 'ui' unit tests subpackage
    │   │   ├── test_editor_presenter.py # Unit tests for editor presenter logic
    │   │   └── test_runner_presenter.py # Unit tests for runner presenter logic
    └── integration/              # Integration tests (leave empty initially)
        └── __init__.py           # Marks 'integration' tests subpackage
```

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/githubnext/workspace-blank.git
   cd workspace-blank
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your `credentials.json` file in the root directory with the following format:
   ```json
   [
     { "name": "example_login", "username": "user@example.com", "password": "password123" }
   ]
   ```

2. Create your workflow JSON files in the `workflows/` directory. Example:
   ```json
   [
     { "type": "Navigate", "url": "https://login.example.com" },
     { "type": "Type", "selector": "#username-input", "value_type": "credential", "value_key": "example_login.username" },
     { "type": "Click", "selector": "#login-button", "check_success_selector": "#dashboard-title", "check_failure_selector": "#login-error-message" },
     { "type": "Wait", "duration_seconds": 3 },
     { "type": "Screenshot", "file_path": "report_screenshot.png" }
   ]
   ```

3. Run the application:
   ```sh
   python src/main_ui.py
   ```

## Testing

1. Run unit tests:
   ```sh
   pytest tests/unit
   ```

2. Run integration tests:
   ```sh
   pytest tests/integration
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
