#!/usr/bin/env python
"""
AutoQliq Responsibility Analyzer

This script analyzes Python files in the codebase to estimate the number of responsibilities
each file has, helping identify potential violations of the Single Responsibility Principle.

Usage:
    python analyze_responsibilities.py [directory]
"""

import os
import sys
import ast
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# Configuration
MAX_RESPONSIBILITIES = 1  # Maximum number of responsibilities a file should have
MIN_METHODS_FOR_CONCERN = 3  # Minimum number of methods to consider a group a separate concern
IGNORE_PATTERNS = [
    r'__init__\.py$',
    r'__pycache__',
    r'\.git',
    r'\.vscode',
    r'\.idea',
    r'venv',
    r'env',
    r'tests',
]

class ResponsibilityAnalyzer(ast.NodeVisitor):
    """
    AST visitor that analyzes Python files to estimate the number of responsibilities.
    """

    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.responsibility_groups = defaultdict(list)
        self.current_class = None

    def visit_ClassDef(self, node):
        """Visit a class definition."""
        old_class = self.current_class
        self.current_class = node.name
        self.classes.append(node)
        # Visit all child nodes
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        if self.current_class:
            # This is a method
            self.functions.append((self.current_class, node.name, node))

            # Group methods by responsibility based on name prefixes
            prefix = self._get_method_prefix(node.name)
            if prefix:
                self.responsibility_groups[prefix].append(node.name)
        else:
            # This is a standalone function
            self.functions.append((None, node.name, node))

        # Visit all child nodes
        self.generic_visit(node)

    def visit_Import(self, node):
        """Visit an import statement."""
        for name in node.names:
            self.imports.append(name.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit a from-import statement."""
        for name in node.names:
            if node.module:
                self.imports.append(f"{node.module}.{name.name}")
            else:
                self.imports.append(name.name)
        self.generic_visit(node)

    def _get_method_prefix(self, method_name: str) -> Optional[str]:
        """
        Extract a prefix from a method name to group related methods.

        Examples:
            get_user -> get
            set_name -> set
            handle_click -> handle
            on_button_press -> on
        """
        prefixes = ['get', 'set', 'create', 'update', 'delete', 'handle', 'on', 'validate', 'parse', 'format', 'load', 'save']
        for prefix in prefixes:
            if method_name.startswith(prefix + '_'):
                return prefix
        return None

    def estimate_responsibilities(self) -> Tuple[int, List[str]]:
        """
        Estimate the number of responsibilities in the analyzed file.

        Returns:
            Tuple containing:
            - Estimated number of responsibilities
            - List of responsibility descriptions
        """
        responsibilities = []

        # Check for multiple unrelated classes
        if len(self.classes) > 1:
            class_names = [cls.name for cls in self.classes]
            responsibilities.append(f"Multiple classes: {', '.join(class_names)}")

        # Check for responsibility groups within classes
        significant_groups = []
        for prefix, methods in self.responsibility_groups.items():
            if len(methods) >= MIN_METHODS_FOR_CONCERN:
                significant_groups.append((prefix, methods))

        if significant_groups:
            for prefix, methods in significant_groups:
                responsibilities.append(f"{prefix.capitalize()} operations: {len(methods)} methods")

        # If we have a single class with no significant method groups, count it as one responsibility
        if len(self.classes) == 1 and not significant_groups:
            responsibilities.append(f"Single class: {self.classes[0].name}")

        # Check for standalone functions (outside classes)
        standalone_functions = [name for cls, name, _ in self.functions if cls is None]
        if standalone_functions:
            responsibilities.append(f"Standalone functions: {len(standalone_functions)} functions")

        # If we couldn't identify any specific responsibilities but have code, assume at least one
        if not responsibilities and (self.classes or self.functions):
            responsibilities.append("Unclassified responsibility")

        return len(responsibilities), responsibilities

def should_ignore(file_path: str) -> bool:
    """Check if a file should be ignored based on patterns."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False

def analyze_file(file_path: str) -> Tuple[int, List[str]]:
    """
    Analyze a Python file to estimate its responsibilities.

    Args:
        file_path: Path to the Python file

    Returns:
        Tuple containing:
        - Estimated number of responsibilities
        - List of responsibility descriptions
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove triple backtick blocks that might cause syntax errors
        content = re.sub(r'```[^`]*```', '', content)
        # Remove any remaining triple backticks
        content = re.sub(r'```', '', content)

        tree = ast.parse(content)
        analyzer = ResponsibilityAnalyzer()
        analyzer.visit(tree)

        return analyzer.estimate_responsibilities()
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return 1, ["Error during analysis"]

def analyze_directory(directory: str) -> Dict[str, Tuple[int, List[str]]]:
    """
    Recursively analyze all Python files in a directory.

    Args:
        directory: Directory to analyze

    Returns:
        Dictionary mapping file paths to responsibility analysis results
    """
    results = {}

    for root, _, files in os.walk(directory):
        if should_ignore(root):
            continue

        for file in files:
            if file.endswith('.py') and not should_ignore(file):
                file_path = os.path.join(root, file)
                results[file_path] = analyze_file(file_path)

    return results

def print_report(results: Dict[str, Tuple[int, List[str]]]):
    """
    Print a report of the responsibility analysis.

    Args:
        results: Dictionary mapping file paths to responsibility analysis results
    """
    print("\n=== AutoQliq Responsibility Analysis Report ===\n")

    # Sort files by number of responsibilities (descending)
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1][0],
        reverse=True
    )

    # Print files with too many responsibilities
    print(f"Files with more than {MAX_RESPONSIBILITIES} responsibility:\n")
    violations_found = False

    for file_path, (num_responsibilities, responsibilities) in sorted_results:
        if num_responsibilities > MAX_RESPONSIBILITIES:
            violations_found = True
            rel_path = os.path.relpath(file_path)
            print(f"{rel_path}: {num_responsibilities} responsibilities")
            for resp in responsibilities:
                print(f"  - {resp}")
            print()

    if not violations_found:
        print("  No violations found! All files follow the Single Responsibility Principle.\n")

    # Print summary statistics
    total_files = len(results)
    compliant_files = sum(1 for _, (num, _) in results.items() if num <= MAX_RESPONSIBILITIES)
    violation_files = total_files - compliant_files

    print("Summary:")
    print(f"  Total files analyzed: {total_files}")
    if total_files > 0:
        print(f"  Files with 1 responsibility: {compliant_files} ({compliant_files/total_files*100:.1f}%)")
        print(f"  Files with multiple responsibilities: {violation_files} ({violation_files/total_files*100:.1f}%)")
    else:
        print("  No files were analyzed.")

    # Print the top 10 worst offenders
    if violation_files > 0:
        print("\nTop offenders:")
        for i, (file_path, (num_responsibilities, _)) in enumerate(sorted_results[:10]):
            if num_responsibilities > MAX_RESPONSIBILITIES:
                rel_path = os.path.relpath(file_path)
                print(f"  {i+1}. {rel_path}: {num_responsibilities} responsibilities")

def main():
    """Main entry point."""
    directory = sys.argv[1] if len(sys.argv) > 1 else 'src'

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)

    print(f"Analyzing Python files in '{directory}'...")
    results = analyze_directory(directory)
    print_report(results)

if __name__ == "__main__":
    main()
