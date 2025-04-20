# Getting Started with AutoQliq

Welcome to AutoQliq! This tutorial will guide you through the basics of creating and running automated workflows.

## What is AutoQliq?

AutoQliq is a powerful automation tool that allows you to create and run workflows to automate web interactions. With AutoQliq, you can:

- Navigate to websites
- Click on elements
- Type text into forms
- Wait for specific conditions
- Take screenshots
- Handle conditional logic
- Loop through repetitive tasks
- Handle errors gracefully
- Create reusable templates

## Installation

To install AutoQliq, follow these steps:

1. Ensure you have Python 3.8 or higher installed
2. Clone the repository: `git clone https://github.com/Phazzie/AUTOQLIQ.git`
3. Navigate to the project directory: `cd AUTOQLIQ`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python src/main.py`

## Quick Start: Using the Default Workflow

AutoQliq comes with a default workflow that demonstrates basic functionality. To run it:

1. Launch AutoQliq
2. Click on the "Workflow Runner" tab
3. Select "default_workflow" from the dropdown
4. Click "Run"

The default workflow will:
1. Navigate to example.com
2. Wait for the page to load
3. Click on a button
4. Take a screenshot of the result
5. Click on another button
6. Take a final screenshot

## Creating Your First Workflow

Let's create a simple workflow to search for something on Google:

1. Launch AutoQliq
2. Click on the "Workflow Editor" tab
3. Click "New Workflow"
4. Enter a name for your workflow (e.g., "Google Search")
5. Click "Create"

Now, let's add actions to our workflow:

### Step 1: Navigate to Google

1. Click "Add Action"
2. Select "Navigate" from the dropdown
3. Enter a name: "Go to Google"
4. Enter URL: "https://www.google.com"
5. Click "Save"

### Step 2: Wait for the page to load

1. Click "Add Action"
2. Select "Wait" from the dropdown
3. Enter a name: "Wait for page"
4. Enter duration: "2" (seconds)
5. Click "Save"

### Step 3: Type in the search box

1. Click "Add Action"
2. Select "Type" from the dropdown
3. Enter a name: "Enter search query"
4. Enter selector: "input[name='q']"
5. Select value type: "text"
6. Enter text: "AutoQliq automation tool"
7. Click "Save"

### Step 4: Click the search button

1. Click "Add Action"
2. Select "Click" from the dropdown
3. Enter a name: "Click search"
4. Enter selector: "input[name='btnK']" (Google's search button)
5. Click "Save"

### Step 5: Wait for results

1. Click "Add Action"
2. Select "Wait" from the dropdown
3. Enter a name: "Wait for results"
4. Enter duration: "3" (seconds)
5. Click "Save"

### Step 6: Take a screenshot

1. Click "Add Action"
2. Select "Screenshot" from the dropdown
3. Enter a name: "Capture results"
4. Enter file path: "screenshots/google_search.png"
5. Click "Save"

### Step 7: Save the workflow

1. Click "Save Workflow"

## Running Your Workflow

To run your newly created workflow:

1. Click on the "Workflow Runner" tab
2. Select your workflow from the dropdown
3. Click "Run"

You should see AutoQliq:
1. Open Google
2. Type your search query
3. Click the search button
4. Wait for results
5. Take a screenshot

The screenshot will be saved in the "screenshots" folder in your AutoQliq directory.

## Advanced Features

### Using Credentials

For websites that require login:

1. Click on the "Credential Manager" tab
2. Click "Add Credential"
3. Enter a name for the credential (e.g., "MyWebsite")
4. Enter username and password
5. Click "Save"

In your workflow, use the "Type" action with value_type set to "credential" and value_key set to "MyWebsite.username" or "MyWebsite.password".

### Conditional Logic

To add conditional logic to your workflow:

1. Click "Add Action"
2. Select "Conditional" from the dropdown
3. Configure the condition (e.g., check if an element exists)
4. Add actions to the "True" branch (executed if condition is true)
5. Add actions to the "False" branch (executed if condition is false)
6. Click "Save"

### Loops

To repeat actions:

1. Click "Add Action"
2. Select "Loop" from the dropdown
3. Choose loop type (count, for_each, or while)
4. Configure loop parameters
5. Add actions to be repeated
6. Click "Save"

### Error Handling

To handle potential errors:

1. Click "Add Action"
2. Select "Error Handling" from the dropdown
3. Add actions to the "Try" section
4. Add actions to the "Catch" section (executed if an error occurs)
5. Click "Save"

## Tips and Best Practices

1. **Start Simple**: Begin with basic workflows and gradually add complexity
2. **Use Descriptive Names**: Give your actions clear names to make workflows easier to understand
3. **Add Wait Actions**: Always add wait actions after navigation or interactions to ensure the page has time to respond
4. **Use Screenshots**: Take screenshots at key points to verify your workflow is working correctly
5. **Test Incrementally**: Run your workflow after adding a few actions to catch issues early
6. **Use Error Handling**: Wrap critical sections in Error Handling actions to make workflows more robust
7. **Create Templates**: For common sequences of actions, create templates to reuse across workflows

## Troubleshooting

### Action Fails to Find Element

If an action fails because it can't find an element:

1. Check the selector is correct
2. Add a longer wait before the action
3. Verify the element exists on the page (use browser developer tools)

### Browser Closes Unexpectedly

If the browser closes during workflow execution:

1. Check for JavaScript errors on the page
2. Ensure you're not navigating away from the domain
3. Add error handling around navigation actions

### Screenshots Not Saving

If screenshots aren't being saved:

1. Verify the screenshots directory exists
2. Check file permissions
3. Use absolute paths instead of relative paths

## Next Steps

Now that you've created your first workflow, try:

1. Creating more complex workflows
2. Using advanced actions like Conditional, Loop, and Error Handling
3. Creating templates for reusable action sequences
4. Scheduling workflows to run automatically
5. Exploring the API to integrate AutoQliq with other tools

Happy automating with AutoQliq!
