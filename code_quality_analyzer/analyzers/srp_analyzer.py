"""Single Responsibility Principle Analyzer.

This module provides an analyzer for detecting violations of the Single Responsibility Principle.
It uses advanced heuristics to identify classes with multiple responsibilities.
"""

import os
import ast
import re
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

from ..base_analyzer import BaseAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# NLP-based responsibility keywords
RESPONSIBILITY_DOMAINS = {
    "data_access": ["database", "query", "repository", "store", "retrieve", "save", "load", "persist", "fetch"],
    "ui": ["display", "show", "render", "view", "ui", "interface", "screen", "layout"],
    "validation": ["validate", "check", "verify", "ensure", "assert", "constraint"],
    "calculation": ["calculate", "compute", "process", "algorithm", "formula"],
    "io": ["file", "read", "write", "stream", "input", "output", "io", "print"],
    "network": ["http", "request", "response", "api", "endpoint", "url", "network", "fetch"],
    "authentication": ["auth", "login", "permission", "role", "access", "credential"],
    "error_handling": ["exception", "error", "handle", "try", "catch", "finally", "raise"],
    "configuration": ["config", "setting", "property", "environment", "parameter"],
    "logging": ["log", "trace", "debug", "info", "warn", "error", "fatal"]
}

class SRPAnalyzer(BaseAnalyzer):
    """Analyzes Python code for Single Responsibility Principle violations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new SRPAnalyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        default_config = {
            'max_responsibilities': 1,
            'cohesion_threshold': 0.5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(
            name="SRP Analyzer",
            description="Analyzes code for violations of the Single Responsibility Principle",
            config=default_config
        )
        
        self.max_responsibilities = self.config['max_responsibilities']
        self.cohesion_threshold = self.config['cohesion_threshold']
    
    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a file for SRP violations.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            tree: AST of the file
            
        Returns:
            A dictionary containing analysis results
        """
        # Find all classes in the file
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        results = {
            "file_path": file_path,
            "class_analysis": [],
            "overall_srp_score": 1.0  # Will be updated based on class analyses
        }
        
        for cls in classes:
            class_result = self._analyze_class(cls, content)
            results["class_analysis"].append(class_result)
        
        # Calculate overall SRP score for the file
        if results["class_analysis"]:
            avg_score = sum(c["srp_score"] for c in results["class_analysis"]) / len(results["class_analysis"])
            results["overall_srp_score"] = avg_score
        
        return results
    
    def _analyze_class(self, cls_node: ast.ClassDef, file_content: str) -> Dict[str, Any]:
        """Analyze a class for SRP violations.
        
        Args:
            cls_node: The class AST node
            file_content: The file content
            
        Returns:
            A dictionary containing analysis results for the class
        """
        methods = [node for node in ast.walk(cls_node) if isinstance(node, ast.FunctionDef)]
        
        # Extract method names and docstrings
        method_info = []
        for method in methods:
            docstring = ast.get_docstring(method) or ""
            method_info.append({
                "name": method.name,
                "docstring": docstring,
                "code": self.get_node_source(method, file_content)
            })
        
        # Analyze responsibilities
        responsibilities = self._identify_responsibilities(cls_node, method_info)
        
        # Calculate method cohesion
        cohesion_score = self._calculate_cohesion(method_info)
        
        # Calculate SRP score (1.0 is perfect, 0.0 is worst)
        srp_violations = max(0, len(responsibilities) - self.max_responsibilities)
        srp_score = max(0.0, 1.0 - (srp_violations * 0.2))
        
        # Adjust score based on cohesion
        if cohesion_score < self.cohesion_threshold:
            srp_score *= cohesion_score / self.cohesion_threshold
        
        return {
            "class_name": cls_node.name,
            "responsibilities": list(responsibilities),
            "num_methods": len(methods),
            "cohesion_score": cohesion_score,
            "srp_score": srp_score,
            "srp_violations": srp_violations > 0,
            "recommendation": self._generate_class_recommendation(cls_node.name, responsibilities, cohesion_score)
        }
    
    def _identify_responsibilities(self, cls_node: ast.ClassDef, method_info: List[Dict[str, str]]) -> Set[str]:
        """Identify distinct responsibilities in a class using NLP techniques.
        
        Args:
            cls_node: The class AST node
            method_info: Information about the class's methods
            
        Returns:
            A set of responsibility domains
        """
        responsibilities = set()
        
        # Check class name and docstring
        class_docstring = ast.get_docstring(cls_node) or ""
        class_text = f"{cls_node.name} {class_docstring}"
        
        # Add responsibilities from class name and docstring
        self._add_responsibilities_from_text(class_text, responsibilities)
        
        # Check methods
        for method in method_info:
            method_text = f"{method['name']} {method['docstring']} {method['code']}"
            self._add_responsibilities_from_text(method_text, responsibilities)
        
        return responsibilities
    
    def _add_responsibilities_from_text(self, text: str, responsibilities: Set[str]) -> None:
        """Extract responsibilities from text using keyword matching.
        
        Args:
            text: The text to analyze
            responsibilities: Set to add responsibilities to
        """
        text = text.lower()
        for domain, keywords in RESPONSIBILITY_DOMAINS.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', text):
                    responsibilities.add(domain)
                    break
    
    def _calculate_cohesion(self, method_info: List[Dict[str, str]]) -> float:
        """Calculate method cohesion based on shared vocabulary.
        
        Args:
            method_info: Information about the class's methods
            
        Returns:
            A cohesion score between 0.0 and 1.0
        """
        if len(method_info) <= 1:
            return 1.0  # Perfect cohesion for single method
        
        # Extract words from each method
        method_words = []
        for method in method_info:
            words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', 
                                  f"{method['name']} {method['docstring']} {method['code']}".lower()))
            method_words.append(words)
        
        # Calculate pairwise similarity
        total_similarity = 0
        comparison_count = 0
        
        for i in range(len(method_words)):
            for j in range(i+1, len(method_words)):
                if not method_words[i] or not method_words[j]:
                    continue
                    
                similarity = len(method_words[i].intersection(method_words[j])) / len(method_words[i].union(method_words[j]))
                total_similarity += similarity
                comparison_count += 1
        
        return total_similarity / max(1, comparison_count)
    
    def _generate_class_recommendation(self, class_name: str, responsibilities: Set[str], cohesion_score: float) -> str:
        """Generate refactoring recommendations based on analysis.
        
        Args:
            class_name: The name of the class
            responsibilities: The identified responsibilities
            cohesion_score: The cohesion score
            
        Returns:
            A recommendation string
        """
        if len(responsibilities) <= self.max_responsibilities and cohesion_score >= self.cohesion_threshold:
            return f"Class '{class_name}' appears to follow SRP."
        
        recommendation = f"Class '{class_name}' may have too many responsibilities: {', '.join(responsibilities)}. "
        
        if len(responsibilities) > self.max_responsibilities:
            recommendation += f"Consider splitting into {len(responsibilities)} classes, each with a single responsibility. "
        
        if cohesion_score < self.cohesion_threshold:
            recommendation += f"Low method cohesion ({cohesion_score:.2f}) indicates methods may not be working together."
        
        return recommendation
    
    def _add_to_summary(self, summary: Dict[str, Any], file_results: List[Dict[str, Any]]) -> None:
        """Add SRP-specific information to the summary.
        
        Args:
            summary: The summary dictionary to add to
            file_results: List of file analysis results
        """
        # Count classes with SRP violations
        violation_count = 0
        class_count = 0
        
        for result in file_results:
            if "error" in result:
                continue
                
            for cls in result.get("class_analysis", []):
                class_count += 1
                if cls.get("srp_violations", False):
                    violation_count += 1
        
        summary["class_count"] = class_count
        summary["srp_violation_count"] = violation_count
        summary["srp_compliance_rate"] = (class_count - violation_count) / max(1, class_count)
    
    def _add_to_text_report(self, report: List[str]) -> None:
        """Add SRP-specific information to the text report.
        
        Args:
            report: The report lines to add to
        """
        summary = self.results.get("summary", {})
        report.append(f"Classes analyzed: {summary.get('class_count', 0)}")
        report.append(f"Classes with SRP violations: {summary.get('srp_violation_count', 0)}")
        report.append(f"SRP compliance rate: {summary.get('srp_compliance_rate', 0):.0%}")
        report.append("")
        
        # Report violations
        report.append("SRP Violations:")
        violations_found = False
        
        for file_result in self.results.get("files", []):
            if "error" in file_result:
                continue
                
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for cls in file_result.get("class_analysis", []):
                if cls.get("srp_violations", False):
                    violations_found = True
                    report.append(f"  {file_name}: Class {cls['class_name']}")
                    report.append(f"    Responsibilities: {', '.join(cls['responsibilities'])}")
                    report.append(f"    Cohesion Score: {cls['cohesion_score']:.2f}")
                    report.append(f"    Recommendation: {cls['recommendation']}")
                    report.append("")
        
        if not violations_found:
            report.append("  No SRP violations detected!")
    
    def _add_to_html_summary(self, html: List[str]) -> None:
        """Add SRP-specific information to the HTML summary.
        
        Args:
            html: The HTML lines to add to
        """
        summary = self.results.get("summary", {})
        html.append(f"<p>Classes analyzed: {summary.get('class_count', 0)}</p>")
        html.append(f"<p>Classes with SRP violations: {summary.get('srp_violation_count', 0)}</p>")
        
        # Add compliance rate with color coding
        compliance_rate = summary.get('srp_compliance_rate', 0)
        color_class = "good" if compliance_rate >= 0.8 else "warning" if compliance_rate >= 0.6 else "bad"
        html.append(f"<p>SRP compliance rate: <span class='{color_class}'>{compliance_rate:.0%}</span></p>")
    
    def _add_to_html_report(self, html: List[str]) -> None:
        """Add SRP-specific information to the HTML report.
        
        Args:
            html: The HTML lines to add to
        """
        html.append("<h2>Class Analysis</h2>")
        
        for file_result in self.results.get("files", []):
            if "error" in file_result:
                continue
                
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for cls in file_result.get("class_analysis", []):
                # Determine color class based on SRP score
                srp_score = cls.get("srp_score", 0)
                color_class = "good" if srp_score >= 0.8 else "warning" if srp_score >= 0.6 else "bad"
                
                html.append("<div class='file'>")
                html.append("<div class='file-header'>")
                html.append(f"<div class='file-path'>{file_name}: Class {cls['class_name']}</div>")
                html.append(f"<div class='file-score {color_class}'>SRP Score: {srp_score:.2f}</div>")
                html.append("</div>")
                
                html.append(f"<p>Responsibilities: {', '.join(cls['responsibilities'])}</p>")
                html.append(f"<p>Methods: {cls['num_methods']}</p>")
                html.append(f"<p>Cohesion Score: {cls['cohesion_score']:.2f}</p>")
                
                if cls.get("srp_violations", False):
                    html.append(f"<p class='recommendation'>{cls['recommendation']}</p>")
                
                html.append("</div>")
