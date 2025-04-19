"""Tests for the SettingsView."""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the base test class
from tests.ui_testing.ui_test_base import UITestBase

# Import the view to test
from src.ui.views.settings_view import SettingsView
from src.ui.presenters.settings_presenter import SettingsPresenter


class TestSettingsView(UITestBase):
    """Test cases for the SettingsView."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Create a mock presenter
        self.mock_presenter = self.create_mock_presenter(SettingsPresenter)
        
        # Create the view
        self.view = SettingsView(self.root, self.mock_presenter)
    
    def test_initialization(self):
        """Test that the view initializes correctly."""
        # Check that the view has the expected title
        self.assertEqual(self.view.title, "Settings")
        
        # Check that the presenter is set
        self.assertEqual(self.view.presenter, self.mock_presenter)
        
        # Check that the setting variables are created
        expected_settings = [
            "log_level", "log_file",
            "workflows_path", "credentials_path",
            "default_browser", "implicit_wait",
            "chrome_driver_path", "firefox_driver_path", "edge_driver_path"
        ]
        
        for setting in expected_settings:
            self.assertIn(setting, self.view.setting_vars)
    
    def test_get_settings_values(self):
        """Test getting settings values from the view."""
        # Set some values in the view
        self.view.setting_vars["log_level"].set("DEBUG")
        self.view.setting_vars["workflows_path"].set("/path/to/workflows")
        self.view.setting_vars["default_browser"].set("firefox")
        
        # Get the settings values
        settings = self.view.get_settings_values()
        
        # Check that the values are correct
        self.assertEqual(settings["log_level"], "DEBUG")
        self.assertEqual(settings["workflows_path"], "/path/to/workflows")
        self.assertEqual(settings["default_browser"], "firefox")
    
    def test_set_settings_values(self):
        """Test setting settings values in the view."""
        # Create a settings dictionary
        settings = {
            "log_level": "INFO",
            "log_file": "app.log",
            "workflows_path": "/path/to/workflows",
            "credentials_path": "/path/to/credentials.json",
            "default_browser": "chrome",
            "implicit_wait": "5",
            "chrome_driver_path": "/path/to/chromedriver",
            "firefox_driver_path": "",
            "edge_driver_path": ""
        }
        
        # Set the settings values
        self.view.set_settings_values(settings)
        
        # Check that the values are set correctly
        self.assertEqual(self.view.setting_vars["log_level"].get(), "INFO")
        self.assertEqual(self.view.setting_vars["log_file"].get(), "app.log")
        self.assertEqual(self.view.setting_vars["workflows_path"].get(), "/path/to/workflows")
        self.assertEqual(self.view.setting_vars["credentials_path"].get(), "/path/to/credentials.json")
        self.assertEqual(self.view.setting_vars["default_browser"].get(), "chrome")
        self.assertEqual(self.view.setting_vars["implicit_wait"].get(), "5")
        self.assertEqual(self.view.setting_vars["chrome_driver_path"].get(), "/path/to/chromedriver")
        self.assertEqual(self.view.setting_vars["firefox_driver_path"].get(), "")
        self.assertEqual(self.view.setting_vars["edge_driver_path"].get(), "")
    
    def test_on_save_settings(self):
        """Test saving settings."""
        # Set some values in the view
        self.view.setting_vars["log_level"].set("DEBUG")
        self.view.setting_vars["workflows_path"].set("/path/to/workflows")
        self.view.setting_vars["default_browser"].set("firefox")
        
        # Call the save method
        self.view.on_save_settings()
        
        # Check that the presenter's save_settings method was called
        self.mock_presenter.save_settings.assert_called_once()
    
    def test_on_cancel_settings(self):
        """Test cancelling settings changes."""
        # Call the cancel method
        self.view.on_cancel_settings()
        
        # Check that the presenter's cancel_changes method was called
        self.mock_presenter.cancel_changes.assert_called_once()
    
    def test_browse_for_path(self):
        """Test browsing for a path."""
        # Mock the filedialog
        with patch('tkinter.filedialog.askdirectory') as mock_askdirectory:
            # Configure the mock
            mock_askdirectory.return_value = "/path/to/directory"
            
            # Call the method
            self.view._browse_for_path("workflows_path", "directory")
            
            # Check that the dialog was shown
            mock_askdirectory.assert_called_once()
            
            # Check that the path was set
            self.assertEqual(self.view.setting_vars["workflows_path"].get(), "/path/to/directory")
    
    def test_browse_for_file(self):
        """Test browsing for a file."""
        # Mock the filedialog
        with patch('tkinter.filedialog.askopenfilename') as mock_askopenfilename:
            # Configure the mock
            mock_askopenfilename.return_value = "/path/to/file.exe"
            
            # Call the method
            self.view._browse_for_path("chrome_driver_path", "open")
            
            # Check that the dialog was shown
            mock_askopenfilename.assert_called_once()
            
            # Check that the path was set
            self.assertEqual(self.view.setting_vars["chrome_driver_path"].get(), "/path/to/file.exe")
    
    def test_set_status(self):
        """Test setting the status message."""
        # Call the method
        self.view.set_status("Settings saved successfully")
        
        # Check that the status label was updated
        self.assertEqual(self.view.status_label["text"], "Settings saved successfully")


if __name__ == "__main__":
    unittest.main()
