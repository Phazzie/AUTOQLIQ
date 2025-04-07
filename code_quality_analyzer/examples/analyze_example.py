"""Example script for using the Code Quality Analyzer.

This script demonstrates how to use the Code Quality Analyzer to analyze a file or directory.
"""

import os
import sys
import argparse
from code_quality_analyzer import UnifiedAnalyzer

def main():
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Code Quality Analyzer Example')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file path')
    args = parser.parse_args()
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path not found: {args.path}")
        sys.exit(1)
    
    # Create analyzer with default configuration
    analyzer = UnifiedAnalyzer()
    
    # Run analysis
    if os.path.isfile(args.path):
        print(f"Analyzing file: {args.path}")
        results = analyzer.analyze_file(args.path)
    else:
        print(f"Analyzing directory: {args.path}")
        results = analyzer.analyze_directory(args.path)
    
    # Generate report
    report = analyzer.generate_report(format=args.format, output_path=args.output)
    
    # Print report if not writing to file
    if not args.output:
        print(report)
    else:
        print(f"Report written to: {args.output}")

if __name__ == '__main__':
    main()
