# Code Quality Analyzer

A comprehensive tool for analyzing code quality according to SOLID, KISS, and DRY principles.

## Features

- **SRP Analyzer**: Detects violations of the Single Responsibility Principle
- **KISS Analyzer**: Identifies complex code that violates the Keep It Simple, Stupid principle
- **DRY Analyzer**: Finds code duplication and other violations of the Don't Repeat Yourself principle
- **Unified Analysis**: Run all analyzers at once and get a combined report
- **Multiple Output Formats**: Generate reports in text, JSON, or HTML format
- **Caching**: Cache analysis results for faster subsequent runs
- **Parallel Processing**: Analyze directories in parallel for better performance

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-quality-analyzer.git

# Navigate to the directory
cd code-quality-analyzer

# Install the package
pip install -e .
```

## Usage

### Command-line Interface

```bash
# Analyze a file
python -m code_quality_analyzer path/to/file.py

# Analyze a directory
python -m code_quality_analyzer path/to/directory

# Analyze with specific analyzers
python -m code_quality_analyzer path/to/file.py --analyzers srp kiss

# Generate HTML report
python -m code_quality_analyzer path/to/file.py --format html --output report.html

# Use parallel processing for directory analysis
python -m code_quality_analyzer path/to/directory --parallel

# Cache analysis results
python -m code_quality_analyzer path/to/directory --cache
```

### Python API

```python
from code_quality_analyzer import UnifiedAnalyzer

# Create analyzer
analyzer = UnifiedAnalyzer()

# Analyze a file
results = analyzer.analyze_file('path/to/file.py')

# Analyze a directory
results = analyzer.analyze_directory('path/to/directory')

# Generate report
report = analyzer.generate_report(format='html', output_path='report.html')
```

## Configuration

### SRP Analyzer

- `max_responsibilities`: Maximum number of responsibilities per class (default: 1)
- `cohesion_threshold`: Minimum cohesion score for a class (default: 0.5)

### KISS Analyzer

- `max_method_lines`: Maximum number of lines per method (default: 20)
- `max_nesting_depth`: Maximum nesting depth (default: 3)
- `max_cyclomatic_complexity`: Maximum cyclomatic complexity (default: 10)
- `max_cognitive_complexity`: Maximum cognitive complexity (default: 15)
- `max_parameters`: Maximum number of parameters per method (default: 5)

### DRY Analyzer

- `min_duplicate_lines`: Minimum number of lines for a duplicate code block (default: 3)
- `similarity_threshold`: Minimum similarity threshold for duplicate code (default: 0.8)
- `min_string_length`: Minimum length for a string literal to be considered (default: 10)
- `min_string_occurrences`: Minimum number of occurrences for a string literal to be considered (default: 3)

## License

MIT
