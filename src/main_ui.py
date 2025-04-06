import tkinter as tk
from tkinter import ttk
import logging
import os

# Core components (interfaces needed for type hinting)
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService

# Infrastructure components
from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory

# Application services
from src.application.services.credential_service import CredentialService
from src.application.services.workflow_service import WorkflowService
from src.application.services.webdriver_service import WebDriverService

# UI components
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter

# Common utilities
from src.infrastructure.common.logger_factory import LoggerFactory

# Configuration
from src.config import Config

# Load configuration from config.ini
config = Config()
LOG_LEVEL = getattr(logging, config.get('logging', 'level', 'DEBUG'))
LOG_FILE = config.get('logging', 'file', 'autoqliq_app.log')
REPOSITORY_TYPE = config.get('repositories', 'type', 'file_system')
CREDENTIALS_PATH = config.get('repositories', 'credentials_path', 'credentials.json')
WORKFLOWS_PATH = config.get('repositories', 'workflows_path', 'workflows')
WINDOW_TITLE = config.get('ui', 'window_title', 'AutoQliq v0.1')
WINDOW_GEOMETRY = config.get('ui', 'window_geometry', '900x650')


def setup_logging():
    """Configure logging for the application."""
    # Basic configuration for file and console
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler() # To console
        ]
    )
    # Example using LoggerFactory if preferred:
    # LoggerFactory.configure_root_logger(level=LOG_LEVEL, log_file=LOG_FILE)
    logging.info("Logging configured.")

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {WINDOW_TITLE}")

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_GEOMETRY)

    # --- Dependency Injection Setup ---
    logger.info(f"Using repository type: {REPOSITORY_TYPE}")
    repo_factory = RepositoryFactory()
    webdriver_factory = WebDriverFactory() # Instantiate the factory

    try:
        # File system paths need validation/creation
        if REPOSITORY_TYPE == "file_system":
            if not os.path.exists(WORKFLOWS_PATH):
                os.makedirs(WORKFLOWS_PATH, exist_ok=True)
                logger.info(f"Created workflows directory: {WORKFLOWS_PATH}")
            if not os.path.exists(CREDENTIALS_PATH):
                with open(CREDENTIALS_PATH, 'w') as f:
                    f.write("[]") # Create empty JSON list
                logger.info(f"Created empty credentials file: {CREDENTIALS_PATH}")

        # Create repositories using the factory
        # Pass create_if_missing=True for file repo robustness
        workflow_repo: IWorkflowRepository = repo_factory.create_workflow_repository(
            repository_type=REPOSITORY_TYPE,
            path=WORKFLOWS_PATH,
            create_if_missing=True
        )
        credential_repo: ICredentialRepository = repo_factory.create_credential_repository(
            repository_type=REPOSITORY_TYPE,
            path=CREDENTIALS_PATH,
            create_if_missing=True
        )
        logger.info("Repositories initialized.")

        # Create application services
        credential_service = CredentialService(credential_repo)
        workflow_service = WorkflowService(workflow_repo)
        webdriver_service = WebDriverService(webdriver_factory)
        logger.info("Application services initialized.")

        # Create Presenters, injecting service dependencies
        editor_presenter = WorkflowEditorPresenter(
            workflow_service=workflow_service,
            credential_service=credential_service
        )
        runner_presenter = WorkflowRunnerPresenter(
            workflow_service=workflow_service,
            credential_service=credential_service,
            webdriver_service=webdriver_service
        )
        logger.info("Presenters initialized.")

    except Exception as e:
         logger.exception("Failed to initialize repositories or presenters. Application cannot start.")
         # Show error message box before exiting
         messagebox.showerror("Initialization Error", f"Failed to initialize application components: {e}\n\nPlease check configuration and file permissions.\nSee log file '{LOG_FILE}' for details.")
         root.destroy() # Close the (likely empty) window
         return # Exit application

    # --- UI Setup ---
    try:
        # Use themed widgets
        style = ttk.Style(root)
        # Select a theme (clam, alt, default, classic) - depends on OS
        available_themes = style.theme_names()
        logger.debug(f"Available ttk themes: {available_themes}")
        # Prefer 'clam' or 'alt' for a more modern look if available
        preferred_themes = ['clam', 'alt', 'default']
        for theme in preferred_themes:
            if theme in available_themes:
                 style.theme_use(theme)
                 logger.info(f"Using ttk theme: {theme}")
                 break
        else:
             logger.warning("Could not find preferred ttk theme. Using system default.")


        # Create Notebook (Tabs)
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Frames for each tab
        editor_tab_frame = ttk.Frame(notebook)
        runner_tab_frame = ttk.Frame(notebook)

        notebook.add(editor_tab_frame, text="Workflow Editor")
        notebook.add(runner_tab_frame, text="Workflow Runner")

        # Create Views, injecting presenters
        editor_view = WorkflowEditorView(editor_tab_frame, editor_presenter)
        runner_view = WorkflowRunnerView(runner_tab_frame, runner_presenter)
        logger.info("Views initialized.")

        # Set views in presenters (linking MVP components)
        editor_presenter.set_view(editor_view)
        runner_presenter.set_view(runner_view)
        logger.info("Views linked to presenters.")

        # --- Start Application ---
        logger.info("Starting Tkinter main loop.")
        root.mainloop()

    except Exception as e:
         logger.exception("An error occurred during application run.")
         # Attempt to show error message if main window still exists
         if root.winfo_exists():
              messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\n\nPlease check the log file '{LOG_FILE}'.")
         # Ensure cleanup happens if possible
    finally:
         logger.info("Application exiting.")
         # Perform any necessary cleanup (e.g., ensure webdriver is quit if runner didn't finish)
         # runner_presenter might hold a driver if execution was interrupted abruptly
         if runner_presenter and hasattr(runner_presenter, '_current_driver') and runner_presenter._current_driver:
              logger.warning("Attempting final WebDriver cleanup.")
              try:
                   runner_presenter._current_driver.quit()
              except Exception as q_e:
                   logger.error(f"Error during final WebDriver cleanup: {q_e}")


if __name__ == "__main__":
    # Import messagebox here so it's available in main's exception handler
    from tkinter import messagebox
    main()