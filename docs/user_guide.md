# AutoQliq User Guide

## Introduction

AutoQliq is a desktop application for automating web tasks. It allows you to create, save, and run sequences of actions that interact with web pages. This guide will help you get started with the application.

## Installation

1. Ensure you have Python 3.8 or higher installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python src/main_ui.py
   ```

## Main Interface

The application has three main tabs:

1. **Workflow Editor**: Create and edit workflows
2. **Workflow Runner**: Run workflows
3. **Settings**: Configure application settings

## Creating a Workflow

1. Go to the **Workflow Editor** tab
2. Click **New Workflow**
3. Enter a name for your workflow
4. Add actions to your workflow:
   - Click **Add Action**
   - Select an action type from the dialog
   - Fill in the required parameters
   - Click **OK**
5. Arrange actions in the desired order using the **Move Up** and **Move Down** buttons
6. Click **Save Workflow** when finished

## Available Action Types

### Basic Actions

- **Navigate**: Go to a specific URL
- **Click**: Click on an element on the page
- **Type**: Enter text into a form field
- **Wait**: Pause execution for a specified time
- **Screenshot**: Take a screenshot of the current page

### Conditional Action

- **Conditional**: Execute different actions based on a condition
  - Specify a condition (element present/not present, variable equals a value)
  - Add actions to execute when the condition is true
  - Add actions to execute when the condition is false

## Managing Credentials

1. Click **Manage** > **Credentials...**
2. Add credentials:
   - Click **Add**
   - Enter a name for the credential set
   - Enter username and password
   - Click **Save**
3. Edit or delete credentials as needed

## Running a Workflow

1. Go to the **Workflow Runner** tab
2. Select a workflow from the list
3. Select credentials if required by the workflow
4. Click **Run Workflow**
5. View the execution log in the log panel
6. Click **Stop Workflow** to cancel execution if needed

## Configuring Settings

1. Go to the **Settings** tab
2. Modify settings as needed:
   - **General**: Log level and log file location
   - **Repository**: Paths for workflows and credentials
   - **WebDriver**: Browser settings and driver paths
3. Click **Save Settings** to apply changes

## Tips and Best Practices

1. **Start Simple**: Begin with basic workflows and gradually add complexity
2. **Use Descriptive Names**: Give your workflows and actions clear, descriptive names
3. **Test Incrementally**: Test your workflow after adding each action
4. **Use Conditional Actions**: Handle different scenarios with conditional actions
5. **Secure Credentials**: Use the credential manager for sensitive information

## Troubleshooting

### Common Issues

1. **Element Not Found**: Check the selector and try using a more specific selector
2. **Browser Not Starting**: Verify WebDriver settings and ensure the browser is installed
3. **Workflow Not Saving**: Check file permissions and paths in settings

### Logs

Execution logs are saved in the `logs/` directory. These can be helpful for diagnosing issues.

## Conclusion

AutoQliq simplifies web automation by providing an intuitive interface for creating and running workflows. With the basic actions and conditional logic, you can automate many common web tasks without writing code.
