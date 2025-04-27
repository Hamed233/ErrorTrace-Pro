"""
ErrorTrace Pro - Enhanced Exception Handling for Python

A professional-grade exception handling library featuring:
- Visual traceback mapping
- Common solution suggestions for known exceptions
- Cloud-based error logging
- Enhanced debugging capabilities

Compatible with Python 3.7+
"""

__version__ = "0.3.0"
__author__ = "Hamed Esam"

import logging
import sys

from .handler import ExceptionHandler
from .visualizer import TracebackVisualizer
from .solutions import SolutionProvider
from .cloud_logger import CloudLogger

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create default handler instance for easy import
default_handler = ExceptionHandler()

def init(solutions_path=None, cloud_logging=False, cloud_provider=None, 
         api_key=None, project_id=None, enable_suggestions=True,
         colored_output=True, verbose=True):
    """
    Initialize ErrorTrace Pro with custom settings
    
    Args:
        solutions_path (str, optional): Path to custom solutions JSON file
        cloud_logging (bool): Enable cloud logging (default: False)
        cloud_provider (str, optional): Cloud provider ('gcp', 'aws', 'azure')
        api_key (str, optional): API key for cloud provider
        project_id (str, optional): Project ID for cloud provider
        enable_suggestions (bool): Enable solution suggestions (default: True)
        colored_output (bool): Enable colored console output (default: True)
        verbose (bool): Enable verbose output (default: True)
        
    Returns:
        ExceptionHandler: Configured exception handler instance
    """
    handler = ExceptionHandler(
        solutions_path=solutions_path,
        cloud_logging=cloud_logging,
        cloud_provider=cloud_provider,
        api_key=api_key,
        project_id=project_id,
        enable_suggestions=enable_suggestions,
        colored_output=colored_output,
        verbose=verbose
    )
    return handler

def install(handler=None):
    """
    Install ErrorTrace Pro as the global exception handler
    
    Args:
        handler (ExceptionHandler, optional): Custom handler instance to use
    """
    if handler is None:
        handler = default_handler
    
    def exception_hook(exc_type, exc_value, exc_traceback):
        # Handle the exception with our custom handler
        handler.handle(exc_type, exc_value, exc_traceback)
        # We don't call the original excepthook to avoid duplicate tracebacks
        # We also need to exit with a non-zero status code to indicate an error occurred
        # but without re-raising the exception
        if exc_type is not None:
            # If this is running in a script, exit with error code 1
            # This prevents the default traceback from showing
            import os
            # Only exit if this is the main thread and not in interactive mode
            if os._exit and not hasattr(sys, 'ps1'):
                # Use os._exit instead of sys.exit to avoid triggering exit handlers
                # which might cause more exceptions
                os._exit(1)
    
    # Set as the global exception hook
    sys.excepthook = exception_hook
    
    return handler

def uninstall():
    """Restore the original sys.excepthook"""
    sys.excepthook = sys.__excepthook__
