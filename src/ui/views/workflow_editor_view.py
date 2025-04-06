"""Workflow editor view module for AutoQliq.

This module provides the view component for the workflow editor.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Dict, Any, Optional, List

from src.core.exceptions import UIError


class WorkflowEditorView:
    """
    View component for the workflow editor.

    This class provides the UI for creating, editing, and managing workflows.
    It communicates with a presenter to handle business logic.

    Attributes:
        root: The root Tkinter window
        presenter: The presenter that handles business logic
        main_frame: The main frame containing all widgets
        workflow_listbox: Listbox displaying available workflows
        action_listbox: Listbox displaying actions in the selected workflow
        logger: Logger for recording view operations and errors
    """

    def __init__(self, root: tk.Tk, presenter: Any):
        """
        Initialize a new WorkflowEditorView.

        Args:
            root: The root Tkinter window
            presenter: The presenter that handles business logic

        Raises:
            UIError: If the view cannot be initialized
        """
        self.root = root
        self.presenter = presenter
        self.logger = logging.getLogger(__name__)
        
        try:
            # Create the main frame
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create widgets
            self.create_widgets()
            
            # Populate the workflow list
            self.populate_workflow_list()
            
            self.logger.debug("WorkflowEditorView initialized")
        except Exception as e:
            error_msg = "Failed to initialize WorkflowEditorView"
            self.logger.error(error_msg, exc_info=True)
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e)

    def create_widgets(self) -> None:
        """
        Create the UI widgets.

        Raises:
            UIError: If the widgets cannot be created
        """
        try:
            # Create a frame for the workflow list
            workflow_frame = ttk.LabelFrame(self.main_frame, text="Workflows")
            workflow_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create the workflow listbox
            self.workflow_listbox = tk.Listbox(workflow_frame, height=10, width=50)
            self.workflow_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.workflow_listbox.bind("<<ListboxSelect>>", self.on_workflow_selected)
            
            # Create workflow buttons
            workflow_button_frame = ttk.Frame(workflow_frame)
            workflow_button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.new_workflow_button = ttk.Button(
                workflow_button_frame, text="New Workflow", command=self.on_new_workflow
            )
            self.new_workflow_button.pack(side=tk.LEFT, padx=5)
            
            self.delete_workflow_button = ttk.Button(
                workflow_button_frame, text="Delete Workflow", command=self.on_delete_workflow
            )
            self.delete_workflow_button.pack(side=tk.LEFT, padx=5)
            
            # Create a frame for the action list
            action_frame = ttk.LabelFrame(self.main_frame, text="Actions")
            action_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create the action listbox
            self.action_listbox = tk.Listbox(action_frame, height=10, width=50)
            self.action_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create action buttons
            action_button_frame = ttk.Frame(action_frame)
            action_button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.add_action_button = ttk.Button(
                action_button_frame, text="Add Action", command=self.on_add_action
            )
            self.add_action_button.pack(side=tk.LEFT, padx=5)
            
            self.edit_action_button = ttk.Button(
                action_button_frame, text="Edit Action", command=self.on_edit_action
            )
            self.edit_action_button.pack(side=tk.LEFT, padx=5)
            
            self.delete_action_button = ttk.Button(
                action_button_frame, text="Delete Action", command=self.on_delete_action
            )
            self.delete_action_button.pack(side=tk.LEFT, padx=5)
            
            # Create save button
            self.save_button = ttk.Button(
                self.main_frame, text="Save Workflow", command=self.on_save_workflow
            )
            self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)
            
            self.logger.debug("Widgets created")
        except Exception as e:
            error_msg = "Failed to create widgets"
            self.logger.error(error_msg, exc_info=True)
            raise UIError(error_msg, component_name="WorkflowEditorView", cause=e)

    def populate_workflow_list(self) -> None:
        """
        Populate the workflow listbox with available workflows.

        Raises:
            UIError: If the workflow list cannot be populated
        """
        try:
            # Clear the listbox
            self.workflow_listbox.delete(0, tk.END)
            
            # Get the list of workflows from the presenter
            workflows = self.presenter.get_workflow_list()
            
            # Add each workflow to the listbox
            for workflow in workflows:
                self.workflow_listbox.insert(tk.END, workflow)
                
            self.logger.debug(f"Populated workflow list with {len(workflows)} workflows")
        except Exception as e:
            error_msg = "Failed to populate workflow list"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_workflow_selected(self, event: tk.Event) -> None:
        """
        Handle workflow selection.

        Args:
            event: The Tkinter event

        Raises:
            UIError: If there is an error loading the selected workflow
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                return
                
            # Load the workflow
            actions = self.presenter.load_workflow(workflow_name)
            if actions is None:
                messagebox.showerror("Error", f"Failed to load workflow: {workflow_name}")
                return
                
            # Update the action listbox
            self.update_action_list(actions)
            
            self.logger.debug(f"Loaded workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to load workflow"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_new_workflow(self) -> None:
        """
        Handle new workflow button click.

        Raises:
            UIError: If there is an error creating a new workflow
        """
        try:
            # Prompt for workflow name
            workflow_name = simpledialog.askstring("New Workflow", "Enter workflow name:")
            if workflow_name is None:
                return  # User cancelled
                
            # Create the workflow
            success = self.presenter.create_workflow(workflow_name)
            if success:
                # Refresh the workflow list
                self.populate_workflow_list()
                self.logger.debug(f"Created new workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to create workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to create new workflow"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_delete_workflow(self) -> None:
        """
        Handle delete workflow button click.

        Raises:
            UIError: If there is an error deleting a workflow
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                messagebox.showwarning("Warning", "No workflow selected")
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm", f"Delete workflow '{workflow_name}'?"):
                return
                
            # Delete the workflow
            success = self.presenter.delete_workflow(workflow_name)
            if success:
                # Refresh the workflow list
                self.populate_workflow_list()
                # Clear the action listbox
                self.action_listbox.delete(0, tk.END)
                self.logger.debug(f"Deleted workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to delete workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to delete workflow"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_add_action(self) -> None:
        """
        Handle add action button click.

        Raises:
            UIError: If there is an error adding an action
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                messagebox.showwarning("Warning", "No workflow selected")
                return
                
            # Show the action dialog
            action_data = self.show_action_dialog()
            if action_data is None:
                return  # User cancelled
                
            # Add the action
            success = self.presenter.add_action(workflow_name, action_data)
            if success:
                # Reload the workflow to update the action list
                self.on_workflow_selected(None)
                self.logger.debug(f"Added action to workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to add action to workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to add action"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_edit_action(self) -> None:
        """
        Handle edit action button click.

        Raises:
            UIError: If there is an error editing an action
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                messagebox.showwarning("Warning", "No workflow selected")
                return
                
            # Get the selected action
            action_index = self.get_selected_action_index()
            if action_index is None:
                messagebox.showwarning("Warning", "No action selected")
                return
                
            # Get the current action data
            current_action = self.presenter.get_action(workflow_name, action_index)
            if current_action is None:
                messagebox.showerror("Error", "Failed to get action data")
                return
                
            # Show the action dialog with the current action data
            action_data = self.show_action_dialog(current_action)
            if action_data is None:
                return  # User cancelled
                
            # Update the action
            success = self.presenter.update_action(workflow_name, action_index, action_data)
            if success:
                # Reload the workflow to update the action list
                self.on_workflow_selected(None)
                self.logger.debug(f"Updated action in workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to update action in workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to edit action"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_delete_action(self) -> None:
        """
        Handle delete action button click.

        Raises:
            UIError: If there is an error deleting an action
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                messagebox.showwarning("Warning", "No workflow selected")
                return
                
            # Get the selected action
            action_index = self.get_selected_action_index()
            if action_index is None:
                messagebox.showwarning("Warning", "No action selected")
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Delete selected action?"):
                return
                
            # Delete the action
            success = self.presenter.delete_action(workflow_name, action_index)
            if success:
                # Reload the workflow to update the action list
                self.on_workflow_selected(None)
                self.logger.debug(f"Deleted action from workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to delete action from workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to delete action"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def on_save_workflow(self) -> None:
        """
        Handle save workflow button click.

        Raises:
            UIError: If there is an error saving the workflow
        """
        try:
            # Get the selected workflow
            workflow_name = self.get_selected_workflow()
            if workflow_name is None:
                messagebox.showwarning("Warning", "No workflow selected")
                return
                
            # Save the workflow
            success = self.presenter.save_workflow(workflow_name)
            if success:
                messagebox.showinfo("Success", f"Workflow '{workflow_name}' saved successfully")
                self.logger.debug(f"Saved workflow: {workflow_name}")
            else:
                messagebox.showerror("Error", f"Failed to save workflow: {workflow_name}")
        except Exception as e:
            error_msg = "Failed to save workflow"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", f"{error_msg}: {str(e)}")

    def get_selected_workflow(self) -> Optional[str]:
        """
        Get the name of the selected workflow.

        Returns:
            The name of the selected workflow, or None if no workflow is selected
        """
        selected_indices = self.workflow_listbox.curselection()
        if not selected_indices:
            return None
            
        return self.workflow_listbox.get(selected_indices[0])

    def get_selected_action_index(self) -> Optional[int]:
        """
        Get the index of the selected action.

        Returns:
            The index of the selected action, or None if no action is selected
        """
        selected_indices = self.action_listbox.curselection()
        if not selected_indices:
            return None
            
        return selected_indices[0]

    def update_action_list(self, actions: List[Any]) -> None:
        """
        Update the action listbox with the given actions.

        Args:
            actions: The list of actions to display
        """
        # Clear the listbox
        self.action_listbox.delete(0, tk.END)
        
        # Add each action to the listbox
        for action in actions:
            action_dict = action.to_dict()
            action_type = action_dict.get("type", "Unknown")
            
            if action_type == "Navigate":
                url = action_dict.get("url", "")
                self.action_listbox.insert(tk.END, f"Navigate to {url}")
            elif action_type == "Click":
                selector = action_dict.get("selector", "")
                self.action_listbox.insert(tk.END, f"Click element {selector}")
            elif action_type == "Type":
                selector = action_dict.get("selector", "")
                value_type = action_dict.get("value_type", "")
                value = action_dict.get("value", "")
                value_key = action_dict.get("value_key", "")
                
                if value_type == "text":
                    self.action_listbox.insert(tk.END, f"Type '{value}' into {selector}")
                elif value_type == "credential":
                    self.action_listbox.insert(tk.END, f"Type credential {value_key} into {selector}")
            elif action_type == "Wait":
                duration = action_dict.get("duration_seconds", 0)
                self.action_listbox.insert(tk.END, f"Wait for {duration} seconds")
            elif action_type == "Screenshot":
                file_path = action_dict.get("file_path", "")
                self.action_listbox.insert(tk.END, f"Take screenshot to {file_path}")
            else:
                self.action_listbox.insert(tk.END, f"{action_type} action")

    def show_action_dialog(self, current_action: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Show a dialog for adding or editing an action.

        Args:
            current_action: The current action data, if editing an existing action

        Returns:
            The action data entered by the user, or None if the user cancelled
        """
        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Action Editor")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create a frame for the dialog content
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a variable for the action type
        action_type_var = tk.StringVar(value="Navigate")
        if current_action:
            action_type_var.set(current_action.get("type", "Navigate"))
        
        # Create a label and combobox for the action type
        ttk.Label(frame, text="Action Type:").grid(row=0, column=0, sticky=tk.W)
        action_type_combobox = ttk.Combobox(
            frame, textvariable=action_type_var, values=["Navigate", "Click", "Type", "Wait", "Screenshot"]
        )
        action_type_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        action_type_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_action_dialog(frame, action_type_var.get()))
        
        # Create a frame for the action parameters
        param_frame = ttk.Frame(frame)
        param_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create a dictionary to store the parameter variables
        param_vars = {}
        
        # Create a function to update the parameter frame based on the action type
        def update_param_frame():
            # Clear the parameter frame
            for widget in param_frame.winfo_children():
                widget.destroy()
                
            # Create parameters based on the action type
            action_type = action_type_var.get()
            
            if action_type == "Navigate":
                ttk.Label(param_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
                url_var = tk.StringVar(value=current_action.get("url", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=url_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E))
                param_vars["url"] = url_var
                
            elif action_type == "Click":
                ttk.Label(param_frame, text="Selector:").grid(row=0, column=0, sticky=tk.W)
                selector_var = tk.StringVar(value=current_action.get("selector", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=selector_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E))
                param_vars["selector"] = selector_var
                
            elif action_type == "Type":
                ttk.Label(param_frame, text="Selector:").grid(row=0, column=0, sticky=tk.W)
                selector_var = tk.StringVar(value=current_action.get("selector", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=selector_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E))
                param_vars["selector"] = selector_var
                
                ttk.Label(param_frame, text="Value Type:").grid(row=1, column=0, sticky=tk.W)
                value_type_var = tk.StringVar(value=current_action.get("value_type", "text") if current_action else "text")
                ttk.Combobox(
                    param_frame, textvariable=value_type_var, values=["text", "credential"]
                ).grid(row=1, column=1, sticky=(tk.W, tk.E))
                param_vars["value_type"] = value_type_var
                
                ttk.Label(param_frame, text="Value:").grid(row=2, column=0, sticky=tk.W)
                value_var = tk.StringVar(value=current_action.get("value", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=value_var, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E))
                param_vars["value"] = value_var
                
                ttk.Label(param_frame, text="Credential Key:").grid(row=3, column=0, sticky=tk.W)
                value_key_var = tk.StringVar(value=current_action.get("value_key", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=value_key_var, width=40).grid(row=3, column=1, sticky=(tk.W, tk.E))
                param_vars["value_key"] = value_key_var
                
            elif action_type == "Wait":
                ttk.Label(param_frame, text="Duration (seconds):").grid(row=0, column=0, sticky=tk.W)
                duration_var = tk.StringVar(value=str(current_action.get("duration_seconds", 1)) if current_action else "1")
                ttk.Entry(param_frame, textvariable=duration_var, width=10).grid(row=0, column=1, sticky=(tk.W, tk.E))
                param_vars["duration_seconds"] = duration_var
                
            elif action_type == "Screenshot":
                ttk.Label(param_frame, text="File Path:").grid(row=0, column=0, sticky=tk.W)
                file_path_var = tk.StringVar(value=current_action.get("file_path", "") if current_action else "")
                ttk.Entry(param_frame, textvariable=file_path_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E))
                param_vars["file_path"] = file_path_var
        
        # Update the parameter frame initially
        update_param_frame()
        
        # Create a function to handle the OK button
        def on_ok():
            # Create the action data
            action_data = {"type": action_type_var.get()}
            
            # Add the parameters
            for param_name, param_var in param_vars.items():
                # Convert numeric values
                if param_name == "duration_seconds":
                    try:
                        action_data[param_name] = int(param_var.get())
                    except ValueError:
                        messagebox.showerror("Error", "Duration must be a number")
                        return
                else:
                    action_data[param_name] = param_var.get()
            
            # Close the dialog
            dialog.result = action_data
            dialog.destroy()
        
        # Create a function to handle the Cancel button
        def on_cancel():
            dialog.result = None
            dialog.destroy()
        
        # Create OK and Cancel buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.E, tk.S))
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=5)
        
        # Bind the action type combobox to update the parameter frame
        action_type_combobox.bind("<<ComboboxSelected>>", lambda e: update_param_frame())
        
        # Wait for the dialog to be closed
        dialog.wait_window()
        
        # Return the result
        return getattr(dialog, "result", None)
