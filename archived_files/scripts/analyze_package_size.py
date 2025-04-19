#!/usr/bin/env python
"""
Script to analyze the size of the packaged codebase file.

This script will:
1. Parse the packaged codebase file
2. Extract information about each file (size, line count, etc.)
3. Provide statistics about what's contributing to the overall size
4. Identify the largest files and directories
"""

import os
import re
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple, NamedTuple
import matplotlib.pyplot as plt
import numpy as np

class FileInfo(NamedTuple):
    """Information about a file in the packaged codebase."""
    path: str
    size_bytes: int
    line_count: int
    marker_overhead: int  # Size of the START/END markers


def parse_packaged_codebase(file_path: str) -> List[FileInfo]:
    """
    Parse the packaged codebase file and extract information about each file.
    
    Args:
        file_path: Path to the packaged codebase file
        
    Returns:
        List of FileInfo objects
    """
    print(f"Analyzing packaged codebase file: {file_path}")
    
    # Define the pattern to match START/END markers and file content
    start_pattern = re.compile(
        r'#{80}\s+' +                            # Start of marker (80 #)
        r'#{10}\s+START\s+FILE:\s+\[(.*?)\]\s+#{10}\s+' +  # File path in START marker
        r'#{80}\s+'                              # End of START marker
    )
    
    end_pattern = re.compile(
        r'#{80}\s+' +                            # Start of END marker
        r'#{10}\s+END\s+FILE:\s+\[(.*?)\]\s+#{10}\s+' +    # File path in END marker
        r'#{80}'                                 # End of END marker
    )
    
    file_infos = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find all START markers
            start_matches = list(start_pattern.finditer(content))
            
            # Find all END markers
            end_matches = list(end_pattern.finditer(content))
            
            if len(start_matches) != len(end_matches):
                print(f"Warning: Mismatch between START ({len(start_matches)}) and END ({len(end_matches)}) markers")
            
            # Process each file
            for i, start_match in enumerate(start_matches):
                if i >= len(end_matches):
                    break
                    
                file_path = start_match.group(1).strip()
                start_pos = start_match.end()
                end_pos = end_matches[i].start()
                
                # Extract file content
                file_content = content[start_pos:end_pos]
                
                # Calculate metrics
                size_bytes = len(file_content.encode('utf-8'))
                line_count = file_content.count('\n') + 1
                
                # Calculate marker overhead
                marker_text = start_match.group(0) + end_matches[i].group(0)
                marker_overhead = len(marker_text.encode('utf-8'))
                
                file_infos.append(FileInfo(
                    path=file_path,
                    size_bytes=size_bytes,
                    line_count=line_count,
                    marker_overhead=marker_overhead
                ))
    
    except Exception as e:
        print(f"Error parsing file: {e}")
        return []
    
    return file_infos


def analyze_by_directory(file_infos: List[FileInfo]) -> Dict[str, int]:
    """
    Analyze file sizes grouped by directory.
    
    Args:
        file_infos: List of FileInfo objects
        
    Returns:
        Dictionary mapping directory paths to total size in bytes
    """
    dir_sizes = defaultdict(int)
    
    for file_info in file_infos:
        # Get directory path
        dir_path = os.path.dirname(file_info.path)
        if not dir_path:
            dir_path = '(root)'
            
        # Add file size to directory total
        dir_sizes[dir_path] += file_info.size_bytes
    
    return dict(sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True))


def analyze_by_extension(file_infos: List[FileInfo]) -> Dict[str, int]:
    """
    Analyze file sizes grouped by file extension.
    
    Args:
        file_infos: List of FileInfo objects
        
    Returns:
        Dictionary mapping file extensions to total size in bytes
    """
    ext_sizes = defaultdict(int)
    
    for file_info in file_infos:
        # Get file extension
        _, ext = os.path.splitext(file_info.path)
        if not ext:
            ext = '(no extension)'
        
        # Add file size to extension total
        ext_sizes[ext] += file_info.size_bytes
    
    return dict(sorted(ext_sizes.items(), key=lambda x: x[1], reverse=True))


def print_largest_files(file_infos: List[FileInfo], limit: int = 20) -> None:
    """
    Print information about the largest files.
    
    Args:
        file_infos: List of FileInfo objects
        limit: Maximum number of files to print
    """
    # Sort files by size (largest first)
    sorted_files = sorted(file_infos, key=lambda x: x.size_bytes, reverse=True)
    
    print(f"\nTop {limit} largest files:")
    print(f"{'Size (KB)':<10} {'Lines':<8} {'Path':<60}")
    print("-" * 80)
    
    for i, file_info in enumerate(sorted_files[:limit]):
        size_kb = file_info.size_bytes / 1024
        print(f"{size_kb:<10.2f} {file_info.line_count:<8} {file_info.path:<60}")


def print_directory_sizes(dir_sizes: Dict[str, int], limit: int = 10) -> None:
    """
    Print information about directory sizes.
    
    Args:
        dir_sizes: Dictionary mapping directory paths to total size in bytes
        limit: Maximum number of directories to print
    """
    print(f"\nTop {limit} largest directories:")
    print(f"{'Size (KB)':<10} {'Directory':<60}")
    print("-" * 80)
    
    for i, (dir_path, size) in enumerate(list(dir_sizes.items())[:limit]):
        size_kb = size / 1024
        print(f"{size_kb:<10.2f} {dir_path:<60}")


