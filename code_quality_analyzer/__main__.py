"""Command-line interface for the code quality analyzer.

This module provides a command-line interface for running the code quality analyzer.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any

from .unified_analyzer import UnifiedAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Code Quality Analyzer')

    parser.add_argument('path', help='File or directory to analyze')

    parser.add_argument('--analyzers', nargs='+',
                        choices=['srp', 'ocp', 'lsp', 'isp', 'dip', 'kiss', 'dry', 'solid', 'all'],
                        default=['all'],
                        help='Analyzers to run (default: all)')

    parser.add_argument('--format', choices=['text', 'json', 'html'],
                        default='text',
                        help='Output format (default: text)')

    parser.add_argument('--output', '-o',
                        help='Output file path (default: stdout)')

    parser.add_argument('--parallel', action='store_true',
                        help='Use parallel processing for directory analysis')

    parser.add_argument('--cache', action='store_true',
                        help='Cache analysis results')

    parser.add_argument('--cache-dir',
                        default='.code_analysis_cache',
                        help='Directory for caching analysis results')

    # SRP analyzer options
    parser.add_argument('--srp-max-responsibilities', type=int, default=1,
                        help='Maximum number of responsibilities per class (default: 1)')

    parser.add_argument('--srp-cohesion-threshold', type=float, default=0.5,
                        help='Minimum cohesion score for a class (default: 0.5)')

    # KISS analyzer options
    parser.add_argument('--kiss-max-method-lines', type=int, default=20,
                        help='Maximum number of lines per method (default: 20)')

    parser.add_argument('--kiss-max-nesting-depth', type=int, default=3,
                        help='Maximum nesting depth (default: 3)')

    parser.add_argument('--kiss-max-cyclomatic-complexity', type=int, default=10,
                        help='Maximum cyclomatic complexity (default: 10)')

    parser.add_argument('--kiss-max-cognitive-complexity', type=int, default=15,
                        help='Maximum cognitive complexity (default: 15)')

    parser.add_argument('--kiss-max-parameters', type=int, default=5,
                        help='Maximum number of parameters per method (default: 5)')

    # DRY analyzer options
    parser.add_argument('--dry-min-duplicate-lines', type=int, default=3,
                        help='Minimum number of lines for a duplicate code block (default: 3)')

    parser.add_argument('--dry-similarity-threshold', type=float, default=0.8,
                        help='Minimum similarity threshold for duplicate code (default: 0.8)')

    parser.add_argument('--dry-min-string-length', type=int, default=10,
                        help='Minimum length for a string literal to be considered (default: 10)')

    parser.add_argument('--dry-min-string-occurrences', type=int, default=3,
                        help='Minimum number of occurrences for a string literal to be considered (default: 3)')

    return parser.parse_args()

def build_config(args) -> Dict[str, Any]:
    """Build configuration dictionary from command-line arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configuration dictionary
    """
    # Determine enabled analyzers
    if 'all' in args.analyzers:
        enabled_analyzers = ['srp', 'ocp', 'lsp', 'isp', 'dip', 'kiss', 'dry']
    elif 'solid' in args.analyzers:
        enabled_analyzers = ['srp', 'ocp', 'lsp', 'isp', 'dip']
    else:
        enabled_analyzers = args.analyzers

    # Build configuration
    config = {
        'enabled_analyzers': enabled_analyzers,
        'use_cache': args.cache,
        'cache_dir': args.cache_dir,

        # SRP analyzer config
        'srp_config': {
            'max_responsibilities': args.srp_max_responsibilities,
            'cohesion_threshold': args.srp_cohesion_threshold,
            'use_cache': args.cache,
            'cache_dir': args.cache_dir
        },

        # KISS analyzer config
        'kiss_config': {
            'max_method_lines': args.kiss_max_method_lines,
            'max_nesting_depth': args.kiss_max_nesting_depth,
            'max_cyclomatic_complexity': args.kiss_max_cyclomatic_complexity,
            'max_cognitive_complexity': args.kiss_max_cognitive_complexity,
            'max_parameters': args.kiss_max_parameters,
            'use_cache': args.cache,
            'cache_dir': args.cache_dir
        },

        # DRY analyzer config
        'dry_config': {
            'min_duplicate_lines': args.dry_min_duplicate_lines,
            'similarity_threshold': args.dry_similarity_threshold,
            'min_string_length': args.dry_min_string_length,
            'min_string_occurrences': args.dry_min_string_occurrences,
            'use_cache': args.cache,
            'cache_dir': args.cache_dir
        }
    }

    return config

def main():
    """Main entry point."""
    # Parse command-line arguments
    args = parse_args()

    # Build configuration
    config = build_config(args)

    # Create analyzer
    analyzer = UnifiedAnalyzer(config)

    # Run analysis
    if os.path.isfile(args.path):
        results = analyzer.analyze_file(args.path)
    elif os.path.isdir(args.path):
        results = analyzer.analyze_directory(args.path, args.parallel)
    else:
        logger.error(f"Path not found: {args.path}")
        sys.exit(1)

    # Generate report
    report = analyzer.generate_report(args.format, args.output)

    # Print report if not writing to file
    if not args.output:
        print(report)

if __name__ == '__main__':
    main()
