# AutoQliq UI Development Guide

**********ARCHIVED**********
Archived on: 2025-04-06


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

### src/ui/interfaces/view.py
Defines the base interface for all views in the application.

### src/ui/interfaces/presenter.py
Defines the base interface for all presenters in the application.

### src/ui/views/base_view.py
Base class for all views, implementing common functionality.

### src/ui/presenters/base_presenter.py
Base class for all presenters, implementing common functionality.

### src/ui/common/ui_factory.py
Factory for creating UI components consistently.

### src/ui/common/widget_factory.py
Factory for creating specific widgets with consistent styling.

### src/ui/dialogs/action_editor_dialog.py
Dialog for editing action properties.

### src/ui/dialogs/credential_manager_dialog.py
Dialog for managing credentials.

### src/ui/views/workflow_editor_view.py
View for editing workflows.

### src/ui/presenters/workflow_editor_presenter.py
Presenter for the workflow editor.

### src/ui/views/settings_view.py
View for application settings.

### src/ui/presenters/settings_presenter.py
Presenter for the settings view.

### src/core/interfaces/action.py
Defines the interface for actions in the core domain.

### src/main_ui.py
Main entry point for the UI application.


## src/ui/interfaces/view.py

```python
"""View interfaces for AutoQliq UI.

This module provides interfaces for views in the UI layer,
defining the contract between presenters and views.
"""

import abc
from typing import Any, Dict, List, Optional

# Assuming IAction is defined in core interfaces
from src.core.interfaces import IAction


class IView(abc.ABC):
    """Base interface for views."""

    @abc.abstractmethod
    def display_error(self, title: str, message: str) -> None:
        """Display an error message to the user."""
        pass

    @abc.abstractmethod
    def display_message(self, title: str, message: str) -> None:
        """Display an informational message to the user."""
        pass

    @abc.abstractmethod
    def confirm_action(self, title: str, message: str) -> bool:
        """Ask the user for confirmation."""
        pass

    @abc.abstractmethod
    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
         """Clear or reset the view's state."""
         pass


class IWorkflowEditorView(IView):
    """Interface for the Workflow Editor View."""

    @abc.abstractmethod
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the list of available workflows."""
        pass

    @abc.abstractmethod
    def set_action_list(self, actions_display: List[str]) -> None:
        """Display the actions for the currently loaded workflow."""
        pass

    @abc.abstractmethod
    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the workflow currently selected in the list."""
        pass

    @abc.abstractmethod
    def get_selected_action_index(self) -> Optional[int]:
         """Get the index of the action currently selected in the list."""
         pass

    @abc.abstractmethod
    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
         """Open a dialog/form to edit or add an action. Returns new data or None if cancelled."""
         pass

    @abc.abstractmethod
    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
         """Prompt the user to enter a name for a new workflow."""
         pass


class IWorkflowRunnerView(IView):
    """Interface for the Workflow Runner View."""

    @abc.abstractmethod
    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the list of available workflows."""
        pass

    @abc.abstractmethod
    def set_credential_list(self, credential_names: List[str]) -> None:
        """Populate the list of available credentials."""
        pass

    @abc.abstractmethod
    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the workflow selected by the user."""
        pass

    @abc.abstractmethod
    def get_selected_credential_name(self) -> Optional[str]:
        """Get the name of the credential selected by the user."""
        pass

    @abc.abstractmethod
    def log_message(self, message: str) -> None:
        """Append a message to the execution log display."""
        pass

    @abc.abstractmethod
    def clear_log(self) -> None:
        """Clear the execution log display."""
        pass

    @abc.abstractmethod
    def set_running_state(self, is_running: bool) -> None:
        """Update the UI elements based on whether a workflow is running (e.g., disable Run, enable Stop)."""
        pass

    # Optional progress indication methods
    # @abc.abstractmethod
    # def start_progress(self) -> None:
    #     """Start a progress indicator (e.g., indeterminate progress bar)."""
    #     pass

    # @abc.abstractmethod
    # def stop_progress(self) -> None:
    #     """Stop the progress indicator."""
    #     pass

    # @abc.abstractmethod
    # def set_progress(self, value: float) -> None:
    #     """Set the value of a determinate progress indicator (0-100)."""
    #     pass
```

## src/ui/interfaces/presenter.py

```python
"""Presenter interfaces for AutoQliq UI.

This module provides interfaces for presenters in the UI layer,
defining the contract between views and presenters.
"""

import abc
from typing import Any, List, Optional, Dict

# Assuming IAction is defined in core interfaces
from src.core.interfaces import IAction


class IPresenter(abc.ABC):
    """Base interface for presenters."""

    @abc.abstractmethod
    def set_view(self, view: Any) -> None:
        """Set the view associated with this presenter.

        Args:
            view: The view instance.
        """
        pass

    @abc.abstractmethod
    def initialize_view(self) -> None:
        """Initialize the associated view with necessary data."""
        pass


class IWorkflowEditorPresenter(IPresenter):
    """Interface for the Workflow Editor Presenter."""

    @abc.abstractmethod
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        pass

    @abc.abstractmethod
    def load_workflow(self, name: str) -> None:
        """Load the specified workflow into the editor view."""
        pass

    @abc.abstractmethod
    def save_workflow(self, name: str, actions: List[Dict[str, Any]]) -> None:
        """Save the currently edited workflow actions under the given name."""
        pass

    @abc.abstractmethod
    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow."""
        pass

    @abc.abstractmethod
    def delete_workflow(self, name: str) -> None:
        """Delete the specified workflow."""
        pass

    @abc.abstractmethod
    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action (represented by data) to the current workflow."""
        pass

    @abc.abstractmethod
    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update the action at the specified index with new data."""
        pass

    @abc.abstractmethod
    def delete_action(self, index: int) -> None:
        """Delete the action at the specified index."""
        pass

    @abc.abstractmethod
    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
         """Get the data dictionary for the action at the specified index."""
         pass


class IWorkflowRunnerPresenter(IPresenter):
    """Interface for the Workflow Runner Presenter."""

    @abc.abstractmethod
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names."""
        pass

    @abc.abstractmethod
    def get_credential_list(self) -> List[str]:
        """Get the list of available credential names."""
        pass

    @abc.abstractmethod
    def run_workflow(self, workflow_name: str, credential_name: Optional[str]) -> None:
        """Start executing the specified workflow using the selected credential."""
        pass

    @abc.abstractmethod
    def stop_workflow(self) -> None:
        """Stop the currently running workflow execution (if any)."""
        pass
```

## src/ui/views/base_view.py

```python
"""Base view class for AutoQliq UI."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Optional, Any

from src.ui.interfaces.view import IView
from src.ui.common.error_handler import ErrorHandler
from src.ui.common.status_bar import StatusBar # Import StatusBar

class BaseView(IView):
    """
    Base class for all view components in the application.

    Provides common functionality like holding the root widget, presenter reference,
    logger, error handler, status bar integration, and basic UI interaction methods.

    Attributes:
        root (tk.Widget): The parent widget for this view (e.g., a tab frame).
        presenter (Any): The presenter associated with this view.
        logger (logging.Logger): Logger instance for the view subclass.
        error_handler (ErrorHandler): Utility for displaying errors.
        main_frame (ttk.Frame): The primary frame holding the view's specific content.
        status_bar (Optional[StatusBar]): Reference to the status bar instance (shared via root).
    """
    def __init__(self, root: tk.Widget, presenter: Any):
        """
        Initialize the BaseView.

        Args:
            root (tk.Widget): The parent widget (e.g., a frame within a tab).
            presenter (Any): The presenter instance handling the logic for this view.
        """
        if root is None:
            raise ValueError("Root widget cannot be None for BaseView.")
        if presenter is None:
             raise ValueError("Presenter cannot be None for BaseView.")

        self.root = root
        self.presenter = presenter
        self.logger = logging.getLogger(f"view.{self.__class__.__name__}")
        self.error_handler = ErrorHandler(self.logger)
        self.status_bar: Optional[StatusBar] = None # Initialize status_bar attribute

        # --- Main Frame Setup ---
        # This frame fills the parent widget (e.g., the tab frame provided by main_ui)
        # Subclasses will add their widgets to this frame.
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Find the status bar - assumes status bar is attached to the toplevel window
        # and registered on it by main_ui.py
        self._find_status_bar()

        self.logger.debug(f"{self.__class__.__name__} initialized.")

    def _find_status_bar(self):
        """Tries to find a StatusBar instance attached to the toplevel window."""
        try:
             toplevel = self.main_frame.winfo_toplevel() # Get the main Tk window
             if hasattr(toplevel, 'status_bar_instance') and isinstance(toplevel.status_bar_instance, StatusBar):
                  self.status_bar = toplevel.status_bar_instance
                  self.logger.debug("Found StatusBar instance on toplevel window.")
             else:
                  self.logger.warning("StatusBar instance not found on toplevel window.")
        except Exception as e:
             self.logger.warning(f"Could not find status bar: {e}")


    @property
    def widget(self) -> tk.Widget:
        """Returns the main content widget managed by this view (the main_frame)."""
        return self.main_frame

    def display_error(self, title: str, message: str) -> None:
        """Display an error message box."""
        self.logger.warning(f"Displaying error: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showerror(title, message, parent=parent_window)
        except Exception as e:
             self.logger.error(f"Failed to display error message box: {e}")
        # Also update status bar
        self.set_status(f"Error: {message[:100]}")

    def display_message(self, title: str, message: str) -> None:
        """Display an informational message box."""
        self.logger.info(f"Displaying message: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            messagebox.showinfo(title, message, parent=parent_window)
            self.set_status(message)
        except Exception as e:
            self.logger.error(f"Failed to display info message box: {e}")

    def confirm_action(self, title: str, message: str) -> bool:
        """Display a confirmation dialog and return the user's choice."""
        self.logger.debug(f"Requesting confirmation: Title='{title}', Message='{message}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            response = messagebox.askyesno(title, message, parent=parent_window)
            self.logger.debug(f"Confirmation response: {response}")
            return response
        except Exception as e:
             self.logger.error(f"Failed to display confirmation dialog: {e}")
             return False

    def prompt_for_input(self, title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Display a simple input dialog and return the user's input."""
        self.logger.debug(f"Requesting input: Title='{title}', Prompt='{prompt}'")
        try:
            parent_window = self.main_frame.winfo_toplevel()
            result = simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=parent_window)
            log_result = '<cancelled>' if result is None else '<input provided>'
            self.logger.debug(f"Input dialog result: {log_result}")
            return result
        except Exception as e:
             self.logger.error(f"Failed to display input dialog: {e}")
             return None

    def set_status(self, message: str) -> None:
        """Update the status bar message."""
        if not self.status_bar: self._find_status_bar() # Try finding again

        if self.status_bar:
            # Schedule the update using 'after' to ensure it runs on the main thread
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, lambda msg=message: self.status_bar.set_message(msg))
                 else: self.logger.warning("StatusBar frame no longer exists.")
            except Exception as e: self.logger.error(f"Failed to schedule status update: {e}")
        else: self.logger.debug(f"Status update requested (no status bar found): {message}")


    def clear(self) -> None:
        """Clear or reset the view's state. Needs implementation in subclasses."""
        self.logger.debug(f"Base clear called for {self.__class__.__name__}.")
        self.set_status("Ready.") # Reset status bar
        if self.status_bar:
            try:
                 if self.status_bar.frame.winfo_exists():
                      self.status_bar.frame.after(0, self.status_bar.stop_progress)
            except Exception as e: self.logger.error(f"Error stopping progress bar during clear: {e}")


    def update(self) -> None:
        """Force an update of the UI. Generally not needed unless managing complex state."""
        try:
             # Use the main_frame's toplevel window for update_idletasks
             toplevel = self.main_frame.winfo_toplevel()
             if toplevel.winfo_exists():
                  toplevel.update_idletasks()
                  # self.logger.debug(f"Base update called for {self.__class__.__name__}.") # Can be noisy
        except Exception as e:
             self.logger.error(f"Error during UI update: {e}")
```

## src/ui/presenters/base_presenter.py

