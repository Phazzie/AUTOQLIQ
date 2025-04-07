"""KISS (Keep It Simple, Stupid) Principle Analyzer.

This module provides an analyzer for detecting violations of the KISS principle.
It identifies complex code patterns that could be simplified.
"""

import os
import ast
import re
import logging
from typing import Dict, List, Set, Tuple, Any, Optional

from ..base_analyzer import BaseAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KISSAnalyzer(BaseAnalyzer):
    """Analyzes Python code for KISS principle violations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new KISSAnalyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        default_config = {
            'max_method_lines': 20,
            'max_nesting_depth': 3,
            'max_cyclomatic_complexity': 10,
            'max_cognitive_complexity': 15,
            'max_parameters': 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(
            name="KISS Analyzer",
            description="Analyzes code for violations of the Keep It Simple, Stupid principle",
            config=default_config
        )
        
        self.max_method_lines = self.config['max_method_lines']
        self.max_nesting_depth = self.config['max_nesting_depth']
        self.max_cyclomatic_complexity = self.config['max_cyclomatic_complexity']
        self.max_cognitive_complexity = self.config['max_cognitive_complexity']
        self.max_parameters = self.config['max_parameters']
    
    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a file for KISS violations.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            tree: AST of the file
            
        Returns:
            A dictionary containing analysis results
        """
        # Find all functions and methods in the file
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(node)
        
        results = {
            "file_path": file_path,
            "method_analysis": [],
            "overall_kiss_score": 1.0  # Will be updated based on method analyses
        }
        
        for func in functions:
            method_result = self._analyze_method(func, content)
            results["method_analysis"].append(method_result)
        
        # Calculate overall KISS score for the file
        if results["method_analysis"]:
            avg_score = sum(m["kiss_score"] for m in results["method_analysis"]) / len(results["method_analysis"])
            results["overall_kiss_score"] = avg_score
        
        return results
    
    def _analyze_method(self, func_node: ast.FunctionDef, file_content: str) -> Dict[str, Any]:
        """Analyze a method for KISS violations.
        
        Args:
            func_node: The function AST node
            file_content: The file content
            
        Returns:
            A dictionary containing analysis results for the method
        """
        method_name = func_node.name
        violations = []
        
        # Get method source code
        method_source = self.get_node_source(func_node, file_content)
        method_lines = method_source.split('\n')
        
        # Check method length
        if len(method_lines) > self.max_method_lines:
            violations.append({
                "type": "long_method",
                "description": f"Method is {len(method_lines)} lines long, exceeding the maximum of {self.max_method_lines}",
                "severity": min(1.0, (len(method_lines) - self.max_method_lines) / self.max_method_lines)
            })
        
        # Check nesting depth
        max_depth = self._calculate_max_nesting_depth(func_node)
        if max_depth > self.max_nesting_depth:
            violations.append({
                "type": "deep_nesting",
                "description": f"Method has a nesting depth of {max_depth}, exceeding the maximum of {self.max_nesting_depth}",
                "severity": min(1.0, (max_depth - self.max_nesting_depth) / self.max_nesting_depth)
            })
        
        # Check cyclomatic complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(func_node)
        if cyclomatic_complexity > self.max_cyclomatic_complexity:
            violations.append({
                "type": "high_cyclomatic_complexity",
                "description": f"Method has a cyclomatic complexity of {cyclomatic_complexity}, exceeding the maximum of {self.max_cyclomatic_complexity}",
                "severity": min(1.0, (cyclomatic_complexity - self.max_cyclomatic_complexity) / self.max_cyclomatic_complexity)
            })
        
        # Check cognitive complexity
        cognitive_complexity = self._calculate_cognitive_complexity(func_node)
        if cognitive_complexity > self.max_cognitive_complexity:
            violations.append({
                "type": "high_cognitive_complexity",
                "description": f"Method has a cognitive complexity of {cognitive_complexity}, exceeding the maximum of {self.max_cognitive_complexity}",
                "severity": min(1.0, (cognitive_complexity - self.max_cognitive_complexity) / self.max_cognitive_complexity)
            })
        
        # Check parameter count
        param_count = len(func_node.args.args)
        if param_count > self.max_parameters:
            violations.append({
                "type": "too_many_parameters",
                "description": f"Method has {param_count} parameters, exceeding the maximum of {self.max_parameters}",
                "severity": min(1.0, (param_count - self.max_parameters) / self.max_parameters)
            })
        
        # Check for complex conditionals
        complex_conditionals = self._find_complex_conditionals(func_node)
        if complex_conditionals:
            violations.append({
                "type": "complex_conditionals",
                "description": f"Method has {len(complex_conditionals)} complex conditional expressions",
                "details": complex_conditionals,
                "severity": min(1.0, len(complex_conditionals) / 3)  # Arbitrary scaling
            })
        
        # Calculate KISS score (1.0 is perfect, 0.0 is worst)
        # Weight violations by severity
        total_severity = sum(v["severity"] for v in violations)
        kiss_score = max(0.0, 1.0 - (total_severity * 0.2))
        
        return {
            "method_name": method_name,
            "line_count": len(method_lines),
            "nesting_depth": max_depth,
            "cyclomatic_complexity": cyclomatic_complexity,
            "cognitive_complexity": cognitive_complexity,
            "parameter_count": param_count,
            "violations": violations,
            "kiss_score": kiss_score,
            "recommendation": self._generate_method_recommendation(method_name, violations)
        }
    
    def _calculate_max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate the maximum nesting depth in a function.
        
        Args:
            node: The AST node
            
        Returns:
            The maximum nesting depth
        """
        max_depth = 0
        
        def _visit_node(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            # Increment depth for nested control structures
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                current_depth += 1
            
            # Recursively visit child nodes
            for child in ast.iter_child_nodes(node):
                _visit_node(child, current_depth)
        
        _visit_node(node)
        return max_depth
    
    def _calculate_cyclomatic_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate the cyclomatic complexity of a function.
        
        Args:
            func_node: The function AST node
            
        Returns:
            The cyclomatic complexity
        """
        # Start with 1 (base complexity)
        complexity = 1
        
        # Count branches
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate the cognitive complexity of a function.
        
        Args:
            func_node: The function AST node
            
        Returns:
            The cognitive complexity
        """
        complexity = 0
        nesting_level = 0
        
        def _visit_node(node, level=0):
            nonlocal complexity, nesting_level
            
            # Increment for control flow structures
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                complexity += level + 1
                nesting_level = level + 1
            
            # Additional increment for else branches
            if isinstance(node, ast.If) and node.orelse:
                complexity += 1
            
            # Increment for boolean operations
            if isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And) or isinstance(node.op, ast.Or):
                    complexity += len(node.values) - 1
            
            # Recursively visit child nodes
            for child in ast.iter_child_nodes(node):
                _visit_node(child, nesting_level)
        
        _visit_node(func_node)
        return complexity
    
    def _find_complex_conditionals(self, func_node: ast.FunctionDef) -> List[str]:
        """Find complex conditional expressions in a function.
        
        Args:
            func_node: The function AST node
            
        Returns:
            A list of complex conditional descriptions
        """
        complex_conditionals = []
        
        for node in ast.walk(func_node):
            # Check for boolean operations with multiple operands
            if isinstance(node, ast.BoolOp) and len(node.values) > 2:
                complex_conditionals.append(f"Boolean operation with {len(node.values)} operands at line {node.lineno}")
            
            # Check for nested boolean operations
            elif isinstance(node, ast.BoolOp):
                for value in node.values:
                    if isinstance(value, ast.BoolOp):
                        complex_conditionals.append(f"Nested boolean operation at line {node.lineno}")
                        break
            
            # Check for complex comparisons
            elif isinstance(node, ast.Compare) and len(node.ops) > 1:
                complex_conditionals.append(f"Comparison with {len(node.ops)} operators at line {node.lineno}")
        
        return complex_conditionals
    
    def _generate_method_recommendation(self, method_name: str, violations: List[Dict[str, Any]]) -> str:
        """Generate refactoring recommendations based on analysis.
        
        Args:
            method_name: The name of the method
            violations: The identified violations
            
        Returns:
            A recommendation string
        """
        if not violations:
            return f"Method '{method_name}' follows the KISS principle."
        
        recommendations = [f"Method '{method_name}' has potential KISS violations:"]
        
        for violation in violations:
            if violation["type"] == "long_method":
                recommendations.append(f"- Method is too long ({violation['description']}). Consider breaking it into smaller, focused methods.")
            
            elif violation["type"] == "deep_nesting":
                recommendations.append(f"- Nesting is too deep ({violation['description']}). Consider extracting nested blocks into separate methods or using early returns.")
            
            elif violation["type"] == "high_cyclomatic_complexity":
                recommendations.append(f"- Cyclomatic complexity is too high ({violation['description']}). Simplify conditional logic and break down the method.")
            
            elif violation["type"] == "high_cognitive_complexity":
                recommendations.append(f"- Cognitive complexity is too high ({violation['description']}). Simplify the method's logic to make it more readable.")
            
            elif violation["type"] == "too_many_parameters":
                recommendations.append(f"- Too many parameters ({violation['description']}). Consider using parameter objects or breaking the method into smaller ones.")
            
            elif violation["type"] == "complex_conditionals":
                recommendations.append(f"- Complex conditionals detected ({violation['description']}). Extract conditions into well-named methods or variables.")
        
        return " ".join(recommendations)
    
    def _add_to_summary(self, summary: Dict[str, Any], file_results: List[Dict[str, Any]]) -> None:
        """Add KISS-specific information to the summary.
        
        Args:
            summary: The summary dictionary to add to
            file_results: List of file analysis results
        """
        # Count methods with KISS violations
        violation_count = 0
        method_count = 0
        
        for result in file_results:
            if "error" in result:
                continue
                
            for method in result.get("method_analysis", []):
                method_count += 1
                if method.get("violations", []):
                    violation_count += 1
        
        summary["method_count"] = method_count
        summary["kiss_violation_count"] = violation_count
        summary["kiss_compliance_rate"] = (method_count - violation_count) / max(1, method_count)
    
    def _add_to_text_report(self, report: List[str]) -> None:
        """Add KISS-specific information to the text report.
        
        Args:
            report: The report lines to add to
        """
        summary = self.results.get("summary", {})
        report.append(f"Methods analyzed: {summary.get('method_count', 0)}")
        report.append(f"Methods with KISS violations: {summary.get('kiss_violation_count', 0)}")
        report.append(f"KISS compliance rate: {summary.get('kiss_compliance_rate', 0):.0%}")
        report.append("")
        
        # Report violations
        report.append("KISS Violations:")
        violations_found = False
        
        for file_result in self.results.get("files", []):
            if "error" in file_result:
                continue
                
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for method in file_result.get("method_analysis", []):
                if method.get("violations", []):
                    violations_found = True
                    report.append(f"  {file_name}: Method {method['method_name']}")
                    report.append(f"    Lines: {method['line_count']}")
                    report.append(f"    Nesting Depth: {method['nesting_depth']}")
                    report.append(f"    Cyclomatic Complexity: {method['cyclomatic_complexity']}")
                    report.append(f"    Cognitive Complexity: {method['cognitive_complexity']}")
                    report.append(f"    Parameters: {method['parameter_count']}")
                    
                    for violation in method.get("violations", []):
                        report.append(f"    Violation: {violation['description']}")
                    
                    report.append(f"    Recommendation: {method['recommendation']}")
                    report.append("")
        
        if not violations_found:
            report.append("  No KISS violations detected!")
    
    def _add_to_html_summary(self, html: List[str]) -> None:
        """Add KISS-specific information to the HTML summary.
        
        Args:
            html: The HTML lines to add to
        """
        summary = self.results.get("summary", {})
        html.append(f"<p>Methods analyzed: {summary.get('method_count', 0)}</p>")
        html.append(f"<p>Methods with KISS violations: {summary.get('kiss_violation_count', 0)}</p>")
        
        # Add compliance rate with color coding
        compliance_rate = summary.get('kiss_compliance_rate', 0)
        color_class = "good" if compliance_rate >= 0.8 else "warning" if compliance_rate >= 0.6 else "bad"
        html.append(f"<p>KISS compliance rate: <span class='{color_class}'>{compliance_rate:.0%}</span></p>")
    
    def _add_to_html_report(self, html: List[str]) -> None:
        """Add KISS-specific information to the HTML report.
        
        Args:
            html: The HTML lines to add to
        """
        html.append("<h2>Method Analysis</h2>")
        
        for file_result in self.results.get("files", []):
            if "error" in file_result:
                continue
                
            file_path = file_result.get("file_path", "Unknown")
            file_name = os.path.basename(file_path)
            
            for method in file_result.get("method_analysis", []):
                # Determine color class based on KISS score
                kiss_score = method.get("kiss_score", 0)
                color_class = "good" if kiss_score >= 0.8 else "warning" if kiss_score >= 0.6 else "bad"
                
                html.append("<div class='file'>")
                html.append("<div class='file-header'>")
                html.append(f"<div class='file-path'>{file_name}: Method {method['method_name']}</div>")
                html.append(f"<div class='file-score {color_class}'>KISS Score: {kiss_score:.2f}</div>")
                html.append("</div>")
                
                html.append("<div class='metrics'>")
                html.append(f"<p>Lines: {method['line_count']}</p>")
                html.append(f"<p>Nesting Depth: {method['nesting_depth']}</p>")
                html.append(f"<p>Cyclomatic Complexity: {method['cyclomatic_complexity']}</p>")
                html.append(f"<p>Cognitive Complexity: {method['cognitive_complexity']}</p>")
                html.append(f"<p>Parameters: {method['parameter_count']}</p>")
                html.append("</div>")
                
                if method.get("violations", []):
                    html.append("<div class='violations'>")
                    html.append("<h3>Violations:</h3>")
                    
                    for violation in method.get("violations", []):
                        html.append(f"<div class='violation'>{violation['description']}</div>")
                    
                    html.append(f"<p class='recommendation'>{method['recommendation']}</p>")
                    html.append("</div>")
                
                html.append("</div>")
