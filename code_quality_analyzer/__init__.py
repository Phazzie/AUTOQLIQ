"""Code Quality Analyzer package.

This package provides tools for analyzing code quality according to SOLID, KISS, and DRY principles.
"""

from .unified_analyzer import UnifiedAnalyzer
from .base_analyzer import BaseAnalyzer

# SOLID Principle Analyzers
from .analyzers.srp_analyzer import SRPAnalyzer     # Single Responsibility Principle
from .analyzers.ocp_analyzer import OCPAnalyzer     # Open/Closed Principle
from .analyzers.lsp_analyzer import LSPAnalyzer     # Liskov Substitution Principle
from .analyzers.isp_analyzer import ISPAnalyzer     # Interface Segregation Principle
from .analyzers.dip_analyzer import DIPAnalyzer     # Dependency Inversion Principle

# Other Code Quality Analyzers
from .analyzers.kiss_analyzer import KISSAnalyzer    # Keep It Simple, Stupid
from .analyzers.dry_analyzer import DRYAnalyzer      # Don't Repeat Yourself

__version__ = '0.1.0'
__all__ = [
    'UnifiedAnalyzer', 'BaseAnalyzer',
    # SOLID Principle Analyzers
    'SRPAnalyzer',   # Single Responsibility Principle
    'OCPAnalyzer',   # Open/Closed Principle
    'LSPAnalyzer',   # Liskov Substitution Principle
    'ISPAnalyzer',   # Interface Segregation Principle
    'DIPAnalyzer',   # Dependency Inversion Principle
    # Other Code Quality Analyzers
    'KISSAnalyzer',  # Keep It Simple, Stupid
    'DRYAnalyzer',   # Don't Repeat Yourself
]
