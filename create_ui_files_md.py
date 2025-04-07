import os
import re

def get_file_content(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"

def create_ui_files_md():
    """Create UIfiles.md with UI-related files and a comprehensive description."""
    # List of files to include
    files_to_include = [
        "src/ui/interfaces/view.py",
        "src/ui/interfaces/presenter.py",
        "src/ui/views/base_view.py",
        "src/ui/presenters/base_presenter.py",
        "src/ui/common/ui_factory.py",
        "src/ui/common/widget_factory.py",
        "src/ui/dialogs/action_editor_dialog.py",
        "src/ui/dialogs/credential_manager_dialog.py",
        "src/ui/views/workflow_editor_view.py",
        "src/ui/presenters/workflow_editor_presenter.py",
        "src/ui/views/settings_view.py",
        "src/ui/presenters/settings_presenter.py",
        "src/core/interfaces/action.py",
        "src/main_ui.py"
    ]
    
    # Comprehensive description
    description = """# AutoQliq UI Development Guide

## Overview

This document provides comprehensive information for developing the UI components of the AutoQliq application. AutoQliq is a web automation tool built with a clean architecture following the Model-View-Presenter (MVP) pattern. The UI is implemented using Tkinter and follows SOLID principles.

## Architecture

AutoQliq follows a layered architecture:
- **Core Layer**: Domain model, interfaces, actions, workflow logic
- **Infrastructure Layer**: WebDrivers, persistence, repositories
- **Application Layer**: Services orchestrating use cases
- **UI Layer**: Views, presenters, dialogs following MVP pattern

The UI layer is structured according to the MVP pattern:
- **Views**: Responsible for rendering UI elements and forwarding user events to presenters
- **Presenters**: Handle UI logic, interact with services, and update views
- **Models**: Data structures representing the domain objects

## UI Components to Develop

### 1. Visual Workflow Designer
A drag-and-drop interface for creating and editing workflows visually.

**Files to Create:**
- `src/ui/views/workflow_designer_view.py`: Visual canvas for workflow design
- `src/ui/presenters/workflow_designer_presenter.py`: Logic for the designer
- `src/ui/common/workflow_canvas.py`: Custom canvas widget for workflow visualization
- `src/ui/common/action_node.py`: Visual representation of actions
- `src/ui/common/connection_line.py`: Visual representation of connections between actions

**Responsibilities:**
- Drag-and-drop action creation
- Visual representation of different action types
- Connection management between actions
- Property editing for actions
- Validation of workflow structure
- Undo/redo functionality
- Zoom and pan capabilities
- Selection and multi-selection of nodes
- Copy/paste functionality

### 2. Dashboard View
An overview dashboard showing workflow status, execution statistics, and quick actions.

**Files to Create:**
- `src/ui/views/dashboard_view.py`: Main dashboard view
- `src/ui/presenters/dashboard_presenter.py`: Dashboard logic
- `src/ui/common/dashboard_widgets.py`: Custom widgets for the dashboard
- `src/ui/common/chart_widgets.py`: Visualization widgets for statistics

**Responsibilities:**
- Display workflow execution statistics
- Show recent workflow runs
- Provide quick access to common actions
- Display system status
- Show scheduled workflows
- Visualize execution results

### 3. Element Inspector Tool
A tool for visually selecting web elements for automation.

**Files to Create:**
- `src/ui/views/element_inspector_view.py`: Element inspector interface
- `src/ui/presenters/element_inspector_presenter.py`: Inspector logic
- `src/ui/dialogs/element_selector_dialog.py`: Dialog for selecting elements
- `src/ui/common/browser_preview.py`: Browser preview widget

**Responsibilities:**
- Browser integration
- Element highlighting
- Property display
- XPath/CSS selector generation
- Element selection and targeting
- Preview of selected elements

### 4. Results Viewer
A detailed view of workflow execution results.

**Files to Create:**
- `src/ui/views/results_viewer_view.py`: Results display interface
- `src/ui/presenters/results_viewer_presenter.py`: Results handling logic
- `src/ui/common/result_widgets.py`: Custom widgets for result display
- `src/ui/dialogs/result_detail_dialog.py`: Dialog for detailed result view

**Responsibilities:**
- Display execution results
- Show execution timeline
- Highlight errors and warnings
- Provide filtering and sorting
- Support exporting results
- Show screenshots captured during execution
- Display logs and detailed information

### 5. Settings Dialog Enhancements
Improvements to the existing settings management.

**Files to Create:**
- `src/ui/dialogs/advanced_settings_dialog.py`: Dialog for advanced settings
- `src/ui/common/settings_widgets.py`: Custom widgets for settings

**Responsibilities:**
- Provide advanced configuration options
- Support for plugin configuration
- Profile management
- Import/export settings

### 6. Credential Manager Enhancements
Improvements to the existing credential management.

**Files to Create:**
- `src/ui/dialogs/credential_import_dialog.py`: Dialog for importing credentials
- `src/ui/dialogs/credential_export_dialog.py`: Dialog for exporting credentials

**Responsibilities:**
- Secure credential import/export
- Credential validation
- Enhanced security features

## Technical Requirements

1. **UI Framework**: Use Tkinter for all UI components
2. **Styling**: Maintain consistent styling across components
3. **Responsiveness**: Ensure UI is responsive and doesn't freeze during operations
4. **Error Handling**: Provide clear error messages and recovery options
5. **Accessibility**: Ensure UI is accessible with keyboard navigation
6. **Cross-platform**: Ensure UI works on Windows, macOS, and Linux

## Integration Points

1. **Service Layer**: UI components should interact with application services
2. **Repository Layer**: Access data through repositories via presenters
3. **Configuration**: Use the configuration system for settings
4. **WebDriver**: Interact with WebDriver for browser automation

## Testing Approach

1. **Unit Tests**: Create unit tests for presenters
2. **Integration Tests**: Test integration with services
3. **UI Tests**: Test UI components with mock objects
4. **User Acceptance Tests**: Create scenarios for end-to-end testing

## Existing Files Overview

The following files are included in this document to provide context and examples for UI development:
"""

    # Add file descriptions
    file_descriptions = {
        "src/ui/interfaces/view.py": "Defines the base interface for all views in the application.",
        "src/ui/interfaces/presenter.py": "Defines the base interface for all presenters in the application.",
        "src/ui/views/base_view.py": "Base class for all views, implementing common functionality.",
        "src/ui/presenters/base_presenter.py": "Base class for all presenters, implementing common functionality.",
        "src/ui/common/ui_factory.py": "Factory for creating UI components consistently.",
        "src/ui/common/widget_factory.py": "Factory for creating specific widgets with consistent styling.",
        "src/ui/dialogs/action_editor_dialog.py": "Dialog for editing action properties.",
        "src/ui/dialogs/credential_manager_dialog.py": "Dialog for managing credentials.",
        "src/ui/views/workflow_editor_view.py": "View for editing workflows.",
        "src/ui/presenters/workflow_editor_presenter.py": "Presenter for the workflow editor.",
        "src/ui/views/settings_view.py": "View for application settings.",
        "src/ui/presenters/settings_presenter.py": "Presenter for the settings view.",
        "src/core/interfaces/action.py": "Defines the interface for actions in the core domain.",
        "src/main_ui.py": "Main entry point for the UI application."
    }
    
    for file_path, desc in file_descriptions.items():
        description += f"\n### {file_path}\n{desc}\n"
    
    # Create the output file
    with open("UIfiles.md", 'w', encoding='utf-8') as output_file:
        output_file.write(description + "\n\n")
        
        # Add each file's content
        for file_path in files_to_include:
            normalized_path = file_path.replace('/', os.sep)
            content = get_file_content(normalized_path)
            
            output_file.write(f"## {file_path}\n\n```python\n{content}\n```\n\n")
    
    print("UIfiles.md has been created successfully.")

if __name__ == "__main__":
    create_ui_files_md()
