#!/usr/bin/env python
"""
KISS (Keep It Simple, Stupid) Principle Analyzer

This script analyzes Python files to identify potential violations of the KISS principle.
It detects patterns that indicate unnecessary complexity:
1. Long methods (> 20 lines)
2. Deep nesting (> 3 levels)
3. Complex conditionals
4. High cyclomatic complexity
5. Excessive parameters
6. Cognitive complexity

Usage:
    python analyze_kiss.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
import io
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

# Try to import complexity calculation libraries
try:
    import radon.complexity
    from radon.visitors import ComplexityVisitor
    HAS_RADON = True
except ImportError:
    HAS_RADON = False

try:
    import cognitive_complexity
    HAS_COGNITIVE_COMPLEXITY = True
except ImportError:
    HAS_COGNITIVE_COMPLEXITY = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KISSAnalyzer:
    """Analyzes Python code for KISS principle violations."""

    def __init__(
        self,
        max_method_lines: int = 20,
        max_nesting_depth: int = 3,
        max_cyclomatic_complexity: int = 10,
        max_cognitive_complexity: int = 15,
        max_parameters: int = 5
    ):
        self.max_method_lines = max_method_lines
        self.max_nesting_depth = max_nesting_depth
        self.max_cyclomatic_complexity = max_cyclomatic_complexity
        self.max_cognitive_complexity = max_cognitive_complexity
        self.max_parameters = max_parameters

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for KISS violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store content for use in complexity calculations
            self.current_file_content = content

            tree = ast.parse(content)

            results = {
                "file_path": file_path,
                "method_analysis": [],
                "overall_kiss_score": 1.0  # Will be updated based on method analyses
            }

            # Find all functions and methods in the file
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node)

            for func in functions:
                method_result = self._analyze_method(func, content)
                results["method_analysis"].append(method_result)

            # Calculate overall KISS score for the file
            if results["method_analysis"]:
                avg_score = sum(m["kiss_score"] for m in results["method_analysis"]) / len(results["method_analysis"])
                results["overall_kiss_score"] = avg_score

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _analyze_method(self, func_node: ast.FunctionDef, file_content: str) -> Dict:
        """Analyze a method for KISS violations."""
        method_name = func_node.name
        violations = []

        # Get method source code
        method_source = self._get_method_source(func_node, file_content)
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
            "recommendation": self._generate_recommendation(method_name, violations)
        }

    def _get_method_source(self, func_node: ast.FunctionDef, file_content: str) -> str:
        """Extract method source code from file content."""
        if not hasattr(func_node, 'lineno') or not hasattr(func_node, 'end_lineno'):
            return ""

        lines = file_content.splitlines()
        start_line = func_node.lineno - 1  # 0-indexed
        end_line = getattr(func_node, 'end_lineno', len(lines)) - 1

        return "\n".join(lines[start_line:end_line+1])

    def _calculate_max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate the maximum nesting depth in a function."""
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

        Uses radon library if available, otherwise falls back to a simplified calculation.
        """
        # Get method source code
        method_source = self._get_node_source(func_node, self.current_file_content)

        # Use radon if available
        if HAS_RADON:
            try:
                # Use radon's ComplexityVisitor
                visitor = ComplexityVisitor.from_code(method_source)
                if visitor.functions:
                    # Return the complexity of the function
                    return visitor.functions[0].complexity
            except Exception as e:
                logger.debug(f"Error calculating complexity with radon: {str(e)}")

        # Fall back to simplified calculation
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

        Uses cognitive_complexity library if available, otherwise falls back to a simplified calculation.
        """
        # Method source is only needed for radon, not for cognitive_complexity

        # Use cognitive_complexity library if available
        if HAS_COGNITIVE_COMPLEXITY:
            try:
                # Use cognitive_complexity library
                return cognitive_complexity.cognitive_complexity(func_node)
            except Exception as e:
                logger.debug(f"Error calculating cognitive complexity: {str(e)}")

        # Fall back to simplified calculation
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
        """Find complex conditional expressions in a function."""
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

    def _get_node_source(self, node: ast.AST, content: str) -> str:
        """Get source code for an AST node."""
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return ""

        lines = content.splitlines()
        start_line = node.lineno - 1  # Convert to 0-indexed
        end_line = getattr(node, 'end_lineno', len(lines)) - 1  # Convert to 0-indexed

        # Ensure we don't go out of bounds
        start_line = max(0, min(start_line, len(lines) - 1))
        end_line = max(0, min(end_line, len(lines) - 1))

        return "\n".join(lines[start_line:end_line + 1])

    def _generate_recommendation(self, method_name: str, violations: List[Dict]) -> str:
        """Generate refactoring recommendations based on analysis."""
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


def analyze_directory(directory_path: str, analyzer: KISSAnalyzer) -> List[Dict]:
    """Recursively analyze all Python files in a directory."""
    results = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results.append(analyzer.analyze_file(file_path))

    return results


def print_results(results: List[Dict]) -> None:
    """Print analysis results in a readable format."""
    print("\n===== KISS PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall KISS Score: {result['overall_kiss_score']:.2f}/1.00")

        for method_analysis in result.get("method_analysis", []):
            kiss_status = "✓" if method_analysis["kiss_score"] >= 0.8 else "✗"
            print(f"\n  Method: {method_analysis['method_name']} {kiss_status}")
            print(f"  KISS Score: {method_analysis['kiss_score']:.2f}/1.00")
            print(f"  Lines: {method_analysis['line_count']}")
            print(f"  Nesting Depth: {method_analysis['nesting_depth']}")
            print(f"  Cyclomatic Complexity: {method_analysis['cyclomatic_complexity']}")
            print(f"  Cognitive Complexity: {method_analysis['cognitive_complexity']}")
            print(f"  Parameters: {method_analysis['parameter_count']}")

            if method_analysis["violations"]:
                violations_found = True
                print("  Violations:")
                for violation in method_analysis["violations"]:
                    print(f"    - {violation['description']}")
                    if "details" in violation:
                        for detail in violation['details'][:3]:  # Show first 3 details
                            print(f"      * {detail}")
                        if len(violation['details']) > 3:
                            print(f"      * ... and {len(violation['details']) - 3} more")

                print(f"  RECOMMENDATION: {method_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo KISS violations detected! 🎉")
    else:
        print("\nKISS violations detected. Consider refactoring the flagged methods.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = KISSAnalyzer()

    if os.path.isfile(path):
        results = [analyzer.analyze_file(path)]
    elif os.path.isdir(path):
        results = analyze_directory(path, analyzer)
    else:
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    print_results(results)


if __name__ == "__main__":
    main()
