#!/usr/bin/env python
"""
Script Fixer

This script fixes common issues in the code quality analyzer scripts.
It addresses missing imports, attribute errors, and other issues.

Usage:
    python fix_analyzer_scripts.py
"""

import os
import re
import shutil
import datetime

# List of fixes to apply
FIXES = [
    {
        "file": "analyze_dry.py",
        "issue": "Missing 'keyword' import",
        "find": "import re\nimport hashlib\nimport logging",
        "replace": "import re\nimport hashlib\nimport logging\nimport keyword"
    },
    {
        "file": "count_responsibilities.py",
        "issue": "parent_field attribute error",
        "find": "if isinstance(node, ast.FunctionDef) and node.parent_field == tree:",
        "replace": "if isinstance(node, ast.FunctionDef) and not any(\n                isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) \n                if hasattr(parent, 'body') and node in parent.body\n            ):"
    },
    {
        "file": "count_responsibilities.py",
        "issue": "parent_field attribute error (second occurrence)",
        "find": "if isinstance(node, ast.FunctionDef) and node.parent_field == cls_node:",
        "replace": "if isinstance(node, ast.FunctionDef) and not any(\n                    isinstance(parent, ast.ClassDef) for parent in ast.walk(cls_node) \n                    if hasattr(parent, 'body') and node in parent.body and parent != cls_node\n                ):"
    },
    {
        "file": "code_quality_analyzer/setup.py",
        "issue": "Missing networkx dependency",
        "find": "install_requires=[],",
        "replace": "install_requires=[\n        'networkx',\n    ],"
    }
]

def fix_scripts():
    """Apply fixes to the scripts."""
    print("Fixing code quality analyzer scripts...")
    
    # Create backup directory
    backup_dir = f"script_backups_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")
    
    fixes_applied = 0
    
    for fix in FIXES:
        file_path = fix["file"]
        
        if os.path.exists(file_path):
            # Create backup
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"Created backup of {file_path} at {backup_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fix
            if fix["find"] in content:
                new_content = content.replace(fix["find"], fix["replace"])
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Fixed: {file_path} - {fix['issue']}")
                fixes_applied += 1
            else:
                print(f"⚠️ Could not find pattern in {file_path} for issue: {fix['issue']}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\nFix completed. Applied {fixes_applied} fixes out of {len(FIXES)} total.")
    print(f"Backups were created in {backup_dir}")

if __name__ == "__main__":
    fix_scripts()
