# AutoQliq Files Explained

## Core Interfaces

1. **src/core/interfaces/action.py** - Defines the `IAction` interface that all automation actions must implement, establishing the contract for executable steps in workflows.

2. **src/core/interfaces/repository.py** - Contains repository interfaces for data persistence, defining how workflows, credentials, and templates are stored and retrieved.

3. **src/core/interfaces/webdriver.py** - Defines the `IWebDriver` interface that abstracts browser automation capabilities, allowing for different implementations.

4. **src/core/interfaces/service.py** - Provides service interfaces for the application layer, defining how services orchestrate domain operations.

## Core Actions

5. **src/core/actions/base.py** - Implements `ActionBase`, the foundation class for all actions with common functionality and parameter validation.

6. **src/core/actions/factory.py** - Contains the `ActionFactory` that creates appropriate action instances based on action type and parameters.

7. **src/core/actions/conditional_action.py** - Implements conditional branching in workflows, allowing for if/else logic based on evaluated conditions.

8. **src/core/actions/loop_action.py** - Provides looping capability for workflows, enabling repeated execution of child actions.

9. **src/core/actions/error_handling_action.py** - Implements try/catch functionality for workflows, allowing for graceful error recovery.

10. **src/core/actions/template_action.py** - Enables reuse of action sequences by referencing saved templates within workflows.

## Core Workflow

11. **src/core/workflow/runner.py** - Contains the `WorkflowRunner` that executes sequences of actions, managing the execution flow and results.

## Core Utilities

12. **src/core/exceptions.py** - Defines custom exception classes for the application, providing structured error handling.

13. **src/core/action_result.py** - Implements the `ActionResult` class that encapsulates the outcome of action execution.

## Application Services

14. **src/application/services/credential_service.py** - Manages secure storage and retrieval of credentials with password hashing.

15. **src/application/services/workflow_service.py** - Orchestrates workflow operations, bridging UI and repositories.

16. **src/application/services/webdriver_service.py** - Manages WebDriver lifecycle and operations, using the factory pattern.

17. **src/application/services/scheduler_service.py** - Handles scheduling of workflow execution (may be a stub implementation).

18. **src/application/services/reporting_service.py** - Generates reports on workflow execution with logging capabilities.

## Infrastructure Common

19. **src/infrastructure/common/error_handling.py** - Provides decorators and utilities for consistent error handling across the application.

20. **src/infrastructure/common/logging_utils.py** - Contains logging decorators and utilities for consistent logging throughout the application.

## Infrastructure Repositories

21. **src/infrastructure/repositories/base/database_repository.py** - Base implementation for database-backed repositories using SQLite.

22. **src/infrastructure/repositories/base/file_system_repository.py** - Base implementation for file system-backed repositories using JSON files.

## Infrastructure WebDrivers

23. **src/infrastructure/webdrivers/selenium_driver.py** - Concrete implementation of the `IWebDriver` interface using Selenium WebDriver.

## UI Interfaces

24. **src/ui/interfaces/presenter.py** - Defines the `IPresenter` interface for the MVP pattern, establishing the contract for presenters.

25. **src/ui/interfaces/view.py** - Defines the `IView` interface for the MVP pattern, establishing the contract for views.

## UI Presenters

26. **src/ui/presenters/base_presenter.py** - Provides a base implementation for all presenters with common functionality.

27. **src/ui/presenters/settings_presenter.py** - Implements the presenter for the settings view, handling configuration management.

28. **src/ui/presenters/workflow_editor_presenter.py** - Implements the presenter for the workflow editor view, handling workflow editing operations.

## UI Views

29. **src/ui/views/base_view.py** - Provides a base implementation for all views with common UI functionality.

30. **src/ui/views/settings_view.py** - Implements the settings view for configuring application settings.

## UI Common

31. **src/ui/common/ui_factory.py** - Factory for creating UI components, ensuring proper dependency injection.

32. **src/ui/common/status_bar.py** - Implements a reusable status bar component used by views to display status information.

## UI Dialogs

33. **src/ui/dialogs/action_editor_dialog.py** - Implements a dialog for creating and editing actions within workflows.

34. **src/ui/dialogs/credential_manager_dialog.py** - Implements a dialog for managing credentials securely.

## Configuration

35. **src/config.py** - Manages application configuration, loading settings from config.ini.

36. **config.ini** - Contains application configuration settings in INI format.

## Main Application

37. **src/main_ui.py** - Main entry point for the application, initializing components and starting the UI.

## Documentation

38. **README.md** - Project documentation with overview, installation instructions, and usage guidelines.
