"""Run the Code Quality Analyzer on the sample code."""

import os
import sys
from code_quality_analyzer import UnifiedAnalyzer

def main():
    """Main entry point."""
    # Get the path to the sample code
    sample_code_path = os.path.join(os.path.dirname(__file__), 'sample_code.py')
    
    # Create analyzer with default configuration
    analyzer = UnifiedAnalyzer()
    
    # Run analysis
    print(f"Analyzing file: {sample_code_path}")
    results = analyzer.analyze_file(sample_code_path)
    
    # Generate HTML report
    report_path = os.path.join(os.path.dirname(__file__), 'sample_code_report.html')
    analyzer.generate_report(format='html', output_path=report_path)
    
    print(f"Report written to: {report_path}")
    
    # Print summary
    print("\nSummary:")
    print(f"SRP Score: {results['analyzers']['SRP Analyzer']['overall_srp_score']:.2f}/1.00")
    print(f"KISS Score: {results['analyzers']['KISS Analyzer']['overall_kiss_score']:.2f}/1.00")
    print(f"DRY Score: {results['analyzers']['DRY Analyzer']['overall_dry_score']:.2f}/1.00")
    print(f"Overall Quality Score: {results['overall_quality_score']:.2f}/1.00")

if __name__ == '__main__':
    main()
