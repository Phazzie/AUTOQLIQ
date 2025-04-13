#!/usr/bin/env python
"""
Update the gemini_missing_files.json file to remove entries for files that were extracted from GEMINI18.TXT.
"""

import json
import os

# Files that were extracted from GEMINI18.TXT
extracted_files = [
    "README.md",
    "src/core/interfaces/action.py",
    "src/core/interfaces/repository.py",
    "src/core/interfaces/webdriver.py",
    "src/core/interfaces/service.py",
    "src/core/actions/__init__.py",
    "src/core/actions/conditional_action.py",
    "src/core/actions/loop_action.py",
    "src/core/actions/template_action.py",
    "src/application/services/reporting_service.py",
    "src/application/services/scheduler_service.py",
    "src/application/services/workflow_service.py",
    "tests/unit/core/__init__.py",
    "tests/integration/test_webdriver_integration.py"
]

# Normalize paths (replace backslashes with forward slashes)
extracted_files = [path.replace("\\", "/") for path in extracted_files]

# Load the current missing files
json_path = "gemini_missing_files.json"
with open(json_path, 'r', encoding='utf-8') as f:
    missing_files = json.load(f)

# Remove entries for files that were extracted
removed_files = []
for file_path in extracted_files:
    if file_path in missing_files:
        del missing_files[file_path]
        removed_files.append(file_path)

# Write updated missing files list
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(missing_files, f, indent=2)

print(f"Updated {json_path}")
print(f"Removed {len(removed_files)} files from the missing files list:")
for file_path in removed_files:
    print(f"  - {file_path}")