```python
"""Base presenter class for AutoQliq UI."""
import logging
from typing import Any, Optional, Dict, List, Callable, TypeVar, Generic

from src.core.exceptions import AutoQliqError, ValidationError
from src.ui.common.error_handler import ErrorHandler
from src.ui.interfaces.presenter import IPresenter
# Import base view interface for type hinting
from src.ui.interfaces.view import IView

# Type variable for the view type
V = TypeVar('V', bound=IView)


class BasePresenter(Generic[V], IPresenter):
    """Base class for all presenters.

    Provides common functionality like view management, logging, and error handling.

    Attributes:
        _view: The view component associated with this presenter. Use property `view`.
        logger: Logger instance specific to the presenter subclass.
        error_handler: Handler for logging and potentially showing errors in the view.
    """

    def __init__(self, view: Optional[V] = None):
        """Initialize a BasePresenter.

        Args:
            view: The view component (optional at init, can be set later).
        """
        self._view: Optional[V] = view
        self.logger = logging.getLogger(f"presenter.{self.__class__.__name__}")
        # ErrorHandler can use the same logger or a dedicated one
        self.error_handler = ErrorHandler(self.logger)
        self.logger.debug(f"{self.__class__.__name__} initialized.")

    @property
    def view(self) -> Optional[V]:
        """Get the associated view instance."""
        return self._view

    def set_view(self, view: V) -> None:
        """Set the view component associated with this presenter.

        Args:
            view: The view component instance.
        """
        if not isinstance(view, IView):
            # Basic check, could be more specific if V had stricter bounds
            raise TypeError("View must implement the IView interface.")
        self._view = view
        self.logger.debug(f"View {type(view).__name__} set for presenter {self.__class__.__name__}")
        # Optionally call initialize_view after setting
        # self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view with data. Should be overridden by subclasses."""
        self.logger.debug(f"Base initialize_view called for {self.__class__.__name__}. Subclass should implement.")
        pass # Subclasses override to populate view on startup or after view is set

    def _handle_error(self, error: Exception, context: str) -> None:
        """Internal helper to handle errors using the error_handler and update the view."""
        self.error_handler.handle_error(error, context, show_message=False) # Log first

        # Show the error in the view if available
        if self.view:
             # Extract a user-friendly title and message
             title = "Error"
             message = str(error)
             if isinstance(error, AutoQliqError):
                 # Use more specific titles for known error types
                 error_type_name = type(error).__name__.replace("Error", " Error") # Add space
                 title = error_type_name
             elif isinstance(error, FileNotFoundError):
                 title = "File Not Found"
             elif isinstance(error, PermissionError):
                 title = "Permission Error"
             else: # Unexpected errors
                 title = "Unexpected Error"
                 message = f"An unexpected error occurred: {message}"

             try:
                self.view.display_error(title, message)
             except Exception as view_e:
                  self.logger.error(f"Failed to display error in view: {view_e}")
        else:
             self.logger.warning(f"Cannot display error in view (view not set) for context: {context}")

    # Optional: Decorator within the base class for convenience
    @classmethod
    def handle_errors(cls, context: str) -> Callable[[Callable], Callable]:
        """
        Class method decorator to automatically handle errors in presenter methods.

        Logs errors and displays them in the associated view (if set).

        Args:
            context: Description of the operation being performed (for error messages).

        Returns:
            A decorator.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(presenter_instance: 'BasePresenter', *args, **kwargs) -> Any:
                try:
                    # Execute the original presenter method
                    return func(presenter_instance, *args, **kwargs)
                except Exception as e:
                    # Use the instance's error handling method
                    presenter_instance._handle_error(e, context)
                    # Decide what to return on error. Often None or False for actions.
                    # Returning None might require callers to check.
                    # Returning False might be suitable for boolean methods.
                    # Re-raising might be needed if the caller needs to react specifically.
                    # Defaulting to returning None here.
                    return None # Or False, or re-raise specific types if needed
            # Need functools for wraps
            import functools
            return wrapper
        return decorator
```

## src/ui/common/ui_factory.py

```python
"""UI factory for creating common UI components."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any, Optional, Union

from src.core.exceptions import UIError


class UIFactory:
    """Factory for creating common UI components.

    This class provides methods for creating common UI components with consistent
    styling and behavior. It primarily uses ttk widgets for a modern look.
    """

    @staticmethod
    def create_frame(parent: tk.Widget, padding: Union[str, int] = "10", relief: str = tk.FLAT, **kwargs) -> ttk.Frame:
        """Create a frame with consistent styling.

        Args:
            parent: The parent widget.
            padding: The padding to apply to the frame (e.g., "10" or 10 or "5 10").
            relief: Border style (e.g., tk.FLAT, tk.RAISED, tk.SUNKEN, tk.GROOVE).
            **kwargs: Additional ttk.Frame options.

        Returns:
            A configured ttk.Frame.

        Raises:
            UIError: If the frame cannot be created.
        """
        try:
            frame = ttk.Frame(parent, padding=padding, relief=relief, **kwargs)
            return frame
        except Exception as e:
            error_msg = "Failed to create frame"
            raise UIError(error_msg, component_name="Frame", cause=e) from e

    @staticmethod
    def create_label_frame(parent: tk.Widget, text: str, padding: Union[str, int] = "10", **kwargs) -> ttk.LabelFrame:
        """Create a labeled frame with consistent styling.

        Args:
            parent: The parent widget.
            text: The text label for the frame.
            padding: The padding to apply inside the frame.
            **kwargs: Additional ttk.LabelFrame options.

        Returns:
            A configured ttk.LabelFrame.

        Raises:
            UIError: If the labeled frame cannot be created.
        """
        try:
            frame = ttk.LabelFrame(parent, text=text, padding=padding, **kwargs)
            return frame
        except Exception as e:
            error_msg = f"Failed to create labeled frame: {text}"
            raise UIError(error_msg, component_name="LabelFrame", cause=e) from e

    @staticmethod
    def create_button(
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None, # Allow None command
        width: Optional[int] = None,
        state: str = tk.NORMAL,
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Button:
        """Create a button with consistent styling.

        Args:
            parent: The parent widget.
            text: The text to display on the button.
            command: The callback to execute when the button is clicked.
            width: The width of the button in characters (approximate).
            state: The initial state of the button (tk.NORMAL, tk.DISABLED).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Button options.

        Returns:
            A configured ttk.Button.

        Raises:
            UIError: If the button cannot be created.
        """
        try:
            button = ttk.Button(parent, text=text, command=command, width=width, state=state, style=style, **kwargs)
            return button
        except Exception as e:
            error_msg = f"Failed to create button: {text}"
            raise UIError(error_msg, component_name="Button", cause=e) from e

    @staticmethod
    def create_label(
        parent: tk.Widget,
        text: str = "",
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        anchor: str = tk.W, # Default to west alignment
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Label:
        """Create a label with consistent styling.

        Args:
            parent: The parent widget.
            text: The static text to display (if textvariable is None).
            textvariable: The variable to bind to the label's text.
            width: The width of the label in characters (approximate).
            anchor: How the text is positioned within the label space (e.g., tk.W, tk.CENTER).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Label options.

        Returns:
            A configured ttk.Label.

        Raises:
            UIError: If the label cannot be created.
        """
        try:
            label = ttk.Label(parent, text=text, textvariable=textvariable, width=width, anchor=anchor, style=style, **kwargs)
            return label
        except Exception as e:
            error_msg = f"Failed to create label: {text or textvariable}"
            raise UIError(error_msg, component_name="Label", cause=e) from e

    @staticmethod
    def create_entry(
        parent: tk.Widget,
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        state: str = tk.NORMAL,
        show: Optional[str] = None, # For password fields
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Entry:
        """Create an entry with consistent styling.

        Args:
            parent: The parent widget.
            textvariable: The variable to bind to the entry.
            width: The width of the entry in characters (approximate).
            state: The initial state of the entry (tk.NORMAL, tk.DISABLED, "readonly").
            show: Character to display instead of actual input (e.g., "*").
            style: Optional ttk style name.
            **kwargs: Additional ttk.Entry options.

        Returns:
            A configured ttk.Entry.

        Raises:
            UIError: If the entry cannot be created.
        """
        try:
            entry = ttk.Entry(parent, textvariable=textvariable, width=width, state=state, show=show, style=style, **kwargs)
            return entry
        except Exception as e:
            error_msg = "Failed to create entry"
            raise UIError(error_msg, component_name="Entry", cause=e) from e

    @staticmethod
    def create_combobox(
        parent: tk.Widget,
        textvariable: Optional[tk.StringVar] = None,
        values: Optional[List[str]] = None,
        width: Optional[int] = None,
        state: str = "readonly", # Default to readonly to prevent typing arbitrary text
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Combobox:
        """Create a combobox with consistent styling.

        Args:
            parent: The parent widget.
            textvariable: The variable to bind to the combobox.
            values: The list of values to display in the dropdown.
            width: The width of the combobox in characters (approximate).
            state: The initial state ('readonly', tk.NORMAL, tk.DISABLED).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Combobox options.

        Returns:
            A configured ttk.Combobox.

        Raises:
            UIError: If the combobox cannot be created.
        """
        try:
            combobox = ttk.Combobox(
                parent,
                textvariable=textvariable,
                values=values or [],
                width=width,
                state=state,
                style=style,
                **kwargs
            )
            return combobox
        except Exception as e:
            error_msg = "Failed to create combobox"
            raise UIError(error_msg, component_name="Combobox", cause=e) from e

    @staticmethod
    def create_listbox(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.BROWSE, # BROWSE is often better default than SINGLE
        **kwargs
    ) -> tk.Listbox:
        """Create a listbox (using standard tk for better compatibility).

        Args:
            parent: The parent widget.
            height: The height of the listbox in lines.
            width: The width of the listbox in characters (approximate).
            selectmode: The selection mode (tk.SINGLE, tk.BROWSE, tk.MULTIPLE, tk.EXTENDED).
            **kwargs: Additional tk.Listbox options.

        Returns:
            A configured tk.Listbox.

        Raises:
            UIError: If the listbox cannot be created.
        """
        try:
            listbox = tk.Listbox(parent, height=height, width=width, selectmode=selectmode, **kwargs)
            # Consider adding borderwidth=0 if using inside ttk.Frame to avoid double borders
            # listbox.config(borderwidth=0, highlightthickness=0) # Example
            return listbox
        except Exception as e:
            error_msg = "Failed to create listbox"
            raise UIError(error_msg, component_name="Listbox", cause=e) from e

    @staticmethod
    def create_scrollbar(
        parent: tk.Widget,
        orient: str = tk.VERTICAL,
        command: Optional[Callable] = None
    ) -> ttk.Scrollbar:
        """Create a scrollbar with consistent styling.

        Args:
            parent: The parent widget.
            orient: The orientation (tk.VERTICAL or tk.HORIZONTAL).
            command: The command to execute when the scrollbar is moved (e.g., listbox.yview).

        Returns:
            A configured ttk.Scrollbar.

        Raises:
            UIError: If the scrollbar cannot be created.
        """
        try:
            scrollbar = ttk.Scrollbar(parent, orient=orient, command=command)
            return scrollbar
        except Exception as e:
            error_msg = "Failed to create scrollbar"
            raise UIError(error_msg, component_name="Scrollbar", cause=e) from e

    @staticmethod
    def create_text(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL,
        **kwargs
    ) -> tk.Text:
        """Create a text widget (using standard tk).

        Args:
            parent: The parent widget.
            height: The height of the text widget in lines.
            width: The width of the text widget in characters (approximate).
            wrap: The wrap mode (tk.WORD, tk.CHAR, tk.NONE).
            state: The initial state (tk.NORMAL, tk.DISABLED).
            **kwargs: Additional tk.Text options.

        Returns:
            A configured tk.Text widget.

        Raises:
            UIError: If the text widget cannot be created.
        """
        try:
            text = tk.Text(parent, height=height, width=width, wrap=wrap, state=state, **kwargs)
            # text.config(borderwidth=0, highlightthickness=0) # Optional styling
            return text
        except Exception as e:
            error_msg = "Failed to create text widget"
            raise UIError(error_msg, component_name="Text", cause=e) from e

    @staticmethod
    def create_separator(parent: tk.Widget, orient: str = tk.HORIZONTAL, **kwargs) -> ttk.Separator:
        """Create a separator line.

        Args:
            parent: The parent widget.
            orient: Orientation (tk.HORIZONTAL or tk.VERTICAL).
            **kwargs: Additional ttk.Separator options.

        Returns:
            A configured ttk.Separator.

        Raises:
            UIError: If the separator cannot be created.
        """
        try:
            separator = ttk.Separator(parent, orient=orient, **kwargs)
            return separator
        except Exception as e:
            error_msg = "Failed to create separator"
            raise UIError(error_msg, component_name="Separator", cause=e) from e

    # --- Composite Component Creation (moved from ComponentFactory) ---

    @staticmethod
    def create_scrolled_listbox(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.BROWSE
    ) -> Dict[str, Union[tk.Listbox, ttk.Scrollbar, ttk.Frame]]:
        """Create a listbox with a vertical scrollbar in a frame.

        Args:
            parent: The parent widget.
            height: The height of the listbox in lines.
            width: The width of the listbox in characters.
            selectmode: The selection mode (tk.SINGLE, tk.BROWSE, etc.).

        Returns:
            A dictionary containing {'frame': ttk.Frame, 'listbox': tk.Listbox, 'scrollbar': ttk.Scrollbar}.

        Raises:
            UIError: If the scrolled listbox cannot be created.
        """
        try:
            # Use FLAT relief for the outer frame usually looks better
            frame = UIFactory.create_frame(parent, padding=0, relief=tk.SUNKEN, borderwidth=1)
            scrollbar = UIFactory.create_scrollbar(frame, orient=tk.VERTICAL)
            listbox = UIFactory.create_listbox(frame, height=height, width=width, selectmode=selectmode,
                                              yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)

            # Grid layout inside the frame is often more flexible
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            listbox.grid(row=0, column=0, sticky=tk.NSEW)
            scrollbar.grid(row=0, column=1, sticky=tk.NS)

            return {"frame": frame, "listbox": listbox, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled listbox"
            raise UIError(error_msg, component_name="ScrolledListbox", cause=e) from e

    @staticmethod
    def create_scrolled_text(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL,
        **text_kwargs
    ) -> Dict[str, Union[tk.Text, ttk.Scrollbar, ttk.Frame]]:
        """Create a text widget with a vertical scrollbar in a frame.

        Args:
            parent: The parent widget.
            height: The height of the text widget in lines.
            width: The width of the text widget in characters.
            wrap: The wrap mode (tk.WORD, tk.CHAR, tk.NONE).
            state: The initial state (tk.NORMAL, tk.DISABLED).
            **text_kwargs: Additional keyword arguments for the tk.Text widget.

        Returns:
            A dictionary containing {'frame': ttk.Frame, 'text': tk.Text, 'scrollbar': ttk.Scrollbar}.

        Raises:
            UIError: If the scrolled text widget cannot be created.
        """
        try:
            frame = UIFactory.create_frame(parent, padding=0, relief=tk.SUNKEN, borderwidth=1)
            scrollbar = UIFactory.create_scrollbar(frame, orient=tk.VERTICAL)
            text = UIFactory.create_text(frame, height=height, width=width, wrap=wrap, state=state,
                                        yscrollcommand=scrollbar.set, **text_kwargs)
            scrollbar.config(command=text.yview)

            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            text.grid(row=0, column=0, sticky=tk.NSEW)
            scrollbar.grid(row=0, column=1, sticky=tk.NS)

            return {"frame": frame, "text": text, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled text widget"
            raise UIError(error_msg, component_name="ScrolledText", cause=e) from e
```

