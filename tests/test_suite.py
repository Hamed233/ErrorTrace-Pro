import os
import sys
import traceback
import json
import importlib
import errortrace_pro

"""
ErrorTrace Pro Test Suite

This script tests various error scenarios to ensure ErrorTrace Pro is working correctly.
Each test case triggers a different type of exception and verifies the output.
"""

# Capture stdout/stderr for testing
class OutputCapture:
    def __init__(self):
        self.stdout_capture = None
        self.stderr_capture = None
        self.stdout_backup = None
        self.stderr_backup = None
    
    def start(self):
        from io import StringIO
        self.stdout_capture = StringIO()
        self.stderr_capture = StringIO()
        self.stdout_backup = sys.stdout
        self.stderr_backup = sys.stderr
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
    
    def stop(self):
        sys.stdout = self.stdout_backup
        sys.stderr = self.stderr_backup
        return self.stdout_capture.getvalue(), self.stderr_capture.getvalue()


# Test cases
test_cases = [
    {
        "name": "ZeroDivisionError",
        "function": lambda: 1/0,
        "expected_fragments": [
            "ZeroDivisionError: division by zero",
            "Exception Detected"
        ]
    },
    {
        "name": "TypeError",
        "function": lambda: "string" + 123,
        "expected_fragments": [
            "TypeError: can only concatenate str",
            "Exception Detected"
        ]
    },
    {
        "name": "IndexError",
        "function": lambda: [1, 2, 3][10],
        "expected_fragments": [
            "IndexError: list index out of range",
            "Exception Detected"
        ]
    },
    {
        "name": "KeyError",
        "function": lambda: {"a": 1}["b"],
        "expected_fragments": [
            "KeyError",
            "Exception Detected"
        ]
    },
    {
        "name": "AttributeError",
        "function": lambda: "string".nonexistent_method(),
        "expected_fragments": [
            "AttributeError: 'str' object has no attribute 'nonexistent_method'",
            "Exception Detected"
        ]
    },
    {
        "name": "ImportError",
        "function": lambda: importlib.import_module("nonexistent_module"),
        "expected_fragments": [
            "ModuleNotFoundError: No module named 'nonexistent_module'",
            "Exception Detected"
        ]
    },
    {
        "name": "FileNotFoundError",
        "function": lambda: open("nonexistent_file.txt", "r"),
        "expected_fragments": [
            "FileNotFoundError",
            "Exception Detected"
        ]
    },
    {
        "name": "Custom Exception",
        "function": lambda: (_ for _ in ()).throw(Exception("Custom error message")),
        "expected_fragments": [
            "Exception: Custom error message",
            "Exception Detected"
        ]
    },
    {
        "name": "Nested Exception",
        "function": lambda: nested_exception_func(),
        "expected_fragments": [
            "ValueError: Inner exception",
            "Exception Detected",
            "nested_exception_func"
        ]
    },
    {
        "name": "Syntax Error Simulation",
        "function": lambda: exec("if True print('invalid syntax')"),
        "expected_fragments": [
            "SyntaxError",
            "Exception Detected"
        ]
    }
]

# Helper function for nested exception test
def nested_exception_func():
    try:
        inner_func()
    except Exception as e:
        raise ValueError("Inner exception") from e

def inner_func():
    raise RuntimeError("Original error")

# Run tests
def run_tests():
    # Install ErrorTrace Pro handler
    handler = errortrace_pro.install()
    
    # Store original excepthook to restore later
    original_excepthook = sys.excepthook
    
    # Test results
    results = []
    
    # Create output capture
    output_capture = OutputCapture()
    
    for test_case in test_cases:
        print(f"\n{'=' * 50}")
        print(f"Testing: {test_case['name']}")
        print(f"{'-' * 50}")
        
        # Start capturing output
        output_capture.start()
        
        # Run the test case
        try:
            test_case["function"]()
        except SystemExit:
            # Catch SystemExit to prevent test termination
            pass
        except Exception as e:
            # Directly handle the exception if it wasn't caught by ErrorTrace Pro
            handler.handle(type(e), e, e.__traceback__)
        
        # Stop capturing and get output
        stdout, stderr = output_capture.stop()
        
        # Check if expected fragments are in the output
        success = True
        missing_fragments = []
        for fragment in test_case["expected_fragments"]:
            if fragment not in stderr and fragment not in stdout:
                success = False
                missing_fragments.append(fragment)
        
        # Store result
        result = {
            "test_name": test_case["name"],
            "success": success,
            "missing_fragments": missing_fragments if not success else [],
            "stdout": stdout,
            "stderr": stderr
        }
        results.append(result)
        
        # Print result
        if success:
            print(f"✅ PASS: {test_case['name']}")
        else:
            print(f"❌ FAIL: {test_case['name']}")
            print(f"Missing fragments: {', '.join(missing_fragments)}")
        
        # Print a sample of the output
        print("\nOutput sample:")
        output_lines = stderr.split('\n')
        print('\n'.join(output_lines[:min(10, len(output_lines))]))
        if len(output_lines) > 10:
            print(f"... ({len(output_lines) - 10} more lines)")
    
    # Restore original excepthook
    sys.excepthook = original_excepthook
    
    # Print summary
    print(f"\n{'=' * 50}")
    print(f"Test Summary")
    print(f"{'-' * 50}")
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    # Print failed tests
    if failed > 0:
        print("\nFailed tests:")
        for result in results:
            if not result["success"]:
                print(f"- {result['test_name']}: Missing fragments: {', '.join(result['missing_fragments'])}")
    
    return results

# Run the tests if this script is executed directly
if __name__ == "__main__":
    run_tests()