def print_extension_sizes(ext_sizes: Dict[str, int]) -> None:
    """
    Print information about file sizes by extension.
    
    Args:
        ext_sizes: Dictionary mapping file extensions to total size in bytes
    """
    print("\nFile sizes by extension:")
    print(f"{'Size (KB)':<10} {'Extension':<15}")
    print("-" * 30)
    
    for ext, size in ext_sizes.items():
        size_kb = size / 1024
        print(f"{size_kb:<10.2f} {ext:<15}")


def print_summary_statistics(file_infos: List[FileInfo], total_size: int) -> None:
    """
    Print summary statistics about the packaged codebase.
    
    Args:
        file_infos: List of FileInfo objects
        total_size: Total size of the packaged codebase file in bytes
    """
    # Calculate total content size and marker overhead
    total_content_size = sum(f.size_bytes for f in file_infos)
    total_marker_overhead = sum(f.marker_overhead for f in file_infos)
    total_line_count = sum(f.line_count for f in file_infos)
    
    # Calculate header/footer overhead
    other_overhead = total_size - total_content_size - total_marker_overhead
    
    print("\nSummary Statistics:")
    print(f"Total packaged file size: {total_size / 1024:.2f} KB ({total_size:,} bytes)")
    print(f"Total number of files: {len(file_infos)}")
    print(f"Total line count: {total_line_count:,}")
    print(f"Average file size: {total_content_size / len(file_infos) / 1024:.2f} KB")
    print(f"Average line count: {total_line_count / len(file_infos):.1f}")
    
    print("\nSize Breakdown:")
    print(f"File content: {total_content_size / 1024:.2f} KB ({total_content_size / total_size * 100:.1f}%)")
    print(f"Marker overhead: {total_marker_overhead / 1024:.2f} KB ({total_marker_overhead / total_size * 100:.1f}%)")
    print(f"Other overhead: {other_overhead / 1024:.2f} KB ({other_overhead / total_size * 100:.1f}%)")


def create_size_charts(file_infos: List[FileInfo], dir_sizes: Dict[str, int], ext_sizes: Dict[str, int], output_dir: str) -> None:
    """
    Create charts visualizing the size distribution.
    
    Args:
        file_infos: List of FileInfo objects
        dir_sizes: Dictionary mapping directory paths to total size in bytes
        ext_sizes: Dictionary mapping file extensions to total size in bytes
        output_dir: Directory to save the charts
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Pie chart of top directories
        plt.figure(figsize=(10, 8))
        
        # Get top 5 directories and group the rest as "Other"
        top_dirs = list(dir_sizes.items())[:5]
        other_size = sum(size for _, size in list(dir_sizes.items())[5:])
        
        labels = [os.path.basename(d) or d for d, _ in top_dirs]
        if other_size > 0:
            labels.append('Other')
            
        sizes = [s for _, s in top_dirs]
        if other_size > 0:
            sizes.append(other_size)
            
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Size Distribution by Directory')
        plt.savefig(os.path.join(output_dir, 'directory_sizes.png'))
        plt.close()
        
        # 2. Bar chart of file extensions
        plt.figure(figsize=(12, 6))
        
        exts = list(ext_sizes.keys())[:10]  # Top 10 extensions
        ext_values = [ext_sizes[ext] / 1024 for ext in exts]  # Convert to KB
        
        plt.bar(exts, ext_values)
        plt.xlabel('File Extension')
        plt.ylabel('Size (KB)')
        plt.title('Size by File Extension')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'extension_sizes.png'))
        plt.close()
        
        # 3. Histogram of file sizes
        plt.figure(figsize=(10, 6))
        
        file_sizes_kb = [f.size_bytes / 1024 for f in file_infos]
        
        plt.hist(file_sizes_kb, bins=20)
        plt.xlabel('File Size (KB)')
        plt.ylabel('Number of Files')
        plt.title('Distribution of File Sizes')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(output_dir, 'file_size_histogram.png'))
        plt.close()
        
        print(f"\nCharts saved to {output_dir}")
        
    except Exception as e:
        print(f"Error creating charts: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Analyze the size of a packaged codebase file.'
    )
    parser.add_argument(
        'file_path',
        help='Path to the packaged codebase file'
    )
    parser.add_argument(
        '--charts',
        action='store_true',
        help='Generate charts visualizing the size distribution'
    )
    parser.add_argument(
        '--charts-dir',
        default='size_analysis_charts',
        help='Directory to save the charts (default: size_analysis_charts)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=20,
        help='Number of top files to display (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Get total file size
    total_size = os.path.getsize(args.file_path)
    
    # Parse the packaged codebase
    file_infos = parse_packaged_codebase(args.file_path)
    
    if not file_infos:
        print("No files found in the packaged codebase.")
        return
    
    # Analyze by directory
    dir_sizes = analyze_by_directory(file_infos)
    
    # Analyze by extension
    ext_sizes = analyze_by_extension(file_infos)
    
    # Print largest files
    print_largest_files(file_infos, args.top)
    
    # Print directory sizes
    print_directory_sizes(dir_sizes)
    
    # Print extension sizes
    print_extension_sizes(ext_sizes)
    
    # Print summary statistics
    print_summary_statistics(file_infos, total_size)
    
    # Create charts if requested
    if args.charts:
        try:
            create_size_charts(file_infos, dir_sizes, ext_sizes, args.charts_dir)
        except ImportError:
            print("\nCould not create charts. Make sure matplotlib is installed:")
            print("pip install matplotlib")


if __name__ == "__main__":
    main()
