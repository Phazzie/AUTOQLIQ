# Example Workflow: Automated Login

This document walks through a simple example of how AutoQliq works in practice, using a login workflow as an example.

## The User's Goal

Imagine you want to automate logging into a website that you visit frequently. You'd like to:
1. Navigate to the website
2. Enter your username
3. Enter your password
4. Click the login button
5. Verify you've successfully logged in

## Creating the Workflow in AutoQliq

### Step 1: Create a New Workflow

The user opens AutoQliq and clicks "New Workflow". They name it "Login to MyWebsite" and provide a description.

### Step 2: Add Actions to the Workflow

The user adds the following actions through the UI:

1. **Navigate Action**
   - Type: Navigate
   - URL: https://example.com/login
   - Name: "Go to login page"

2. **Type Action** (for username)
   - Type: Type
   - Selector: "#username"
   - Value Type: credential
   - Value Key: "mywebsite_username"
   - Name: "Enter username"

3. **Type Action** (for password)
   - Type: Type
   - Selector: "#password"
   - Value Type: credential
   - Value Key: "mywebsite_password"
   - Name: "Enter password"

4. **Click Action**
   - Type: Click
   - Selector: "#login-button"
   - Name: "Click login button"

5. **Conditional Action** (to verify login)
   - Type: Conditional
   - Condition: Element exists
   - Selector: ".welcome-message"
   - True Branch: [Screenshot Action]
   - False Branch: [Error Handling Action]
   - Name: "Verify login success"

   5.1. **Screenshot Action** (in True Branch)
   - Type: Screenshot
   - File Path: "login_success.png"
   - Name: "Capture success screenshot"

   5.2. **Error Handling Action** (in False Branch)
   - Type: ErrorHandling
   - Try Actions: [Wait Action]
   - Catch Actions: [Screenshot Action]
   - Name: "Handle login failure"

      5.2.1. **Wait Action**
      - Type: Wait
      - Duration: 5
      - Name: "Wait and retry"

      5.2.2. **Screenshot Action**
      - Type: Screenshot
      - File Path: "login_failure.png"
      - Name: "Capture failure screenshot"

### Step 3: Save the Workflow

The user clicks "Save Workflow" and the workflow is stored in the database.

## What Happens Behind the Scenes

### When Creating the Workflow:

1. **UI Layer**:
   - Captures the user's input for each action
   - Validates basic input (required fields, etc.)
   - Sends the action data to the Application layer

2. **Application Layer**:
   - Converts UI data to action data dictionaries
   - Calls the WorkflowService to create a new workflow

3. **Core Layer**:
   - The ActionFactory validates each action
   - The WorkflowValidator checks the overall workflow structure
   - The workflow is prepared for storage

4. **Infrastructure Layer**:
   - The WorkflowRepository saves the workflow to the database

### When Running the Workflow:

1. **UI Layer**:
   - User selects the workflow and clicks "Run"
   - UI calls the Application layer to execute the workflow

2. **Application Layer**:
   - WorkflowService retrieves the workflow
   - Passes it to the Core layer for execution

3. **Core Layer**:
   - WorkflowRunner loads the workflow
   - For each action:
     - ActionFactory creates the appropriate action object
     - The action is executed
     - Results are collected

4. **Infrastructure Layer**:
   - WebDriver interacts with the browser
   - CredentialRepository provides secure access to credentials
   - Screenshots are saved to disk

5. **Results Flow Back**:
   - Each action returns a success/failure result
   - Results are aggregated by the WorkflowRunner
   - The final result is passed back to the Application layer
   - The UI displays the results to the user

## The Data Transformation

Let's look at how a single action (the Click Action) transforms through the system:

1. **User Input (UI Form)**:
   ```
   Action Type: Click
   Selector: #login-button
   Name: Click login button
   ```

2. **Action Data Dictionary**:
   ```json
   {
     "type": "Click",
     "selector": "#login-button",
     "name": "Click login button"
   }
   ```

3. **Action Object**:
   ```python
   ClickAction(
     selector="#login-button",
     name="Click login button"
   )
   ```

4. **Execution Result**:
   ```python
   ActionResult(
     success=True,
     message="Successfully clicked element with selector: #login-button",
     action_name="Click login button",
     action_type="Click"
   )
   ```

5. **UI Display**:
   ```
   ✅ Click login button: Successfully clicked element with selector: #login-button
   ```

## Benefits of the Architecture

This layered approach with SOLID principles provides several benefits:

1. **Extensibility**: New action types can be added without changing existing code
2. **Testability**: Each component can be tested in isolation
3. **Maintainability**: Changes in one layer don't affect others
4. **Security**: Credentials are handled securely in the infrastructure layer
5. **Usability**: Complex automation logic is hidden behind a simple UI

The recent refactoring of the ActionFactory further improves these benefits by making the code more modular and focused on single responsibilities.
