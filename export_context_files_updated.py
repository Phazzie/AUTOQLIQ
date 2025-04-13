#!/usr/bin/env python
"""
AutoQliq Context Files Exporter

This script exports the essential context files for the AutoQliq project,
organized into groups based on their importance for providing context in a new chat window.

The files are exported to a 'context_export' folder with clear markers for each group.
"""

import os
import shutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('context_export.log')
    ]
)
logger = logging.getLogger(__name__)

# Define the files to export
# Group 1: MUST ADD
GROUP_1_FILES = [
    "src/core/interfaces/action.py",
    "src/core/interfaces/repository.py",
    "src/core/interfaces/webdriver.py",
    "src/core/interfaces/service.py",
    "src/core/actions/base.py",
    "src/core/actions/factory.py",
    "src/core/workflow/runner.py",
    "src/core/exceptions.py",
    "src/core/action_result.py",
    "src/ui/interfaces/presenter.py",
    "src/ui/interfaces/view.py",
    "src/ui/presenters/base_presenter.py",
    "src/ui/views/base_view.py",
    "src/config.py",
    "config.ini",
    "src/main_ui.py",
    "README.md",
    "src/ui/common/ui_factory.py",
    "src/ui/dialogs/action_editor_dialog.py",
    "src/ui/dialogs/credential_manager_dialog.py",
    "src/ui/views/settings_view.py",
    "src/ui/presenters/settings_presenter.py"
]

# Group 2: SHOULD PROBABLY ADD
GROUP_2_FILES = [
    "src/application/services/credential_service.py",
    "src/application/services/workflow_service.py",
    "src/application/services/webdriver_service.py",
    "src/application/services/scheduler_service.py",
    "src/application/services/reporting_service.py",
    "src/core/actions/conditional_action.py",
    "src/core/actions/loop_action.py",
    "src/core/actions/error_handling_action.py",
    "src/core/actions/template_action.py",
    "src/infrastructure/common/error_handling.py",
    "src/infrastructure/common/logging_utils.py",
    "src/ui/common/status_bar.py"
]

# Group 3: COULD ADD
GROUP_3_FILES = [
    "src/infrastructure/repositories/base/database_repository.py",
    "src/infrastructure/repositories/base/file_system_repository.py",
    "src/infrastructure/webdrivers/selenium_driver.py",
    "src/ui/presenters/workflow_editor_presenter.py"
]

# Combine all files
FILES_TO_EXPORT = GROUP_1_FILES + GROUP_2_FILES + GROUP_3_FILES

def create_export_folder():
    """Create the export folder with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_folder = f"context_export_{timestamp}"

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
        logger.info(f"Created export folder: {export_folder}")

    return export_folder

def export_file(file_path, export_folder):
    """Export a single file to the export folder."""
    # Normalize path
    normalized_path = os.path.normpath(file_path)

    # Check if file exists
    if not os.path.exists(normalized_path):
        logger.warning(f"File not found: {normalized_path}")
        return False

    # Read file content
    try:
        with open(normalized_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file {normalized_path}: {e}")
        return False

    # Create the export content with markers
    export_content = f"""
########## START FILE: {file_path} ##########

{content}

########## END FILE: {file_path} ##########

"""

    # Write to the export file
    export_file_path = os.path.join(export_folder, "context_files.txt")
    try:
        with open(export_file_path, 'a', encoding='utf-8') as f:
            f.write(export_content)
        logger.info(f"Exported file: {normalized_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to export file: {e}")
        return False

def create_file_list(export_folder):
    """Create a list of all files that were exported."""
    file_list_content = "# Files included in this export:\n\n"

    for file_path in FILES_TO_EXPORT:
        normalized_path = os.path.normpath(file_path)
        exists = "✓" if os.path.exists(normalized_path) else "✗"
        file_list_content += f"{exists} {file_path}\n"

    # Write to the file list file
    file_list_path = os.path.join(export_folder, "file_list.txt")
    try:
        with open(file_list_path, 'w', encoding='utf-8') as f:
            f.write(file_list_content)
        logger.info(f"Created file list")
        return True
    except Exception as e:
        logger.error(f"Failed to write file list: {e}")
        return False

def create_prompt_template(export_folder):
    """Create a template for the first prompt in a new chat window."""
    template_content = """
# First Prompt Template for New Chat Window

```
Okay, let's resume work on the AutoQliq project.

**Goal for this Session:**
[DESCRIBE YOUR IMMEDIATE GOAL HERE]

**Essential Context Files:**

[PASTE SELECTED FILES FROM context_files.txt HERE]

**What I'd like to accomplish:**
[DESCRIBE SPECIFIC TASKS OR FEATURES YOU WANT TO IMPLEMENT]

Please analyze these files and help me [SPECIFIC REQUEST].
```

Instructions:
1. Copy this template
2. Fill in the sections in [BRACKETS]
3. For the Essential Context Files section, copy and paste the relevant files from context_files.txt
4. Remove these instructions before sending the prompt
"""

    # Write to the template file
    template_file_path = os.path.join(export_folder, "first_prompt_template.txt")
    try:
        with open(template_file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        logger.info(f"Created prompt template")
        return True
    except Exception as e:
        logger.error(f"Failed to write prompt template: {e}")
        return False

def main():
    """Main function to run the script."""
    # Create export folder
    export_folder = create_export_folder()

    # Create empty context_files.txt to start fresh
    open(os.path.join(export_folder, "context_files.txt"), 'w').close()

    # Add header to context_files.txt
    with open(os.path.join(export_folder, "context_files.txt"), 'w', encoding='utf-8') as f:
        f.write(f"""# AutoQliq Context Files
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This file contains the essential context files for the AutoQliq project.

""")

    # Export all files
    for file_path in FILES_TO_EXPORT:
        export_file(file_path, export_folder)

    # Create file list
    create_file_list(export_folder)

    # Create prompt template
    create_prompt_template(export_folder)

    # Print summary
    print(f"\nContext files exported to {export_folder}/")
    print(f"  - context_files.txt: Contains all exported files with markers")
    print(f"  - file_list.txt: Contains a list of all files that were exported")
    print(f"  - first_prompt_template.txt: Template for the first prompt in a new chat window")

    logger.info("Export completed successfully")

if __name__ == "__main__":
    main()
