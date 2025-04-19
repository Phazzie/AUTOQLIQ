import os
import shutil
import glob
import re

def move_files_to_archive():
    """Move non-essential files to the archive directories."""
    # Ensure archive directories exist
    os.makedirs("archived_files/scripts", exist_ok=True)
    os.makedirs("archived_files/logs", exist_ok=True)
    os.makedirs("archived_files/docs", exist_ok=True)
    os.makedirs("archived_files/temp", exist_ok=True)
    
    # Files to move to scripts directory
    script_patterns = [
        "*package*.py", 
        "*export*.py", 
        "*archive*.py", 
        "*consolidate*.py",
        "*apply*.py",
        "*gemini*.py",
        "*parse*.py",
        "*organize*.py",
        "*convert*.py",
        "analyze_package_size.py"
    ]
    
    # Files to move to logs directory
    log_patterns = ["*.log"]
    
    # Files to move to docs directory (excluding README.md)
    doc_patterns = ["*.md"]
    doc_exclusions = ["README.md"]
    
    # Files to move to temp directory
    temp_patterns = [
        "*_v*.py", 
        "*_refactored*.py",
        "*.txt"
    ]
    temp_exclusions = ["requirements.txt"]
    
    # Move script files
    print("Moving script files...")
    for pattern in script_patterns:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) and not file_path.startswith("archived_files"):
                # Skip the current script
                if file_path == os.path.basename(__file__) or file_path == "create_archive_dirs.py":
                    continue
                    
                dest_path = os.path.join("archived_files/scripts", os.path.basename(file_path))
                print(f"  Moving {file_path} to {dest_path}")
                shutil.copy2(file_path, dest_path)
    
    # Move log files
    print("\nMoving log files...")
    for pattern in log_patterns:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) and not file_path.startswith("archived_files"):
                dest_path = os.path.join("archived_files/logs", os.path.basename(file_path))
                print(f"  Moving {file_path} to {dest_path}")
                shutil.copy2(file_path, dest_path)
    
    # Move doc files
    print("\nMoving doc files...")
    for pattern in doc_patterns:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) and not file_path.startswith("archived_files"):
                # Skip excluded files
                if os.path.basename(file_path) in doc_exclusions:
                    continue
                    
                dest_path = os.path.join("archived_files/docs", os.path.basename(file_path))
                print(f"  Moving {file_path} to {dest_path}")
                shutil.copy2(file_path, dest_path)
    
    # Move temp files
    print("\nMoving temp files...")
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) and not file_path.startswith("archived_files"):
                # Skip excluded files
                if os.path.basename(file_path) in temp_exclusions:
                    continue
                    
                dest_path = os.path.join("archived_files/temp", os.path.basename(file_path))
                print(f"  Moving {file_path} to {dest_path}")
                shutil.copy2(file_path, dest_path)
    
    print("\nFiles have been copied to the archive directories.")
    print("The original files have NOT been deleted.")
    print("Review the archived files and delete the originals manually if desired.")

if __name__ == "__main__":
    move_files_to_archive()
