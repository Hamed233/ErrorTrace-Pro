"""
Exception handler module for ErrorTrace Pro
"""
import os
import sys
import traceback
import logging
import platform
import datetime
import json

from .visualizer import TracebackVisualizer
from .solutions import SolutionProvider
from .cloud_logger import CloudLogger

logger = logging.getLogger(__name__)

class ExceptionHandler:
    """
    Main exception handler class for ErrorTrace Pro
    
    Handles exceptions, visualizes tracebacks, suggests solutions,
    and logs errors to cloud services.
    """
    
    def __init__(self, solutions_path=None, cloud_logging=False, 
                 cloud_provider=None, api_key=None, project_id=None,
                 enable_suggestions=True, colored_output=True, verbose=True):
        """
        Initialize the exception handler
        
        Args:
            solutions_path (str, optional): Path to custom solutions JSON file
            cloud_logging (bool): Enable cloud logging
            cloud_provider (str, optional): Cloud provider name ('gcp', 'aws', 'azure')
            api_key (str, optional): API key for cloud provider
            project_id (str, optional): Project ID for cloud provider
            enable_suggestions (bool): Enable solution suggestions
            colored_output (bool): Enable colored console output
            verbose (bool): Enable verbose output
        """
        self.enable_suggestions = enable_suggestions
        self.verbose = verbose
        
        # Initialize visualizer
        self.visualizer = TracebackVisualizer(colored_output=colored_output)
        
        # Initialize solution provider
        self.solution_provider = SolutionProvider(custom_path=solutions_path)
        
        # Initialize cloud logger if requested
        self.cloud_logging = cloud_logging
        self.cloud_logger = None
        
        if cloud_logging:
            # Get API key from environment if not provided
            if api_key is None:
                api_key = os.getenv("ERRORTRACE_API_KEY", None)
                
            # Get project ID from environment if not provided
            if project_id is None:
                project_id = os.getenv("ERRORTRACE_PROJECT_ID", None)
                
            self.cloud_logger = CloudLogger(
                provider=cloud_provider,
                api_key=api_key,
                project_id=project_id
            )
    
    def handle(self, exc_type=None, exc_value=None, exc_traceback=None):
        """
        Handle an exception
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            exc_traceback (traceback): Exception traceback
        
        If called without arguments, will use sys.exc_info()
        """
        # If no exception info is provided, get it from sys.exc_info()
        if exc_type is None or exc_value is None or exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
        if exc_type is None:
            logger.warning("No exception to handle")
            return
            
        # Log the exception
        logger.error(f"Exception occurred: {exc_type.__name__}: {exc_value}")
        
        # Generate error context
        context = self._get_error_context(exc_type, exc_value, exc_traceback)
        
        # Check if handler is already installed (sys.excepthook is not the default)
        is_installed = sys.excepthook is not sys.__excepthook__
        
        # Visualize the traceback
        visual_traceback = self.visualizer.format_traceback(exc_type, exc_value, exc_traceback, show_tip=not is_installed)
        
        # Print the visual traceback
        print(visual_traceback, file=sys.stderr)
        
        # Get solution suggestions if enabled
        if self.enable_suggestions:
            suggestions = self.solution_provider.get_solutions(exc_type, exc_value, context)
            if suggestions:
                print("\n🔍 Suggested Solutions:", file=sys.stderr)
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}", file=sys.stderr)
            else:
                print("\n❓ No specific solutions found for this error.", file=sys.stderr)
                
        # Log to cloud if enabled
        if self.cloud_logging and self.cloud_logger:
            try:
                self.cloud_logger.log_exception(
                    exc_type=exc_type,
                    exc_value=exc_value,
                    traceback_str=traceback.format_tb(exc_traceback),
                    context=context,
                    visual_traceback=visual_traceback
                )
                print("\n☁️ Error logged to cloud service", file=sys.stderr)
            except Exception as e:
                logger.error(f"Failed to log to cloud: {e}")
                print(f"\n⚠️ Failed to log to cloud: {e}", file=sys.stderr)
                
        return context
    
    def _get_error_context(self, exc_type, exc_value, exc_traceback):
        """
        Collect contextual information about the error
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            exc_traceback (traceback): Exception traceback
            
        Returns:
            dict: Context information about the error
        """
        frames = traceback.extract_tb(exc_traceback)
        
        # Get the most recent frame
        last_frame = frames[-1] if frames else None
        
        context = {
            "timestamp": datetime.datetime.now().isoformat(),
            "exception": {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "module": exc_type.__module__
            },
            "system": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "system": platform.system(),
                "processor": platform.processor()
            },
            "traceback": {
                "frames_count": len(frames),
                "last_frame": {
                    "filename": last_frame.filename if last_frame else None,
                    "lineno": last_frame.lineno if last_frame else None,
                    "name": last_frame.name if last_frame else None,
                    "line": last_frame.line if last_frame else None
                }
            }
        }
        
        # Add environment variables (safe ones only)
        safe_env_vars = {
            "HOME", "USER", "LANG", "SHELL", "PYTHONPATH", "PYTHONHOME",
            "VIRTUAL_ENV", "PATH", "PWD", "TMPDIR", "TMP", "TEMP"
        }
        
        env_data = {}
        for key in safe_env_vars:
            if key in os.environ:
                env_data[key] = os.environ[key]
                
        context["environment"] = env_data
        
        return context
