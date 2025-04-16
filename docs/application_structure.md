# AutoQliq Application Structure

## Overview

AutoQliq is a browser automation tool that helps users automate repetitive tasks on websites. Think of it as a "robot" that can click buttons, fill out forms, and navigate websites for you based on a set of instructions you provide.

## Core Components

The application is structured in layers, like a cake, with each layer having a specific responsibility:

```
┌─────────────────────────────────────────┐
│                   UI                    │
│  (What the user sees and interacts with)│
├─────────────────────────────────────────┤
│              Application               │
│  (Coordinates between UI and core logic)│
├─────────────────────────────────────────┤
│                 Core                   │
│  (The brain - workflows and actions)    │
├─────────────────────────────────────────┤
│             Infrastructure             │
│  (Tools for storage and web automation) │
└─────────────────────────────────────────┘
```

### 1. UI Layer

This is what users see and interact with. It includes:

- **Views**: The screens and forms users interact with
- **Presenters**: Connect the UI to the application logic
- **Dialogs**: Pop-up windows for user input

Think of this layer as the "dashboard" of a car - it's what you touch and see, but it doesn't actually make the car move.

### 2. Application Layer

This layer coordinates between what the user wants and how the system does it:

- **Services**: Handle specific features like running workflows or managing credentials
- **DTOs**: Simple data containers that move between layers

Think of this as the "steering wheel and pedals" - they translate your intentions into actions the car can understand.

### 3. Core Layer

This is the "brain" of the application:

- **Workflows**: A sequence of actions to perform
- **Actions**: Individual operations like clicking or typing
- **Factories**: Create the right type of actions based on user input
- **Validators**: Ensure everything is set up correctly

Think of this as the "engine" of the car - it's what actually makes things happen.

### 4. Infrastructure Layer

This layer handles the technical details:

- **WebDrivers**: Control the browser (like Selenium)
- **Repositories**: Store and retrieve data
- **Error Handlers**: Deal with problems that occur

Think of this as the "wheels, fuel system, and transmission" - the parts that connect to the real world.

## How It All Works Together

Here's how the application works in simple terms:

1. **User Creates a Workflow**:
   - User opens the application and uses the UI to create a new workflow
   - They add actions like "go to website", "click this button", "type this text"
   - The UI sends this information to the Application layer

2. **Saving the Workflow**:
   - The Application layer asks the Core layer to validate the workflow
   - If valid, it's passed to the Infrastructure layer to be saved
   - The workflow is stored in a database or file

3. **Running a Workflow**:
   - User selects a saved workflow and clicks "Run"
   - The UI tells the Application layer to run the workflow
   - The Application layer retrieves the workflow and passes it to the Core layer

4. **Executing Actions**:
   - The Core layer processes each action in the workflow
   - For each action, it uses the appropriate Factory to create the action
   - The action is executed using components from the Infrastructure layer
   - Results of each action are collected and reported back

5. **Handling Results**:
   - Success or failure is reported back up through the layers
   - The UI displays the results to the user
   - Any data collected during execution can be saved or displayed

## Key Design Patterns

The application uses several design patterns to keep the code organized:

1. **Model-View-Presenter (MVP)**: Separates the UI from the logic
2. **Factory Pattern**: Creates different types of actions
3. **Repository Pattern**: Handles data storage and retrieval
4. **Strategy Pattern**: Allows different ways to execute similar actions
5. **Command Pattern**: Each action is a self-contained command

## SOLID Principles in Action

The application follows SOLID principles:

1. **Single Responsibility**: Each class has one job (e.g., ClickAction just handles clicking)
2. **Open/Closed**: New actions can be added without changing existing code
3. **Liskov Substitution**: Any action can be used where an IAction is expected
4. **Interface Segregation**: Interfaces are specific to needs (e.g., IAction, IValidator)
5. **Dependency Inversion**: High-level modules depend on abstractions, not details

## Recent Refactoring: Action Factory

We recently refactored the ActionFactory to better follow the Single Responsibility Principle:

**Before**: One large class handled registration, validation, creation, and error handling.

**After**: Separated into specialized components:
- `ActionRegistry`: Manages the registry of action types
- `ActionValidator`: Validates action data
- `NestedActionHandler`: Processes nested actions
- `ActionCreator`: Creates action instances
- `ActionFactory`: Acts as a facade for the other components

This makes the code more maintainable, testable, and easier to extend with new action types.

## Conclusion

AutoQliq is like a robot assistant for web browsing. You tell it what to do through the UI, and it uses a series of specialized components to carry out those instructions in a web browser. The application is designed to be flexible, maintainable, and extensible, following good software design principles.
