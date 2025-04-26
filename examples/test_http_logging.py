"""
Simple HTTP endpoint logging test for ErrorTrace Pro
"""

import errortrace_pro

# Initialize with HTTP endpoint logging
handler = errortrace_pro.init(
    cloud_logging=True,
    cloud_provider="http",
    api_key="test-key",  
    endpoint="https://httpbin.org/post"  # This test endpoint echoes back what you send
)

# Install the handler
errortrace_pro.install(handler)

print("ErrorTrace Pro - HTTP Logging Test")
print("-" * 40)
print("Generating a test exception...")

# Generate an exception to test
def cause_error():
    # This will cause a ZeroDivisionError
    return 1/0

try:
    cause_error()
except Exception as e:
    print(f"Caught exception: {e}")
    print("The error has been logged to the HTTP endpoint.")
    print("Check the response above to verify the logging worked correctly.")

print("\nDone!")