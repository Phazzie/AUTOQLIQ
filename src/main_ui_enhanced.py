"""Enhanced main UI application for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox, Menu, scrolledtext
import logging
import os
import sys
import traceback
import threading
import time
from typing import Dict, Any, Optional

# Configuration
from src.config import config

# Core components
from src.core.exceptions import AutoQliqError, UIError, ConfigError

# Infrastructure components
from src.infrastructure.repositories.factory import RepositoryFactory
from src.infrastructure.repositories.thread_safe_workflow_repository import ThreadSafeWorkflowRepository
from src.infrastructure.repositories.secure_credential_repository import SecureCredentialRepository
from src.infrastructure.encryption.simple_encryption_service import SimpleEncryptionService
from src.infrastructure.webdrivers import WebDriverFactory

# Error handling and recovery
from src.infrastructure.common.error_recovery import recovery_manager, with_error_recovery
from src.infrastructure.common.error_monitoring import error_monitor, monitor_errors

# Application Services
from src.application.services import (
    CredentialService, WorkflowService, WebDriverService,
    SchedulerService, ReportingService
)

# Enhanced UI components
from src.ui.views.workflow_runner_view_enhanced import WorkflowRunnerViewEnhanced
from src.ui.presenters.workflow_editor_presenter_enhanced import WorkflowEditorPresenterEnhanced
from src.ui.presenters.workflow_runner_presenter_enhanced import WorkflowRunnerPresenterEnhanced
from src.ui.factories.enhanced_ui_factory import EnhancedUIFactory
from src.ui.common.status_bar import StatusBar
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog
from src.ui.dialogs.diagnostics_dialog import DiagnosticsDialog

# Original UI components (for compatibility)
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.settings_view import SettingsView
from src.ui.presenters.settings_presenter import SettingsPresenter

logger = logging.getLogger(__name__)


def setup_logging() -> logging.Logger:
    """Set up logging for the application."""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(config.log_file), exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=config.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(config.log_file, mode='a')
            ]
        )

        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized. Log file: {config.log_file}")
        return logger
    except Exception as e:
        # Fallback logging setup if the config-based setup fails
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to set up logging from config: {e}")
        logger.info("Using fallback logging configuration")
        return logger


@monitor_errors("repository_creation")
def create_repositories() -> Dict[str, Any]:
    """Create the repositories for the application."""
    try:
        logger.info(f"Creating repositories. Type: {config.repository_type}")

        # Create the encryption service
        encryption_service = SimpleEncryptionService(config.encryption_key)

        if config.repository_type == "file_system":
            # Create the directories if they don't exist
            os.makedirs(config.workflows_path, exist_ok=True)
            os.makedirs(os.path.dirname(config.credentials_path), exist_ok=True)

            # Create the repositories with error recovery
            workflow_repository = create_workflow_repository_with_recovery(
                config.workflows_path
            )

            credential_repository = create_credential_repository_with_recovery(
                config.credentials_path,
                encryption_service
            )
        else:
            # Use the repository factory for other repository types
            factory = RepositoryFactory()
            workflow_repository = factory.create_workflow_repository(
                repo_type=config.repository_type,
                directory_path=config.workflows_path,
                db_path=config.db_path
            )
            credential_repository = factory.create_credential_repository(
                repo_type=config.repository_type,
                file_path=config.credentials_path,
                db_path=config.db_path,
                encryption_key=config.encryption_key
            )

        # Create the WebDriver factory
        webdriver_factory = WebDriverFactory()

        logger.info("Repositories created successfully")
        return {
            'workflow_repository': workflow_repository,
            'credential_repository': credential_repository,
            'webdriver_factory': webdriver_factory
        }
    except Exception as e:
        logger.exception(f"Failed to create repositories: {e}")
        error_monitor.record_error(e, "create_repositories")
        raise ConfigError(f"Failed to create repositories: {e}", cause=e) from e


@with_error_recovery("creating workflow repository")
def create_workflow_repository_with_recovery(directory_path: str) -> ThreadSafeWorkflowRepository:
    """Create a workflow repository with error recovery."""
    try:
        return ThreadSafeWorkflowRepository(
            directory_path=directory_path,
            create_if_missing=True
        )
    except Exception as e:
        logger.error(f"Error creating workflow repository: {e}")
        # Try to recover by creating a new directory
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            logger.info(f"Created workflow directory: {directory_path}")

        # Try again
        return ThreadSafeWorkflowRepository(
            directory_path=directory_path,
            create_if_missing=True
        )


@with_error_recovery("creating credential repository")
def create_credential_repository_with_recovery(
    file_path: str,
    encryption_service: SimpleEncryptionService
) -> SecureCredentialRepository:
    """Create a credential repository with error recovery."""
    try:
        return SecureCredentialRepository(
            file_path=file_path,
            encryption_service=encryption_service,
            create_if_missing=True
        )
    except Exception as e:
        logger.error(f"Error creating credential repository: {e}")
        # Try to recover by creating the directory
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # If the file exists but is corrupted, try to delete it
        if os.path.exists(file_path):
            try:
                # Backup the corrupted file
                backup_path = f"{file_path}.corrupted.{int(time.time())}"
                os.rename(file_path, backup_path)
                logger.info(f"Backed up corrupted credential file to {backup_path}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted credential file: {backup_error}")

        # Try again
        return SecureCredentialRepository(
            file_path=file_path,
            encryption_service=encryption_service,
            create_if_missing=True
        )


def create_services(repositories: Dict[str, Any]) -> Dict[str, Any]:
    """Create the application services."""
    try:
        logger.info("Creating application services")

        # Create the services
        credential_service = CredentialService(repositories['credential_repository'])
        webdriver_service = WebDriverService(repositories['webdriver_factory'])
        workflow_service = WorkflowService(
            repositories['workflow_repository'],
            repositories['credential_repository'],
            webdriver_service
        )

        # Initialize placeholder services
        scheduler_service = SchedulerService()
        reporting_service = ReportingService()

        logger.info("Application services created successfully")
        return {
            'credential_service': credential_service,
            'webdriver_service': webdriver_service,
            'workflow_service': workflow_service,
            'scheduler_service': scheduler_service,
            'reporting_service': reporting_service
        }
    except Exception as e:
        logger.exception(f"Failed to create application services: {e}")
        raise ConfigError(f"Failed to create application services: {e}", cause=e) from e


def create_enhanced_ui(
    root: tk.Tk,
    repositories: Dict[str, Any],
    services: Dict[str, Any]
) -> Dict[str, Any]:
    """Create the enhanced UI components."""
    try:
        logger.info("Creating enhanced UI components")

        # Create a status bar
        status_bar = StatusBar(root, show_progress=True, initial_message="Ready")
        status_bar.frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a notebook for the views
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create frames for each view
        editor_frame = ttk.Frame(notebook)
        runner_frame = ttk.Frame(notebook)
        settings_frame = ttk.Frame(notebook)

        notebook.add(editor_frame, text="Workflow Editor")
        notebook.add(runner_frame, text="Workflow Runner")
        notebook.add(settings_frame, text="Settings")

        # Create the enhanced presenters
        workflow_editor_presenter = WorkflowEditorPresenterEnhanced(
            repositories['workflow_repository']
        )

        workflow_runner_presenter = WorkflowRunnerPresenterEnhanced(
            repositories['workflow_repository'],
            repositories['credential_repository'],
            repositories['webdriver_factory']
        )

        settings_presenter = SettingsPresenter(config)

        # Create the views
        workflow_editor_view = WorkflowEditorView(editor_frame, workflow_editor_presenter)
        workflow_runner_view = WorkflowRunnerViewEnhanced(runner_frame, workflow_runner_presenter)
        settings_view = SettingsView(settings_frame, settings_presenter)

        # Link views and presenters
        workflow_editor_presenter.set_view(workflow_editor_view)
        workflow_runner_presenter.set_view(workflow_runner_view)
        settings_presenter.set_view(settings_view)

        logger.info("Enhanced UI components created successfully")
        return {
            'notebook': notebook,
            'status_bar': status_bar,
            'workflow_editor_presenter': workflow_editor_presenter,
            'workflow_runner_presenter': workflow_runner_presenter,
            'settings_presenter': settings_presenter,
            'workflow_editor_view': workflow_editor_view,
            'workflow_runner_view': workflow_runner_view,
            'settings_view': settings_view
        }
    except Exception as e:
        logger.exception(f"Failed to create enhanced UI components: {e}")
        raise UIError(f"Failed to create enhanced UI components: {e}", cause=e) from e


def create_menu(
    root: tk.Tk,
    ui_components: Dict[str, Any],
    repositories: Dict[str, Any],
    services: Dict[str, Any]
) -> tk.Menu:
    """Create the application menu."""
    try:
        logger.info("Creating application menu")

        # Create the menu bar
        menubar = Menu(root)
        root.config(menu=menubar)

        # Create the File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Exit", command=root.quit)

        # Create the Manage menu
        manage_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=manage_menu)

        # Add credential manager command
        def open_credential_manager():
            try:
                dialog = CredentialManagerDialog(
                    root,
                    credential_service=services['credential_service']
                )
                dialog.show()
                # Refresh the credential list in the runner view
                ui_components['workflow_runner_view'].set_credential_list(
                    repositories['credential_repository'].list_credentials()
                )
            except Exception as e:
                logger.exception(f"Error opening credential manager: {e}")
                messagebox.showerror(
                    "Error",
                    f"Failed to open credential manager: {e}",
                    parent=root
                )

        manage_menu.add_command(label="Credentials...", command=open_credential_manager)

        # Create the Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Add diagnostics command
        def open_diagnostics():
            try:
                dialog = DiagnosticsDialog(
                    root,
                    repositories=repositories,
                    services=services
                )
                dialog.show()
            except Exception as e:
                logger.exception(f"Error opening diagnostics: {e}")
                messagebox.showerror(
                    "Error",
                    f"Failed to open diagnostics: {e}",
                    parent=root
                )

        tools_menu.add_command(label="Diagnostics...", command=open_diagnostics)

        # Create the Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        def show_about():
            messagebox.showinfo(
                "About AutoQliq",
                f"AutoQliq {config.VERSION}\n\n"
                "A browser automation tool for creating and running workflows.\n\n"
                "© 2023 AutoQliq Team",
                parent=root
            )

        help_menu.add_command(label="About", command=show_about)

        # Add error log viewer command
        def view_error_log():
            try:
                # Get the error summary
                error_summary = error_monitor.get_error_summary(days=7, include_details=True)

                # Create a simple dialog to display the errors
                error_dialog = tk.Toplevel(root)
                error_dialog.title("Error Log")
                error_dialog.geometry("800x600")
                error_dialog.minsize(600, 400)

                # Make the dialog modal
                error_dialog.transient(root)
                error_dialog.grab_set()

                # Create a scrolled text widget
                text = scrolledtext.ScrolledText(error_dialog, wrap=tk.WORD)
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                # Add the error summary
                text.insert(tk.END, f"Error Summary (Last {error_summary['period_days']} days)\n")
                text.insert(tk.END, f"Total Errors: {error_summary['total_errors']}\n")
                text.insert(tk.END, f"Unique Error Types: {error_summary['unique_error_types']}\n\n")

                # Add the error records
                if 'records' in error_summary and error_summary['records']:
                    text.insert(tk.END, "Recent Errors:\n")
                    for record in error_summary['records']:
                        text.insert(tk.END, f"Type: {record['error_type']}\n")
                        text.insert(tk.END, f"Message: {record['error_message']}\n")
                        text.insert(tk.END, f"Context: {record['context']}\n")
                        text.insert(tk.END, f"Time: {record['datetime']}\n\n")
                else:
                    text.insert(tk.END, "No errors recorded.\n")

                # Make the text widget read-only
                text.config(state=tk.DISABLED)

                # Add a close button
                close_button = ttk.Button(error_dialog, text="Close", command=error_dialog.destroy)
                close_button.pack(pady=10)

                # Center the dialog on the parent
                error_dialog.update_idletasks()
                parent_x = root.winfo_rootx()
                parent_y = root.winfo_rooty()
                parent_width = root.winfo_width()
                parent_height = root.winfo_height()
                dialog_width = error_dialog.winfo_width()
                dialog_height = error_dialog.winfo_height()
                x = parent_x + (parent_width - dialog_width) // 2
                y = parent_y + (parent_height - dialog_height) // 2
                error_dialog.geometry(f"+{x}+{y}")
            except Exception as e:
                logger.exception(f"Error viewing error log: {e}")
                messagebox.showerror(
                    "Error",
                    f"Failed to view error log: {e}",
                    parent=root
                )

        help_menu.add_command(label="View Error Log", command=view_error_log)

        logger.info("Application menu created successfully")
        return menubar
    except Exception as e:
        logger.exception(f"Failed to create application menu: {e}")
        raise UIError(f"Failed to create application menu: {e}", cause=e) from e


def setup_error_handlers(root: tk.Tk, ui_components: Dict[str, Any]) -> None:
    """Set up global error handlers."""
    try:
        logger.info("Setting up global error handlers")

        # Set up the default exception handler
        def handle_exception(exc_type, exc_value, exc_traceback):
            # Log the exception
            if issubclass(exc_type, KeyboardInterrupt):
                # Don't log keyboard interrupt
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Log the exception
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

            # Show an error message to the user
            if root and root.winfo_exists():
                try:
                    # Format the error message
                    error_message = str(exc_value)
                    if not error_message:
                        error_message = exc_type.__name__

                    # Show the error message
                    messagebox.showerror(
                        "Unexpected Error",
                        f"An unexpected error occurred:\n\n{error_message}\n\n"
                        f"Please check the log file for details:\n{config.log_file}",
                        parent=root
                    )
                except Exception as e:
                    # If showing the error message fails, log it
                    logger.error(f"Failed to show error message: {e}")

        # Set the exception handler
        sys.excepthook = handle_exception

        # Set up the threading exception handler
        def handle_thread_exception(args):
            # Extract the exception information
            exc_type, exc_value, exc_traceback = args.exc_type, args.exc_value, args.exc_traceback

            # Log the exception
            logger.critical("Uncaught exception in thread", exc_info=(exc_type, exc_value, exc_traceback))

            # Show an error message to the user
            if root and root.winfo_exists():
                try:
                    # Format the error message
                    error_message = str(exc_value)
                    if not error_message:
                        error_message = exc_type.__name__

                    # Schedule showing the error message on the main thread
                    root.after(0, lambda: messagebox.showerror(
                        "Unexpected Error in Thread",
                        f"An unexpected error occurred in a background thread:\n\n{error_message}\n\n"
                        f"Please check the log file for details:\n{config.log_file}",
                        parent=root
                    ))
                except Exception as e:
                    # If showing the error message fails, log it
                    logger.error(f"Failed to show thread error message: {e}")

        # Set the threading exception handler
        threading.excepthook = handle_thread_exception

        # Set up periodic status bar updates
        if 'status_bar' in ui_components:
            def update_status_bar():
                try:
                    # Update the status bar with memory usage
                    import psutil
                    process = psutil.Process(os.getpid())
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    ui_components['status_bar'].set_message(f"Memory: {memory_mb:.1f} MB")
                except Exception as e:
                    logger.error(f"Failed to update status bar: {e}")
                finally:
                    # Schedule the next update
                    if root and root.winfo_exists():
                        root.after(10000, update_status_bar)  # Update every 10 seconds

            # Start the periodic updates
            root.after(10000, update_status_bar)

        logger.info("Global error handlers set up successfully")
    except Exception as e:
        logger.exception(f"Failed to set up global error handlers: {e}")
        # Don't raise an exception here, as this is the error handler setup


def main() -> None:
    """Main application entry point."""
    # Set up logging
    global logger
    logger = setup_logging()
    logger.info(f"--- Starting {config.WINDOW_TITLE} ---")

    # Create the root window
    root = tk.Tk()
    root.title(config.WINDOW_TITLE)
    root.geometry(config.WINDOW_GEOMETRY)

    try:
        # Create the repositories
        repositories = create_repositories()

        # Create the services
        services = create_services(repositories)

        # Create the enhanced UI components
        ui_components = create_enhanced_ui(root, repositories, services)

        # Create the menu
        menu = create_menu(root, ui_components, repositories, services)

        # Set up error handlers
        setup_error_handlers(root, ui_components)

        # Set the initial status
        if 'status_bar' in ui_components:
            ui_components['status_bar'].set_message("Ready")

        # Start the main loop
        logger.info("Starting main loop")
        root.mainloop()
    except ConfigError as e:
        logger.critical(f"Configuration error: {e}")
        messagebox.showerror(
            "Configuration Error",
            f"Failed to initialize application due to a configuration error:\n\n{e}\n\n"
            f"Please check your configuration and try again.",
            parent=root if root.winfo_exists() else None
        )
    except UIError as e:
        logger.critical(f"UI error: {e}")
        messagebox.showerror(
            "UI Error",
            f"Failed to initialize application due to a UI error:\n\n{e}\n\n"
            f"Please check the log file for details:\n{config.log_file}",
            parent=root if root.winfo_exists() else None
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        messagebox.showerror(
            "Unexpected Error",
            f"Failed to initialize application due to an unexpected error:\n\n{e}\n\n"
            f"Please check the log file for details:\n{config.log_file}",
            parent=root if root.winfo_exists() else None
        )
    finally:
        logger.info("--- Application exiting ---")
        # Perform any necessary cleanup
        if root.winfo_exists():
            root.destroy()


if __name__ == "__main__":
    main()
