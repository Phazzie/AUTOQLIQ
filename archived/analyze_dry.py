#!/usr/bin/env python
"""
DRY (Don't Repeat Yourself) Principle Analyzer

This script analyzes Python files to identify potential violations of the DRY principle.
It detects patterns that indicate code duplication:
1. Duplicate code blocks
2. Similar method signatures
3. Repeated string literals
4. Repeated numeric constants
5. Repeated code patterns

Usage:
    python analyze_dry.py <file_or_directory_path>
"""

import os
import sys
import ast
import re
import difflib
import hashlib
import logging
import keyword
import tokenize
import io
from typing import Dict, List
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DRYAnalyzer:
    """Analyzes Python code for DRY principle violations."""

    def __init__(
        self,
        min_duplicate_lines: int = 3,
        similarity_threshold: float = 0.8,
        min_string_length: int = 10,
        min_string_occurrences: int = 3
    ):
        self.min_duplicate_lines = min_duplicate_lines
        self.similarity_threshold = similarity_threshold
        self.min_string_length = min_string_length
        self.min_string_occurrences = min_string_occurrences

        # Storage for cross-file analysis
        self.all_methods = {}  # Maps method signature hash to method info
        self.all_strings = defaultdict(list)  # Maps string literals to their locations
        self.all_constants = defaultdict(list)  # Maps numeric constants to their locations
        self.code_blocks = defaultdict(list)  # Maps code block hashes to their locations

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a Python file for DRY violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            results = {
                "file_path": file_path,
                "duplicate_code_blocks": [],
                "similar_methods": [],
                "repeated_strings": [],
                "repeated_constants": [],
                "overall_dry_score": 1.0  # Will be updated based on violations
            }

            # Find duplicate code blocks
            duplicate_blocks = self._find_duplicate_code_blocks(content, file_path)
            if duplicate_blocks:
                results["duplicate_code_blocks"] = duplicate_blocks

            # Find similar methods
            similar_methods = self._find_similar_methods(tree, content, file_path)
            if similar_methods:
                results["similar_methods"] = similar_methods

            # Find repeated string literals
            repeated_strings = self._find_repeated_strings(tree, file_path)
            if repeated_strings:
                results["repeated_strings"] = repeated_strings

            # Find repeated numeric constants
            repeated_constants = self._find_repeated_constants(tree, file_path)
            if repeated_constants:
                results["repeated_constants"] = repeated_constants

            # Calculate overall DRY score
            violation_count = (
                len(duplicate_blocks) +
                len(similar_methods) +
                len(repeated_strings) +
                len(repeated_constants)
            )

            # Each violation reduces score by 0.1, with a minimum of 0.0
            results["overall_dry_score"] = max(0.0, 1.0 - (violation_count * 0.1))

            return results

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": str(e)}

    def _find_duplicate_code_blocks(self, content: str, file_path: str) -> List[Dict]:
        """Find duplicate code blocks in a file using token-based detection."""
        duplicates = []

        # Tokenize the file content
        try:
            # Convert content to bytes for tokenize
            content_bytes = io.BytesIO(content.encode('utf-8'))
            tokens = list(tokenize.tokenize(content_bytes.readline))

            # Filter and normalize tokens
            normalized_tokens = []
            line_map = {}  # Maps token positions to original line numbers

            for token in tokens:
                token_type = token.type
                token_string = token.string
                start_line = token.start[0]

                # Skip comments, whitespace, and newlines
                if token_type in (tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
                    continue

                # Normalize identifiers and literals
                if token_type == tokenize.NAME and not keyword.iskeyword(token_string):
                    # Replace variable/function names with a placeholder
                    normalized_token = "NAME"
                elif token_type == tokenize.STRING:
                    # Replace string literals with a placeholder
                    normalized_token = "STRING"
                elif token_type == tokenize.NUMBER:
                    # Replace numeric literals with a placeholder
                    normalized_token = "NUMBER"
                else:
                    # Keep other tokens as is
                    normalized_token = token_string

                normalized_tokens.append(normalized_token)
                line_map[len(normalized_tokens) - 1] = start_line

            # Find duplicate token sequences
            min_tokens = self.min_duplicate_lines * 5  # Rough estimate: 5 tokens per line
            token_count = len(normalized_tokens)

            # Use a sliding window approach with token sequences
            token_sequences = {}

            for i in range(token_count - min_tokens + 1):
                # Create a sequence of tokens
                end_pos = min(i + 100, token_count)  # Limit sequence size
                token_seq = tuple(normalized_tokens[i:end_pos])

                if len(token_seq) < min_tokens:
                    continue

                # Hash the token sequence
                seq_hash = hashlib.md5(str(token_seq).encode()).hexdigest()

                # Store sequence info
                if seq_hash not in token_sequences:
                    token_sequences[seq_hash] = []

                # Find the corresponding line numbers in the original code
                start_line = line_map.get(i, 1)
                end_line = line_map.get(end_pos - 1, start_line + 1)

                # Extract the actual code block
                lines = content.splitlines()
                block = "\n".join(lines[start_line - 1:end_line])

                token_sequences[seq_hash].append({
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": block
                })

                # Store in global collection for cross-file analysis
                self.code_blocks[seq_hash].append({
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "code": block
                })
        except Exception as e:
            logger.warning(f"Error in token-based duplication detection: {str(e)}")
            # Fall back to line-based detection if tokenization fails
            logger.info("Falling back to line-based duplication detection")
            return self._find_duplicate_code_blocks_line_based(content, file_path)

        # Process token sequences to find duplicates
        for seq_hash, locations in self.code_blocks.items():
            # Only consider sequences with multiple occurrences
            if len(locations) < 2:
                continue

            # Only consider duplicates where at least one occurrence is in this file
            file_locations = [loc for loc in locations if loc["file_path"] == file_path]
            if not file_locations:
                continue

            # Create a duplicate entry
            duplicates.append({
                "code": locations[0]["code"],
                "occurrences": len(locations),
                "locations": locations,
                "severity": min(1.0, (len(locations) - 1) * 0.2)  # More occurrences = higher severity
            })

        return duplicates

    def _normalize_code_block(self, block: str) -> str:
        """Normalize a code block for comparison."""
        # Remove comments
        block = re.sub(r'#.*$', '', block, flags=re.MULTILINE)

        # Normalize whitespace
        block = re.sub(r'\s+', ' ', block)

        # Remove string literals
        block = re.sub(r'"[^"]*"', '""', block)
        block = re.sub(r"'[^']*'", "''", block)

        return block.strip()

    def _find_duplicate_code_blocks_line_based(self, content: str, file_path: str) -> List[Dict]:
        """Find duplicate code blocks in a file using line-based detection (fallback method)."""
        lines = content.splitlines()
        line_count = len(lines)
        duplicates = []

        # Generate hashes for all possible code blocks of minimum size
        for i in range(line_count - self.min_duplicate_lines + 1):
            for j in range(i + self.min_duplicate_lines, min(i + 30, line_count) + 1):  # Limit block size to 30 lines
                block = "\n".join(lines[i:j])
                # Normalize whitespace and comments
                normalized_block = self._normalize_code_block(block)
                if not normalized_block.strip():
                    continue

                block_hash = hashlib.md5(normalized_block.encode()).hexdigest()

                # Store block info
                self.code_blocks[block_hash].append({
                    "file_path": file_path,
                    "start_line": i + 1,  # 1-indexed
                    "end_line": j,
                    "code": block
                })

        # Find duplicates within this file
        for block_hash, locations in self.code_blocks.items():
            # Only consider blocks with multiple occurrences
            if len(locations) < 2:
                continue

            # Only consider duplicates where at least one occurrence is in this file
            file_locations = [loc for loc in locations if loc["file_path"] == file_path]
            if not file_locations:
                continue

            # Create a duplicate entry
            duplicates.append({
                "code": locations[0]["code"],
                "occurrences": len(locations),
                "locations": locations,
                "severity": min(1.0, (len(locations) - 1) * 0.2)  # More occurrences = higher severity
            })

        return duplicates

    def _find_similar_methods(self, tree: ast.AST, content: str, file_path: str) -> List[Dict]:
        """Find similar methods in a file."""
        similar_methods = []

        # Extract all methods from the file
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                method_source = self._get_node_source(node, content)

                # Create a signature for the method
                param_types = []
                for arg in node.args.args:
                    if hasattr(arg, 'annotation') and arg.annotation:
                        param_types.append(self._get_annotation_name(arg.annotation))
                    else:
                        param_types.append("any")

                return_type = "any"
                if hasattr(node, 'returns') and node.returns:
                    return_type = self._get_annotation_name(node.returns)

                # Create a normalized version of the method body for comparison
                method_body = self._normalize_method_body(node, content)

                method_info = {
                    "name": node.name,
                    "file_path": file_path,
                    "line_number": node.lineno,
                    "param_count": len(node.args.args),
                    "param_types": param_types,
                    "return_type": return_type,
                    "source": method_source,
                    "body": method_body
                }

                # Generate a hash for the method signature
                signature = f"{len(param_types)}:{','.join(param_types)}:{return_type}"
                signature_hash = hashlib.md5(signature.encode()).hexdigest()

                # Store method info
                if signature_hash in self.all_methods:
                    # Check similarity with existing method
                    existing_method = self.all_methods[signature_hash]
                    similarity = self._calculate_similarity(method_body, existing_method["body"])

                    if similarity >= self.similarity_threshold:
                        similar_methods.append({
                            "method1": {
                                "name": method_info["name"],
                                "file_path": method_info["file_path"],
                                "line_number": method_info["line_number"]
                            },
                            "method2": {
                                "name": existing_method["name"],
                                "file_path": existing_method["file_path"],
                                "line_number": existing_method["line_number"]
                            },
                            "similarity": similarity,
                            "severity": min(1.0, similarity - self.similarity_threshold + 0.2)
                        })

                # Store this method for future comparisons
                self.all_methods[signature_hash] = method_info

                # Also compare with all other methods regardless of signature
                for other_hash, other_method in self.all_methods.items():
                    if other_hash == signature_hash:
                        continue

                    # Skip methods from the same file (already compared)
                    if other_method["file_path"] == file_path:
                        continue

                    similarity = self._calculate_similarity(method_body, other_method["body"])

                    if similarity >= self.similarity_threshold:
                        similar_methods.append({
                            "method1": {
                                "name": method_info["name"],
                                "file_path": method_info["file_path"],
                                "line_number": method_info["line_number"]
                            },
                            "method2": {
                                "name": other_method["name"],
                                "file_path": other_method["file_path"],
                                "line_number": other_method["line_number"]
                            },
                            "similarity": similarity,
                            "severity": min(1.0, similarity - self.similarity_threshold + 0.2)
                        })

        return similar_methods

    def _normalize_method_body(self, node: ast.FunctionDef, content: str) -> str:
        """Normalize a method body for comparison."""
        # Get the method body source code
        if not hasattr(node, 'body'):
            return ""

        body_source = ""
        for stmt in node.body:
            if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                stmt_source = self._get_node_source(stmt, content)
                body_source += stmt_source + "\n"

        # Normalize the body
        # Remove comments
        body_source = re.sub(r'#.*$', '', body_source, flags=re.MULTILINE)

        # Normalize variable names
        var_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        variables = re.findall(var_pattern, body_source)
        var_map = {}
        var_counter = 0

        for var in variables:
            if var not in var_map and not keyword.iskeyword(var):
                var_map[var] = f"var{var_counter}"
                var_counter += 1

        for var, replacement in var_map.items():
            body_source = re.sub(r'\b' + var + r'\b', replacement, body_source)

        # Normalize whitespace
        body_source = re.sub(r'\s+', ' ', body_source)

        return body_source.strip()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using difflib."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def _find_repeated_strings(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Find repeated string literals in a file."""
        repeated_strings = []
        string_occurrences = defaultdict(list)

        # Find all string literals
        for node in ast.walk(tree):
            # Handle both Python 3.8+ (Constant) and older versions (Str)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) >= self.min_string_length:
                string_value = node.value
                string_occurrences[string_value].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

                # Also store in global collection
                self.all_strings[string_value].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
            # For backward compatibility with Python < 3.8
            elif hasattr(ast, 'Str') and isinstance(node, ast.Str) and len(node.s) >= self.min_string_length:
                string_occurrences[node.s].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

                # Also store in global collection
                self.all_strings[node.s].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

        # Find strings with multiple occurrences
        for string, occurrences in string_occurrences.items():
            if len(occurrences) >= self.min_string_occurrences:
                repeated_strings.append({
                    "string": string,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })

        # Also check global collection for strings that appear in multiple files
        for string, occurrences in self.all_strings.items():
            # Skip strings already reported
            if string in string_occurrences and len(string_occurrences[string]) >= self.min_string_occurrences:
                continue

            # Check if this string appears in this file and others
            file_occurrences = [o for o in occurrences if o["file_path"] == file_path]
            if file_occurrences and len(occurrences) >= self.min_string_occurrences:
                repeated_strings.append({
                    "string": string,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })

        return repeated_strings

    def _find_repeated_constants(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Find repeated numeric constants in a file."""
        repeated_constants = []
        constant_occurrences = defaultdict(list)

        # Find all numeric constants
        for node in ast.walk(tree):
            # Handle both Python 3.8+ (Constant) and older versions (Num)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip common constants like 0, 1, -1
                if node.value in (0, 1, -1):
                    continue

                constant_occurrences[node.value].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

                # Also store in global collection
                self.all_constants[node.value].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })
            # For backward compatibility with Python < 3.8
            elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
                # Skip common constants like 0, 1, -1
                if node.n in (0, 1, -1):
                    continue

                constant_occurrences[node.n].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

                # Also store in global collection
                self.all_constants[node.n].append({
                    "file_path": file_path,
                    "line_number": node.lineno
                })

        # Find constants with multiple occurrences
        for constant, occurrences in constant_occurrences.items():
            if len(occurrences) >= self.min_string_occurrences:
                repeated_constants.append({
                    "constant": constant,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })

        # Also check global collection for constants that appear in multiple files
        for constant, occurrences in self.all_constants.items():
            # Skip constants already reported
            if constant in constant_occurrences and len(constant_occurrences[constant]) >= self.min_string_occurrences:
                continue

            # Check if this constant appears in this file and others
            file_occurrences = [o for o in occurrences if o["file_path"] == file_path]
            if file_occurrences and len(occurrences) >= self.min_string_occurrences:
                repeated_constants.append({
                    "constant": constant,
                    "occurrences": len(occurrences),
                    "locations": occurrences,
                    "severity": min(1.0, (len(occurrences) - self.min_string_occurrences + 1) * 0.1)
                })

        return repeated_constants

    def _get_node_source(self, node: ast.AST, content: str) -> str:
        """Get source code for an AST node."""
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return ""

        lines = content.splitlines()
        start_line = node.lineno - 1  # 0-indexed
        end_line = getattr(node, 'end_lineno', len(lines)) - 1

        return "\n".join(lines[start_line:end_line+1])

    def _get_annotation_name(self, annotation: ast.AST) -> str:
        """Extract the name from a type annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id
        return "any"

    def generate_recommendations(self, results: Dict) -> Dict:
        """Generate refactoring recommendations based on analysis."""
        recommendations = {}

        # Recommendations for duplicate code blocks
        if results.get("duplicate_code_blocks"):
            block_recs = []
            for block in results["duplicate_code_blocks"]:
                rec = f"Extract duplicate code block (found in {block['occurrences']} locations) into a reusable function or method."
                block_recs.append(rec)
            recommendations["duplicate_code_blocks"] = block_recs

        # Recommendations for similar methods
        if results.get("similar_methods"):
            method_recs = []
            for methods in results["similar_methods"]:
                rec = f"Methods '{methods['method1']['name']}' and '{methods['method2']['name']}' are {methods['similarity']:.0%} similar. Consider extracting common functionality."
                method_recs.append(rec)
            recommendations["similar_methods"] = method_recs

        # Recommendations for repeated strings
        if results.get("repeated_strings"):
            string_recs = []
            for string in results["repeated_strings"]:
                rec = f"String '{string['string'][:30]}...' is repeated {string['occurrences']} times. Consider defining it as a constant."
                string_recs.append(rec)
            recommendations["repeated_strings"] = string_recs

        # Recommendations for repeated constants
        if results.get("repeated_constants"):
            constant_recs = []
            for constant in results["repeated_constants"]:
                rec = f"Constant {constant['constant']} is repeated {constant['occurrences']} times. Consider defining it as a named constant."
                constant_recs.append(rec)
            recommendations["repeated_constants"] = constant_recs

        return recommendations


def analyze_directory(directory_path: str, analyzer: DRYAnalyzer) -> List[Dict]:
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
    print("\n===== DRY PRINCIPLE ANALYSIS =====\n")

    violations_found = False

    for result in results:
        if "error" in result:
            print(f"Error analyzing {result['file_path']}: {result['error']}")
            continue

        print(f"File: {result['file_path']}")
        print(f"Overall DRY Score: {result['overall_dry_score']:.2f}/1.00")

        # Generate recommendations
        analyzer = DRYAnalyzer()
        recommendations = analyzer.generate_recommendations(result)

        # Print duplicate code blocks
        if result.get("duplicate_code_blocks"):
            violations_found = True
            print(f"\n  Duplicate Code Blocks: {len(result['duplicate_code_blocks'])}")
            for i, block in enumerate(result["duplicate_code_blocks"][:3]):  # Show first 3
                print(f"    {i+1}. Found in {block['occurrences']} locations")
                print(f"       First few lines: {block['code'].split('\\n')[0][:50]}...")
                print(f"       RECOMMENDATION: {recommendations['duplicate_code_blocks'][i]}")
            if len(result["duplicate_code_blocks"]) > 3:
                print(f"    ... and {len(result['duplicate_code_blocks']) - 3} more")

        # Print similar methods
        if result.get("similar_methods"):
            violations_found = True
            print(f"\n  Similar Methods: {len(result['similar_methods'])}")
            for i, methods in enumerate(result["similar_methods"][:3]):  # Show first 3
                print(f"    {i+1}. {methods['method1']['name']} (line {methods['method1']['line_number']}) and "
                      f"{methods['method2']['name']} (in {os.path.basename(methods['method2']['file_path'])}, line {methods['method2']['line_number']})")
                print(f"       Similarity: {methods['similarity']:.0%}")
                print(f"       RECOMMENDATION: {recommendations['similar_methods'][i]}")
            if len(result["similar_methods"]) > 3:
                print(f"    ... and {len(result['similar_methods']) - 3} more")

        # Print repeated strings
        if result.get("repeated_strings"):
            violations_found = True
            print(f"\n  Repeated Strings: {len(result['repeated_strings'])}")
            for i, string in enumerate(result["repeated_strings"][:3]):  # Show first 3
                print(f"    {i+1}. '{string['string'][:30]}...' repeated {string['occurrences']} times")
                print(f"       RECOMMENDATION: {recommendations['repeated_strings'][i]}")
            if len(result["repeated_strings"]) > 3:
                print(f"    ... and {len(result['repeated_strings']) - 3} more")

        # Print repeated constants
        if result.get("repeated_constants"):
            violations_found = True
            print(f"\n  Repeated Constants: {len(result['repeated_constants'])}")
            for i, constant in enumerate(result["repeated_constants"][:3]):  # Show first 3
                print(f"    {i+1}. {constant['constant']} repeated {constant['occurrences']} times")
                print(f"       RECOMMENDATION: {recommendations['repeated_constants'][i]}")
            if len(result["repeated_constants"]) > 3:
                print(f"    ... and {len(result['repeated_constants']) - 3} more")

        print("\n" + "-" * 60)

    if not violations_found:
        print("\nNo DRY violations detected! 🎉")
    else:
        print("\nDRY violations detected. Consider refactoring the flagged code.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory_path>")
        sys.exit(1)

    path = sys.argv[1]
    analyzer = DRYAnalyzer()

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