## src/ui/common/widget_factory.py

```python
"""Factory for creating basic UI widgets.

This module provides a factory for creating basic UI widgets with consistent styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, List, Union

from src.core.exceptions import UIError


class WidgetFactory:
    """Factory for creating basic UI widgets.
    
    This class provides methods for creating basic UI widgets with consistent
    styling and behavior.
    """
    
    @staticmethod
    def create_frame(parent: tk.Widget, padding: str = "10") -> ttk.Frame:
        """Create a frame with consistent styling.
        
        Args:
            parent: The parent widget
            padding: The padding to apply to the frame
            
        Returns:
            A configured frame
            
        Raises:
            UIError: If the frame cannot be created
        """
        try:
            frame = ttk.Frame(parent, padding=padding)
            return frame
        except Exception as e:
            error_msg = "Failed to create frame"
            raise UIError(error_msg, component_name="Frame", cause=e)
    
    @staticmethod
    def create_button(
        parent: tk.Widget, 
        text: str, 
        command: Callable[[], None],
        width: Optional[int] = None,
        state: str = tk.NORMAL
    ) -> ttk.Button:
        """Create a button with consistent styling.
        
        Args:
            parent: The parent widget
            text: The text to display on the button
            command: The callback to execute when the button is clicked
            width: The width of the button in characters
            state: The initial state of the button (NORMAL, DISABLED)
            
        Returns:
            A configured button
            
        Raises:
            UIError: If the button cannot be created
        """
        try:
            button = ttk.Button(parent, text=text, command=command, width=width, state=state)
            return button
        except Exception as e:
            error_msg = f"Failed to create button: {text}"
            raise UIError(error_msg, component_name="Button", cause=e)
    
    @staticmethod
    def create_label(
        parent: tk.Widget, 
        text: str,
        width: Optional[int] = None
    ) -> ttk.Label:
        """Create a label with consistent styling.
        
        Args:
            parent: The parent widget
            text: The text to display on the label
            width: The width of the label in characters
            
        Returns:
            A configured label
            
        Raises:
            UIError: If the label cannot be created
        """
        try:
            label = ttk.Label(parent, text=text, width=width)
            return label
        except Exception as e:
            error_msg = f"Failed to create label: {text}"
            raise UIError(error_msg, component_name="Label", cause=e)
    
    @staticmethod
    def create_entry(
        parent: tk.Widget, 
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        state: str = tk.NORMAL
    ) -> ttk.Entry:
        """Create an entry with consistent styling.
        
        Args:
            parent: The parent widget
            textvariable: The variable to bind to the entry
            width: The width of the entry in characters
            state: The initial state of the entry (NORMAL, DISABLED, READONLY)
            
        Returns:
            A configured entry
            
        Raises:
            UIError: If the entry cannot be created
        """
        try:
            entry = ttk.Entry(parent, textvariable=textvariable, width=width, state=state)
            return entry
        except Exception as e:
            error_msg = "Failed to create entry"
            raise UIError(error_msg, component_name="Entry", cause=e)
    
    @staticmethod
    def create_combobox(
        parent: tk.Widget, 
        textvariable: Optional[tk.StringVar] = None,
        values: Optional[List[str]] = None,
        width: Optional[int] = None,
        state: str = "readonly"
    ) -> ttk.Combobox:
        """Create a combobox with consistent styling.
        
        Args:
            parent: The parent widget
            textvariable: The variable to bind to the combobox
            values: The values to display in the combobox
            width: The width of the combobox in characters
            state: The initial state of the combobox (NORMAL, DISABLED, READONLY)
            
        Returns:
            A configured combobox
            
        Raises:
            UIError: If the combobox cannot be created
        """
        try:
            combobox = ttk.Combobox(
                parent, 
                textvariable=textvariable, 
                values=values or [], 
                width=width,
                state=state
            )
            return combobox
        except Exception as e:
            error_msg = "Failed to create combobox"
            raise UIError(error_msg, component_name="Combobox", cause=e)
    
    @staticmethod
    def create_listbox(
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.SINGLE
    ) -> tk.Listbox:
        """Create a listbox with consistent styling.
        
        Args:
            parent: The parent widget
            height: The height of the listbox in lines
            width: The width of the listbox in characters
            selectmode: The selection mode (SINGLE, MULTIPLE, EXTENDED, BROWSE)
            
        Returns:
            A configured listbox
            
        Raises:
            UIError: If the listbox cannot be created
        """
        try:
            listbox = tk.Listbox(parent, height=height, width=width, selectmode=selectmode)
            return listbox
        except Exception as e:
            error_msg = "Failed to create listbox"
            raise UIError(error_msg, component_name="Listbox", cause=e)
    
    @staticmethod
    def create_scrollbar(
        parent: tk.Widget, 
        orient: str = tk.VERTICAL,
        command: Optional[Callable] = None
    ) -> ttk.Scrollbar:
        """Create a scrollbar with consistent styling.
        
        Args:
            parent: The parent widget
            orient: The orientation of the scrollbar (VERTICAL, HORIZONTAL)
            command: The command to execute when the scrollbar is moved
            
        Returns:
            A configured scrollbar
            
        Raises:
            UIError: If the scrollbar cannot be created
        """
        try:
            scrollbar = ttk.Scrollbar(parent, orient=orient, command=command)
            return scrollbar
        except Exception as e:
            error_msg = "Failed to create scrollbar"
            raise UIError(error_msg, component_name="Scrollbar", cause=e)
    
    @staticmethod
    def create_text(
        parent: tk.Widget, 
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL
    ) -> tk.Text:
        """Create a text widget with consistent styling.
        
        Args:
            parent: The parent widget
            height: The height of the text widget in lines
            width: The width of the text widget in characters
            wrap: The wrap mode (WORD, CHAR, NONE)
            state: The initial state of the text widget (NORMAL, DISABLED)
            
        Returns:
            A configured text widget
            
        Raises:
            UIError: If the text widget cannot be created
        """
        try:
            text = tk.Text(parent, height=height, width=width, wrap=wrap, state=state)
            return text
        except Exception as e:
            error_msg = "Failed to create text widget"
            raise UIError(error_msg, component_name="Text", cause=e)

```

## src/ui/dialogs/action_editor_dialog.py

