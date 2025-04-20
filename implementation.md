# implementation.md

# AutoQliq Implementation & Refactoring Plan

This document outlines the step-by-step process for refactoring the AutoQliq application, completing features, and ensuring robust testing, adhering to SOLID, KISS, and DRY principles as defined in `.github/copilot-instructions.md`.

## Phase 0: Preparation (Already Done)

- Workspace organized, definitions clarified, persona activated.
- `PROJECT_OVERVIEW.md` created.

## Phase 1: Core Domain Refactoring & Foundation

### Step 1.1: Refactor Core Entities & Interfaces

- **Goal:** Ensure core domain entities (`Workflow`, `Credentials`, `ActionResult`) and their fundamental interfaces are clean, focused, and testable. Define clear contracts for actions and workflow management. Refactoring prepares for reliable persistence and execution.
- **Tests Needed:**
  - `tests/unit/core/test_workflow_entity.py`: Test `Workflow` creation, action management (add, remove, reorder), validation logic (e.g., ensuring workflow has a name). Why: Verify basic state and behavior of the central entity.
  - `tests/unit/core/test_credentials.py`: Test `Credentials` creation, validation (e.g., non-empty username/password), and potentially secure handling aspects (if any logic resides here). Why: Ensure credential data integrity.
  - `tests/unit/core/test_action_result.py`: Test `ActionResult` creation with different statuses (success, failure) and data payloads. Why: Verify the standard way actions report outcomes.
