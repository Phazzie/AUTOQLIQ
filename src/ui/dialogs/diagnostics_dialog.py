"""Diagnostics dialog for AutoQliq."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import os
import sys
import platform
import threading
import time
import json
from typing import Dict, Any, List, Optional, Callable

from src.core.exceptions import AutoQliqError, UIError
from src.infrastructure.common.error_monitoring import error_monitor
from src.config import config

logger = logging.getLogger(__name__)


class DiagnosticsDialog(tk.Toplevel):
    """Dialog for running diagnostics and troubleshooting the application."""
    
    def __init__(
        self,
        parent: tk.Widget,
        repositories: Optional[Dict[str, Any]] = None,
        services: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the diagnostics dialog.
        
        Args:
            parent: The parent widget
            repositories: Dictionary of repository instances
            services: Dictionary of service instances
        """
        super().__init__(parent)
        self.title("AutoQliq Diagnostics")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Store references to repositories and services
        self.repositories = repositories or {}
        self.services = services or {}
        
        # Create the UI
        self._create_widgets()
        
        # Center the dialog on the parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Set up the diagnostics
        self._setup_diagnostics()
        
        logger.debug("DiagnosticsDialog initialized")
    
    def _create_widgets(self) -> None:
        """Create the dialog widgets."""
        # Create the main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create the System tab
        system_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(system_frame, text="System")
        
        # Create the system info text widget
        system_frame.columnconfigure(0, weight=1)
        system_frame.rowconfigure(0, weight=1)
        
        system_info_frame = ttk.LabelFrame(system_frame, text="System Information")
        system_info_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        self.system_info_text = scrolledtext.ScrolledText(
            system_info_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            state=tk.DISABLED
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the Repositories tab
        repo_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(repo_frame, text="Repositories")
        
        # Create the repository info text widget
        repo_frame.columnconfigure(0, weight=1)
        repo_frame.rowconfigure(0, weight=1)
        
        repo_info_frame = ttk.LabelFrame(repo_frame, text="Repository Information")
        repo_info_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        self.repo_info_text = scrolledtext.ScrolledText(
            repo_info_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            state=tk.DISABLED
        )
        self.repo_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the Errors tab
        errors_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(errors_frame, text="Errors")
        
        # Create the error info text widget
        errors_frame.columnconfigure(0, weight=1)
        errors_frame.rowconfigure(0, weight=1)
        
        error_info_frame = ttk.LabelFrame(errors_frame, text="Recent Errors")
        error_info_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        self.error_info_text = scrolledtext.ScrolledText(
            error_info_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            state=tk.DISABLED
        )
        self.error_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the Troubleshooting tab
        troubleshoot_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(troubleshoot_frame, text="Troubleshooting")
        
        # Create the troubleshooting tools
        troubleshoot_frame.columnconfigure(0, weight=1)
        troubleshoot_frame.rowconfigure(1, weight=1)
        
        # Create the tools frame
        tools_frame = ttk.LabelFrame(troubleshoot_frame, text="Troubleshooting Tools")
        tools_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 10))
        
        # Create the tool buttons
        self.verify_button = ttk.Button(
            tools_frame,
            text="Verify Repositories",
            command=self._verify_repositories
        )
        self.verify_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.test_webdriver_button = ttk.Button(
            tools_frame,
            text="Test WebDriver",
            command=self._test_webdriver
        )
        self.test_webdriver_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_cache_button = ttk.Button(
            tools_frame,
            text="Clear Cache",
            command=self._clear_cache
        )
        self.clear_cache_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.backup_button = ttk.Button(
            tools_frame,
            text="Backup Data",
            command=self._backup_data
        )
        self.backup_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create the output frame
        output_frame = ttk.LabelFrame(troubleshoot_frame, text="Output")
        output_frame.grid(row=1, column=0, sticky=tk.NSEW)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            state=tk.NORMAL
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self._refresh_all
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(
            button_frame,
            text="Export Diagnostics",
            command=self._export_diagnostics
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.destroy
        )
        self.close_button.pack(side=tk.RIGHT, padx=5)
    
    def _setup_diagnostics(self) -> None:
        """Set up the diagnostics tabs."""
        # Populate the system info tab
        self._populate_system_info()
        
        # Populate the repository info tab
        self._populate_repository_info()
        
        # Populate the error info tab
        self._populate_error_info()
        
        # Add initial message to output
        self._append_output("Diagnostics tool ready. Select a troubleshooting option above.")
    
    def _populate_system_info(self) -> None:
        """Populate the system information tab."""
        try:
            # Get system information
            system_info = self._get_system_info()
            
            # Format the information
            info_text = "System Information:\n\n"
            
            for section, data in system_info.items():
                info_text += f"=== {section} ===\n"
                for key, value in data.items():
                    info_text += f"{key}: {value}\n"
                info_text += "\n"
            
            # Update the text widget
            self._set_text(self.system_info_text, info_text)
        except Exception as e:
            logger.error(f"Failed to populate system info: {e}")
            self._set_text(
                self.system_info_text,
                f"Error retrieving system information: {e}"
            )
    
    def _populate_repository_info(self) -> None:
        """Populate the repository information tab."""
        try:
            # Get repository information
            repo_info = self._get_repository_info()
            
            # Format the information
            info_text = "Repository Information:\n\n"
            
            for repo_name, data in repo_info.items():
                info_text += f"=== {repo_name} ===\n"
                for key, value in data.items():
                    info_text += f"{key}: {value}\n"
                info_text += "\n"
            
            # Update the text widget
            self._set_text(self.repo_info_text, info_text)
        except Exception as e:
            logger.error(f"Failed to populate repository info: {e}")
            self._set_text(
                self.repo_info_text,
                f"Error retrieving repository information: {e}"
            )
    
    def _populate_error_info(self) -> None:
        """Populate the error information tab."""
        try:
            # Get error information
            error_info = self._get_error_info()
            
            # Format the information
            info_text = "Error Information:\n\n"
            
            # Add summary
            info_text += "=== Summary ===\n"
            info_text += f"Total Errors: {error_info['summary']['total_errors']}\n"
            info_text += f"Unique Error Types: {error_info['summary']['unique_error_types']}\n"
            info_text += "\n"
            
            # Add error counts
            info_text += "=== Error Counts ===\n"
            for error_type, count in error_info['summary']['error_counts'].items():
                info_text += f"{error_type}: {count}\n"
            info_text += "\n"
            
            # Add recent errors
            info_text += "=== Recent Errors ===\n"
            for error in error_info['recent_errors']:
                info_text += f"Type: {error['error_type']}\n"
                info_text += f"Message: {error['error_message']}\n"
                info_text += f"Context: {error['context']}\n"
                info_text += f"Time: {error['datetime']}\n"
                info_text += "\n"
            
            # Update the text widget
            self._set_text(self.error_info_text, info_text)
        except Exception as e:
            logger.error(f"Failed to populate error info: {e}")
            self._set_text(
                self.error_info_text,
                f"Error retrieving error information: {e}"
            )
    
    def _get_system_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get system information.
        
        Returns:
            Dictionary of system information
        """
        system_info = {}
        
        # Python information
        system_info['Python'] = {
            'Version': platform.python_version(),
            'Implementation': platform.python_implementation(),
            'Compiler': platform.python_compiler(),
            'Path': sys.executable,
            'Modules': ', '.join(sorted(sys.modules.keys())[:20]) + '...'
        }
        
        # OS information
        system_info['Operating System'] = {
            'System': platform.system(),
            'Release': platform.release(),
            'Version': platform.version(),
            'Machine': platform.machine(),
            'Processor': platform.processor()
        }
        
        # Application information
        system_info['Application'] = {
            'Version': getattr(config, 'VERSION', 'Unknown'),
            'Config File': getattr(config, 'config_file', 'Unknown'),
            'Log File': getattr(config, 'log_file', 'Unknown'),
            'Repository Type': getattr(config, 'repository_type', 'Unknown'),
            'Workflows Path': getattr(config, 'workflows_path', 'Unknown'),
            'Credentials Path': getattr(config, 'credentials_path', 'Unknown')
        }
        
        # Environment information
        system_info['Environment'] = {
            'Current Directory': os.getcwd(),
            'User': os.getenv('USER', 'Unknown'),
            'Home': os.getenv('HOME', 'Unknown'),
            'Path': os.getenv('PATH', 'Unknown')[:100] + '...'
        }
        
        return system_info
    
    def _get_repository_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get repository information.
        
        Returns:
            Dictionary of repository information
        """
        repo_info = {}
        
        # Workflow repository information
        if 'workflow_repository' in self.repositories:
            workflow_repo = self.repositories['workflow_repository']
            
            try:
                workflows = workflow_repo.list_workflows()
                
                repo_info['Workflow Repository'] = {
                    'Type': workflow_repo.__class__.__name__,
                    'Workflow Count': len(workflows),
                    'Workflows': ', '.join(workflows[:10]) + ('...' if len(workflows) > 10 else ''),
                    'Path': getattr(workflow_repo, 'directory_path', 'Unknown')
                }
            except Exception as e:
                repo_info['Workflow Repository'] = {
                    'Type': workflow_repo.__class__.__name__,
                    'Error': str(e)
                }
        
        # Credential repository information
        if 'credential_repository' in self.repositories:
            credential_repo = self.repositories['credential_repository']
            
            try:
                credentials = credential_repo.list_credentials()
                
                repo_info['Credential Repository'] = {
                    'Type': credential_repo.__class__.__name__,
                    'Credential Count': len(credentials),
                    'Credentials': ', '.join(credentials[:10]) + ('...' if len(credentials) > 10 else ''),
                    'Path': getattr(credential_repo, 'file_path', 'Unknown')
                }
            except Exception as e:
                repo_info['Credential Repository'] = {
                    'Type': credential_repo.__class__.__name__,
                    'Error': str(e)
                }
        
        return repo_info
    
    def _get_error_info(self) -> Dict[str, Any]:
        """
        Get error information.
        
        Returns:
            Dictionary of error information
        """
        error_info = {}
        
        # Get error summary
        error_info['summary'] = error_monitor.get_error_summary(days=7)
        
        # Get recent errors
        error_info['recent_errors'] = error_monitor.get_recent_errors(count=10)
        
        return error_info
    
    def _verify_repositories(self) -> None:
        """Verify the repositories."""
        self._append_output("Verifying repositories...")
        
        # Run the verification in a background thread
        threading.Thread(target=self._verify_repositories_thread, daemon=True).start()
    
    def _verify_repositories_thread(self) -> None:
        """Verify the repositories in a background thread."""
        try:
            # Verify workflow repository
            if 'workflow_repository' in self.repositories:
                workflow_repo = self.repositories['workflow_repository']
                
                self._append_output("Verifying workflow repository...")
                
                # List workflows
                workflows = workflow_repo.list_workflows()
                self._append_output(f"Found {len(workflows)} workflows")
                
                # Verify each workflow
                for workflow_name in workflows:
                    try:
                        # Load the workflow
                        actions = workflow_repo.load(workflow_name)
                        self._append_output(f"Workflow '{workflow_name}' loaded successfully with {len(actions)} actions")
                    except Exception as e:
                        self._append_output(f"Error loading workflow '{workflow_name}': {e}")
            
            # Verify credential repository
            if 'credential_repository' in self.repositories:
                credential_repo = self.repositories['credential_repository']
                
                self._append_output("Verifying credential repository...")
                
                # List credentials
                credentials = credential_repo.list_credentials()
                self._append_output(f"Found {len(credentials)} credentials")
                
                # Verify each credential
                for credential_name in credentials:
                    try:
                        # Get the credential
                        credential = credential_repo.get_by_name(credential_name)
                        if credential:
                            self._append_output(f"Credential '{credential_name}' loaded successfully")
                        else:
                            self._append_output(f"Credential '{credential_name}' not found")
                    except Exception as e:
                        self._append_output(f"Error loading credential '{credential_name}': {e}")
            
            self._append_output("Repository verification complete")
        except Exception as e:
            self._append_output(f"Error verifying repositories: {e}")
    
    def _test_webdriver(self) -> None:
        """Test the WebDriver."""
        self._append_output("Testing WebDriver...")
        
        # Run the test in a background thread
        threading.Thread(target=self._test_webdriver_thread, daemon=True).start()
    
    def _test_webdriver_thread(self) -> None:
        """Test the WebDriver in a background thread."""
        driver = None
        try:
            # Get the WebDriver factory
            if 'webdriver_factory' not in self.repositories:
                self._append_output("WebDriver factory not available")
                return
            
            webdriver_factory = self.repositories['webdriver_factory']
            
            # Create a WebDriver
            self._append_output("Creating WebDriver...")
            driver = webdriver_factory.create_driver()
            self._append_output("WebDriver created successfully")
            
            # Navigate to a test page
            self._append_output("Navigating to test page...")
            driver.get("https://www.google.com")
            self._append_output("Navigation successful")
            
            # Get the page title
            title = driver.title
            self._append_output(f"Page title: {title}")
            
            # Take a screenshot
            self._append_output("Taking screenshot...")
            screenshot_path = os.path.join("logs", "webdriver_test.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            driver.save_screenshot(screenshot_path)
            self._append_output(f"Screenshot saved to {screenshot_path}")
            
            self._append_output("WebDriver test complete")
        except Exception as e:
            self._append_output(f"Error testing WebDriver: {e}")
        finally:
            # Close the WebDriver
            if driver:
                try:
                    driver.quit()
                    self._append_output("WebDriver closed")
                except Exception as e:
                    self._append_output(f"Error closing WebDriver: {e}")
    
    def _clear_cache(self) -> None:
        """Clear the application cache."""
        self._append_output("Clearing cache...")
        
        try:
            # Clear the cache directory
            cache_dir = os.path.join("cache")
            if os.path.exists(cache_dir):
                for filename in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            self._append_output(f"Deleted cache file: {filename}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            self._append_output(f"Deleted cache directory: {filename}")
                    except Exception as e:
                        self._append_output(f"Error deleting {file_path}: {e}")
            else:
                self._append_output("Cache directory not found")
            
            self._append_output("Cache cleared")
        except Exception as e:
            self._append_output(f"Error clearing cache: {e}")
    
    def _backup_data(self) -> None:
        """Backup the application data."""
        self._append_output("Backing up data...")
        
        try:
            # Create a backup directory
            backup_dir = os.path.join("backups", time.strftime("%Y%m%d_%H%M%S"))
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup workflows
            workflows_path = getattr(config, 'workflows_path', 'data/workflows')
            if os.path.exists(workflows_path):
                workflows_backup = os.path.join(backup_dir, "workflows")
                shutil.copytree(workflows_path, workflows_backup)
                self._append_output(f"Backed up workflows to {workflows_backup}")
            
            # Backup credentials
            credentials_path = getattr(config, 'credentials_path', 'data/credentials.json')
            if os.path.exists(credentials_path):
                credentials_backup = os.path.join(backup_dir, "credentials.json")
                shutil.copy2(credentials_path, credentials_backup)
                self._append_output(f"Backed up credentials to {credentials_backup}")
            
            # Backup configuration
            config_file = getattr(config, 'config_file', 'config.ini')
            if os.path.exists(config_file):
                config_backup = os.path.join(backup_dir, "config.ini")
                shutil.copy2(config_file, config_backup)
                self._append_output(f"Backed up configuration to {config_backup}")
            
            self._append_output(f"Backup complete: {backup_dir}")
        except Exception as e:
            self._append_output(f"Error backing up data: {e}")
    
    def _refresh_all(self) -> None:
        """Refresh all diagnostics tabs."""
        self._populate_system_info()
        self._populate_repository_info()
        self._populate_error_info()
        self._append_output("Diagnostics refreshed")
    
    def _export_diagnostics(self) -> None:
        """Export diagnostics information to a file."""
        try:
            # Create the export directory
            export_dir = os.path.join("logs", "diagnostics")
            os.makedirs(export_dir, exist_ok=True)
            
            # Create the export file
            export_file = os.path.join(export_dir, f"diagnostics_{time.strftime('%Y%m%d_%H%M%S')}.txt")
            
            # Collect diagnostics information
            diagnostics = {}
            diagnostics['system_info'] = self._get_system_info()
            diagnostics['repository_info'] = self._get_repository_info()
            diagnostics['error_info'] = self._get_error_info()
            
            # Write the information to the file
            with open(export_file, 'w') as f:
                f.write("AutoQliq Diagnostics\n")
                f.write("===================\n\n")
                
                # Write system information
                f.write("System Information\n")
                f.write("-----------------\n\n")
                for section, data in diagnostics['system_info'].items():
                    f.write(f"{section}:\n")
                    for key, value in data.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                # Write repository information
                f.write("Repository Information\n")
                f.write("---------------------\n\n")
                for repo_name, data in diagnostics['repository_info'].items():
                    f.write(f"{repo_name}:\n")
                    for key, value in data.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                # Write error information
                f.write("Error Information\n")
                f.write("----------------\n\n")
                
                # Write error summary
                f.write("Error Summary:\n")
                f.write(f"  Total Errors: {diagnostics['error_info']['summary']['total_errors']}\n")
                f.write(f"  Unique Error Types: {diagnostics['error_info']['summary']['unique_error_types']}\n")
                f.write("\n")
                
                # Write error counts
                f.write("Error Counts:\n")
                for error_type, count in diagnostics['error_info']['summary']['error_counts'].items():
                    f.write(f"  {error_type}: {count}\n")
                f.write("\n")
                
                # Write recent errors
                f.write("Recent Errors:\n")
                for error in diagnostics['error_info']['recent_errors']:
                    f.write(f"  Type: {error['error_type']}\n")
                    f.write(f"  Message: {error['error_message']}\n")
                    f.write(f"  Context: {error['context']}\n")
                    f.write(f"  Time: {error['datetime']}\n")
                    f.write("\n")
            
            # Show a success message
            messagebox.showinfo(
                "Export Complete",
                f"Diagnostics exported to {export_file}",
                parent=self
            )
        except Exception as e:
            logger.error(f"Failed to export diagnostics: {e}")
            messagebox.showerror(
                "Export Error",
                f"Failed to export diagnostics: {e}",
                parent=self
            )
    
    def _set_text(self, text_widget: scrolledtext.ScrolledText, text: str) -> None:
        """
        Set the text of a text widget.
        
        Args:
            text_widget: The text widget
            text: The text to set
        """
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
    
    def _append_output(self, text: str) -> None:
        """
        Append text to the output text widget.
        
        Args:
            text: The text to append
        """
        # Schedule the update on the main thread
        self.after(0, self._append_output_main_thread, text)
    
    def _append_output_main_thread(self, text: str) -> None:
        """
        Append text to the output text widget on the main thread.
        
        Args:
            text: The text to append
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.NORMAL)  # Keep it editable for now
    
    def show(self) -> None:
        """Show the dialog and wait for it to be closed."""
        self.wait_window()
