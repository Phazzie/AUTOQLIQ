"""Presenter for the Settings View."""

import logging
from typing import Optional, Dict, Any

# Configuration manager
from src.config import AppConfig, RepositoryType, BrowserTypeStr # Import literals
from src.core.exceptions import ConfigError, ValidationError
# UI dependencies
from src.ui.interfaces.presenter import IPresenter # Base interface might suffice
from src.ui.interfaces.view import IView # Use generic view or create ISettingsView
from src.ui.presenters.base_presenter import BasePresenter

# Define a more specific interface for the Settings View if needed
class ISettingsView(IView):
    def get_settings_values(self) -> Dict[str, Any]: pass
    def set_settings_values(self, settings: Dict[str, Any]) -> None: pass
    # Add specific methods if view needs more granular updates


class SettingsPresenter(BasePresenter[ISettingsView]):
    """
    Presenter for the Settings View. Handles loading settings into the view
    and saving changes back to the configuration source (config.ini).
    """
    def __init__(self, config_manager: AppConfig, view: Optional[ISettingsView] = None):
        """
        Initialize the SettingsPresenter.

        Args:
            config_manager: The application configuration manager instance.
            view: The associated SettingsView instance.
        """
        super().__init__(view)
        if config_manager is None:
             raise ValueError("Configuration manager cannot be None.")
        self.config = config_manager
        self.logger.info("SettingsPresenter initialized.")

    def set_view(self, view: ISettingsView) -> None:
        """Set the view and load initial settings."""
        super().set_view(view)
        self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view when it's set (calls load_settings)."""
        self.load_settings()

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Loading settings")
    def load_settings(self) -> None:
        """Load current settings from the config manager and update the view."""
        if not self.view:
             self.logger.warning("Load settings called but view is not set.")
             return

        self.logger.debug("Loading settings into view.")
        # Reload config from file to ensure latest values are shown
        self.config.reload_config()

        settings_data = {
            'log_level': logging.getLevelName(self.config.log_level),
            'log_file': self.config.log_file,
            'repository_type': self.config.repository_type,
            'workflows_path': self.config.workflows_path,
            'credentials_path': self.config.credentials_path,
            'db_path': self.config.db_path,
            'repo_create_if_missing': self.config.repo_create_if_missing,
            'default_browser': self.config.default_browser,
            'chrome_driver_path': self.config.get_driver_path('chrome') or "",
            'firefox_driver_path': self.config.get_driver_path('firefox') or "",
            'edge_driver_path': self.config.get_driver_path('edge') or "",
            'implicit_wait': self.config.implicit_wait,
            # Security settings intentionally omitted from UI editing
        }
        self.view.set_settings_values(settings_data)
        self.view.set_status("Settings loaded from config.ini.")
        self.logger.info("Settings loaded and view updated.")

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Saving settings")
    def save_settings(self) -> None:
        """Get settings from the view, validate, save via config manager, and reload."""
        if not self.view:
            self.logger.error("Save settings called but view is not set.")
            return

        self.logger.info("Attempting to save settings.")
        settings_to_save = self.view.get_settings_values()

        # --- Basic Validation (Presenter-level) ---
        errors = {}
        # Validate paths (basic check for emptiness if relevant)
        repo_type = settings_to_save.get('repository_type')
        if repo_type == 'file_system':
            if not settings_to_save.get('workflows_path'): errors['workflows_path'] = ["Workflows path required."]
            if not settings_to_save.get('credentials_path'): errors['credentials_path'] = ["Credentials path required."]
        elif repo_type == 'database':
             if not settings_to_save.get('db_path'): errors['db_path'] = ["Database path required."]
        else:
            errors['repository_type'] = ["Invalid repository type selected."]

        # Validate implicit wait
        try:
            wait = int(settings_to_save.get('implicit_wait', 0))
            if wait < 0: errors['implicit_wait'] = ["Implicit wait cannot be negative."]
        except (ValueError, TypeError):
            errors['implicit_wait'] = ["Implicit wait must be an integer."]
        # Validate Log Level
        log_level_str = str(settings_to_save.get('log_level', 'INFO')).upper()
        if log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
             errors['log_level'] = ["Invalid log level selected."]
        # Validate browser type
        browser_str = str(settings_to_save.get('default_browser','chrome')).lower()
        if browser_str not in ['chrome', 'firefox', 'edge', 'safari']:
             errors['default_browser'] = ["Invalid default browser selected."]


        if errors:
             self.logger.warning(f"Settings validation failed: {errors}")
             # Raise ValidationError for the decorator to catch and display
             error_msg = "Validation errors:\n" + "\n".join([f"- {field}: {err}" for field, errs in errors.items() for err in errs])
             raise ValidationError(error_msg) # Decorator will call view.display_error

        # --- Save individual settings using config manager ---
        # Wrap saving logic in try block although decorator handles file I/O errors
        try:
            success = True
            # Use getattr to avoid repeating; assumes setting_key matches config property name
            sections = {'General': ['log_level', 'log_file'],
                        'Repository': ['type', 'workflows_path', 'credentials_path', 'db_path', 'create_if_missing'],
                        'WebDriver': ['default_browser', 'implicit_wait', 'chrome_driver_path', 'firefox_driver_path', 'edge_driver_path']}

            for section, keys in sections.items():
                for key in keys:
                    # Map UI key to config property if names differ, here they match
                    config_key = key
                    # Handle boolean conversion for saving
                    value_to_save = settings_to_save.get(config_key)
                    if isinstance(value_to_save, bool):
                         value_str = str(value_to_save).lower()
                    else:
                         value_str = str(value_to_save)

                    success &= self.config.save_setting(section, config_key, value_str)

            if not success:
                 # Should not happen if save_setting handles errors well, but check
                 raise ConfigError("Failed to update one or more settings in memory.")

            # --- Write changes to file ---
            if self.config.save_config_to_file(): # This can raise IO/Config errors
                self.logger.info("Settings saved to config.ini.")
                self.view.set_status("Settings saved successfully.")
                # Reload config internally and update view to reflect saved state
                self.load_settings()
            else:
                 # save_config_to_file failed (should raise error caught by decorator)
                 raise ConfigError("Failed to write settings to config.ini file.")

        except Exception as e:
             # Let the decorator handle logging/displaying unexpected errors during save
             raise ConfigError(f"An unexpected error occurred during save: {e}", cause=e) from e


    # No decorator needed for simple reload trigger
    def cancel_changes(self) -> None:
        """Discard changes and reload settings from the file."""
        self.logger.info("Cancelling settings changes, reloading from file.")
        self.load_settings() # Reload settings from file, decorator handles errors