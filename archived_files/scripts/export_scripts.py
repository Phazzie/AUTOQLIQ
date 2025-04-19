#!/usr/bin/env python
"""
Script Exporter

This script exports the contents of all code quality analyzer scripts to a single text file.
It helps with reviewing all scripts at once and identifying issues.

Usage:
    python export_scripts.py
"""

import os
import datetime

# List of scripts to export
SCRIPTS_TO_EXPORT = [
    # Archived standalone analyzers (now in 'archived' directory)
    "archived/analyze_single_responsibility.py",  # SRP
    "archived/analyze_open_closed.py",           # OCP
    "archived/analyze_liskov_substitution.py",   # LSP
    "archived/analyze_interface_segregation.py", # ISP
    "archived/analyze_dependency_inversion.py",  # DIP

    # Other archived code quality analyzers
    "archived/analyze_kiss.py",                  # KISS principle
    "archived/analyze_dry.py",                   # DRY principle
    "archived/analyze_responsibilities.py",      # Alternative SRP analyzer
    "archived/count_responsibilities.py",        # Responsibility counter

    # Integrated suite core files
    "code_quality_analyzer/__init__.py",
    "code_quality_analyzer/__main__.py",
    "code_quality_analyzer/base_analyzer.py",
    "code_quality_analyzer/unified_analyzer.py",

    # Analyzers in the integrated suite
    "code_quality_analyzer/analyzers/__init__.py",

    # SOLID Principle Analyzers
    "code_quality_analyzer/analyzers/srp_analyzer.py",  # Single Responsibility Principle
    "code_quality_analyzer/analyzers/ocp_analyzer.py",  # Open/Closed Principle
    "code_quality_analyzer/analyzers/lsp_analyzer.py",  # Liskov Substitution Principle
    "code_quality_analyzer/analyzers/isp_analyzer.py",  # Interface Segregation Principle
    "code_quality_analyzer/analyzers/dip_analyzer.py",  # Dependency Inversion Principle

    # Other Code Quality Analyzers
    "code_quality_analyzer/analyzers/kiss_analyzer.py", # Keep It Simple, Stupid
    "code_quality_analyzer/analyzers/dry_analyzer.py",  # Don't Repeat Yourself

    # Examples
    "code_quality_analyzer/examples/analyze_example.py",
    "code_quality_analyzer/examples/run_analysis.py",
    "code_quality_analyzer/examples/sample_code.py",

    # Tests
    "code_quality_analyzer/tests/__init__.py",
    "code_quality_analyzer/tests/run_tests.py",
    "code_quality_analyzer/tests/test_analyzers.py",

    # Setup and documentation
    "code_quality_analyzer/setup.py",
    "code_quality_analyzer/README.md"
]

