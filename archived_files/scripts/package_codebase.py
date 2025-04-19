#!/usr/bin/env python
"""
AutoQliq Codebase Packaging Script

This script packages all project files (excluding dependencies) into a single text file
with specific START/END markers for each file. The output is compatible with the
apply_packaged_codebase_enhanced.py script.

The script will:
1. Walk through the project directory
2. Filter out dependencies and non-project files
3. Validate file paths for compatibility
4. Generate a text file with START/END markers for each file

The output format uses markers like this:
################################################################################
########## START FILE: [path/to/file.ext] ##########
################################################################################
(file content)
################################################################################
########## END FILE: [path/to/file.ext] ##########
################################################################################

Usage:
    python package_codebase.py [options]

--------------------------------------------------------------------------------
# PROJECT OVERVIEW FOR AI ANALYSIS
--------------------------------------------------------------------------------

## 1. Project Structure Overview

AutoQliq follows a layered architecture with clear separation of concerns:

- Core Layer: Domain model, interfaces, actions, workflow logic
- Infrastructure Layer: WebDrivers, persistence, repositories
- Application Layer: Services, application-level interfaces
- UI Layer: Views, presenters, components
- Testing: Unit tests, integration tests, end-to-end tests

## 2. Current Implementation Status

- Phase 1 (Completed): Core Domain Model with entities, interfaces, actions
- Phase 2 (In Progress): Infrastructure layer, UI components, presenters
- Not Started: Advanced security, performance optimizations, comprehensive docs

## 3. Key Gaps and Missing Components

- Infrastructure Layer: Need to complete repository and WebDriver implementations
- UI Layer: Need to refactor components and implement presenters
- Testing: Need integration tests and end-to-end tests
- Documentation: Need API docs, architecture docs, user guides
- Tooling: Need build/deployment processes, CI/CD pipeline

## 4. Priority Areas for Immediate Focus

- Complete Repository Implementations
- Refactor UI Components for better separation of concerns
- Implement Presenters for workflow editing and execution
- Add Integration Tests for component interactions
- Improve Documentation for completed components

## 5. Development Principles

- TDD: Red-Green-Refactor cycle, tests before implementation, >90% coverage
- SOLID: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- KISS: Simple solutions, no premature optimization, methods ≤20 lines
- DRY: No duplicated code, shared functionality in utilities, single source of truth
"""

import os
import argparse
from pathlib import Path
from typing import List, Tuple
import fnmatch
import datetime
import logging

# Directories and patterns to exclude (these are typically dependencies or generated files)
DEFAULT_EXCLUDE_DIRS = [
    '.git',
    '.github',
    '.vscode',
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
    '*.egg-info',
]

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
    '*.class',
    '*.jar',
    '*.war',
    '*.min.js',
    '*.min.css',
    '*.bundle.js',
    '*.bundle.css',
    '*.lock',
    'package-lock.json',
    'yarn.lock',
    'Pipfile.lock',
    'poetry.lock',
]

# File extensions to include (customize based on your project)
DEFAULT_INCLUDE_EXTENSIONS = [
    '.py',
    '.js',
    '.ts',
    '.jsx',
    '.tsx',
    '.html',
    '.css',
    '.scss',
    '.json',
    '.md',
    '.yaml',
    '.yml',
    '.xml',
    '.txt',
]

# Configure logging
log_filename = f"codebase_packaging_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)
logger = logging.getLogger(__name__)

def is_excluded_path(path: str, exclude_dirs: List[str]) -> bool:
    """Check if a path should be excluded based on directory names."""
    path_parts = Path(path).parts
    return any(exclude_dir in path_parts for exclude_dir in exclude_dirs)

def matches_pattern(filename: str, patterns: List[str]) -> bool:
    """Check if a filename matches any of the given patterns."""
    return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)

def has_included_extension(filename: str, extensions: List[str]) -> bool:
    """Check if a filename has one of the included extensions."""
    return any(filename.endswith(ext) for ext in extensions)

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

