#!/usr/bin/env python
"""
Code Quality Dashboard

A modern, sleek GUI for running and visualizing code quality analysis.
"""

import os
import sys
import json
import subprocess
import threading
import importlib.util
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QProgressBar, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QSplitter, QFrame, QComboBox,
    QCheckBox, QLineEdit, QMessageBox, QTextEdit, QScrollArea,
    QGridLayout, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, QUrl
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

# Try to import the unified analyzer
try:
    from code_quality_analyzer.unified_analyzer import UnifiedAnalyzer
    UNIFIED_ANALYZER_AVAILABLE = True
except ImportError:
    UNIFIED_ANALYZER_AVAILABLE = False

# Define color scheme
COLORS = {
    "background": "#1E1E1E",
    "card_bg": "#252526",
    "accent": "#007ACC",
    "text": "#CCCCCC",
    "success": "#6A9955",
    "warning": "#FFCC00",
    "error": "#F14C4C",
    "chart_colors": ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6"]
}

class AnalyzerThread(QThread):
    """Thread for running code analysis without blocking the UI."""
    progress_update = pyqtSignal(int, str)
    analysis_complete = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, analyzer_type, target_path, options=None):
        super().__init__()
        self.analyzer_type = analyzer_type
        self.target_path = target_path
        self.options = options or {}
        
    def run(self):
        try:
            self.progress_update.emit(10, f"Starting {self.analyzer_type} analysis...")
            
            if self.analyzer_type == "unified" and UNIFIED_ANALYZER_AVAILABLE:
                # Use the unified analyzer directly
                analyzer = UnifiedAnalyzer(config=self.options)
                
                if os.path.isfile(self.target_path):
                    self.progress_update.emit(30, f"Analyzing file: {os.path.basename(self.target_path)}")
                    results = analyzer.analyze_file(self.target_path)
                else:
                    self.progress_update.emit(30, f"Analyzing directory: {os.path.basename(self.target_path)}")
                    results = analyzer.analyze_directory(self.target_path)
                
                self.progress_update.emit(90, "Processing results...")
                self.analysis_complete.emit(results)
                
            else:
                # Run the appropriate script as a subprocess
                script_path = self._get_script_path(self.analyzer_type)
                
                if not script_path:
                    self.analysis_error.emit(f"Could not find script for {self.analyzer_type} analyzer")
                    return
                
                self.progress_update.emit(30, f"Running {os.path.basename(script_path)}...")
                
                cmd = [sys.executable, script_path, self.target_path]
                
                # Add any options as command-line arguments
                for key, value in self.options.items():
                    cmd.extend([f"--{key}", str(value)])
                
                self.progress_update.emit(50, "Executing analysis...")
                
                # Run the process and capture output
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    self.analysis_error.emit(f"Analysis failed: {stderr}")
                    return
                
                self.progress_update.emit(80, "Processing results...")
                
                # Try to parse the output as JSON
                try:
                    results = json.loads(stdout)
                except json.JSONDecodeError:
                    # If not JSON, return as text
                    results = {"raw_output": stdout}
                
                self.progress_update.emit(90, "Analysis complete!")
                self.analysis_complete.emit(results)
                
        except Exception as e:
            self.analysis_error.emit(f"Error during analysis: {str(e)}")
    
    def _get_script_path(self, analyzer_type):
        """Get the path to the analyzer script."""
        # Map analyzer types to script paths
        script_map = {
            "missing_files": "check_missing_files.py",
            "package_size": "analyze_package_size.py",
            "test_analyzers": "test_analyzers.py",
            "srp": "code_quality_analyzer/analyzers/srp_analyzer.py",
            "ocp": "code_quality_analyzer/analyzers/ocp_analyzer.py",
            "lsp": "code_quality_analyzer/analyzers/lsp_analyzer.py",
            "isp": "code_quality_analyzer/analyzers/isp_analyzer.py",
            "dip": "code_quality_analyzer/analyzers/dip_analyzer.py",
            "kiss": "code_quality_analyzer/analyzers/kiss_analyzer.py",
            "dry": "code_quality_analyzer/analyzers/dry_analyzer.py"
        }
        
        if analyzer_type in script_map:
            script_path = script_map[analyzer_type]
            if os.path.exists(script_path):
                return script_path
        
        return None


