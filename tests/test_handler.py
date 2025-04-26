"""
Unit tests for the exception handler module
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add the parent directory to sys.path to import the package in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from errortrace_pro.handler import ExceptionHandler

class TestExceptionHandler(unittest.TestCase):
    """Test cases for the ExceptionHandler class"""
    
    def setUp(self):
        """Set up the test environment"""
        self.handler = ExceptionHandler(
            cloud_logging=False,
            enable_suggestions=True,
            colored_output=False,
            verbose=True
        )
    
    def test_init(self):
        """Test initialization of the handler"""
        self.assertIsNotNone(self.handler.visualizer)
        self.assertIsNotNone(self.handler.solution_provider)
        self.assertFalse(self.handler.cloud_logging)
        self.assertIsNone(self.handler.cloud_logger)
        self.assertTrue(self.handler.enable_suggestions)
    
    def test_init_with_cloud_logging(self):
        """Test initialization with cloud logging enabled"""
        with patch('errortrace_pro.handler.CloudLogger') as mock_cloud_logger:
            handler = ExceptionHandler(
                cloud_logging=True,
                cloud_provider='http',
                api_key='test_key',
                project_id='test_project'
            )
            
            self.assertTrue(handler.cloud_logging)
            self.assertIsNotNone(handler.cloud_logger)
            mock_cloud_logger.assert_called_once_with(
                provider='http',
                api_key='test_key',
                project_id='test_project'
            )
    
    def test_get_error_context(self):
        """Test getting error context from an exception"""
        try:
            # Generate an exception
            1 / 0
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            context = self.handler._get_error_context(exc_type, exc_value, exc_traceback)
            
            # Check that basic fields are present
            self.assertIn('timestamp', context)
            self.assertIn('exception', context)
            self.assertIn('system', context)
            self.assertIn('traceback', context)
            self.assertIn('environment', context)
            
            # Check exception details
            self.assertEqual(context['exception']['type'], 'ZeroDivisionError')
            self.assertIn('division by zero', context['exception']['message'])
            
            # Check traceback fields
            self.assertIn('frames_count', context['traceback'])
            self.assertIn('last_frame', context['traceback'])
            
            # Check system fields
            self.assertIn('python_version', context['system'])
            self.assertIn('platform', context['system'])
    
    @patch('errortrace_pro.handler.print')
    @patch('errortrace_pro.handler.traceback')
    def test_handle_with_suggestions(self, mock_traceback, mock_print):
        """Test handling an exception with solution suggestions"""
        # Create a mock solution provider
        self.handler.solution_provider = MagicMock()
        self.handler.solution_provider.get_solutions.return_value = [
            "Test solution 1",
            "Test solution 2"
        ]
        
        # Create a mock visualizer
        self.handler.visualizer = MagicMock()
        self.handler.visualizer.format_traceback.return_value = "Formatted traceback"
        
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.handler.handle(exc_type, exc_value, exc_traceback)
            
            # Check that the solution provider and visualizer were called
            self.handler.solution_provider.get_solutions.assert_called_once()
            self.handler.visualizer.format_traceback.assert_called_once_with(
                exc_type, exc_value, exc_traceback
            )
            
            # Check that the solutions were printed
            mock_print.assert_any_call("\n🔍 Suggested Solutions:", file=sys.stderr)
            mock_print.assert_any_call("  1. Test solution 1", file=sys.stderr)
            mock_print.assert_any_call("  2. Test solution 2", file=sys.stderr)
    
    @patch('errortrace_pro.handler.print')
    def test_handle_without_suggestions(self, mock_print):
        """Test handling an exception without solution suggestions"""
        # Disable suggestions
        self.handler.enable_suggestions = False
        
        # Create a mock visualizer
        self.handler.visualizer = MagicMock()
        self.handler.visualizer.format_traceback.return_value = "Formatted traceback"
        
        try:
            # Generate an exception
            1 / 0
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.handler.handle(exc_type, exc_value, exc_traceback)
            
            # Check that the solution provider was not called
            self.handler.solution_provider.get_solutions.assert_not_called()
            
            # Check that no solution suggestions were printed
            for call_args in mock_print.call_args_list:
                args, _ = call_args
                if args and isinstance(args[0], str):
                    self.assertNotIn("Suggested Solutions", args[0])

if __name__ == '__main__':
    unittest.main()
