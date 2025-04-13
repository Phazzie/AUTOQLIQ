#!/usr/bin/env python
"""
Code Analyzer GUI

A simple GUI for running code quality analysis tools.
"""

import os
import sys
import subprocess
import threading
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

class CodeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Analyzer")
        self.root.geometry("900x700")

        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5")
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create widgets
        self.create_widgets()

        # Current process
        self.current_process = None

    def create_widgets(self):
        # Target selection frame
        target_frame = ttk.Frame(self.main_frame)
        target_frame.pack(fill=tk.X, pady=5)

        ttk.Label(target_frame, text="Target:", width=10).pack(side=tk.LEFT)

        self.target_path = tk.StringVar()
        target_entry = ttk.Entry(target_frame, textvariable=self.target_path, width=50)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        browse_btn = ttk.Button(target_frame, text="Browse", command=self.browse_target)
        browse_btn.pack(side=tk.LEFT)

        # Analyzer selection frame
        analyzer_frame = ttk.Frame(self.main_frame)
        analyzer_frame.pack(fill=tk.X, pady=10)

        ttk.Label(analyzer_frame, text="Analyzer:", width=10).pack(side=tk.LEFT)

        self.analyzer_var = tk.StringVar()
        self.analyzer_var.set("srp_analyzer")  # Default analyzer

        # Get available analyzers
        self.analyzers = self.get_available_analyzers()
        analyzer_dropdown = ttk.Combobox(analyzer_frame, textvariable=self.analyzer_var,
                                         values=list(self.analyzers.keys()), width=30)
        analyzer_dropdown.pack(side=tk.LEFT, padx=5)

        run_btn = ttk.Button(analyzer_frame, text="Run Analysis", command=self.run_analysis)
        run_btn.pack(side=tk.LEFT, padx=5)

        # Options frame
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Label(options_frame, text="Options:").pack(side=tk.LEFT)

        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(options_frame, text="Recursive", variable=self.recursive_var)
        recursive_check.pack(side=tk.LEFT, padx=10)

        self.verbose_var = tk.BooleanVar(value=True)
        verbose_check = ttk.Checkbutton(options_frame, text="Verbose", variable=self.verbose_var)
        verbose_check.pack(side=tk.LEFT, padx=10)

        # Results frame
        results_frame = ttk.Frame(self.main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Results notebook
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Output tab
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="Output")

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                    width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

        # Summary tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")

        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD,
                                                     width=80, height=20)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        self.summary_text.config(state=tk.DISABLED)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL,
                                       length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

    def get_available_analyzers(self):
        """Get available analyzers from the code_quality_analyzer directory."""
        analyzers = {}

        # Check for code_quality_analyzer directory
        if os.path.exists("code_quality_analyzer/analyzers"):
            for file in os.listdir("code_quality_analyzer/analyzers"):
                if file.endswith("_analyzer.py"):
                    name = file[:-3]  # Remove .py
                    display_name = name.replace('_', ' ').title()
                    analyzers[name] = os.path.join("code_quality_analyzer/analyzers", file)

        # Add other analyzers
        other_analyzers = {
            "Check Missing Files": "check_missing_files.py",
            "Analyze Package Size": "analyze_package_size.py",
            "Test Analyzers": "test_analyzers.py"
        }

        for display_name, file_path in other_analyzers.items():
            if os.path.exists(file_path):
                analyzers[display_name] = file_path

        return analyzers

    def browse_target(self):
        """Open file dialog to select target file or directory."""
        path = filedialog.askdirectory(title="Select Directory")
        if path:
            self.target_path.set(path)

    def run_analysis(self):
        """Run the selected analyzer on the target path."""
        target_path = self.target_path.get()
        analyzer_key = self.analyzer_var.get()

        if not target_path:
            messagebox.showerror("Error", "Please select a target directory")
            return

        if analyzer_key not in self.analyzers:
            messagebox.showerror("Error", "Please select a valid analyzer")
            return

        analyzer_path = self.analyzers[analyzer_key]

        # Clear output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.config(state=tk.DISABLED)

        # Update status
        self.status_var.set(f"Running {analyzer_key}...")

        # Start progress bar
        self.progress.start()

        # Run analyzer in a separate thread
        threading.Thread(target=self._run_analyzer,
                        args=(analyzer_path, target_path),
                        daemon=True).start()

    def _run_analyzer(self, analyzer_path, target_path):
        """Run the analyzer in a separate thread."""
        try:
            # Check if analyzer file exists
            if not os.path.exists(analyzer_path):
                self.root.after(0, self._analysis_error, f"Analyzer file not found: {analyzer_path}")
                return

            cmd = [sys.executable, analyzer_path, target_path]

            # Check if analyzer supports recursive and verbose flags
            # We'll do a simple check by reading the file and looking for argument parsing
            supports_recursive = False
            supports_verbose = False

            try:
                with open(analyzer_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    supports_recursive = "--recursive" in content or "recursive" in content
                    supports_verbose = "--verbose" in content or "verbose" in content
            except Exception:
                # If we can't read the file, assume it doesn't support these flags
                pass

            if self.recursive_var.get() and supports_recursive:
                cmd.append("--recursive")

            if self.verbose_var.get() and supports_verbose:
                cmd.append("--verbose")

            # Run the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )

            self.current_process = process

            # Capture output
            stdout_data = []
            stderr_data = []

            # Read stdout
            for line in process.stdout:
                stdout_data.append(line)
                self.update_output(line)

            # Read stderr
            for line in process.stderr:
                stderr_data.append(line)
                self.update_output(f"ERROR: {line}", error=True)

            # Wait for process to complete
            process.wait()

            # Process complete
            self.root.after(0, self._analysis_complete,
                           process.returncode, ''.join(stdout_data), ''.join(stderr_data))

        except Exception as e:
            self.root.after(0, self._analysis_error, str(e))

    def update_output(self, text, error=False):
        """Update the output text widget from the main thread."""
        self.root.after(0, self._update_output_text, text, error)

    def _update_output_text(self, text, error=False):
        """Update the output text widget (called from main thread)."""
        self.output_text.config(state=tk.NORMAL)

        if error:
            self.output_text.insert(tk.END, text, "error")
            self.output_text.tag_configure("error", foreground="red")
        else:
            self.output_text.insert(tk.END, text)

        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _analysis_complete(self, return_code, stdout, stderr):
        """Handle completed analysis (called from main thread)."""
        self.progress.stop()

        if return_code == 0:
            self.status_var.set("Analysis completed successfully")
            self._generate_summary(stdout)
        else:
            self.status_var.set(f"Analysis failed with code {return_code}")

            if stderr:
                self.summary_text.config(state=tk.NORMAL)
                self.summary_text.insert(tk.END, "Analysis Failed\n\n", "header")
                self.summary_text.insert(tk.END, stderr, "error")
                self.summary_text.tag_configure("header", font=("Arial", 12, "bold"))
                self.summary_text.tag_configure("error", foreground="red")
                self.summary_text.config(state=tk.DISABLED)

        self.current_process = None

    def _analysis_error(self, error_message):
        """Handle analysis error (called from main thread)."""
        self.progress.stop()
        self.status_var.set(f"Error: {error_message}")

        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\nERROR: {error_message}\n", "error")
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.config(state=tk.DISABLED)

        self.current_process = None

    def _generate_summary(self, output):
        """Generate a summary from the analyzer output."""
        self.summary_text.config(state=tk.NORMAL)

        # Clear summary
        self.summary_text.delete(1.0, tk.END)

        # Add header
        analyzer_name = self.analyzer_var.get()
        target_path = self.target_path.get()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.summary_text.insert(tk.END, f"Analysis Summary\n", "header")
        self.summary_text.insert(tk.END, f"Analyzer: {analyzer_name}\n")
        self.summary_text.insert(tk.END, f"Target: {target_path}\n")
        self.summary_text.insert(tk.END, f"Time: {timestamp}\n\n")

        # Configure tags
        self.summary_text.tag_configure("header", font=("Arial", 12, "bold"))

        # Try to extract key information based on the analyzer
        if "srp_analyzer" in analyzer_name.lower():
            self._summarize_srp_output(output)
        elif "missing_files" in analyzer_name.lower():
            self._summarize_missing_files(output)
        elif "package_size" in analyzer_name.lower():
            self._summarize_package_size(output)
        else:
            # Generic summary
            self.summary_text.insert(tk.END, "Key Findings:\n\n", "subheader")

            # Look for lines with "violation", "error", "warning"
            important_lines = []
            for line in output.split('\n'):
                lower_line = line.lower()
                if any(keyword in lower_line for keyword in
                      ["violation", "error", "warning", "failed", "missing"]):
                    important_lines.append(line)

            if important_lines:
                for line in important_lines[:10]:  # Show first 10
                    self.summary_text.insert(tk.END, f"• {line}\n")

                if len(important_lines) > 10:
                    self.summary_text.insert(tk.END, f"\n... and {len(important_lines) - 10} more issues\n")
            else:
                self.summary_text.insert(tk.END, "No significant issues found.\n")

        self.summary_text.tag_configure("subheader", font=("Arial", 10, "bold"))
        self.summary_text.config(state=tk.DISABLED)

        # Switch to summary tab
        self.notebook.select(1)  # Index 1 is the Summary tab

    def _summarize_srp_output(self, output):
        """Summarize SRP analyzer output."""
        self.summary_text.insert(tk.END, "Single Responsibility Principle Analysis\n\n", "subheader")

        # Count violations
        violations = []
        current_file = None

        for line in output.split('\n'):
            if line.startswith("Analyzing ") and line.endswith(".py"):
                current_file = line.split("Analyzing ")[1].strip()
            elif ("has multiple responsibilities" in line or
                  "may have too many responsibilities" in line) and current_file:
                violations.append((current_file, line))

        if violations:
            self.summary_text.insert(tk.END, f"Found {len(violations)} SRP violations:\n\n")

            for file_path, message in violations:
                self.summary_text.insert(tk.END, f"• {os.path.basename(file_path)}: {message}\n")
        else:
            self.summary_text.insert(tk.END, "No SRP violations found. Great job!\n")

    def _summarize_missing_files(self, output):
        """Summarize missing files output."""
        self.summary_text.insert(tk.END, "Missing Files Analysis\n\n", "subheader")

        # Extract missing files
        missing_files = []

        for line in output.split('\n'):
            if line.startswith("  - "):  # Missing file line format
                missing_files.append(line[4:])

        if missing_files:
            self.summary_text.insert(tk.END, f"Found {len(missing_files)} missing files:\n\n")

            for file_path in missing_files:
                self.summary_text.insert(tk.END, f"• {file_path}\n")
        else:
            self.summary_text.insert(tk.END, "No missing files found. Great job!\n")

    def _summarize_package_size(self, output):
        """Summarize package size output."""
        self.summary_text.insert(tk.END, "Package Size Analysis\n\n", "subheader")

        # Extract key statistics
        total_size = None
        largest_files = []
        capture_largest = False  # Initialize the flag

        for line in output.split('\n'):
            if "Total package size:" in line:
                total_size = line.split("Total package size:")[1].strip()
            elif "Largest files:" in line:
                # Next lines will be largest files
                capture_largest = True
            elif capture_largest and line.strip() and ":" in line:
                largest_files.append(line.strip())
            elif capture_largest and not line.strip():
                capture_largest = False

        if total_size:
            self.summary_text.insert(tk.END, f"Total package size: {total_size}\n\n")

        if largest_files:
            self.summary_text.insert(tk.END, "Largest files:\n\n")

            for file_info in largest_files[:5]:  # Show top 5
                self.summary_text.insert(tk.END, f"• {file_info}\n")

def main():
    root = tk.Tk()
    app = CodeAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
