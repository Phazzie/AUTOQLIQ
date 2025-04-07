"""Interface Segregation Principle Analyzer.

This module provides an analyzer for detecting violations of the Interface Segregation Principle.
"""

import os
import ast
import logging
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

from ..base_analyzer import BaseAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ISPAnalyzer(BaseAnalyzer):
    """Analyzer for detecting violations of the Interface Segregation Principle.

    The Interface Segregation Principle states that clients should not be forced
    to depend on interfaces they do not use.

    This analyzer detects:
    - Large interfaces with many methods
    - Classes implementing interfaces but not using all methods
    - Interface methods with different client usage patterns
    - Interfaces with low cohesion
    """

    def __init__(self, config=None):
        """Initialize the ISP analyzer.

        Args:
            config: Optional configuration dictionary
        """
        name = "Interface Segregation Principle Analyzer"
        description = "Analyzer for detecting violations of the Interface Segregation Principle"
        super().__init__(name, description, config)
        self.principle = "ISP"
        self.class_violations = defaultdict(list)
        self.class_scores = {}
        self.overall_score = 1.0
        self.interfaces = {}
        self.implementations = defaultdict(list)

        # Configuration
        self.max_interface_methods = self.config.get('max_interface_methods', 5)  # Maximum number of methods an interface should have

    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a Python file for ISP violations.

        Args:
            file_path: Path to the Python file to analyze
            content: Content of the file
            tree: AST of the file

        Returns:
            Dict containing analysis results
        """
        # Initialize results
        results = {
            "file_path": file_path,
            "overall_isp_score": 1.0,
            "class_analysis": []
        }

        # First pass: identify interfaces and implementations
        self._identify_interfaces_and_implementations(tree)

        # Second pass: analyze each interface for ISP violations
        for interface_name, methods in self.interfaces.items():
            if len(methods) > self.max_interface_methods:
                # This interface has too many methods
                implementations = self.implementations.get(interface_name, [])

                # Check if implementations use all methods
                for impl_name in implementations:
                    class_result = self._analyze_implementation(impl_name, interface_name, methods)
                    results["class_analysis"].append(class_result)

        # Calculate overall score
        if results["class_analysis"]:
            total_score = sum(cls["isp_score"] for cls in results["class_analysis"])
            results["overall_isp_score"] = round(total_score / len(results["class_analysis"]), 2)

        self.overall_score = results["overall_isp_score"]
        return results

    def _identify_interfaces_and_implementations(self, tree: ast.AST) -> None:
        """Identify interfaces and their implementations.

        Args:
            tree: AST for the file
        """
        # Reset interfaces and implementations
        self.interfaces = {}
        self.implementations = defaultdict(list)

        # Find all classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name

                # Check if this is an interface
                if self._is_interface(node):
                    # Store interface methods
                    methods = []
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            methods.append(method.name)

                    self.interfaces[class_name] = methods
                else:
                    # Check if this class implements any interfaces
                    for base in node.bases:
                        base_name = self._get_name_from_node(base)
                        if base_name:
                            self.implementations[base_name].append(class_name)

    def _analyze_implementation(self, impl_name: str, interface_name: str, interface_methods: List[str]) -> Dict:
        """Analyze an implementation for ISP violations.

        Args:
            impl_name: Name of the implementation class
            interface_name: Name of the interface
            interface_methods: List of methods in the interface

        Returns:
            Dict containing analysis results for the implementation
        """
        violations = []

        # Check if the interface has too many methods
        if len(interface_methods) > self.max_interface_methods:
            violations.append({
                "type": "Interface has too many methods",
                "details": f"Interface '{interface_name}' has {len(interface_methods)} methods, exceeding the maximum of {self.max_interface_methods}",
                "location": f"Class {impl_name} implements {interface_name}"
            })

        # Calculate ISP score
        isp_score = 1.0
        if violations:
            # Deduct points for each violation
            isp_score = max(0.0, 1.0 - (len(violations) * 0.1))

        # Store results
        self.class_violations[impl_name] = violations
        self.class_scores[impl_name] = isp_score

        return {
            "class_name": impl_name,
            "isp_score": round(isp_score, 2),
            "implements": interface_name,
            "violations": violations,
            "recommendation": self._generate_recommendation(impl_name, violations, interface_name) if violations else ""
        }

    def _is_interface(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class appears to be an interface using standard Python patterns.

        Args:
            cls_node: AST node for the class

        Returns:
            True if the class appears to be an interface, False otherwise
        """
        # Check for ABC in bases (standard Python way to define abstract classes)
        for base in cls_node.bases:
            base_name = self._get_name_from_node(base)

            # Direct ABC inheritance
            if base_name in ["ABC", "Interface", "Abstract"]:
                return True

            # Check for module.ABC pattern
            if isinstance(base, ast.Attribute):
                if base.attr in ["ABC", "Interface", "Abstract"]:
                    return True

        # Check for @abstractmethod decorators (standard Python way to define abstract methods)
        has_abstract_method = False
        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Check for direct abstractmethod
                    decorator_name = self._get_name_from_node(decorator)
                    if decorator_name == "abstractmethod":
                        has_abstract_method = True
                        break

                    # Check for abc.abstractmethod or module.abstractmethod pattern
                    if isinstance(decorator, ast.Attribute):
                        if decorator.attr == "abstractmethod":
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

    def _get_name_from_node(self, node: ast.AST) -> Optional[str]:
        """Extract name from an AST node.

        Args:
            node: AST node

        Returns:
            Name extracted from the node, or None if not found
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _generate_recommendation(self, class_name: str, violations: List[Dict], interface_name: str) -> str:
        """Generate refactoring recommendations based on analysis.

        Args:
            class_name: Name of the class
            violations: List of violations
            interface_name: Name of the interface

        Returns:
            String containing recommendations
        """
        if not violations:
            return ""

        recommendations = [f"Class '{class_name}' has potential ISP violations:"]

        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            violation_types[violation["type"]].append(violation["details"])

        # Add recommendations for each violation type
        for violation_type, details_list in violation_types.items():
            for details in details_list:
                recommendations.append(f"- {details}")

            # Add specific recommendations based on violation type
            if "too many methods" in violation_type:
                recommendations.append(f"- Consider splitting interface '{interface_name}' into smaller, more focused interfaces.")
                recommendations.append("- Group methods by client usage patterns or functionality.")
                recommendations.append("- Use interface composition instead of large interfaces.")

        return "\n".join(recommendations)

    def print_results(self, results: Dict) -> None:
        """Print analysis results.

        Args:
            results: Analysis results
        """
        print("\n===== INTERFACE SEGREGATION PRINCIPLE ANALYSIS =====\n")
        print(f"File: {results['file_path']}")
        print(f"Overall ISP Score: {results['overall_isp_score']:.2f}/1.00\n")

        for cls in results["class_analysis"]:
            print(f"  Class: {cls['class_name']} {'✓' if cls['isp_score'] >= 0.8 else '✗'}")
            print(f"  ISP Score: {cls['isp_score']:.2f}/1.00")
            print(f"  Implements: {cls['implements']}")

            if cls["violations"]:
                print("  Violations:")

                # Group violations by type
                violation_types = defaultdict(list)
                for violation in cls["violations"]:
                    violation_types[violation["type"]].append(violation["details"])

                # Print each violation type
                for violation_type, details_list in violation_types.items():
                    print(f"    - {violation_type}")
                    for details in details_list:
                        print(f"      * {details}")

            if cls["recommendation"]:
                print(f"  RECOMMENDATION: {cls['recommendation']}")

            print()

        print("------------------------------------------------------------\n")

        if results["overall_isp_score"] < 1.0:
            print("ISP violations detected. Consider refactoring the flagged classes.")
        else:
            print("No ISP violations detected! 🎉")

    def get_summary(self) -> str:
        """Get a summary of the analysis results.

        Returns:
            String containing a summary of the analysis results
        """
        return f"ISP Score: {self.overall_score:.2f}/1.00"