```python
"""Custom dialog for adding/editing workflow actions."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, List

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory # To get action types and create for validation
from src.ui.common.ui_factory import UIFactory
# Assuming Action parameter specs are defined or accessible
# For now, use the hardcoded spec within this file.
# from .action_param_specs import ACTION_PARAMS # Ideal approach

logger = logging.getLogger(__name__)

class ActionEditorDialog(tk.Toplevel):
    """
    A modal dialog window for creating or editing workflow action parameters.
    Dynamically displays input fields based on the selected action type.
    Includes improved validation feedback.
    """
    # Define parameter specs for each action type
    # Format: { 'param_key': {'label': 'Label Text', 'widget': 'widget_type', 'options': {<widget_options>}, 'required': bool, 'tooltip': '...' } }
    # Widget Types: 'entry', 'combobox', 'entry_with_browse', 'label_readonly', 'number_entry' (future), 'checkbox' (future)
    ACTION_PARAMS = {
        # ActionBase params (handled separately) - "name"
        "Navigate": {
            "url": {"label": "URL:", "widget": "entry", "required": True, "tooltip": "Full URL (e.g., https://example.com)"}
        },
        "Click": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the element"}
        },
        "Type": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the input field"},
            "value_type": {"label": "Value Type:", "widget": "combobox", "required": True, "options": {"values": ["text", "credential"]}, "tooltip": "Source of the text"},
            "value_key": {"label": "Text / Key:", "widget": "entry", "required": True, "tooltip": "Literal text or credential key (e.g., login.username)"}
        },
        "Wait": {
            "duration_seconds": {"label": "Duration (sec):", "widget": "entry", "required": True, "options": {"width": 10}, "tooltip": "Pause time in seconds (e.g., 1.5)"}
        },
        "Screenshot": {
            "file_path": {"label": "File Path:", "widget": "entry_with_browse", "required": True, "options": {"browse_type": "save_as"}, "tooltip": "Path to save the PNG file"}
        },
        "Conditional": {
            "condition_type": {"label": "Condition:", "widget": "combobox", "required": True, "options": {"values": ["element_present", "element_not_present", "variable_equals"]}, "tooltip": "Condition to evaluate"},
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": False, "tooltip": "Required for element conditions"}, # Required conditionally
            "variable_name": {"label": "Variable Name:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "expected_value": {"label": "Expected Value:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "true_branch": {"label": "True Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
            "false_branch": {"label": "False Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Loop": {
            "loop_type": {"label": "Loop Type:", "widget": "combobox", "required": True, "options": {"values": ["count", "for_each"]}, "tooltip": "Type of loop"},
            "count": {"label": "Iterations:", "widget": "entry", "required": False, "options": {"width": 10}, "tooltip": "Required for 'count' loop"},
            "list_variable_name": {"label": "List Variable:", "widget": "entry", "required": False, "tooltip": "Context variable name holding list for 'for_each'"},
            "loop_actions": {"label": "Loop Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "ErrorHandling": {
             "try_actions": {"label": "Try Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
             "catch_actions": {"label": "Catch Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Template": {
            "template_name": {"label": "Template Name:", "widget": "entry", "required": True, "tooltip": "Name of the saved template to execute"}
        }
        # Add new action types and their parameters here
    }


    def __init__(self, parent: tk.Widget, initial_data: Optional[Dict[str, Any]] = None):
        """Initialize the Action Editor Dialog."""
        super().__init__(parent)
        self.parent = parent
        self.initial_data = initial_data or {}
        self.result: Optional[Dict[str, Any]] = None

        self.is_edit_mode = bool(initial_data)
        self.title("Edit Action" if self.is_edit_mode else "Add Action")

        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._action_type_var = tk.StringVar(self)
        # Stores {'param_key': {'label': Label, 'widget': Widget, 'var': StringVar/IntVar, 'frame': Frame (optional)}}
        self._param_widgets: Dict[str, Dict[str, Any]] = {}
        self._param_frame: Optional[ttk.Frame] = None

        try:
            self._create_widgets()
            self._populate_initial_data()
        except Exception as e:
            logger.exception("Failed to create ActionEditorDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize action editor: {e}", parent=parent)
            self.destroy()
            return # Exit init if UI fails

        self.grab_set() # Make modal AFTER widgets potentially created
        self._center_window()
        # Don't call wait_window here; call show() externally


    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # --- Action Type ---
        row = 0
        UIFactory.create_label(main_frame, text="Action Type:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        action_types = ActionFactory.get_registered_action_types()
        if not action_types: raise UIError("No action types registered.")

        self.type_combobox = UIFactory.create_combobox(
            main_frame, textvariable=self._action_type_var, values=action_types, state="readonly", width=48
        )
        self.type_combobox.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        # Set initial type before trace, otherwise trace runs with default empty value first
        initial_type = self.initial_data.get("type", action_types[0])
        if initial_type not in action_types: initial_type = action_types[0]
        self._action_type_var.set(initial_type)
        self._action_type_var.trace_add("write", self._on_type_change)

        # --- Action Name ---
        row += 1
        # Use helper to create + store name widget references
        self._create_parameter_widget(main_frame, "name", "Action Name:", "entry", row=row, options={'width': 50})

        # --- Dynamic Parameter Frame ---
        row += 1
        self._param_frame = UIFactory.create_label_frame(main_frame, text="Parameters")
        self._param_frame.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self._param_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        row += 1
        button_frame = UIFactory.create_frame(main_frame, padding="5 0 0 0")
        button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))

        cancel_button = UIFactory.create_button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        ok_button = UIFactory.create_button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        self.bind('<Return>', lambda e: self._on_ok())
        self.bind('<Escape>', lambda e: self._on_cancel())

    def _populate_initial_data(self):
        """Fill fields with initial data if in edit mode."""
        # Name is populated separately
        name_var = self._param_widgets.get("name", {}).get("var")
        if name_var:
             # Use initial name if present, otherwise default to action type
             name_val = self.initial_data.get("name", self._action_type_var.get())
             name_var.set(name_val)

        # Populate dynamic fields based on current (initial) type
        self._update_parameter_fields() # This will now populate values for the initial type


    def _on_type_change(self, *args):
        """Callback when the action type combobox value changes."""
        action_type = self._action_type_var.get()
        # Update default name if name hasn't been manually changed
        name_var = self._param_widgets["name"]["var"]
        current_name = name_var.get()
        registered_types = ActionFactory.get_registered_action_types()
        if current_name in registered_types or not current_name: # Update if default or empty
             name_var.set(action_type)

        self._update_parameter_fields() # Regenerate fields for new type

    def _update_parameter_fields(self):
        """Clear and recreate parameter widgets based on selected action type."""
        if not self._param_frame: return
        action_type = self._action_type_var.get()
        logger.debug(f"Updating parameters for action type: {action_type}")

        # Clear existing dynamic widgets
        for widget in self._param_frame.winfo_children(): widget.destroy()
        # Clear non-name entries from _param_widgets dict
        keys_to_delete = [k for k in self._param_widgets if k != 'name']
        for key in keys_to_delete: del self._param_widgets[key]

        # --- Create Fields for Selected Action Type ---
        param_specs = self.ACTION_PARAMS.get(action_type, {})
        row = 0
        for key, spec in param_specs.items():
            initial_val = self.initial_data.get(key) if self.is_edit_mode else None
            # Create widget using helper, which now handles initial value setting
            self._create_parameter_widget(
                self._param_frame, key,
                spec.get("label", key.replace('_', ' ').title() + ":"),
                spec.get("widget", "entry"),
                row=row, options=spec.get("options", {}), initial_value=initial_val
            )
            row += 1

    def _create_parameter_widget(self, parent: tk.Widget, key: str, label_text: str, widget_type: str, row: int, options: Optional[Dict]=None, initial_value: Optional[Any]=None):
        """Helper to create label, input widget, store references, and set initial value."""
        options = options or {}
        var: Optional[tk.Variable] = None
        widget: Optional[tk.Widget] = None
        browse_btn: Optional[tk.Widget] = None
        width = options.get('width', 40)

        # Determine variable type and create var
        # Add more types like BooleanVar if Checkbox is used
        var = tk.StringVar(self)
        self._param_widgets[key] = {'label': None, 'widget': None, 'var': var, 'browse_btn': None} # Store var first

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        self._param_widgets[key]['label'] = label

        # Create widget
        widget_frame_needed = widget_type == "entry_with_browse"
        container = UIFactory.create_frame(parent, padding=0) if widget_frame_needed else parent

        if widget_type == "entry":
             widget = UIFactory.create_entry(container, textvariable=var, width=width, **options.get('config', {}))
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  container, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width-2
             )
        elif widget_type == "entry_with_browse":
             entry_frame = container # Use the frame created above
             entry_frame.columnconfigure(0, weight=1)
             widget = UIFactory.create_entry(entry_frame, textvariable=var, width=width-5)
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda k=key, btype=browse_type: self._browse_for_path(k, btype)
             browse_btn = UIFactory.create_button(entry_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
             widget = entry_frame # Main widget for grid placement is the frame
        elif widget_type == "label_readonly":
             display_text = ""
             if initial_value is not None and isinstance(initial_value, list):
                  display_text = f"({len(initial_value)} actions, edit in main list)"
             else:
                  display_text = str(initial_value) if initial_value is not None else "(Not editable)"
             var.set(display_text)
             widget = UIFactory.create_label(container, textvariable=var, anchor=tk.W, relief=tk.SUNKEN, borderwidth=1, padding=(3,1))
        # Add other widget types here

        # Grid the widget/container
        if widget:
            grid_target = container if widget_frame_needed else widget
            grid_target.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
            self._param_widgets[key]['widget'] = widget
            self._param_widgets[key]['browse_btn'] = browse_btn

        # Set initial value *after* widget creation
        if initial_value is not None and widget_type != "label_readonly":
             try: var.set(str(initial_value))
             except tk.TclError as e: logger.warning(f"Could not set initial value for '{key}': {e}")


    def _browse_for_path(self, setting_key: str, browse_type: str):
         """Handles browsing for file or directory for a parameter field."""
         if setting_key not in self._param_widgets: return
         var = self._param_widgets[setting_key]['var']
         current_path = var.get()
         initial_dir = os.path.abspath(".")
         if current_path:
              potential_dir = os.path.dirname(current_path)
              if os.path.isdir(potential_dir): initial_dir = potential_dir
              elif os.path.isfile(current_path): initial_dir = os.path.dirname(current_path)

         new_path: Optional[str] = None
         parent_window = self # Use dialog as parent
         try:
              if browse_type == "directory": new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory", parent=parent_window)
              elif browse_type == "open": new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File", parent=parent_window)
              elif browse_type == "save_as": new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File Path", parent=parent_window)

              if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
              else: logger.debug(f"Browse cancelled for {setting_key}")
         except Exception as e:
              logger.error(f"Error during file dialog browse: {e}", exc_info=True)
              messagebox.showerror("Browse Error", f"Could not open file dialog: {e}", parent=self)

    def _on_ok(self):
        """Validate data using ActionFactory/Action.validate and close dialog."""
        action_data = {"type": self._action_type_var.get()}
        validation_errors = {}
        action_params_spec = self.ACTION_PARAMS.get(action_data["type"], {})

        # Collect data and perform basic type conversion
        for key, widgets in self._param_widgets.items():
            spec = action_params_spec.get(key, {})
            widget_type = spec.get('widget', 'entry')

            if widget_type == "label_readonly": # Skip read-only display fields
                # Keep original nested data if editing, otherwise empty list
                action_data[key] = self.initial_data.get(key, []) if self.is_edit_mode else []
                continue

            try:
                value_str = widgets["var"].get()
                value: Any = value_str # Start as string

                # Attempt type conversion based on known param names or hints
                if key == "count":
                     try: value = int(value_str) if value_str else None # Allow empty count? No, validation handles it.
                     except (ValueError, TypeError): validation_errors[key] = "Iterations must be an integer."
                elif key == "duration_seconds":
                     try: value = float(value_str) if value_str else None
                     except (ValueError, TypeError): validation_errors[key] = "Duration must be a number."
                # Add boolean conversion if checkbox is added

                action_data[key] = value # Store potentially converted value

            except Exception as e:
                 logger.error(f"Error retrieving value for param '{key}': {e}")
                 validation_errors[key] = "Error retrieving value."

        if validation_errors:
             error_msg = "Input Errors:\n\n" + "\n".join([f"- {k}: {v}" for k, v in validation_errors.items()])
             messagebox.showerror("Validation Failed", error_msg, parent=self)
             return

        # --- Final validation using ActionFactory and Action's validate() ---
        try:
            # Create temporary instance to run validation
            temp_action = ActionFactory.create_action(action_data)
            temp_action.validate() # This should raise ValidationError if invalid
            logger.debug("Action data validated successfully using action class.")
            # If valid, set result and close
            self.result = action_data
            self.destroy()
        except ValidationError as e:
             logger.warning(f"Action validation failed: {e}. Data: {action_data}")
             # Display the specific validation error message from the action
             messagebox.showerror("Validation Failed", f"Invalid action parameters:\n\n{e}", parent=self)
        except (ActionError, TypeError) as e: # Catch factory errors too
             logger.error(f"Action creation/validation failed: {e}. Data: {action_data}")
             messagebox.showerror("Validation Failed", f"Could not validate action:\n\n{e}", parent=self)
        except Exception as e:
             logger.error(f"Unexpected error validating action: {e}. Data: {action_data}", exc_info=True)
             messagebox.showerror("Validation Error", f"Unexpected error validating action:\n\n{e}", parent=self)

    def _on_cancel(self):
        """Close the dialog without setting a result."""
        self.result = None
        self.destroy()

    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_win = self.parent.winfo_toplevel()
        parent_x = parent_win.winfo_rootx(); parent_y = parent_win.winfo_rooty()
        parent_w = parent_win.winfo_width(); parent_h = parent_win.winfo_height()
        win_w = self.winfo_reqwidth(); win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth(); screen_h = self.winfo_screenheight()
        pos_x = max(0, min(pos_x, screen_w - win_w)); pos_y = max(0, min(pos_y, screen_h - win_h))
        self.geometry(f"+{pos_x}+{pos_y}")


    def show(self) -> Optional[Dict[str, Any]]:
        """Make the dialog visible and wait for user interaction."""
        self.wait_window() # Blocks until destroy() is called
        return self.result
```

## src/ui/dialogs/credential_manager_dialog.py