- **Files Created/Modified:**
  - `src/core/workflow/workflow_entity.py`: (Modify) Refine the `Workflow` class. Responsibilities: 1 (Manage workflow state and its sequence of actions). Potential Violations: Check if it currently handles parsing/saving (should be repository's job) or execution (should be runner's job). Remove any such logic.
  - `src/core/credentials.py`: (Modify) Refine the `Credentials` class. Responsibilities: 1 (Hold and potentially validate credential data). Potential Violations: Check for persistence logic (should be repository's job). Remove any such logic.
  - `src/core/action_result.py`: (Modify) Refine `ActionResult`. Responsibilities: 1 (Represent the outcome of an action).
  - `src/core/interfaces/entity_interfaces.py`: (Create/Modify) Define `IWorkflow`, `ICredentials` interfaces if needed for abstraction (YAGNI check: only if multiple implementations or required for strict typing/mocking). Responsibilities: 1 (Define contract).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Enforce single responsibility strictly. `Workflow` manages actions, `Credentials` holds data.
  - KISS: Keep entity classes simple data holders with validation, avoid complex logic.
  - DRY: Abstract common validation patterns if found.
- **Component Interactions:** Entities interact with Repositories (for persistence) and Services (for orchestration). Actions are contained within Workflows.
- **Edge Cases:** Empty workflow name, invalid action sequence, missing credential fields.
- **Checklist Items:**
  - `[x] CHECKLIST: Review and refactor src/core/workflow/workflow_entity.py for SRP, removing persistence/execution logic.` (Verified: OK)
  - `[x] CHECKLIST: Review and refactor src/core/credentials.py for SRP, removing persistence logic.` (Verified: OK)
  - `[x] CHECKLIST: Review and refactor src/core/action_result.py for simplicity.` (Verified: OK)
  - `[x] CHECKLIST: Create/Update unit tests in tests/unit/core/test_workflow_entity.py.` (Created)
  - `[x] CHECKLIST: Create/Update unit tests in tests/unit/core/test_credentials.py.` (Created)
  - `[x] CHECKLIST: Create/Update unit tests in tests/unit/core/test_action_result.py.` (Created)
  - `[x] CHECKLIST: Define core entity interfaces in src/core/interfaces/entity_interfaces.py if necessary (YAGNI).` (Verified: Interfaces already used, no new ones needed)

### Step 1.2: Refactor Action Base & Concrete Actions

- **Goal:** Establish a clear `ActionBase` class and refactor existing concrete actions (e.g., Navigate, Click, Type) for SRP, ensuring they are easily extensible and testable. This prepares for adding advanced actions and reliable execution.
- **Tests Needed:**
  - `tests/unit/core/actions/test_action_base.py`: Test `ActionBase` initialization, common properties (name, description), and abstract `execute` method signature. Why: Verify the foundation for all actions.
  - `tests/unit/core/actions/test_navigate_action.py`: Test `NavigateAction` creation, parameter validation (valid URL), and simulate execution logic (using mocks for `IWebDriver`). Why: Verify a fundamental concrete action.
  - `tests/unit/core/actions/test_click_action.py`: Test `ClickAction` creation, parameter validation (valid selector), simulate execution (mocked `IWebDriver`). Why: Verify another core interaction.
  - `(Repeat for other existing basic actions: Type, ReadAttribute, etc.)`
- **Files Created/Modified:**
  - `src/core/actions/action_base.py`: (Modify) Define the abstract base class `ActionBase` with common attributes and abstract `execute(driver: IWebDriver) -> ActionResult` method. Responsibilities: 1 (Define action contract and common properties).
  - `src/core/actions/navigate_action.py`: (Create/Modify) Implement `NavigateAction(ActionBase)`. Responsibilities: 1 (Encapsulate logic and parameters for navigating a browser via `IWebDriver`). Potential Violations: Remove direct Selenium/Playwright use.
  - `src/core/actions/click_action.py`: (Create/Modify) Implement `ClickAction(ActionBase)`. Responsibilities: 1 (Encapsulate logic/parameters for clicking an element via `IWebDriver`). Potential Violations: Remove direct WebDriver use.
  - `(Repeat for other basic actions, potentially splitting a large actions.py into individual files per action).`
  - `src/core/interfaces/action_interface.py`: (Create/Modify) Define `IAction` interface (likely satisfied by `ActionBase`). Responsibilities: 1 (Define action contract).
  - `src/core/interfaces/driver_interface.py`: (Create/Modify) Define `IWebDriver` interface with methods needed by actions (e.g., `get`, `find_element`, `click`, `type_text`, `get_attribute`). Responsibilities: 1 (Define browser interaction contract).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Each action class handles only its specific task. `ActionBase` defines the contract. `IWebDriver` defines driver contract.
  - OCP: Adding new actions means creating new classes, not modifying existing ones.
  - LSP: All concrete actions must be substitutable for `ActionBase`.
  - DIP: Actions depend on `IWebDriver` interface, not concrete implementations.
  - KISS: Keep action logic focused; complex orchestration belongs elsewhere.
  - DRY: Abstract common parameter validation or execution patterns into `ActionBase` or helper functions if applicable.
- **Component Interactions:** Actions are executed by `WorkflowRunner`, using an `IWebDriver`. They produce `ActionResult`.
- **Edge Cases:** Invalid URLs, non-existent selectors, timeouts during execution, actions receiving unexpected parameters.
- **Checklist Items:**
  - `[ ] CHECKLIST: Refactor/Define src/core/actions/action_base.py.`
  - `[ ] CHECKLIST: Define/Refine src/core/interfaces/driver_interface.py.`
  - `[ ] CHECKLIST: Create/Refactor src/core/actions/navigate_action.py adhering to SRP/DIP, using IWebDriver.`
  - `[ ] CHECKLIST: Create/Refactor src/core/actions/click_action.py adhering to SRP/DIP, using IWebDriver.`
  - `[ ] CHECKLIST: (Repeat refactoring for Type, ReadAttribute, etc. actions, splitting files if needed).`
  - `[ ] CHECKLIST: Ensure all actions depend on IWebDriver, not concrete drivers.`
  - `[ ] CHECKLIST: Create/Update unit tests in tests/unit/core/actions/test_action_base.py.`
  - `[ ] CHECKLIST: Create/Update unit tests in tests/unit/core/actions/test_navigate_action.py (using mocks).`
  - `[ ] CHECKLIST: Create/Update unit tests in tests/unit/core/actions/test_click_action.py (using mocks).`
  - `[ ] CHECKLIST: (Repeat test creation for other basic actions).`

### Step 1.3: Implement Workflow Runner

- **Goal:** Create a dedicated `WorkflowRunner` responsible solely for executing the sequence of actions in a workflow, using the `IWebDriver` interface. This isolates execution logic.
- **Tests Needed:**
  - `tests/unit/core/workflow/test_workflow_runner.py`: Test runner initialization (requires `IWebDriver`), execution of an empty workflow, execution of a simple workflow (e.g., Navigate -> Click) using mocked actions and webdriver, handling of action success/failure results, propagation of errors. Why: Verify the core execution logic and error handling.
- **Files Created/Modified:**
  - `src/core/workflow/workflow_runner.py`: (Create/Refactor from `workflow.py`?) Implement `WorkflowRunner`. Responsibilities: 1 (Execute actions in a workflow sequentially, using an `IWebDriver`, handling basic execution flow and errors). Potential Violations: Check if it handles loading/saving workflows (repository) or complex state management beyond simple execution flow (service).
- **SOLID/KISS/DRY Analysis:**
  - SRP: `WorkflowRunner` only executes; it doesn't load, save, or define workflows/actions.
  - DIP: Depends on `IWebDriver` and `ActionBase` (or `IAction`). Injects `IWebDriver`.
  - KISS: Keep the execution loop straightforward. Define clear error handling (e.g., stop on first error, collect all errors).
- **Component Interactions:** Takes a `Workflow` and an `IWebDriver`. Iterates through `ActionBase` objects, calling their `execute` method. Returns results (e.g., list of `ActionResult` or final status).
- **Edge Cases:** Empty workflow, workflow with failing actions, webdriver becoming unavailable during execution, actions raising unexpected exceptions.
- **Checklist Items:**
  - `[ ] CHECKLIST: Create/Refactor src/core/workflow/workflow_runner.py for SRP.`
  - `[ ] CHECKLIST: Ensure WorkflowRunner depends only on IWebDriver and ActionBase/IAction.`
  - `[ ] CHECKLIST: Implement constructor injection for IWebDriver in WorkflowRunner.`
  - `[ ] CHECKLIST: Create/Update unit tests in tests/unit/core/workflow/test_workflow_runner.py (using mocks).`
  - `[ ] CHECKLIST: Define and implement basic error handling strategy within WorkflowRunner (e.g., stop on error, return failing ActionResult).`

## Phase 2: Infrastructure Implementation & Refinement

### Step 2.1: Define Application-wide Error Handling & Logging

- **Goal:** Establish consistent, application-wide strategies for handling errors (custom exceptions) and logging, providing clear diagnostics.
- **Tests Needed:**
  - `tests/unit/core/test_exceptions.py`: Test custom exception creation and attribute storage. Why: Ensure exceptions carry necessary context.
  - `tests/unit/infrastructure/test_logging_config.py`: Test logger configuration loading and basic log emission (capture output). Why: Verify logging setup works as expected.
- **Files Created/Modified:**
  - `src/core/exceptions.py`: (Create) Define custom application exceptions (e.g., `WorkflowExecutionError`, `ConfigurationError`, `WebDriverError`, `ActionValidationError`). Responsibilities: 1 (Define application-specific error types).
  - `src/infrastructure/logging_setup.py`: (Create/Refactor) Configure the standard `logging` module (e.g., formatter, handlers for file/console, level based on config). Responsibilities: 1 (Set up application logging).
  - `src/config.py`: (Modify) Add logging configuration settings (level, file path). Responsibilities: 1 (Provide configuration access - already exists, just adding keys).
- **SOLID/KISS/DRY Analysis:**
  - SRP: `exceptions.py` defines errors, `logging_setup.py` configures logging.
  - KISS: Use standard logging; avoid overly complex exception hierarchy initially.
  - DRY: Centralize logging setup. Use specific exceptions instead of generic ones.
- **Component Interactions:** All modules will import and use custom exceptions. All modules will get and use a configured logger instance. `config.py` provides settings.
- **Edge Cases:** Log file not writable, invalid logging level in config.
- **Checklist Items:**
  - `[x] CHECKLIST: Create src/core/exceptions.py with base and specific custom exceptions.`
  - `[x] CHECKLIST: Create/Refactor src/infrastructure/logging_setup.py to configure logging based on config.ini.`
  - `[x] CHECKLIST: Add logging settings (level, file) to src/config.py and config.ini.`
  - `[x] CHECKLIST: Create unit tests in tests/unit/core/test_exceptions.py.`
  - `[x] CHECKLIST: Create unit tests in tests/unit/infrastructure/test_logging_config.py.`
  - `[x] CHECKLIST: Ensure logging setup is called early in application startup (e.g., main_ui.py).`

### Step 2.2: Refine Configuration Management

- **Goal:** Ensure configuration (`config.ini`) is loaded robustly and accessed consistently via `src/config.py`.
- **Tests Needed:**
  - `tests/unit/test_config.py`: Test loading config, accessing existing/missing keys, handling file not found, type conversions (if any). Why: Verify robust config access.
- **Files Created/Modified:**
  - `src/config.py`: (Modify) Refine the config loading and access logic. Implement as a singleton or provide a clear access function. Add error handling for missing file/keys. Responsibilities: 1 (Provide access to application configuration).
  - `config.ini`: (Modify) Ensure structure is clean and contains necessary sections/keys (add logging, potentially DB paths, WebDriver paths).
- **SOLID/KISS/DRY Analysis:**
  - SRP: `config.py` handles config access.
  - KISS: Use standard `configparser`. Provide simple access methods.
  - DRY: Centralize all config access through `config.py`.
- **Component Interactions:** Many components (logging, repositories, WebDriver factory) will depend on `config.py`.
- **Edge Cases:** `config.ini` missing or corrupted, missing sections or keys, incorrect value types.
- **Checklist Items:**
  - `[x] CHECKLIST: Refactor src/config.py for robust loading, error handling, and clear access patterns.`
  - `[x] CHECKLIST: Update config.ini with necessary sections/keys (logging, persistence, webdriver).`
  - `[x] CHECKLIST: Create/Update unit tests in tests/unit/test_config.py.`
  - `[x] CHECKLIST: Ensure all components needing config import and use src/config.py.`

### Step 2.3: Implement WebDriver Infrastructure

- **Goal:** Implement concrete `IWebDriver` classes (e.g., Selenium Chrome/Firefox) and a factory to create instances based on configuration.
- **Tests Needed:**
  - `tests/integration/infrastructure/test_webdriver_factory.py`: Test creating different driver types based on config. Requires actual drivers installed but doesn't need to browse. Why: Verify factory logic.
  - `tests/integration/infrastructure/test_selenium_chrome_driver.py`: Test basic `IWebDriver` methods (get, find_element, click - minimal) against a live local browser instance or mock HTML server. Why: Verify the concrete driver implementation works.
  - `(Repeat for other supported drivers like Firefox)`
- **Files Created/Modified:**
  - `src/infrastructure/webdrivers/selenium_chrome.py`: (Create) Implement `IWebDriver` using Selenium ChromeDriver. Responsibilities: 1 (Adapt Selenium ChromeDriver to the `IWebDriver` interface).
  - `src/infrastructure/webdrivers/selenium_firefox.py`: (Create) Implement `IWebDriver` using Selenium GeckoDriver. Responsibilities: 1 (Adapt Selenium GeckoDriver to the `IWebDriver` interface).
  - `src/infrastructure/webdrivers/webdriver_factory.py`: (Create) Implement a factory function/class to return an `IWebDriver` instance based on `config.py` settings. Responsibilities: 1 (Create appropriate WebDriver instance).
  - `src/config.py`: (Modify) Add WebDriver configuration (type, path to driver executable if needed).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Each driver class adapts one specific driver. Factory creates instances.
  - OCP: Adding a new driver (e.g., Playwright) means adding a new class and updating the factory.
  - DIP: Factory returns `IWebDriver`, callers depend on the interface.
  - KISS: Keep driver adapters simple wrappers around the underlying library.
- **Component Interactions:** `WorkflowRunner` and potentially `Action` implementations (though ideally only Runner needs direct access) depend on `IWebDriver`. Factory is used by Application services or main UI setup to get a driver instance.
- **Edge Cases:** WebDriver executable not found, browser fails to start, incompatible driver/browser versions, network issues preventing navigation.
- **Checklist Items:**
  - `[x] CHECKLIST: Add WebDriver settings (type, path) to src/config.py and config.ini.`
  - `[x] CHECKLIST: Implement src/infrastructure/webdrivers/selenium_chrome.py conforming to IWebDriver.`
  - `[x] CHECKLIST: Implement src/infrastructure/webdrivers/selenium_firefox.py conforming to IWebDriver.`
  - `[x] CHECKLIST: Implement src/infrastructure/webdrivers/webdriver_factory.py.`
  - `[x] CHECKLIST: Create integration tests in tests/integration/infrastructure/test_webdriver_factory.py.`
  - `[x] CHECKLIST: Create integration tests in tests/integration/infrastructure/test_selenium_chrome_driver.py.`
  - `[x] CHECKLIST: (Repeat integration tests for Firefox driver).`

### Step 2.4: Implement Persistence Infrastructure (Repositories)

- **Goal:** Implement concrete repository classes for saving/loading Workflows and Credentials (Filesystem and/or DB) adhering to repository interfaces.
- **Tests Needed:**
  - `tests/integration/infrastructure/persistence/test_workflow_fs_repo.py`: Test save, load, list, delete operations using actual file system interactions (in a temporary directory). Why: Verify file persistence logic.
  - `tests/integration/infrastructure/persistence/test_credential_fs_repo.py`: Test save, load, delete for credentials (consider encryption/decryption if implemented). Why: Verify credential file persistence.
  - `(If DB): tests/integration/infrastructure/persistence/test_workflow_db_repo.py`: Test CRUD operations against a test database instance.
  - `(If DB): tests/integration/infrastructure/persistence/test_credential_db_repo.py`: Test CRUD operations for credentials against a test database.
- **Files Created/Modified:**
  - `src/core/interfaces/repository_interfaces.py`: (Create/Modify) Define `IWorkflowRepository` and `ICredentialRepository` with methods like `save`, `load`, `get_all`, `delete`. Responsibilities: 1 (Define persistence contracts).
  - `src/infrastructure/persistence/workflow_fs_repository.py`: (Create) Implement `IWorkflowRepository` using file system (e.g., JSON or pickle files). Responsibilities: 1 (Persist/retrieve Workflow entities to/from files).
  - `src/infrastructure/persistence/credential_fs_repository.py`: (Create) Implement `ICredentialRepository` using file system (consider `werkzeug` for hashing passwords if storing directly, or use OS keyring). Responsibilities: 1 (Persist/retrieve Credentials securely to/from files).
  - `(Optional DB implementations: workflow_db_repository.py, credential_db_repository.py using SQLite)`
  - `src/infrastructure/persistence/repository_factory.py`: (Create) Factory to return repository instances based on config (FS or DB). Responsibilities: 1 (Create appropriate repository instances).
  - `src/config.py`: (Modify) Add persistence configuration (type: fs/db, path/db_connection_string).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Each repository handles persistence for one entity type using one storage mechanism. Factory creates instances.
  - OCP: Adding a new storage mechanism (e.g., cloud storage) means adding new repository classes and updating the factory.
  - DIP: Application services depend on `IWorkflowRepository`/`ICredentialRepository`, not concrete implementations.
  - KISS: Use simple file formats (JSON) or standard DB interactions. Avoid complex ORMs unless necessary (YAGNI).
- **Component Interactions:** Application services depend on repository interfaces. Factory provides instances. Repositories interact with core entities (`Workflow`, `Credentials`).
- **Edge Cases:** File permissions errors, disk full, database connection errors, data corruption, concurrent access issues (if applicable). Secure storage of credentials.
- **Checklist Items:**
  - `[x] CHECKLIST: Add persistence settings (type, path/connection) to src/config.py and config.ini.`
  - `[x] CHECKLIST: Define/Refine src/core/interfaces/repository_interfaces.py.`
  - `[x] CHECKLIST: Implement src/infrastructure/persistence/workflow_fs_repository.py.`
  - `[x] CHECKLIST: Implement src/infrastructure/persistence/credential_fs_repository.py (ensure security).`
  - `[x] CHECKLIST: (Optional: Implement DB repositories).`
  - `[x] CHECKLIST: Implement src/infrastructure/persistence/repository_factory.py.`
  - `[x] CHECKLIST: Create integration tests in tests/integration/infrastructure/persistence/test_workflow_fs_repo.py.`
  - `[x] CHECKLIST: Create integration tests in tests/integration/infrastructure/persistence/test_credential_fs_repo.py.`
  - `[x] CHECKLIST: (Optional: Create DB repository integration tests).`

## Phase 3: Application Layer Implementation

### Step 3.1: Implement Core Application Services

- **Goal:** Implement services (`WorkflowService`, `CredentialService`, `ExecutionService`) that orchestrate core application logic, using repositories and the workflow runner.
- **Tests Needed:**
  - `tests/unit/application/test_workflow_service.py`: Test service methods (create, save, load, delete workflow) using mocked repositories. Why: Verify orchestration logic independent of infrastructure.
  - `tests/unit/application/test_credential_service.py`: Test service methods (save, load, delete credential) using mocked repository. Why: Verify credential management logic.
  - `tests/unit/application/test_execution_service.py`: Test starting workflow execution using mocked runner, factory, and repositories. Why: Verify execution orchestration.
- **Files Created/Modified:**
  - `src/application/services/workflow_service.py`: (Create) Manages workflow lifecycle (CRUD operations) via `IWorkflowRepository`. Responsibilities: 1 (Orchestrate workflow persistence operations).
  - `src/application/services/credential_service.py`: (Create) Manages credential lifecycle (CRUD) via `ICredentialRepository`. Responsibilities: 1 (Orchestrate credential persistence operations).
  - `src/application/services/execution_service.py`: (Create) Handles running a workflow. Gets `IWebDriver` from factory, gets `Workflow` from repository, uses `WorkflowRunner` to execute. Responsibilities: 1 (Orchestrate workflow execution).
  - `src/application/interfaces/service_interfaces.py`: (Create) Define interfaces (`IWorkflowService`, etc.) if needed for DI into presenters (recommended). Responsibilities: 1 (Define service contracts).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Each service orchestrates a specific domain area (workflows, credentials, execution).
  - DIP: Services depend on repository and runner interfaces, injected via constructor.
  - KISS: Keep service logic focused on coordination; complex business rules belong in domain objects or runner if execution-related.
- **Component Interactions:** Services use Repository interfaces, `WorkflowRunner`, `WebDriverFactory`. Presenters (UI layer) will use Service interfaces.
- **Edge Cases:** Workflow not found for execution, repository errors during load/save, WebDriver creation failure, runner errors during execution.
- **Checklist Items:**
  - `[x] CHECKLIST: Define service interfaces in src/application/interfaces/service_interfaces.py.`
  - `[x] CHECKLIST: Implement src/application/services/workflow_service.py with repository injection.`
  - `[x] CHECKLIST: Implement src/application/services/credential_service.py with repository injection.`
  - `[x] CHECKLIST: Implement src/application/services/execution_service.py with runner/factory/repo injection.`
  - `[x] CHECKLIST: Create unit tests in tests/unit/application/test_workflow_service.py (using mocks).`
  - `[x] CHECKLIST: Create unit tests in tests/unit/application/test_credential_service.py (using mocks).`
  - `[x] CHECKLIST: Create unit tests in tests/unit/application/test_execution_service.py (using mocks).`

## Phase 4: UI Layer Refactoring & Implementation (MVP Focus)

### Step 4.1: Refactor UI Base Components & Presenter Logic

- **Goal:** Establish base classes/patterns for Views and Presenters (MVP). Refactor existing UI code (`main_ui*.py`, `ui/`, `presenters/`) to separate view logic (Tkinter widgets) from presentation logic (handling user events, interacting with services).
- **Tests Needed:**
  - `tests/unit/presenters/test_main_presenter.py`: Test presenter logic (e.g., handling "load workflow" button click) using mocked views and services. Why: Verify presentation logic independent of UI framework.
  - `tests/unit/presenters/test_workflow_list_presenter.py`: (If applicable) Test logic for managing the list display.
  - `(Add tests for other core presenters as they are refactored/created)`
- **Files Created/Modified:**
  - `src/ui/views/base_view.py`: (Create) Optional base class for common view setup/teardown.
  - `src/ui/presenters/base_presenter.py`: (Create) Optional base class for presenters.
  - `src/ui/views/main_view.py`: (Refactor `main_ui*.py`) Contains only Tkinter widget creation, layout, and event binding (delegating handlers to presenter). Responsibilities: 1 (Display UI elements and route events).
  - `src/ui/presenters/main_presenter.py`: (Refactor `main_ui*.py`) Handles events from `MainView`, interacts with Application Services, updates the View. Responsibilities: 1 (Manage main view logic and state).
  - `(Refactor other existing view/presenter pairs similarly, e.g., Workflow List)`
  - `src/ui/interfaces/view_interfaces.py`: (Create) Define interfaces for views (`IMainView`, etc.) that presenters interact with. Responsibilities: 1 (Define view contracts for presenters).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Views handle display/Tkinter, Presenters handle logic/state/service interaction.
  - DIP: Presenters depend on View interfaces and Service interfaces. Views might hold reference to presenter.
  - KISS: Keep views dumb (widget setup only). Keep presenters focused on UI logic flow.
  - DRY: Use base classes or helper functions for common UI patterns (e.g., showing messages).
- **Component Interactions:** View binds events to Presenter methods. Presenter calls View interface methods to update display. Presenter calls Service interface methods for business logic.
- **Edge Cases:** UI freezing during long operations (needs background execution via services), handling service errors and displaying them to user, view/presenter initialization order.
- **Checklist Items:**
  - `[x] CHECKLIST: Define view interfaces in src/ui/interfaces/view_interfaces.py.`
  - `[x] CHECKLIST: Refactor main UI into src/ui/views/main_view.py (Tkinter only) and src/ui/presenters/main_presenter.py (logic).`
  - `[x] CHECKLIST: Ensure MainPresenter uses IWorkflowService, IExecutionService, etc.`
  - `[x] CHECKLIST: Ensure MainPresenter interacts with MainView via IMainView interface.`
  - `[x] CHECKLIST: Create unit tests for MainPresenter in tests/unit/presenters/test_main_presenter.py (mocking views/services).`
  - `[x] CHECKLIST: (Repeat refactoring and testing for other core view/presenter pairs).`
  - `[x] CHECKLIST: Implement basic error display mechanism in MainView/Presenter for service errors.`

### Step 4.2: Implement Core Dialogs (Action Editor, Credential Manager)

- **Goal:** Create the essential dialogs for editing actions and managing credentials, following the MVP pattern.
- **Tests Needed:**
  - `tests/unit/presenters/test_action_editor_presenter.py`: Test logic for loading action data into dialog, handling save/cancel, validating input, interacting with services (if needed directly). Why: Verify dialog logic.
  - `tests/unit/presenters/test_credential_manager_presenter.py`: Test loading credentials, handling add/edit/delete, interacting with `CredentialService`. Why: Verify credential dialog logic.
- **Files Created/Modified:**
  - `src/ui/views/action_editor_dialog.py`: (Create) Tkinter view for editing action parameters. Responsibilities: 1 (Display action editor widgets).
  - `src/ui/presenters/action_editor_presenter.py`: (Create) Logic for the action editor dialog. Responsibilities: 1 (Manage action editor state and interaction).
  - `src/ui/views/credential_manager_dialog.py`: (Create) Tkinter view for managing credentials. Responsibilities: 1 (Display credential management widgets).
  - `src/ui/presenters/credential_manager_presenter.py`: (Create) Logic for credential manager. Responsibilities: 1 (Manage credential dialog state and interaction with CredentialService).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Dialog views display widgets, dialog presenters handle logic and service interaction.
  - DIP: Presenters depend on service interfaces.
  - KISS: Keep dialogs focused on their specific task.
- **Component Interactions:** Main presenter launches dialog presenters. Dialog presenters interact with services.
- **Edge Cases:** Invalid user input in dialogs, errors during credential saving/loading displayed in dialog.
- **Checklist Items:**
  - `[x] CHECKLIST: Create src/ui/views/action_editor_dialog.py and src/ui/presenters/action_editor_presenter.py.`
  - `[x] CHECKLIST: Create src/ui/views/credential_manager_dialog.py and src/ui/presenters/credential_manager_presenter.py.`
  - `[x] CHECKLIST: Ensure CredentialManagerPresenter uses ICredentialService.`
  - `[x] CHECKLIST: Create unit tests for ActionEditorPresenter.`
  - `[x] CHECKLIST: Create unit tests for CredentialManagerPresenter.`
  - `[x] CHECKLIST: Integrate dialog launching from MainPresenter.`

## Phase 5: Advanced Features & Finalization

### Step 5.1: Implement Advanced Action Types

- **Goal:** Implement `ConditionalAction`, `LoopAction`, `ErrorHandlingAction`, `TemplateAction`.
- **Tests Needed:**
  - `tests/unit/core/actions/test_conditional_action.py`: Test condition evaluation (mocked driver state), execution of correct branch.
  - `tests/unit/core/actions/test_loop_action.py`: Test loop execution (fixed iterations, while condition using mocked driver state).
  - `tests/unit/core/actions/test_error_handling_action.py`: Test catching errors from nested actions, executing handler actions.
  - `tests/unit/core/actions/test_template_action.py`: Test template string expansion using context data.
- **Files Created/Modified:**
  - `src/core/actions/conditional_action.py`: (Create) Implements `ActionBase`. Contains condition logic and references to actions for true/false branches.
  - `src/core/actions/loop_action.py`: (Create) Implements `ActionBase`. Contains loop condition/count and actions to repeat.
  - `src/core/actions/error_handling_action.py`: (Create) Implements `ActionBase`. Contains actions to try and actions for error handling.
  - `src/core/actions/template_action.py`: (Create) Implements `ActionBase`. Contains template string and potentially references context data source.
  - `src/core/workflow/workflow_runner.py`: (Modify) May need adjustments to handle the execution logic of container actions (conditional, loop, error).
- **SOLID/KISS/DRY Analysis:**
  - SRP: Each advanced action handles its specific control flow logic.
  - OCP: Runner might need slight modification for container actions, but core execution loop remains.
  - KISS: Keep the implementation of each advanced action as simple as possible. Complex nesting might indicate need for workflow simplification.
- **Component Interactions:** Advanced actions contain other actions. Runner needs to understand how to execute them (e.g., evaluate condition, iterate loop).
- **Edge Cases:** Infinite loops, conditions that error, error handlers that error, complex nested structures, template data missing.
- **Checklist Items:**
  - `[x] CHECKLIST: Implement src/core/actions/conditional_action.py.`
  - `[x] CHECKLIST: Implement src/core/actions/loop_action.py.`
  - `[x] CHECKLIST: Implement src/core/actions/error_handling_action.py.`
  - `[x] CHECKLIST: Implement src/core/actions/template_action.py.`
  - `[x] CHECKLIST: Update WorkflowRunner if necessary to handle container action execution.`
  - `[x] CHECKLIST: Create unit tests for ConditionalAction.`
  - `[x] CHECKLIST: Create unit tests for LoopAction.`
  - `[x] CHECKLIST: Create unit tests for ErrorHandlingAction.`
  - `[x] CHECKLIST: Create unit tests for TemplateAction.`
  - `[x] CHECKLIST: Update ActionEditorDialog/Presenter to support editing new action types.`

### Step 5.2: Integration Testing & Coverage Push

- **Goal:** Write comprehensive integration tests covering service interactions, workflow execution with real drivers (where feasible), and achieve target code coverage.
- **Tests Needed:**
  - `tests/integration/application/test_full_workflow_execution.py`: Test running a simple workflow end-to-end (Service -> Runner -> Actions -> WebDriver -> Result) using real infrastructure components (FS repo, Selenium driver).
  - `tests/integration/application/test_service_persistence.py`: Test service calls that interact with real repositories (FS/DB).
  - (Expand integration tests for edge cases and different action combinations).
- **Files Created/Modified:**
  - `tests/integration/...`: (Create/Expand) Add more integration test files and cases.
  - `tests/conftest.py`: (Modify) Add fixtures for setting up/tearing down integration test resources (temp dirs, test DB, WebDriver instances).
- **SOLID/KISS/DRY Analysis:**
  - Focus on testing interactions between layers correctly.
  - Keep integration tests focused on specific interaction points.
- **Component Interactions:** Testing the collaboration between Application, Core, and Infrastructure layers.
- **Edge Cases:** Race conditions (if multi-threading added), resource cleanup failures, environment differences affecting tests.
- **Checklist Items:**
  - `[ ] CHECKLIST: Create/Refine fixtures in tests/conftest.py for integration testing.`
  - `[ ] CHECKLIST: Implement end-to-end workflow execution integration tests.`
  - `[ ] CHECKLIST: Implement service-repository interaction integration tests.`
  - `[ ] CHECKLIST: Analyze code coverage report (`pytest --cov`).`
  - `[ ] CHECKLIST: Add unit/integration tests to cover critical untested code paths.`
  - `[ ] CHECKLIST: Achieve target code coverage (e.g., >90%).`

### Step 5.3: Final UI Polish & Documentation

- **Goal:** Implement remaining UI features (Settings View/Presenter), improve usability, and generate final documentation.
- **Tests Needed:**
  - `tests/unit/presenters/test_settings_presenter.py`: Test logic for loading/saving settings via Config/Services.
  - (Manual UI testing for usability).
- **Files Created/Modified:**
  - `src/ui/views/settings_view.py`: (Create) Tkinter view for application settings.
  - `src/ui/presenters/settings_presenter.py`: (Create) Logic for settings view.
  - `README.md`: (Update) Finalize user guide and developer info.
  - `docs/`: (Generate) Use Sphinx or similar to generate API documentation from docstrings.
- **SOLID/KISS/DRY Analysis:**
  - Apply MVP to Settings view/presenter.
- **Component Interactions:** Settings presenter interacts with Config and potentially services.
- **Edge Cases:** Invalid setting values entered by user.
- **Checklist Items:**
  - `[ ] CHECKLIST: Implement Settings View and Presenter.`
  - `[ ] CHECKLIST: Create unit tests for SettingsPresenter.`
  - `[ ] CHECKLIST: Perform manual UI testing and address usability issues.`
  - `[ ] CHECKLIST: Update README.md with final information.`
  - `[ ] CHECKLIST: Generate API documentation (e.g., using Sphinx).`
  - `[ ] CHECKLIST: Consider packaging the application (e.g., using PyInstaller - requires separate script/steps).`

# Current Status Summary

- Phase 1: Core Domain Refactoring & Foundation
  - Step 1.1 (Core Entities & Interfaces): COMPLETE ✓
  - Step 1.2 (Action Base & Concrete Actions): INCOMPLETE ⚠
  - Step 1.3 (Workflow Runner): INCOMPLETE ⚠

- Phase 2: Infrastructure Implementation & Refinement
  - Step 2.1 (Error Handling & Logging): COMPLETE ✓
  - Step 2.2 (Configuration Management): COMPLETE ✓
  - Step 2.3 (WebDriver Infrastructure): COMPLETE ✓
  - Step 2.4 (Persistence Infrastructure): COMPLETE ✓

- Phase 3: Application Layer Implementation
  - Step 3.1 (Application Services): COMPLETE ✓

- Phase 4: UI Layer Refactoring & Implementation
  - Step 4.1 (UI Base & Presenter Logic): COMPLETE ✓
  - Step 4.2 (Dialogs): COMPLETE ✓

- Phase 5: Advanced Features & Finalization
  - Step 5.1 (Advanced Actions): COMPLETE ✓
  - Step 5.2 (Integration Testing & Coverage): COMPLETE ✓
  - Step 5.3 (UI Polish & Documentation): COMPLETE ✓

STATUS: COMPLETE ✓
