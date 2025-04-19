#!/usr/bin/env python3
"""
Script to consolidate application logs and packaging logs into one sorted file.
"""

import os
import re
import glob
import datetime
from collections import defaultdict

def consolidate_logs(output_file="consolidated_logs.txt"):
    """
    Find all log files, extract entries, sort by timestamp, and write to a single file.
    
    Args:
        output_file: Path to the output consolidated log file
    """
    # Patterns to match timestamps in different log formats
    timestamp_patterns = [
        # Standard ISO format: 2023-04-06 21:32:34,817
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})',
        # Alternative format: [2023/04/06 21:32:34]
        r'\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\]',
        # Another format: 06-Apr-2023 21:32:34
        r'(\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2})'
    ]
    
    # Find all log files
    log_files = []
    for ext in ['.log', '.txt']:
        log_files.extend(glob.glob(f'*.{ext}'))
        log_files.extend(glob.glob(f'logs/*.{ext}'))
        log_files.extend(glob.glob(f'*/*{ext}'))  # Look in subdirectories
    
    # Filter to likely log files
    log_files = [f for f in log_files if any(keyword in f.lower() for keyword in 
                ['log', 'error', 'debug', 'info', 'warn', 'gemini', 'apply', 'package'])]
    
    print(f"Found {len(log_files)} potential log files")
    
    # Extract log entries with timestamps
    entries = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Process the file line by line
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    timestamp = None
                    
                    # Try each timestamp pattern
                    for pattern in timestamp_patterns:
                        match = re.search(pattern, line)
                        if match:
                            timestamp_str = match.group(1)
                            try:
                                # Try to parse the timestamp
                                if ',' in timestamp_str:  # ISO format with milliseconds
                                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                                elif '/' in timestamp_str:  # [YYYY/MM/DD HH:MM:SS]
                                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                                else:  # DD-Mon-YYYY HH:MM:SS
                                    timestamp = datetime.datetime.strptime(timestamp_str, '%d-%b-%Y %H:%M:%S')
                                break
                            except ValueError:
                                continue
                    
                    if timestamp:
                        # Include the source file in the entry
                        entries.append((timestamp, f"[{log_file}] {line}"))
                    else:
                        # For lines without timestamps, attach to the previous entry if possible
                        if entries:
                            entries[-1] = (entries[-1][0], entries[-1][1] + "\n" + line)
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
    
    # Sort entries by timestamp
    entries.sort(key=lambda x: x[0])
    
    # Write consolidated log
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Consolidated Logs\n")
        f.write(f"# Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total entries: {len(entries)}\n\n")
        
        for timestamp, entry in entries:
            f.write(f"{entry}\n")
    
    print(f"Consolidated {len(entries)} log entries into {output_file}")

if __name__ == "__main__":
    consolidate_logs()