```python
"""Custom dialog for managing credentials."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, List

# Core imports
from src.core.exceptions import CredentialError, ValidationError, UIError
from src.core.interfaces.service import ICredentialService
# UI imports
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class CredentialManagerDialog(tk.Toplevel):
    """
    A modal dialog window for listing, adding, and deleting credentials.
    Interacts with the ICredentialService.
    """

    def __init__(self, parent: tk.Widget, credential_service: ICredentialService):
        """
        Initialize the Credential Manager Dialog.

        Args:
            parent: The parent widget.
            credential_service: The service used to manage credentials.
        """
        super().__init__(parent)
        self.parent = parent
        self.credential_service = credential_service

        self.title("Manage Credentials")
        self.resizable(False, False)
        self.transient(parent) # Keep on top of parent
        self.protocol("WM_DELETE_WINDOW", self._on_close) # Handle window close

        # --- Internal State ---
        self._name_var = tk.StringVar(self)
        self._username_var = tk.StringVar(self)
        self._password_var = tk.StringVar(self)
        self._listbox: Optional[tk.Listbox] = None

        # --- Build UI ---
        try:
            self._create_widgets()
            self._load_credentials() # Initial population
        except Exception as e:
            logger.exception("Failed to create CredentialManagerDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize credential manager: {e}", parent=parent)
            self.destroy()
            return # Stop further execution if init fails

        self.grab_set() # Make modal AFTER widgets are created
        self._center_window()
        self.wait_window() # Block until destroyed


    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1) # Listbox expands

        # --- Add/Edit Form ---
        form_frame = UIFactory.create_label_frame(main_frame, text="Add/Edit Credential")
        form_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)

        UIFactory.create_label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        name_entry = UIFactory.create_entry(form_frame, textvariable=self._name_var)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        UIFactory.create_label(form_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        user_entry = UIFactory.create_entry(form_frame, textvariable=self._username_var)
        user_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        UIFactory.create_label(form_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        pass_entry = UIFactory.create_entry(form_frame, textvariable=self._password_var, show="*")
        pass_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        add_button = UIFactory.create_button(form_frame, text="Add/Update", command=self._on_add_update)
        add_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)
        clear_button = UIFactory.create_button(form_frame, text="Clear Fields", command=self._clear_fields)
        clear_button.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

        # --- Credential List ---
        list_frame = UIFactory.create_label_frame(main_frame, text="Existing Credentials")
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        list_scrolled = UIFactory.create_scrolled_listbox(list_frame, height=8, selectmode=tk.BROWSE)
        self._listbox = list_scrolled["listbox"]
        list_scrolled["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self._listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # --- List Buttons ---
        list_button_frame = UIFactory.create_frame(main_frame)
        list_button_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        delete_button = UIFactory.create_button(list_button_frame, text="Delete Selected", command=self._on_delete)
        delete_button.pack(pady=5)

        close_button = UIFactory.create_button(list_button_frame, text="Close", command=self._on_close)
        close_button.pack(pady=5, side=tk.BOTTOM) # Place Close at the bottom


    def _load_credentials(self):
        """Load credential names from the service and populate the listbox."""
        if not self._listbox: return
        try:
             self._listbox.delete(0, tk.END) # Clear existing items
             credential_names = self.credential_service.list_credentials()
             for name in sorted(credential_names):
                  self._listbox.insert(tk.END, name)
             logger.debug(f"Loaded {len(credential_names)} credentials into list.")
        except Exception as e:
             logger.error(f"Failed to load credentials into dialog: {e}", exc_info=True)
             messagebox.showerror("Load Error", f"Could not load credentials: {e}", parent=self)

    def _on_list_select(self, event: Optional[tk.Event] = None):
        """Handle selection change in the listbox to populate edit fields."""
        if not self._listbox: return
        selection_indices = self._listbox.curselection()
        if not selection_indices:
            self._clear_fields() # Clear fields if nothing selected
            return

        selected_name = self._listbox.get(selection_indices[0])
        try:
            # Fetch details - WARNING: This retrieves the HASH, not the original password.
            # Editing requires re-entering the password.
            cred_details = self.credential_service.get_credential(selected_name)
            if cred_details:
                self._name_var.set(cred_details.get("name", ""))
                self._username_var.set(cred_details.get("username", ""))
                # DO NOT set the password field with the hash. Leave it blank for editing.
                self._password_var.set("")
                logger.debug(f"Populated fields for editing '{selected_name}' (password field cleared).")
            else:
                 logger.warning(f"Selected credential '{selected_name}' not found by service.")
                 self._clear_fields()
        except Exception as e:
            logger.error(f"Failed to get details for credential '{selected_name}': {e}", exc_info=True)
            messagebox.showerror("Load Error", f"Could not load details for '{selected_name}': {e}", parent=self)
            self._clear_fields()


    def _clear_fields(self):
        """Clear the input fields."""
        self._name_var.set("")
        self._username_var.set("")
        self._password_var.set("")
        # Deselect listbox item if needed
        if self._listbox: self._listbox.selection_clear(0, tk.END)
        logger.debug("Credential input fields cleared.")

    def _on_add_update(self):
        """Handle Add/Update button click."""
        name = self._name_var.get().strip()
        username = self._username_var.get().strip()
        password = self._password_var.get() # Get password as entered

        if not name or not username or not password:
            messagebox.showerror("Input Error", "Name, Username, and Password cannot be empty.", parent=self)
            return

        try:
            # Check if it exists (for logging/confirmation message)
            # exists = self.credential_service.get_credential(name) is not None
            # Service's create_credential should handle "already exists" error if needed,
            # or we assume save() in repo handles UPSERT. Let's rely on create failing if needed.

            # Attempt to create/update via service (which handles hashing)
            # A combined save/update method in the service might be cleaner.
            # For now, try create, if fails assume update? No, better to use repo UPSERT.
            # Let's assume service needs explicit create/update or repo handles UPSERT.
            # Assuming repo handles UPSERT via save()
            self.credential_service.create_credential(name, username, password) # This might fail if exists
            # Or use a save method if available in service/repo that does UPSERT logic:
            # self.credential_service.save_credential({"name": name, "username": username, "password": password})

            logger.info(f"Credential '{name}' added/updated successfully.")
            messagebox.showinfo("Success", f"Credential '{name}' saved successfully.", parent=self)
            self._clear_fields()
            self._load_credentials() # Refresh list
        except (ValidationError, CredentialError, RepositoryError) as e:
             logger.error(f"Failed to save credential '{name}': {e}")
             messagebox.showerror("Save Error", f"Failed to save credential:\n{e}", parent=self)
        except Exception as e:
             logger.exception(f"Unexpected error saving credential '{name}'.")
             messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}", parent=self)


    def _on_delete(self):
        """Handle Delete Selected button click."""
        if not self._listbox: return
        selection_indices = self._listbox.curselection()
        if not selection_indices:
            messagebox.showwarning("Delete Error", "Please select a credential to delete.", parent=self)
            return

        selected_name = self._listbox.get(selection_indices[0])

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete credential '{selected_name}'?", parent=self):
            return

        try:
            deleted = self.credential_service.delete_credential(selected_name)
            if deleted:
                logger.info(f"Credential '{selected_name}' deleted.")
                messagebox.showinfo("Success", f"Credential '{selected_name}' deleted.", parent=self)
                self._clear_fields()
                self._load_credentials() # Refresh list
            else:
                # Should not happen if item was selected from list, but handle anyway
                logger.warning(f"Attempted to delete '{selected_name}' but service reported not found.")
                messagebox.showerror("Delete Error", f"Credential '{selected_name}' could not be found for deletion.", parent=self)
                self._load_credentials() # Refresh list in case of inconsistency
        except (ValidationError, CredentialError, RepositoryError) as e:
             logger.error(f"Failed to delete credential '{selected_name}': {e}")
             messagebox.showerror("Delete Error", f"Failed to delete credential:\n{e}", parent=self)
        except Exception as e:
             logger.exception(f"Unexpected error deleting credential '{selected_name}'.")
             messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}", parent=self)


    def _on_close(self):
        """Handle dialog closing."""
        logger.debug("Credential Manager dialog closed.")
        self.grab_release()
        self.destroy()

    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_geo = self.parent.winfo_geometry().split('+')
        parent_w = int(parent_geo[0].split('x')[0])
        parent_h = int(parent_geo[0].split('x')[1])
        parent_x = int(parent_geo[1])
        parent_y = int(parent_geo[2])
        win_w = self.winfo_reqwidth()
        win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if pos_x + win_w > screen_w: pos_x = screen_w - win_w
        if pos_y + win_h > screen_h: pos_y = screen_h - win_h
        if pos_x < 0: pos_x = 0
        if pos_y < 0: pos_y = 0
        self.geometry(f"+{pos_x}+{pos_y}")
```

## src/ui/views/workflow_editor_view.py

```python
"""Workflow editor view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.exceptions import UIError

# UI elements
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
# Import the new dialog
from src.ui.dialogs.action_editor_dialog import ActionEditorDialog


class WorkflowEditorView(BaseView, IWorkflowEditorView):
    """
    View component for the workflow editor. Displays workflows and actions,
    and forwards user interactions to the WorkflowEditorPresenter.
    Uses ActionEditorDialog for adding/editing actions.
    """

    def __init__(self, root: tk.Widget, presenter: IWorkflowEditorPresenter):
        """
        Initialize the workflow editor view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: IWorkflowEditorPresenter # Type hint

        # Widgets specific to this view
        self.workflow_list_widget: Optional[tk.Listbox] = None
        self.action_list_widget: Optional[tk.Listbox] = None
        self.new_button: Optional[ttk.Button] = None
        self.save_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None
        self.add_action_button: Optional[ttk.Button] = None
        self.edit_action_button: Optional[ttk.Button] = None
        self.delete_action_button: Optional[ttk.Button] = None

        try:
            self._create_widgets()
            self.logger.info("WorkflowEditorView initialized successfully.")
        except Exception as e:
            error_msg = "Failed to create WorkflowEditorView widgets"
            self.logger.exception(error_msg)
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the editor view within self.main_frame."""
        self.logger.debug("Creating editor widgets.")

        # Configure grid weights for self.main_frame resizing
        self.main_frame.rowconfigure(0, weight=1) # Lists take vertical space
        self.main_frame.rowconfigure(1, weight=0) # Buttons fixed size
        self.main_frame.columnconfigure(0, weight=1, minsize=200) # Workflow list column
        self.main_frame.columnconfigure(1, weight=3, minsize=350) # Action list column

        # --- Workflow List Section ---
        wf_list_frame = UIFactory.create_label_frame(self.main_frame, text="Workflows")
        wf_list_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5), pady=(0, 5))
        wf_list_frame.rowconfigure(0, weight=1)
        wf_list_frame.columnconfigure(0, weight=1)

        wf_scrolled_list = UIFactory.create_scrolled_listbox(wf_list_frame, height=15, selectmode=tk.BROWSE)
        self.workflow_list_widget = wf_scrolled_list["listbox"]
        wf_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self.workflow_list_widget.bind("<<ListboxSelect>>", self._on_workflow_selected)

        # --- Workflow Buttons Section ---
        wf_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0")
        wf_button_frame.grid(row=1, column=0, sticky=tk.EW, padx=(0, 5))

        self.new_button = UIFactory.create_button(wf_button_frame, text="New", command=self._on_new_workflow)
        self.new_button.pack(side=tk.LEFT, padx=2)

        self.save_button = UIFactory.create_button(wf_button_frame, text="Save", command=self._on_save_workflow, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=2)

        self.delete_button = UIFactory.create_button(wf_button_frame, text="Delete", command=self._on_delete_workflow, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=2)

        # --- Action List Section ---
        action_list_frame = UIFactory.create_label_frame(self.main_frame, text="Actions")
        action_list_frame.grid(row=0, column=1, sticky=tk.NSEW, pady=(0, 5))
        action_list_frame.rowconfigure(0, weight=1)
        action_list_frame.columnconfigure(0, weight=1)

        action_scrolled_list = UIFactory.create_scrolled_listbox(action_list_frame, height=15, selectmode=tk.BROWSE)
        self.action_list_widget = action_scrolled_list["listbox"]
        action_scrolled_list["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self.action_list_widget.bind("<<ListboxSelect>>", self._on_action_selected)
        self.action_list_widget.bind("<Double-1>", self._on_edit_action)

        # --- Action Buttons Section ---
        action_button_frame = UIFactory.create_frame(self.main_frame, padding="5 0 0 0")
        action_button_frame.grid(row=1, column=1, sticky=tk.EW)

        self.add_action_button = UIFactory.create_button(action_button_frame, text="Add Action", command=self._on_add_action, state=tk.DISABLED)
        self.add_action_button.pack(side=tk.LEFT, padx=2)

        self.edit_action_button = UIFactory.create_button(action_button_frame, text="Edit Action", command=self._on_edit_action, state=tk.DISABLED)
        self.edit_action_button.pack(side=tk.LEFT, padx=2)

        self.delete_action_button = UIFactory.create_button(action_button_frame, text="Delete Action", command=self._on_delete_action, state=tk.DISABLED)
        self.delete_action_button.pack(side=tk.LEFT, padx=2)

        self.logger.debug("Editor widgets created.")

    # --- IWorkflowEditorView Implementation ---

    def set_workflow_list(self, workflow_names: List[str]) -> None:
        """Populate the workflow listbox."""
        if not self.workflow_list_widget: return
        self.logger.debug(f"Setting workflow list with {len(workflow_names)} items.")
        selected_name = self.get_selected_workflow_name()
        self.workflow_list_widget.delete(0, tk.END)
        sorted_names = sorted(workflow_names)
        for name in sorted_names:
            self.workflow_list_widget.insert(tk.END, name)
        if selected_name in sorted_names:
             try:
                  list_items = self.workflow_list_widget.get(0, tk.END)
                  idx = list_items.index(selected_name)
                  self.workflow_list_widget.selection_set(idx)
                  self.workflow_list_widget.activate(idx)
                  self.workflow_list_widget.see(idx)
             except (ValueError, tk.TclError): pass
        self._update_workflow_button_states() # Update states after list changes


    def set_action_list(self, actions_display: List[str]) -> None:
        """Display the actions for the current workflow."""
        if not self.action_list_widget: return
        self.logger.debug(f"Setting action list with {len(actions_display)} items.")
        selected_index = self.get_selected_action_index()
        self.action_list_widget.delete(0, tk.END)
        for display_text in actions_display:
            self.action_list_widget.insert(tk.END, display_text)
        if selected_index is not None and selected_index < len(actions_display):
             try:
                  self.action_list_widget.selection_set(selected_index)
                  self.action_list_widget.activate(selected_index)
                  self.action_list_widget.see(selected_index)
             except tk.TclError: pass
        self._update_action_button_states() # Update states after list changes

    def get_selected_workflow_name(self) -> Optional[str]:
        """Get the name of the currently selected workflow."""
        if not self.workflow_list_widget: return None
        selection_indices = self.workflow_list_widget.curselection()
        return self.workflow_list_widget.get(selection_indices[0]) if selection_indices else None

    def get_selected_action_index(self) -> Optional[int]:
         """Get the index of the action currently selected in the list."""
         if not self.action_list_widget: return None
         selection_indices = self.action_list_widget.curselection()
         return selection_indices[0] if selection_indices else None

    def show_action_editor(self, action_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
         """Show the dedicated ActionEditorDialog to add/edit an action."""
         self.logger.debug(f"Showing ActionEditorDialog. Initial data: {action_data}")
         try:
              # Use the new custom dialog, passing main_frame as parent
              dialog = ActionEditorDialog(self.main_frame, initial_data=action_data)
              result_data = dialog.show() # show() blocks and returns data or None
              self.logger.debug(f"ActionEditorDialog returned: {result_data}")
              return result_data
         except Exception as e:
              self.logger.error(f"Error showing ActionEditorDialog: {e}", exc_info=True)
              self.display_error("Dialog Error", f"Could not open action editor: {e}")
              return None

    def prompt_for_workflow_name(self, title: str, prompt: str) -> Optional[str]:
         """Prompt user for a workflow name."""
         return super().prompt_for_input(title, prompt)

    def clear(self) -> None:
        """Clear the workflow and action lists."""
        self.logger.debug("Clearing editor view.")
        if self.workflow_list_widget: self.workflow_list_widget.delete(0, tk.END)
        if self.action_list_widget: self.action_list_widget.delete(0, tk.END)
        self._update_workflow_button_states()
        self._update_action_button_states()
        super().clear() # Call base clear for status bar etc.

    # --- Internal Event Handlers ---

    def _on_workflow_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when a workflow is selected."""
        selected_name = self.get_selected_workflow_name()
        self.logger.debug(f"Workflow selected: {selected_name}")
        self._update_workflow_button_states()
        self._update_action_button_states() # Update action buttons based on workflow selection
        if selected_name:
            self.presenter.load_workflow(selected_name)
        else:
            self.set_action_list([]) # Clear action list if nothing selected


    def _on_action_selected(self, event: Optional[tk.Event] = None) -> None:
        """Callback when an action is selected."""
        self._update_action_button_states()

    def _on_new_workflow(self) -> None:
        """Handle 'New Workflow' button press."""
        self.logger.debug("New workflow button pressed.")
        name = self.prompt_for_workflow_name("New Workflow", "Enter name for new workflow:")
        if name:
            self.presenter.create_new_workflow(name)
        else:
             self.logger.debug("New workflow cancelled by user.")

    def _on_save_workflow(self) -> None:
        """Handle 'Save Workflow' button press."""
        self.logger.debug("Save workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
             # Tell presenter to save the currently loaded state
             self.presenter.save_workflow(name) # Presenter holds the actions
        else:
             self.logger.warning("Save button pressed but no workflow selected.")
             self.set_status("Please select a workflow to save.")


    def _on_delete_workflow(self) -> None:
        """Handle 'Delete Workflow' button press."""
        self.logger.debug("Delete workflow button pressed.")
        name = self.get_selected_workflow_name()
        if name:
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete workflow '{name}'? This cannot be undone."):
                self.presenter.delete_workflow(name) # Delegate to presenter
        else:
             self.logger.warning("Delete button pressed but no workflow selected.")
             self.set_status("Please select a workflow to delete.")

    def _on_add_action(self) -> None:
        """Handle 'Add Action' button press."""
        self.logger.debug("Add action button pressed.")
        if self.get_selected_workflow_name() is None:
             self.display_message("Add Action", "Please select or create a workflow first.")
             return
        # Use the new dialog
        action_data = self.show_action_editor() # No initial data for add
        if action_data:
            # Delegate adding to presenter (updates internal state)
            self.presenter.add_action(action_data)
        else:
             self.logger.debug("Add action cancelled by user.")

    def _on_edit_action(self, event: Optional[tk.Event] = None) -> None: # Can be called by button or double-click
        """Handle 'Edit Action' button press or double-click."""
        self.logger.debug("Edit action triggered.")
        index = self.get_selected_action_index()
        if index is not None:
            # Get current data from presenter's internal state
            current_action_data = self.presenter.get_action_data(index)
            if current_action_data:
                 # Use the new dialog with initial data
                 new_action_data = self.show_action_editor(current_action_data)
                 if new_action_data:
                      # Delegate update to presenter (updates internal state)
                      self.presenter.update_action(index, new_action_data)
                 else:
                      self.logger.debug("Edit action cancelled by user.")
            else:
                 # Error handled by get_action_data, but show msg just in case
                 self.display_error("Edit Error", f"Could not retrieve data for action at index {index}.")
        else:
             self.logger.warning("Edit action triggered but no action selected.")
             self.set_status("Please select an action to edit.")


    def _on_delete_action(self) -> None:
        """Handle 'Delete Action' button press."""
        self.logger.debug("Delete action button pressed.")
        index = self.get_selected_action_index()
        if index is not None:
            action_name_display = self.action_list_widget.get(index) if self.action_list_widget else f"Action {index+1}"
            if self.confirm_action("Confirm Delete", f"Are you sure you want to delete '{action_name_display}'?"):
                # Delegate deletion to presenter (updates internal state)
                self.presenter.delete_action(index)
        else:
             self.logger.warning("Delete action button pressed but no action selected.")
             self.set_status("Please select an action to delete.")

    # --- Widget State Management ---

    def _update_workflow_button_states(self) -> None:
        """Enable/disable workflow buttons based on selection."""
        selected = self.get_selected_workflow_name() is not None
        save_state = tk.NORMAL if selected else tk.DISABLED
        delete_state = tk.NORMAL if selected else tk.DISABLED

        if self.save_button: self.save_button.config(state=save_state)
        if self.delete_button: self.delete_button.config(state=delete_state)
        if self.new_button: self.new_button.config(state=tk.NORMAL)


    def _update_action_button_states(self, workflow_selected: Optional[bool] = None) -> None:
        """Enable/disable action buttons based on selections."""
        if workflow_selected is None:
             workflow_selected = self.get_selected_workflow_name() is not None
        action_selected = self.get_selected_action_index() is not None

        add_state = tk.NORMAL if workflow_selected else tk.DISABLED
        edit_state = tk.NORMAL if action_selected else tk.DISABLED
        delete_state = tk.NORMAL if action_selected else tk.DISABLED

        if self.add_action_button: self.add_action_button.config(state=add_state)
        if self.edit_action_button: self.edit_action_button.config(state=edit_state)
        if self.delete_action_button: self.delete_action_button.config(state=delete_state)
```

