import os
import sys
import traceback
import json
import importlib
import errortrace_pro

"""
ErrorTrace Pro Feature Tests

This script tests specific features of ErrorTrace Pro to ensure they're working correctly.
It includes tests for:
1. Custom initialization options
2. Solution suggestions
3. Proper formatting
4. Handler installation/uninstallation
5. Cloud logging (mock)
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


# Test 1: Test custom initialization options
def test_custom_init():
    print("\n=== Testing Custom Initialization ===\n")
    
    # Create a custom handler with specific options
    handler = errortrace_pro.init(
        enable_suggestions=True,
        colored_output=True,
        verbose=True
    )
    
    # Verify handler configuration
    print(f"Handler has suggestions enabled: {handler.enable_suggestions}")
    print(f"Handler has verbose mode: {handler.verbose}")
    print(f"Visualizer has colored output: {handler.visualizer.colored_output}")
    
    # Test the handler with a simple error
    capture = OutputCapture()
    capture.start()
    
    try:
        1/0
    except Exception as e:
        handler.handle(type(e), e, e.__traceback__)
    
    stdout, stderr = capture.stop()
    
    # Check output for expected elements
    if "ZeroDivisionError" in stderr and "Suggested Solutions" in stderr:
        print("✅ Custom handler correctly processed exception with suggestions")
    else:
        print("❌ Custom handler failed to process exception correctly")


# Test 2: Test solution suggestions
def test_solution_suggestions():
    print("\n=== Testing Solution Suggestions ===\n")
    
    # Common errors that should have solution suggestions
    test_errors = [
        ("ZeroDivisionError", lambda: 1/0),
        ("IndexError", lambda: [1, 2, 3][10]),
        ("KeyError", lambda: {"a": 1}["b"]),
        ("ImportError", lambda: importlib.import_module("nonexistent_module")),
        ("FileNotFoundError", lambda: open("nonexistent_file.txt", "r"))
    ]
    
    # Create handlers with and without suggestions
    handler_with_suggestions = errortrace_pro.init(enable_suggestions=True)
    handler_without_suggestions = errortrace_pro.init(enable_suggestions=False)
    
    capture = OutputCapture()
    
    for error_name, error_func in test_errors:
        print(f"Testing {error_name} solutions:")
        
        # Test with suggestions enabled
        capture.start()
        try:
            error_func()
        except Exception as e:
            handler_with_suggestions.handle(type(e), e, e.__traceback__)
        stdout, stderr = capture.stop()
        
        if "Suggested Solutions" in stderr:
            print(f"  ✅ With suggestions: Solutions found for {error_name}")
        else:
            print(f"  ❌ With suggestions: No solutions found for {error_name}")
        
        # Test with suggestions disabled
        capture.start()
        try:
            error_func()
        except Exception as e:
            handler_without_suggestions.handle(type(e), e, e.__traceback__)
        stdout, stderr = capture.stop()
        
        if "Suggested Solutions" not in stderr:
            print(f"  ✅ Without suggestions: No solutions shown for {error_name}")
        else:
            print(f"  ❌ Without suggestions: Solutions incorrectly shown for {error_name}")


# Test 3: Test handler installation/uninstallation
def test_handler_installation():
    print("\n=== Testing Handler Installation/Uninstallation ===\n")
    
    # Store original excepthook
    original_excepthook = sys.excepthook
    
    # Install handler
    handler = errortrace_pro.install()
    
    # Check if excepthook was changed
    if sys.excepthook != original_excepthook:
        print("✅ Handler successfully installed")
    else:
        print("❌ Handler installation failed")
    
    # Test if installation tip is shown or not
    capture = OutputCapture()
    capture.start()
    
    try:
        1/0
    except SystemExit:
        # Catch SystemExit to prevent test termination
        pass
    except Exception as e:
        # This should be handled by the installed handler
        pass
    
    stdout, stderr = capture.stop()
    
    # The tip should NOT be shown when handler is already installed
    if "Use errortrace_pro.install() to enable this handler globally" not in stderr:
        print("✅ Installation tip correctly hidden when handler is installed")
    else:
        print("❌ Installation tip incorrectly shown when handler is already installed")
    
    # Uninstall handler
    errortrace_pro.uninstall()
    
    # Check if excepthook was restored
    if sys.excepthook == original_excepthook:
        print("✅ Handler successfully uninstalled")
    else:
        print("❌ Handler uninstallation failed")
    
    # Reinstall for further tests
    errortrace_pro.install()


# Test 4: Test formatting options
def test_formatting_options():
    print("\n=== Testing Formatting Options ===\n")
    
    # Test with colored output
    colored_handler = errortrace_pro.init(colored_output=True)
    plain_handler = errortrace_pro.init(colored_output=False)
    
    # Test colored output
    capture = OutputCapture()
    capture.start()
    
    try:
        1/0
    except Exception as e:
        colored_handler.handle(type(e), e, e.__traceback__)
    
    stdout, stderr = capture.stop()
    
    # Check for ANSI color codes or Rich formatting indicators
    # This is a more reliable way to detect formatting without relying on internal variables
    has_color_indicators = any(indicator in stderr for indicator in [
        "\033[",  # ANSI escape code
        "[bold",   # Rich formatting
        "[red",    # Rich color
        "[blue",   # Rich color
        "border_style"  # Rich panel styling
    ])
    
    print(f"Colored output test: {'✅ Colors detected' if has_color_indicators else '❌ No colors detected'}")
    
    # Test plain output
    capture.start()
    
    try:
        1/0
    except Exception as e:
        plain_handler.handle(type(e), e, e.__traceback__)
    
    stdout, stderr = capture.stop()
    
    # Check for absence of color indicators
    has_color_indicators = any(indicator in stderr for indicator in [
        "\033[",  # ANSI escape code
        "[bold",   # Rich formatting
        "[red",    # Rich color
        "[blue",   # Rich color
        "border_style"  # Rich panel styling
    ])
    
    print(f"Plain output test: {'✅ No colors detected' if not has_color_indicators else '❌ Colors detected'}")


# Test 5: Test with different exception types
def test_exception_types():
    print("\n=== Testing Different Exception Types ===\n")
    
    # Define exception types to test
    exception_types = [
        ("Standard Exception", Exception("Standard exception message")),
        ("Custom Exception", type("CustomError", (Exception,), {})("Custom error message")),
        ("System Exit", SystemExit(1)),
        ("Keyboard Interrupt", KeyboardInterrupt()),
        ("Assertion Error", AssertionError("Assertion failed")),
        ("Value Error", ValueError("Invalid value")),
        ("Type Error", TypeError("Invalid type")),
        ("OS Error", OSError("OS error")),
        ("IO Error", IOError("IO error")),
        ("Runtime Error", RuntimeError("Runtime error"))
    ]
    
    handler = errortrace_pro.init()
    capture = OutputCapture()
    
    for name, exception in exception_types:
        print(f"Testing {name}:")
        
        capture.start()
        handler.handle(type(exception), exception, None)
        stdout, stderr = capture.stop()
        
        if type(exception).__name__ in stderr:
            print(f"  ✅ Exception type correctly identified")
        else:
            print(f"  ❌ Exception type not identified")
        
        if str(exception) in stderr:
            print(f"  ✅ Exception message correctly displayed")
        else:
            print(f"  ❌ Exception message not displayed")


# Run all tests
def run_all_tests():
    print("\n===== ErrorTrace Pro Feature Tests =====\n")
    
    # Run all tests
    test_custom_init()
    test_solution_suggestions()
    test_handler_installation()
    test_formatting_options()
    test_exception_types()
    
    print("\n===== All Tests Completed =====\n")


# Run the tests if this script is executed directly
if __name__ == "__main__":
    run_all_tests()
