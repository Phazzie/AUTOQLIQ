# AutoQliq UI Development Prompt

**********ARCHIVED**********
Archived on: 2025-04-06


## Overview

I need you to develop several key UI components for AutoQliq, a web automation tool built with a clean architecture following the Model-View-Presenter (MVP) pattern. The application is implemented using Tkinter and follows SOLID principles.

The UIfiles.md document contains all the existing UI code and architecture information you'll need to understand the current implementation. Please review it thoroughly before starting development.

## Components to Implement

### 1. Visual Workflow Designer

Create a drag-and-drop interface for visually designing automation workflows. This is the most critical and complex component.

**Files to create:**
- `src/ui/views/workflow_designer_view.py`
- `src/ui/presenters/workflow_designer_presenter.py`
- `src/ui/common/workflow_canvas.py`
- `src/ui/common/action_node.py`
- `src/ui/common/connection_line.py`

**Key features:**
- Canvas for dragging and dropping action nodes
- Visual representation of different action types (different colors/icons)
- Connection lines between actions to show execution flow
- Property editing for actions (using the existing ActionEditorDialog)
- Ability to select, move, and delete nodes
- Zoom and pan capabilities
- Undo/redo functionality
- Validation of workflow structure

**Integration points:**
- Must use the existing ActionFactory to create actions
- Must use the existing ActionEditorDialog for editing action properties
- Must integrate with WorkflowService for saving/loading workflows

### 2. Template Management UI

Create a UI for managing action templates, which are reusable collections of actions.

**Files to create:**
- `src/ui/views/template_manager_view.py`
- `src/ui/presenters/template_manager_presenter.py`
- `src/ui/dialogs/template_editor_dialog.py`

**Key features:**
- List of available templates
- Ability to create, edit, and delete templates
- Interface for selecting actions to include in a template
- Template import/export functionality

**Integration points:**
- Must use WorkflowService for template operations
- Should reuse components from the workflow editor where appropriate

### 3. Dashboard View

Create a dashboard that provides an overview of workflows, executions, and system status.

**Files to create:**
- `src/ui/views/dashboard_view.py`
- `src/ui/presenters/dashboard_presenter.py`
- `src/ui/common/dashboard_widgets.py`

**Key features:**
- Summary of available workflows
- Recent execution results
- Quick access to common actions
- System status indicators
- Basic statistics (execution counts, success rates, etc.)

**Integration points:**
- Must integrate with WorkflowService for workflow information
- Should integrate with ReportingService for execution statistics

### 4. Element Inspector Tool

Create a tool for visually selecting web elements for automation.

**Files to create:**
- `src/ui/views/element_inspector_view.py`
- `src/ui/presenters/element_inspector_presenter.py`
- `src/ui/dialogs/element_selector_dialog.py`

**Key features:**
- Browser preview window
- Element highlighting
- XPath/CSS selector generation
- Element property display
- Selection confirmation

**Integration points:**
- Must integrate with WebDriverService for browser control
- Should provide selectors back to the action editor

## Technical Requirements

1. **Follow MVP Pattern**: All components must follow the Model-View-Presenter pattern used throughout the application.
2. **Use Tkinter**: All UI components must use Tkinter and ttk for consistency.
3. **SOLID Principles**: Follow SOLID principles in your implementation.
4. **Error Handling**: Implement proper error handling and user feedback.
5. **Responsive UI**: Ensure the UI remains responsive during operations.
6. **Documentation**: Include docstrings and comments explaining your implementation.
7. **Testing**: Include suggestions for how to test the components.

## Implementation Approach

1. Start with the Visual Workflow Designer as it's the most critical component.
2. Implement the Template Management UI next, as it builds on the workflow editor concepts.
3. Then implement the Dashboard View for better application navigation.
4. Finally, implement the Element Inspector Tool to enhance the action creation experience.

## Deliverables

For each component, provide:
1. Complete Python code for all required files
2. Brief explanation of your implementation approach
3. Notes on any challenges or design decisions
4. Suggestions for future enhancements

## Additional Context

The UIfiles.md document contains all the existing UI code and architecture information. Pay special attention to:
- The MVP pattern implementation
- How views and presenters interact
- How the existing dialogs are implemented
- The action model and factory pattern

Remember that the UI should be clean, intuitive, and follow the existing design patterns. Focus on creating components that are maintainable, extensible, and adhere to SOLID principles.

Thank you for your help with this important part of the AutoQliq project!
