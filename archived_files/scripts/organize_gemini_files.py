#!/usr/bin/env python3
"""
Script to organize gemini files into their own folder and update scripts to reference them there.
"""

import os
import re
import glob
import shutil

def organize_gemini_files(target_folder="gemini_files"):
    """
    Move all gemini*.txt files to a dedicated folder and update scripts that reference them.
    
    Args:
        target_folder: Path to the folder where gemini files will be moved
    """
    # Create target folder if it doesn't exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Created folder: {target_folder}")
    
    # Find all gemini*.txt files
    gemini_files = glob.glob("gemini*.txt")
    
    if not gemini_files:
        print("No gemini files found")
        return
    
    print(f"Found {len(gemini_files)} gemini files")
    
    # Move files to target folder
    moved_files = []
    for file_path in gemini_files:
        filename = os.path.basename(file_path)
        target_path = os.path.join(target_folder, filename)
        
        # Skip if already in target folder
        if os.path.dirname(os.path.abspath(file_path)) == os.path.abspath(target_folder):
            print(f"Skipping {file_path} (already in target folder)")
            continue
        
        # Copy instead of move to avoid breaking existing scripts
        shutil.copy2(file_path, target_path)
        moved_files.append((file_path, target_path))
        print(f"Copied {file_path} to {target_path}")
    
    # Find Python scripts that might reference gemini files
    python_files = glob.glob("*.py")
    
    # Update references in scripts
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file contains references to gemini files
            has_gemini_refs = False
            for gemini_file, _ in moved_files:
                if gemini_file in content:
                    has_gemini_refs = True
                    break
            
            if has_gemini_refs:
                # Create backup
                backup_path = f"{py_file}.bak"
                shutil.copy2(py_file, backup_path)
                
                # Update references
                updated_content = content
                for old_path, new_path in moved_files:
                    # Replace direct references to the file
                    updated_content = updated_content.replace(f'"{old_path}"', f'"{new_path}"')
                    updated_content = updated_content.replace(f"'{old_path}'", f"'{new_path}'")
                
                # Write updated content
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"Updated references in {py_file} (backup saved as {backup_path})")
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    print(f"\nSummary:")
    print(f"- Copied {len(moved_files)} gemini files to {target_folder}")
    print(f"- Original files preserved in root directory")
    print(f"- Updated references in Python scripts")
    print(f"\nNote: You can manually delete the original gemini files after verifying everything works.")

if __name__ == "__main__":
    organize_gemini_files()
