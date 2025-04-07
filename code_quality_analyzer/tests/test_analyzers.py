"""Tests for the Code Quality Analyzer."""

import os
import sys
import unittest
import tempfile

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code_quality_analyzer import SRPAnalyzer, KISSAnalyzer, DRYAnalyzer, UnifiedAnalyzer

class TestAnalyzers(unittest.TestCase):
    """Tests for the Code Quality Analyzer."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary file with some code
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
        self.temp_file.write(b"""
class TooManyResponsibilities:
    def __init__(self):
        self.data = []
    
    def load_data(self):
        # This is a data access responsibility
        self.data = [1, 2, 3]
    
    def process_data(self):
        # This is a calculation responsibility
        return sum(self.data)
    
    def display_data(self):
        # This is a UI responsibility
        print(self.data)

def complex_method(data):
    # This is a complex method with deep nesting
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    for subitem in value:
                        if isinstance(subitem, str):
                            result.append(subitem.upper())
                        else:
                            result.append(str(subitem))
                else:
                    result.append(str(value))
        else:
            result.append(str(item))
    return result

# Duplicate code
def validate_email(email):
    return '@' in email and '.' in email

def validate_user(user):
    if not user.get('email'):
        return False
    return '@' in user.get('email') and '.' in user.get('email')
""")
        self.temp_file.close()
    
    def tearDown(self):
        """Tear down the test case."""
        os.unlink(self.temp_file.name)
    
    def test_srp_analyzer(self):
        """Test the SRP analyzer."""
        analyzer = SRPAnalyzer()
        result = analyzer.analyze_file(self.temp_file.name)
        
        # Check that the file was analyzed
        self.assertEqual(result['file_path'], self.temp_file.name)
        
        # Check that the class was analyzed
        self.assertEqual(len(result['class_analysis']), 1)
        
        # Check that the class has multiple responsibilities
        class_result = result['class_analysis'][0]
        self.assertEqual(class_result['class_name'], 'TooManyResponsibilities')
        self.assertGreater(len(class_result['responsibilities']), 1)
        self.assertTrue(class_result['srp_violations'])
    
    def test_kiss_analyzer(self):
        """Test the KISS analyzer."""
        analyzer = KISSAnalyzer()
        result = analyzer.analyze_file(self.temp_file.name)
        
        # Check that the file was analyzed
        self.assertEqual(result['file_path'], self.temp_file.name)
        
        # Check that the methods were analyzed
        self.assertGreater(len(result['method_analysis']), 0)
        
        # Check that the complex method was detected
        complex_method = None
        for method in result['method_analysis']:
            if method['method_name'] == 'complex_method':
                complex_method = method
                break
        
        self.assertIsNotNone(complex_method)
        self.assertGreater(len(complex_method['violations']), 0)
    
    def test_dry_analyzer(self):
        """Test the DRY analyzer."""
        analyzer = DRYAnalyzer()
        result = analyzer.analyze_file(self.temp_file.name)
        
        # Check that the file was analyzed
        self.assertEqual(result['file_path'], self.temp_file.name)
        
        # Check for duplicate code
        self.assertGreaterEqual(len(result['duplicate_code_blocks']), 1)
    
    def test_unified_analyzer(self):
        """Test the unified analyzer."""
        analyzer = UnifiedAnalyzer()
        result = analyzer.analyze_file(self.temp_file.name)
        
        # Check that the file was analyzed
        self.assertEqual(result['file_path'], self.temp_file.name)
        
        # Check that all analyzers were run
        self.assertIn('SRP Analyzer', result['analyzers'])
        self.assertIn('KISS Analyzer', result['analyzers'])
        self.assertIn('DRY Analyzer', result['analyzers'])
        
        # Check that an overall score was calculated
        self.assertIn('overall_quality_score', result)
        self.assertGreaterEqual(result['overall_quality_score'], 0.0)
        self.assertLessEqual(result['overall_quality_score'], 1.0)

if __name__ == '__main__':
    unittest.main()
