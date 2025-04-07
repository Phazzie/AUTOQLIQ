"""Base analyzer module for code quality analysis.

This module provides a base class for all code quality analyzers, with common
functionality for file and directory analysis, caching, and reporting.
"""

import os
import ast
import logging
import pickle
import multiprocessing
from typing import Dict, List, Any, Optional, Set, Callable
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """Base class for all code quality analyzers.
    
    This class provides common functionality for analyzing files and directories,
    caching results, and generating reports.
    
    Attributes:
        name: The name of the analyzer
        description: A description of what the analyzer checks for
        cache_dir: Directory for caching analysis results
        results: Dictionary of analysis results
    """
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """Initialize a new BaseAnalyzer.
        
        Args:
            name: The name of the analyzer
            description: A description of what the analyzer checks for
            config: Optional configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.cache_dir = self.config.get('cache_dir', '.code_analysis_cache')
        self.results = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            A dictionary containing analysis results
        """
        # Check cache first if enabled
        if self.config.get('use_cache', False):
            cached_result = self._get_cached_result(file_path)
            if cached_result is not None:
                return cached_result
        
        try:
            # Try to read the file with utf-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fall back to latin-1 encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {str(e)}")
                return {"file_path": file_path, "error": f"File reading error: {str(e)}"}
        
        try:
            # Parse the file into an AST
            tree = ast.parse(content)
            
            # Call the implementation-specific analysis method
            result = self._analyze_file_impl(file_path, content, tree)
            
            # Cache the result if caching is enabled
            if self.config.get('use_cache', False):
                self._cache_result(file_path, result)
            
            return result
            
        except SyntaxError as e:
            logger.error(f"Syntax error in file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": f"Syntax error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "error": f"Analysis error: {str(e)}"}
    
    @abstractmethod
    def _analyze_file_impl(self, file_path: str, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Implementation-specific file analysis.
        
        This method must be implemented by subclasses to perform the actual analysis.
        
        Args:
            file_path: Path to the file being analyzed
            content: Content of the file
            tree: AST of the file
            
        Returns:
            A dictionary containing analysis results
        """
        pass
    
    def analyze_directory(self, directory_path: str, parallel: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to the directory to analyze
            parallel: Whether to use parallel processing
            
        Returns:
            A dictionary containing analysis results for all files
        """
        python_files = self._get_python_files(directory_path)
        
        if not python_files:
            logger.warning(f"No Python files found in {directory_path}")
            return {"files": [], "summary": {"file_count": 0}}
        
        # Analyze files
        if parallel and len(python_files) > 1:
            with multiprocessing.Pool() as pool:
                file_results = pool.map(self.analyze_file, python_files)
        else:
            file_results = [self.analyze_file(f) for f in python_files]
        
        # Generate summary
        summary = self._generate_summary(file_results)
        
        # Store results
        self.results = {
            "files": file_results,
            "summary": summary
        }
        
        return self.results
    
    def _get_python_files(self, directory_path: str) -> List[str]:
        """Get all Python files in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            A list of paths to Python files
        """
        python_files = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _generate_summary(self, file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of analysis results.
        
        Args:
            file_results: List of file analysis results
            
        Returns:
            A dictionary containing summary information
        """
        # Basic summary
        summary = {
            "file_count": len(file_results),
            "error_count": sum(1 for r in file_results if "error" in r),
            "analyzed_count": sum(1 for r in file_results if "error" not in r)
        }
        
        # Let subclasses add to the summary
        self._add_to_summary(summary, file_results)
        
        return summary
    
    def _add_to_summary(self, summary: Dict[str, Any], file_results: List[Dict[str, Any]]) -> None:
        """Add analyzer-specific information to the summary.
        
        This method can be overridden by subclasses to add additional information to the summary.
        
        Args:
            summary: The summary dictionary to add to
            file_results: List of file analysis results
        """
        pass
    
    def _get_cached_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Cached result, or None if not found
        """
        cache_file = self._get_cache_file_path(file_path)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    cached_result = pickle.load(f)
                
                # Check if the file has been modified since the cache was created
                if os.path.getmtime(file_path) <= os.path.getmtime(cache_file):
                    return cached_result
            except Exception as e:
                logger.warning(f"Error reading cache for {file_path}: {str(e)}")
        
        return None
    
    def _cache_result(self, file_path: str, result: Dict[str, Any]) -> None:
        """Cache analysis result for a file.
        
        Args:
            file_path: Path to the file
            result: Analysis result to cache
        """
        cache_file = self._get_cache_file_path(file_path)
        
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.warning(f"Error caching result for {file_path}: {str(e)}")
    
    def _get_cache_file_path(self, file_path: str) -> str:
        """Get the path to the cache file for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Path to the cache file
        """
        rel_path = os.path.relpath(file_path)
        cache_key = rel_path.replace(os.path.sep, '_')
        return os.path.join(self.cache_dir, f"{self.name}_{cache_key}.cache")
    
    def get_node_source(self, node: ast.AST, content: str) -> str:
        """Get source code for an AST node.
        
        Args:
            node: The AST node
            content: The source code
            
        Returns:
            The source code for the node
        """
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return ""
        
        lines = content.splitlines()
        start_line = node.lineno - 1  # 0-indexed
        end_line = getattr(node, 'end_lineno', len(lines)) - 1
        
        return "\n".join(lines[start_line:end_line+1])
    
    def generate_report(self, format: str = 'text') -> str:
        """Generate a report of analysis results.
        
        Args:
            format: The format of the report ('text', 'json', or 'html')
            
        Returns:
            The report as a string
        """
        if not self.results:
            return f"No analysis results available for {self.name}"
        
        if format == 'json':
            import json
            return json.dumps(self.results, indent=2)
        elif format == 'html':
            return self._generate_html_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a text report of analysis results.
        
        Returns:
            The report as a string
        """
        report = [f"===== {self.name} ====="]
        report.append(f"Description: {self.description}")
        report.append("")
        
        summary = self.results.get("summary", {})
        report.append(f"Files analyzed: {summary.get('analyzed_count', 0)}")
        report.append(f"Files with errors: {summary.get('error_count', 0)}")
        report.append("")
        
        # Let subclasses add to the report
        self._add_to_text_report(report)
        
        return "\n".join(report)
    
    def _add_to_text_report(self, report: List[str]) -> None:
        """Add analyzer-specific information to the text report.
        
        This method can be overridden by subclasses to add additional information to the report.
        
        Args:
            report: The report lines to add to
        """
        # Default implementation just lists files
        report.append("Files:")
        for file_result in self.results.get("files", []):
            file_path = file_result.get("file_path", "Unknown")
            if "error" in file_result:
                report.append(f"  {file_path}: Error - {file_result['error']}")
            else:
                report.append(f"  {file_path}")
    
    def _generate_html_report(self) -> str:
        """Generate an HTML report of analysis results.
        
        Returns:
            The report as an HTML string
        """
        # Basic HTML report
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{self.name} Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1 { color: #333; }",
            "h2 { color: #666; }",
            ".summary { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }",
            ".file { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }",
            ".file-header { display: flex; justify-content: space-between; }",
            ".file-path { font-weight: bold; }",
            ".file-score { font-weight: bold; }",
            ".good { color: green; }",
            ".warning { color: orange; }",
            ".bad { color: red; }",
            ".violation { margin-left: 20px; margin-bottom: 10px; }",
            ".recommendation { font-style: italic; color: #666; margin-top: 5px; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{self.name} Report</h1>",
            f"<p>{self.description}</p>",
            "<div class='summary'>",
            "<h2>Summary</h2>"
        ]
        
        summary = self.results.get("summary", {})
        html.append(f"<p>Files analyzed: {summary.get('analyzed_count', 0)}</p>")
        html.append(f"<p>Files with errors: {summary.get('error_count', 0)}</p>")
        
        # Let subclasses add to the summary
        self._add_to_html_summary(html)
        
        html.append("</div>")
        
        # Let subclasses add file details
        self._add_to_html_report(html)
        
        html.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)
    
    def _add_to_html_summary(self, html: List[str]) -> None:
        """Add analyzer-specific information to the HTML summary.
        
        This method can be overridden by subclasses to add additional information to the summary.
        
        Args:
            html: The HTML lines to add to
        """
        pass
    
    def _add_to_html_report(self, html: List[str]) -> None:
        """Add analyzer-specific information to the HTML report.
        
        This method can be overridden by subclasses to add additional information to the report.
        
        Args:
            html: The HTML lines to add to
        """
        # Default implementation just lists files
        html.append("<h2>Files</h2>")
        for file_result in self.results.get("files", []):
            file_path = file_result.get("file_path", "Unknown")
            html.append("<div class='file'>")
            html.append("<div class='file-header'>")
            html.append(f"<div class='file-path'>{file_path}</div>")
            html.append("</div>")
            
            if "error" in file_result:
                html.append(f"<p class='bad'>Error: {file_result['error']}</p>")
            
            html.append("</div>")
