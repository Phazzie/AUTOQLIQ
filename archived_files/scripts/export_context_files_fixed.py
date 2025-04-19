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

# Define the groups of files
GROUP_1_MUST_ADD = [
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
    "README.md"
]

GROUP_2_SHOULD_ADD = [
    "src/application/services/credential_service.py",
    "src/application/services/workflow_service.py",
    "src/application/services/webdriver_service.py",
    "src/application/services/reporting_service.py",
    "src/application/services/scheduler_service.py",
    "src/core/actions/conditional_action.py",
    "src/core/actions/loop_action.py",
    "src/core/actions/template_action.py",
    "src/core/actions/error_handling_action.py",
    "src/infrastructure/common/error_handling.py",
    "src/infrastructure/common/logging_utils.py",
    "src/infrastructure/repositories/repository_factory.py",
    "src/ui/common/ui_factory.py",
    "src/ui/dialogs/action_editor_dialog.py",
    "src/ui/dialogs/credential_manager_dialog.py",
    "src/ui/presenters/settings_presenter.py",
    "src/ui/views/settings_view.py"
]

GROUP_3_COULD_ADD = [
    "src/core/actions/navigation.py",
    "src/core/actions/interaction.py",
    "src/core/actions/utility.py",
    "src/infrastructure/common/database_connection.py",
    "src/infrastructure/common/validators.py",
    "src/infrastructure/repositories/base/database_repository.py",
    "src/infrastructure/repositories/base/file_system_repository.py",
    "src/infrastructure/repositories/base/repository.py",
    "src/infrastructure/repositories/workflow_repository.py",
    "src/infrastructure/repositories/database_workflow_repository.py",
    "src/infrastructure/repositories/serialization/action_serializer.py",
    "src/infrastructure/repositories/serialization/workflow_metadata_serializer.py",
    "src/infrastructure/webdrivers/base.py",
    "src/infrastructure/webdrivers/error_handler.py",
    "src/infrastructure/webdrivers/factory.py",
    "src/infrastructure/webdrivers/selenium_driver.py",
    "src/ui/common/error_handler.py",
    "src/ui/common/form_validator.py",
    "src/ui/common/widget_factory.py",
    "tests/unit/application/test_credential_service.py",
    "tests/unit/application/test_workflow_service.py",
    "tests/unit/application/test_reporting_service.py",
    "tests/unit/application/test_scheduler_service.py",
    "tests/unit/core/test_workflow.py",
    "tests/unit/core/test_actions.py",
    "tests/unit/core/test_conditional_action.py",
    "tests/unit/core/test_loop_action.py",
    "tests/unit/core/test_error_handling_action.py",
    "tests/integration/test_database_repository_integration.py",
    "tests/integration/test_presenter_repository_integration.py",
    "tests/integration/test_service_repository_integration.py",
    "tests/integration/test_webdriver_integration.py"
]

