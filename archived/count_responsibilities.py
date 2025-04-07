#!/usr/bin/env python
"""
Responsibility Counter for Python Files

This script analyzes Python files to count the number of responsibilities per file.
It uses a combination of heuristics to identify distinct responsibilities:
1. Class and method naming patterns
2. Import categories
3. Natural language processing of docstrings and comments
4. Code structure analysis

Usage:
    python count_responsibilities.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
from collections import defaultdict
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Responsibility domains and their associated keywords
RESPONSIBILITY_DOMAINS = {
    "data_access": ["database", "query", "repository", "store", "retrieve", "save", "load", "persist", "fetch", "db", "sql", "orm"],
    "ui": ["display", "show", "render", "view", "ui", "interface", "screen", "layout", "widget", "window", "dialog", "form"],
    "validation": ["validate", "check", "verify", "ensure", "assert", "constraint", "rule", "valid", "invalid", "error"],
    "calculation": ["calculate", "compute", "process", "algorithm", "formula", "math", "arithmetic", "sum", "average", "mean"],
    "io": ["file", "read", "write", "stream", "input", "output", "io", "print", "open", "close", "path", "directory"],
    "network": ["http", "request", "response", "api", "endpoint", "url", "network", "fetch", "download", "upload", "socket"],
    "authentication": ["auth", "login", "permission", "role", "access", "credential", "password", "user", "account", "session"],
    "error_handling": ["exception", "error", "handle", "try", "catch", "finally", "raise", "except", "log", "debug"],
    "configuration": ["config", "setting", "property", "environment", "parameter", "option", "preference", "profile"],
    "logging": ["log", "trace", "debug", "info", "warn", "error", "fatal", "logger", "message", "level"],
    "caching": ["cache", "memory", "temporary", "store", "retrieve", "expire", "invalidate", "hit", "miss"],
    "threading": ["thread", "async", "concurrent", "parallel", "lock", "mutex", "semaphore", "synchronize", "queue"],
    "serialization": ["serialize", "deserialize", "marshal", "unmarshal", "encode", "decode", "json", "xml", "yaml", "pickle"],
    "business_logic": ["business", "rule", "workflow", "process", "policy", "domain", "entity", "service", "operation"],
    "testing": ["test", "assert", "mock", "stub", "fixture", "suite", "case", "scenario", "verify", "expect"]
}

class ResponsibilityCounter:
    """Counts responsibilities in Python files using advanced heuristics."""

    def __init__(self):
        self.file_responsibilities = {}

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file to count responsibilities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract file-level information
            file_name = os.path.basename(file_path)
            module_name = os.path.splitext(file_name)[0]

            # Initialize results
            results = {
                "file_path": file_path,
                "module_name": module_name,
                "responsibilities": set(),
                "classes": [],
                "imports": [],
                "responsibility_score": 0.0  # Will be updated based on analysis
            }

            # Analyze imports
            import_responsibilities = self._analyze_imports(tree)
            results["imports"] = list(import_responsibilities)
            results["responsibilities"].update(import_responsibilities)

            # Analyze classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_result = self._analyze_class(node, content)
                    results["classes"].append(class_result)
                    results["responsibilities"].update(class_result["responsibilities"])

            # Analyze module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                docstring_responsibilities = self._extract_responsibilities_from_text(module_docstring)
                results["responsibilities"].update(docstring_responsibilities)

            # Analyze module-level functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node in tree.body:
                    function_responsibilities = self._analyze_function(node, content)
                    results["responsibilities"].update(function_responsibilities)

            # Convert responsibilities set to list for JSON serialization
            results["responsibilities"] = list(results["responsibilities"])

            # Calculate responsibility score (1.0 is ideal - one clear responsibility)
            # More responsibilities = lower score
            num_responsibilities = len(results["responsibilities"])
            if num_responsibilities == 0:
                results["responsibility_score"] = 0.5  # No clear responsibility is not ideal
            elif num_responsibilities == 1:
                results["responsibility_score"] = 1.0  # One responsibility is ideal
            else:
                results["responsibility_score"] = max(0.0, 1.0 - ((num_responsibilities - 1) * 0.2))

            # Store results for this file
            self.file_responsibilities[file_path] = results

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _analyze_imports(self, tree: ast.AST) -> Set[str]:
        """Analyze imports to identify responsibilities."""
        responsibilities = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    import_name = name.name.split('.')[0]
                    responsibilities.update(self._get_responsibility_from_name(import_name))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_name = node.module.split('.')[0]
                    responsibilities.update(self._get_responsibility_from_name(import_name))

                for name in node.names:
                    responsibilities.update(self._get_responsibility_from_name(name.name))

        return responsibilities

    def _analyze_class(self, cls_node: ast.ClassDef, content: str) -> Dict:
        """Analyze a class to identify responsibilities."""
        class_name = cls_node.name
        responsibilities = set()

        # Check class name for responsibility indicators
        responsibilities.update(self._get_responsibility_from_name(class_name))

        # Check class docstring
        docstring = ast.get_docstring(cls_node)
        if docstring:
            responsibilities.update(self._extract_responsibilities_from_text(docstring))

        # Check methods
        methods = []
        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef) and node in cls_node.body:
                method_responsibilities = self._analyze_function(node, content)
                methods.append({
                    "name": node.name,
                    "responsibilities": list(method_responsibilities)
                })
                responsibilities.update(method_responsibilities)

        return {
            "name": class_name,
            "responsibilities": list(responsibilities),
            "methods": methods
        }

    def _analyze_function(self, func_node: ast.FunctionDef, content: str) -> Set[str]:
        """Analyze a function to identify responsibilities."""
        responsibilities = set()

        # Check function name for responsibility indicators
        responsibilities.update(self._get_responsibility_from_name(func_node.name))

        # Check function docstring
        docstring = ast.get_docstring(func_node)
        if docstring:
            responsibilities.update(self._extract_responsibilities_from_text(docstring))

        # Check function body for responsibility indicators
        func_source = self._get_node_source(func_node, content)
        responsibilities.update(self._extract_responsibilities_from_text(func_source))

        return responsibilities

    def _get_responsibility_from_name(self, name: str) -> Set[str]:
        """Extract responsibilities from a name based on keywords."""
        responsibilities = set()
        name_lower = name.lower()

        for domain, keywords in RESPONSIBILITY_DOMAINS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', name_lower):
                    responsibilities.add(domain)
                    break

        return responsibilities

    def _extract_responsibilities_from_text(self, text: str) -> Set[str]:
        """Extract responsibilities from text using keyword matching."""
        responsibilities = set()
        text_lower = text.lower()

        for domain, keywords in RESPONSIBILITY_DOMAINS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    responsibilities.add(domain)
                    break

        return responsibilities

    def _get_node_source(self, node: ast.AST, content: str) -> str:
        """Get source code for an AST node."""
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return ""

        lines = content.splitlines()
        start_line = node.lineno - 1  # 0-indexed
        end_line = getattr(node, 'end_lineno', len(lines)) - 1

        return "\n".join(lines[start_line:end_line+1])

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of file responsibilities."""
        report = {
            "files": list(self.file_responsibilities.values()),
            "responsibility_distribution": self._calculate_responsibility_distribution(),
            "recommendations": self._generate_recommendations()
        }

        return report

    def _calculate_responsibility_distribution(self) -> Dict:
        """Calculate the distribution of responsibilities across files."""
        distribution = defaultdict(list)

        for file_path, results in self.file_responsibilities.items():
            if "error" in results:
                continue

            for responsibility in results["responsibilities"]:
                distribution[responsibility].append(file_path)

        # Convert to regular dict for JSON serialization
        return {k: list(v) for k, v in distribution.items()}

    def _generate_recommendations(self) -> List[str]:
        """Generate refactoring recommendations based on responsibility analysis."""
        recommendations = []

        # Find files with too many responsibilities
        for file_path, results in self.file_responsibilities.items():
            if "error" in results:
                continue

            num_responsibilities = len(results["responsibilities"])
            if num_responsibilities > 1:
                file_name = os.path.basename(file_path)
                recommendations.append(
                    f"File '{file_name}' has {num_responsibilities} responsibilities "
                    f"({', '.join(results['responsibilities'])}). "
                    f"Consider splitting it into multiple files, each with a single responsibility."
                )

        # Find responsibilities spread across too many files
        responsibility_count = {r: len(files) for r, files in self._calculate_responsibility_distribution().items()}
        for responsibility, count in responsibility_count.items():
            if count > 3:  # Arbitrary threshold
                recommendations.append(
                    f"Responsibility '{responsibility}' is spread across {count} files. "
                    f"Consider consolidating related functionality."
                )

        return recommendations


