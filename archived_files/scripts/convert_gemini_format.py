#!/usr/bin/env python
"""
Convert Gemini format to the format expected by apply_packaged_codebase_enhanced.py.

This script converts a file in the format:
```
FILE LIST
path/to/file1.ext
path/to/file2.ext
...

FILE CONTENTS
FILE: path/to/file1.ext
(file content)

FILE: path/to/file2.ext
(file content)
...
```

To the format expected by apply_packaged_codebase_enhanced.py:
```
################################################################################
########## START FILE: [path/to/file1.ext] ##########
################################################################################
(file content)
################################################################################
########## END FILE: [path/to/file1.ext] ##########
################################################################################

################################################################################
########## START FILE: [path/to/file2.ext] ##########
################################################################################
(file content)
################################################################################
########## END FILE: [path/to/file2.ext] ##########
################################################################################
...
```
"""

import os
import sys
import re
import argparse

def convert_file(input_file, output_file):
    """
    Convert a file from Gemini format to the format expected by apply_packaged_codebase_enhanced.py.

    Args:
        input_file: Path to the input file in Gemini format
        output_file: Path to the output file to write
    """
    print(f"Converting {input_file} to {output_file}...")

    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the file list
    file_list_match = re.search(r'FILE LIST\s+(.*?)(?=\s+FILE CONTENTS)', content, re.DOTALL)
    if not file_list_match:
        print("Error: Could not find FILE LIST section")
        return False

    file_list = file_list_match.group(1).strip().split('\n')
    print(f"Found {len(file_list)} files in the file list")

    # Extract the file contents
    file_contents = {}

    # Find the FILE CONTENTS section
    file_contents_start = content.find("FILE CONTENTS")
    if file_contents_start == -1:
        print("Error: Could not find FILE CONTENTS section")
        return False

    # Split the content by "FILE:" markers
    file_sections = content[file_contents_start:].split("FILE: ")[1:]

    for section in file_sections:
        # The first line is the file path
        lines = section.split('\n', 1)
        if len(lines) < 2:
            continue

        file_path = lines[0].strip()
        file_content = lines[1].strip()

        # If there's another FILE: marker, trim the content
        next_file_marker = file_content.find("\nFILE: ")
        if next_file_marker != -1:
            file_content = file_content[:next_file_marker].strip()

        file_contents[file_path] = file_content

    print(f"Found {len(file_contents)} file contents")

    # Check if all files in the file list have content
    missing_files = []
    for file_path in file_list:
        if file_path not in file_contents:
            missing_files.append(file_path)

    if missing_files:
        print(f"Warning: {len(missing_files)} files in the file list have no content:")
        for file_path in missing_files[:10]:
            print(f"  {file_path}")
        if len(missing_files) > 10:
            print(f"  ... and {len(missing_files) - 10} more")

    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the analysis section if it exists
        analysis_match = re.search(r'```text\s+FILE LIST.*?```(.*?)FILE CONTENTS', content, re.DOTALL)
        if analysis_match:
            analysis = analysis_match.group(1).strip()
            f.write(f"{analysis}\n\n")

        # Write the file contents in the expected format
        for file_path in file_list:
            if file_path in file_contents:
                # Write the exact format expected by apply_packaged_codebase_enhanced.py
                f.write("################################################################################\n")
                f.write(f"########## START FILE: [{file_path}] ##########\n")
                f.write("################################################################################\n")
                f.write(file_contents[file_path])
                # Ensure there's a newline at the end of the file content
                if not file_contents[file_path].endswith('\n'):
                    f.write("\n")
                f.write("################################################################################\n")
                f.write(f"########## END FILE: [{file_path}] ##########\n")
                f.write("################################################################################\n\n")

    print(f"Conversion complete. Output written to {output_file}")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Convert Gemini format to the format expected by apply_packaged_codebase_enhanced.py.'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input file in Gemini format'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Path to the output file (default: input_file_converted.txt)'
    )

    args = parser.parse_args()

    # Set default output file if not specified
    if args.output is None:
        base_name, ext = os.path.splitext(args.input_file)
        args.output = f"{base_name}_converted{ext}"

    # Convert the file
    success = convert_file(args.input_file, args.output)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
