"""
Cloud logging example for ErrorTrace Pro

This example demonstrates how to use ErrorTrace Pro with different cloud logging providers.
"""

import os
import sys
import errortrace_pro


def test_http_endpoint():
    """Test logging to a generic HTTP endpoint"""
    print("Testing HTTP endpoint logging...")
    
    # Initialize with HTTP endpoint logging
    handler = errortrace_pro.init(
        cloud_logging=True,
        cloud_provider="http",
        api_key="test-key",  # Can be any value for testing
        endpoint="https://httpbin.org/post"  # This is a test endpoint that echoes back what you send
    )
    
    # Install the handler
    errortrace_pro.install(handler)
    
    # Generate an exception to test
    try:
        # This will cause a ZeroDivisionError
        return 1/0
    except Exception as e:
        print(f"Caught exception: {e}")
        print("The error has been logged to the HTTP endpoint.")


def test_gcp_logging():
    """Test logging to Google Cloud Logging"""
    print("Testing Google Cloud Logging...")
    
    # Check if API key is provided
    api_key = os.environ.get("GCP_API_KEY")
    project_id = os.environ.get("GCP_PROJECT_ID")
    
    if not api_key or not project_id:
        print("GCP API key or project ID not found in environment variables.")
        print("Set GCP_API_KEY and GCP_PROJECT_ID to test GCP logging.")
        return
    
    # Initialize ErrorTrace Pro with GCP logging
    handler = errortrace_pro.init(
        cloud_logging=True,
        cloud_provider="gcp",
        api_key=api_key,
        project_id=project_id
    )
    
    # Install the handler
    errortrace_pro.install(handler)
    
    # Generate an exception to test
    try:
        # This will cause an IndexError
        data = [1, 2, 3]
        return data[10]
    except Exception as e:
        print(f"Caught exception: {e}")
        print("The error has been logged to Google Cloud Logging.")


def test_aws_logging():
    """Test logging to AWS CloudWatch"""
    print("Testing AWS CloudWatch Logging...")
    
    # Check if API keys are provided
    api_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_REGION", "us-east-1")
    
    if not api_key or not secret_key:
        print("AWS API keys not found in environment variables.")
        print("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to test AWS logging.")
        return
    
    # Set up AWS environment variables
    os.environ["ERRORTRACE_PROVIDER"] = "aws"
    os.environ["ERRORTRACE_API_KEY"] = api_key
    os.environ["ERRORTRACE_SECRET_KEY"] = secret_key
    os.environ["ERRORTRACE_REGION"] = region
    
    # Initialize ErrorTrace Pro
    handler = errortrace_pro.init(cloud_logging=True)
    errortrace_pro.install(handler)
    
    # Generate an exception to test
    try:
        # This will cause a TypeError
        return "string" + 42
    except Exception as e:
        print(f"Caught exception: {e}")
        print("The error has been logged to AWS CloudWatch.")


def test_azure_logging():
    """Test logging to Azure Application Insights"""
    print("Testing Azure Application Insights Logging...")
    
    # Check if API key is provided
    api_key = os.environ.get("AZURE_INSTRUMENTATION_KEY")
    
    if not api_key:
        print("Azure instrumentation key not found in environment variables.")
        print("Set AZURE_INSTRUMENTATION_KEY to test Azure logging.")
        return
    
    # Set up Azure environment variables
    os.environ["ERRORTRACE_PROVIDER"] = "azure"
    os.environ["ERRORTRACE_API_KEY"] = api_key
    
    # Initialize ErrorTrace Pro
    handler = errortrace_pro.init(cloud_logging=True)
    errortrace_pro.install(handler)
    
    # Generate an exception to test
    try:
        # This will cause an AttributeError
        return "ErrorTrace Pro".nonexistent_method()
    except Exception as e:
        print(f"Caught exception: {e}")
        print("The error has been logged to Azure Application Insights.")


def main():
    """Main function to test different cloud logging providers"""
    print("ErrorTrace Pro - Cloud Logging Example")
    print("-" * 50)
    
    # Always test HTTP endpoint since it doesn't require credentials
    test_http_endpoint()
    print("\n" + "-" * 50 + "\n")
    
    # Test other providers if requested
    if len(sys.argv) > 1:
        provider = sys.argv[1].lower()
        
        if provider == "gcp":
            test_gcp_logging()
        elif provider == "aws":
            test_aws_logging()
        elif provider == "azure":
            test_azure_logging()
        elif provider == "all":
            test_gcp_logging()
            print("\n" + "-" * 50 + "\n")
            test_aws_logging()
            print("\n" + "-" * 50 + "\n")
            test_azure_logging()
        else:
            print(f"Unknown provider: {provider}")
            print("Available providers: gcp, aws, azure, all")
    
    print("\nDone!")


if __name__ == "__main__":
    main()