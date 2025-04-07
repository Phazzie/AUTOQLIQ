#!/usr/bin/env python
"""
Interface Segregation Principle Analyzer

This script analyzes Python files to identify potential violations of the Interface Segregation Principle.
It detects patterns that indicate interfaces that are too large or clients forced to depend on methods they don't use:
1. Large interfaces with many methods
2. Classes implementing interfaces but not using all methods
3. Interface methods with different client usage patterns
4. Interfaces with low cohesion

Usage:
    python analyze_interface_segregation.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import logging
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class InterfaceSegregationAnalyzer:
    """Analyzes Python code for Interface Segregation Principle violations."""

    def __init__(self, max_interface_methods: int = 5, cohesion_threshold: float = 0.5):
        self.max_interface_methods = max_interface_methods
        self.cohesion_threshold = cohesion_threshold
        self.interfaces = {}  # Maps interface names to their methods
        self.implementations = defaultdict(list)  # Maps interface names to implementing classes
        self.method_usage = defaultdict(set)  # Maps method names to classes that use them
        self.class_methods = {}  # Maps class names to their methods
        self.interface_clients = defaultdict(set)  # Maps interface names to client classes

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for ISP violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # First pass: identify interfaces and implementations
            self._identify_interfaces_and_implementations(tree)

            # Second pass: analyze method usage
            self._analyze_method_usage(tree)

            # Third pass: analyze for ISP violations
            results = {
                "file_path": file_path,
                "interface_analysis": [],
                "overall_isp_score": 1.0  # Will be updated based on interface analyses
            }

            # Analyze each interface
            for interface_name, methods in self.interfaces.items():
                interface_result = self._analyze_interface(interface_name, methods)
                results["interface_analysis"].append(interface_result)

            # Calculate overall ISP score for the file
            if results["interface_analysis"]:
                avg_score = sum(i["isp_score"] for i in results["interface_analysis"]) / len(results["interface_analysis"])
                results["overall_isp_score"] = avg_score

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _identify_interfaces_and_implementations(self, tree: ast.AST) -> None:
        """Identify interfaces and their implementations."""
        # Find all classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # First, identify potential interfaces
        for cls in classes:
            # Check if this looks like an interface
            if self._is_interface(cls):
                # Get all abstract methods
                methods = self._get_abstract_methods(cls)
                if methods:
                    self.interfaces[cls.name] = methods

        # Then, identify implementations
        for cls in classes:
            # Check if this class implements any interfaces
            for base in cls.bases:
                base_name = self._get_name_from_node(base)
                if base_name in self.interfaces:
                    self.implementations[base_name].append(cls.name)

                    # Store methods of this class
                    methods = self._get_methods(cls)
                    self.class_methods[cls.name] = methods

    def _analyze_method_usage(self, tree: ast.AST) -> None:
        """Analyze which classes use which methods."""
        # Find all classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for cls in classes:
            class_name = cls.name

            # Look for method calls
            for node in ast.walk(cls):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    # This is a method call like obj.method()
                    method_name = node.func.attr

                    # Check if this method is part of any interface
                    for interface_name, methods in self.interfaces.items():
                        if method_name in methods:
                            # Record that this class uses this method
                            self.method_usage[f"{interface_name}.{method_name}"].add(class_name)

                            # Record that this class is a client of this interface
                            self.interface_clients[interface_name].add(class_name)

    def _analyze_interface(self, interface_name: str, methods: List[str]) -> Dict:
        """Analyze an interface for ISP violations."""
        violations = []

        # Check if interface has too many methods
        if len(methods) > self.max_interface_methods:
            violations.append({
                "type": "large_interface",
                "description": f"Interface has {len(methods)} methods, which exceeds the recommended maximum of {self.max_interface_methods}",
                "methods": methods
            })

        # Check for implementations that don't use all methods
        for impl_class in self.implementations.get(interface_name, []):
            unused_methods = []
            for method in methods:
                method_key = f"{interface_name}.{method}"
                if impl_class not in self.method_usage.get(method_key, set()):
                    unused_methods.append(method)

            if unused_methods:
                violations.append({
                    "type": "unused_methods",
                    "description": f"Class '{impl_class}' implements interface '{interface_name}' but doesn't use {len(unused_methods)} methods",
                    "class": impl_class,
                    "unused_methods": unused_methods
                })

        # Check for methods with different client usage patterns
        method_clients = {}
        for method in methods:
            method_key = f"{interface_name}.{method}"
            method_clients[method] = self.method_usage.get(method_key, set())

        # Build a graph of method relationships based on client usage
        method_graph = self._build_method_relationship_graph(method_clients)

        # Identify method clusters that could be separate interfaces
        clusters = self._identify_method_clusters(method_graph, methods)

        if len(clusters) > 1:
            violations.append({
                "type": "method_clusters",
                "description": f"Interface '{interface_name}' has {len(clusters)} distinct method clusters that could be separate interfaces",
                "clusters": clusters
            })

        # Calculate cohesion score
        cohesion_score = self._calculate_interface_cohesion(method_clients)

        if cohesion_score < self.cohesion_threshold:
            violations.append({
                "type": "low_cohesion",
                "description": f"Interface '{interface_name}' has low cohesion score of {cohesion_score:.2f}, below threshold of {self.cohesion_threshold}",
                "cohesion_score": cohesion_score
            })

        # Calculate ISP score (1.0 is perfect, 0.0 is worst)
        # Each violation type reduces score by 0.2
        isp_score = max(0.0, 1.0 - (len(violations) * 0.2))

        # Adjust score based on cohesion
        if cohesion_score < self.cohesion_threshold:
            isp_score *= cohesion_score / self.cohesion_threshold

        return {
            "interface_name": interface_name,
            "methods": methods,
            "implementations": self.implementations.get(interface_name, []),
            "clients": list(self.interface_clients.get(interface_name, set())),
            "violations": violations,
            "cohesion_score": cohesion_score,
            "isp_score": isp_score,
            "recommendation": self._generate_recommendation(interface_name, violations, clusters)
        }

    def _is_interface(self, cls_node: ast.ClassDef) -> bool:
        """Determine if a class appears to be an interface using standard Python patterns."""
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

    def _get_name_from_node(self, node: ast.AST) -> str:
        """Extract name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return "unknown"

    def _get_abstract_methods(self, cls_node: ast.ClassDef) -> List[str]:
        """Get all abstract methods from a class."""
        methods = []

        for node in ast.walk(cls_node):
            if isinstance(node, ast.FunctionDef):
                # Check if method is abstract
                is_abstract = False
                for decorator in node.decorator_list:
                    decorator_name = self._get_name_from_node(decorator)
                    if decorator_name == "abstractmethod":
                        is_abstract = True
                        break

                if is_abstract:
                    methods.append(node.name)

        return methods

    def _get_methods(self, cls_node: ast.ClassDef) -> List[str]:
        """Get all methods from a class."""
        return [node.name for node in ast.walk(cls_node) if isinstance(node, ast.FunctionDef)]

    def _build_method_relationship_graph(self, method_clients: Dict[str, Set[str]]) -> nx.Graph:
        """Build a graph of method relationships based on client usage."""
        graph = nx.Graph()

        # Add all methods as nodes
        for method in method_clients:
            graph.add_node(method)

        # Add edges between methods that share clients
        methods = list(method_clients.keys())
        for i in range(len(methods)):
            for j in range(i+1, len(methods)):
                method1 = methods[i]
                method2 = methods[j]

                # Calculate Jaccard similarity between client sets
                clients1 = method_clients[method1]
                clients2 = method_clients[method2]

                if not clients1 or not clients2:
                    continue

                similarity = len(clients1.intersection(clients2)) / len(clients1.union(clients2))

                if similarity > 0:
                    graph.add_edge(method1, method2, weight=similarity)

        return graph

    def _identify_method_clusters(self, graph: nx.Graph, methods: List[str]) -> List[List[str]]:
        """Identify clusters of methods that could be separate interfaces."""
        # If graph is empty or has no edges, return each method as its own cluster
        if not graph.nodes or not graph.edges:
            return [[method] for method in methods]

        # Use community detection to find clusters
        try:
            # Try to use Louvain method for community detection
            from community import best_partition
            partition = best_partition(graph)

            # Group methods by community
            communities = defaultdict(list)
            for method, community_id in partition.items():
                communities[community_id].append(method)

            return list(communities.values())
        except ImportError:
            # Fall back to connected components if community detection is not available
            return [list(component) for component in nx.connected_components(graph)]

    def _calculate_interface_cohesion(self, method_clients: Dict[str, Set[str]]) -> float:
        """Calculate cohesion score for an interface based on client usage patterns."""
        if not method_clients:
            return 1.0

        # Calculate average Jaccard similarity between all pairs of methods
        methods = list(method_clients.keys())
        if len(methods) <= 1:
            return 1.0

        total_similarity = 0
        pair_count = 0

        for i in range(len(methods)):
            for j in range(i+1, len(methods)):
                method1 = methods[i]
                method2 = methods[j]

                clients1 = method_clients[method1]
                clients2 = method_clients[method2]

                if not clients1 or not clients2:
                    continue

                similarity = len(clients1.intersection(clients2)) / len(clients1.union(clients2))
                total_similarity += similarity
                pair_count += 1

        if pair_count == 0:
            return 0.0

        return total_similarity / pair_count

    def _generate_recommendation(self, interface_name: str, violations: List[Dict], clusters: List[List[str]]) -> str:
        """Generate refactoring recommendations based on analysis."""
        if not violations:
            return f"Interface '{interface_name}' appears to follow ISP."

        recommendations = [f"Interface '{interface_name}' has potential ISP violations:"]

        for violation in violations:
            if violation["type"] == "large_interface":
                recommendations.append(f"- Interface has too many methods ({len(violation['methods'])}). Consider breaking it into smaller interfaces.")

            elif violation["type"] == "unused_methods":
                recommendations.append(f"- Class '{violation['class']}' is forced to implement methods it doesn't use: {', '.join(violation['unused_methods'])}.")

            elif violation["type"] == "method_clusters":
                recommendations.append("- Interface contains distinct method clusters that could be separate interfaces:")
                for i, cluster in enumerate(clusters):
                    recommendations.append(f"  * Interface {i+1}: {', '.join(cluster)}")

            elif violation["type"] == "low_cohesion":
                recommendations.append(f"- Interface has low cohesion ({violation['cohesion_score']:.2f}), indicating methods may not be related.")

        recommendations.append("- Consider splitting this interface into smaller, more focused interfaces based on client usage patterns.")

        return " ".join(recommendations)


