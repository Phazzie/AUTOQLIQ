#!/usr/bin/env python3
"""
Unit tests for AppConfig class in src/config.py.
"""

import configparser
import logging
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Import the module under test
from src.config import AppConfig, DEFAULT_CONFIG

class TestAppConfig(unittest.TestCase):
    """
    Test cases for the AppConfig class to ensure it follows SOLID, KISS, and DRY principles.
    
    These tests cover the 7 main responsibilities of AppConfig:
    1. Loading configuration from an INI file
    2. Providing default values for missing configurations
    3. Saving configuration changes
    4. Type-safe property accessors
    5. Validation of configuration values
    6. Logging configuration state
    7. Global singleton instance management
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_config_path = os.path.join(self.temp_dir.name, 'test_config.ini')
        
        # Create a basic config
        self.test_config = configparser.ConfigParser()
        self.test_config.read_dict(DEFAULT_CONFIG)
        
        # Set up a logger mock
        self.logger_patcher = patch('logging.getLogger')
        self.mock_logger = self.logger_patcher.start().return_value
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.logger_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_init_with_nonexistent_file(self):
        """Test initialization with a non-existent config file."""
        non_existent_path = os.path.join(self.temp_dir.name, 'nonexistent.ini')
        
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as mock_file:
                config = AppConfig(non_existent_path)
                
                # Check if default config is created
                mock_file.assert_called_once_with(non_existent_path, 'w', encoding='utf-8')
                
                # Verify defaults are used
                self.assertEqual(config.log_level, logging.INFO)
                self.assertEqual(config.repository_type, 'file_system')
    
    def test_init_with_existing_file(self):
        """Test initialization with an existing config file."""
        # Create a test config file
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        # Initialize with the existing file
        config = AppConfig(self.temp_config_path)
        
        # Verify config is loaded
        self.assertEqual(config.log_level, logging.INFO)
        self.assertEqual(config.repository_type, 'file_system')
    
    def test_reload_config(self):
        """Test reloading the configuration."""
        # Create initial config
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        # Initialize with the existing file
        config = AppConfig(self.temp_config_path)
        
        # Modify the config file
        self.test_config.set('General', 'log_level', 'DEBUG')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        # Reload the config
        config.reload_config()
        
        # Verify the new value is loaded
        self.assertEqual(config.log_level, logging.DEBUG)
    
    def test_save_setting_and_save_to_file(self):
        """Test saving settings to memory and then to file."""
        # Initialize with a non-existent file
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as mock_file:
                config = AppConfig(self.temp_config_path)
        
        # Save a setting to memory
        self.assertTrue(config.save_setting('General', 'log_level', 'DEBUG'))
        
        # Save to file
        with patch('builtins.open', mock_open()) as mock_file:
            self.assertTrue(config.save_config_to_file())
            mock_file.assert_called_once_with(self.temp_config_path, 'w', encoding='utf-8')
    
    def test_log_level_property(self):
        """Test the log_level property with valid and invalid values."""
        # Test with valid value
        self.test_config.set('General', 'log_level', 'DEBUG')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.log_level, logging.DEBUG)
        
        # Test with invalid value
        self.test_config.set('General', 'log_level', 'INVALID_LEVEL')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.log_level, logging.INFO)  # Should default to INFO
    
    def test_repository_type_property(self):
        """Test the repository_type property with valid and invalid values."""
        # Test with valid value
        self.test_config.set('Repository', 'type', 'database')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.repository_type, 'database')
        
        # Test with invalid value
        self.test_config.set('Repository', 'type', 'invalid_type')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.repository_type, 'file_system')  # Should default to file_system
    
    def test_paths_properties(self):
        """Test the various path properties."""
        # Set up test config
        self.test_config.set('Repository', 'type', 'file_system')
        self.test_config.set('Repository', 'workflows_path', 'custom_workflows')
        self.test_config.set('Repository', 'credentials_path', 'custom_credentials.json')
        self.test_config.set('Repository', 'db_path', 'custom_db.db')
        
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        
        # Test with file_system type
        self.assertEqual(config.workflows_path, 'custom_workflows')
        self.assertEqual(config.credentials_path, 'custom_credentials.json')
        
        # Test with database type
        self.test_config.set('Repository', 'type', 'database')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.workflows_path, 'custom_db.db')
        self.assertEqual(config.credentials_path, 'custom_db.db')
        self.assertEqual(config.db_path, 'custom_db.db')
    
    def test_repo_create_if_missing_property(self):
        """Test the repo_create_if_missing property."""
        # Test with true value
        self.test_config.set('Repository', 'create_if_missing', 'true')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertTrue(config.repo_create_if_missing)
        
        # Test with false value
        self.test_config.set('Repository', 'create_if_missing', 'false')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertFalse(config.repo_create_if_missing)
        
        # Test with invalid value
        self.test_config.set('Repository', 'create_if_missing', 'not_a_boolean')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertTrue(config.repo_create_if_missing)  # Should default to True
    
    def test_default_browser_property(self):
        """Test the default_browser property."""
        # Test with valid value
        self.test_config.set('WebDriver', 'default_browser', 'firefox')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.default_browser, 'firefox')
        
        # Test with invalid value
        self.test_config.set('WebDriver', 'default_browser', 'invalid_browser')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.default_browser, 'chrome')  # Should default to chrome
    
    def test_get_driver_path(self):
        """Test the get_driver_path method."""
        # Set up test config
        self.test_config.set('WebDriver', 'chrome_driver_path', '/path/to/chromedriver')
        self.test_config.set('WebDriver', 'firefox_driver_path', '')  # Empty path
        
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        
        # Test with existing path
        self.assertEqual(config.get_driver_path('chrome'), '/path/to/chromedriver')
        
        # Test with empty path
        self.assertIsNone(config.get_driver_path('firefox'))
        
        # Test with non-existent path
        self.assertIsNone(config.get_driver_path('edge'))
    
    def test_implicit_wait_property(self):
        """Test the implicit_wait property."""
        # Test with valid value
        self.test_config.set('WebDriver', 'implicit_wait', '10')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.implicit_wait, 10)
        
        # Test with invalid value
        self.test_config.set('WebDriver', 'implicit_wait', 'not_a_number')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.implicit_wait, 5)  # Should default to 5
        
        # Test with negative value
        self.test_config.set('WebDriver', 'implicit_wait', '-5')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.implicit_wait, 0)  # Should be non-negative
    
    def test_password_hash_method_property(self):
        """Test the password_hash_method property."""
        # Test with custom value
        self.test_config.set('Security', 'password_hash_method', 'pbkdf2:sha512:100000')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.password_hash_method, 'pbkdf2:sha512:100000')
    
    def test_password_salt_length_property(self):
        """Test the password_salt_length property."""
        # Test with valid value
        self.test_config.set('Security', 'password_salt_length', '32')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.password_salt_length, 32)
        
        # Test with invalid value
        self.test_config.set('Security', 'password_salt_length', 'not_a_number')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.password_salt_length, 16)  # Should default to 16
        
        # Test with value below minimum
        self.test_config.set('Security', 'password_salt_length', '4')
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            self.test_config.write(f)
        
        config = AppConfig(self.temp_config_path)
        self.assertEqual(config.password_salt_length, 8)  # Should enforce minimum of 8
    
    def test_singleton_pattern(self):
        """Test the global singleton instance pattern."""
        # This test requires patching the global config instance
        with patch('src.config.config', spec=AppConfig) as mock_config:
            with patch('src.config.AppConfig', return_value=mock_config) as mock_app_config:
                # Simulate importing the module to create the singleton
                import importlib
                importlib.reload(importlib.import_module('src.config'))
                
                # Verify AppConfig was called once
                mock_app_config.assert_called_once()
                
    def test_error_handling_during_init(self):
        """Test error handling during initialization."""
        # Test handling of critical errors
        with patch('src.config.AppConfig._load_config', side_effect=Exception('Test error')):
            with patch('logging.basicConfig') as mock_basic_config:
                with patch('logging.critical') as mock_critical:
                    with self.assertRaises(RuntimeError):
                        AppConfig(self.temp_config_path)
                    
                    # Verify logging was configured and critical error was logged
                    mock_basic_config.assert_called_once()
                    mock_critical.assert_called_once()

if __name__ == '__main__':
    unittest.main()