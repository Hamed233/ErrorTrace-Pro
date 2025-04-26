"""
Test that the package can be imported and basic functionality works.
"""
import sys
import unittest
import importlib.util

class TestPackaging(unittest.TestCase):
    """Test package import and basic functionality."""
    
    def test_import(self):
        """Test that the package can be imported."""
        self.assertIsNotNone(importlib.util.find_spec("errortrace_pro"))
        
    def test_version(self):
        """Test that the package has a version."""
        import errortrace_pro
        self.assertTrue(hasattr(errortrace_pro, '__version__'))
        self.assertIsInstance(errortrace_pro.__version__, str)
        
    def test_init(self):
        """Test that init function works."""
        import errortrace_pro
        handler = errortrace_pro.init()
        self.assertIsNotNone(handler)
        
    def test_install(self):
        """Test that install function works."""
        import errortrace_pro
        old_excepthook = sys.excepthook
        
        try:
            errortrace_pro.install()
            self.assertNotEqual(sys.excepthook, old_excepthook)
        finally:
            # Restore original excepthook
            sys.excepthook = old_excepthook
            
    def test_uninstall(self):
        """Test that uninstall function works."""
        import errortrace_pro
        old_excepthook = sys.excepthook
        
        try:
            errortrace_pro.install()
            errortrace_pro.uninstall()
            self.assertEqual(sys.excepthook, old_excepthook)
        finally:
            # Ensure we always restore the original excepthook
            sys.excepthook = old_excepthook

if __name__ == '__main__':
    unittest.main()