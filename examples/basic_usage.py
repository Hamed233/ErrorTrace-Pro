"""
Basic usage example for ErrorTrace Pro
"""
import sys
import os

# Add the parent directory to sys.path to import the package in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import errortrace_pro

# Install as global exception handler
errortrace_pro.install()

def divide(a, b):
    """Simple division function that will raise an exception if b is 0"""
    return a / b

def process_data(data):
    """Process a dictionary of data"""
    result = data['key'] * 2
    return result

def recursive_function(n):
    """A recursive function that will cause a RecursionError"""
    if n == 0:
        return 0
    else:
        # Mistake: no decreasing n, will cause RecursionError
        return recursive_function(n)

def main():
    """Main function with various errors to demonstrate ErrorTrace Pro"""
    print("ErrorTrace Pro Basic Usage Example")
    print("----------------------------------")
    print("This example will intentionally cause exceptions to show ErrorTrace Pro in action.")
    print("Each example will demonstrate ErrorTrace Pro's enhanced error handling.\n")
    
    # Get example choice from user
    print("Choose an example to run:")
    print("1. ZeroDivisionError")
    print("2. KeyError")
    print("3. TypeError")
    print("4. AttributeError")
    print("5. RecursionError (careful, this may crash)")
    
    choice = input("\nEnter example number (1-5): ")
    
    if choice == '1':
        print("\n[Example 1: ZeroDivisionError]")
        print("Attempting to divide by zero...\n")
        # This will be caught by ErrorTrace Pro
        result = divide(10, 0)
        
    elif choice == '2':
        print("\n[Example 2: KeyError]")
        print("Attempting to access a non-existent dictionary key...\n")
        # This will be caught by ErrorTrace Pro
        data = {'name': 'ErrorTrace Pro', 'version': '0.1.0'}
        process_data(data)
        
    elif choice == '3':
        print("\n[Example 3: TypeError]")
        print("Attempting to add a string and an integer...\n")
        # This will be caught by ErrorTrace Pro
        result = "ErrorTrace Pro" + 42
        
    elif choice == '4':
        print("\n[Example 4: AttributeError]")
        print("Attempting to access a non-existent attribute...\n")
        # This will be caught by ErrorTrace Pro
        value = "ErrorTrace Pro"
        result = value.nonexistent_method()
        
    elif choice == '5':
        print("\n[Example 5: RecursionError]")
        print("Attempting to cause a recursion error...\n")
        # This will be caught by ErrorTrace Pro
        recursive_function(10)
        
    else:
        print("\nInvalid choice. Please run the script again and select a valid option.")

if __name__ == "__main__":
    main()