def create_export_folder():
    """Create a folder for the exported files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_folder = f"context_export_{timestamp}"
    
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
        logger.info(f"Created export folder: {export_folder}")
    
    return export_folder

def export_files(export_folder):
    """Export all files to the export folder."""
    # Create the context_files.txt file
    context_files_path = os.path.join(export_folder, "context_files.txt")
    
    with open(context_files_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# AutoQliq Context Files\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write Group 1 files
        f.write("# Group 1: MUST ADD\n")
        f.write("# These files are essential for understanding the core architecture\n\n")
        
        for file_path in GROUP_1_MUST_ADD:
            if os.path.exists(file_path):
                f.write(f"########## START FILE: {file_path} ##########\n")
                f.write("# GROUP: Group 1: MUST ADD\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                        f.write(content)
                        if not content.endswith('\n'):
                            f.write('\n')
                except Exception as e:
                    f.write(f"ERROR: Could not read file: {str(e)}\n")
                    logger.error(f"Failed to read file {file_path}: {e}")
                
                f.write(f"\n########## END FILE: {file_path} ##########\n\n")
                logger.info(f"Exported Group 1 file: {file_path}")
            else:
                logger.warning(f"Group 1 file not found: {file_path}")
        
        # Write Group 2 files
        f.write("\n# Group 2: SHOULD PROBABLY ADD\n")
        f.write("# These files are important for understanding specific implementations\n\n")
        
        for file_path in GROUP_2_SHOULD_ADD:
            if os.path.exists(file_path):
                f.write(f"########## START FILE: {file_path} ##########\n")
                f.write("# GROUP: Group 2: SHOULD PROBABLY ADD\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                        f.write(content)
                        if not content.endswith('\n'):
                            f.write('\n')
                except Exception as e:
                    f.write(f"ERROR: Could not read file: {str(e)}\n")
                    logger.error(f"Failed to read file {file_path}: {e}")
                
                f.write(f"\n########## END FILE: {file_path} ##########\n\n")
                logger.info(f"Exported Group 2 file: {file_path}")
            else:
                logger.warning(f"Group 2 file not found: {file_path}")
        
        # Write Group 3 files
        f.write("\n# Group 3: COULD ADD\n")
        f.write("# These files provide additional context for specific tasks\n\n")
        
        for file_path in GROUP_3_COULD_ADD:
            if os.path.exists(file_path):
                f.write(f"########## START FILE: {file_path} ##########\n")
                f.write("# GROUP: Group 3: COULD ADD\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                        f.write(content)
                        if not content.endswith('\n'):
                            f.write('\n')
                except Exception as e:
                    f.write(f"ERROR: Could not read file: {str(e)}\n")
                    logger.error(f"Failed to read file {file_path}: {e}")
                
                f.write(f"\n########## END FILE: {file_path} ##########\n\n")
                logger.info(f"Exported Group 3 file: {file_path}")
            else:
                logger.warning(f"Group 3 file not found: {file_path}")
    
    logger.info(f"Created context_files.txt in {export_folder}")
    
    # Create the context_summary.txt file
    context_summary_path = os.path.join(export_folder, "context_summary.txt")
    
    with open(context_summary_path, 'w', encoding='utf-8') as f:
        f.write("# AutoQliq Context Summary\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Group 1 summary
        f.write("## Group 1: MUST ADD\n")
        f.write("These files are essential for understanding the core architecture\n\n")
        
        for file_path in GROUP_1_MUST_ADD:
            if os.path.exists(file_path):
                f.write(f"- {file_path}\n")
            else:
                f.write(f"- {file_path} (NOT FOUND)\n")
        
        # Group 2 summary
        f.write("\n## Group 2: SHOULD PROBABLY ADD\n")
        f.write("These files are important for understanding specific implementations\n\n")
        
        for file_path in GROUP_2_SHOULD_ADD:
            if os.path.exists(file_path):
                f.write(f"- {file_path}\n")
            else:
                f.write(f"- {file_path} (NOT FOUND)\n")
        
        # Group 3 summary
        f.write("\n## Group 3: COULD ADD\n")
        f.write("These files provide additional context for specific tasks\n\n")
        
        for file_path in GROUP_3_COULD_ADD:
            if os.path.exists(file_path):
                f.write(f"- {file_path}\n")
            else:
                f.write(f"- {file_path} (NOT FOUND)\n")
    
    logger.info(f"Created context_summary.txt in {export_folder}")
    
    # Create the first_prompt_template.txt file
    template_file_path = os.path.join(export_folder, "first_prompt_template.txt")
    
    template_content = """# First Prompt Template for New Chat Window

```
Okay, let's resume work on the AutoQliq project.

**Goal for this Session:**
[DESCRIBE YOUR IMMEDIATE GOAL HERE]

**Essential Context Files:**

[PASTE SELECTED FILES FROM context_files.txt HERE]
For example:

########## START FILE: src/core/interfaces/action.py ##########
# GROUP: Group 1: MUST ADD

[CONTENT OF THE FILE]

########## END FILE: src/core/interfaces/action.py ##########

**What I'd like to accomplish:**
[DESCRIBE SPECIFIC TASKS OR FEATURES YOU WANT TO IMPLEMENT]

Please analyze these files and help me [SPECIFIC REQUEST].
```

Instructions:
1. Copy this template
2. Fill in the sections in [BRACKETS]
3. For the Essential Context Files section, copy and paste the relevant files from context_files.txt
   - Always include all Group 1 (MUST ADD) files
   - Include Group 2 (SHOULD ADD) files relevant to your current task
   - Include Group 3 (COULD ADD) files only if directly modifying them
4. Remove these instructions before sending the prompt
"""
    
    try:
        with open(template_file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        logger.info("Created prompt template")
        return True
    except Exception as e:
        logger.error(f"Failed to write prompt template: {e}")
        return False

def main():
    """Main function to export context files."""
    logger.info("Starting context files export")
    
    # Create export folder
    export_folder = create_export_folder()
    
    # Export files
    export_files(export_folder)
    
    # Print summary
    print(f"\nContext files exported to {export_folder}/")
    print("  - context_files.txt: Contains all exported files with markers")
    print("  - context_summary.txt: Contains a summary of all files by group")
    print("  - first_prompt_template.txt: Template for the first prompt in a new chat window")
    
    logger.info("Export completed successfully")

if __name__ == "__main__":
    main()
