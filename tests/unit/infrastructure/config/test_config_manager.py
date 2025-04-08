#!/usr/bin/env python3
"""
Unit tests for config manager in src/infrastructure/config/config_manager.py.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
import configparser
from pathlib import Path
import tempfile

# Import the module under test
from src.infrastructure.config.config_manager import ConfigManager
from src.core.exceptions import ConfigError


class TestConfigManager(unittest.TestCase):
    """
    Test cases for the ConfigManager class.
    
    This test suite verifies that ConfigManager correctly handles loading,
    saving, and accessing configuration settings.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
        
        # Sample config content
        self.sample_config = configparser.ConfigParser()
        self.sample_config["General"] = {
            "app_name": "AutoQliq",
            "version": "1.0.0",
            "log_level": "INFO"
        }
        self.sample_config["UI"] = {
            "theme": "default",
            "font_size": "12"
        }
        self.sample_config["Storage"] = {
            "data_dir": "./data",
            "backup_enabled": "true"
        }
        
        # Write sample config to file
        with open(self.config_path, 'w') as f:
            self.sample_config.write(f)
        
        # Create ConfigManager instance with test config path
        self.config_manager = ConfigManager(str(self.config_path))
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_init_with_existing_file(self):
        """Test initialization with an existing config file."""
        # Verify the config was loaded correctly
        self.assertEqual(self.config_manager.get("General", "app_name"), "AutoQliq")
        self.assertEqual(self.config_manager.get("UI", "theme"), "default")
        self.assertEqual(self.config_manager.get("Storage", "data_dir"), "./data")
    
    def test_init_with_nonexistent_file(self):
        """Test initialization with a nonexistent config file."""
        # Create path to a nonexistent file
        nonexistent_path = Path(self.temp_dir.name) / "nonexistent.ini"
        
        # Create ConfigManager with nonexistent path
        # Should create default config
        config_manager = ConfigManager(str(nonexistent_path))
        
        # Verify a default config was created
        self.assertTrue(os.path.exists(nonexistent_path))
        
        # Verify default values
        # Note: Adjust these assertions based on your actual default values
        self.assertIsNotNone(config_manager.get("General", "app_name"))
        self.assertIsNotNone(config_manager.get("General", "version"))
    
    def test_get_existing_value(self):
        """Test getting an existing config value."""
        # Get an existing value
        value = self.config_manager.get("General", "app_name")
        
        # Verify the value
        self.assertEqual(value, "AutoQliq")
    
    def test_get_nonexistent_section(self):
        """Test getting a value from a nonexistent section."""
        # Try to get a value from a nonexistent section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get("NonexistentSection", "key")
        
        # Verify error message
        self.assertIn("section", str(context.exception).lower())
    
    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key from an existing section."""
        # Try to get a nonexistent key from an existing section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get("General", "nonexistent_key")
        
        # Verify error message
        self.assertIn("key", str(context.exception).lower())
    
    def test_get_with_default(self):
        """Test getting a value with a default fallback."""
        # Get an existing value with a default
        value = self.config_manager.get("General", "app_name", "DefaultName")
        
        # Verify the actual value is returned (not the default)
        self.assertEqual(value, "AutoQliq")
        
        # Get a nonexistent value with a default
        value = self.config_manager.get("General", "nonexistent_key", "DefaultValue")
        
        # Verify the default value is returned
        self.assertEqual(value, "DefaultValue")
    
    def test_get_boolean(self):
        """Test getting a boolean value."""
        # Get a boolean value
        value = self.config_manager.get_boolean("Storage", "backup_enabled")
        
        # Verify the value is a boolean
        self.assertIsInstance(value, bool)
        self.assertTrue(value)
        
        # Add a section with various boolean formats
        self.config_manager.set("BooleanTest", "true_value", "true")
        self.config_manager.set("BooleanTest", "yes_value", "yes")
        self.config_manager.set("BooleanTest", "false_value", "false")
        self.config_manager.set("BooleanTest", "no_value", "no")
        self.config_manager.set("BooleanTest", "invalid_value", "invalid")
        
        # Verify the boolean values
        self.assertTrue(self.config_manager.get_boolean("BooleanTest", "true_value"))
        self.assertTrue(self.config_manager.get_boolean("BooleanTest", "yes_value"))
        self.assertFalse(self.config_manager.get_boolean("BooleanTest", "false_value"))
        self.assertFalse(self.config_manager.get_boolean("BooleanTest", "no_value"))
        
        # Invalid boolean value should raise an error
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get_boolean("BooleanTest", "invalid_value")
        
        # Verify error message
        self.assertIn("boolean", str(context.exception).lower())
        
        # Test nonexistent value with default
        value = self.config_manager.get_boolean("BooleanTest", "nonexistent_key", False)
        self.assertFalse(value)
    
    def test_get_int(self):
        """Test getting an integer value."""
        # Add a section with various integer formats
        self.config_manager.set("IntTest", "valid_int", "123")
        self.config_manager.set("IntTest", "negative_int", "-456")
        self.config_manager.set("IntTest", "invalid_int", "abc")
        
        # Verify the integer values
        self.assertEqual(self.config_manager.get_int("IntTest", "valid_int"), 123)
        self.assertEqual(self.config_manager.get_int("IntTest", "negative_int"), -456)
        
        # Invalid integer value should raise an error
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get_int("IntTest", "invalid_int")
        
        # Verify error message
        self.assertIn("integer", str(context.exception).lower())
        
        # Test nonexistent value with default
        value = self.config_manager.get_int("IntTest", "nonexistent_key", 789)
        self.assertEqual(value, 789)
    
    def test_get_float(self):
        """Test getting a float value."""
        # Add a section with various float formats
        self.config_manager.set("FloatTest", "valid_float", "123.45")
        self.config_manager.set("FloatTest", "negative_float", "-456.78")
        self.config_manager.set("FloatTest", "integer_as_float", "123")
        self.config_manager.set("FloatTest", "invalid_float", "abc")
        
        # Verify the float values
        self.assertEqual(self.config_manager.get_float("FloatTest", "valid_float"), 123.45)
        self.assertEqual(self.config_manager.get_float("FloatTest", "negative_float"), -456.78)
        self.assertEqual(self.config_manager.get_float("FloatTest", "integer_as_float"), 123.0)
        
        # Invalid float value should raise an error
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get_float("FloatTest", "invalid_float")
        
        # Verify error message
        self.assertIn("float", str(context.exception).lower())
        
        # Test nonexistent value with default
        value = self.config_manager.get_float("FloatTest", "nonexistent_key", 789.0)
        self.assertEqual(value, 789.0)
    
    def test_get_section(self):
        """Test getting an entire section."""
        # Get an existing section
        section = self.config_manager.get_section("General")
        
        # Verify the section is a dictionary with the correct values
        self.assertIsInstance(section, dict)
        self.assertEqual(section["app_name"], "AutoQliq")
        self.assertEqual(section["version"], "1.0.0")
        self.assertEqual(section["log_level"], "INFO")
        
        # Try to get a nonexistent section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get_section("NonexistentSection")
        
        # Verify error message
        self.assertIn("section", str(context.exception).lower())
    
    def test_set_value(self):
        """Test setting a config value."""
        # Set a new value in an existing section
        self.config_manager.set("General", "new_key", "new_value")
        
        # Verify the value was set correctly
        self.assertEqual(self.config_manager.get("General", "new_key"), "new_value")
        
        # Set a value in a new section
        self.config_manager.set("NewSection", "key", "value")
        
        # Verify the new section and value were created
        self.assertEqual(self.config_manager.get("NewSection", "key"), "value")
        
        # Update an existing value
        self.config_manager.set("General", "app_name", "UpdatedName")
        
        # Verify the value was updated
        self.assertEqual(self.config_manager.get("General", "app_name"), "UpdatedName")
    
    def test_save(self):
        """Test saving the config to file."""
        # Make some changes to the config
        self.config_manager.set("General", "new_key", "new_value")
        self.config_manager.set("NewSection", "key", "value")
        
        # Save the config
        self.config_manager.save()
        
        # Create a new ConfigManager to load the saved file
        new_config_manager = ConfigManager(str(self.config_path))
        
        # Verify the changes were saved
        self.assertEqual(new_config_manager.get("General", "new_key"), "new_value")
        self.assertEqual(new_config_manager.get("NewSection", "key"), "value")
    
    def test_save_error(self):
        """Test error handling when saving the config."""
        # Mock the open function to simulate a file write error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            # Try to save the config
            with self.assertRaises(ConfigError) as context:
                self.config_manager.save()
            
            # Verify error message
            self.assertIn("save", str(context.exception).lower())
    
    def test_has_section(self):
        """Test checking if a section exists."""
        # Check an existing section
        self.assertTrue(self.config_manager.has_section("General"))
        
        # Check a nonexistent section
        self.assertFalse(self.config_manager.has_section("NonexistentSection"))
    
    def test_has_option(self):
        """Test checking if an option exists in a section."""
        # Check an existing option in an existing section
        self.assertTrue(self.config_manager.has_option("General", "app_name"))
        
        # Check a nonexistent option in an existing section
        self.assertFalse(self.config_manager.has_option("General", "nonexistent_key"))
        
        # Check an option in a nonexistent section
        self.assertFalse(self.config_manager.has_option("NonexistentSection", "key"))
    
    def test_remove_option(self):
        """Test removing an option from a section."""
        # Remove an existing option
        self.config_manager.remove_option("General", "app_name")
        
        # Verify the option was removed
        self.assertFalse(self.config_manager.has_option("General", "app_name"))
        
        # Try to remove a nonexistent option
        with self.assertRaises(ConfigError) as context:
            self.config_manager.remove_option("General", "nonexistent_key")
        
        # Verify error message
        self.assertIn("option", str(context.exception).lower())
        
        # Try to remove an option from a nonexistent section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.remove_option("NonexistentSection", "key")
        
        # Verify error message
        self.assertIn("section", str(context.exception).lower())
    
    def test_remove_section(self):
        """Test removing a section."""
        # Remove an existing section
        self.config_manager.remove_section("UI")
        
        # Verify the section was removed
        self.assertFalse(self.config_manager.has_section("UI"))
        
        # Try to remove a nonexistent section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.remove_section("NonexistentSection")
        
        # Verify error message
        self.assertIn("section", str(context.exception).lower())
    
    def test_get_sections(self):
        """Test getting all section names."""
        # Get all section names
        sections = self.config_manager.get_sections()
        
        # Verify the section names
        self.assertIsInstance(sections, list)
        self.assertIn("General", sections)
        self.assertIn("UI", sections)
        self.assertIn("Storage", sections)
    
    def test_get_options(self):
        """Test getting all option names in a section."""
        # Get all option names in a section
        options = self.config_manager.get_options("General")
        
        # Verify the option names
        self.assertIsInstance(options, list)
        self.assertIn("app_name", options)
        self.assertIn("version", options)
        self.assertIn("log_level", options)
        
        # Try to get options from a nonexistent section
        with self.assertRaises(ConfigError) as context:
            self.config_manager.get_options("NonexistentSection")
        
        # Verify error message
        self.assertIn("section", str(context.exception).lower())
    
    def test_reset(self):
        """Test resetting the config to default values."""
        # Make some changes to the config
        self.config_manager.set("General", "app_name", "ChangedName")
        self.config_manager.set("NewSection", "key", "value")
        
        # Reset the config
        self.config_manager.reset()
        
        # Verify the config was reset to defaults
        # Note: Adjust these assertions based on your actual default values
        self.assertIsNotNone(self.config_manager.get("General", "app_name"))
        self.assertNotEqual(self.config_manager.get("General", "app_name"), "ChangedName")
        self.assertFalse(self.config_manager.has_section("NewSection"))


if __name__ == '__main__':
    unittest.main()