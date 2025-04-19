# AutoQliq Configuration Guide

## Overview

AutoQliq uses a simple configuration system based on an INI file (`config.ini`) to store application settings. This guide explains the available configuration options and how to modify them.

## Configuration File Location

The configuration file is located in the root directory of the application:

```
config.ini
```

If this file doesn't exist, a default configuration file will be created automatically when the application starts.

## Configuration Sections

The configuration file is divided into several sections:

### General

```ini
[General]
log_level = INFO
log_file = autoqliq_app.log
```

- `log_level`: Sets the logging level. Valid values are DEBUG, INFO, WARNING, ERROR, CRITICAL.
- `log_file`: The name of the log file where application logs are stored.

### Repository

```ini
[Repository]
workflows_path = workflows
credentials_path = credentials.json
```

- `workflows_path`: The directory where workflow files are stored.
- `credentials_path`: The file where credentials are stored.

### WebDriver

```ini
[WebDriver]
default_browser = chrome
chrome_driver_path = 
firefox_driver_path = 
edge_driver_path = 
implicit_wait = 5
```

- `default_browser`: The default browser to use for automation. Valid values are chrome, firefox, edge, safari.
- `*_driver_path`: Optional paths to WebDriver executables. If left empty, Selenium Manager will attempt to find or download the appropriate driver.
- `implicit_wait`: The default implicit wait time in seconds for WebDriver operations.

### Security

```ini
[Security]
password_hash_method = pbkdf2:sha256:600000
password_salt_length = 16
```

- `password_hash_method`: The method used to hash passwords.
- `password_salt_length`: The length of the salt used for password hashing.

## Modifying Configuration

There are two ways to modify the configuration:

### Using the Settings UI

1. Open the application
2. Go to the "Settings" tab
3. Modify the settings as needed
4. Click "Save Settings"

### Editing the Configuration File Directly

1. Open `config.ini` in a text editor
2. Modify the settings as needed
3. Save the file
4. Restart the application for the changes to take effect

## Default Values

If a configuration option is missing or invalid, the application will use the following default values:

- `log_level`: INFO
- `log_file`: autoqliq_app.log
- `workflows_path`: workflows
- `credentials_path`: credentials.json
- `default_browser`: chrome
- `implicit_wait`: 5
- `password_hash_method`: pbkdf2:sha256:600000
- `password_salt_length`: 16

## Best Practices

1. **Use the Settings UI**: Whenever possible, use the Settings tab in the application to modify settings to ensure proper validation.
2. **Backup Your Configuration**: Before making significant changes, back up your configuration file.
3. **Check Logs**: If you encounter issues after changing configuration, check the application logs for error messages.
4. **WebDriver Paths**: Only specify WebDriver paths if you need to use a specific version. Otherwise, leave them blank to use Selenium Manager.
