# Editing the Default Workflow

AutoQliq comes with a default workflow that demonstrates basic functionality. This guide will show you how to edit this workflow to suit your specific needs.

## Understanding the Default Workflow

The default workflow consists of the following actions:

1. **Navigate to website** - Opens a web browser and navigates to example.com
2. **Wait for page to load** - Pauses for 2 seconds to ensure the page has loaded
3. **Click on first button** - Clicks on an element with the ID "main-button"
4. **Wait for action to complete** - Pauses for 1 second after clicking
5. **Take screenshot of result** - Captures a screenshot of the current page
6. **Click on second button** - Clicks on an element with the ID "secondary-button"
7. **Wait for second action** - Pauses for 1 second after clicking
8. **Take final screenshot** - Captures a final screenshot of the page

## Opening the Default Workflow

1. Launch AutoQliq
2. Click on the "Workflow Editor" tab
3. Select "default_workflow" from the dropdown
4. Click "Load"

You should now see the list of actions in the default workflow.

## Modifying Actions

### Changing the Website URL

1. Click on the "Navigate to website" action in the list
2. Click "Edit"
3. Change the URL from "https://example.com" to your desired website
4. Click "Save"

### Adjusting Wait Times

1. Click on any "Wait" action in the list
2. Click "Edit"
3. Change the duration in seconds
4. Click "Save"

### Updating Element Selectors

1. Click on any "Click" action in the list
2. Click "Edit"
3. Change the selector to match elements on your target website
   - For example, change "#main-button" to ".login-button" or whatever selector matches your target element
4. Click "Save"

### Changing Screenshot Locations

1. Click on any "Screenshot" action in the list
2. Click "Edit"
3. Change the file path to your desired location
   - For example, change "screenshots/result.png" to "screenshots/my_custom_screenshot.png"
4. Click "Save"

## Adding New Actions

To add a new action to the workflow:

1. Click "Add Action" (or "Insert" at a specific position)
2. Select the action type from the dropdown
3. Fill in the required fields
4. Click "Save"

## Removing Actions

To remove an action from the workflow:

1. Click on the action in the list
2. Click "Delete"
3. Confirm the deletion

## Reordering Actions

To change the order of actions:

1. Click on the action in the list
2. Click "Move Up" or "Move Down" to change its position

## Testing Your Changes

After making changes to the workflow:

1. Click "Save Workflow" to save your changes
2. Go to the "Workflow Runner" tab
3. Select your modified workflow
4. Click "Run" to test it

## Common Customizations

### Logging into a Website

To modify the workflow for logging into a website:

1. Change the Navigate action to point to the login page
2. Add Type actions for username and password fields
3. Update the Click action to target the login button
4. Add a Wait action after login to ensure the page loads
5. Take a screenshot to verify successful login

Example:

```
1. Navigate to "https://example.com/login"
2. Wait for 2 seconds
3. Type "your_username" into "#username" field
4. Type "your_password" into "#password" field
5. Click on "#login-button"
6. Wait for 3 seconds
7. Take screenshot "screenshots/login_result.png"
```

### Filling Out a Form

To modify the workflow for filling out a form:

1. Navigate to the form page
2. Add Type actions for each form field
3. Click the submit button
4. Wait for confirmation
5. Take a screenshot of the result

Example:

```
1. Navigate to "https://example.com/form"
2. Wait for 2 seconds
3. Type "John Doe" into "#name" field
4. Type "john@example.com" into "#email" field
5. Type "This is a message" into "#message" field
6. Click on "#submit-button"
7. Wait for 3 seconds
8. Take screenshot "screenshots/form_submission.png"
```

### Extracting Data

To modify the workflow for extracting data from a website:

1. Navigate to the page with data
2. Add actions to navigate to the specific data section
3. Take screenshots of the data
4. Optionally add conditional logic to handle different data states

## Advanced Customization

For more advanced customization, consider:

1. Adding conditional logic to handle different scenarios
2. Using loops to process multiple items
3. Adding error handling to make your workflow more robust
4. Creating templates for reusable parts of your workflow

## Saving Your Customized Workflow

After customizing the default workflow, you might want to save it with a new name:

1. Click "Save As"
2. Enter a new name for your workflow
3. Click "Save"

This preserves the original default workflow while creating your custom version.

## Next Steps

Once you've customized the default workflow, consider:

1. Creating additional workflows for different tasks
2. Scheduling your workflows to run automatically
3. Sharing your workflows with team members
4. Exploring more advanced features of AutoQliq

Happy automating!
