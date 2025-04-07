#!/usr/bin/env python3
"""
Script to archive all markdown (.md) files by adding an ARCHIVED marker and moving them to an archive folder.
"""

import os
import glob
import shutil
import datetime

def archive_md_files(archive_folder="archived_docs"):
    """
    Archive all markdown files by adding an ARCHIVED marker and moving them to an archive folder.
    
    Args:
        archive_folder: Path to the folder where archived files will be stored
    """
    # Create archive folder if it doesn't exist
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)
        print(f"Created folder: {archive_folder}")
    
    # Find all markdown files
    md_files = glob.glob("*.md")
    
    # Files to exclude from archiving
    exclude_files = ["README.md"]  # Keep the main README
    
    # Filter out excluded files
    md_files = [f for f in md_files if f not in exclude_files]
    
    if not md_files:
        print("No markdown files found to archive")
        return
    
    print(f"Found {len(md_files)} markdown files to archive")
    
    # Archive each file
    for file_path in md_files:
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add archive marker
            archive_date = datetime.datetime.now().strftime('%Y-%m-%d')
            archive_marker = f"**********ARCHIVED**********\nArchived on: {archive_date}\n\n"
            
            # Prepare new content with archive marker
            if content.startswith("#"):
                # If file starts with a heading, insert marker after the first heading
                lines = content.split('\n')
                new_content = lines[0] + '\n\n' + archive_marker + '\n'.join(lines[1:])
            else:
                # Otherwise, insert at the beginning
                new_content = archive_marker + content
            
            # Create the target path in the archive folder
            filename = os.path.basename(file_path)
            target_path = os.path.join(archive_folder, filename)
            
            # Write the modified content to the archive location
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Archived {file_path} to {target_path}")
            
            # Remove the original file
            os.remove(file_path)
            print(f"Removed original file: {file_path}")
            
        except Exception as e:
            print(f"Error archiving {file_path}: {e}")
    
    print(f"\nSummary:")
    print(f"- Archived {len(md_files)} markdown files to {archive_folder}")
    print(f"- Added archive markers to all files")
    print(f"- Removed original files")
    print(f"- Excluded files: {', '.join(exclude_files)}")

if __name__ == "__main__":
    archive_md_files()
