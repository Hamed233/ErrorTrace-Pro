"""
Traceback visualization module for ErrorTrace Pro
"""
import os
import sys
import traceback
import re
from io import StringIO
import logging

# Check if Rich is available, otherwise fallback to colorama
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.traceback import Traceback
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
    # Try to use colorama as fallback
    try:
        from colorama import init, Fore, Back, Style
        init()
        COLORAMA_AVAILABLE = True
    except ImportError:
        COLORAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class TracebackVisualizer:
    """
    Visualize Python tracebacks with enhanced formatting and colors
    """
    
    def __init__(self, colored_output=True, theme="monokai"):
        """
        Initialize the traceback visualizer
        
        Args:
            colored_output (bool): Whether to use colors in output
            theme (str): Syntax highlighting theme (when using Rich)
        """
        self.colored_output = colored_output
        self.theme = theme
        
        # Initialize Rich console if available
        if RICH_AVAILABLE and colored_output:
            self.console = Console(file=StringIO(), highlight=True)
            self._use_rich = True
        else:
            self._use_rich = False
            if colored_output and not COLORAMA_AVAILABLE:
                logger.warning("Colorama not available. Install with 'pip install colorama' for colored output.")
    
    def format_traceback(self, exc_type, exc_value, exc_traceback):
        """
        Format a traceback with visual enhancements
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            exc_traceback (traceback): Exception traceback
            
        Returns:
            str: Formatted traceback string
        """
        if self._use_rich:
            return self._format_with_rich(exc_type, exc_value, exc_traceback)
        elif COLORAMA_AVAILABLE and self.colored_output:
            return self._format_with_colorama(exc_type, exc_value, exc_traceback)
        else:
            return self._format_plain(exc_type, exc_value, exc_traceback)
    
    def _format_with_rich(self, exc_type, exc_value, exc_traceback):
        """Format traceback using Rich for beautiful output"""
        output = StringIO()
        console = Console(file=output, width=100)
        
        # Get the traceback object
        rich_traceback = Traceback.from_exception(
            exc_type, exc_value, exc_traceback,
            show_locals=True,
            word_wrap=True,
            indent_guides=True
        )
        
        # Print header
        console.print()
        console.print(Panel(f"[bold red]ErrorTrace Pro: {exc_type.__name__}[/bold red]", 
                     expand=False))
        
        # Print traceback
        console.print(rich_traceback)
        
        # Print exception message with more context
        console.print(f"[bold red]{exc_type.__name__}[/bold red]: [yellow]{str(exc_value)}[/yellow]")
        
        return "\n" + output.getvalue()
    
    def _format_with_colorama(self, exc_type, exc_value, exc_traceback):
        """Format traceback using Colorama for colored output"""
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Process each line to add colors
        formatted_lines = []
        
        # Add header
        formatted_lines.append(f"\n{Fore.RED}{Style.BRIGHT}ErrorTrace Pro: {exc_type.__name__}{Style.RESET_ALL}\n")
        
        for line in tb_lines:
            # Color file paths
            line = re.sub(r'File "([^"]+)"', f'File "{Fore.CYAN}\\1{Fore.RESET}"', line)
            
            # Color line numbers
            line = re.sub(r'line (\d+)', f'line {Fore.GREEN}\\1{Fore.RESET}', line)
            
            # Color function names
            line = re.sub(r'in ([^\n]+)', f'in {Fore.YELLOW}\\1{Fore.RESET}', line)
            
            # Highlight the error type
            if exc_type.__name__ in line:
                line = line.replace(
                    exc_type.__name__, 
                    f"{Fore.RED}{Style.BRIGHT}{exc_type.__name__}{Style.RESET_ALL}"
                )
                
            formatted_lines.append(line)
            
        return "".join(formatted_lines)
    
    def _format_plain(self, exc_type, exc_value, exc_traceback):
        """Format traceback without colors"""
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Add header
        header = f"\nErrorTrace Pro: {exc_type.__name__}\n"
        
        # Join all lines
        return header + "".join(tb_lines)
    
    def highlight_code(self, code, filename):
        """
        Highlight code snippet from the error location
        
        Args:
            code (str): Code snippet to highlight
            filename (str): Source filename
            
        Returns:
            str: Highlighted code
        """
        if not self._use_rich:
            return code
            
        # Determine lexer by filename extension
        extension = os.path.splitext(filename)[1].lower()
        lexer = "python" if extension == ".py" else "text"
        
        # Create syntax highlighted code
        syntax = Syntax(code, lexer, theme=self.theme, line_numbers=True)
        
        # Render to string
        output = StringIO()
        console = Console(file=output)
        console.print(syntax)
        
        return output.getvalue()