## src/ui/presenters/workflow_editor_presenter.py

```python
"""Workflow editor presenter implementation for AutoQliq."""

import logging
from typing import List, Dict, Any, Optional

# Core dependencies
from src.core.interfaces import IAction
from src.core.interfaces.service import IWorkflowService # Use Service Interface
from src.core.exceptions import WorkflowError, ActionError, ValidationError, AutoQliqError

# UI dependencies
from src.ui.interfaces.presenter import IWorkflowEditorPresenter
from src.ui.interfaces.view import IWorkflowEditorView
from src.ui.presenters.base_presenter import BasePresenter
# Use ActionFactory directly for creating/validating action data from UI dialog
from src.core.actions.factory import ActionFactory


class WorkflowEditorPresenter(BasePresenter[IWorkflowEditorView], IWorkflowEditorPresenter):
    """
    Presenter for the workflow editor view. Handles logic for creating, loading,
    saving workflows, and managing their actions by interacting with the WorkflowService.
    """

    def __init__(self, workflow_service: IWorkflowService, view: Optional[IWorkflowEditorView] = None):
        """
        Initialize the presenter.

        Args:
            workflow_service: The service handling workflow business logic and persistence.
            view: The associated view instance (optional).
        """
        super().__init__(view)
        if workflow_service is None:
             raise ValueError("Workflow service cannot be None.")
        self.workflow_service = workflow_service
        # Store the currently loaded workflow actions in memory for editing
        self._current_workflow_name: Optional[str] = None
        self._current_actions: List[IAction] = [] # Presenter holds domain objects
        self.logger.info("WorkflowEditorPresenter initialized.")

    def set_view(self, view: IWorkflowEditorView) -> None:
        """Set the view and perform initial population."""
        super().set_view(view)
        self.initialize_view()

    @BasePresenter.handle_errors("Initializing editor view")
    def initialize_view(self) -> None:
        """Populate the view with initial data (workflow list)."""
        if not self.view: return
        self.logger.debug("Initializing editor view...")
        workflows = self.get_workflow_list() # Uses service
        self.view.set_workflow_list(workflows or [])
        self._update_action_list_display() # Show empty actions initially
        self.view.set_status("Editor ready. Select a workflow or create a new one.")
        self.logger.debug("Editor view initialized.")

    @BasePresenter.handle_errors("Getting workflow list")
    def get_workflow_list(self) -> List[str]:
        """Get the list of available workflow names via the service."""
        self.logger.debug("Fetching workflow list from service.")
        return self.workflow_service.list_workflows()

    @BasePresenter.handle_errors("Loading workflow")
    def load_workflow(self, name: str) -> None:
        """Load a workflow via the service and update the view."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Loading workflow: {name}")
        # Service handles interaction with repository
        actions = self.workflow_service.get_workflow(name) # Raises WorkflowError if not found etc.
        self._current_workflow_name = name
        self._current_actions = actions if actions else [] # Ensure it's a list
        self._update_action_list_display()
        self.view.set_status(f"Workflow '{name}' loaded with {len(self._current_actions)} actions.")
        self.logger.info(f"Successfully loaded workflow '{name}'.")

    @BasePresenter.handle_errors("Saving workflow")
    def save_workflow(self, name: Optional[str] = None, actions_data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save the current workflow actions via the service."""
        if not self.view: return

        target_name = name or self._current_workflow_name
        if not target_name:
             raise WorkflowError("Cannot save workflow without a name. Load or create a workflow first.")

        self.logger.info(f"Attempting to save workflow: {target_name}")
        actions_to_save = self._current_actions

        # Service handles validation, serialization, saving. Decorator catches errors.
        success = self.workflow_service.save_workflow(target_name, actions_to_save)
        if success: # Service method returns bool now
            self._current_workflow_name = target_name
            self.view.set_status(f"Workflow '{target_name}' saved successfully.")
            self.logger.info(f"Successfully saved workflow '{target_name}'.")
            workflows = self.get_workflow_list()
            if self.view: self.view.set_workflow_list(workflows or [])


    @BasePresenter.handle_errors("Creating new workflow")
    def create_new_workflow(self, name: str) -> None:
        """Create a new, empty workflow via the service."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Creating new workflow: {name}")
        success = self.workflow_service.create_workflow(name) # Service raises errors if exists etc.
        if success:
            self.view.set_status(f"Created new workflow: '{name}'.")
            self.logger.info(f"Successfully created workflow '{name}'.")
            workflows = self.get_workflow_list()
            if self.view:
                 self.view.set_workflow_list(workflows or [])
                 self.load_workflow(name) # Load the newly created empty workflow


    @BasePresenter.handle_errors("Deleting workflow")
    def delete_workflow(self, name: str) -> None:
        """Delete a workflow via the service."""
        if not self.view: return
        if not name:
             raise ValidationError("Workflow name cannot be empty.", field_name="workflow_name")

        self.logger.info(f"Deleting workflow: {name}")
        deleted = self.workflow_service.delete_workflow(name) # Service raises errors
        if deleted:
            self.view.set_status(f"Workflow '{name}' deleted.")
            self.logger.info(f"Successfully deleted workflow '{name}'.")
            if self._current_workflow_name == name:
                 self._current_workflow_name = None
                 self._current_actions = []
                 self._update_action_list_display()
            workflows = self.get_workflow_list()
            if self.view: self.view.set_workflow_list(workflows or [])
        else:
             # Service returned False (likely not found)
             raise WorkflowError(f"Workflow '{name}' not found, cannot delete.", workflow_name=name)


    # --- Action Management (Operate on internal state, save separately) ---

    def add_action(self, action_data: Dict[str, Any]) -> None:
        """Add a new action to the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot add action."), "adding action")
             return

        self.logger.debug(f"Attempting to add action to '{self._current_workflow_name}': {action_data.get('type')}")
        try:
            new_action = ActionFactory.create_action(action_data) # Raises ActionError/ValidationError
            new_action.validate() # Raises ValidationError
            self._current_actions.append(new_action)
            self._update_action_list_display()
            self.view.set_status(f"Action '{new_action.name}' added to '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Added action {new_action.action_type} to internal list for '{self._current_workflow_name}'.")
        except (ActionError, ValidationError) as e:
             self._handle_error(e, "adding action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error adding action.", cause=e), "adding action")


    def update_action(self, index: int, action_data: Dict[str, Any]) -> None:
        """Update an action in the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot update action."), "updating action")
             return
        if not (0 <= index < len(self._current_actions)):
            self._handle_error(IndexError(f"Invalid action index for update: {index}"), "updating action")
            return

        self.logger.debug(f"Attempting to update action at index {index} in '{self._current_workflow_name}'")
        try:
            updated_action = ActionFactory.create_action(action_data) # Raises ActionError/ValidationError
            updated_action.validate() # Raises ValidationError
            self._current_actions[index] = updated_action
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{updated_action.name}') updated in '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Updated action at index {index} in internal list for '{self._current_workflow_name}'.")
        except (ActionError, ValidationError) as e:
            self._handle_error(e, "updating action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error updating action.", cause=e), "updating action")


    def delete_action(self, index: int) -> None:
        """Delete an action from the current in-memory list and update view."""
        if not self.view: return
        if self._current_workflow_name is None:
             self._handle_error(WorkflowError("No workflow loaded. Cannot delete action."), "deleting action")
             return
        if not (0 <= index < len(self._current_actions)):
             self._handle_error(IndexError(f"Invalid action index for delete: {index}"), "deleting action")
             return

        self.logger.debug(f"Attempting to delete action at index {index} from '{self._current_workflow_name}'")
        try:
            deleted_action = self._current_actions.pop(index)
            self._update_action_list_display()
            self.view.set_status(f"Action {index+1} ('{deleted_action.name}') deleted from '{self._current_workflow_name}' (unsaved).")
            self.logger.info(f"Deleted action at index {index} from internal list for '{self._current_workflow_name}'.")
        except IndexError:
             self._handle_error(IndexError(f"Action index {index} out of range during delete."), "deleting action")
        except Exception as e:
             self._handle_error(AutoQliqError("Unexpected error deleting action.", cause=e), "deleting action")


    def get_action_data(self, index: int) -> Optional[Dict[str, Any]]:
         """Get the data dictionary for the action at the specified index."""
         if not (0 <= index < len(self._current_actions)):
              self.logger.warning(f"Attempted to get action data for invalid index: {index}")
              return None
         try:
              action = self._current_actions[index]
              return action.to_dict()
         except Exception as e:
              self._handle_error(AutoQliqError(f"Failed to get dictionary for action at index {index}", cause=e), "getting action data")
              return None

    # --- Helper Methods ---

    def _update_action_list_display(self) -> None:
        """Format the current actions and tell the view to display them."""
        if not self.view: return
        try:
             # Use str(action) which should provide a user-friendly summary
             actions_display = [f"{i+1}: {str(action)}" for i, action in enumerate(self._current_actions)]
             self.view.set_action_list(actions_display)
             self.logger.debug(f"Updated action list display in view for '{self._current_workflow_name}'. Actions: {len(actions_display)}")
        except Exception as e:
            # Use the internal error handler which will log and show error in view
            self._handle_error(UIError("Failed to update action list display.", cause=e), "updating action list")
```

