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