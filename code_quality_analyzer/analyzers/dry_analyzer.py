"""DRY (Don't Repeat Yourself) Principle Analyzer.

This module provides an analyzer for detecting violations of the DRY principle.
It identifies code duplication and repeated patterns.
"""

import os
import ast
import re
import hashlib
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

from ..base_analyzer import BaseAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DRYAnalyzer(BaseAnalyzer):
    """Analyzes Python code for DRY principle violations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new DRYAnalyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        default_config = {
            'min_duplicate_lines': 3,
            'similarity_threshold': 0.8,
            'min_string_length': 10,
            'min_string_occurrences': 3
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(
            name="DRY Analyzer",
            description="Analyzes code for violations of the Don't Repeat Yourself principle",
            config=default_config
        )
        
        self.min_duplicate_lines = self.config['min_duplicate_lines']
        self.similarity_threshold = self.config['similarity_threshold']
        self.min_string_length = self.config['min_string_length']
        self.min_string_occurrences = self.config['min_string_occurrences']
        
        # Storage for cross-file analysis
        self.code_blocks = defaultdict(list)  # Maps code block hashes to their locations
        self.string_literals = defaultdict(list)  # Maps string literals to their locations
        self.numeric_constants = defaultdict(list)  # Maps numeric constants to their locations
    
    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a file for DRY violations.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            tree: AST of the file
            
        Returns:
            A dictionary containing analysis results
        """
        results = {
            "file_path": file_path,
            "duplicate_code_blocks": [],
            "repeated_strings": [],
            "repeated_constants": [],
            "overall_dry_score": 1.0  # Will be updated based on violations
        }
        
        # Find duplicate code blocks
        duplicate_blocks = self._find_duplicate_code_blocks(content, file_path)
        if duplicate_blocks:
            results["duplicate_code_blocks"] = duplicate_blocks
        
        # Find repeated string literals
        repeated_strings = self._find_repeated_strings(tree, file_path)
        if repeated_strings:
            results["repeated_strings"] = repeated_strings
        
        # Find repeated numeric constants
        repeated_constants = self._find_repeated_constants(tree, file_path)
        if repeated_constants:
            results["repeated_constants"] = repeated_constants
        
        # Calculate overall DRY score
        violation_count = (
            len(duplicate_blocks) + 
            len(repeated_strings) + 
            len(repeated_constants)
        )
        
        # Each violation reduces score by 0.1, with a minimum of 0.0
        results["overall_dry_score"] = max(0.0, 1.0 - (violation_count * 0.1))
        
        return results
    
    def _find_duplicate_code_blocks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Find duplicate code blocks in a file.
        
        Args:
            content: Content of the file
            file_path: Path to the file
            
        Returns:
            A list of duplicate code blocks
        """
        lines = content.splitlines()
        line_count = len(lines)
        duplicates = []
        
        # Generate hashes for all possible code blocks of minimum size
        for i in range(line_count - self.min_duplicate_lines + 1):
            for j in range(i + self.min_duplicate_lines, min(i + 30, line_count) + 1):  # Limit block size to 30 lines
                block = "\n".join(lines[i:j])
                # Normalize whitespace and comments
                normalized_block = self._normalize_code_block(block)
                if not normalized_block.strip():
                    continue
                    
                block_hash = hashlib.md5(normalized_block.encode()).hexdigest()
                
                # Store block info
                self.code_blocks[block_hash].append({
                    "file_path": file_path,
                    "start_line": i + 1,  # 1-indexed
                    "end_line": j,
                    "code": block
                })
        
        # Find duplicates within this file
        for block_hash, locations in self.code_blocks.items():
            # Only consider blocks with multiple occurrences
            if len(locations) < 2:
                continue
                
            # Only consider duplicates where at least one occurrence is in this file
            file_locations = [loc for loc in locations if loc["file_path"] == file_path]
            if not file_locations:
                continue
                
            # Create a duplicate entry
            duplicates.append({
                "code": locations[0]["code"],
                "occurrences": len(locations),
                "locations": locations,
                "severity": min(1.0, (len(locations) - 1) * 0.2)  # More occurrences = higher severity
            })
        
        return duplicates
    
    def _normalize_code_block(self, block: str) -> str:
        """Normalize a code block for comparison.
        
        Args:
            block: The code block
            
        Returns:
            Normalized code block
        """
        # Remove comments
        block = re.sub(r'#.*$', '', block, flags=re.MULTILINE)
        
        # Normalize whitespace
        block = re.sub(r'\s+', ' ', block)
        
        # Remove string literals
        block = re.sub(r'"[^"]*"', '""', block)
        block = re.sub(r"'[^']*'", "''", block)
        
        return block.strip()
    
    def _find_repeated_strings(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Find repeated string literals in a file.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            
        Returns:
            A list of repeated string literals
        """
        repeated_strings = []
        string_occurrences = defaultdict(list)
        
        # Find all string literals
        for node in ast.walk(tree):
            if isinstance(node, ast.Str) and len(node.s) >= self.min_string_length:
                string_occurrences[node.s].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
                
                # Also store in global collection
                self.string_literals[node.s].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
        
        # Find strings with multiple occurrences
        for string, occurrences in string_occurrences.items():
            if len(occurrences) >= self.min_string_occurrences:
                repeated_strings.append({
                    "string": string,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })
        
        # Also check global collection for strings that appear in multiple files
        for string, occurrences in self.string_literals.items():
            # Skip strings already reported
            if string in string_occurrences and len(string_occurrences[string]) >= self.min_string_occurrences:
                continue
                
            # Check if this string appears in this file and others
            file_occurrences = [o for o in occurrences if o["file_path"] == file_path]
            if file_occurrences and len(occurrences) >= self.min_string_occurrences:
                repeated_strings.append({
                    "string": string,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })
        
        return repeated_strings
    
    def _find_repeated_constants(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Find repeated numeric constants in a file.
        
        Args:
            tree: AST of the file
            file_path: Path to the file
            
        Returns:
            A list of repeated numeric constants
        """
        repeated_constants = []
        constant_occurrences = defaultdict(list)
        
        # Find all numeric constants
        for node in ast.walk(tree):
            if isinstance(node, ast.Num):
                # Skip common constants like 0, 1, -1
                if node.n in (0, 1, -1):
                    continue
                    
                constant_occurrences[node.n].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
                
                # Also store in global collection
                self.numeric_constants[node.n].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
        
        # Find constants with multiple occurrences
        for constant, occurrences in constant_occurrences.items():
            if len(occurrences) >= self.min_string_occurrences:
                repeated_constants.append({
                    "constant": constant,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })
        
        # Also check global collection for constants that appear in multiple files
        for constant, occurrences in self.numeric_constants.items():
            # Skip constants already reported
            if constant in constant_occurrences and len(constant_occurrences[constant]) >= self.min_string_occurrences:
                continue
                
            # Check if this constant appears in this file and others
            file_occurrences = [o for o in occurrences if o["file_path"] == file_path]
            if file_occurrences and len(occurrences) >= self.min_string_occurrences:
                repeated_constants.append({
                    "constant": constant,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })
        
        return repeated_constants
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate refactoring recommendations based on analysis.
        
        Args:
            results: Analysis results
            
        Returns:
            A dictionary of recommendations
        """
        recommendations = {}
        
        # Recommendations for duplicate code blocks
        if results.get("duplicate_code_blocks"):
            block_recs = []
            for block in results["duplicate_code_blocks"]:
                rec = f"Extract duplicate code block (found in {block['occurrences']} locations) into a reusable function or method."
                block_recs.append(rec)
            recommendations["duplicate_code_blocks"] = block_recs
        
        # Recommendations for repeated strings
        if results.get("repeated_strings"):
            string_recs = []
            for string in results["repeated_strings"]:
                rec = f"String '{string['string'][:30]}...' is repeated {string['occurrences']} times. Consider defining it as a constant."
                string_recs.append(rec)
            recommendations["repeated_strings"] = string_recs
        
        # Recommendations for repeated constants
        if results.get("repeated_constants"):
            constant_recs = []
            for constant in results["repeated_constants"]:
                rec = f"Constant {constant['constant']} is repeated {constant['occurrences']} times. Consider defining it as a named constant."
                constant_recs.append(rec)
            recommendations["repeated_constants"] = constant_recs
        
        return recommendations
    
    def _add_to_summary(self, summary: Dict[str, Any], file_results: List[Dict[str, Any]]) -> None:
        """Add DRY-specific information to the summary.
        
        Args:
            summary: The summary dictionary to add to
            file_results: List of file analysis results
        """
        # Count DRY violations
        duplicate_blocks_count = 0
        repeated_strings_count = 0
        repeated_constants_count = 0
        
        for result in file_results:
            if "error" in result:
                continue
                
            duplicate_blocks_count += len(result.get("duplicate_code_blocks", []))
            repeated_strings_count += len(result.get("repeated_strings", []))
            repeated_constants_count += len(result.get("repeated_constants", []))
        
        total_violations = duplicate_blocks_count + repeated_strings_count + repeated_constants_count
        
        summary["duplicate_blocks_count"] = duplicate_blocks_count
        summary["repeated_strings_count"] = repeated_strings_count
        summary["repeated_constants_count"] = repeated_constants_count
        summary["total_dry_violations"] = total_violations
        
        # Calculate DRY compliance rate (arbitrary formula)
        file_count = summary.get("analyzed_count", 0)
        if file_count > 0:
            # A perfect codebase would have 0 violations
            # Let's say more than 2 violations per file is bad
            max_acceptable_violations = file_count * 2
            summary["dry_compliance_rate"] = max(0.0, 1.0 - (total_violations / max(1, max_acceptable_violations)))
        else:
            summary["dry_compliance_rate"] = 1.0
    
    def _add_to_text_report(self, report: List[str]) -> None:
        """Add DRY-specific information to the text report.
        
        Args:
            report: The report lines to add to
        """
        summary = self.results.get("summary", {})
        report.append(f"Duplicate code blocks: {summary.get('duplicate_blocks_count', 0)}")
        report.append(f"Repeated string literals: {summary.get('repeated_strings_count', 0)}")
        report.append(f"Repeated numeric constants: {summary.get('repeated_constants_count', 0)}")
        report.append(f"Total DRY violations: {summary.get('total_dry_violations', 0)}")
        report.append(f"DRY compliance rate: {summary.get('dry_compliance_rate', 0):.0%}")
        report.append("")
        
        # Report violations
        violations_found = False
        
        # Report duplicate code blocks
        if summary.get('duplicate_blocks_count', 0) > 0:
            violations_found = True
            report.append("Duplicate Code Blocks:")
            
            for file_result in self.results.get("files", []):
                if "error" in file_result:
                    continue
                    
                file_path = file_result.get("file_path", "Unknown")
                file_name = os.path.basename(file_path)
                
                for block in file_result.get("duplicate_code_blocks", []):
                    report.append(f"  {file_name}: Block with {block['occurrences']} occurrences")
                    report.append(f"    First few lines: {block['code'].split('\\n')[0][:50]}...")
                    
                    # Generate recommendation
                    recommendations = self._generate_recommendations(file_result)
                    if "duplicate_code_blocks" in recommendations:
                        report.append(f"    Recommendation: {recommendations['duplicate_code_blocks'][0]}")
                    
                    report.append("")
        
        # Report repeated strings
        if summary.get('repeated_strings_count', 0) > 0:
            violations_found = True
            report.append("Repeated String Literals:")
            
            for file_result in self.results.get("files", []):
                if "error" in file_result:
                    continue
                    
                file_path = file_result.get("file_path", "Unknown")
                file_name = os.path.basename(file_path)
                
                for string in file_result.get("repeated_strings", []):
                    report.append(f"  {file_name}: '{string['string'][:30]}...' repeated {string['occurrences']} times")
                    
                    # Generate recommendation
                    recommendations = self._generate_recommendations(file_result)
                    if "repeated_strings" in recommendations:
                        report.append(f"    Recommendation: {recommendations['repeated_strings'][0]}")
                    
                    report.append("")
        
        # Report repeated constants
        if summary.get('repeated_constants_count', 0) > 0:
            violations_found = True
            report.append("Repeated Numeric Constants:")
            
            for file_result in self.results.get("files", []):
                if "error" in file_result:
                    continue
                    
                file_path = file_result.get("file_path", "Unknown")
                file_name = os.path.basename(file_path)
                
                for constant in file_result.get("repeated_constants", []):
                    report.append(f"  {file_name}: {constant['constant']} repeated {constant['occurrences']} times")
                    
                    # Generate recommendation
                    recommendations = self._generate_recommendations(file_result)
                    if "repeated_constants" in recommendations:
                        report.append(f"    Recommendation: {recommendations['repeated_constants'][0]}")
                    
                    report.append("")
        
        if not violations_found:
            report.append("  No DRY violations detected!")
    
    def _add_to_html_summary(self, html: List[str]) -> None:
        """Add DRY-specific information to the HTML summary.
        
        Args:
            html: The HTML lines to add to
        """
        summary = self.results.get("summary", {})
        html.append(f"<p>Duplicate code blocks: {summary.get('duplicate_blocks_count', 0)}</p>")
        html.append(f"<p>Repeated string literals: {summary.get('repeated_strings_count', 0)}</p>")
        html.append(f"<p>Repeated numeric constants: {summary.get('repeated_constants_count', 0)}</p>")
        html.append(f"<p>Total DRY violations: {summary.get('total_dry_violations', 0)}</p>")
        
        # Add compliance rate with color coding
        compliance_rate = summary.get('dry_compliance_rate', 0)
        color_class = "good" if compliance_rate >= 0.8 else "warning" if compliance_rate >= 0.6 else "bad"
        html.append(f"<p>DRY compliance rate: <span class='{color_class}'>{compliance_rate:.0%}</span></p>")
    
    def _add_to_html_report(self, html: List[str]) -> None:
        """Add DRY-specific information to the HTML report.
        
        Args:
            html: The HTML lines to add to
        """
        # Report duplicate code blocks
        html.append("<h2>Duplicate Code Blocks</h2>")
        
        blocks_found = False
        for file_result in self.results.get("files", []):
            if "error" in file_result or not file_result.get("duplicate_code_blocks"):
                continue
                
            blocks_found = True
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for block in file_result.get("duplicate_code_blocks", []):
                html.append("<div class='file'>")
                html.append("<div class='file-header'>")
                html.append(f"<div class='file-path'>{file_name}: Duplicate Code Block</div>")
                html.append(f"<div class='file-score bad'>Occurrences: {block['occurrences']}</div>")
                html.append("</div>")
                
                html.append("<div class='code-preview'>")
                html.append("<pre>")
                html.append(block['code'][:200] + ("..." if len(block['code']) > 200 else ""))
                html.append("</pre>")
                html.append("</div>")
                
                # Generate recommendation
                recommendations = self._generate_recommendations(file_result)
                if "duplicate_code_blocks" in recommendations:
                    html.append(f"<p class='recommendation'>{recommendations['duplicate_code_blocks'][0]}</p>")
                
                html.append("</div>")
        
        if not blocks_found:
            html.append("<p>No duplicate code blocks detected.</p>")
        
        # Report repeated strings
        html.append("<h2>Repeated String Literals</h2>")
        
        strings_found = False
        for file_result in self.results.get("files", []):
            if "error" in file_result or not file_result.get("repeated_strings"):
                continue
                
            strings_found = True
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for string in file_result.get("repeated_strings", []):
                html.append("<div class='file'>")
                html.append("<div class='file-header'>")
                html.append(f"<div class='file-path'>{file_name}: Repeated String</div>")
                html.append(f"<div class='file-score warning'>Occurrences: {string['occurrences']}</div>")
                html.append("</div>")
                
                html.append("<div class='string-preview'>")
                html.append(f"<p>'{string['string'][:50]}{'...' if len(string['string']) > 50 else ''}'</p>")
                html.append("</div>")
                
                # Generate recommendation
                recommendations = self._generate_recommendations(file_result)
                if "repeated_strings" in recommendations:
                    html.append(f"<p class='recommendation'>{recommendations['repeated_strings'][0]}</p>")
                
                html.append("</div>")
        
        if not strings_found:
            html.append("<p>No repeated string literals detected.</p>")
        
        # Report repeated constants
        html.append("<h2>Repeated Numeric Constants</h2>")
        
        constants_found = False
        for file_result in self.results.get("files", []):
            if "error" in file_result or not file_result.get("repeated_constants"):
                continue
                
            constants_found = True
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for constant in file_result.get("repeated_constants", []):
                html.append("<div class='file'>")
                html.append("<div class='file-header'>")
                html.append(f"<div class='file-path'>{file_name}: Repeated Constant</div>")
                html.append(f"<div class='file-score warning'>Occurrences: {constant['occurrences']}</div>")
                html.append("</div>")
                
                html.append("<div class='constant-preview'>")
                html.append(f"<p>{constant['constant']}</p>")
                html.append("</div>")
                
                # Generate recommendation
                recommendations = self._generate_recommendations(file_result)
                if "repeated_constants" in recommendations:
                    html.append(f"<p class='recommendation'>{recommendations['repeated_constants'][0]}</p>")
                
                html.append("</div>")
        
        if not constants_found:
            html.append("<p>No repeated numeric constants detected.</p>")
