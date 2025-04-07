import tkinter as tk
from tkinter import ttk, messagebox, Menu
import logging
import os

# Configuration
from src.config import config # Import the configured instance

# Core components (interfaces needed for type hinting)
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService

# Infrastructure components
from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory

# Application Services
from src.application.services import (
    CredentialService, WorkflowService, WebDriverService,
    SchedulerService, ReportingService # Include stubs
)

# UI components (use final names)
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.ui.views.settings_view import SettingsView # Import new Settings View
from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.ui.presenters.settings_presenter import SettingsPresenter # Import new Settings Presenter
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog # Import Credential Manager Dialog

# Common utilities
# LoggerFactory configures root logger based on AppConfig now
# from src.infrastructure.common.logger_factory import LoggerFactory


def setup_logging():
    """Configure logging based on AppConfig."""
    # BasicConfig is handled by config.py loading now
    # Just get the root logger and ensure level is set
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    # Add file handler if specified in config and not already added
    if config.log_file and not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
         try:
              file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
              formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
              file_handler.setFormatter(formatter)
              root_logger.addHandler(file_handler)
              logging.info(f"Added FileHandler for {config.log_file}")
         except Exception as e:
              logging.error(f"Failed to add FileHandler based on config: {e}")

    logging.info(f"Logging configured. Level: {logging.getLevelName(config.log_level)}")

# --- Global variable for Credential Dialog to prevent multiple instances ---
# (Alternatively, manage dialog lifecycle within a main controller/app class)
credential_dialog_instance: Optional[tk.Toplevel] = None

def main():
    """Main application entry point."""
    # Setup logging first using config values
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"--- Starting {config.WINDOW_TITLE} ---")
    logger.info(f"Using Repository Type: {config.repository_type}")
    logger.info(f"Workflows Path: {config.workflows_path}")
    logger.info(f"Credentials Path: {config.credentials_path}")

    root = tk.Tk()
    root.title(config.WINDOW_TITLE)
    root.geometry(config.WINDOW_GEOMETRY)

    # --- Dependency Injection Setup ---
    try:
        repo_factory = RepositoryFactory()
        webdriver_factory = WebDriverFactory()

        # Ensure directories/files exist for file system repo if selected
        if config.repository_type == "file_system":
            wf_path = config.workflows_path
            cred_path = config.credentials_path
            if not os.path.exists(wf_path):
                os.makedirs(wf_path, exist_ok=True)
                logger.info(f"Created workflows directory: {wf_path}")
            if not os.path.exists(cred_path) and config.repo_create_if_missing:
                with open(cred_path, 'w', encoding='utf-8') as f:
                    f.write("[]") # Create empty JSON list
                logger.info(f"Created empty credentials file: {cred_path}")

        # Create repositories using the factory and config
        workflow_repo: IWorkflowRepository = repo_factory.create_workflow_repository(
            repository_type=config.repository_type,
            path=config.workflows_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        credential_repo: ICredentialRepository = repo_factory.create_credential_repository(
            repository_type=config.repository_type,
            path=config.credentials_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        logger.info("Repositories initialized.")

        # Create Application Services, injecting dependencies
        credential_service = CredentialService(credential_repo)
        webdriver_service = WebDriverService(webdriver_factory)
        workflow_service = WorkflowService(workflow_repo, credential_repo, webdriver_service)
        # Initialize placeholder services (they don't do anything yet)
        scheduler_service = SchedulerService()
        reporting_service = ReportingService()
        logger.info("Application services initialized.")

        # Create Presenters, injecting Service interfaces
        editor_presenter = WorkflowEditorPresenter(workflow_service)
        runner_presenter = WorkflowRunnerPresenter(workflow_service, credential_service, webdriver_service)
        settings_presenter = SettingsPresenter(config) # Settings presenter interacts with config directly
        logger.info("Presenters initialized.")

    except Exception as e:
         logger.exception("FATAL: Failed to initialize core components. Application cannot start.")
         messagebox.showerror("Initialization Error", f"Failed to initialize application components: {e}\n\nPlease check configuration (`config.ini`) and file permissions.\nSee log file '{config.log_file}' for details.")
         root.destroy()
         return

    # --- UI Setup ---
    try:
        # Use themed widgets
        style = ttk.Style(root)
        available_themes = style.theme_names()
        logger.debug(f"Available ttk themes: {available_themes}")
        preferred_themes = ['clam', 'alt', 'vista', 'xpnative', 'aqua', 'default']
        for theme in preferred_themes:
            if theme in available_themes:
                 try: style.theme_use(theme); logger.info(f"Using ttk theme: {theme}"); break
                 except tk.TclError: logger.warning(f"Failed theme: '{theme}'.")
        else: logger.warning("Could not find preferred theme.")

        # --- Menu Bar ---
        menubar = Menu(root)
        root.config(menu=menubar)

        manage_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=manage_menu)

        def open_credential_manager():
             global credential_dialog_instance
             # Prevent multiple instances
             if credential_dialog_instance is not None and credential_dialog_instance.winfo_exists():
                  credential_dialog_instance.lift()
                  credential_dialog_instance.focus_set()
                  logger.debug("Credential Manager dialog already open, focusing.")
                  return
             logger.debug("Opening Credential Manager dialog.")
             # Pass the service to the dialog
             dialog = CredentialManagerDialog(root, credential_service)
             credential_dialog_instance = dialog.window # Store reference to Toplevel
             # Dialog runs its own loop implicitly via wait_window() called by show() if needed
             # For a non-blocking approach, dialog would need different handling.

        manage_menu.add_command(label="Credentials...", command=open_credential_manager)
        # Add other management options later if needed

        # --- Main Content Area (Notebook) ---
        notebook = ttk.Notebook(root)

        # Create Frames for each tab content area
        editor_tab_frame = ttk.Frame(notebook)
        runner_tab_frame = ttk.Frame(notebook)
        settings_tab_frame = ttk.Frame(notebook) # Frame for Settings tab

        notebook.add(editor_tab_frame, text="Workflow Editor")
        notebook.add(runner_tab_frame, text="Workflow Runner")
        notebook.add(settings_tab_frame, text="Settings") # Add Settings tab

        # --- Create Views, injecting presenters ---
        # Views are now created with the tab frame as their parent root
        editor_view = WorkflowEditorView(editor_tab_frame, editor_presenter)
        runner_view = WorkflowRunnerView(runner_tab_frame, runner_presenter)
        settings_view = SettingsView(settings_tab_frame, settings_presenter) # Create Settings view
        logger.info("Views initialized.")

        # --- Link Views and Presenters ---
        editor_presenter.set_view(editor_view)
        runner_presenter.set_view(runner_view)
        settings_presenter.set_view(settings_view) # Link Settings presenter and view
        logger.info("Views linked to presenters.")

        # --- Pack the Notebook ---
        # Pack notebook *after* creating views inside their frames
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Start Application ---
        logger.info("Starting Tkinter main loop.")
        root.mainloop()

    except Exception as e:
         logger.exception("An error occurred during application run.")
         if root.winfo_exists():
              messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\n\nPlease check the log file '{config.log_file}'.")
    finally:
         logger.info("--- Application exiting ---")
         # Cleanup handled within presenter/service threads now.
         # Any final cleanup needed? e.g. saving config explicitly?
         # config.save_config_to_file() # Uncomment if auto-save on exit is desired


if __name__ == "__main__":
    # Import Literal for type hinting if used directly here (it's used in RepositoryFactory)
    from typing import Literal
    main()