## src/ui/views/settings_view.py

```python
"""Settings view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, filedialog
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.exceptions import UIError
from src.config import RepositoryType, BrowserTypeStr # Import literals

# UI elements
from src.ui.interfaces.presenter import IPresenter # Use base presenter interface for now
from src.ui.interfaces.view import IView # Use base view interface
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
# Type hint for the specific presenter
from src.ui.presenters.settings_presenter import SettingsPresenter, ISettingsView


class SettingsView(BaseView, ISettingsView):
    """
    View component for managing application settings. Allows users to view and
    modify settings stored in config.ini.
    """
    # Define allowed values for dropdowns
    REPO_TYPES: List[RepositoryType] = ["file_system", "database"]
    BROWSER_TYPES: List[BrowserTypeStr] = ["chrome", "firefox", "edge", "safari"]
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, root: tk.Widget, presenter: SettingsPresenter):
        """
        Initialize the settings view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: SettingsPresenter # Type hint

        # Dictionary to hold the tk.StringVar instances for settings
        self.setting_vars: Dict[str, tk.StringVar] = {}

        try:
            self._create_widgets()
            self.logger.info("SettingsView initialized successfully.")
            # Initial population happens via presenter.initialize_view -> presenter.load_settings -> view.set_settings_values
        except Exception as e:
            error_msg = "Failed to create SettingsView widgets"
            self.logger.exception(error_msg) # Log traceback
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="SettingsView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the settings view."""
        self.logger.debug("Creating settings widgets.")
        # Use grid layout within the main_frame provided by BaseView
        content_frame = UIFactory.create_frame(self.main_frame, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(1, weight=1) # Allow entry/path fields to expand

        row_index = 0

        # --- General Settings ---
        general_frame = UIFactory.create_label_frame(content_frame, text="General")
        general_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        general_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(general_frame, 0, "Log Level:", "log_level", "combobox", options={'values': self.LOG_LEVELS})
        self._create_setting_row(general_frame, 1, "Log File:", "log_file", "entry_with_browse", options={'browse_type': 'save_as'})

        # --- Repository Settings ---
        repo_frame = UIFactory.create_label_frame(content_frame, text="Repository")
        repo_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        repo_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(repo_frame, 0, "Storage Type:", "repository_type", "combobox", options={'values': self.REPO_TYPES})
        self._create_setting_row(repo_frame, 1, "DB Path:", "db_path", "entry_with_browse", options={'browse_type': 'save_as', 'label_note': '(Used if type=database)'})
        self._create_setting_row(repo_frame, 2, "Workflows Path:", "workflows_path", "entry_with_browse", options={'browse_type': 'directory', 'label_note': '(Used if type=file_system)'})
        self._create_setting_row(repo_frame, 3, "Credentials Path:", "credentials_path", "entry_with_browse", options={'browse_type': 'save_as', 'label_note': '(Used if type=file_system)'})

        # --- WebDriver Settings ---
        wd_frame = UIFactory.create_label_frame(content_frame, text="WebDriver")
        wd_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        wd_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(wd_frame, 0, "Default Browser:", "default_browser", "combobox", options={'values': self.BROWSER_TYPES})
        self._create_setting_row(wd_frame, 1, "Implicit Wait (sec):", "implicit_wait", "entry", options={'width': 5})
        self._create_setting_row(wd_frame, 2, "ChromeDriver Path:", "chrome_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 3, "GeckoDriver Path (FF):", "firefox_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 4, "EdgeDriver Path:", "edge_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})

        # --- Action Buttons ---
        row_index += 1
        button_frame = UIFactory.create_frame(content_frame, padding="10 10 0 0") # Padding top only
        button_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.E, pady=10)

        save_btn = UIFactory.create_button(button_frame, text="Save Settings", command=self._on_save)
        save_btn.pack(side=tk.RIGHT, padx=5)
        reload_btn = UIFactory.create_button(button_frame, text="Reload Settings", command=self._on_reload)
        reload_btn.pack(side=tk.RIGHT, padx=5)


        self.logger.debug("Settings widgets created.")

    def _create_setting_row(self, parent: tk.Widget, row: int, label_text: str, setting_key: str, widget_type: str, options: Optional[Dict]=None):
        """Helper to create a label and input widget for a setting."""
        options = options or {}
        var = tk.StringVar()
        self.setting_vars[setting_key] = var

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        # Add tooltip/note if provided
        if options.get('label_note'):
             # Simple way: modify label text. Better way: use a tooltip library.
             label.config(text=f"{label_text} {options['label_note']}")


        widget_frame = UIFactory.create_frame(parent, padding=0) # Frame to hold widget + potential button
        widget_frame.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        widget_frame.columnconfigure(0, weight=1) # Make widget expand

        widget: Optional[tk.Widget] = None

        width = options.get('width', 40) # Default width slightly smaller
        if widget_type == "entry":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width)
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  widget_frame, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width
             )
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "entry_with_browse":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width-5) # Adjust width for button
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda key=setting_key, btype=browse_type: self._browse_for_path(key, btype)
             browse_btn = UIFactory.create_button(widget_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
        else:
             self.logger.error(f"Unsupported widget type '{widget_type}' for setting '{setting_key}'")


    def _browse_for_path(self, setting_key: str, browse_type: str):
        """Handles browsing for file or directory."""
        self.logger.debug(f"Browsing for path: Key={setting_key}, Type={browse_type}")
        if setting_key not in self.setting_vars: return
        var = self.setting_vars[setting_key]
        current_path = var.get()
        # Robust initial directory finding
        initial_dir = os.path.abspath(".") # Default to current dir
        if current_path:
             potential_dir = os.path.dirname(current_path)
             if os.path.isdir(potential_dir):
                  initial_dir = potential_dir
             elif os.path.isfile(current_path): # If current path is file, use its dir
                  initial_dir = os.path.dirname(current_path)

        new_path: Optional[str] = None
        parent_window = self.main_frame.winfo_toplevel() # Use toplevel as parent
        try:
             if browse_type == "directory":
                  new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory for {setting_key}", parent=parent_window)
             elif browse_type == "open":
                  new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File for {setting_key}", parent=parent_window)
             elif browse_type == "save_as":
                   new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File for {setting_key}", parent=parent_window)

             if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
             else: logger.debug(f"Browse cancelled for {setting_key}")
        except Exception as e:
             self.logger.error(f"Error during file dialog browse: {e}", exc_info=True)
             self.display_error("Browse Error", f"Could not open file dialog: {e}")

    # --- ISettingsView Implementation ---

    def set_settings_values(self, settings: Dict[str, Any]) -> None:
        """Update the view widgets with values from the settings dictionary."""
        self.logger.debug(f"Setting settings values in view: {list(settings.keys())}")
        for key, var in self.setting_vars.items():
            if key in settings:
                 value = settings[key]
                 try: var.set(str(value) if value is not None else "") # Handle None, ensure string
                 except Exception as e: self.logger.error(f"Failed to set view variable '{key}' to '{value}': {e}")
            else:
                 self.logger.warning(f"Setting key '{key}' not found in provided settings data during set.")
                 var.set("") # Clear field if key missing from data


    def get_settings_values(self) -> Dict[str, Any]:
        """Retrieve the current values from the view widgets, attempting type conversion."""
        self.logger.debug("Getting settings values from view.")
        data = {}
        for key, var in self.setting_vars.items():
             try:
                  value_str = var.get()
                  # Attempt type conversion based on key name (heuristic)
                  if key == 'implicit_wait': data[key] = int(value_str)
                  elif key == 'repo_create_if_missing': data[key] = value_str.lower() in ['true', '1', 'yes'] # Basic bool conversion
                  else: data[key] = value_str # Keep others as strings by default
             except (ValueError, TypeError) as e:
                  self.logger.error(f"Error converting value for setting '{key}': {e}. Storing as string.")
                  data[key] = var.get() # Store as string on conversion error
             except Exception as e:
                  self.logger.error(f"Failed to get view variable for setting '{key}': {e}")
                  data[key] = None
        return data

    # --- Internal Event Handlers ---

    def _on_save(self):
        """Handle Save button click."""
        self.logger.debug("Save settings button clicked.")
        # Confirmation before potentially overwriting config.ini
        if self.confirm_action("Save Settings", "Save current settings to config.ini?\nThis may require restarting the application for some changes to take effect."):
            self.presenter.save_settings() # Delegate to presenter

    def _on_reload(self):
        """Handle Reload button click."""
        self.logger.debug("Reload settings button clicked.")
        if self.confirm_action("Reload Settings", "Discard any unsaved changes and reload settings from config.ini?"):
             self.presenter.load_settings() # Delegate reload to presenter
```

## src/ui/presenters/settings_presenter.py

```python
"""Presenter for the Settings View."""

import logging
from typing import Optional, Dict, Any

# Configuration manager
from src.config import AppConfig, RepositoryType, BrowserTypeStr # Import literals
from src.core.exceptions import ConfigError, ValidationError
# UI dependencies
from src.ui.interfaces.presenter import IPresenter # Base interface might suffice
from src.ui.interfaces.view import IView # Use generic view or create ISettingsView
from src.ui.presenters.base_presenter import BasePresenter

# Define a more specific interface for the Settings View if needed
class ISettingsView(IView):
    def get_settings_values(self) -> Dict[str, Any]: pass
    def set_settings_values(self, settings: Dict[str, Any]) -> None: pass
    # Add specific methods if view needs more granular updates


class SettingsPresenter(BasePresenter[ISettingsView]):
    """
    Presenter for the Settings View. Handles loading settings into the view
    and saving changes back to the configuration source (config.ini).
    """
    def __init__(self, config_manager: AppConfig, view: Optional[ISettingsView] = None):
        """
        Initialize the SettingsPresenter.

        Args:
            config_manager: The application configuration manager instance.
            view: The associated SettingsView instance.
        """
        super().__init__(view)
        if config_manager is None:
             raise ValueError("Configuration manager cannot be None.")
        self.config = config_manager
        self.logger.info("SettingsPresenter initialized.")

    def set_view(self, view: ISettingsView) -> None:
        """Set the view and load initial settings."""
        super().set_view(view)
        self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view when it's set (calls load_settings)."""
        self.load_settings()

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Loading settings")
    def load_settings(self) -> None:
        """Load current settings from the config manager and update the view."""
        if not self.view:
             self.logger.warning("Load settings called but view is not set.")
             return

        self.logger.debug("Loading settings into view.")
        # Reload config from file to ensure latest values are shown
        self.config.reload_config()

        settings_data = {
            'log_level': logging.getLevelName(self.config.log_level),
            'log_file': self.config.log_file,
            'repository_type': self.config.repository_type,
            'workflows_path': self.config.workflows_path,
            'credentials_path': self.config.credentials_path,
            'db_path': self.config.db_path,
            'repo_create_if_missing': self.config.repo_create_if_missing,
            'default_browser': self.config.default_browser,
            'chrome_driver_path': self.config.get_driver_path('chrome') or "",
            'firefox_driver_path': self.config.get_driver_path('firefox') or "",
            'edge_driver_path': self.config.get_driver_path('edge') or "",
            'implicit_wait': self.config.implicit_wait,
            # Security settings intentionally omitted from UI editing
        }
        self.view.set_settings_values(settings_data)
        self.view.set_status("Settings loaded from config.ini.")
        self.logger.info("Settings loaded and view updated.")

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Saving settings")
    def save_settings(self) -> None:
        """Get settings from the view, validate, save via config manager, and reload."""
        if not self.view:
            self.logger.error("Save settings called but view is not set.")
            return

        self.logger.info("Attempting to save settings.")
        settings_to_save = self.view.get_settings_values()

        # --- Basic Validation (Presenter-level) ---
        errors = {}
        # Validate paths (basic check for emptiness if relevant)
        repo_type = settings_to_save.get('repository_type')
        if repo_type == 'file_system':
            if not settings_to_save.get('workflows_path'): errors['workflows_path'] = ["Workflows path required."]
            if not settings_to_save.get('credentials_path'): errors['credentials_path'] = ["Credentials path required."]
        elif repo_type == 'database':
             if not settings_to_save.get('db_path'): errors['db_path'] = ["Database path required."]
        else:
            errors['repository_type'] = ["Invalid repository type selected."]

        # Validate implicit wait
        try:
            wait = int(settings_to_save.get('implicit_wait', 0))
            if wait < 0: errors['implicit_wait'] = ["Implicit wait cannot be negative."]
        except (ValueError, TypeError):
            errors['implicit_wait'] = ["Implicit wait must be an integer."]
        # Validate Log Level
        log_level_str = str(settings_to_save.get('log_level', 'INFO')).upper()
        if log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
             errors['log_level'] = ["Invalid log level selected."]
        # Validate browser type
        browser_str = str(settings_to_save.get('default_browser','chrome')).lower()
        if browser_str not in ['chrome', 'firefox', 'edge', 'safari']:
             errors['default_browser'] = ["Invalid default browser selected."]


        if errors:
             self.logger.warning(f"Settings validation failed: {errors}")
             # Raise ValidationError for the decorator to catch and display
             error_msg = "Validation errors:\n" + "\n".join([f"- {field}: {err}" for field, errs in errors.items() for err in errs])
             raise ValidationError(error_msg) # Decorator will call view.display_error

        # --- Save individual settings using config manager ---
        # Wrap saving logic in try block although decorator handles file I/O errors
        try:
            success = True
            # Use getattr to avoid repeating; assumes setting_key matches config property name
            sections = {'General': ['log_level', 'log_file'],
                        'Repository': ['type', 'workflows_path', 'credentials_path', 'db_path', 'create_if_missing'],
                        'WebDriver': ['default_browser', 'implicit_wait', 'chrome_driver_path', 'firefox_driver_path', 'edge_driver_path']}

            for section, keys in sections.items():
                for key in keys:
                    # Map UI key to config property if names differ, here they match
                    config_key = key
                    # Handle boolean conversion for saving
                    value_to_save = settings_to_save.get(config_key)
                    if isinstance(value_to_save, bool):
                         value_str = str(value_to_save).lower()
                    else:
                         value_str = str(value_to_save)

                    success &= self.config.save_setting(section, config_key, value_str)

            if not success:
                 # Should not happen if save_setting handles errors well, but check
                 raise ConfigError("Failed to update one or more settings in memory.")

            # --- Write changes to file ---
            if self.config.save_config_to_file(): # This can raise IO/Config errors
                self.logger.info("Settings saved to config.ini.")
                self.view.set_status("Settings saved successfully.")
                # Reload config internally and update view to reflect saved state
                self.load_settings()
            else:
                 # save_config_to_file failed (should raise error caught by decorator)
                 raise ConfigError("Failed to write settings to config.ini file.")

        except Exception as e:
             # Let the decorator handle logging/displaying unexpected errors during save
             raise ConfigError(f"An unexpected error occurred during save: {e}", cause=e) from e


    # No decorator needed for simple reload trigger
    def cancel_changes(self) -> None:
        """Discard changes and reload settings from the file."""
        self.logger.info("Cancelling settings changes, reloading from file.")
        self.load_settings() # Reload settings from file, decorator handles errors
```

