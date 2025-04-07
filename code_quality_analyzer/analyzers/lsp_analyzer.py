"""Liskov Substitution Principle Analyzer.

This module provides an analyzer for detecting violations of the Liskov Substitution Principle.
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

class LSPAnalyzer(BaseAnalyzer):
    """Analyzer for detecting violations of the Liskov Substitution Principle.

    The Liskov Substitution Principle states that objects of a superclass should be
    replaceable with objects of a subclass without affecting the correctness of the program.

    This analyzer detects:
    - Method signature changes in overrides
    - Precondition strengthening
    - Postcondition weakening
    - Exception type changes
    """

    def __init__(self, config=None):
        """Initialize the LSP analyzer.

        Args:
            config: Optional configuration dictionary
        """
        name = "Liskov Substitution Principle Analyzer"
        description = "Analyzer for detecting violations of the Liskov Substitution Principle"
        super().__init__(name, description, config)
        self.principle = "LSP"
        self.class_violations = defaultdict(list)
        self.class_scores = {}
        self.overall_score = 1.0
        self.class_hierarchy = {}
        self.method_signatures = {}

    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a Python file for LSP violations.

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
            "overall_lsp_score": 1.0,
            "class_analysis": []
        }

        # First pass: build class hierarchy and method signatures
        self._build_class_hierarchy(tree)

        # Second pass: analyze each class for LSP violations
        for class_name, bases in self.class_hierarchy.items():
            if bases:  # Only analyze classes that extend other classes
                class_node = self._find_class_node(tree, class_name)
                if class_node:
                    class_result = self._analyze_class(class_node, bases)
                    results["class_analysis"].append(class_result)

        # Calculate overall score
        if results["class_analysis"]:
            total_score = sum(cls["lsp_score"] for cls in results["class_analysis"])
            results["overall_lsp_score"] = round(total_score / len(results["class_analysis"]), 2)

        self.overall_score = results["overall_lsp_score"]
        return results

    def _build_class_hierarchy(self, tree: ast.AST) -> None:
        """Build the class hierarchy and method signatures.

        Args:
            tree: AST for the file
        """
        # Reset class hierarchy and method signatures
        self.class_hierarchy = {}
        self.method_signatures = {}

        # Find all classes and their base classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                bases = []

                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)

                self.class_hierarchy[class_name] = bases

                # Store method signatures for this class
                self.method_signatures[class_name] = {}

                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        method_name = method.name

                        # Skip special methods
                        if method_name.startswith("__") and method_name.endswith("__"):
                            continue

                        # Get parameter types
                        param_types = []
                        for arg in method.args.args:
                            if arg.annotation:
                                param_types.append(self._get_annotation_name(arg.annotation))
                            else:
                                param_types.append("unknown")

                        # Get return type
                        return_type = "unknown"
                        if method.returns:
                            return_type = self._get_annotation_name(method.returns)

                        # Get exceptions raised
                        exceptions = self._find_exceptions(method)

                        # Store method signature
                        self.method_signatures[class_name][method_name] = {
                            "params": param_types,
                            "return": return_type,
                            "exceptions": exceptions
                        }

    def _find_class_node(self, tree: ast.AST, class_name: str) -> Optional[ast.ClassDef]:
        """Find the AST node for a class.

        Args:
            tree: AST for the file
            class_name: Name of the class to find

        Returns:
            AST node for the class, or None if not found
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None

    def _analyze_class(self, cls_node: ast.ClassDef, bases: List[str]) -> Dict:
        """Analyze a class for LSP violations.

        Args:
            cls_node: AST node for the class
            bases: List of base class names

        Returns:
            Dict containing analysis results for the class
        """
        class_name = cls_node.name
        violations = []

        # Check each method for LSP violations
        for method in cls_node.body:
            if isinstance(method, ast.FunctionDef):
                method_name = method.name

                # Skip special methods
                if method_name.startswith("__") and method_name.endswith("__"):
                    continue

                # Check if this method overrides a method in a base class
                for base in bases:
                    if base in self.method_signatures and method_name in self.method_signatures[base]:
                        # Check for LSP violations
                        method_violations = self._check_method_override(
                            class_name, method_name, base, method
                        )
                        violations.extend(method_violations)

        # Calculate LSP score
        lsp_score = 1.0
        if violations:
            # Deduct points for each violation
            lsp_score = max(0.0, 1.0 - (len(violations) * 0.1))

        # Store results
        self.class_violations[class_name] = violations
        self.class_scores[class_name] = lsp_score

        return {
            "class_name": class_name,
            "lsp_score": round(lsp_score, 2),
            "extends": ", ".join(bases),
            "violations": violations,
            "recommendation": self._generate_recommendation(class_name, violations, bases) if violations else ""
        }

    def _check_method_override(self, class_name: str, method_name: str, base_name: str, method_node: ast.FunctionDef) -> List[Dict]:
        """Check if a method override violates LSP.

        Args:
            class_name: Name of the class
            method_name: Name of the method
            base_name: Name of the base class
            method_node: AST node for the method

        Returns:
            List of LSP violations
        """
        violations = []
        base_signature = self.method_signatures[base_name][method_name]

        # Check parameter types
        param_types = []
        for arg in method_node.args.args:
            if arg.annotation:
                param_types.append(self._get_annotation_name(arg.annotation))
            else:
                param_types.append("unknown")

        # Check return type
        return_type = "unknown"
        if method_node.returns:
            return_type = self._get_annotation_name(method_node.returns)

        # Check exceptions raised
        exceptions = self._find_exceptions(method_node)

        # Check for parameter type changes
        if len(param_types) != len(base_signature["params"]):
            violations.append({
                "type": "Method override changes parameter count",
                "details": f"Base: {len(base_signature['params'])} params, Override: {len(param_types)} params",
                "location": f"Line {method_node.lineno} in {class_name}"
            })

        # Check for return type changes
        if return_type != base_signature["return"] and base_signature["return"] != "unknown" and return_type != "unknown":
            violations.append({
                "type": "Method override changes return type",
                "details": f"Base: {base_signature['return']}, Override: {return_type}",
                "location": f"Line {method_node.lineno} in {class_name}"
            })

        # Check for new exceptions
        new_exceptions = [exc for exc in exceptions if exc not in base_signature["exceptions"]]
        if new_exceptions:
            violations.append({
                "type": "Method override violates LSP in method '{}'".format(method_name),
                "details": f"New exceptions: {', '.join(new_exceptions)}",
                "location": f"Line {method_node.lineno} in {class_name}"
            })

        return violations

    def _find_exceptions(self, method_node: ast.FunctionDef) -> List[str]:
        """Find exceptions raised in a method.

        Args:
            method_node: AST node for the method

        Returns:
            List of exception names
        """
        exceptions = []

        for node in ast.walk(method_node):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call):
                    if isinstance(node.exc.func, ast.Name):
                        exceptions.append(node.exc.func.id)
                    elif isinstance(node.exc.func, ast.Attribute):
                        exceptions.append(node.exc.func.attr)
                elif isinstance(node.exc, ast.Name):
                    exceptions.append(node.exc.id)

        return exceptions

    def _get_annotation_name(self, annotation: ast.AST) -> str:
        """Extract the name from a type annotation.

        Args:
            annotation: AST node for the annotation

        Returns:
            Name of the annotation
        """
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id
        elif isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            # For string literal annotations like "int"
            return annotation.value
        elif hasattr(ast, 'Str') and isinstance(annotation, ast.Str):
            # For Python < 3.8
            return annotation.s
        return "unknown"

    def _generate_recommendation(self, class_name: str, violations: List[Dict], bases: List[str]) -> str:
        """Generate refactoring recommendations based on analysis.

        Args:
            class_name: Name of the class
            violations: List of violations
            bases: List of base class names

        Returns:
            String containing recommendations
        """
        if not violations:
            return ""

        recommendations = [f"Class '{class_name}' has potential LSP violations:"]

        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            key = f"{violation['type']} when extending '{bases[0]}'"
            details = f"  * {violation['details']}\n  * {violation['location']}"
            violation_types[key].append(details)

        # Add recommendations for each violation type
        for violation_type, details_list in violation_types.items():
            recommendations.append(f"- {violation_type}.")
            for details in details_list:
                recommendations.append(details)

            # Add specific recommendations based on violation type
            if "parameter count" in violation_type:
                recommendations.append("  * Consider maintaining the same method signature as the base class.")
            elif "return type" in violation_type:
                recommendations.append("  * Return types in overridden methods should be covariant (same or more specific).")
            elif "exceptions" in violation_type:
                recommendations.append("  * Consider maintaining the same method signature and behavior contract as the base class.")

            recommendations.append("  * Ensure derived classes can be used anywhere base classes are used without changing behavior.")

        return "\n".join(recommendations)

    def print_results(self, results: Dict) -> None:
        """Print analysis results.

        Args:
            results: Analysis results
        """
        print("\n===== LISKOV SUBSTITUTION PRINCIPLE ANALYSIS =====\n")
        print(f"File: {results['file_path']}")
        print(f"Overall LSP Score: {results['overall_lsp_score']:.2f}/1.00\n")

        for cls in results["class_analysis"]:
            print(f"  Class: {cls['class_name']} {'✓' if cls['lsp_score'] >= 0.8 else '✗'}")
            print(f"  LSP Score: {cls['lsp_score']:.2f}/1.00")
            print(f"  Extends: {cls['extends']}")

            if cls["violations"]:
                print("  Violations:")

                # Group violations by type
                violation_types = defaultdict(list)
                for violation in cls["violations"]:
                    key = violation["type"]
                    details = f"{violation['details']}\n      * {violation['location']}"
                    violation_types[key].append(details)

                # Print each violation type
                for violation_type, details_list in violation_types.items():
                    print(f"    - {violation_type}")
                    for details in details_list:
                        print(f"      * {details}")

            if cls["recommendation"]:
                print(f"  RECOMMENDATION: {cls['recommendation']}")

            print()

        print("------------------------------------------------------------\n")

        if results["overall_lsp_score"] < 1.0:
            print("LSP violations detected. Consider refactoring the flagged classes.")
        else:
            print("No LSP violations detected! 🎉")

    def get_summary(self) -> str:
        """Get a summary of the analysis results.

        Returns:
            String containing a summary of the analysis results
        """
        return f"LSP Score: {self.overall_score:.2f}/1.00"
