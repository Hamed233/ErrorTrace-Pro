"""
Unit tests for the visualizer module
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import traceback

# Add the parent directory to sys.path to import the package in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from errortrace_pro.visualizer import TracebackVisualizer, RICH_AVAILABLE, COLORAMA_AVAILABLE

class TestTracebackVisualizer(unittest.TestCase):
    """Test cases for the TracebackVisualizer class"""
    
    def setUp(self):
        """Set up the test environment"""
        self.visualizer = TracebackVisualizer(colored_output=False)
    
    def test_init(self):
        """Test initialization of the visualizer"""
        self.assertFalse(self.visualizer.colored_output)
        self.assertEqual(self.visualizer.theme, "monokai")
        self.assertFalse(self.visualizer._use_rich)
    
    def test_init_with_color(self):
        """Test initialization with colored output"""
        visualizer = TracebackVisualizer(colored_output=True)
        
        if RICH_AVAILABLE:
            self.assertTrue(visualizer._use_rich)
            self.assertIsNotNone(visualizer.console)
        elif COLORAMA_AVAILABLE:
            self.assertFalse(visualizer._use_rich)
        else:
            self.assertFalse(visualizer._use_rich)
    
    def test_format_plain(self):
        """Test formatting a traceback without colors"""
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            result = self.visualizer._format_plain(exc_type, exc_value, exc_traceback)
            
            # Basic checks on the result
            self.assertIsInstance(result, str)
            self.assertIn("ErrorTrace Pro: ZeroDivisionError", result)
            self.assertIn("division by zero", result)
    
    @unittest.skipIf(not COLORAMA_AVAILABLE, "Colorama not available")
    def test_format_with_colorama(self):
        """Test formatting a traceback with Colorama"""
        visualizer = TracebackVisualizer(colored_output=True)
        
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Only test if not using Rich
            if not visualizer._use_rich:
                result = visualizer._format_with_colorama(exc_type, exc_value, exc_traceback)
                
                # Basic checks on the result
                self.assertIsInstance(result, str)
                self.assertIn("ErrorTrace Pro: ZeroDivisionError", result)
                self.assertIn("division by zero", result)
    
    @unittest.skipIf(not RICH_AVAILABLE, "Rich not available")
    def test_format_with_rich(self):
        """Test formatting a traceback with Rich"""
        visualizer = TracebackVisualizer(colored_output=True)
        
        # Only proceed if Rich is available
        if not RICH_AVAILABLE:
            return
            
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            result = visualizer._format_with_rich(exc_type, exc_value, exc_traceback)
            
            # Basic checks on the result
            self.assertIsInstance(result, str)
            # Rich output includes ANSI codes, so we can't check for exact strings
            self.assertGreater(len(result), 100)  # Should be substantial
    
    def test_format_traceback(self):
        """Test the main format_traceback method"""
        # Mock the internal formatting methods
        self.visualizer._format_with_rich = MagicMock(return_value="Rich format")
        self.visualizer._format_with_colorama = MagicMock(return_value="Colorama format")
        self.visualizer._format_plain = MagicMock(return_value="Plain format")
        
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Test with _use_rich = True
            self.visualizer._use_rich = True
            result = self.visualizer.format_traceback(exc_type, exc_value, exc_traceback)
            self.assertEqual(result, "Rich format")
            self.visualizer._format_with_rich.assert_called_once()
            
            # Reset mocks
            self.visualizer._format_with_rich.reset_mock()
            self.visualizer._format_with_colorama.reset_mock()
            self.visualizer._format_plain.reset_mock()
            
            # Test with _use_rich = False and COLORAMA_AVAILABLE = True
            self.visualizer._use_rich = False
            with patch('errortrace_pro.visualizer.COLORAMA_AVAILABLE', True):
                result = self.visualizer.format_traceback(exc_type, exc_value, exc_traceback)
                self.assertEqual(result, "Colorama format")
                self.visualizer._format_with_colorama.assert_called_once()
            
            # Reset mocks
            self.visualizer._format_with_rich.reset_mock()
            self.visualizer._format_with_colorama.reset_mock()
            self.visualizer._format_plain.reset_mock()
            
            # Test with _use_rich = False and COLORAMA_AVAILABLE = False
            self.visualizer._use_rich = False
            with patch('errortrace_pro.visualizer.COLORAMA_AVAILABLE', False):
                result = self.visualizer.format_traceback(exc_type, exc_value, exc_traceback)
                self.assertEqual(result, "Plain format")
                self.visualizer._format_plain.assert_called_once()

if __name__ == '__main__':
    unittest.main()
