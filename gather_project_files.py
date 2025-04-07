#!/usr/bin/env python
"""
Script to gather all project files (excluding dependencies) and output them in a specific format.

The script will:
1. Walk through the project directory
2. Filter out dependencies and non-project files
3. Generate a text file with FILE LIST and FILE CONTENTS sections
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Set, Tuple

# Directories and patterns to exclude (these are typically dependencies or generated files)
DEFAULT_EXCLUDE_DIRS = [
    '.git',
    '.github',
    '.vscode',
    '__pycache__',
    'venv',
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

def is_excluded_path(path: str, exclude_dirs: List[str]) -> bool:
    """Check if a path should be excluded based on directory names."""
    path_parts = Path(path).parts
    return any(exclude_dir in path_parts for exclude_dir in exclude_dirs)

def matches_pattern(filename: str, patterns: List[str]) -> bool:
    """Check if a filename matches any of the given patterns."""
    from fnmatch import fnmatch
    return any(fnmatch(filename, pattern) for pattern in patterns)

def has_included_extension(filename: str, extensions: List[str]) -> bool:
    """Check if a filename has one of the included extensions."""
    return any(filename.endswith(ext) for ext in extensions)

def find_project_files(
    root_dir: str,
    exclude_dirs: List[str] = DEFAULT_EXCLUDE_DIRS,
    exclude_patterns: List[str] = DEFAULT_EXCLUDE_PATTERNS,
    include_extensions: List[str] = DEFAULT_INCLUDE_EXTENSIONS,
    additional_exclude_paths: List[str] = None,
) -> List[str]:
    """
    Find all project files, excluding dependencies and non-project files.
    
    Args:
        root_dir: The root directory to start searching from
        exclude_dirs: List of directory names to exclude
        exclude_patterns: List of filename patterns to exclude
        include_extensions: List of file extensions to include
        additional_exclude_paths: Additional specific paths to exclude
        
    Returns:
        A list of file paths relative to the root directory
    """
    project_files = []
    additional_exclude_paths = additional_exclude_paths or []
    
    # Convert additional_exclude_paths to absolute paths for comparison
    abs_exclude_paths = [os.path.abspath(os.path.join(root_dir, p)) for p in additional_exclude_paths]
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
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
                continue
                
            # Skip if any part of the path is in exclude_dirs
            if is_excluded_path(rel_path, exclude_dirs):
                continue
                
            project_files.append(rel_path)
    
    return sorted(project_files)

def generate_output_file(
    output_file: str,
    file_paths: List[str],
    root_dir: str
) -> None:
    """
    Generate the output file in the required format.
    
    Args:
        output_file: Path to the output file
        file_paths: List of file paths to include
        root_dir: The root directory of the project
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write FILE LIST section
        f.write("FILE LIST\n")
        for file_path in file_paths:
            f.write(f"{file_path}\n")
        
        f.write("\n")
        
        # Write FILE CONTENTS section
        f.write("FILE CONTENTS\n")
        for file_path in file_paths:
            full_path = os.path.join(root_dir, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()
                
                f.write(f"FILE: {file_path}\n")
                f.write(f"{content}\n\n")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Gather project files and output them in a specific format.'
    )
    parser.add_argument(
        '--root-dir', 
        default='.', 
        help='Root directory of the project (default: current directory)'
    )
    parser.add_argument(
        '--output', 
        default='project_files.txt', 
        help='Output file path (default: project_files.txt)'
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
    args = parse_arguments()
    
    # Load additional exclude paths from file if specified
    additional_exclude_paths = args.exclude_paths
    if args.exclude_file and os.path.exists(args.exclude_file):
        with open(args.exclude_file, 'r') as f:
            additional_exclude_paths.extend([line.strip() for line in f if line.strip()])
    
    # Find project files
    project_files = find_project_files(
        args.root_dir,
        args.exclude_dirs,
        args.exclude_patterns,
        args.include_extensions,
        additional_exclude_paths
    )
    
    # Generate output file
    generate_output_file(args.output, project_files, args.root_dir)
    
    print(f"Found {len(project_files)} project files.")
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
