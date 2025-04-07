"""Unified code quality analyzer.

This module provides a unified interface for running multiple code quality analyzers.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set

from .base_analyzer import BaseAnalyzer

# SOLID Principle Analyzers
from .analyzers.srp_analyzer import SRPAnalyzer     # Single Responsibility Principle
from .analyzers.ocp_analyzer import OCPAnalyzer     # Open/Closed Principle
from .analyzers.lsp_analyzer import LSPAnalyzer     # Liskov Substitution Principle
from .analyzers.isp_analyzer import ISPAnalyzer     # Interface Segregation Principle
from .analyzers.dip_analyzer import DIPAnalyzer     # Dependency Inversion Principle

# Other Code Quality Analyzers
from .analyzers.kiss_analyzer import KISSAnalyzer    # Keep It Simple, Stupid
from .analyzers.dry_analyzer import DRYAnalyzer      # Don't Repeat Yourself

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class UnifiedAnalyzer:
    """Unified interface for running multiple code quality analyzers.

    This class provides a single interface for running multiple analyzers
    and generating combined reports.

    Attributes:
        analyzers: List of analyzers to run
        results: Combined analysis results
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new UnifiedAnalyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.analyzers = []
        self.results = {}

        # Initialize analyzers
        self._initialize_analyzers()

    def _initialize_analyzers(self) -> None:
        """Initialize the analyzers to use."""
        # Get enabled analyzers from config
        enabled_analyzers = self.config.get('enabled_analyzers',
                                          ['srp', 'ocp', 'lsp', 'isp', 'dip', 'kiss', 'dry'])

        # Initialize SOLID principle analyzers
        if 'srp' in enabled_analyzers:  # Single Responsibility Principle
            self.analyzers.append(SRPAnalyzer(self.config.get('srp_config')))

        if 'ocp' in enabled_analyzers:  # Open/Closed Principle
            self.analyzers.append(OCPAnalyzer(self.config.get('ocp_config')))

        if 'lsp' in enabled_analyzers:  # Liskov Substitution Principle
            self.analyzers.append(LSPAnalyzer(self.config.get('lsp_config')))

        if 'isp' in enabled_analyzers:  # Interface Segregation Principle
            self.analyzers.append(ISPAnalyzer(self.config.get('isp_config')))

        if 'dip' in enabled_analyzers:  # Dependency Inversion Principle
            self.analyzers.append(DIPAnalyzer(self.config.get('dip_config')))

        # Initialize other code quality analyzers
        if 'kiss' in enabled_analyzers:  # Keep It Simple, Stupid
            self.analyzers.append(KISSAnalyzer(self.config.get('kiss_config')))

        if 'dry' in enabled_analyzers:  # Don't Repeat Yourself
            self.analyzers.append(DRYAnalyzer(self.config.get('dry_config')))

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file with all analyzers.

        Args:
            file_path: Path to the file to analyze

        Returns:
            A dictionary containing combined analysis results
        """
        results = {
            "file_path": file_path,
            "analyzers": {}
        }

        # Run each analyzer
        for analyzer in self.analyzers:
            analyzer_result = analyzer.analyze_file(file_path)
            results["analyzers"][analyzer.name] = analyzer_result

        # Calculate overall quality score
        self._calculate_overall_score(results)

        # Store results
        self.results = results

        return results

    def analyze_directory(self, directory_path: str, parallel: bool = False) -> Dict[str, Any]:
        """Analyze all Python files in a directory with all analyzers.

        Args:
            directory_path: Path to the directory to analyze
            parallel: Whether to use parallel processing

        Returns:
            A dictionary containing combined analysis results
        """
        results = {
            "directory_path": directory_path,
            "analyzers": {}
        }

        # Run each analyzer
        for analyzer in self.analyzers:
            analyzer_result = analyzer.analyze_directory(directory_path, parallel)
            results["analyzers"][analyzer.name] = analyzer_result

        # Calculate overall quality score
        self._calculate_overall_score(results)

        # Store results
        self.results = results

        return results

    def _calculate_overall_score(self, results: Dict[str, Any]) -> None:
        """Calculate an overall code quality score.

        Args:
            results: Analysis results
        """
        # Get scores from each analyzer
        scores = []

        for analyzer_name, analyzer_result in results.get("analyzers", {}).items():
            # SOLID Principle Analyzers
            if "overall_srp_score" in analyzer_result:  # Single Responsibility Principle
                scores.append(analyzer_result["overall_srp_score"])
            elif "overall_ocp_score" in analyzer_result:  # Open/Closed Principle
                scores.append(analyzer_result["overall_ocp_score"])
            elif "overall_lsp_score" in analyzer_result:  # Liskov Substitution Principle
                scores.append(analyzer_result["overall_lsp_score"])
            elif "overall_isp_score" in analyzer_result:  # Interface Segregation Principle
                scores.append(analyzer_result["overall_isp_score"])
            elif "overall_dip_score" in analyzer_result:  # Dependency Inversion Principle
                scores.append(analyzer_result["overall_dip_score"])
            # Other Code Quality Analyzers
            elif "overall_kiss_score" in analyzer_result:  # Keep It Simple, Stupid
                scores.append(analyzer_result["overall_kiss_score"])
            elif "overall_dry_score" in analyzer_result:  # Don't Repeat Yourself
                scores.append(analyzer_result["overall_dry_score"])
            elif "summary" in analyzer_result:
                # Try to get score from summary
                summary = analyzer_result["summary"]
                if "srp_compliance_rate" in summary:
                    scores.append(summary["srp_compliance_rate"])
                elif "kiss_compliance_rate" in summary:
                    scores.append(summary["kiss_compliance_rate"])
                elif "dry_compliance_rate" in summary:
                    scores.append(summary["dry_compliance_rate"])

        # Calculate average score
        if scores:
            results["overall_quality_score"] = sum(scores) / len(scores)
        else:
            results["overall_quality_score"] = 0.0

    def generate_report(self, format: str = 'text', output_path: Optional[str] = None) -> str:
        """Generate a combined report of analysis results.

        Args:
            format: The format of the report ('text', 'json', or 'html')
            output_path: Optional path to write the report to

        Returns:
            The report as a string
        """
        if not self.results:
            return "No analysis results available"

        if format == 'json':
            report = json.dumps(self.results, indent=2)
        elif format == 'html':
            report = self._generate_html_report()
        else:
            report = self._generate_text_report()

        # Write report to file if output path is provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                logger.info(f"Report written to {output_path}")
            except Exception as e:
                logger.error(f"Error writing report to {output_path}: {str(e)}")

        return report

    def _generate_text_report(self) -> str:
        """Generate a text report of analysis results.

        Returns:
            The report as a string
        """
        report = ["===== CODE QUALITY ANALYSIS REPORT ====="]

        # Add overall score
        overall_score = self.results.get("overall_quality_score", 0.0)
        report.append(f"Overall Quality Score: {overall_score:.2f}/1.00")
        report.append("")

        # Add analyzer reports
        for analyzer in self.analyzers:
            try:
                if hasattr(analyzer, '_generate_text_report'):
                    report.append(analyzer._generate_text_report())
                elif hasattr(analyzer, 'print_results'):
                    # Capture the output of print_results
                    import io
                    import sys
                    old_stdout = sys.stdout
                    new_stdout = io.StringIO()
                    sys.stdout = new_stdout
                    analyzer.print_results(analyzer.results)
                    sys.stdout = old_stdout
                    report.append(new_stdout.getvalue())
                else:
                    report.append(f"No report available for {analyzer.name}")
                report.append("")
            except Exception as e:
                report.append(f"Error generating report for {analyzer.name}: {str(e)}")
                report.append("")

        return "\n".join(report)

    def _generate_html_report(self) -> str:
        """Generate an HTML report of analysis results.

        Returns:
            The report as an HTML string
        """
        # Basic HTML report
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Code Quality Analysis Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1 { color: #333; }",
            "h2 { color: #666; }",
            ".summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }",
            ".file { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }",
            ".file-header { display: flex; justify-content: space-between; }",
            ".file-path { font-weight: bold; }",
            ".file-score { font-weight: bold; }",
            ".good { color: green; }",
            ".warning { color: orange; }",
            ".bad { color: red; }",
            ".violation { margin-left: 20px; margin-bottom: 10px; }",
            ".recommendation { font-style: italic; color: #666; margin-top: 5px; }",
            ".metrics { margin-top: 10px; }",
            ".code-preview { background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 10px; }",
            ".code-preview pre { margin: 0; white-space: pre-wrap; }",
            ".string-preview, .constant-preview { background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 10px; }",
            ".analyzer { margin-bottom: 30px; border: 1px solid #eee; padding: 10px; border-radius: 5px; }",
            ".analyzer h2 { margin-top: 0; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Code Quality Analysis Report</h1>",
            "<div class='summary'>",
            "<h2>Summary</h2>"
        ]

        # Add overall score with color coding
        overall_score = self.results.get("overall_quality_score", 0.0)
        color_class = "good" if overall_score >= 0.8 else "warning" if overall_score >= 0.6 else "bad"
        html.append(f"<p>Overall Quality Score: <span class='{color_class}'>{overall_score:.2f}/1.00</span></p>")

        html.append("</div>")

        # Add analyzer reports
        for analyzer in self.analyzers:
            html.append("<div class='analyzer'>")
            html.append(analyzer._generate_html_report())
            html.append("</div>")

        html.extend([
            "</body>",
            "</html>"
        ])

        return "\n".join(html)
