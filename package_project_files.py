#!/usr/bin/env python
"""
AutoQliq Project Files Packaging Script

This script packages essential project files (source code, documentation, and important
root files) into a single text file with specific START/END markers for each file.
The output is compatible with the apply_packaged_codebase_enhanced.py script.

The script will:
1. Include important files from the root directory
2. Walk through the src directory
3. Include documentation files
4. Filter out dependencies and non-essential files
5. Validate file paths for compatibility
6. Generate a text file with START/END markers for each file
7. Optionally organize text files, keeping only the newest output in the main directory

Usage:
    python package_project_files.py [options]

Options:
    --root-dir DIR       Root directory of the project (default: current directory)
    --output FILE        Output file path (default: autoqliq_project_files.txt)
    --exclude-dirs DIRS  Directories to exclude (space-separated)
    --exclude-patterns P File patterns to exclude (space-separated)
    --organize          Organize text files after packaging
"""

import os
import argparse
from pathlib import Path
from typing import List, Tuple
import fnmatch
import datetime
import logging

# Configure logging
log_filename = f"source_packaging_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)
logger = logging.getLogger(__name__)

# Directories and patterns to exclude
DEFAULT_EXCLUDE_DIRS = [
    '__pycache__',
    'venv',
    '.venv',
    'env',
    'node_modules',
    'dist',
    'build',
    'site-packages',
    '.pytest_cache',
    '.mypy_cache',
    '.eggs',
    '.tox',
]

# File patterns to exclude
DEFAULT_EXCLUDE_PATTERNS = [
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*.so',
    '*.dll',
    '*.exe',
    '*.egg-info',
    '*.egg',
    '*.whl',
    '*.log',
    '*.db',
    '*.sqlite',
    '*.sqlite3',
    '*.coverage',
    '*.DS_Store',
    '*_refactored*.py',
    '*_v*.py',
]

def is_excluded_path(path: str, exclude_dirs: List[str]) -> bool:
    """Check if a path should be excluded based on directory names."""
    path_parts = Path(path).parts
    return any(exclude_dir in path_parts for exclude_dir in exclude_dirs)

def matches_pattern(filename: str, patterns: List[str]) -> bool:
    """Check if a filename matches any of the given patterns."""
    return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)

def is_valid_path(path: str) -> bool:
    """Check if a path is valid for inclusion in the packaged codebase."""
    # Check for invalid characters
    if any(c in path for c in ['*', '?', '"', '<', '>', '|', ':', '\0']):
        logger.warning(f"Path contains invalid characters: {path}")
        return False

    # Check for absolute paths
    if os.path.isabs(path):
        logger.warning(f"Absolute paths are not allowed: {path}")
        return False

    return True

