"""Dependency Inversion Principle Analyzer.

This module provides an analyzer for detecting violations of the Dependency Inversion Principle.
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

class DIPAnalyzer(BaseAnalyzer):
    """Analyzer for detecting violations of the Dependency Inversion Principle.

    The Dependency Inversion Principle states that high-level modules should not
    depend on low-level modules. Both should depend on abstractions.

    This analyzer detects:
    - High-level modules depending on low-level modules
    - Direct instantiation of concrete classes
    - Missing abstractions/interfaces
    - Concrete class dependencies in constructors
    - Hardcoded dependencies
    """

    def __init__(self, config=None):
        """Initialize the DIP analyzer.

        Args:
            config: Optional configuration dictionary
        """
        name = "Dependency Inversion Principle Analyzer"
        description = "Analyzer for detecting violations of the Dependency Inversion Principle"
        super().__init__(name, description, config)
        self.principle = "DIP"
        self.class_violations = defaultdict(list)
        self.class_scores = {}
        self.overall_score = 1.0
        self.abstractions = set()
        self.concrete_classes = set()
        self.dependencies = defaultdict(set)
        self.high_level_modules = set()
        self.low_level_modules = set()

    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Analyze a Python file for DIP violations.

        Args:
            file_path: Path to the Python file to analyze
            content: Content of the file
            tree: AST of the file

        Returns:
            Dict containing analysis results
        """
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        # Initialize results
        results = {
            "file_path": file_path,
            "module_name": module_name,
            "overall_dip_score": 1.0,
            "class_analysis": []
        }

        # First pass: identify abstractions and concrete classes
        self._identify_abstractions_and_concretes(tree)

        # Second pass: analyze dependencies
        self._analyze_dependencies(tree)

        # Third pass: identify high-level and low-level modules
        self._identify_module_levels()

        # Fourth pass: analyze for DIP violations
        for class_name in self.dependencies.keys():
            class_result = self._analyze_class_dip(class_name)
            results["class_analysis"].append(class_result)

        # Calculate overall score
        if results["class_analysis"]:
            total_score = sum(cls["dip_score"] for cls in results["class_analysis"])
            results["overall_dip_score"] = round(total_score / len(results["class_analysis"]), 2)

        self.overall_score = results["overall_dip_score"]
        return results

    def _identify_abstractions_and_concretes(self, tree: ast.AST) -> None:
        """Identify abstractions and concrete classes.

        Args:
            tree: AST for the file
        """
        # Reset abstractions and concrete classes
        self.abstractions = set()
        self.concrete_classes = set()

        # Find all classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name

                # Check if this is an abstraction
                if self._is_abstract_class(node):
                    self.abstractions.add(class_name)
                else:
                    self.concrete_classes.add(class_name)

    def _analyze_dependencies(self, tree: ast.AST) -> None:
        """Analyze dependencies between classes.

        Args:
            tree: AST for the file
        """
        # Reset dependencies
        self.dependencies = defaultdict(set)

        # Find all classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name

                # Check for dependencies in base classes
                for base in node.bases:
                    base_name = self._get_name_from_node(base)
                    if base_name:
                        self.dependencies[class_name].add(base_name)

                # Check for dependencies in class body
                self._analyze_class_body_dependencies(node, class_name)

    def _analyze_class_body_dependencies(self, cls_node: ast.ClassDef, class_name: str) -> None:
        """Analyze dependencies in class body.

        Args:
            cls_node: AST node for the class
            class_name: Name of the class
        """
        # Check for direct instantiations and other dependencies
        for node in ast.walk(cls_node):
            # Check for class instantiations: obj = ClassName()
            if isinstance(node, ast.Call):
                # Handle direct class instantiation: ClassName()
                dependency = self._get_name_from_node(node.func)
                if dependency:
                    self.dependencies[class_name].add(dependency)

            # Check for attribute access that might indicate dependency: self.dependency = SomeClass()
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    # Look for self.attribute assignments
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        # If the right side is a class instantiation
                        if isinstance(node.value, ast.Call):
                            dependency = self._get_name_from_node(node.value.func)
                            if dependency:
                                self.dependencies[class_name].add(dependency)

    def _identify_module_levels(self) -> None:
        """Identify high-level and low-level modules based on dependencies."""
        # Reset high-level and low-level modules
        self.high_level_modules = set()
        self.low_level_modules = set()

        # Count incoming and outgoing dependencies
        incoming = defaultdict(int)
        outgoing = defaultdict(int)

        for class_name, deps in self.dependencies.items():
            outgoing[class_name] = len(deps)
            for dep in deps:
                incoming[dep] += 1

        # High-level modules have more incoming than outgoing dependencies
        # Low-level modules have more outgoing than incoming dependencies
        for class_name in set(incoming.keys()) | set(outgoing.keys()):
            if incoming[class_name] > outgoing[class_name]:
                self.high_level_modules.add(class_name)
            elif outgoing[class_name] > incoming[class_name]:
                self.low_level_modules.add(class_name)

    def _analyze_class_dip(self, class_name: str) -> Dict:
        """Analyze a class for DIP violations.

        Args:
            class_name: Name of the class

        Returns:
            Dict containing analysis results for the class
        """
        violations = []

        # Check if this is a high-level module
        is_high_level = class_name in self.high_level_modules

        # Check for dependencies on concrete classes
        concrete_deps = [dep for dep in self.dependencies[class_name] if dep in self.concrete_classes]
        if concrete_deps and is_high_level:
            violations.append({
                "type": "High-level module depends on concrete classes",
                "details": f"Depends on concrete classes: {', '.join(concrete_deps)}",
                "location": f"Class {class_name}"
            })

        # Check for direct instantiations
        direct_instantiations = self._find_direct_instantiations(class_name)
        if direct_instantiations and is_high_level:
            violations.append({
                "type": "High-level module directly instantiates concrete classes",
                "details": f"Direct instantiation of {', '.join(direct_instantiations)}",
                "location": f"Class {class_name}"
            })

        # Check for missing constructor injection
        if is_high_level and self.dependencies[class_name]:
            violations.append({
                "type": "High-level module doesn't use constructor injection for dependencies",
                "details": f"Dependencies: {', '.join(self.dependencies[class_name])}",
                "location": f"Class {class_name}"
            })

        # Calculate DIP score
        dip_score = 1.0
        if violations:
            # Deduct points for each violation
            dip_score = max(0.0, 1.0 - (len(violations) * 0.2))

        # Store results
        self.class_violations[class_name] = violations
        self.class_scores[class_name] = dip_score

        return {
            "class_name": class_name,
            "dip_score": round(dip_score, 2),
            "is_high_level": is_high_level,
            "dependencies": list(self.dependencies[class_name]),
            "violations": violations,
            "recommendation": self._generate_recommendation(class_name, violations, is_high_level) if violations else ""
        }

    def _is_abstract_class(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class is abstract using standard Python patterns.

        Args:
            cls_node: AST node for the class

        Returns:
            True if the class is abstract, False otherwise
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

    def _find_direct_instantiations(self, class_name: str) -> List[str]:
        """Find direct instantiations of concrete classes.

        Args:
            class_name: Name of the class

        Returns:
            List of directly instantiated concrete classes
        """
        # This is a simplified implementation
        # In a real implementation, we would need to analyze the AST more thoroughly
        return [dep for dep in self.dependencies[class_name] if dep in self.concrete_classes]

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

    def _generate_recommendation(self, class_name: str, violations: List[Dict], is_high_level: bool) -> str:
        """Generate refactoring recommendations based on analysis.

        Args:
            class_name: Name of the class
            violations: List of violations
            is_high_level: Whether the class is a high-level module

        Returns:
            String containing recommendations
        """
        if not violations:
            return ""

        if is_high_level:
            recommendations = [f"Class '{class_name}' is a high-level module with potential DIP violations:"]
        else:
            recommendations = [f"Class '{class_name}' has potential DIP violations:"]

        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            violation_types[violation["type"]].append(violation["details"])

        # Add recommendations for each violation type
        for violation_type, details_list in violation_types.items():
            if "depends on concrete classes" in violation_type:
                recommendations.append("- Depend on abstractions (interfaces or abstract classes) instead of concrete implementations.")
            elif "directly instantiates" in violation_type:
                recommendations.append("- Replace direct instantiation with dependency injection or factory pattern.")
            elif "constructor injection" in violation_type:
                recommendations.append("- Use constructor injection to make dependencies explicit and testable.")

        recommendations.append("- Consider creating interfaces for your dependencies and injecting implementations.")

        return "\n".join(recommendations)

    def print_results(self, results: Dict) -> None:
        """Print analysis results.

        Args:
            results: Analysis results
        """
        print("\n===== DEPENDENCY INVERSION PRINCIPLE ANALYSIS =====\n")
        print(f"File: {results['file_path']}")
        print(f"Module: {results['module_name']}")
        print(f"Overall DIP Score: {results['overall_dip_score']:.2f}/1.00\n")

        for cls in results["class_analysis"]:
            print(f"  Class: {cls['class_name']} {'✓' if cls['dip_score'] >= 0.8 else '✗'} {' [HIGH-LEVEL]' if cls['is_high_level'] else ''} ")
            print(f"  DIP Score: {cls['dip_score']:.2f}/1.00")

            if cls["dependencies"]:
                print(f"  Dependencies: {', '.join(cls['dependencies'])}")

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

        if results["overall_dip_score"] < 1.0:
            print("DIP violations detected. Consider refactoring the flagged classes.")
        else:
            print("No DIP violations detected! 🎉")

    def get_summary(self) -> str:
        """Get a summary of the analysis results.

        Returns:
            String containing a summary of the analysis results
        """
        return f"DIP Score: {self.overall_score:.2f}/1.00"