class AnalyzerCard(QFrame):
    """A card widget for an individual analyzer."""
    
    def __init__(self, title, description, analyzer_type, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.analyzer_type = analyzer_type
        self.parent_dashboard = parent
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid #3E3E3E;
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0086E3;
            }}
            QPushButton:pressed {{
                background-color: #005999;
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Spacer
        layout.addStretch(1)
        
        # Run button
        run_button = QPushButton("Run Analysis")
        run_button.setFixedHeight(36)
        run_button.clicked.connect(self.run_analysis)
        layout.addWidget(run_button)
        
        self.setLayout(layout)
        self.setMinimumHeight(180)
    
    def run_analysis(self):
        """Run the analyzer when the button is clicked."""
        if self.parent_dashboard:
            self.parent_dashboard.run_analyzer(self.analyzer_type)


class ResultsViewer(QWidget):
    """Widget for displaying analysis results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Tabs for different result views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #3E3E3E;
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                border: 1px solid #3E3E3E;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['card_bg']};
                border-bottom: none;
            }}
        """)
        
        # Summary tab
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_layout.addWidget(self.summary_text)
        self.tabs.addTab(self.summary_tab, "Summary")
        
        # Details tab
        self.details_tab = QWidget()
        self.details_layout = QVBoxLayout(self.details_tab)
        self.details_tree = QTreeWidget()
        self.details_tree.setHeaderLabels(["Property", "Value"])
        self.details_tree.setAlternatingRowColors(True)
        self.details_layout.addWidget(self.details_tree)
        self.tabs.addTab(self.details_tab, "Details")
        
        # Visualization tab
        self.viz_tab = QWidget()
        self.viz_layout = QVBoxLayout(self.viz_tab)
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(self.chart_view.RenderHint.Antialiasing)
        self.viz_layout.addWidget(self.chart_view)
        self.tabs.addTab(self.viz_tab, "Visualization")
        
        # Raw output tab
        self.raw_tab = QWidget()
        self.raw_layout = QVBoxLayout(self.raw_tab)
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setFont(QFont("Consolas", 10))
        self.raw_layout.addWidget(self.raw_text)
        self.tabs.addTab(self.raw_tab, "Raw Output")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def display_results(self, results):
        """Display the analysis results."""
        # Clear previous results
        self.summary_text.clear()
        self.details_tree.clear()
        self.raw_text.clear()
        
        # Set raw output
        if isinstance(results, dict):
            self.raw_text.setText(json.dumps(results, indent=2))
        else:
            self.raw_text.setText(str(results))
        
        # Generate summary
        summary = self._generate_summary(results)
        self.summary_text.setText(summary)
        
        # Populate details tree
        self._populate_details_tree(results)
        
        # Create visualization
        self._create_visualization(results)
    
    def _generate_summary(self, results):
        """Generate a summary of the analysis results."""
        if not isinstance(results, dict):
            return "No summary available for this analysis."
        
        summary = "<h2>Analysis Summary</h2>"
        
        # Check for common result patterns
        if "violations" in results:
            violations = results["violations"]
            if isinstance(violations, list):
                summary += f"<p>Found {len(violations)} violations.</p>"
                
                if violations:
                    summary += "<ul>"
                    for violation in violations[:5]:  # Show first 5
                        if isinstance(violation, dict) and "message" in violation:
                            summary += f"<li>{violation['message']}</li>"
                        else:
                            summary += f"<li>{str(violation)}</li>"
                    
                    if len(violations) > 5:
                        summary += f"<li>... and {len(violations) - 5} more</li>"
                    
                    summary += "</ul>"
                else:
                    summary += "<p>No violations found. Great job!</p>"
        
        elif "files" in results:
            files = results["files"]
            if isinstance(files, dict):
                total_files = len(files)
                files_with_issues = sum(bool(isinstance(f, dict) and f.get("issues", []))
                
                summary += f"<p>Analyzed {total_files} files, found issues in {files_with_issues} files.</p>"
                
                if files_with_issues > 0:
                    summary += "<ul>"
                    count = 0
                    for filename, file_data in files.items():
                        if isinstance(file_data, dict) and file_data.get("issues", []):
                            issues = file_data["issues"]
                            summary += f"<li>{filename}: {len(issues)} issues</li>"
                            count += 1
                            if count >= 5:
                                break
                    
                    if files_with_issues > 5:
                        summary += f"<li>... and {files_with_issues - 5} more files with issues</li>"
                    
                    summary += "</ul>"
        
        elif "missing_files" in results:
            missing = results["missing_files"]
            if isinstance(missing, list):
                summary += f"<p>Found {len(missing)} missing files.</p>"
                
                if missing:
                    summary += "<ul>"
                    for file in missing[:10]:  # Show first 10
                        summary += f"<li>{file}</li>"
                    
                    if len(missing) > 10:
                        summary += f"<li>... and {len(missing) - 10} more</li>"
                    
                    summary += "</ul>"
                else:
                    summary += "<p>No missing files found. Great job!</p>"
        
        else:
            # Generic summary for unknown result format
            summary += "<p>Analysis completed successfully.</p>"
            summary += "<p>See the Details tab for more information.</p>"
        
        return summary
    
    def _populate_details_tree(self, results):
        """Populate the details tree with the analysis results."""
        if not isinstance(results, dict):
            item = QTreeWidgetItem(["Results", str(results)])
            self.details_tree.addTopLevelItem(item)
            return
        
        def add_dict_to_tree(parent_item, data):
            """Recursively add dictionary data to the tree."""
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        item = QTreeWidgetItem([str(key), ""])
                        if parent_item is None:
                            self.details_tree.addTopLevelItem(item)
                        else:
                            parent_item.addChild(item)
                        
                        if isinstance(value, dict):
                            add_dict_to_tree(item, value)
                        elif isinstance(value, list):
                            for i, list_item in enumerate(value):
                                if isinstance(list_item, (dict, list)):
                                    list_item_widget = QTreeWidgetItem([f"Item {i}", ""])
                                    item.addChild(list_item_widget)
                                    add_dict_to_tree(list_item_widget, list_item)
                                else:
                                    item.addChild(QTreeWidgetItem(["", str(list_item)]))
                    else:
                        if parent_item is None:
                            self.details_tree.addTopLevelItem(QTreeWidgetItem([str(key), str(value)]))
                        else:
                            parent_item.addChild(QTreeWidgetItem([str(key), str(value)]))
        
        add_dict_to_tree(None, results)
        self.details_tree.expandToDepth(0)
    
    def _create_visualization(self, results):
        """Create a visualization of the analysis results."""
        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.setTheme(QChart.ChartThemeDark)
        chart.setTitle("Analysis Results")
        
        # Try to determine the best visualization based on the results
        if isinstance(results, dict):
            if "violations" in results and isinstance(results["violations"], list):
                # Group violations by type
                violation_types = {}
                for violation in results["violations"]:
                    if isinstance(violation, dict) and "type" in violation:
                        vtype = violation["type"]
                        violation_types[vtype] = violation_types.get(vtype, 0) + 1
                    
                if violation_types:
                    # Create pie chart for violation types
                    series = QPieSeries()
                    for vtype, count in violation_types.items():
                        slice = series.append(f"{vtype} ({count})", count)
                        slice.setBrush(QColor(COLORS["chart_colors"][len(series) % len(COLORS["chart_colors"])]))
                    
                    chart.addSeries(series)
                    chart.setTitle("Violations by Type")
                    
                    self.chart_view.setChart(chart)
                    return
            
            elif "files" in results and isinstance(results["files"], dict):
                # Create bar chart for files with issues
                files_with_issues = {}
                for filename, file_data in results["files"].items():
                    if isinstance(file_data, dict) and "issues" in file_data:
                        issues = file_data["issues"]
                        if isinstance(issues, list) and issues:
                            files_with_issues[filename] = len(issues)
                
                if files_with_issues:
                    # Sort by number of issues (descending)
                    sorted_files = sorted(files_with_issues.items(), key=lambda x: x[1], reverse=True)
                    
                    # Take top 10 files
                    top_files = sorted_files[:10]
                    
                    # Create bar chart
                    bar_set = QBarSet("Issues")
                    categories = []
                    
                    for filename, count in top_files:
                        bar_set.append(count)
                        # Use just the filename, not the full path
                        categories.append(os.path.basename(filename))
                    
                    bar_series = QBarSeries()
                    bar_series.append(bar_set)
                    
                    chart.addSeries(bar_series)
                    
                    axis_x = QBarCategoryAxis()
                    axis_x.append(categories)
                    chart.addAxis(axis_x, Qt.AlignBottom)
                    bar_series.attachAxis(axis_x)
                    
                    axis_y = QValueAxis()
                    axis_y.setRange(0, max(files_with_issues.values()) * 1.1)
                    chart.addAxis(axis_y, Qt.AlignLeft)
                    bar_series.attachAxis(axis_y)
                    
                    chart.setTitle("Files with Most Issues")
                    
                    self.chart_view.setChart(chart)
                    return
        
        # Default visualization if no specific one could be created
        label = QLabel("No visualization available for this analysis.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {COLORS['text']};")
        
        # Replace the chart view with the label
        if self.viz_layout.count() > 0:
            self.viz_layout.itemAt(0).widget().deleteLater()
        
        self.viz_layout.addWidget(label)


class CodeQualityDashboard(QMainWindow):
    """Main dashboard window for code quality analysis."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Quality Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Initialize UI
        self.init_ui()
    
    def set_dark_theme(self):
        """Set dark theme for the application."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLORS["background"]))
        palette.setColor(QPalette.WindowText, QColor(COLORS["text"]))
        palette.setColor(QPalette.Base, QColor(COLORS["card_bg"]))
        palette.setColor(QPalette.AlternateBase, QColor("#2D2D30"))
        palette.setColor(QPalette.ToolTipBase, QColor(COLORS["text"]))
        palette.setColor(QPalette.ToolTipText, QColor(COLORS["text"]))
        palette.setColor(QPalette.Text, QColor(COLORS["text"]))
        palette.setColor(QPalette.Button, QColor(COLORS["card_bg"]))
        palette.setColor(QPalette.ButtonText, QColor(COLORS["text"]))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(COLORS["accent"]))
        palette.setColor(QPalette.Highlight, QColor(COLORS["accent"]))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(palette)
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Code Quality Dashboard")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch(1)
        
        # Target selection
        self.target_path = QLineEdit()
        self.target_path.setPlaceholderText("Select a file or directory to analyze")
        self.target_path.setMinimumWidth(400)
        header_layout.addWidget(self.target_path)
        
        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_target)
        header_layout.addWidget(browse_button)
        
        main_layout.addLayout(header_layout)
        
        # Splitter for cards and results
        splitter = QSplitter(Qt.Vertical)
        
        # Cards area
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        
        # Create analyzer cards
        analyzers = [
            ("Missing Files", "Check for missing important files in the project", "missing_files"),
            ("Package Size", "Analyze the size of packaged codebase files", "package_size"),
            ("SRP Analyzer", "Check for Single Responsibility Principle violations", "srp"),
            ("OCP Analyzer", "Check for Open/Closed Principle violations", "ocp"),
            ("LSP Analyzer", "Check for Liskov Substitution Principle violations", "lsp"),
            ("ISP Analyzer", "Check for Interface Segregation Principle violations", "isp"),
            ("DIP Analyzer", "Check for Dependency Inversion Principle violations", "dip"),
            ("KISS Analyzer", "Check for Keep It Simple, Stupid violations", "kiss"),
            ("DRY Analyzer", "Check for Don't Repeat Yourself violations", "dry")
        ]
        
        row, col = 0, 0
        for title, description, analyzer_type in analyzers:
            card = AnalyzerCard(title, description, analyzer_type, self)
            cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1
        
        # Add unified analyzer card if available
        if UNIFIED_ANALYZER_AVAILABLE:
            unified_card = AnalyzerCard(
                "Unified Analysis", 
                "Run all analyzers at once for comprehensive results", 
                "unified",
                self
            )
            cards_layout.addWidget(unified_card, row, col)
        
        splitter.addWidget(cards_widget)
        
        # Results area
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        results_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Select a file or directory and run an analyzer")
        self.status_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.status_label)
        
        # Results viewer
        self.results_viewer = ResultsViewer()
        results_layout.addWidget(self.results_viewer)
        
        splitter.addWidget(results_widget)
        
        # Set initial splitter sizes (30% cards, 70% results)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Current analyzer thread
        self.current_analyzer_thread = None
    
    def browse_target(self):
        """Open a file dialog to select a target file or directory."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        dialog = QFileDialog(self, "Select File or Directory", "", "Python Files (*.py);;All Files (*)")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setOptions(options)
        
        # Add a button to select directories
        dir_button = QPushButton("Select Directory")
        dir_button.clicked.connect(lambda: dialog.setFileMode(QFileDialog.Directory))
        dialog.layout().addWidget(dir_button)
        
        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.target_path.setText(selected_files[0])
    
    def run_analyzer(self, analyzer_type):
        """Run the selected analyzer on the target path."""
        target_path = self.target_path.text()
        
        if not target_path:
            QMessageBox.warning(self, "No Target Selected", "Please select a file or directory to analyze.")
            return
        
        if not os.path.exists(target_path):
            QMessageBox.warning(self, "Invalid Path", f"The path '{target_path}' does not exist.")
            return
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Running {analyzer_type} analysis...")
        
        # Create and start analyzer thread
        self.current_analyzer_thread = AnalyzerThread(analyzer_type, target_path)
        self.current_analyzer_thread.progress_update.connect(self.update_progress)
        self.current_analyzer_thread.analysis_complete.connect(self.analysis_complete)
        self.current_analyzer_thread.analysis_error.connect(self.analysis_error)
        self.current_analyzer_thread.start()
    
    def update_progress(self, value, message):
        """Update the progress bar and status message."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def analysis_complete(self, results):
        """Handle completed analysis."""
        self.progress_bar.setValue(100)
        self.status_label.setText("Analysis complete!")
        
        # Display results
        self.results_viewer.display_results(results)
        
        # Hide progress bar after a delay
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def analysis_error(self, error_message):
        """Handle analysis error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")
        
        QMessageBox.critical(self, "Analysis Error", error_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better dark theme support
    
    dashboard = CodeQualityDashboard()
    dashboard.show()
    
    sys.exit(app.exec_())
