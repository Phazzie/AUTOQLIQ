#!/usr/bin/env python3
"""
Script to check for missing important files in the AutoQliq project.
"""

import os
import sys
from datetime import datetime

# List of core files that should exist
CORE_FILES = [
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
    "src/core/actions/error_handling_action.py",
    "src/core/actions/navigation.py",
    "src/core/actions/interaction.py",
    "src/core/actions/utility.py",
    "src/core/actions/__init__.py",
    
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
    "src/application/services/__init__.py",
    
    # Infrastructure
    "src/infrastructure/repositories/workflow_repository.py",
    "src/infrastructure/repositories/database_workflow_repository.py",
    "src/infrastructure/repositories/credential_repository.py",
    "src/infrastructure/repositories/database_credential_repository.py",
    "src/infrastructure/repositories/__init__.py",
    "src/infrastructure/webdrivers/selenium_driver.py",
    "src/infrastructure/webdrivers/__init__.py",
    "src/infrastructure/common/logging_utils.py",
    "src/infrastructure/common/connection_manager.py",
    
    # UI
    "src/ui/presenters/base_presenter.py",
    "src/ui/presenters/workflow_editor_presenter.py",
    "src/ui/presenters/workflow_runner_presenter.py",
    "src/ui/presenters/settings_presenter.py",
    "src/ui/presenters/__init__.py",
    "src/ui/views/base_view.py",
    "src/ui/views/workflow_editor_view.py",
    "src/ui/views/workflow_runner_view.py",
    "src/ui/views/settings_view.py",
    "src/ui/views/__init__.py",
    "src/ui/dialogs/action_editor_dialog.py",
    "src/ui/dialogs/credential_manager_dialog.py",
    "src/ui/dialogs/__init__.py",
    "src/ui/common/ui_factory.py",
    "src/ui/common/__init__.py",
    "src/ui/interfaces/presenter.py",
    "src/ui/interfaces/view.py",
    "src/ui/interfaces/__init__.py",
    
    # Main files
    "src/main_ui.py",
    "src/config.py",
    "src/__init__.py",
    
    # Configuration
    "config.ini",
    
    # Documentation
    "README.md"
]

def check_missing_files():
    """Check for missing important files and output the results."""
    missing_files = []
    existing_files = []
    
    for file_path in CORE_FILES:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    # Output results
    print(f"Found {len(existing_files)} existing files and {len(missing_files)} missing files.")
    
    if missing_files:
        print("\nMissing files:")
        for file in missing_files:
            print(f"  - {file}")
    
    # Check for main entry point specifically
    if "src/main_ui.py" in missing_files:
        print("\nWARNING: Main entry point (src/main_ui.py) is missing!")
    
    return existing_files, missing_files

if __name__ == "__main__":
    existing_files, missing_files = check_missing_files()
    
    # Output to file if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--output":
        with open("missing_files.md", "w", encoding="utf-8") as out_file:
            out_file.write("# AutoQliq Missing Files\n\n")
            out_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            out_file.write(f"## Summary\n\n")
            out_file.write(f"- Found {len(existing_files)} existing files\n")
            out_file.write(f"- Found {len(missing_files)} missing files\n\n")
            
            if missing_files:
                out_file.write("## Missing Files\n\n")
                for file in missing_files:
                    out_file.write(f"- `{file}`\n")
            
            out_file.write("\n## Existing Files\n\n")
            for file in existing_files:
                out_file.write(f"- `{file}`\n")
        
        print(f"\nDetailed results written to missing_files.md")
