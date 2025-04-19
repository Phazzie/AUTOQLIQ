#!/usr/bin/env python3
"""
Script to collect the content of specific files from a project directory
and output them into a single text file, formatted for review.
"""

import os
import sys
import logging
from pathlib import Path
import argparse # Use argparse for potential future command-line options

# --- Configuration ---

# Define the output file relative to the script's location
OUTPUT_FILE_NAME = "codebase_for_review.txt"

# Configure basic logging for this script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Log to console
    ]
)
log = logging.getLogger(__name__)

# List of specific files to include (relative to project root)
# Use forward slashes for cross-platform compatibility in paths
INCLUDE_FILES = [
    "run.py",
    # "collect_codebase.py", # Typically exclude the collector itself
    # "run_refactored.py", # Exclude old runner
    "config.ini",
    "logging.conf",
    "requirements.txt",
    "src/core/interfaces.py",
    "src/core/models.py",
    "src/application/services/workflow_service.py",
    "src/application/services/webdriver_service.py",
    "src/infrastructure/webdrivers/selenium_driver.py",
    "src/infrastructure/webdrivers/playwright_driver.py",
    "src/infrastructure/repositories/file_repository.py",
    "src/infrastructure/repositories/db_repository.py",
    "src/infrastructure/utils/error_handling.py",
    "src/infrastructure/utils/logger_factory.py",
    "src/ui/main_view.py",
    "src/ui/presenters/editor_presenter.py",
    "src/ui/presenters/runner_presenter.py",
    # Add other essential files following the same pattern
    "src/main_ui.py", # Added likely entry point
    "tests/test_workflow_service.py", # Example test file
]

# --- Helper Functions ---

def get_language_identifier(file_path: Path) -> str:
    """Get the appropriate language identifier for Markdown code blocks."""
    suffix_map = {
        ".py": "python",
        ".js": "javascript",
        ".json": "json",
        ".ini": "ini",
        ".conf": "ini", # Often compatible with ini highlighting
        ".txt": "text",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sh": "bash",
    }
    return suffix_map.get(file_path.suffix.lower(), "text")

def collect_specific_files(root_dir: Path) -> list[tuple[str, Path]]:
    """
    Collects the absolute paths of specifically listed files if they exist.

    Args:
        root_dir: The root directory of the project (Path object).

    Returns:
        A list of tuples, where each tuple contains the relative path (str, using '/')
        and the absolute path (Path object) of a found file.
    """
    found_files = []
    log.info(f"Searching for {len(INCLUDE_FILES)} specific files relative to root: {root_dir}")
    for rel_path_str in INCLUDE_FILES:
        # Convert potential backslashes from definition to forward slashes for consistency
        rel_path_normalized = rel_path_str.replace("\\", "/")
        abs_path = root_dir / rel_path_normalized # Use Path object division
        if abs_path.is_file():
            log.debug(f"Found: {rel_path_normalized} ({abs_path})")
            found_files.append((rel_path_normalized, abs_path))
        else:
            log.warning(f"Specified file not found, skipping: {rel_path_normalized} (Checked: {abs_path})")
    return found_files

# --- Main Execution ---

def main():
    """Main function to collect files and write the output."""
    # Determine project root (assuming this script is in the root or a subdir)
    # For robustness, might want to search upwards for a known marker like .git or src/
    script_path = Path(__file__).resolve()
    project_root = script_path.parent # Assume script is in project root
    log.info(f"Project root identified as: {project_root}")

    output_file_path = project_root / OUTPUT_FILE_NAME
    log.info(f"Output will be written to: {output_file_path}")

    files_to_collect = collect_specific_files(project_root)

    if not files_to_collect:
        log.error("No specified files were found. Cannot create output file.")
        sys.exit(1)

    collected_count = 0
    try:
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            outfile.write("--- START OF FILE codebase_for_review.txt ---\n\n") # Add header
            for rel_path, abs_path in files_to_collect:
                log.info(f"Processing: {rel_path}")
                lang = get_language_identifier(abs_path)
                outfile.write(f"--- START FILE {rel_path} ---\n")
                try:
                    content = abs_path.read_text(encoding="utf-8")
                    outfile.write(f"```{lang}\n")
                    outfile.write(content)
                    # Ensure a newline before the closing backticks if file doesn't end with one
                    if not content.endswith('\n'):
                        outfile.write("\n")
                    outfile.write("```")
                    collected_count += 1
                except (IOError, OSError) as e:
                    log.error(f"Error reading file {rel_path}: {e}", exc_info=False)
                    outfile.write(f"[Error reading file: {e}]")
                except UnicodeDecodeError as e:
                    log.error(f"Encoding error reading file {rel_path}: {e}", exc_info=False)
                    outfile.write(f"[Encoding error reading file: {e}]")
                except Exception as e:
                    log.exception(f"Unexpected error processing file {rel_path}: {e}") # Log full trace for unexpected
                    outfile.write(f"[Unexpected error processing file: {e}]")

                outfile.write(f"\n--- END FILE {rel_path} ---\n\n")

        log.info(f"Successfully collected {collected_count} out of {len(files_to_collect)} found files into {output_file_path}")

    except IOError as e:
        log.critical(f"Failed to open or write to output file {output_file_path}: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
         log.critical(f"An unexpected error occurred during output file generation: {e}", exc_info=True)
         sys.exit(1)

if __name__ == "__main__":
    # Setup argument parsing (optional, but good practice)
    parser = argparse.ArgumentParser(description="Collects specified AutoQliq source files into a single review file.")
    # Add arguments here if needed in the future, e.g., --output-file, --root-dir
    args = parser.parse_args()

    main()

# Removed the unused `collect_files` and `should_include_file` functions.
# Replaced os.path with pathlib.Path for more modern path manipulation.
# Integrated standard logging instead of print().
# Improved error handling during file reading and writing.
# Made the list of files to include the single source of truth.
# Added a header to the output file for clarity.
