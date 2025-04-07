"""Handles loading and accessing application configuration from config.ini."""

import configparser
import os
import logging
from typing import Literal, Optional, List

# Define allowed repository types
RepositoryType = Literal["file_system", "database"]
# Define allowed browser types (should align with BrowserType enum if possible)
BrowserTypeStr = Literal["chrome", "firefox", "edge", "safari"]

# Default values in case config.ini is missing or incomplete
DEFAULT_CONFIG = {
    'General': {
        'log_level': 'INFO',
        'log_file': 'autoqliq_app.log',
    },
    'Repository': {
        'type': 'file_system',
        'workflows_path': 'workflows',
        'credentials_path': 'credentials.json',
        'create_if_missing': 'true',
        'db_path': 'autoqliq_data.db'
    },
    'WebDriver': {
        'default_browser': 'chrome',
        'chrome_driver_path': '',
        'firefox_driver_path': '',
        'edge_driver_path': '',
        'implicit_wait': '5',
    },
    'Security': {
        'password_hash_method': 'pbkdf2:sha256:600000',
        'password_salt_length': '16'
    }
}

CONFIG_FILE_NAME = "config.ini" # Standard name

class AppConfig:
    """Loads and provides typed access to application configuration settings."""

    def __init__(self, config_file_path: str = CONFIG_FILE_NAME):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config_file_path = config_file_path
        # Use a temporary basic logger until config is loaded
        self._temp_logger = logging.getLogger(__name__)
        self._load_config()
        # Replace temp logger with one configured according to loaded settings
        self.logger = logging.getLogger(__name__)
        try:
             self.logger.setLevel(self.log_level)
        except Exception:
             self.logger.setLevel(logging.INFO) # Fallback

    def _load_config(self):
        """Loads configuration from the INI file, using defaults."""
        self.config = configparser.ConfigParser(interpolation=None) # Re-initialize parser
        self.config.read_dict(DEFAULT_CONFIG) # Set defaults first
        if os.path.exists(self.config_file_path):
            try:
                read_files = self.config.read(self.config_file_path, encoding='utf-8')
                if read_files: self._temp_logger.info(f"Configuration loaded successfully from: {self.config_file_path}")
                else: self._temp_logger.warning(f"Config file found '{self.config_file_path}' but empty/unreadable. Using defaults.")
            except configparser.Error as e: self._temp_logger.error(f"Error parsing config '{self.config_file_path}': {e}. Using defaults.")
            except Exception as e: self._temp_logger.error(f"Error loading config '{self.config_file_path}': {e}. Using defaults.", exc_info=True)
        else:
            self._temp_logger.warning(f"Config file not found: '{self.config_file_path}'. Using default settings.")
            self._create_default_config()

    def reload_config(self):
        """Reloads the configuration from the file."""
        self.logger.info(f"Reloading configuration from {self.config_file_path}")
        self._load_config()
        # Re-apply logger level after reload
        logging.getLogger().setLevel(self.log_level)
        self.logger.setLevel(self.log_level)
        self.logger.info(f"Configuration reloaded. Log level set to {logging.getLevelName(self.log_level)}.")


    def _create_default_config(self):
        """Creates a default config.ini file if it doesn't exist."""
        try:
            # Ensure directory exists if config_file_path includes directories
            config_dir = os.path.dirname(self.config_file_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                self._temp_logger.info(f"Created directory for config file: {config_dir}")

            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                # Write defaults to the file
                temp_config = configparser.ConfigParser(interpolation=None)
                temp_config.read_dict(DEFAULT_CONFIG)
                temp_config.write(configfile)
            self._temp_logger.info(f"Created default config file: {self.config_file_path}")
        except Exception as e:
            self._temp_logger.error(f"Failed to create default config file '{self.config_file_path}': {e}", exc_info=True)


    def _get_value(self, section: str, key: str, fallback_override: Optional[str] = None) -> Optional[str]:
        """Helper to get value, using internal defaults as ultimate fallback."""
        try:
             if not self.config.has_section(section):
                  self.logger.warning(f"Config section [{section}] not found. Returning fallback '{fallback_override}'.")
                  return fallback_override
             # Use fallback kwarg in get()
             return self.config.get(section, key, fallback=fallback_override)
        except (configparser.NoOptionError):
            self.logger.warning(f"Config key [{section}]{key} not found. Returning fallback '{fallback_override}'.")
            return fallback_override
        except Exception as e:
            self.logger.error(f"Error reading config [{section}]{key}: {e}. Returning fallback '{fallback_override}'.")
            return fallback_override


    def save_setting(self, section: str, key: str, value: str) -> bool:
        """Saves a single setting to the config object (does not write to file yet)."""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value)) # Ensure value is string
            self.logger.info(f"Config setting updated in memory: [{section}]{key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update setting [{section}]{key} in memory: {e}")
            return False

    def save_config_to_file(self) -> bool:
        """Writes the current config object state back to the INI file."""
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved successfully to: {self.config_file_path}")
            # Optionally reload after saving to ensure consistency?
            # self.reload_config()
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration file '{self.config_file_path}': {e}", exc_info=True)
            return False

    # --- Typed Property Accessors ---

    @property
    def log_level(self) -> int:
        level_str = self._get_value('General', 'log_level', DEFAULT_CONFIG['General']['log_level']).upper()
        level = getattr(logging, level_str, logging.INFO)
        if not isinstance(level, int):
             self.logger.warning(f"Invalid log level '{level_str}' in config. Defaulting to INFO.")
             return logging.INFO
        return level

    @property
    def log_file(self) -> str:
        return self._get_value('General', 'log_file', DEFAULT_CONFIG['General']['log_file'])

    @property
    def repository_type(self) -> RepositoryType:
        repo_type = self._get_value('Repository', 'type', DEFAULT_CONFIG['Repository']['type']).lower()
        if repo_type not in ('file_system', 'database'):
            self.logger.warning(f"Invalid repository type '{repo_type}'. Defaulting to '{DEFAULT_CONFIG['Repository']['type']}'.")
            return DEFAULT_CONFIG['Repository']['type'] # type: ignore
        return repo_type # type: ignore

    @property
    def workflows_path(self) -> str:
        # Return path based on type, falling back to defaults if key missing
        repo_type = self.repository_type
        # Determine key and fallback based on repo type
        key = 'db_path' if repo_type == 'database' else 'workflows_path'
        fallback = DEFAULT_CONFIG['Repository'][key]
        return self._get_value('Repository', key, fallback)

    @property
    def credentials_path(self) -> str:
        repo_type = self.repository_type
        key = 'db_path' if repo_type == 'database' else 'credentials_path'
        fallback = DEFAULT_CONFIG['Repository'][key]
        return self._get_value('Repository', key, fallback)

    @property
    def db_path(self) -> str:
         return self._get_value('Repository', 'db_path', DEFAULT_CONFIG['Repository']['db_path'])

    @property
    def repo_create_if_missing(self) -> bool:
        try:
            # Use getboolean which handles true/false, yes/no, 1/0
            return self.config.getboolean('Repository', 'create_if_missing', fallback=True)
        except ValueError:
            fallback = DEFAULT_CONFIG['Repository']['create_if_missing'].lower() == 'true'
            self.logger.warning(f"Invalid boolean value for 'create_if_missing'. Using default: {fallback}.")
            return fallback

    @property
    def default_browser(self) -> BrowserTypeStr:
        browser = self._get_value('WebDriver', 'default_browser', DEFAULT_CONFIG['WebDriver']['default_browser']).lower()
        # Validate against allowed types
        allowed_browsers: List[BrowserTypeStr] = ["chrome", "firefox", "edge", "safari"]
        if browser not in allowed_browsers:
             default_b = DEFAULT_CONFIG['WebDriver']['default_browser']
             self.logger.warning(f"Invalid default browser '{browser}'. Defaulting to '{default_b}'.")
             return default_b # type: ignore
        return browser # type: ignore

    def get_driver_path(self, browser_type: str) -> Optional[str]:
        """Gets the configured path for a specific browser driver, or None."""
        key = f"{browser_type.lower()}_driver_path"
        # Check if key exists before getting, return None if it doesn't
        if self.config.has_option('WebDriver', key):
            path = self.config.get('WebDriver', key)
            return path if path else None # Return None if empty string in config
        return None

    @property
    def implicit_wait(self) -> int:
        try:
            wait_str = self._get_value('WebDriver', 'implicit_wait', DEFAULT_CONFIG['WebDriver']['implicit_wait'])
            wait = int(wait_str or '0') # Default to 0 if empty string
            return max(0, wait) # Ensure non-negative
        except (ValueError, TypeError):
            fallback_wait = int(DEFAULT_CONFIG['WebDriver']['implicit_wait'])
            self.logger.warning(f"Invalid integer value for 'implicit_wait'. Using default: {fallback_wait}.")
            return fallback_wait

    @property
    def password_hash_method(self) -> str:
        return self._get_value('Security', 'password_hash_method', DEFAULT_CONFIG['Security']['password_hash_method'])

    @property
    def password_salt_length(self) -> int:
        try:
            length_str = self._get_value('Security', 'password_salt_length', DEFAULT_CONFIG['Security']['password_salt_length'])
            length = int(length_str or '0') # Default to 0 if empty
            return max(8, length) # Ensure a minimum reasonable salt length (e.g., 8)
        except (ValueError, TypeError):
             fallback_len = int(DEFAULT_CONFIG['Security']['password_salt_length'])
             self.logger.warning(f"Invalid integer value for 'password_salt_length'. Using default: {fallback_len}.")
             return fallback_len


# --- Global Singleton Instance ---
try:
    config = AppConfig()
    # Apply logging level immediately after loading
    logging.getLogger().setLevel(config.log_level) # Set root logger level
    config.logger.info(f"--- Application Configuration Loaded (Level: {logging.getLevelName(config.log_level)}) ---")
    config.logger.info(f"Repository Type: {config.repository_type}")
    if config.repository_type == 'database': config.logger.info(f"Database Path: {config.db_path}")
    else:
        config.logger.info(f"Workflows Path: {config.workflows_path}")
        config.logger.info(f"Credentials Path: {config.credentials_path}")
    config.logger.info(f"Default Browser: {config.default_browser}")
    config.logger.info(f"Implicit Wait: {config.implicit_wait}s")
    config.logger.debug(f"Password Hash Method: {config.password_hash_method}")
except Exception as e:
     logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     logging.critical(f"CRITICAL ERROR: Failed to initialize AppConfig: {e}", exc_info=True)
     raise RuntimeError("Failed to load application configuration. Cannot continue.") from e