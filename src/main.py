"""Main entry point for AutoQliq application.

This module provides the main entry point for the AutoQliq application.
It initializes the application, sets up logging, creates repositories,
and ensures the default workflow exists.
"""

import tkinter as tk
import logging
from tkinter import ttk, messagebox, Menu

# Configuration
from src.config import config

# Infrastructure components
from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory

# Application Services
from src.application.services import (
    CredentialService, WorkflowService, WebDriverService,
    SchedulerService, ReportingService
)

# UI components
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.ui.views.settings_view import SettingsView
from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.ui.presenters.settings_presenter import SettingsPresenter
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog

# Default workflow loader
from src.ui.default_workflow_loader import ensure_default_workflow_exists


def setup_logging():
    """Set up logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.log_file)
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging()
    logger.info(f"--- Starting {config.WINDOW_TITLE} ---")
    logger.info(f"Using Repository Type: {config.repository_type}")
    logger.info(f"Workflows Path: {config.workflows_path}")
    logger.info(f"Credentials Path: {config.credentials_path}")

    try:
        root = tk.Tk()
        root.title(config.WINDOW_TITLE)
        root.geometry(config.WINDOW_GEOMETRY)
    except Exception as e:
        logger.exception(f"Failed to initialize Tkinter: {e}")
        print(f"ERROR: Failed to initialize Tkinter: {e}")
        print("This may be due to compatibility issues with your operating system.")
        print("Please check the log file for more details.")
        return

    try:
        # Create repositories
        logger.info("Initializing repositories...")
        repository_factory = RepositoryFactory()
        workflow_repo = repository_factory.create_workflow_repository(config.repository_type)
        credential_repo = repository_factory.create_credential_repository(config.repository_type)

        # Ensure default workflow exists
        logger.info("Checking for default workflow...")
        ensure_default_workflow_exists(workflow_repo)

        # Create WebDriver factory
        logger.info("Initializing WebDriver factory...")
        webdriver_factory = WebDriverFactory()
        logger.info("Repositories initialized.")

        # Create Application Services, injecting dependencies
        credential_service = CredentialService(credential_repo)
        webdriver_service = WebDriverService(webdriver_factory)
        workflow_service = WorkflowService(workflow_repo, credential_repo, webdriver_service)
        # Initialize placeholder services
        scheduler_service = SchedulerService()
        reporting_service = ReportingService()
        logger.info("Application services initialized.")

        # Create Presenters, injecting Service interfaces
        editor_presenter = WorkflowEditorPresenter(workflow_service)
        runner_presenter = WorkflowRunnerPresenter(workflow_service, credential_service, webdriver_service)
        settings_presenter = SettingsPresenter(config)
        logger.info("Presenters initialized.")

    except Exception as e:
        logger.exception("FATAL: Failed to initialize core components. Application cannot start.")
        messagebox.showerror("Initialization Error",
                            f"Failed to initialize application components: {e}\n\n"
                            f"Please check configuration (`config.ini`) and file permissions.\n"
                            f"See log file '{config.log_file}' for details.")
        root.destroy()
        return

    try:
        # Create the main menu
        logger.info("Creating main menu...")
        main_menu = Menu(root)
        root.config(menu=main_menu)

        # File menu
        file_menu = Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=root.destroy)

        # Manage menu
        manage_menu = Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="Manage", menu=manage_menu)

        # Credential Manager dialog
        def open_credential_manager():
            CredentialManagerDialog(root, credential_service)

        manage_menu.add_command(label="Credentials...", command=open_credential_manager)

        # Main Content Area (Notebook)
        notebook = ttk.Notebook(root)

        # Create Frames for each tab content area
        editor_tab_frame = ttk.Frame(notebook)
        runner_tab_frame = ttk.Frame(notebook)
        settings_tab_frame = ttk.Frame(notebook)

        notebook.add(editor_tab_frame, text="Workflow Editor")
        notebook.add(runner_tab_frame, text="Workflow Runner")
        notebook.add(settings_tab_frame, text="Settings")

        # Create Views, injecting their frames and presenters
        editor_view = WorkflowEditorView(editor_tab_frame, editor_presenter)
        runner_view = WorkflowRunnerView(runner_tab_frame, runner_presenter)
        settings_view = SettingsView(settings_tab_frame, settings_presenter)

        # Connect presenters to views
        editor_presenter.set_view(editor_view)
        runner_presenter.set_view(runner_view)
        settings_presenter.set_view(settings_view)

        # Initialize views (which triggers presenter initialization)
        editor_view.initialize()
        runner_view.initialize()
        settings_view.initialize()

        # Pack the notebook to fill the window
        notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Status bar at the bottom
        status_frame = ttk.Frame(root, relief=tk.SUNKEN, borderwidth=1)
        status_label = ttk.Label(status_frame, text="Ready")
        status_label.pack(side=tk.LEFT, padx=5)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Start Application
        logger.info("Starting Tkinter main loop.")
        root.mainloop()

    except Exception as e:
        logger.exception("An error occurred during application run.")
        if root.winfo_exists():
            messagebox.showerror("Application Error",
                                f"An unexpected error occurred: {e}\n\n"
                                f"Please check the log file '{config.log_file}'.")
    finally:
        logger.info("--- Application exiting ---")


if __name__ == "__main__":
    main()
