"""Open/Closed Principle Analyzer.

This module provides an analyzer for detecting violations of the Open/Closed Principle.
"""

import os
import ast
import re
import logging
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

from ..base_analyzer import BaseAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OCPAnalyzer(BaseAnalyzer):
    """Analyzer for detecting violations of the Open/Closed Principle.

    The Open/Closed Principle states that software entities (classes, modules, functions, etc.)
    should be open for extension, but closed for modification.

    This analyzer detects:
    - Type checking with conditionals
    - Switch/if-else chains based on type
    - Concrete class instantiations
    - Hardcoded behavior that should be extensible
    """

    def __init__(self, config=None):
        """Initialize the OCP analyzer.

        Args:
            config: Optional configuration dictionary
        """
        name = "Open/Closed Principle Analyzer"
        description = "Analyzer for detecting violations of the Open/Closed Principle"
        super().__init__(name, description, config)
        self.principle = "OCP"
        self.class_violations = defaultdict(list)
        self.class_scores = {}
        self.overall_score = 1.0

    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a Python file for OCP violations.

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
            "overall_ocp_score": 1.0,
            "class_analysis": []
        }

        # Analyze each class in the file
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_result = self._analyze_class(node, file_path)
                results["class_analysis"].append(class_result)

        # Calculate overall score
        if results["class_analysis"]:
            total_score = sum(cls["ocp_score"] for cls in results["class_analysis"])
            results["overall_ocp_score"] = round(total_score / len(results["class_analysis"]), 2)

        self.overall_score = results["overall_ocp_score"]
        return results

    def _analyze_class(self, cls_node: ast.ClassDef, file_path: str) -> Dict:
        """Analyze a class for OCP violations.

        Args:
            cls_node: AST node for the class
            file_path: Path to the file containing the class

        Returns:
            Dict containing analysis results for the class
        """
        class_name = cls_node.name
        violations = []

        # Check for type checking with conditionals
        type_checking = self._find_type_checking(cls_node)
        if type_checking:
            violations.extend(type_checking)

        # Check for concrete class instantiations
        concrete_instantiations = self._find_concrete_instantiations(cls_node)
        if concrete_instantiations:
            violations.extend(concrete_instantiations)

        # Check if the class is an interface/abstract class
        is_interface = self._is_interface_class(cls_node)

        # Calculate OCP score
        ocp_score = 1.0
        if violations:
            # Deduct points for each violation
            ocp_score = max(0.0, 1.0 - (len(violations) * 0.1))

        # Store results
        self.class_violations[class_name] = violations
        self.class_scores[class_name] = ocp_score

        return {
            "class_name": class_name,
            "ocp_score": round(ocp_score, 2),
            "is_interface": is_interface,
            "violations": violations,
            "recommendation": self._generate_recommendation(class_name, violations) if violations else ""
        }

    def _is_interface_class(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class appears to be an interface or abstract class.

        Args:
            cls_node: AST node for the class

        Returns:
            True if the class appears to be an interface or abstract class, False otherwise
        """
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

    def _find_type_checking(self, cls_node: ast.ClassDef) -> List[Dict]:
        """Find instances of type checking with conditionals.

        Args:
            cls_node: AST node for the class

        Returns:
            List of type checking violations
        """
        violations = []

        for node in ast.walk(cls_node):
            # Check for isinstance() calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "isinstance":
                violations.append({
                    "type": "Type checking with isinstance()",
                    "location": f"Line {node.lineno}"
                })

            # Check for type() calls
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "type":
                violations.append({
                    "type": "Type checking with type()",
                    "location": f"Line {node.lineno}"
                })

            # Check for if-elif chains
            elif isinstance(node, ast.If):
                chain_length = 1
                current = node

                # Count the length of the if-elif chain
                while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                    chain_length += 1
                    current = current.orelse[0]

                if chain_length >= 3:
                    violations.append({
                        "type": "If-elif chain with {} conditions".format(chain_length),
                        "location": f"Line {node.lineno}"
                    })

        return violations

    def _find_concrete_instantiations(self, cls_node: ast.ClassDef) -> List[Dict]:
        """Find instances of concrete class instantiations.

        Args:
            cls_node: AST node for the class

        Returns:
            List of concrete instantiation violations
        """
        violations = []

        for node in ast.walk(cls_node):
            # Check for direct instantiations in __init__ method
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name):
                        # Skip common built-in types
                        if subnode.func.id not in ["list", "dict", "set", "tuple", "int", "float", "str", "bool"]:
                            violations.append({
                                "type": "Direct instantiation of concrete classes instead of using factories or DI",
                                "location": f"Line {subnode.lineno}"
                            })

        return violations

    def _generate_recommendation(self, class_name: str, violations: List[Dict]) -> str:
        """Generate refactoring recommendations based on analysis.

        Args:
            class_name: Name of the class
            violations: List of violations

        Returns:
            String containing recommendations
        """
        if not violations:
            return ""

        recommendations = [f"Class '{class_name}' has potential OCP violations:"]

        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            violation_types[violation["type"]].append(violation["location"])

        # Add recommendations for each violation type
        for violation_type, locations in violation_types.items():
            recommendations.append(f"  - {violation_type}")
            for location in locations:
                recommendations.append(f"    * {location}")

        # Add general recommendations
        if any("Type checking" in vtype for vtype in violation_types.keys()):
            recommendations.append("  - Replace conditional logic with polymorphic behavior through strategy pattern or command pattern.")

        if any("Direct instantiation" in vtype for vtype in violation_types.keys()):
            recommendations.append("  - Use dependency injection or factory pattern instead of directly instantiating concrete classes.")

        if any("If-elif chain" in vtype for vtype in violation_types.keys()):
            recommendations.append("  - Consider using polymorphism or the strategy pattern to handle different types.")

        recommendations.append("  - Consider implementing or extending an interface/abstract class to better follow OCP.")

        return "\n".join(recommendations)

    def print_results(self, results: Dict) -> None:
        """Print analysis results.

        Args:
            results: Analysis results
        """
        print("\n===== OPEN/CLOSED PRINCIPLE ANALYSIS =====\n")
        print(f"File: {results['file_path']}")
        print(f"Overall OCP Score: {results['overall_ocp_score']:.2f}/1.00\n")

        for cls in results["class_analysis"]:
            print(f"  Class: {cls['class_name']} {'✓' if cls['ocp_score'] >= 0.8 else '✗'}")
            print(f"  OCP Score: {cls['ocp_score']:.2f}/1.00")

            if cls["violations"]:
                print("  Violations:")

                # Group violations by type
                violation_types = defaultdict(list)
                for violation in cls["violations"]:
                    violation_types[violation["type"]].append(violation["location"])

                # Print each violation type
                for violation_type, locations in violation_types.items():
                    print(f"    - {violation_type}")
                    for location in locations:
                        print(f"      * {location}")

            if cls["recommendation"]:
                print(f"  RECOMMENDATION: {cls['recommendation']}")

            print()

        print("------------------------------------------------------------\n")

        if results["overall_ocp_score"] < 1.0:
            print("OCP violations detected. Consider refactoring the flagged classes.")
        else:
            print("No OCP violations detected! 🎉")

    def get_summary(self) -> str:
        """Get a summary of the analysis results.

        Returns:
            String containing a summary of the analysis results
        """
        return f"OCP Score: {self.overall_score:.2f}/1.00"
