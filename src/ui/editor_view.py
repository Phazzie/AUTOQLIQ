import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from typing import Callable, List, Dict

class EditorView:
    def __init__(self, root: tk.Tk, save_callback: Callable[[str, List[Dict]], None], load_callback: Callable[[str], List[Dict]]):
        self.root = root
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.actions = []

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Workflow Editor")

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.action_listbox = tk.Listbox(self.main_frame, height=15, width=50)
        self.action_listbox.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))

        self.add_action_button = ttk.Button(self.main_frame, text="Add Action", command=self.add_action)
        self.add_action_button.grid(row=1, column=0, sticky=tk.W)

        self.remove_action_button = ttk.Button(self.main_frame, text="Remove Action", command=self.remove_action)
        self.remove_action_button.grid(row=1, column=1, sticky=tk.W)

        self.save_button = ttk.Button(self.main_frame, text="Save Workflow", command=self.save_workflow)
        self.save_button.grid(row=2, column=0, sticky=tk.W)

        self.load_button = ttk.Button(self.main_frame, text="Load Workflow", command=self.load_workflow)
        self.load_button.grid(row=2, column=1, sticky=tk.W)

    def add_action(self):
        action = {"type": "Navigate", "url": "https://example.com"}
        self.actions.append(action)
        self.action_listbox.insert(tk.END, f"Navigate to {action['url']}")

    def remove_action(self):
        selected_indices = self.action_listbox.curselection()
        for index in selected_indices[::-1]:
            self.action_listbox.delete(index)
            del self.actions[index]

    def save_workflow(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.save_callback(file_path, self.actions)

    def load_workflow(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.actions = self.load_callback(file_path)
            self.action_listbox.delete(0, tk.END)
            for action in self.actions:
                self.action_listbox.insert(tk.END, f"{action['type']} to {action.get('url', '')}")

if __name__ == "__main__":
    root = tk.Tk()
    editor_view = EditorView(root, save_callback=lambda path, actions: print(f"Saving to {path}"), load_callback=lambda path: [])
    root.mainloop()
