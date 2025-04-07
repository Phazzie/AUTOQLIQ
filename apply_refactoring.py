#!/usr/bin/env python
"""
AutoQliq Refactoring Script

This script parses AI-generated refactoring output and applies the changes to the codebase.
It expects a specific format for the refactored code:

FILE LIST
src/file1.py
src/file2.py
...

FILE CONTENTS
FILE: src/file1.py
(python code for file1.py)

FILE: src/file2.py
(python code for file2.py)
...

Usage:
    python apply_refactoring.py <refactored_code_file>
"""

import os
import sys
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('refactoring.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_refactored_code(file_path):
    """
    Parse the refactored code file and extract file paths and contents.
    
    Args:
        file_path (str): Path to the refactored code file
        
    Returns:
        tuple: (file_list, file_contents)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)
    
    # Extract file list section
    file_list_match = re.search(r'FILE LIST\s+(.*?)(?=\s+FILE CONTENTS)', content, re.DOTALL)
    if not file_list_match:
        logger.error("Could not find FILE LIST section in the input file")
        sys.exit(1)
    
    file_list_text = file_list_match.group(1).strip()
    file_list = [line.strip() for line in file_list_text.split('\n') if line.strip()]
    
    # Extract file contents section
    file_contents_match = re.search(r'FILE CONTENTS\s+(.*)', content, re.DOTALL)
    if not file_contents_match:
        logger.error("Could not find FILE CONTENTS section in the input file")
        sys.exit(1)
    
    file_contents_text = file_contents_match.group(1).strip()
    
    # Parse individual file contents
    file_contents = {}
    file_pattern = re.compile(r'FILE: (.*?)\s+(.*?)(?=\s+FILE:|$)', re.DOTALL)
    
    for match in file_pattern.finditer(file_contents_text):
        file_path = match.group(1).strip()
        file_content = match.group(2).strip()
        file_contents[file_path] = file_content
    
    return file_list, file_contents

def validate_parsed_data(file_list, file_contents):
    """
    Validate that all files in the list have corresponding content.
    
    Args:
        file_list (list): List of file paths
        file_contents (dict): Dictionary mapping file paths to content
        
    Returns:
        bool: True if valid, False otherwise
    """
    missing_files = []
    for file_path in file_list:
        if file_path not in file_contents:
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"The following files are in the file list but have no content: {', '.join(missing_files)}")
        return False
    
    extra_files = []
    for file_path in file_contents:
        if file_path not in file_list:
            extra_files.append(file_path)
    
    if extra_files:
        logger.warning(f"The following files have content but are not in the file list: {', '.join(extra_files)}")
    
    return len(missing_files) == 0

def apply_changes(file_list, file_contents):
    """
    Apply the changes to the codebase.
    
    Args:
        file_list (list): List of file paths
        file_contents (dict): Dictionary mapping file paths to content
        
    Returns:
        tuple: (created_files, updated_files, skipped_files)
    """
    created_files = []
    updated_files = []
    skipped_files = []
    
    for file_path in file_list:
        if file_path not in file_contents:
            logger.warning(f"Skipping {file_path} - no content available")
            skipped_files.append(file_path)
            continue
        
        content = file_contents[file_path]
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Check if file exists
        file_exists = os.path.exists(file_path)
        
        # Write the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if file_exists:
                logger.info(f"Updated file: {file_path}")
                updated_files.append(file_path)
            else:
                logger.info(f"Created file: {file_path}")
                created_files.append(file_path)
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")
            skipped_files.append(file_path)
    
    return created_files, updated_files, skipped_files

def main():
    """Main function to run the script."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <refactored_code_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    logger.info(f"Processing refactored code from {input_file}")
    
    # Parse the refactored code
    file_list, file_contents = parse_refactored_code(input_file)
    logger.info(f"Found {len(file_list)} files in the file list")
    logger.info(f"Found {len(file_contents)} files with content")
    
    # Validate the parsed data
    if not validate_parsed_data(file_list, file_contents):
        logger.error("Validation failed. Please check the input file format.")
        sys.exit(1)
    
    # Ask for confirmation
    print("\nThe following files will be created or updated:")
    for file_path in file_list:
        status = "NEW" if not os.path.exists(file_path) else "UPDATE"
        print(f"  [{status}] {file_path}")
    
    confirmation = input("\nDo you want to proceed? (y/n): ")
    if confirmation.lower() != 'y':
        logger.info("Operation cancelled by user")
        sys.exit(0)
    
    # Apply the changes
    created_files, updated_files, skipped_files = apply_changes(file_list, file_contents)
    
    # Print summary
    print("\nRefactoring completed!")
    print(f"  Created: {len(created_files)} files")
    print(f"  Updated: {len(updated_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")
    
    if skipped_files:
        print("\nSkipped files:")
        for file_path in skipped_files:
            print(f"  {file_path}")
    
    logger.info("Refactoring completed successfully")

if __name__ == "__main__":
    main()
