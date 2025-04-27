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
    
    def format_traceback(self, exc_type, exc_value, exc_traceback, show_tip=True):
        """
        Format a traceback with visual enhancements
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            exc_traceback (traceback): Exception traceback
            show_tip (bool): Whether to show the installation tip
            
        Returns:
            str: Formatted traceback string
        """
        if self._use_rich:
            return self._format_with_rich(exc_type, exc_value, exc_traceback, show_tip)
        elif COLORAMA_AVAILABLE and self.colored_output:
            return self._format_with_colorama(exc_type, exc_value, exc_traceback, show_tip)
        else:
            return self._format_plain(exc_type, exc_value, exc_traceback, show_tip)
    
    def _format_with_rich(self, exc_type, exc_value, exc_traceback, show_tip=True):
        """Format traceback using Rich for beautiful output"""
        output = StringIO()
        console = Console(file=output, width=100, highlight=True)
        
        # Get the traceback object
        rich_traceback = Traceback.from_exception(
            exc_type, exc_value, exc_traceback,
            show_locals=True,
            word_wrap=True,
            indent_guides=True,
            theme=self.theme
        )
        
        # Create an error title
        title = f"{exc_type.__name__}: {str(exc_value)}"
        
        # Print header with a stylish panel
        console.print()
        console.print(Panel(
            f"[bold white on red]{title}[/bold white on red]",
            border_style="red",
            expand=False,
            title="[bold yellow]💥 Exception Detected 💥[/bold yellow]",
            title_align="center",
            subtitle="[italic cyan]ErrorTrace Pro[/italic cyan]",
            subtitle_align="right"
        ))
        
        # Print traceback with enhanced styling
        console.print(rich_traceback)
        
        # Add solution suggestions panel if available
        if hasattr(rich_traceback, 'locals') and rich_traceback.locals:
            console.print(Panel(
                "[bold magenta]🔍 Local Variables:[/bold magenta]",
                border_style="magenta",
                expand=False
            ))
        
        # Add a footer with tips only if show_tip is True
        if show_tip:
            console.print(Panel(
                "[bold blue]💡 Tip:[/bold blue] Use [bold green]errortrace_pro.install()[/bold green] to enable this handler globally.",
                border_style="blue",
                expand=False
            ))
        
        return "\n" + output.getvalue()
    
    def _format_with_colorama(self, exc_type, exc_value, exc_traceback, show_tip=True):
        """Format traceback using Colorama for colored output"""
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Process each line to add colors
        formatted_lines = []
        
        # Add header with a border
        header = f"{exc_type.__name__}: {str(exc_value)}"
        border = "═" * (len(header) + 20)
        
        # Create a more visually appealing header
        formatted_lines.append(f"\n{Fore.RED}{Style.BRIGHT}╭{border}╮{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.RED}{Style.BRIGHT}│{Fore.WHITE} 💥 Exception Detected 💥 {' ' * (len(border) - 21)}│{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.RED}{Style.BRIGHT}├{border}┤{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.RED}{Style.BRIGHT}│{Fore.WHITE} ErrorTrace Pro - {header} {' ' * (len(border) - len(header) - 16)}│{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.RED}{Style.BRIGHT}╰{border}╯{Style.RESET_ALL}\n")
        
        # Add traceback header
        tb_header = "Traceback (most recent call last)"
        tb_border = "─" * (len(tb_header) + 40)
        formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}╭{tb_border}╮{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Fore.CYAN} {tb_header} {' ' * (len(tb_border) - len(tb_header) - 2)}│{Style.RESET_ALL}")
        formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}╰{tb_border}╯{Style.RESET_ALL}\n")
        
        current_file = None
        frame_num = 0
        
        for line in tb_lines:
            # Special handling for the traceback frames
            if line.strip().startswith("File "):
                frame_num += 1
                parts = line.strip().split(", ")
                
                if len(parts) >= 3:
                    file_part = parts[0].replace('File "', '').replace('"', '')
                    line_part = parts[1]
                    func_part = ", ".join(parts[2:])
                    
                    # Extract just the filename from the path
                    if "/" in file_part:
                        file_name = file_part.split("/")[-1]
                    else:
                        file_name = file_part
                    
                    current_file = file_part
                    
                    # Format the frame with numbers and better layout
                    formatted_lines.append(
                        f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} "
                        f"{Fore.YELLOW}{Style.BRIGHT}[{frame_num}]{Style.RESET_ALL} "
                        f"{Fore.MAGENTA}{Style.BRIGHT}{file_name}{Style.RESET_ALL} "
                        f"({Fore.CYAN}{file_part}{Fore.RESET}), "
                        f"{Fore.GREEN}{line_part}{Fore.RESET}, "
                        f"{Fore.YELLOW}{func_part}{Fore.RESET}\n"
                    )
                    formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}\n")
                else:
                    # Fallback if the line doesn't match the expected format
                    # Color file paths
                    line = re.sub(r'File "([^"]+)"', f'File "{Fore.CYAN}\\1{Fore.RESET}"', line)
                    # Color line numbers
                    line = re.sub(r'line (\d+)', f'line {Fore.GREEN}\\1{Fore.RESET}', line)
                    # Color function names
                    line = re.sub(r'in ([^\n]+)', f'in {Fore.YELLOW}\\1{Fore.RESET}', line)
                    formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL} {line}")
            
            # Highlight code lines
            elif line.strip().startswith("->"): 
                if "->" in line:
                    line = line.replace("->", f"{Fore.RED}{Style.BRIGHT}❱{Style.RESET_ALL}")
                formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}  {Fore.WHITE}{Style.BRIGHT}{line.strip()}{Style.RESET_ALL}\n")
                formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}\n")
            elif current_file and line.strip() and not line.strip().startswith("Traceback"):
                formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Style.RESET_ALL}  {Fore.WHITE}{line.strip()}{Style.RESET_ALL}\n")
            
            # Highlight the error type and message
            elif exc_type.__name__ in line:
                # Create a bottom border for the traceback
                formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}╰{tb_border}╯{Style.RESET_ALL}\n")
                
                # Format the exception line
                line = line.replace(
                    exc_type.__name__, 
                    f"{Fore.RED}{Style.BRIGHT}{exc_type.__name__}{Style.RESET_ALL}"
                )
                # Try to color the error message too
                message_part = str(exc_value)
                if message_part and message_part in line:
                    line = line.replace(
                        message_part,
                        f"{Fore.YELLOW}{message_part}{Fore.RESET}"
                    )
                formatted_lines.append(f"{line}\n")
            
            # Other lines
            else:
                formatted_lines.append(line)
        
        # Add solution suggestions section
        if show_tip:
            tip_border = "─" * 65
            formatted_lines.append(f"\n{Fore.BLUE}{Style.BRIGHT}╭{tip_border}╮{Style.RESET_ALL}")
            formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}│{Fore.CYAN} 💡 Tip: Use {Fore.GREEN}{Style.BRIGHT}errortrace_pro.install(){Style.RESET_ALL}{Fore.CYAN} to enable this handler globally. {' ' * 5}│{Style.RESET_ALL}")
            formatted_lines.append(f"{Fore.BLUE}{Style.BRIGHT}╰{tip_border}╯{Style.RESET_ALL}\n")
            
        return "".join(formatted_lines)
    
    def _format_plain(self, exc_type, exc_value, exc_traceback, show_tip=True):
        """Format traceback without colors"""
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Create a more structured plain text output
        formatted_lines = []
        
        # Add header with ASCII art border
        header = f"{exc_type.__name__}: {str(exc_value)}"
        border = "=" * (len(header) + 20)
        
        # Create a visually appealing header even without colors
        formatted_lines.append(f"\n+{border}+")
        formatted_lines.append(f"| ErrorTrace Pro - Exception Detected |")
        formatted_lines.append(f"+{border}+")
        formatted_lines.append(f"| {header} {' ' * (len(border) - len(header) - 2)}|")
        formatted_lines.append(f"+{border}+\n")
        
        # Add traceback header
        tb_header = "Traceback (most recent call last)"
        tb_border = "-" * (len(tb_header) + 40)
        formatted_lines.append(f"+{tb_border}+")
        formatted_lines.append(f"| {tb_header} {' ' * (len(tb_border) - len(tb_header) - 2)}|")
        formatted_lines.append(f"+{tb_border}+\n")
        
        # Process each line of the traceback
        frame_num = 0
        current_file = None
        
        for line in tb_lines:
            # Format file lines
            if line.strip().startswith("File "):
                frame_num += 1
                parts = line.strip().split(", ")
                
                if len(parts) >= 3:
                    file_part = parts[0].replace('File "', '').replace('"', '')
                    line_part = parts[1]
                    func_part = ", ".join(parts[2:])
                    
                    # Extract just the filename from the path
                    if "/" in file_part:
                        file_name = file_part.split("/")[-1]
                    else:
                        file_name = file_part
                    
                    current_file = file_part
                    
                    # Format the frame with numbers and better layout
                    formatted_lines.append(f"| [{frame_num}] {file_name} ({file_part}), {line_part}, {func_part}\n")
                    formatted_lines.append(f"|\n")
                else:
                    formatted_lines.append(f"| {line}")
            
            # Format code lines
            elif line.strip().startswith("->"): 
                if "->" in line:
                    line = line.replace("->", ">>")
                formatted_lines.append(f"|  {line.strip()}\n")
                formatted_lines.append(f"|\n")
            elif current_file and line.strip() and not line.strip().startswith("Traceback"):
                formatted_lines.append(f"|  {line.strip()}\n")
            
            # Format the exception line
            elif exc_type.__name__ in line:
                # Create a bottom border for the traceback
                formatted_lines.append(f"+{tb_border}+\n")
                formatted_lines.append(f"{line}\n")
            
            # Other lines
            else:
                formatted_lines.append(line)
        
        # Add tip section if needed
        if show_tip:
            tip_border = "-" * 65
            formatted_lines.append(f"\n+{tip_border}+")
            formatted_lines.append(f"| Tip: Use errortrace_pro.install() to enable this handler globally. {' ' * 5}|")
            formatted_lines.append(f"+{tip_border}+\n")
        
        return "".join(formatted_lines)
    
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
