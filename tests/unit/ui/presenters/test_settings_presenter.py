"""Tests for the SettingsPresenter.

This module tests the SettingsPresenter implementation.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
from typing import Dict, Any

from src.ui.presenters.settings_presenter import SettingsPresenter
from src.ui.interfaces.view_interfaces import ISettingsView
from src.core.exceptions import ValidationError, ConfigError

class TestSettingsPresenter(unittest.TestCase):
    """Test case for SettingsPresenter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = MagicMock()
        self.view = MagicMock(spec=ISettingsView)
        
        self.presenter = SettingsPresenter(self.config_manager)
        self.presenter.set_view(self.view)
    
    def test_initialize(self):
        """Test presenter initialization."""
        # Initialize presenter
        self.presenter.initialize()
        
        # Check that view handlers were bound
        self.view.bind_handlers.assert_called_once()
        
        # Check that settings were loaded
        self.view.display_settings.assert_called_once()
    
    def test_load_settings(self):
        """Test loading settings."""
        # Set up config manager to return values
        self.config_manager.window_title = "Test Title"
        self.config_manager.window_geometry = "800x600"
        
        # Load settings
        self.presenter.load_settings()
        
        # Check that settings were displayed
        self.view.display_settings.assert_called_once()
        settings = self.view.display_settings.call_args[0][0]
        self.assertEqual(settings["window_title"], "Test Title")
        self.assertEqual(settings["window_geometry"], "800x600")
    
    def test_save_settings_success(self):
        """Test saving settings successfully."""
        # Set up view to return valid settings
        self.view.get_settings.return_value = {
            "window_title": "Test Title",
            "window_geometry": "800x600",
            "browser_type": "chrome",
            "page_load_timeout": 30,
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "workflows",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Mock os.path.exists to return True for all paths
        with patch('os.path.exists', return_value=True):
            # Mock os.access to return True for all paths
            with patch('os.access', return_value=True):
                # Save settings
                self.presenter.on_save_settings()
        
        # Check that settings were saved to config manager
        self.assertEqual(self.config_manager.window_title, "Test Title")
        self.assertEqual(self.config_manager.window_geometry, "800x600")
        
        # Check that config was saved to file
        self.config_manager.save_config_to_file.assert_called_once()
        
        # Check that success message was shown
        self.view.show_info.assert_called_once()
    
    def test_save_settings_validation_error(self):
        """Test saving settings with validation error."""
        # Set up view to return invalid settings
        self.view.get_settings.return_value = {
            "window_title": "Test Title",
            "window_geometry": "invalid",  # Invalid geometry
            "browser_type": "chrome",
            "page_load_timeout": -1,  # Invalid timeout
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "workflows",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Save settings
        self.presenter.on_save_settings()
        
        # Check that error was shown
        self.view.show_error.assert_called_once()
        
        # Check that config was not saved to file
        self.config_manager.save_config_to_file.assert_not_called()
    
    def test_reset_settings(self):
        """Test resetting settings to defaults."""
        # Set up view to confirm reset
        self.view.confirm_action.return_value = True
        
        # Reset settings
        self.presenter.on_reset_settings()
        
        # Check that default settings were displayed
        self.view.display_settings.assert_called_with(self.presenter._default_settings)
    
    def test_reset_settings_cancelled(self):
        """Test cancelling reset settings."""
        # Set up view to cancel reset
        self.view.confirm_action.return_value = False
        
        # Reset settings
        self.presenter.on_reset_settings()
        
        # Check that settings were not displayed
        self.view.display_settings.assert_not_called()
    
    def test_validate_settings_valid(self):
        """Test validating valid settings."""
        # Valid settings
        settings = {
            "window_title": "Test Title",
            "window_geometry": "800x600",
            "browser_type": "chrome",
            "page_load_timeout": 30,
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "workflows",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Mock os.path.exists to return True for all paths
        with patch('os.path.exists', return_value=True):
            # Validate settings
            self.presenter._validate_settings(settings)
            # No exception should be raised
    
    def test_validate_settings_invalid_geometry(self):
        """Test validating settings with invalid geometry."""
        # Settings with invalid geometry
        settings = {
            "window_title": "Test Title",
            "window_geometry": "invalid",
            "browser_type": "chrome",
            "page_load_timeout": 30,
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "workflows",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Validate settings
        with self.assertRaises(ValidationError):
            self.presenter._validate_settings(settings)
    
    def test_validate_settings_invalid_timeout(self):
        """Test validating settings with invalid timeout."""
        # Settings with invalid timeout
        settings = {
            "window_title": "Test Title",
            "window_geometry": "800x600",
            "browser_type": "chrome",
            "page_load_timeout": -1,
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "workflows",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Validate settings
        with self.assertRaises(ValidationError):
            self.presenter._validate_settings(settings)
    
    def test_validate_settings_nonexistent_path(self):
        """Test validating settings with nonexistent path."""
        # Settings with nonexistent path
        settings = {
            "window_title": "Test Title",
            "window_geometry": "800x600",
            "browser_type": "chrome",
            "page_load_timeout": 30,
            "implicit_wait": 10,
            "repository_type": "file_system",
            "workflows_path": "nonexistent/path",
            "credentials_path": "credentials",
            "log_level": "INFO",
            "log_file": "autoqliq.log"
        }
        
        # Mock os.path.exists to return False for nonexistent path
        def mock_exists(path):
            return path != "nonexistent/path" and path != "nonexistent"
        
        with patch('os.path.exists', side_effect=mock_exists):
            # Validate settings
            with self.assertRaises(ValidationError):
                self.presenter._validate_settings(settings)

if __name__ == "__main__":
    unittest.main()
