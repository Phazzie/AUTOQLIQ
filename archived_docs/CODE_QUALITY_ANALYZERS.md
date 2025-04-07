# Code Quality Analyzers

**********ARCHIVED**********
Archived on: 2025-04-06


This directory contains a set of tools for analyzing code quality according to SOLID, KISS, and DRY principles.

## Individual Analyzers

### SOLID Principle Analyzers

#### 1. analyze_single_responsibility.py

Analyzes code for violations of the Single Responsibility Principle (SRP). It identifies:

- Classes with multiple responsibilities
- Low method cohesion
- Mixed concerns in a single class

#### 2. analyze_open_closed.py

Analyzes code for violations of the Open/Closed Principle (OCP). It identifies:

- Type checking with conditionals
- Switch/if-else chains based on type
- Concrete class instantiations
- Hardcoded behavior that should be extensible

#### 3. analyze_liskov_substitution.py

Analyzes code for violations of the Liskov Substitution Principle (LSP). It identifies:

- Method signature changes in overrides
- Precondition strengthening
- Postcondition weakening
- Exception type changes

#### 4. analyze_interface_segregation.py

Analyzes code for violations of the Interface Segregation Principle (ISP). It identifies:

- Large interfaces with many methods
- Classes implementing interfaces but not using all methods
- Interface methods with different client usage patterns
- Interfaces with low cohesion

#### 5. analyze_dependency_inversion.py

Analyzes code for violations of the Dependency Inversion Principle (DIP). It identifies:

- High-level modules depending on low-level modules
- Direct instantiation of concrete classes
- Missing abstractions/interfaces
- Concrete class dependencies in constructors
- Hardcoded dependencies

### Other Code Quality Analyzers

#### 6. analyze_kiss.py

Detects violations of the Keep It Simple, Stupid (KISS) principle. It identifies:

- Long methods (> 20 lines)
- Deep nesting (> 3 levels)
- Complex conditionals
- High cyclomatic complexity
- Excessive parameters
- High cognitive complexity

#### 7. analyze_dry.py

Identifies violations of the Don't Repeat Yourself (DRY) principle. It detects:

- Duplicate code blocks
- Similar method signatures
- Repeated string literals
- Repeated numeric constants

#### 8. analyze_responsibilities.py

Alternative analyzer for identifying responsibilities in files. It focuses on:

- Method naming patterns
- Responsibility grouping
- Multiple unrelated classes in a file

#### 9. count_responsibilities.py

Counts distinct responsibilities in files to help identify Single Responsibility Principle (SRP) violations. It uses:

- Natural language processing of docstrings and comments
- Method naming patterns
- Import categories
- Code structure analysis

## Integrated Suite

The `code_quality_analyzer` directory contains an integrated suite that combines all the individual analyzers into a unified interface with advanced features:

- Caching for faster subsequent runs
- Parallel processing for directory analysis
- Multiple output formats (text, JSON, HTML)
- Detailed reports with specific recommendations

## Installation

### Dependencies

Install the required dependencies:

```bash
python install_dependencies.py
```

This will install:

- networkx (for dependency graph analysis)
- matplotlib (for visualization)
- jedi (for import resolution)
- radon (for cyclomatic complexity calculation)
- cognitive_complexity (for cognitive complexity calculation)

## Usage

### Individual Analyzers

```bash
# SOLID Principle Analyzers
python analyze_single_responsibility.py path/to/file.py  # SRP
python analyze_open_closed.py path/to/file.py           # OCP
python analyze_liskov_substitution.py path/to/file.py   # LSP
python analyze_interface_segregation.py path/to/file.py # ISP
python analyze_dependency_inversion.py path/to/file.py  # DIP

# Other Code Quality Analyzers
python analyze_kiss.py path/to/file.py                  # KISS
python analyze_dry.py path/to/file.py                   # DRY
python analyze_responsibilities.py path/to/file.py      # Alternative SRP
python count_responsibilities.py path/to/file.py        # Responsibility counter
```

### Integrated Suite

```bash
# Analyze a file with all analyzers
python -m code_quality_analyzer path/to/file.py

# Analyze a directory
python -m code_quality_analyzer path/to/directory

# Generate HTML report
python -m code_quality_analyzer path/to/file.py --format html --output report.html

# Use parallel processing for directory analysis
python -m code_quality_analyzer path/to/directory --parallel

# Cache analysis results
python -m code_quality_analyzer path/to/directory --cache
```

## Testing

To test all analyzers on a sample file:

```bash
python test_analyzers.py
```

## VS Code Extension

A VS Code extension is available that integrates these analyzers into the editor. It provides:

- Real-time analysis as you type
- Inline diagnostics
- Quick fixes for common issues
- Detailed reports in a webview

To install the extension, see the `vscode-extension` directory.

## License

MIT