def analyze_directory(directory_path: str, analyzer: InterfaceSegregationAnalyzer) -> List[Dict]:
    """Recursively analyze all Python files in a directory."""
    results = []

    # First pass to build interface and implementation info across all files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    analyzer._identify_interfaces_and_implementations(tree)
                except Exception as e:
                    logger.error(f"Error pre-processing file {file_path}: {str(e)}")

    # Second pass to analyze method usage across all files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    analyzer._analyze_method_usage(tree)
                except Exception as e:
                    logger.error(f"Error analyzing method usage in file {file_path}: {str(e)}")

    # Third pass to analyze each file
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results.append(analyzer.analyze_file(file_path))

    return results


def print_results(results: List[Dict]) -> None:
    """Print analysis results in a readable format."""
    print("\n===== INTERFACE SEGREGATION PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall ISP Score: {result['overall_isp_score']:.2f}/1.00")

        for interface_analysis in result.get("interface_analysis", []):
            isp_status = "✓" if interface_analysis["isp_score"] >= 0.8 else "✗"
            print(f"\n  Interface: {interface_analysis['interface_name']} {isp_status}")
            print(f"  ISP Score: {interface_analysis['isp_score']:.2f}/1.00")
            print(f"  Cohesion: {interface_analysis['cohesion_score']:.2f}/1.00")
            print(f"  Methods: {', '.join(interface_analysis['methods'])}")
            print(f"  Implementations: {', '.join(interface_analysis['implementations'])}")
            print(f"  Clients: {', '.join(interface_analysis['clients'])}")

            if interface_analysis["violations"]:
                violations_found = True
                print("  Violations:")
                for violation in interface_analysis["violations"]:
                    print(f"    - {violation['description']}")

                print(f"  RECOMMENDATION: {interface_analysis['recommendation']}")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo ISP violations detected! 🎉")
    else:
        print("\nISP violations detected. Consider refactoring the flagged interfaces.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = InterfaceSegregationAnalyzer()

    if os.path.isfile(path):
        # For a single file, we need to pre-process it
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            analyzer._identify_interfaces_and_implementations(tree)
            analyzer._analyze_method_usage(tree)
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
