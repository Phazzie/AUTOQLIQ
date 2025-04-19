# AutoQliq Workflow Runner Guide

## Overview

The AutoQliq Workflow Runner is responsible for executing workflows by running a sequence of actions in a web browser. This guide explains how the workflow runner works and how to use it effectively.

## Architecture

The workflow runner is implemented using a layered architecture:

1. **UI Layer**: `WorkflowRunnerView` and `WorkflowRunnerPresenter`
2. **Service Layer**: `WorkflowService` and `WorkflowExecutor`
3. **Core Layer**: `WorkflowRunner`

### Key Components

- **WorkflowRunnerPresenter**: Handles UI interactions and delegates to the service layer
- **WorkflowService**: Provides high-level workflow operations
- **WorkflowExecutor**: Orchestrates the execution of a workflow
- **WorkflowRunner**: Executes individual actions in sequence

## Running a Workflow

### Using the UI

1. Go to the **Workflow Runner** tab
2. Select a workflow from the dropdown
3. (Optional) Select credentials if required by the workflow
4. (Optional) Select a browser type
5. Click **Run Workflow**
6. View the execution log in the log panel
7. (Optional) Click **Stop Workflow** to cancel execution

### Programmatically

```python
# Create a stop event for cancellation
stop_event = threading.Event()

# Run the workflow
execution_log = workflow_service.run_workflow(
    name="my_workflow",
    credential_name="my_credentials",  # Optional
    browser_type=BrowserType.CHROME,
    log_callback=print,  # Optional
    stop_event=stop_event  # Optional
)

# Check the result
if execution_log["final_status"] == "SUCCESS":
    print("Workflow completed successfully!")
else:
    print(f"Workflow failed: {execution_log.get('error_message')}")
```

## Execution Flow

1. **Initialization**:
   - Load the workflow from the repository
   - Create a web driver instance
   - Initialize the workflow runner

2. **Execution**:
   - Execute actions sequentially
   - For each action:
     - Validate the action
     - Execute the action
     - Check for cancellation requests
     - Log the result

3. **Cleanup**:
   - Dispose of the web driver
   - Log the final result
   - Update the UI

## Error Handling

The workflow runner handles several types of errors:

- **ValidationError**: Occurs when an action fails validation
- **ActionError**: Occurs when an action fails during execution
- **WebDriverError**: Occurs when there's an issue with the web driver
- **CredentialError**: Occurs when there's an issue with credentials
- **WorkflowError**: General workflow-related errors

When an error occurs:

1. The error is logged
2. Execution is stopped
3. Resources are cleaned up
4. The error is reported to the user

## Cancellation

Workflows can be cancelled at any time by:

1. Clicking the **Stop Workflow** button in the UI
2. Setting the stop event programmatically

The cancellation process:

1. Sets a stop event
2. The workflow runner checks for this event between actions
3. If the event is set, execution is gracefully stopped
4. Resources are cleaned up
5. A "STOPPED" status is reported

## Execution Log

The workflow runner produces a detailed execution log with:

- Workflow name
- Start and end times
- Duration
- Final status
- Action results
- Error messages (if any)
- Summary statistics

Example:

```json
{
  "workflow_name": "Login Workflow",
  "start_time_iso": "2023-06-01T12:00:00",
  "end_time_iso": "2023-06-01T12:00:10",
  "duration_seconds": 10.0,
  "final_status": "SUCCESS",
  "action_results": [
    {
      "action_name": "Navigate to Login Page",
      "action_type": "Navigate",
      "success": true,
      "message": "Navigated to https://example.com/login"
    },
    {
      "action_name": "Enter Username",
      "action_type": "Type",
      "success": true,
      "message": "Typed text into #username"
    }
  ],
  "summary": {
    "total_actions": 2,
    "success_count": 2,
    "failure_count": 0
  }
}
```

## Best Practices

1. **Use Descriptive Action Names**: Give your actions clear, descriptive names to make logs easier to understand
2. **Handle Conditions**: Use conditional actions to handle different scenarios
3. **Add Wait Actions**: Add wait actions when needed to ensure the page has time to load
4. **Use Credentials**: Store sensitive information in credentials rather than hardcoding them
5. **Check Logs**: Review execution logs to diagnose issues

## Troubleshooting

### Common Issues

1. **Element Not Found**: Check the selector and try using a more specific selector
2. **Browser Not Starting**: Verify WebDriver settings and ensure the browser is installed
3. **Workflow Hangs**: Add appropriate wait actions or increase implicit wait time
4. **Credentials Not Working**: Verify credential values and ensure they're being used correctly

### Debugging Tips

1. **Check Logs**: Review the execution log for error messages
2. **Add Screenshots**: Add screenshot actions at key points to capture the state of the browser
3. **Use Conditional Actions**: Add conditional actions to handle different scenarios
4. **Simplify**: Start with a simple workflow and add complexity incrementally
