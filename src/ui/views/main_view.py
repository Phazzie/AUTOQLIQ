"""Main view implementation for AutoQliq.

This module provides the MainView class that serves as the main application window.
"""

import logging
import tkinter as tk
from tkinter import ttk, Menu
from typing import Callable, Dict

from src.ui.views.base_view import BaseView
from src.ui.interfaces.view_interfaces import IMainView
from src.ui.common.status_bar import StatusBar

logger = logging.getLogger(__name__)

class MainView(BaseView, IMainView):
    """
    Main application view that contains the notebook with tabs for different views.
    
    Provides the main window, menu, status bar, and notebook container for other views.
    """
    
    def __init__(self, root: tk.Tk, presenter: 'MainPresenter'):
        """
        Initialize the main view.
        
        Args:
            root: The root Tk window.
            presenter: The main presenter.
        """
        super().__init__(root, presenter)
        
        # Store root window reference
        self.root = root
        
        # Create status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store status bar on toplevel for other views to access
        self.root.status_bar_instance = self.status_bar
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create menu
        self.create_menu()
        
        logger.debug("MainView initialized")
    
    def set_status(self, status: str) -> None:
        """
        Set the status message in the status bar.
        
        Args:
            status: The status message to display.
        """
        self.status_bar.set_message(status)
    
    def set_title(self, title: str) -> None:
        """
        Set the window title.
        
        Args:
            title: The window title.
        """
        self.root.title(title)
    
    def create_menu(self) -> None:
        """Create the application menu."""
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self._on_exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Manage menu
        self.manage_menu = Menu(self.menu_bar, tearoff=0)
        self.manage_menu.add_command(label="Credentials...", command=self._on_open_credential_manager)
        self.menu_bar.add_cascade(label="Manage", menu=self.manage_menu)
        
        # Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self._on_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
    
    def bind_menu_handlers(self, handlers: Dict[str, Callable]) -> None:
        """
        Bind menu item handlers.
        
        Args:
            handlers: Dictionary mapping menu item names to handler functions.
        """
        if 'exit' in handlers:
            self._on_exit = handlers['exit']
        
        if 'about' in handlers:
            self._on_about = handlers['about']
        
        if 'open_credential_manager' in handlers:
            self._on_open_credential_manager = handlers['open_credential_manager']
    
    def add_tab(self, view: BaseView, text: str) -> None:
        """
        Add a tab to the notebook.
        
        Args:
            view: The view to add as a tab.
            text: The tab label text.
        """
        self.notebook.add(view.widget, text=text)
    
    def _on_exit(self) -> None:
        """Default exit handler."""
        logger.debug("Default exit handler called")
        self.root.destroy()
    
    def _on_about(self) -> None:
        """Default about handler."""
        logger.debug("Default about handler called")
        self.display_message("About AutoQliq", "AutoQliq - Web Automation Tool\nVersion 1.0")
    
    def _on_open_credential_manager(self) -> None:
        """Default credential manager handler."""
        logger.debug("Default credential manager handler called")
        self.display_message("Credential Manager", "Credential Manager not implemented yet.")
