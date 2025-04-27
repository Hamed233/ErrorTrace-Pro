import errortrace_pro
import sys
import os

"""
ErrorTrace Pro Color Test

This script tests the enhanced color output of ErrorTrace Pro.
It will generate different types of errors to showcase the improved formatting.
"""

# Install ErrorTrace Pro as the global exception handler
errortrace_pro.install()

# Define a nested function to create a more interesting traceback
def outer_function(value):
    return middle_function(value)

def middle_function(value):
    return inner_function(value)

def inner_function(value):
    # Create a complex local context
    local_var1 = "test string"
    local_var2 = [1, 2, 3, 4, 5]
    local_var3 = {"key1": "value1", "key2": "value2"}
    local_var4 = (1, "tuple", True)
    
    # Trigger different types of errors based on the value
    if value == 1:
        # ZeroDivisionError with locals
        return 1 / 0
    elif value == 2:
        # TypeError with string formatting
        return "string" + 123
    elif value == 3:
        # IndexError with list
        return local_var2[10]
    elif value == 4:
        # KeyError with dict
        return local_var3["nonexistent_key"]
    elif value == 5:
        # AttributeError
        return local_var1.nonexistent_method()
    else:
        # Custom exception
        raise ValueError(f"Invalid test value: {value}")

# Main function to run the tests
def main():
    print("\n===== ErrorTrace Pro Color Output Test =====\n")
    print("This test will demonstrate the enhanced color output of ErrorTrace Pro.")
    print("You'll see different types of errors with improved formatting.\n")
    
    # Get the test number from command line or use default
    try:
        test_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    except ValueError:
        test_num = 1
    
    print(f"Running test #{test_num}...\n")
    
    # Run the selected test
    try:
        result = outer_function(test_num)
        print(f"Test completed successfully with result: {result}")
    except SystemExit:
        # Catch SystemExit to prevent test termination
        print("\nTest completed with an error (as expected).")
    except Exception as e:
        # This should not be reached as ErrorTrace Pro will handle the exception
        print(f"Unexpected exception handling: {e}")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
