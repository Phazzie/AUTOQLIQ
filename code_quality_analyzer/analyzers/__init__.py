"""Analyzers package for the Code Quality Analyzer.

This package provides individual analyzers for different code quality principles.
"""

# SOLID Principle Analyzers
from .srp_analyzer import SRPAnalyzer     # Single Responsibility Principle
from .ocp_analyzer import OCPAnalyzer     # Open/Closed Principle
from .lsp_analyzer import LSPAnalyzer     # Liskov Substitution Principle
from .isp_analyzer import ISPAnalyzer     # Interface Segregation Principle
from .dip_analyzer import DIPAnalyzer     # Dependency Inversion Principle

# Other Code Quality Analyzers
from .kiss_analyzer import KISSAnalyzer    # Keep It Simple, Stupid
from .dry_analyzer import DRYAnalyzer      # Don't Repeat Yourself

__all__ = [
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
