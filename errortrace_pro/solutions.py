"""
Solution provider module for ErrorTrace Pro
"""
import os
import json
import logging
import re
import importlib.resources as pkg_resources
from difflib import get_close_matches
import traceback

logger = logging.getLogger(__name__)

class SolutionProvider:
    """
    Provides solution suggestions for common exceptions
    
    Maintains a database of known exceptions and their solutions,
    and finds the most relevant solutions for a given exception.
    """
    
    def __init__(self, custom_path=None):
        """
        Initialize the solution provider
        
        Args:
            custom_path (str, optional): Path to custom solutions JSON file
        """
        self.solutions_db = {}
        self.custom_path = custom_path
        
        # Load the built-in solutions database
        self._load_builtin_solutions()
        
        # Load custom solutions if provided
        if custom_path:
            self._load_custom_solutions(custom_path)
    
    def _load_builtin_solutions(self):
        """Load the built-in solutions database"""
        try:
            # Try to load from package data using importlib.resources
            solution_file = "data/solutions.json"
            
            # First check if the file exists in the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, solution_file)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.solutions_db = json.load(f)
            else:
                # Fall back to a default set of solutions
                self.solutions_db = self._get_default_solutions()
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write the default solutions to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.solutions_db, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to load built-in solutions: {e}")
            # Fall back to a default set of solutions
            self.solutions_db = self._get_default_solutions()
    
    def _get_default_solutions(self):
        """Return a default set of solutions for common exceptions"""
        return {
            "SyntaxError": [
                "Check for missing parentheses, brackets, or quotes",
                "Ensure proper indentation is used",
                "Look for missing colons after conditional statements or loops",
                "Verify correct use of equals (=) vs. comparison (==)"
            ],
            "IndentationError": [
                "Check for consistent indentation (spaces vs tabs)",
                "Ensure each code block is indented with the same pattern",
                "Look for mixed tabs and spaces"
            ],
            "NameError": [
                "Check if the variable is defined before usage",
                "Verify variable name spelling",
                "Make sure the variable is in scope",
                "Check for case sensitivity issues"
            ],
            "TypeError": [
                "Ensure you're using compatible types in operations",
                "Check argument types passed to functions",
                "Verify that you're not treating a non-callable as a function",
                "Use type conversion functions like int(), str(), list() if needed"
            ],
            "ValueError": [
                "Check if the value is appropriate for the operation (e.g., converting 'abc' to int)",
                "Ensure values are within valid ranges for functions",
                "Verify format strings match the values being formatted"
            ],
            "AttributeError": [
                "Check if the object has the attribute or method you're trying to access",
                "Verify object type before accessing attributes",
                "Check for typos in attribute names",
                "Ensure the module or package is properly imported"
            ],
            "ImportError": [
                "Verify the module name is correct",
                "Check if the module is installed (pip install module_name)",
                "Ensure the package is in the Python path",
                "Check for circular imports"
            ],
            "KeyError": [
                "Ensure the key exists in the dictionary before accessing it",
                "Use dict.get(key, default) to provide a default value",
                "Check for case sensitivity or typos in key names"
            ],
            "IndexError": [
                "Check that the index is within the valid range of the sequence",
                "Verify the sequence is not empty before accessing elements",
                "Use bounds checking with if len(list) > index before accessing"
            ],
            "FileNotFoundError": [
                "Verify the file path is correct",
                "Check if the file exists in the expected location",
                "Ensure proper permissions to access the file",
                "Use absolute paths instead of relative paths if needed"
            ],
            "ZeroDivisionError": [
                "Add a check to prevent division by zero",
                "Use a try-except block to handle the case",
                "Consider using float('inf') for certain use cases"
            ],
            "PermissionError": [
                "Check if the application has proper permissions",
                "Verify file access rights",
                "Run the application with elevated permissions if needed",
                "Check if the file is locked by another process"
            ],
            "RuntimeError": [
                "Check for recursive function calls without a proper exit condition",
                "Look for issues with threads or concurrent execution",
                "Review custom exception handling"
            ],
            "MemoryError": [
                "Reduce memory usage by processing data in smaller chunks",
                "Check for memory leaks in long-running loops",
                "Consider using generators instead of lists for large data sets",
                "Use more efficient data structures"
            ],
            "RecursionError": [
                "Ensure your recursive function has a proper base case",
                "Consider rewriting using iteration instead of recursion",
                "Check for unintended recursive calls"
            ],
            "ConnectionError": [
                "Verify network connectivity",
                "Check if the server is accessible",
                "Ensure proper URL/IP and port configuration",
                "Add retry logic with exponential backoff"
            ],
            "TimeoutError": [
                "Increase timeout duration",
                "Check server or service responsiveness",
                "Consider implementing circuit breaker pattern",
                "Add retry logic with backoff"
            ],
            "JSONDecodeError": [
                "Verify the JSON format is valid (use a JSON validator)",
                "Check for missing quotes, commas, or brackets",
                "Ensure the content is actually JSON data",
                "Print the raw response to inspect issues"
            ],
            "ModuleNotFoundError": [
                "Install the module with pip: pip install <module_name>",
                "Check the module name for typos",
                "Verify your Python environment has the required packages",
                "Check if the module is compatible with your Python version"
            ]
        }
    
    def _load_custom_solutions(self, path):
        """
        Load custom solutions from a JSON file
        
        Args:
            path (str): Path to custom solutions JSON file
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                custom_solutions = json.load(f)
                
            # Merge with existing solutions
            for exc_name, solutions in custom_solutions.items():
                if exc_name in self.solutions_db:
                    # Add new solutions while avoiding duplicates
                    existing_solutions = set(self.solutions_db[exc_name])
                    for solution in solutions:
                        if solution not in existing_solutions:
                            self.solutions_db[exc_name].append(solution)
                else:
                    # Add new exception type with its solutions
                    self.solutions_db[exc_name] = solutions
                    
            logger.info(f"Loaded custom solutions from {path}")
        except Exception as e:
            logger.error(f"Failed to load custom solutions from {path}: {e}")
    
    def get_solutions(self, exc_type, exc_value, context=None):
        """
        Get solution suggestions for an exception
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            context (dict, optional): Additional context about the error
            
        Returns:
            list: List of solution suggestions
        """
        # Initialize solutions list
        solutions = []
        
        # Get exception name
        exc_name = exc_type.__name__
        
        # Check if we have specific solutions for this exception type
        if exc_name in self.solutions_db:
            solutions.extend(self.solutions_db[exc_name])
        else:
            # Try to find similar exception types
            similar_exc = self._find_similar_exception(exc_name)
            if similar_exc:
                solutions.extend(self.solutions_db[similar_exc])
                solutions.insert(0, f"This appears similar to a {similar_exc}. Consider these solutions:")
        
        # Add specific guidance based on the exception message
        message_guidance = self._get_message_specific_guidance(exc_name, str(exc_value))
        if message_guidance:
            solutions.insert(0, message_guidance)
        
        # Add contextual solutions based on traceback analysis
        if context:
            contextual_solutions = self._get_contextual_solutions(exc_type, exc_value, context)
            if contextual_solutions:
                solutions.extend(contextual_solutions)
        
        return solutions
    
    def _find_similar_exception(self, exc_name):
        """
        Find similar exception names in our database
        
        Args:
            exc_name (str): Exception name to look for
            
        Returns:
            str: Similar exception name or None
        """
        matches = get_close_matches(exc_name, self.solutions_db.keys(), n=1, cutoff=0.7)
        return matches[0] if matches else None
    
    def _get_message_specific_guidance(self, exc_name, message):
        """
        Provide specific guidance based on the exception message pattern
        
        Args:
            exc_name (str): Exception name
            message (str): Exception message
            
        Returns:
            str: Specific guidance or None
        """
        # Common patterns and their solutions
        patterns = {
            "ImportError": {
                r"No module named '([^']+)'": "Install the module with: pip install {0}",
                r"cannot import name '([^']+)'": "Check if {0} exists in the imported module"
            },
            "AttributeError": {
                r"'([^']+)' object has no attribute '([^']+)'": 
                "The {0} object doesn't have a {1} attribute. Check the object type and documentation."
            },
            "TypeError": {
                r"'([^']+)' object is not callable": "The {0} variable is not a function but you're trying to call it",
                r"([^(]+)\(\) takes (\d+) positional arguments? but (\d+) were given":
                "The function takes {1} arguments but you provided {2}"
            },
            "KeyError": {
                r"'([^']+)'": "The key '{0}' doesn't exist in the dictionary. Use .get() or check if key exists first."
            },
            "SyntaxError": {
                r"invalid syntax": "Check for missing colons, parentheses, or brackets",
                r"unexpected EOF": "Check for unclosed parentheses, brackets, or quotes"
            }
        }
        
        # Check if we have patterns for this exception
        if exc_name in patterns:
            for pattern, template in patterns[exc_name].items():
                match = re.search(pattern, message)
                if match:
                    # Format the guidance with captured groups
                    groups = match.groups()
                    return template.format(*groups)
        
        return None
    
    def _get_contextual_solutions(self, exc_type, exc_value, context):
        """
        Generate solutions based on error context
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            context (dict): Error context information
            
        Returns:
            list: Contextual solutions
        """
        solutions = []
        
        # Extract context information
        last_frame = context.get("traceback", {}).get("last_frame", {})
        filename = last_frame.get("filename")
        lineno = last_frame.get("lineno")
        line = last_frame.get("line")
        
        if not (filename and lineno and line):
            return solutions
        
        # Add specific solutions based on file type
        if filename.endswith(".py"):
            if "IndentationError" in exc_type.__name__:
                solutions.append(f"Check line {lineno} in {filename} for inconsistent indentation")
            elif "SyntaxError" in exc_type.__name__:
                solutions.append(f"Syntax error near line {lineno} in {filename}")
            elif "ImportError" in exc_type.__name__ or "ModuleNotFoundError" in exc_type.__name__:
                module_name = str(exc_value).split("'")[1] if "'" in str(exc_value) else ""
                if module_name:
                    solutions.append(f"Try installing the module with: pip install {module_name}")
            elif "AttributeError" in exc_type.__name__ and line:
                # Try to extract the attribute name from the error
                attr_match = re.search(r"'([^']+)'", str(exc_value))
                if attr_match:
                    attr_name = attr_match.group(1)
                    solutions.append(f"Check if the attribute '{attr_name}' exists or is spelled correctly at line {lineno}")
            elif "FileNotFoundError" in exc_type.__name__:
                # Extract the file path
                path_match = re.search(r"'([^']+)'", str(exc_value))
                if path_match:
                    file_path = path_match.group(1)
                    solutions.append(f"The file '{file_path}' was not found. Check the path and permissions.")
        
        return solutions