## src/core/interfaces/action.py

```python
"""Action interface for AutoQliq.

This module defines the interface for action implementations that provide
workflow step capabilities.
"""
import abc
from typing import Dict, Any, Optional, List

# Assuming ActionResult and IWebDriver are defined elsewhere
from src.core.action_result import ActionResult
from src.core.interfaces.webdriver import IWebDriver
from src.core.interfaces.repository import ICredentialRepository
# ActionError likely defined in core.exceptions
# from src.core.exceptions import ActionError


class IAction(abc.ABC):
    """Interface for action implementations.

    Defines the contract for executable steps within a workflow.

    Attributes:
        name (str): A user-defined name for this specific action instance.
        action_type (str): The identifier for the action type (e.g., "Navigate", "Loop").
                           Must be defined as a class attribute in implementations.
    """
    name: str
    action_type: str

    @abc.abstractmethod
    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Context added
    ) -> ActionResult:
        """Execute the action using the provided web driver and context.

        Args:
            driver: The web driver instance.
            credential_repo: Optional credential repository.
            context: Optional dictionary holding execution context (e.g., loop variables).

        Returns:
            An ActionResult indicating success or failure.

        Raises:
            ActionError: For action-specific execution failures.
            CredentialError: For credential-related failures.
            WebDriverError: For driver-related failures.
            ValidationError: If context needed is missing/invalid.
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary representation.

        Must include 'type' and 'name' keys, plus action-specific parameters.
        Nested actions (like in Loop or Conditional) should also be serialized.

        Returns:
            A dictionary representation of the action.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """Validate the action's configuration parameters.

        Checks if required parameters are present and have valid types/formats.
        Should also validate nested actions if applicable (e.g., Loop, Conditional).

        Returns:
            True if the action is configured correctly.

        Raises:
            ValidationError: If validation fails (recommended approach).
        """
        pass

    def get_nested_actions(self) -> List['IAction']:
        """Return any nested actions contained within this action."""
        return []
```

## src/main_ui.py

```python
import tkinter as tk
from tkinter import ttk, messagebox, Menu
import logging
import os

# Configuration
from src.config import config # Import the configured instance

# Core components (interfaces needed for type hinting)
from src.core.interfaces import IWorkflowRepository, ICredentialRepository
from src.core.interfaces.service import IWorkflowService, ICredentialService, IWebDriverService

# Infrastructure components
from src.infrastructure.repositories import RepositoryFactory
from src.infrastructure.webdrivers import WebDriverFactory

# Application Services
from src.application.services import (
    CredentialService, WorkflowService, WebDriverService,
    SchedulerService, ReportingService # Include stubs
)

# UI components (use final names)
from src.ui.views.workflow_editor_view import WorkflowEditorView
from src.ui.views.workflow_runner_view import WorkflowRunnerView
from src.ui.views.settings_view import SettingsView # Import new Settings View
from src.ui.presenters.workflow_editor_presenter import WorkflowEditorPresenter
from src.ui.presenters.workflow_runner_presenter import WorkflowRunnerPresenter
from src.ui.presenters.settings_presenter import SettingsPresenter # Import new Settings Presenter
from src.ui.dialogs.credential_manager_dialog import CredentialManagerDialog # Import Credential Manager Dialog

# Common utilities
# LoggerFactory configures root logger based on AppConfig now
# from src.infrastructure.common.logger_factory import LoggerFactory


def setup_logging():
    """Configure logging based on AppConfig."""
    # BasicConfig is handled by config.py loading now
    # Just get the root logger and ensure level is set
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    # Add file handler if specified in config and not already added
    if config.log_file and not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
         try:
              file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
              formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
              file_handler.setFormatter(formatter)
              root_logger.addHandler(file_handler)
              logging.info(f"Added FileHandler for {config.log_file}")
         except Exception as e:
              logging.error(f"Failed to add FileHandler based on config: {e}")

    logging.info(f"Logging configured. Level: {logging.getLevelName(config.log_level)}")

# --- Global variable for Credential Dialog to prevent multiple instances ---
# (Alternatively, manage dialog lifecycle within a main controller/app class)
credential_dialog_instance: Optional[tk.Toplevel] = None

def main():
    """Main application entry point."""
    # Setup logging first using config values
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"--- Starting {config.WINDOW_TITLE} ---")
    logger.info(f"Using Repository Type: {config.repository_type}")
    logger.info(f"Workflows Path: {config.workflows_path}")
    logger.info(f"Credentials Path: {config.credentials_path}")

    root = tk.Tk()
    root.title(config.WINDOW_TITLE)
    root.geometry(config.WINDOW_GEOMETRY)

    # --- Dependency Injection Setup ---
    try:
        repo_factory = RepositoryFactory()
        webdriver_factory = WebDriverFactory()

        # Ensure directories/files exist for file system repo if selected
        if config.repository_type == "file_system":
            wf_path = config.workflows_path
            cred_path = config.credentials_path
            if not os.path.exists(wf_path):
                os.makedirs(wf_path, exist_ok=True)
                logger.info(f"Created workflows directory: {wf_path}")
            if not os.path.exists(cred_path) and config.repo_create_if_missing:
                with open(cred_path, 'w', encoding='utf-8') as f:
                    f.write("[]") # Create empty JSON list
                logger.info(f"Created empty credentials file: {cred_path}")

        # Create repositories using the factory and config
        workflow_repo: IWorkflowRepository = repo_factory.create_workflow_repository(
            repository_type=config.repository_type,
            path=config.workflows_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        credential_repo: ICredentialRepository = repo_factory.create_credential_repository(
            repository_type=config.repository_type,
            path=config.credentials_path, # Use correct config property
            create_if_missing=config.repo_create_if_missing
        )
        logger.info("Repositories initialized.")

        # Create Application Services, injecting dependencies
        credential_service = CredentialService(credential_repo)
        webdriver_service = WebDriverService(webdriver_factory)
        workflow_service = WorkflowService(workflow_repo, credential_repo, webdriver_service)
        # Initialize placeholder services (they don't do anything yet)
        scheduler_service = SchedulerService()
        reporting_service = ReportingService()
        logger.info("Application services initialized.")

        # Create Presenters, injecting Service interfaces
        editor_presenter = WorkflowEditorPresenter(workflow_service)
        runner_presenter = WorkflowRunnerPresenter(workflow_service, credential_service, webdriver_service)
        settings_presenter = SettingsPresenter(config) # Settings presenter interacts with config directly
        logger.info("Presenters initialized.")

    except Exception as e:
         logger.exception("FATAL: Failed to initialize core components. Application cannot start.")
         messagebox.showerror("Initialization Error", f"Failed to initialize application components: {e}\n\nPlease check configuration (`config.ini`) and file permissions.\nSee log file '{config.log_file}' for details.")
         root.destroy()
         return

    # --- UI Setup ---
    try:
        # Use themed widgets
        style = ttk.Style(root)
        available_themes = style.theme_names()
        logger.debug(f"Available ttk themes: {available_themes}")
        preferred_themes = ['clam', 'alt', 'vista', 'xpnative', 'aqua', 'default']
        for theme in preferred_themes:
            if theme in available_themes:
                 try: style.theme_use(theme); logger.info(f"Using ttk theme: {theme}"); break
                 except tk.TclError: logger.warning(f"Failed theme: '{theme}'.")
        else: logger.warning("Could not find preferred theme.")

        # --- Menu Bar ---
        menubar = Menu(root)
        root.config(menu=menubar)

        manage_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Manage", menu=manage_menu)

        def open_credential_manager():
             global credential_dialog_instance
             # Prevent multiple instances
             if credential_dialog_instance is not None and credential_dialog_instance.winfo_exists():
                  credential_dialog_instance.lift()
                  credential_dialog_instance.focus_set()
                  logger.debug("Credential Manager dialog already open, focusing.")
                  return
             logger.debug("Opening Credential Manager dialog.")
             # Pass the service to the dialog
             dialog = CredentialManagerDialog(root, credential_service)
             credential_dialog_instance = dialog.window # Store reference to Toplevel
             # Dialog runs its own loop implicitly via wait_window() called by show() if needed
             # For a non-blocking approach, dialog would need different handling.

        manage_menu.add_command(label="Credentials...", command=open_credential_manager)
        # Add other management options later if needed

        # --- Main Content Area (Notebook) ---
        notebook = ttk.Notebook(root)

        # Create Frames for each tab content area
        editor_tab_frame = ttk.Frame(notebook)
        runner_tab_frame = ttk.Frame(notebook)
        settings_tab_frame = ttk.Frame(notebook) # Frame for Settings tab

        notebook.add(editor_tab_frame, text="Workflow Editor")
        notebook.add(runner_tab_frame, text="Workflow Runner")
        notebook.add(settings_tab_frame, text="Settings") # Add Settings tab

        # --- Create Views, injecting presenters ---
        # Views are now created with the tab frame as their parent root
        editor_view = WorkflowEditorView(editor_tab_frame, editor_presenter)
        runner_view = WorkflowRunnerView(runner_tab_frame, runner_presenter)
        settings_view = SettingsView(settings_tab_frame, settings_presenter) # Create Settings view
        logger.info("Views initialized.")

        # --- Link Views and Presenters ---
        editor_presenter.set_view(editor_view)
        runner_presenter.set_view(runner_view)
        settings_presenter.set_view(settings_view) # Link Settings presenter and view
        logger.info("Views linked to presenters.")

        # --- Pack the Notebook ---
        # Pack notebook *after* creating views inside their frames
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Start Application ---
        logger.info("Starting Tkinter main loop.")
        root.mainloop()

    except Exception as e:
         logger.exception("An error occurred during application run.")
         if root.winfo_exists():
              messagebox.showerror("Application Error", f"An unexpected error occurred: {e}\n\nPlease check the log file '{config.log_file}'.")
    finally:
         logger.info("--- Application exiting ---")
         # Cleanup handled within presenter/service threads now.
         # Any final cleanup needed? e.g. saving config explicitly?
         # config.save_config_to_file() # Uncomment if auto-save on exit is desired


if __name__ == "__main__":
    # Import Literal for type hinting if used directly here (it's used in RepositoryFactory)
    from typing import Literal
    main()
```