def find_source_files(
    root_dir: str,
    exclude_dirs: List[str] = DEFAULT_EXCLUDE_DIRS,
    exclude_patterns: List[str] = DEFAULT_EXCLUDE_PATTERNS,
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Find all source code files and important project files, excluding dependencies and non-essential files.

    Args:
        root_dir: The root directory to start searching from
        exclude_dirs: List of directory names to exclude
        exclude_patterns: List of filename patterns to exclude

    Returns:
        Tuple containing:
            - A list of valid file paths relative to the root directory
            - A list of skipped file paths with reasons
    """
    logger.info(f"Starting to find source files in {root_dir}")
    source_files = []
    skipped_files = []

    # Important files in the root directory to include
    important_files = [
        'README.md',
        'requirements.txt',
        'progress.md',
        'progress_phase1_archived.md',
        'refactor.md',
        'implementation.md',
        'project_status.md',
        'package_codebase.py',
        'apply_packaged_codebase_enhanced.py',
        'package_source_only.py',
        'analyze_package_size.py',
        'exclude_paths.txt'
    ]

    # Add important files from the root directory
    for filename in important_files:
        file_path = os.path.join(root_dir, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            rel_path = os.path.relpath(file_path, root_dir)
            source_files.append(rel_path)
            logger.info(f"Added important file: {rel_path}")

    # Include files from the src directory
    src_dir = os.path.join(root_dir, 'src')
    if not os.path.exists(src_dir):
        logger.error(f"Source directory not found: {src_dir}")
    else:
        for dirpath, dirnames, filenames in os.walk(src_dir):
            # Track excluded directories
            excluded_dirs = []
            for d in list(dirnames):
                if d in exclude_dirs or any(fnmatch.fnmatch(d, pattern) for pattern in exclude_dirs if '*' in pattern):
                    excluded_dirs.append(d)
                    dirnames.remove(d)

            # Log excluded directories
            for d in excluded_dirs:
                dir_path = os.path.relpath(os.path.join(dirpath, d), root_dir)
                skipped_files.append((dir_path, "Excluded directory"))

            # Process files
            for filename in filenames:
                # Get the full path and relative path
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)

                # Skip files matching exclude patterns
                if matches_pattern(filename, exclude_patterns):
                    skipped_files.append((rel_path, "Matches exclude pattern"))
                    continue

                # Skip if any part of the path is in exclude_dirs
                if is_excluded_path(rel_path, exclude_dirs):
                    skipped_files.append((rel_path, "In excluded directory"))
                    continue

                # Validate the path
                if not is_valid_path(rel_path):
                    skipped_files.append((rel_path, "Invalid path"))
                    continue

                source_files.append(rel_path)

    # Include files from the docs directory
    docs_dir = os.path.join(root_dir, 'docs')
    if os.path.exists(docs_dir):
        for dirpath, dirnames, filenames in os.walk(docs_dir):
            # Track excluded directories
            excluded_dirs = []
            for d in list(dirnames):
                if d in exclude_dirs or any(fnmatch.fnmatch(d, pattern) for pattern in exclude_dirs if '*' in pattern):
                    excluded_dirs.append(d)
                    dirnames.remove(d)

            # Log excluded directories
            for d in excluded_dirs:
                dir_path = os.path.relpath(os.path.join(dirpath, d), root_dir)
                skipped_files.append((dir_path, "Excluded directory"))

            # Process files
            for filename in filenames:
                # Get the full path and relative path
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)

                # Skip files matching exclude patterns
                if matches_pattern(filename, exclude_patterns):
                    skipped_files.append((rel_path, "Matches exclude pattern"))
                    continue

                # Skip if any part of the path is in exclude_dirs
                if is_excluded_path(rel_path, exclude_dirs):
                    skipped_files.append((rel_path, "In excluded directory"))
                    continue

                # Validate the path
                if not is_valid_path(rel_path):
                    skipped_files.append((rel_path, "Invalid path"))
                    continue

                source_files.append(rel_path)

    logger.info(f"Found {len(source_files)} valid source files")
    logger.info(f"Skipped {len(skipped_files)} files")

    return sorted(source_files), skipped_files

def generate_output_file(
    output_file: str,
    file_paths: List[str],
    root_dir: str
) -> Tuple[int, List[Tuple[str, str]]]:
    """
    Generate the output file with START/END markers for each file.

    Args:
        output_file: Path to the output file
        file_paths: List of file paths to include
        root_dir: The root directory of the project

    Returns:
        Tuple containing:
            - Number of successfully processed files
            - List of failed files with error messages
    """
    logger.info(f"Generating output file: {output_file}")
    processed_count = 0
    failed_files = []

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header with project information
        f.write("################################################################################\n")
        f.write("# AUTOQLIQ SOURCE CODE PACKAGE\n")
        f.write("# Generated on: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("################################################################################\n\n")

        # Write detailed project summary and status
        f.write("# DETAILED PROJECT SUMMARY AND STATUS\n\n")

        f.write("## 1. Project Structure Overview\n\n")
        f.write("AutoQliq is a web automation tool designed to create, edit, and execute automated workflows for web interactions. \n")
        f.write("The application follows a layered architecture with clear separation of concerns:\n\n")
        f.write("- **Core Layer**: Domain model, interfaces, actions, workflow logic\n")
        f.write("  - Defines the core entities (Workflow, Action, Credential)\n")
        f.write("  - Implements action types (Navigate, Click, Type, Wait, Screenshot)\n")
        f.write("  - Provides workflow execution and management\n\n")
        f.write("- **Infrastructure Layer**: WebDrivers, persistence, repositories\n")
        f.write("  - Implements browser automation via Selenium and Playwright\n")
        f.write("  - Provides storage mechanisms for workflows and credentials\n")
        f.write("  - Handles file system and database operations\n\n")
        f.write("- **Application Layer**: Services, application-level interfaces\n")
        f.write("  - Implements business logic and use cases\n")
        f.write("  - Coordinates between UI and infrastructure layers\n")
        f.write("  - Manages application state and configuration\n\n")
        f.write("- **UI Layer**: Views, presenters, components\n")
        f.write("  - Provides user interface for workflow editing and execution\n")
        f.write("  - Implements presenters to mediate between views and application logic\n")
        f.write("  - Creates reusable UI components\n\n")
        f.write("- **Testing**: Unit tests, integration tests, end-to-end tests\n")
        f.write("  - Verifies behavior of individual components\n")
        f.write("  - Tests interactions between components\n")
        f.write("  - Validates complete user journeys\n\n")

        f.write("## 2. Current Implementation Status\n\n")
        f.write("### Completed (Phase 1)\n")
        f.write("- Core Domain Model with entities, interfaces, and basic implementations\n")
        f.write("- Core action types (Navigate, Click, Type, Wait, Screenshot)\n")
        f.write("- Basic workflow execution engine\n")
        f.write("- Exception handling and validation\n")
        f.write("- Unit tests for core components with >90% coverage\n\n")

        f.write("### In Progress (Phase 2)\n")
        f.write("- Infrastructure layer implementation\n")
        f.write("  - WebDriver implementations (Selenium, Playwright)\n")
        f.write("  - Repository implementations (FileSystem, Database)\n")
        f.write("- UI components for workflow editing and execution\n")
        f.write("- Presenters and application logic\n")
        f.write("- Integration tests\n\n")

        f.write("### Not Started\n")
        f.write("- Advanced security features (encryption, authentication)\n")
        f.write("- Performance optimizations (caching, parallel execution)\n")
        f.write("- Comprehensive documentation (API docs, user guides)\n")
        f.write("- Deployment and packaging (installers, containers)\n")
        f.write("- CI/CD pipeline setup\n\n")

        f.write("## 3. Unimplemented Features\n\n")
        f.write("### Core Layer\n")
        f.write("- **Advanced Action Types**: Conditional actions, loop actions, error handling actions\n")
        f.write("- **Workflow Versioning**: Track changes and maintain version history\n")
        f.write("- **Action Templates**: Reusable action templates for common tasks\n")
        f.write("- **Workflow Validation**: Comprehensive validation of workflows before execution\n\n")

        f.write("### Infrastructure Layer\n")
        f.write("- **Database Repositories**: Complete implementations for database storage\n")
        f.write("- **Cloud Storage**: Integration with cloud storage providers\n")
        f.write("- **Headless Execution**: Support for headless browser execution\n")
        f.write("- **Proxy Support**: Configure and use proxies for web automation\n")
        f.write("- **Multi-browser Support**: Complete support for Chrome, Firefox, Edge, Safari\n\n")

        f.write("### Application Layer\n")
        f.write("- **User Management**: User accounts, roles, and permissions\n")
        f.write("- **Workflow Scheduling**: Schedule workflows to run at specific times\n")
        f.write("- **Reporting**: Generate reports on workflow execution results\n")
        f.write("- **Notifications**: Email or webhook notifications for workflow events\n")
        f.write("- **API**: REST API for programmatic access to workflows\n\n")

        f.write("### UI Layer\n")
        f.write("- **Workflow Designer**: Visual drag-and-drop workflow designer\n")
        f.write("- **Dashboard**: Overview of workflows, execution status, and statistics\n")
        f.write("- **Element Inspector**: Visual tool to identify web elements\n")
        f.write("- **Result Viewer**: Detailed view of workflow execution results\n")
        f.write("- **Settings Panel**: Configure application settings\n\n")

        f.write("## 4. Key Gaps and Missing Components\n\n")
        f.write("### Infrastructure Layer Gaps\n")
        f.write("- **Repository Implementations**: Need to complete FileSystemWorkflowRepository and FileSystemCredentialRepository\n")
        f.write("- **WebDriver Implementations**: Need to complete Selenium and Playwright implementations\n")
        f.write("- **Error Handling**: Need comprehensive error handling and recovery mechanisms\n\n")

        f.write("### UI Layer Gaps\n")
        f.write("- **Component Structure**: Need to refactor UI components for better separation of concerns\n")
        f.write("- **Presenters**: Need to implement WorkflowEditorPresenter and WorkflowRunnerPresenter\n")
        f.write("- **UI Factory**: Need to refactor for better component creation and management\n\n")

        f.write("### Testing Gaps\n")
        f.write("- **Integration Tests**: Need tests for component interactions\n")
        f.write("- **End-to-End Tests**: Need tests for complete user journeys\n")
        f.write("- **Test Coverage**: Need to ensure >90% coverage across all components\n\n")

        f.write("### Documentation Gaps\n")
        f.write("- **API Documentation**: Need comprehensive documentation for all public APIs\n")
        f.write("- **Architecture Documentation**: Need diagrams and explanations of system architecture\n")
        f.write("- **User Guides**: Need guides for end users\n")
        f.write("- **Developer Guides**: Need guides for contributors\n\n")

        f.write("## 5. Priority Areas for Immediate Focus\n\n")
        f.write("1. **Complete Repository Implementations**: Finish the FileSystemWorkflowRepository and FileSystemCredentialRepository\n")
        f.write("2. **Refactor UI Components**: Improve separation of concerns in UI layer\n")
        f.write("3. **Implement Presenters**: Complete WorkflowEditorPresenter and WorkflowRunnerPresenter\n")
        f.write("4. **Add Integration Tests**: Create tests for component interactions\n")
        f.write("5. **Improve Documentation**: Start with API documentation for completed components\n\n")

        f.write("## 6. Development Principles\n\n")
        f.write("### TDD (Test-Driven Development)\n")
        f.write("- Write tests before implementation (Red-Green-Refactor cycle)\n")
        f.write("- Ensure >90% test coverage for all components\n")
        f.write("- Tests should verify behavior, not implementation details\n")
        f.write("- Refactor only after tests pass\n\n")

        f.write("### SOLID Principles\n")
        f.write("- **Single Responsibility**: Each class should have only one reason to change\n")
        f.write("- **Open/Closed**: Open for extension, closed for modification\n")
        f.write("- **Liskov Substitution**: Subtypes must be substitutable for their base types\n")
        f.write("- **Interface Segregation**: Many client-specific interfaces are better than one general-purpose interface\n")
        f.write("- **Dependency Inversion**: Depend on abstractions, not concretions\n\n")

        f.write("### KISS (Keep It Simple, Stupid)\n")
        f.write("- Keep methods short (≤20 lines)\n")
        f.write("- Avoid premature optimization\n")
        f.write("- Prefer simple solutions over complex ones\n")
        f.write("- Clear naming and straightforward logic\n\n")

        f.write("### DRY (Don't Repeat Yourself)\n")
        f.write("- No duplicated code\n")
        f.write("- Extract shared functionality into utilities\n")
        f.write("- Single source of truth for all information\n")
        f.write("- Use inheritance and composition appropriately\n\n")

        f.write("################################################################################\n")
        f.write("# FILE CONTENTS\n")
        f.write("################################################################################\n\n")

        # Process each file
        for file_path in file_paths:
            full_path = os.path.join(root_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()

                # Use forward slashes for consistency in paths
                normalized_path = file_path.replace('\\', '/')
                content_size = len(content)
                content_lines = content.count('\n') + 1

                logger.info(f"Processing {normalized_path}: {content_size} bytes, {content_lines} lines")

                # Write start marker
                f.write("################################################################################\n")
                f.write(f"########## START FILE: [{normalized_path}] ##########\n")
                f.write("################################################################################\n")

                # Write file content
                f.write(content)

                # Add a newline if the file doesn't end with one
                if content and not content.endswith('\n'):
                    f.write('\n')

                # Write end marker
                f.write("################################################################################\n")
                f.write(f"########## END FILE: [{normalized_path}] ##########\n")
                f.write("################################################################################\n\n")

                processed_count += 1
            except Exception as e:
                error_msg = f"Error reading file {file_path}: {e}"
                logger.error(error_msg)
                failed_files.append((file_path, str(e)))

    return processed_count, failed_files

def main():
    """Main function."""
    start_time = datetime.datetime.now()
    logger.info(f"Script started at {start_time}")

    parser = argparse.ArgumentParser(
        description='Package project files into a single text file with START/END markers.'
    )
    parser.add_argument(
        '--root-dir',
        default='.',
        help='Root directory of the project (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='autoqliq_project_files.txt',
        help='Output file path (default: autoqliq_project_files.txt)'
    )
    parser.add_argument(
        '--exclude-dirs',
        nargs='+',
        default=DEFAULT_EXCLUDE_DIRS,
        help='Directories to exclude (space-separated)'
    )
    parser.add_argument(
        '--exclude-patterns',
        nargs='+',
        default=DEFAULT_EXCLUDE_PATTERNS,
        help='File patterns to exclude (space-separated)'
    )
    parser.add_argument(
        '--organize',
        action='store_true',
        help='Organize text files after packaging (default: False)'
    )

    args = parser.parse_args()

    # Find source files
    source_files, skipped_files = find_source_files(
        args.root_dir,
        args.exclude_dirs,
        args.exclude_patterns
    )

    # Generate output file
    processed_count, failed_files = generate_output_file(args.output, source_files, args.root_dir)

    # Calculate elapsed time
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Print summary
    print(f"\nPackaging completed!")
    print(f"  Found: {len(source_files)} source files")
    print(f"  Processed: {processed_count} files")
    print(f"  Failed: {len(failed_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")
    print(f"  Total time: {elapsed_time}")
    print(f"\nOutput written to {args.output}")

    if failed_files:
        print("\nFailed files:")
        for file_path, error in failed_files[:10]:  # Show only first 10 to avoid clutter
            print(f"  {file_path}: {error}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")

    if skipped_files:
        print("\nSkipped files (not included in package):")
        # Group skipped files by reason
        reasons = {}
        for file_path, reason in skipped_files:
            if reason not in reasons:
                reasons[reason] = []
            reasons[reason].append(file_path)

        # Print skipped files by reason
        for reason, files in reasons.items():
            print(f"\n  Reason: {reason}")
            for file_path in files[:5]:  # Show only first 5 for each reason
                print(f"    {file_path}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

    logger.info(f"Processing complete. Found: {len(source_files)}, Processed: {processed_count}, "
                f"Failed: {len(failed_files)}, Skipped: {len(skipped_files)}")
    logger.info(f"Script completed at {end_time} (elapsed: {elapsed_time})")

    # Organize text files if requested
    if args.organize:
        organize_text_files(args.output)
        print("\nText files organized. Only the newest output file remains in the main directory.")

    return args.output

def organize_text_files(output_file: str):
    """
    Organize text files by moving them to appropriate directories,
    keeping only the newest output file in the main directory.

    Args:
        output_file: Path to the newest output file that should remain in the main directory
    """
    logger.info("Organizing text files...")

    # Create directories if they don't exist
    os.makedirs("archived_packages", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # Get all text files in the main directory
    text_files = [f for f in os.listdir(".") if f.endswith(".txt") and os.path.isfile(f)]

    # Skip the newest output file
    if output_file in text_files:
        text_files.remove(output_file)

    # Move files to appropriate directories
    for file_name in text_files:
        source_path = os.path.join(".", file_name)

        # Determine destination directory based on file name
        if file_name.startswith("autoqliq_codebase") or file_name.startswith("autoqliq_project_files"):
            dest_dir = "archived_packages"
        elif file_name.endswith(".log") or "log" in file_name.lower():
            dest_dir = "logs"
        elif file_name.startswith("code_quality_scripts_"):
            dest_dir = "archived_packages"
        elif file_name == "requirements.txt":
            # Keep requirements.txt in the main directory
            continue
        else:
            dest_dir = "temp"

        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)

        # Move the file
        dest_path = os.path.join(dest_dir, file_name)
        try:
            # Check if file already exists in destination
            if os.path.exists(dest_path):
                # Add timestamp to avoid overwriting
                base_name, ext = os.path.splitext(file_name)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_file_name = f"{base_name}_{timestamp}{ext}"
                dest_path = os.path.join(dest_dir, new_file_name)

            # Move the file
            os.rename(source_path, dest_path)
            logger.info(f"Moved {file_name} to {dest_path}")
        except Exception as e:
            logger.error(f"Failed to move {file_name}: {e}")

    logger.info("File organization complete")

if __name__ == "__main__":
    # Run the main packaging function
    output_file = main()

    # Ask user if they want to organize files
    try:
        response = input("\nDo you want to organize text files, keeping only the newest output file in the main directory? (y/n): ")
        if response.lower() in ['y', 'yes']:
            organize_text_files(output_file)
            print("\nText files organized. Only the newest output file remains in the main directory.")
    except KeyboardInterrupt:
        print("\nSkipping file organization.")
