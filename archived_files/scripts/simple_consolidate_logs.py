#!/usr/bin/env python3
"""
Simplified script to consolidate application logs and packaging logs.
"""

import os
import glob
import datetime

def simple_consolidate_logs(output_file="consolidated_logs.txt"):
    """
    Find all log files and concatenate them into a single file with headers.

    Args:
        output_file: Path to the output consolidated log file
    """
    # Find all log files
    log_files = []
    for ext in ['.log', '.txt']:
        log_files.extend(glob.glob(f'*.{ext}'))
        log_files.extend(glob.glob(f'logs/*.{ext}'))
        log_files.extend(glob.glob(f'*/*{ext}'))
        log_files.extend(glob.glob(f'*/*/*{ext}'))

    # Filter to likely log files
    log_files = [f for f in log_files if any(keyword in f.lower() for keyword in
                ['log', 'error', 'debug', 'info', 'warn', 'gemini', 'apply', 'package'])]

    print(f"Found {len(log_files)} potential log files")

    # Sort log files by name
    log_files.sort()

    # Write consolidated log
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(f"# Consolidated Logs\n")
        out_file.write(f"# Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out_file.write(f"# Total files: {len(log_files)}\n\n")

        for log_file in log_files:
            try:
                # Add a header for each file
                out_file.write(f"\n\n{'='*80}\n")
                out_file.write(f"FILE: {log_file}\n")
                out_file.write(f"{'='*80}\n\n")

                # Read and append the file content
                with open(log_file, 'r', encoding='utf-8') as in_file:
                    content = in_file.read()
                    out_file.write(content)

                print(f"Added {log_file} to consolidated log")
            except Exception as e:
                print(f"Error processing {log_file}: {e}")

    print(f"Consolidated {len(log_files)} log files into {output_file}")

if __name__ == "__main__":
    simple_consolidate_logs()
