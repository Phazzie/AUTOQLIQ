"""Setup script for the Code Quality Analyzer package."""

from setuptools import setup, find_packages

setup(
    name="code_quality_analyzer",
    version="0.1.0",
    description="A tool for analyzing code quality according to SOLID, KISS, and DRY principles",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        'networkx',       # For dependency graph analysis
        'matplotlib',     # For visualization
        'jedi',           # For import resolution
        'radon',          # For cyclomatic complexity calculation
        'cognitive_complexity',  # For cognitive complexity calculation
    ],
    entry_points={
        "console_scripts": [
            "code-quality-analyzer=code_quality_analyzer.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