def find_project_files(
    root_dir: str,
    exclude_dirs: List[str] = DEFAULT_EXCLUDE_DIRS,
    exclude_patterns: List[str] = DEFAULT_EXCLUDE_PATTERNS,
    include_extensions: List[str] = DEFAULT_INCLUDE_EXTENSIONS,
    additional_exclude_paths: List[str] = None,
) -> Tuple[List[str], List[str]]:
    """
    Find all project files, excluding dependencies and non-project files.

    Args:
        root_dir: The root directory to start searching from
        exclude_dirs: List of directory names to exclude
        exclude_patterns: List of filename patterns to exclude
        include_extensions: List of file extensions to include
        additional_exclude_paths: Additional specific paths to exclude

    Returns:
        Tuple containing:
            - A list of valid file paths relative to the root directory
            - A list of skipped file paths with reasons
    """
    logger.info(f"Starting to find project files in {root_dir}")
    project_files = []
    skipped_files = []
    additional_exclude_paths = additional_exclude_paths or []

    # Convert additional_exclude_paths to absolute paths for comparison
    abs_exclude_paths = [os.path.abspath(os.path.join(root_dir, p)) for p in additional_exclude_paths]

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs and
                      not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_dirs if '*' in pattern)]

        # Process files
        for filename in filenames:
            # Skip files matching exclude patterns
            if matches_pattern(filename, exclude_patterns):
                continue

            # Only include files with specified extensions
            if not has_included_extension(filename, include_extensions):
                continue

            # Get the full path and relative path
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_dir)

            # Skip if the path is in additional_exclude_paths
            if os.path.abspath(full_path) in abs_exclude_paths:
                skipped_files.append((rel_path, "In exclude paths list"))
                continue

            # Skip if any part of the path is in exclude_dirs
            if is_excluded_path(rel_path, exclude_dirs):
                skipped_files.append((rel_path, "In excluded directory"))
                continue

            # Validate the path
            if not is_valid_path(rel_path):
                skipped_files.append((rel_path, "Invalid path"))
                continue

            project_files.append(rel_path)

    logger.info(f"Found {len(project_files)} valid project files")
    logger.info(f"Skipped {len(skipped_files)} files")

    return sorted(project_files), skipped_files

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
        f.write("# AUTOQLIQ PROJECT CODEBASE PACKAGE\n")
        f.write("# Generated on: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("################################################################################\n\n")

        # Write project overview
        f.write("# PROJECT OVERVIEW FOR AI ANALYSIS\n\n")

        f.write("## 1. Project Structure Overview\n\n")
        f.write("AutoQliq follows a layered architecture with clear separation of concerns:\n\n")
        f.write("- Core Layer: Domain model, interfaces, actions, workflow logic\n")
        f.write("- Infrastructure Layer: WebDrivers, persistence, repositories\n")
        f.write("- Application Layer: Services, application-level interfaces\n")
        f.write("- UI Layer: Views, presenters, components\n")
        f.write("- Testing: Unit tests, integration tests, end-to-end tests\n\n")

        f.write("## 2. Current Implementation Status\n\n")
        f.write("- Phase 1 (Completed): Core Domain Model with entities, interfaces, actions\n")
        f.write("- Phase 2 (In Progress): Infrastructure layer, UI components, presenters\n")
        f.write("- Not Started: Advanced security, performance optimizations, comprehensive docs\n\n")

        f.write("## 3. Key Gaps and Missing Components\n\n")
        f.write("- Infrastructure Layer: Need to complete repository and WebDriver implementations\n")
        f.write("- UI Layer: Need to refactor components and implement presenters\n")
        f.write("- Testing: Need integration tests and end-to-end tests\n")
        f.write("- Documentation: Need API docs, architecture docs, user guides\n")
        f.write("- Tooling: Need build/deployment processes, CI/CD pipeline\n\n")

        f.write("## 4. Priority Areas for Immediate Focus\n\n")
        f.write("- Complete Repository Implementations\n")
        f.write("- Refactor UI Components for better separation of concerns\n")
        f.write("- Implement Presenters for workflow editing and execution\n")
        f.write("- Add Integration Tests for component interactions\n")
        f.write("- Improve Documentation for completed components\n\n")

        f.write("## 5. Development Principles\n\n")
        f.write("- TDD: Red-Green-Refactor cycle, tests before implementation, >90% coverage\n")
        f.write("- SOLID: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion\n")
        f.write("- KISS: Simple solutions, no premature optimization, methods ≤20 lines\n")
        f.write("- DRY: No duplicated code, shared functionality in utilities, single source of truth\n\n")

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

def parse_arguments():
    """Parse command line arguments."""
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
        default='packaged_codebase.txt',
        help='Output file path (default: packaged_codebase.txt)'
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
        '--include-extensions',
        nargs='+',
        default=DEFAULT_INCLUDE_EXTENSIONS,
        help='File extensions to include (space-separated)'
    )
    parser.add_argument(
        '--exclude-paths',
        nargs='+',
        default=[],
        help='Specific paths to exclude (space-separated, relative to root)'
    )
    parser.add_argument(
        '--exclude-file',
        help='File containing paths to exclude (one per line)'
    )

    return parser.parse_args()

def main():
    """Main function."""
    start_time = datetime.datetime.now()
    logger.info(f"Script started at {start_time}")

    args = parse_arguments()

    # Load additional exclude paths from file if specified
    additional_exclude_paths = args.exclude_paths
    if args.exclude_file and os.path.exists(args.exclude_file):
        with open(args.exclude_file, 'r') as f:
            additional_exclude_paths.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
        logger.info(f"Loaded {len(additional_exclude_paths)} exclude paths from {args.exclude_file}")

    # Find project files
    project_files, skipped_files = find_project_files(
        args.root_dir,
        args.exclude_dirs,
        args.exclude_patterns,
        args.include_extensions,
        additional_exclude_paths
    )

    # Generate output file
    processed_count, failed_files = generate_output_file(args.output, project_files, args.root_dir)

    # Calculate elapsed time
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Print summary
    print(f"\nPackaging completed!")
    print(f"  Found: {len(project_files)} project files")
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

    logger.info(f"Processing complete. Found: {len(project_files)}, Processed: {processed_count}, "
                f"Failed: {len(failed_files)}, Skipped: {len(skipped_files)}")
    logger.info(f"Script completed at {end_time} (elapsed: {elapsed_time})")

if __name__ == "__main__":
    main()
