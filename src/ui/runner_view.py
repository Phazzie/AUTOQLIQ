import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from typing import Callable, List, Dict

class RunnerView:
    def __init__(self, root: tk.Tk, run_callback: Callable[[str], None], list_workflows_callback: Callable[[], List[str]]):
        self.root = root
        self.run_callback = run_callback
        self.list_workflows_callback = list_workflows_callback

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Workflow Runner")

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.workflow_listbox = tk.Listbox(self.main_frame, height=15, width=50)
        self.workflow_listbox.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))

        self.run_button = ttk.Button(self.main_frame, text="Run Workflow", command=self.run_workflow)
        self.run_button.grid(row=1, column=0, sticky=tk.W)

        self.refresh_button = ttk.Button(self.main_frame, text="Refresh Workflows", command=self.refresh_workflows)
        self.refresh_button.grid(row=1, column=1, sticky=tk.W)

    def run_workflow(self):
        selected_indices = self.workflow_listbox.curselection()
        if selected_indices:
            workflow_name = self.workflow_listbox.get(selected_indices[0])
            self.run_callback(workflow_name)

    def refresh_workflows(self):
        workflows = self.list_workflows_callback()
        self.workflow_listbox.delete(0, tk.END)
        for workflow in workflows:
            self.workflow_listbox.insert(tk.END, workflow)

if __name__ == "__main__":
    root = tk.Tk()
    runner_view = RunnerView(root, run_callback=lambda name: print(f"Running {name}"), list_workflows_callback=lambda: ["example_workflow"])
    root.mainloop()
