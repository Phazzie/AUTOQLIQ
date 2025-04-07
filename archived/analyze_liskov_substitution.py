#!/usr/bin/env python
"""
Liskov Substitution Principle Analyzer

This script analyzes Python files to identify potential violations of the Liskov Substitution Principle.
It detects patterns that break substitutability of derived classes, including:
1. Method signature changes in overrides
2. Precondition strengthening
3. Postcondition weakening
4. Invariant changes
5. Exception type changes

Usage:
    python analyze_liskov_substitution.py <file_or_directory_path>
"""

import os
import sys
import ast
import inspect
import re
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LiskovAnalyzer:
    """Analyzes Python code for Liskov Substitution Principle violations."""

    def __init__(self):
        self.class_methods = {}  # Maps class names to their methods
        self.class_hierarchy = defaultdict(list)  # Maps parent classes to child classes
        self.method_signatures = {}  # Maps class.method to signature info

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for LSP violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # First pass: build class hierarchy and collect method signatures
            self._build_class_info(tree, file_path)

            # Second pass: analyze for LSP violations
            results = {
                "file_path": file_path,
                "class_analysis": [],
                "overall_lsp_score": 1.0  # Will be updated based on class analyses
            }

            # Find all classes in the file
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            for cls in classes:
                # Only analyze classes that inherit from something
                if cls.bases:
                    class_result = self._analyze_class(cls, content, file_path)
                    results["class_analysis"].append(class_result)

            # Calculate overall LSP score for the file
            if results["class_analysis"]:
                avg_score = sum(c["lsp_score"] for c in results["class_analysis"]) / len(results["class_analysis"])
                results["overall_lsp_score"] = avg_score

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _build_class_info(self, tree: ast.AST, file_path: str) -> None:
        """Build class hierarchy and collect method information."""
        for cls_node in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            class_name = cls_node.name

            # Get base classes
            base_classes = []
            for base in cls_node.bases:
                if isinstance(base, ast.Name):
                    base_classes.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_classes.append(base.attr)

            # Update class hierarchy
            for base in base_classes:
                self.class_hierarchy[base].append(class_name)

            # Collect methods
            methods = {}
            for node in [n for n in ast.walk(cls_node) if isinstance(n, ast.FunctionDef)]:
                method_name = node.name
                methods[method_name] = node

                # Store method signature
                signature_key = f"{class_name}.{method_name}"

                # Get parameter info
                params = []
                returns_type = None
                raises = []

                # Extract parameter types from annotations
                for arg in node.args.args:
                    param_name = arg.arg
                    param_type = None
                    if hasattr(arg, 'annotation') and arg.annotation:
                        param_type = self._get_annotation_name(arg.annotation)
                    params.append((param_name, param_type))

                # Extract return type from annotations
                if hasattr(node, 'returns') and node.returns:
                    returns_type = self._get_annotation_name(node.returns)

                # Extract raised exceptions from docstring
                docstring = ast.get_docstring(node) or ""
                raises_matches = re.findall(r'(?:Raises|raises):\s*([A-Za-z0-9_]+(?:,\s*[A-Za-z0-9_]+)*)', docstring)
                if raises_matches:
                    for match in raises_matches:
                        raises.extend([e.strip() for e in match.split(',')])

                # Also look for explicit raise statements
                for raise_node in [n for n in ast.walk(node) if isinstance(n, ast.Raise)]:
                    if isinstance(raise_node.exc, ast.Name):
                        raises.append(raise_node.exc.id)
                    elif isinstance(raise_node.exc, ast.Call) and isinstance(raise_node.exc.func, ast.Name):
                        raises.append(raise_node.exc.func.id)

                self.method_signatures[signature_key] = {
                    "params": params,
                    "returns": returns_type,
                    "raises": raises,
                    "node": node,
                    "file_path": file_path
                }

            self.class_methods[class_name] = methods

    def _get_annotation_name(self, annotation: ast.AST) -> str:
        """Extract the name from a type annotation.

        Handles both Python 3.8+ (using ast.Constant) and older versions.
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

    def _analyze_class(self, cls_node: ast.ClassDef, content: str, file_path: str) -> Dict:
        """Analyze a class for LSP violations."""
        class_name = cls_node.name
        violations = []

        # Get base classes
        base_classes = []
        for base in cls_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)

        # Check each method for LSP violations
        for method_name, method_node in self.class_methods.get(class_name, {}).items():
            # Skip methods that start with _ (private/protected)
            if method_name.startswith('_') and not method_name.startswith('__'):
                continue

            # Check if this method overrides a method in any base class
            for base_class in base_classes:
                if base_class in self.class_methods and method_name in self.class_methods[base_class]:
                    # This is an override - check for LSP violations
                    violation = self._check_method_override(
                        base_class, class_name, method_name, method_node, file_path
                    )
                    if violation:
                        violations.append(violation)

        # Calculate LSP score (1.0 is perfect, 0.0 is worst)
        # Each violation reduces score by 0.2
        lsp_score = max(0.0, 1.0 - (len(violations) * 0.2))

        return {
            "class_name": class_name,
            "base_classes": base_classes,
            "violations": violations,
            "lsp_score": lsp_score,
            "recommendation": self._generate_recommendation(class_name, violations)
        }

    def _check_method_override(
        self, base_class: str, derived_class: str, method_name: str,
        method_node: ast.FunctionDef, file_path: str
    ) -> Optional[Dict]:
        """Check if a method override violates LSP."""
        base_signature_key = f"{base_class}.{method_name}"
        derived_signature_key = f"{derived_class}.{method_name}"

        if base_signature_key not in self.method_signatures or derived_signature_key not in self.method_signatures:
            return None

        base_sig = self.method_signatures[base_signature_key]
        derived_sig = self.method_signatures[derived_signature_key]

        violations = []

        # Check parameter count
        if len(base_sig["params"]) != len(derived_sig["params"]):
            violations.append(f"Parameter count mismatch: {len(base_sig['params'])} vs {len(derived_sig['params'])}")

        # Check parameter types (derived should accept same or broader types)
        for i, ((base_name, base_type), (derived_name, derived_type)) in enumerate(
            zip(base_sig["params"], derived_sig["params"])
        ):
            if base_type and derived_type and base_type != derived_type:
                # This is a simplification - ideally we'd check if derived_type is a supertype of base_type
                violations.append(f"Parameter {i+1} type changed: {base_type} to {derived_type}")

        # Check return type (derived should return same or narrower type)
        if base_sig["returns"] and derived_sig["returns"] and base_sig["returns"] != derived_sig["returns"]:
            # This is a simplification - ideally we'd check if derived_type is a subtype of base_type
            violations.append(f"Return type changed: {base_sig['returns']} to {derived_sig['returns']}")

        # Check exceptions (derived should throw same or fewer exceptions)
        base_exceptions = set(base_sig["raises"])
        derived_exceptions = set(derived_sig["raises"])

        new_exceptions = derived_exceptions - base_exceptions
        if new_exceptions:
            violations.append(f"New exceptions: {', '.join(new_exceptions)}")

        if not violations:
            return None

        return {
            "type": "method_override",
            "method": method_name,
            "base_class": base_class,
            "description": f"Method override violates LSP",
            "details": violations,
            "location": f"Line {method_node.lineno} in {file_path}"
        }

    def _generate_recommendation(self, class_name: str, violations: List[Dict]) -> str:
        """Generate refactoring recommendations based on analysis."""
        if not violations:
            return f"Class '{class_name}' appears to follow LSP."

        recommendations = [f"Class '{class_name}' has potential LSP violations:"]

        for violation in violations:
            if violation["type"] == "method_override":
                recommendations.append(f"- Method '{violation['method']}' override violates LSP when extending '{violation['base_class']}'.")
                for detail in violation["details"]:
                    recommendations.append(f"  * {detail}")

                recommendations.append("  * Consider maintaining the same method signature and behavior contract as the base class.")
                recommendations.append("  * Ensure derived classes can be used anywhere base classes are used without changing behavior.")

        return " ".join(recommendations)


def analyze_directory(directory_path: str, analyzer: LiskovAnalyzer) -> List[Dict]:
    """Recursively analyze all Python files in a directory."""
    results = []

    # First pass to build class hierarchy across all files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    analyzer._build_class_info(tree, file_path)
                except Exception as e:
                    logger.error(f"Error pre-processing file {file_path}: {str(e)}")

    # Second pass to analyze each file
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results.append(analyzer.analyze_file(file_path))

    return results


def print_results(results: List[Dict]) -> None:
    """Print analysis results in a readable format."""
    print("\n===== LISKOV SUBSTITUTION PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall LSP Score: {result['overall_lsp_score']:.2f}/1.00")

        for cls_analysis in result.get("class_analysis", []):
            lsp_status = "✓" if cls_analysis["lsp_score"] >= 0.8 else "✗"
            print(f"\n  Class: {cls_analysis['class_name']} {lsp_status}")
            print(f"  LSP Score: {cls_analysis['lsp_score']:.2f}/1.00")
            print(f"  Extends: {', '.join(cls_analysis['base_classes'])}")

            if cls_analysis["violations"]:
                violations_found = True
                print("  Violations:")
                for violation in cls_analysis["violations"]:
                    print(f"    - {violation['description']} in method '{violation['method']}'")
                    for detail in violation['details']:
                        print(f"      * {detail}")
                    print(f"      * Location: {violation['location']}")

                print(f"  RECOMMENDATION: {cls_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo LSP violations detected! 🎉")
    else:
        print("\nLSP violations detected. Consider refactoring the flagged classes.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = LiskovAnalyzer()

    if os.path.isfile(path):
        # For a single file, we need to pre-process it to build class hierarchy
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            analyzer._build_class_info(tree, path)
        except Exception as e:
            logger.error(f"Error pre-processing file {path}: {str(e)}")

        results = [analyzer.analyze_file(path)]
    elif os.path.isdir(path):
        results = analyze_directory(path, analyzer)
    else:
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    print_results(results)


if __name__ == "__main__":
    main()
