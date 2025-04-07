#!/usr/bin/env python
"""
Open/Closed Principle Analyzer

This script analyzes Python files to identify potential violations of the Open/Closed Principle.
It detects patterns that make code difficult to extend without modification, including:
1. Switch/if-else chains based on type
2. Lack of abstraction/interfaces
3. Concrete class dependencies
4. Hardcoded behavior that should be extensible

Usage:
    python analyze_open_closed.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
from typing import Dict, List, Set, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OpenClosedAnalyzer:
    """Analyzes Python code for Open/Closed Principle violations."""

    def __init__(self):
        self.inheritance_graph = {}  # Track class inheritance
        self.interface_classes = set()  # Classes that appear to be interfaces/abstract
        self.concrete_classes = set()  # Concrete implementation classes

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for OCP violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # First pass: identify classes and build inheritance graph
            self._build_inheritance_graph(tree)

            # Second pass: analyze for OCP violations
            results = {
                "file_path": file_path,
                "class_analysis": [],
                "overall_ocp_score": 1.0  # Will be updated based on class analyses
            }

            # Find all classes in the file
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            for cls in classes:
                class_result = self._analyze_class(cls, content)
                results["class_analysis"].append(class_result)

            # Calculate overall OCP score for the file
            if results["class_analysis"]:
                avg_score = sum(c["ocp_score"] for c in results["class_analysis"]) / len(results["class_analysis"])
                results["overall_ocp_score"] = avg_score

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _build_inheritance_graph(self, tree: ast.AST) -> None:
        """Build a graph of class inheritance relationships."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get base classes
                bases = [base.id if isinstance(base, ast.Name) else
                         base.attr if isinstance(base, ast.Attribute) else
                         "unknown" for base in node.bases]

                self.inheritance_graph[node.name] = bases

                # Check if this is an interface/abstract class
                if self._is_interface_class(node):
                    self.interface_classes.add(node.name)
                else:
                    self.concrete_classes.add(node.name)

    def _is_interface_class(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class appears to be an interface or abstract class."""
        # Check for ABC in bases (standard Python way to define abstract classes)
        for base in cls_node.bases:
            if isinstance(base, ast.Name) and base.id in ["ABC", "Interface", "Abstract"]:
                return True
            elif isinstance(base, ast.Attribute) and base.attr in ["ABC", "Interface", "Abstract"]:
                return True

        # Check for @abstractmethod decorators (standard Python way to define abstract methods)
        has_abstract_method = False
        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Check for direct abstractmethod
                    if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                        has_abstract_method = True
                        break

                    # Check for abc.abstractmethod or module.abstractmethod pattern
                    if isinstance(decorator, ast.Attribute) and decorator.attr == "abstractmethod":
                        has_abstract_method = True
                        break

                if has_abstract_method:
                    break

        if has_abstract_method:
            return True

        # Check naming conventions (less reliable but common in some codebases)
        # Interface naming convention (IInterface)
        if cls_node.name.startswith("I") and len(cls_node.name) > 1 and cls_node.name[1].isupper():
            return True

        # Abstract/Interface in name
        if "Interface" in cls_node.name or "Abstract" in cls_node.name:
            return True

        # Check if the class has any abstract methods but no implementation
        # This is a heuristic for detecting abstract classes without explicit markers
        method_count = 0
        empty_method_count = 0

        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef):
                method_count += 1

                # Check if method body only contains 'pass' or docstring
                if len(node.body) <= 1:
                    if len(node.body) == 0 or (
                        len(node.body) == 1 and (
                            isinstance(node.body[0], ast.Pass) or
                            isinstance(node.body[0], ast.Expr) and (
                                isinstance(node.body[0].value, ast.Str) if hasattr(ast, 'Str') else
                                isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)
                            )
                        )
                    ):
                        empty_method_count += 1

        # If all methods are empty and there's at least one method, it's likely abstract
        if method_count > 0 and method_count == empty_method_count:
            return True

        return False

    def _analyze_class(self, cls_node: ast.ClassDef, file_content: str) -> Dict:
        """Analyze a class for OCP violations."""
        violations = []

        # Check for type checking and conditional behavior
        type_checking = self._find_type_checking(cls_node)
        if type_checking:
            violations.append({
                "type": "type_checking",
                "description": "Type checking with conditionals instead of polymorphism",
                "locations": type_checking
            })

        # Check for direct instantiation of concrete classes
        concrete_instantiations = self._find_concrete_instantiations(cls_node)
        if concrete_instantiations:
            violations.append({
                "type": "concrete_instantiation",
                "description": "Direct instantiation of concrete classes instead of using factories or DI",
                "locations": concrete_instantiations
            })

        # Check for hardcoded behavior that should be extensible
        hardcoded_behavior = self._find_hardcoded_behavior(cls_node)
        if hardcoded_behavior:
            violations.append({
                "type": "hardcoded_behavior",
                "description": "Hardcoded behavior that should be extensible",
                "locations": hardcoded_behavior
            })

        # Calculate OCP score (1.0 is perfect, 0.0 is worst)
        # Each violation type reduces score by 0.2
        ocp_score = max(0.0, 1.0 - (len(violations) * 0.2))

        # Check if class extends an interface/abstract class
        implements_interface = any(base in self.interface_classes for base in self.inheritance_graph.get(cls_node.name, []))
        if implements_interface:
            ocp_score = min(1.0, ocp_score + 0.1)  # Bonus for implementing interfaces

        return {
            "class_name": cls_node.name,
            "violations": violations,
            "ocp_score": ocp_score,
            "implements_interface": implements_interface,
            "recommendation": self._generate_recommendation(cls_node.name, violations, implements_interface)
        }

    def _find_type_checking(self, cls_node: ast.ClassDef) -> List[str]:
        """Find instances of type checking with conditionals."""
        type_checks = []

        for node in ast.walk(cls_node):
            # Check for isinstance() calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "isinstance":
                type_checks.append(f"isinstance() check at line {node.lineno}")

            # Check for type() comparisons
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "type":
                type_checks.append(f"type() check at line {node.lineno}")

            # Check for if-elif chains with type checking
            elif isinstance(node, ast.If):
                # Look for patterns like: if obj.__class__.__name__ == "ClassName":
                test = node.test
                if isinstance(test, ast.Compare):
                    left = test.left
                    if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Attribute):
                        if left.attr == "__name__" and left.value.attr == "__class__":
                            type_checks.append(f"Class name check at line {node.lineno}")

        return type_checks

    def _find_concrete_instantiations(self, cls_node: ast.ClassDef) -> List[str]:
        """Find instances of direct instantiation of concrete classes."""
        instantiations = []

        for node in ast.walk(cls_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                class_name = node.func.id
                if class_name in self.concrete_classes and class_name != cls_node.name:  # Exclude self instantiation
                    instantiations.append(f"Direct instantiation of {class_name} at line {node.lineno}")

        return instantiations

    def _find_hardcoded_behavior(self, cls_node: ast.ClassDef) -> List[str]:
        """Find instances of hardcoded behavior that should be extensible."""
        hardcoded = []

        for node in ast.walk(cls_node):
            # Check for large if-elif-else chains
            if isinstance(node, ast.If):
                chain_length = self._count_if_chain(node)
                if chain_length >= 3:  # Arbitrary threshold
                    hardcoded.append(f"If-elif chain with {chain_length} conditions at line {node.lineno}")

            # Check for large match/case statements (Python 3.10+)
            elif hasattr(ast, 'Match') and isinstance(node, getattr(ast, 'Match')):
                if len(node.cases) >= 3:  # Arbitrary threshold
                    hardcoded.append(f"Match statement with {len(node.cases)} cases at line {node.lineno}")

        return hardcoded

    def _count_if_chain(self, if_node: ast.If) -> int:
        """Count the length of an if-elif-else chain."""
        count = 1  # Start with 1 for the initial if

        # Count elif branches
        current = if_node
        while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            count += 1
            current = current.orelse[0]

        # Count final else if present
        if current.orelse:
            count += 1

        return count

    def _generate_recommendation(self, class_name: str, violations: List[Dict], implements_interface: bool) -> str:
        """Generate refactoring recommendations based on analysis."""
        if not violations:
            if implements_interface:
                return f"Class '{class_name}' follows OCP by implementing an interface/abstract class."
            else:
                return f"Class '{class_name}' appears to follow OCP, but consider defining interfaces."

        recommendations = [f"Class '{class_name}' has potential OCP violations:"]

        for violation in violations:
            if violation["type"] == "type_checking":
                recommendations.append("- Replace type checking with polymorphism. Create a common interface with different implementations.")

            elif violation["type"] == "concrete_instantiation":
                recommendations.append("- Use dependency injection or factory pattern instead of directly instantiating concrete classes.")

            elif violation["type"] == "hardcoded_behavior":
                recommendations.append("- Replace conditional logic with polymorphic behavior through strategy pattern or command pattern.")

        if not implements_interface:
            recommendations.append("- Consider implementing or extending an interface/abstract class to better follow OCP.")

        return " ".join(recommendations)


def analyze_directory(directory_path: str, analyzer: OpenClosedAnalyzer) -> List[Dict]:
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
    print("\n===== OPEN/CLOSED PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall OCP Score: {result['overall_ocp_score']:.2f}/1.00")

        for cls_analysis in result.get("class_analysis", []):
            ocp_status = "✓" if cls_analysis["ocp_score"] >= 0.8 else "✗"
            print(f"\n  Class: {cls_analysis['class_name']} {ocp_status}")
            print(f"  OCP Score: {cls_analysis['ocp_score']:.2f}/1.00")

            if cls_analysis["violations"]:
                violations_found = True
                print("  Violations:")
                for violation in cls_analysis["violations"]:
                    print(f"    - {violation['description']}")
                    for location in violation['locations'][:3]:  # Show first 3 locations
                        print(f"      * {location}")
                    if len(violation['locations']) > 3:
                        print(f"      * ... and {len(violation['locations']) - 3} more")

                print(f"  RECOMMENDATION: {cls_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo OCP violations detected! 🎉")
    else:
        print("\nOCP violations detected. Consider refactoring the flagged classes.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = OpenClosedAnalyzer()

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
