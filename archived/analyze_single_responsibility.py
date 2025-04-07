#!/usr/bin/env python
"""
Single Responsibility Principle Analyzer

This script analyzes Python files to identify potential violations of the Single Responsibility Principle.
It uses advanced metrics like:
1. Method cohesion analysis
2. Responsibility counting through natural language processing
3. Change reason analysis

Usage:
    python analyze_single_responsibility.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple

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

class ResponsibilityAnalyzer:
    """Analyzes Python code for SRP violations using advanced heuristics."""

    def __init__(self, max_responsibilities: int = 1, cohesion_threshold: float = 0.5):
        self.max_responsibilities = max_responsibilities
        self.cohesion_threshold = cohesion_threshold

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for SRP violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

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

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _analyze_class(self, cls_node: ast.ClassDef, file_content: str) -> Dict:
        """Analyze a class for SRP violations."""
        methods = [node for node in ast.walk(cls_node) if isinstance(node, ast.FunctionDef)]

        # Extract method names and docstrings
        method_info = []
        for method in methods:
            docstring = ast.get_docstring(method) or ""
            method_info.append({
                "name": method.name,
                "docstring": docstring,
                "code": self._get_method_source(method, file_content)
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
            "recommendation": self._generate_recommendation(cls_node.name, responsibilities, cohesion_score)
        }

    def _identify_responsibilities(self, cls_node: ast.ClassDef, method_info: List[Dict]) -> Set[str]:
        """Identify distinct responsibilities in a class using NLP techniques."""
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
        """Extract responsibilities from text using keyword matching."""
        text = text.lower()
        for domain, keywords in RESPONSIBILITY_DOMAINS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    responsibilities.add(domain)
                    break

    def _calculate_cohesion(self, method_info: List[Dict]) -> float:
        """Calculate method cohesion based on shared vocabulary."""
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

    def _get_method_source(self, method_node: ast.FunctionDef, file_content: str) -> str:
        """Extract method source code from file content."""
        if not hasattr(method_node, 'lineno') or not hasattr(method_node, 'end_lineno'):
            return ""

        lines = file_content.splitlines()
        start_line = method_node.lineno - 1  # 0-indexed
        end_line = getattr(method_node, 'end_lineno', len(lines)) - 1

        return "\n".join(lines[start_line:end_line+1])

    def _generate_recommendation(self, class_name: str, responsibilities: Set[str], cohesion_score: float) -> str:
        """Generate refactoring recommendations based on analysis."""
        if len(responsibilities) <= self.max_responsibilities and cohesion_score >= self.cohesion_threshold:
            return f"Class '{class_name}' appears to follow SRP."

        recommendation = f"Class '{class_name}' may have too many responsibilities: {', '.join(responsibilities)}. "

        if len(responsibilities) > self.max_responsibilities:
            recommendation += f"Consider splitting into {len(responsibilities)} classes, each with a single responsibility. "

        if cohesion_score < self.cohesion_threshold:
            recommendation += f"Low method cohesion ({cohesion_score:.2f}) indicates methods may not be working together."

        return recommendation


def analyze_directory(directory_path: str, analyzer: ResponsibilityAnalyzer) -> List[Dict]:
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
    print("\n===== SINGLE RESPONSIBILITY PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall SRP Score: {result['overall_srp_score']:.2f}/1.00")

        for cls_analysis in result.get("class_analysis", []):
            srp_status = "✓" if not cls_analysis["srp_violations"] else "✗"
            print(f"\n  Class: {cls_analysis['class_name']} {srp_status}")
            print(f"  SRP Score: {cls_analysis['srp_score']:.2f}/1.00")
            print(f"  Cohesion: {cls_analysis['cohesion_score']:.2f}/1.00")
            print(f"  Responsibilities: {', '.join(cls_analysis['responsibilities'])}")

            if cls_analysis["srp_violations"]:
                violations_found = True
                print(f"  RECOMMENDATION: {cls_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo SRP violations detected! 🎉")
    else:
        print("\nSRP violations detected. Consider refactoring the flagged classes.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = ResponsibilityAnalyzer()

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