def export_scripts():
    """Export all scripts to a single text file."""
    # Create output filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"code_quality_scripts_{timestamp}.txt"

    print(f"Exporting scripts to {output_file}...")

    # Count successful exports
    successful_exports = 0
    total_lines = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# CODE QUALITY ANALYZER SCRIPTS\n")
        f.write(f"# Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# This file contains all code quality analyzer scripts for easy reference\n\n")

        # Write summary
        f.write("# SUMMARY\n")
        f.write("# =======\n\n")
        f.write("The Code Quality Analyzer is a comprehensive suite of tools for analyzing code quality,\n")
        f.write("focusing on SOLID principles, KISS, and DRY. It includes both standalone analyzers\n")
        f.write("(now archived) and an integrated framework.\n\n")

        f.write("## SOLID Principles\n")
        f.write("- **S**ingle Responsibility Principle (SRP): A class should have only one reason to change\n")
        f.write("- **O**pen/Closed Principle (OCP): Software entities should be open for extension but closed for modification\n")
        f.write("- **L**iskov Substitution Principle (LSP): Subtypes must be substitutable for their base types\n")
        f.write("- **I**nterface Segregation Principle (ISP): Clients should not be forced to depend on methods they do not use\n")
        f.write("- **D**ependency Inversion Principle (DIP): High-level modules should not depend on low-level modules\n\n")

        f.write("## Other Principles\n")
        f.write("- **K**eep **I**t **S**imple, **S**tupid (KISS): Simplicity should be a key goal and unnecessary complexity avoided\n")
        f.write("- **D**on't **R**epeat **Y**ourself (DRY): Every piece of knowledge must have a single, unambiguous representation\n\n")

        # Write table of contents
        f.write("# TABLE OF CONTENTS\n")
        f.write("# ================\n\n")

        # Group scripts by category and ensure no duplicates
        categorized_paths = set()
        categories = {}

        # Define category assignment functions
        def is_archived(path):
            return path.startswith("archived/")

        def is_core_file(path):
            return path.startswith("code_quality_analyzer/") and "/" not in path.replace("code_quality_analyzer/", "")

        def is_solid_analyzer(path):
            return "/analyzers/" in path and any(path.endswith(f"{p}_analyzer.py") for p in ["srp", "ocp", "lsp", "isp", "dip"])

        def is_other_analyzer(path):
            return "/analyzers/" in path and any(path.endswith(f"{p}_analyzer.py") for p in ["kiss", "dry"])

        def is_example(path):
            return "/examples/" in path

        def is_test(path):
            return "/tests/" in path

        def is_setup_or_doc(path):
            return path.endswith("setup.py") or path.endswith(".md")

        # Assign scripts to categories in order of priority
        categories["ARCHIVED STANDALONE ANALYZERS"] = []
        categories["INTEGRATED CORE FILES"] = []
        categories["SOLID PRINCIPLE ANALYZERS"] = []
        categories["OTHER CODE QUALITY ANALYZERS"] = []
        categories["EXAMPLES"] = []
        categories["TESTS"] = []
        categories["SETUP AND DOCUMENTATION"] = []

        for path in SCRIPTS_TO_EXPORT:
            if path in categorized_paths:
                continue

            if is_archived(path):
                categories["ARCHIVED STANDALONE ANALYZERS"].append(path)
            elif is_core_file(path):
                categories["INTEGRATED CORE FILES"].append(path)
            elif is_solid_analyzer(path):
                categories["SOLID PRINCIPLE ANALYZERS"].append(path)
            elif is_other_analyzer(path):
                categories["OTHER CODE QUALITY ANALYZERS"].append(path)
            elif is_example(path):
                categories["EXAMPLES"].append(path)
            elif is_test(path):
                categories["TESTS"].append(path)
            elif is_setup_or_doc(path):
                categories["SETUP AND DOCUMENTATION"].append(path)

            categorized_paths.add(path)

        # Write table of contents with line numbers
        line_count = 0
        toc_entries = []

        for category, paths in categories.items():
            if paths:
                toc_entries.append((category, line_count))
                line_count += len(paths) * 6  # Approximate lines per file entry in TOC

        for category, line_num in toc_entries:
            f.write(f"# {category} (Line {line_num})\n")

        f.write("\n\n")

        # Write each category of scripts
        for category, paths in categories.items():
            if paths:
                f.write(f"\n\n{'#' * 80}\n")
                f.write(f"# {category}\n")
                f.write(f"{'#' * 80}\n\n")

                for script_path in paths:
                    if os.path.exists(script_path):
                        f.write(f"\n\n{'=' * 80}\n")
                        f.write(f"# FILE: {script_path}\n")
                        f.write(f"{'=' * 80}\n\n")

                        try:
                            with open(script_path, 'r', encoding='utf-8') as script_file:
                                content = script_file.read()
                                f.write(content)
                                line_count = content.count('\n') + 1
                                total_lines += line_count
                            print(f"✅ Exported: {script_path} ({line_count} lines)")
                            successful_exports += 1
                        except Exception as e:
                            f.write(f"ERROR: Could not read file: {str(e)}\n")
                            print(f"❌ Failed to export: {script_path} - {str(e)}")
                    else:
                        f.write(f"\n\n{'=' * 80}\n")
                        f.write(f"# FILE: {script_path}\n")
                        f.write(f"{'=' * 80}\n\n")
                        f.write(f"ERROR: File not found\n")
                        print(f"❌ File not found: {script_path}")

    print(f"\nExport completed. All scripts have been exported to {output_file}")
    print(f"Total scripts processed: {len(SCRIPTS_TO_EXPORT)}")
    print(f"Successfully exported: {successful_exports} scripts")
    print(f"Total lines of code: {total_lines}")

if __name__ == "__main__":
    export_scripts()