def analyze_directory(directory_path: str, counter: ResponsibilityCounter) -> None:
    """Recursively analyze all Python files in a directory."""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                counter.analyze_file(file_path)


def print_report(report: Dict) -> None:
    """Print the responsibility report in a readable format."""
    print("\n===== RESPONSIBILITY ANALYSIS REPORT =====\n")

    # Print file responsibilities
    print("File Responsibilities:")
    for file_info in sorted(report["files"], key=lambda x: len(x.get("responsibilities", [])), reverse=True):
        if "error" in file_info:
            print(f"  Error analyzing {file_info['file_path']}: {file_info['error']}")
            continue

        file_name = os.path.basename(file_info["file_path"])
        responsibilities = file_info.get("responsibilities", [])

        if not responsibilities:
            print(f"  {file_name}: No clear responsibilities identified")
        else:
            print(f"  {file_name}: {len(responsibilities)} responsibilities - {', '.join(responsibilities)}")
            print(f"    Responsibility Score: {file_info['responsibility_score']:.2f}/1.00")

            # Print class responsibilities
            for cls in file_info.get("classes", []):
                print(f"    Class {cls['name']}: {', '.join(cls['responsibilities'])}")

        print()

    # Print responsibility distribution
    print("\nResponsibility Distribution:")
    for responsibility, files in sorted(report["responsibility_distribution"].items(),
                                       key=lambda x: len(x[1]), reverse=True):
        file_names = [os.path.basename(f) for f in files]
        print(f"  {responsibility}: {len(files)} files - {', '.join(file_names[:3])}" +
              (f" and {len(file_names) - 3} more" if len(file_names) > 3 else ""))

    # Print recommendations
    if report["recommendations"]:
        print("\nRecommendations:")
        for i, recommendation in enumerate(report["recommendations"]):
            print(f"  {i+1}. {recommendation}")
    else:
        print("\nNo recommendations - codebase appears well-organized!")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    counter = ResponsibilityCounter()

    if os.path.isfile(path):
        counter.analyze_file(path)
    elif os.path.isdir(path):
        analyze_directory(path, counter)
    else:
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    report = counter.generate_report()
    print_report(report)


if __name__ == "__main__":
    main()
