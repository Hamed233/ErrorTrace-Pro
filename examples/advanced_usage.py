"""
Advanced usage example for ErrorTrace Pro
"""
import sys
import os
import logging
import tempfile
import json

# Add the parent directory to sys.path to import the package in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import errortrace_pro

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_temporary_solutions_file():
    """Create a temporary file with custom solutions"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
    
    # Write custom solutions to the temporary file
    custom_solutions = {
        "CustomError": [
            "This is a custom solution for CustomError",
            "Another solution for this error type"
        ],
        "ValueError": [
            "Additional custom solution for ValueError",
            "Try converting the value to the correct type first"
        ]
    }
    
    json.dump(custom_solutions, temp_file)
    temp_file.close()
    
    return temp_file.name

# Define a custom exception
class CustomError(Exception):
    """Custom exception for demonstration purposes"""
    pass

def test_custom_error():
    """Raise a custom error"""
    raise CustomError("This is a custom error message")

def test_value_error():
    """Raise a ValueError"""
    raise ValueError("This value is not valid")

def nested_function_with_error(level):
    """Nested function to demonstrate deep traceback"""
    if level <= 0:
        # Cause a TypeError
        return "ErrorTrace Pro" + 42
    else:
        return nested_function_with_error(level - 1)

def main():
    """Main function demonstrating advanced features"""
    print("ErrorTrace Pro Advanced Usage Example")
    print("------------------------------------")
    
    # Create a temporary custom solutions file
    custom_solutions_path = create_temporary_solutions_file()
    print(f"Created temporary custom solutions file at: {custom_solutions_path}")
    
    # Initialize with custom settings
    handler = errortrace_pro.init(
        solutions_path=custom_solutions_path,
        cloud_logging=False,  # Set to True and configure below to test cloud logging
        # cloud_provider="http",
        # api_key=os.getenv("API_KEY"),
        # endpoint=os.getenv("LOGGING_ENDPOINT"),
        enable_suggestions=True,
        colored_output=True,
        verbose=True
    )
    
    # Install the custom handler
    errortrace_pro.install(handler)
    
    # Test with different exception scenarios
    try:
        print("\n[Example 1: Custom Exception]")
        print("Raising a CustomError exception...")
        test_custom_error()
    except Exception as e:
        print(f"Caught: {type(e).__name__}: {e}")
    
    try:
        print("\n[Example 2: ValueError with Custom Solutions]")
        print("Raising a ValueError exception...")
        test_value_error()
    except Exception as e:
        print(f"Caught: {type(e).__name__}: {e}")
    
    try:
        print("\n[Example 3: Nested Function Call]")
        print("Calling a deeply nested function that will raise an error...")
        nested_function_with_error(5)
    except Exception as e:
        print(f"Caught: {type(e).__name__}: {e}")
    
    # Clean up the temporary file
    os.unlink(custom_solutions_path)
    print(f"\nRemoved temporary custom solutions file: {custom_solutions_path}")
    
    print("\nAll examples completed.")

if __name__ == "__main__":
    main()
