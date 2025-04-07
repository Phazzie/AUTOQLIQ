#!/usr/bin/env python
"""
Dependency Inversion Principle Analyzer

This script analyzes Python files to identify potential violations of the Dependency Inversion Principle.
It detects patterns that indicate high-level modules depending on low-level modules:
1. Direct instantiation of concrete classes
2. Missing abstractions/interfaces
3. Concrete class dependencies in constructors
4. Hardcoded dependencies

Usage:
    python analyze_dependency_inversion.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DependencyInversionAnalyzer:
    """Analyzes Python code for Dependency Inversion Principle violations."""

    def __init__(self):
        self.abstractions = set()  # Set of abstract classes/interfaces
        self.concrete_classes = set()  # Set of concrete classes
        self.dependencies = defaultdict(set)  # Maps classes to their dependencies
        self.dependency_graph = nx.DiGraph()  # Directed graph of dependencies
        self.module_abstractions = defaultdict(set)  # Maps modules to their abstractions

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for DIP violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            module_name = os.path.splitext(os.path.basename(file_path))[0]

            # Initialize Jedi script for import resolution if jedi is available
            try:
                import jedi
                self.jedi_script = jedi.Script(code=content, path=file_path)
                self.has_jedi = True
            except ImportError:
                self.has_jedi = False
                logger.warning("Jedi not available. Import resolution will be limited.")

            # First pass: identify abstractions and concrete classes
            self._identify_abstractions_and_concretes(tree, module_name)

            # Second pass: analyze dependencies
            self._analyze_dependencies(tree, module_name)

            # Third pass: analyze for DIP violations
            results = {
                "file_path": file_path,
                "module_name": module_name,
                "class_analysis": [],
                "overall_dip_score": 1.0  # Will be updated based on class analyses
            }

            # Find all classes in the file
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            for cls in classes:
                class_result = self._analyze_class(cls, module_name)
                results["class_analysis"].append(class_result)

            # Calculate overall DIP score for the file
            if results["class_analysis"]:
                avg_score = sum(c["dip_score"] for c in results["class_analysis"]) / len(results["class_analysis"])
                results["overall_dip_score"] = avg_score

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _identify_abstractions_and_concretes(self, tree: ast.AST, module_name: str) -> None:
        """Identify abstract and concrete classes."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                full_name = f"{module_name}.{class_name}"

                # Check if this is an abstract class/interface
                if self._is_abstract_class(node):
                    self.abstractions.add(full_name)
                    self.module_abstractions[module_name].add(class_name)
                else:
                    self.concrete_classes.add(full_name)

                # Add to dependency graph
                self.dependency_graph.add_node(full_name)

    def _analyze_dependencies(self, tree: ast.AST, module_name: str) -> None:
        """Analyze dependencies between classes."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                full_name = f"{module_name}.{class_name}"

                # Check dependencies in base classes
                for base in node.bases:
                    # Use Jedi to resolve the import if available
                    base_name = self._resolve_import(base)
                    if base_name:
                        # Add dependency
                        self.dependencies[full_name].add(base_name)

                        # Add to dependency graph
                        if base_name not in self.dependency_graph:
                            self.dependency_graph.add_node(base_name)
                        self.dependency_graph.add_edge(full_name, base_name)

                # Check dependencies in class body
                self._analyze_class_body_dependencies(node, full_name, module_name)

    def _analyze_class_body_dependencies(self, cls_node: ast.ClassDef, full_class_name: str, module_name: str) -> None:
        """Analyze dependencies in class body."""
        # Check for direct instantiations and other dependencies
        for node in ast.walk(cls_node):
            # Check for class instantiations: obj = ClassName()
            if isinstance(node, ast.Call):
                # Handle direct class instantiation: ClassName()
                # Use Jedi to resolve the import if available
                dependency = self._resolve_import(node.func)
                if dependency:
                    # If Jedi couldn't resolve the full name, check if it's a local class
                    if '.' not in dependency and dependency in self.module_abstractions.get(module_name, set()):
                        dependency = f"{module_name}.{dependency}"

                    # Add dependency
                    self.dependencies[full_class_name].add(dependency)

                    # Add to dependency graph
                    if dependency not in self.dependency_graph:
                        self.dependency_graph.add_node(dependency)
                    self.dependency_graph.add_edge(full_class_name, dependency)

            # Check for attribute access that might indicate dependency: self.dependency = SomeClass()
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    # Look for self.attribute assignments
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        # If the right side is a class instantiation
                        if isinstance(node.value, ast.Call):
                            dependency = self._resolve_import(node.value.func)
                            if dependency:
                                # If Jedi couldn't resolve the full name, check if it's a local class
                                if '.' not in dependency and dependency in self.module_abstractions.get(module_name, set()):
                                    dependency = f"{module_name}.{dependency}"

                                # Add dependency
                                self.dependencies[full_class_name].add(dependency)

                                # Add to dependency graph
                                if dependency not in self.dependency_graph:
                                    self.dependency_graph.add_node(dependency)
                                self.dependency_graph.add_edge(full_class_name, dependency)

    def _analyze_class(self, cls_node: ast.ClassDef, module_name: str) -> Dict:
        """Analyze a class for DIP violations."""
        class_name = cls_node.name
        full_name = f"{module_name}.{class_name}"
        violations = []

        # Check if this is a high-level module (heuristic: has "service", "manager", "controller", etc. in name)
        is_high_level = any(term in class_name.lower() for term in
                           ["service", "manager", "controller", "handler", "processor", "orchestrator"])

        # Get dependencies
        deps = self.dependencies.get(full_name, set())
        concrete_deps = [d for d in deps if d in self.concrete_classes]
        abstract_deps = [d for d in deps if d in self.abstractions]

        # Check for direct instantiation of concrete classes
        instantiations = self._find_concrete_instantiations(cls_node)
        if instantiations and is_high_level:
            violations.append({
                "type": "direct_instantiation",
                "description": "High-level module directly instantiates concrete classes",
                "details": instantiations
            })

        # Check for concrete class dependencies
        if concrete_deps and is_high_level:
            violations.append({
                "type": "concrete_dependency",
                "description": "High-level module depends on concrete classes instead of abstractions",
                "details": concrete_deps
            })

        # Check for constructor injection
        has_constructor_injection = self._has_constructor_injection(cls_node)
        if not has_constructor_injection and deps and is_high_level:
            violations.append({
                "type": "missing_injection",
                "description": "High-level module doesn't use constructor injection for dependencies",
                "details": list(deps)
            })

        # Check for hardcoded dependencies
        hardcoded = self._find_hardcoded_dependencies(cls_node)
        if hardcoded and is_high_level:
            violations.append({
                "type": "hardcoded_dependency",
                "description": "High-level module has hardcoded dependencies",
                "details": hardcoded
            })

        # Calculate DIP score (1.0 is perfect, 0.0 is worst)
        # Each violation reduces score by 0.2
        dip_score = max(0.0, 1.0 - (len(violations) * 0.2))

        # Bonus for using abstractions
        if abstract_deps and is_high_level:
            dip_score = min(1.0, dip_score + 0.1)

        # Bonus for constructor injection
        if has_constructor_injection and is_high_level:
            dip_score = min(1.0, dip_score + 0.1)

        return {
            "class_name": class_name,
            "full_name": full_name,
            "is_high_level": is_high_level,
            "is_abstract": full_name in self.abstractions,
            "dependencies": list(deps),
            "violations": violations,
            "dip_score": dip_score,
            "recommendation": self._generate_recommendation(class_name, violations, is_high_level)
        }

    def _is_abstract_class(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class is abstract."""
        # Check for ABC in bases
        for base in cls_node.bases:
            base_name = self._get_name_from_node(base)
            if base_name in ["ABC", "Interface", "Abstract"]:
                return True

        # Check for @abstractmethod decorators
        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    decorator_name = self._get_name_from_node(decorator)
                    if decorator_name == "abstractmethod":
                        return True

        # Check if class name starts with "I" or contains "Interface" or "Abstract"
        if cls_node.name.startswith("I") and len(cls_node.name) > 1 and cls_node.name[1].isupper():
            return True
        if "Interface" in cls_node.name or "Abstract" in cls_node.name:
            return True

        return False

    def _get_name_from_node(self, node: ast.AST) -> Optional[str]:
        """Extract name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _resolve_import(self, node: ast.AST) -> Optional[str]:
        """Resolve an import using Jedi if available."""
        if not hasattr(self, 'has_jedi') or not self.has_jedi:
            return self._get_name_from_node(node)

        try:
            # Get line and column for the node
            line = getattr(node, 'lineno', 1)
            col = getattr(node, 'col_offset', 0)

            # Use Jedi to infer the type
            definitions = self.jedi_script.infer(line=line, column=col)

            if definitions:
                # Get the first definition
                definition = definitions[0]

                # Check if it's a class
                if definition.type == 'class':
                    # Return the full name (module.Class)
                    return definition.full_name

                # For other types, return the name
                return definition.name
        except Exception as e:
            logger.debug(f"Error resolving import with Jedi: {str(e)}")

        # Fall back to simple name extraction
        return self._get_name_from_node(node)

    def _find_concrete_instantiations(self, cls_node: ast.ClassDef) -> List[str]:
        """Find instances of direct instantiation of concrete classes."""
        instantiations = []

        for node in ast.walk(cls_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                class_name = node.func.id

                # Check if this is a concrete class (simplification)
                if class_name[0].isupper() and not class_name.startswith("I"):
                    instantiations.append(f"Direct instantiation of {class_name} at line {node.lineno}")

        return instantiations

    def _has_constructor_injection(self, cls_node: ast.ClassDef) -> bool:
        """Check if a class uses constructor injection."""
        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                # Check if constructor has parameters other than self
                return len(node.args.args) > 1

        return False

    def _find_hardcoded_dependencies(self, cls_node: ast.ClassDef) -> List[str]:
        """Find instances of hardcoded dependencies."""
        hardcoded = []

        for node in ast.walk(cls_node):
            # Check for string literals that look like file paths or URLs
            # Handle both Python 3.8+ (Constant) and older versions (Str)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                value = node.value
                if (value.endswith('.py') or value.endswith('.json') or value.endswith('.xml') or
                    value.startswith('http://') or value.startswith('https://')):
                    hardcoded.append(f"Hardcoded path/URL: '{value}' at line {node.lineno}")
            # For backward compatibility with Python < 3.8
            elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
                value = node.s
                if (value.endswith('.py') or value.endswith('.json') or value.endswith('.xml') or
                    value.startswith('http://') or value.startswith('https://')):
                    hardcoded.append(f"Hardcoded path/URL: '{value}' at line {node.lineno}")

            # Check for hardcoded configuration values
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.upper() == name and len(name) > 2:  # Looks like a constant
                            hardcoded.append(f"Hardcoded constant: {name} at line {node.lineno}")

        return hardcoded

    def _generate_recommendation(self, class_name: str, violations: List[Dict], is_high_level: bool) -> str:
        """Generate refactoring recommendations based on analysis."""
        if not violations:
            if is_high_level:
                return f"Class '{class_name}' follows DIP by depending on abstractions."
            else:
                return f"Class '{class_name}' is not a high-level module, so DIP is less critical."

        recommendations = []

        if is_high_level:
            recommendations.append(f"Class '{class_name}' is a high-level module with potential DIP violations:")
        else:
            recommendations.append(f"Class '{class_name}' has potential DIP violations (though it's not identified as a high-level module):")

        for violation in violations:
            if violation["type"] == "direct_instantiation":
                recommendations.append("- Replace direct instantiation with dependency injection or factory pattern.")

            elif violation["type"] == "concrete_dependency":
                recommendations.append("- Depend on abstractions (interfaces/abstract classes) instead of concrete implementations.")

            elif violation["type"] == "missing_injection":
                recommendations.append("- Use constructor injection to make dependencies explicit and testable.")

            elif violation["type"] == "hardcoded_dependency":
                recommendations.append("- Extract hardcoded values to configuration and inject them.")

        recommendations.append("- Consider creating interfaces for your dependencies and injecting implementations.")

        return " ".join(recommendations)


def analyze_directory(directory_path: str, analyzer: DependencyInversionAnalyzer) -> List[Dict]:
    """Recursively analyze all Python files in a directory."""
    results = []

    # First pass to identify abstractions and concrete classes
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    module_name = os.path.splitext(os.path.basename(file_path))[0]
                    analyzer._identify_abstractions_and_concretes(tree, module_name)
                except Exception as e:
                    logger.error(f"Error pre-processing file {file_path}: {str(e)}")

    # Second pass to analyze dependencies
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    module_name = os.path.splitext(os.path.basename(file_path))[0]
                    analyzer._analyze_dependencies(tree, module_name)
                except Exception as e:
                    logger.error(f"Error analyzing dependencies in file {file_path}: {str(e)}")

    # Third pass to analyze each file
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results.append(analyzer.analyze_file(file_path))

    return results


def print_results(results: List[Dict]) -> None:
    """Print analysis results in a readable format."""
    print("\n===== DEPENDENCY INVERSION PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Module: {result['module_name']}")
        print(f"Overall DIP Score: {result['overall_dip_score']:.2f}/1.00")

        for cls_analysis in result.get("class_analysis", []):
            dip_status = "✓" if cls_analysis["dip_score"] >= 0.8 else "✗"
            high_level_indicator = "[HIGH-LEVEL]" if cls_analysis["is_high_level"] else ""
            abstract_indicator = "[ABSTRACT]" if cls_analysis["is_abstract"] else ""

            print(f"\n  Class: {cls_analysis['class_name']} {dip_status} {high_level_indicator} {abstract_indicator}")
            print(f"  DIP Score: {cls_analysis['dip_score']:.2f}/1.00")

            if cls_analysis["dependencies"]:
                print(f"  Dependencies: {', '.join(cls_analysis['dependencies'])}")

            if cls_analysis["violations"]:
                violations_found = True
                print("  Violations:")
                for violation in cls_analysis["violations"]:
                    print(f"    - {violation['description']}")
                    for detail in violation['details'][:3]:  # Show first 3 details
                        print(f"      * {detail}")
                    if len(violation['details']) > 3:
                        print(f"      * ... and {len(violation['details']) - 3} more")

                print(f"  RECOMMENDATION: {cls_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo DIP violations detected! 🎉")
    else:
        print("\nDIP violations detected. Consider refactoring the flagged classes.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = DependencyInversionAnalyzer()

    if os.path.isfile(path):
        # For a single file, we need to pre-process it
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            module_name = os.path.splitext(os.path.basename(path))[0]
            analyzer._identify_abstractions_and_concretes(tree, module_name)
            analyzer._analyze_dependencies(tree, module_name)
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
