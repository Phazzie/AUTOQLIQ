#!/usr/bin/env python
"""
AutoQliq Gemini Output Parser

This script parses Gemini-generated output and extracts the files and their contents.
It looks for file markers in the format:
########## START FILE: [path] ##########
(file content)
########## END FILE: [path] ##########

Usage:
    python parse_gemini.py <gemini_output_file>
"""

import os
import sys
import re
from pathlib import Path
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gemini_parsing.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_gemini_output(file_path):
    """
    Parse the Gemini output file and extract file paths and contents.
    
    Args:
        file_path (str): Path to the Gemini output file
        
    Returns:
        dict: Dictionary mapping file paths to content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)
    
    # Extract files using regex
    file_pattern = re.compile(r'########## START FILE: (.*?) ##########\s+(.*?)########## END FILE: \1 ##########', re.DOTALL)
    
    file_contents = {}
    for match in file_pattern.finditer(content):
        file_path = match.group(1).strip()
        file_content = match.group(2).strip()
        file_contents[file_path] = file_content
    
    return file_contents

def apply_changes(file_contents, dry_run=False):
    """
    Apply the changes to the codebase.
    
    Args:
        file_contents (dict): Dictionary mapping file paths to content
        dry_run (bool): If True, don't actually write files
        
    Returns:
        tuple: (created_files, updated_files, skipped_files)
    """
    created_files = []
    updated_files = []
    skipped_files = []
    
    for file_path, content in file_contents.items():
        # Normalize path (replace forward slashes with the OS-specific separator)
        normalized_path = os.path.normpath(file_path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(normalized_path)
        if directory and not os.path.exists(directory) and not dry_run:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Check if file exists
        file_exists = os.path.exists(normalized_path)
        
        if dry_run:
            status = "NEW" if not file_exists else "UPDATE"
            logger.info(f"[DRY RUN] Would {status.lower()} file: {normalized_path}")
            if file_exists:
                updated_files.append(normalized_path)
            else:
                created_files.append(normalized_path)
            continue
        
        # Write the file
        try:
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if file_exists:
                logger.info(f"Updated file: {normalized_path}")
                updated_files.append(normalized_path)
            else:
                logger.info(f"Created file: {normalized_path}")
                created_files.append(normalized_path)
        except Exception as e:
            logger.error(f"Failed to write {normalized_path}: {e}")
            skipped_files.append(normalized_path)
    
    return created_files, updated_files, skipped_files

def update_missing_files_json(created_files, gemini_file):
    """
    Update the gemini_missing_files.json file to remove entries for files that were created.
    
    Args:
        created_files (list): List of files that were created
        gemini_file (str): Name of the Gemini file being processed
    """
    json_path = "gemini_missing_files.json"
    
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                missing_files = json.load(f)
        else:
            missing_files = {}
        
        # Remove entries for files that were created
        for file_path in created_files:
            if file_path in missing_files:
                del missing_files[file_path]
                logger.info(f"Removed {file_path} from missing files list")
        
        # Write updated missing files list
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(missing_files, f, indent=2)
        
        logger.info(f"Updated {json_path}")
    except Exception as e:
        logger.error(f"Failed to update missing files JSON: {e}")

def main():
    """Main function to run the script."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <gemini_output_file> [--dry-run]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    logger.info(f"Processing Gemini output from {input_file}")
    
    # Parse the Gemini output
    file_contents = parse_gemini_output(input_file)
    logger.info(f"Found {len(file_contents)} files in the Gemini output")
    
    # Ask for confirmation if not dry run
    if not dry_run:
        print("\nThe following files will be created or updated:")
        for file_path in file_contents:
            normalized_path = os.path.normpath(file_path)
            status = "NEW" if not os.path.exists(normalized_path) else "UPDATE"
            print(f"  [{status}] {normalized_path}")
        
        confirmation = input("\nDo you want to proceed? (y/n): ")
        if confirmation.lower() != 'y':
            logger.info("Operation cancelled by user")
            sys.exit(0)
    
    # Apply the changes
    created_files, updated_files, skipped_files = apply_changes(file_contents, dry_run)
    
    # Print summary
    print("\nParsing completed!")
    print(f"  Created: {len(created_files)} files")
    print(f"  Updated: {len(updated_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")
    
    if skipped_files:
        print("\nSkipped files:")
        for file_path in skipped_files:
            print(f"  {file_path}")
    
    # Update missing files JSON if not dry run
    if not dry_run and created_files:
        gemini_file_name = os.path.basename(input_file)
        update_missing_files_json(created_files, gemini_file_name)
    
    logger.info("Parsing completed successfully")

if __name__ == "__main__":
    main()
