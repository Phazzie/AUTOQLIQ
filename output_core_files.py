#!/usr/bin/env python3
"""
Script to output core AutoQliq files to a single markdown file for review.
This helps with sharing the current state of key files with other AI systems.
"""

import os
import sys
from datetime import datetime

# List of files to output
FILES_TO_OUTPUT = [
    # Core interfaces
    "src/core/interfaces/action.py",
    "src/core/interfaces/repository.py",
    "src/core/interfaces/webdriver.py",
    "src/core/interfaces/service.py",
    "src/core/interfaces/presenter.py",
    "src/core/interfaces/view.py",

    # Core actions
    "src/core/actions/base.py",
    "src/core/actions/factory.py",
    "src/core/actions/conditional_action.py",
    "src/core/actions/loop_action.py",
    "src/core/actions/template_action.py",

    # Core workflow
    "src/core/workflow/runner.py",
    "src/core/workflow/workflow.py",
    "src/core/workflow/errors.py",

    # Core utilities
    "src/core/exceptions.py",
    "src/core/action_result.py",

    # Application services
    "src/application/services/credential_service.py",
    "src/application/services/workflow_service.py",
    "src/application/services/webdriver_service.py",
    "src/application/services/reporting_service.py",
    "src/application/services/scheduler_service.py",

    # Infrastructure
    "src/infrastructure/repositories/workflow_repository.py",
    "src/infrastructure/repositories/database_workflow_repository.py",
    "src/infrastructure/common/connection_manager.py",

    # UI
    "src/ui/presenters/base_presenter.py",
    "src/ui/presenters/workflow_runner_presenter.py",
    "src/ui/views/base_view.py",

    # Main files
    "src/main_ui.py",
    "src/config.py",

    # Configuration
    "config.ini",

    # Documentation
    "README.md"
]

def output_files(output_file="core_files.md"):
    """Output the content of the specified files to a markdown file."""
    with open(output_file, "w", encoding="utf-8") as out_file:
        # Write header
        out_file.write(f"# AutoQliq Core Files\n\n")
        out_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Process each file
        for file_path in FILES_TO_OUTPUT:
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Write file header
                    out_file.write(f"## {file_path}\n\n")

                    # Determine language for syntax highlighting
                    extension = os.path.splitext(file_path)[1]
                    language = ""
                    if extension == ".py":
                        language = "python"
                    elif extension == ".ini":
                        language = "ini"
                    elif extension == ".md":
                        language = "markdown"

                    # Write file content with syntax highlighting
                    out_file.write(f"```{language}\n")
                    out_file.write(content)
                    if not content.endswith("\n"):
                        out_file.write("\n")
                    out_file.write("```\n\n")
                else:
                    out_file.write(f"## {file_path}\n\n")
                    out_file.write(f"*File not found*\n\n")
            except Exception as e:
                out_file.write(f"## {file_path}\n\n")
                out_file.write(f"*Error reading file: {str(e)}*\n\n")

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    output_file = "core_files.md"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    output_files(output_file)
