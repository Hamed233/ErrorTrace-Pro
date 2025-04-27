# 🔍 ErrorTrace Pro

<div align="center">

**Enhanced exception handling for Python with visual tracebacks, solution suggestions, and cloud logging.**

<img src="Screenshot.png" alt="ErrorTrace Pro Thumbnail" width="600"/>

[![Python versions](https://img.shields.io/badge/python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI version](https://img.shields.io/badge/pypi-v0.3.0-blue?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/errortrace-pro/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange?style=for-the-badge)](https://github.com/Hamed233/ErrorTrace-Pro)

</div>

---

Ever stared at a Python exception and wondered what went wrong? ErrorTrace Pro transforms cryptic tracebacks into clear, actionable insights. With stunning visualizations, solution suggestions, and integrated cloud logging, it's the exception handler you've always wanted.

## Features

- **Visual Traceback Mapping**: Beautiful, colorful, and informative tracebacks that highlight exactly what went wrong
- **Common Solution Database**: Intelligent suggestions to fix exceptions based on a comprehensive solutions library
- **Multi-Cloud Logging**: Seamlessly log exceptions to GCP, AWS, Azure, or custom HTTP endpoints
- **Drop-in Integration**: Works with any Python codebase with minimal configuration
- **Powerful CLI**: Run scripts with enhanced error handling directly from the command line

## Installation

```bash
pip install errortrace-pro
```

### Optional Features

ErrorTrace Pro provides several installation options for enhanced functionality:

```bash
# Install with Rich for enhanced visual output
pip install errortrace-pro[rich]

# Install with Click for better CLI experience
pip install errortrace-pro[cli]

# Install all optional dependencies
pip install errortrace-pro[all]
```

## Quick Start

### Basic Usage

The simplest way to use ErrorTrace Pro is to install it as a global exception handler:

```python
import errortrace_pro

# Install as global exception handler
errortrace_pro.install()

# Now all unhandled exceptions will be processed by ErrorTrace Pro
def main():
    # Your code here
    result = 10 / 0  # This will trigger a ZeroDivisionError with enhanced output

if __name__ == "__main__":
    main()
```

### With Custom Settings

You can customize the behavior of ErrorTrace Pro:

```python
import errortrace_pro

# Initialize with custom settings
handler = errortrace_pro.init(
    solutions_path="custom_solutions.json",  # Path to your custom solutions database
    cloud_logging=True,                      # Enable cloud logging
    cloud_provider="gcp",                    # Use Google Cloud for logging
    api_key="your-api-key",                  # API key for cloud logging
    project_id="your-project-id",            # Project ID for cloud logging
    enable_suggestions=True,                 # Enable solution suggestions
    colored_output=True,                     # Enable colored output
    verbose=True                             # Enable verbose output
)

# Install the custom handler
errortrace_pro.install(handler)

# Your code here
```

## Advanced Usage

### Running the CLI Tool

ErrorTrace Pro provides a command-line tool to run scripts with enhanced error handling:

```bash
# Run a script with ErrorTrace Pro
errortrace run script.py

# Run with cloud logging enabled
errortrace run script.py --cloud --provider=http --endpoint=http://logs.example.com

# Run with custom solutions database
errortrace run script.py --solutions=custom_solutions.json

# Generate a template solutions database
errortrace init-solutions --output=custom_solutions.json
```

### Creating a Custom Solutions Database

You can create a custom solutions database to provide specific suggestions for your own exceptions:

```json
{
    "CustomError": [
        "This is a custom solution for CustomError",
        "Another solution for this error type"
    ],
    "ValueError": [
        "Additional custom solution for ValueError",
        "Try converting the value to the correct type first"
    ]
}
```

### Setting Up Cloud Logging

ErrorTrace Pro supports logging exceptions to various cloud providers:

- Generic HTTP endpoint
- Google Cloud Logging
- AWS CloudWatch
- Azure Application Insights

Configure cloud logging with environment variables:

```bash
# Set environment variables for cloud logging
export ERRORTRACE_PROVIDER="gcp"
export ERRORTRACE_API_KEY="your-api-key"
export ERRORTRACE_PROJECT_ID="your-project-id"
export ERRORTRACE_ENDPOINT="http://logs.example.com"
```

Or set up programmatically:

```python
import os
os.environ["ERRORTRACE_PROVIDER"] = "gcp"
os.environ["ERRORTRACE_API_KEY"] = "your-api-key"
os.environ["ERRORTRACE_PROJECT_ID"] = "your-project-id"
```

### Testing Cloud Logging

#### Using a Generic HTTP Endpoint

The easiest way to test cloud logging without setting up actual cloud accounts:

```python
import errortrace_pro

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
def cause_error():
    # This will cause a ZeroDivisionError
    return 1/0

try:
    cause_error()
except Exception:
    pass  # The handler will log the exception
```

#### Testing with Google Cloud (GCP)

```python
import os
# Set environment variables
os.environ["ERRORTRACE_PROVIDER"] = "gcp"
os.environ["ERRORTRACE_API_KEY"] = "your-gcp-api-key"
os.environ["ERRORTRACE_PROJECT_ID"] = "your-gcp-project-id"

# Initialize ErrorTrace Pro
import errortrace_pro
handler = errortrace_pro.init(cloud_logging=True)
errortrace_pro.install(handler)

# Cause an error
1/0  # This will be logged to GCP
```

#### Testing with AWS CloudWatch

```python
import os
# Set environment variables
os.environ["ERRORTRACE_PROVIDER"] = "aws"
os.environ["ERRORTRACE_API_KEY"] = "your-aws-access-key-id"
os.environ["ERRORTRACE_SECRET_KEY"] = "your-aws-secret-access-key"
os.environ["ERRORTRACE_REGION"] = "us-east-1"  # Or your preferred region

# Initialize ErrorTrace Pro
import errortrace_pro
handler = errortrace_pro.init(cloud_logging=True)
errortrace_pro.install(handler)

# Cause an error
1/0  # This will be logged to AWS CloudWatch
```

#### Testing with Azure Application Insights

```python
import os
# Set environment variables
os.environ["ERRORTRACE_PROVIDER"] = "azure"
os.environ["ERRORTRACE_API_KEY"] = "your-azure-instrumentation-key"

# Initialize ErrorTrace Pro
import errortrace_pro
handler = errortrace_pro.init(cloud_logging=True)
errortrace_pro.install(handler)

# Cause an error
1/0  # This will be logged to Azure Application Insights
```

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `errortrace_pro.init()` | Initialize ErrorTrace Pro with custom settings |
| `errortrace_pro.install()` | Install ErrorTrace Pro as the global exception handler |
| `errortrace_pro.uninstall()` | Restore the original sys.excepthook |

### Classes

| Class | Description |
|-------|-------------|
| `errortrace_pro.handler.ExceptionHandler` | The main exception handler class |
| `errortrace_pro.visualizer.TracebackVisualizer` | The traceback visualization class |
| `errortrace_pro.solutions.SolutionProvider` | The solution provider class |
| `errortrace_pro.cloud_logger.CloudLogger` | The cloud logging class |

## Contributing

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Roadmap

- [ ] AI-powered solution suggestions
- [ ] Integration with more IDEs and tools
- [ ] Performance profiling during exception handling
- [ ] Customizable visualization themes
- [ ] Multi-language support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- The [Rich](https://github.com/Textualize/rich) library for beautiful terminal formatting
- The open-source Python community for inspiration and support

---

<div align="center">
  <p>Made by Hamed Esam ❤️</p>
  <p>
    <a href="https://github.com/Hamed233/ErrorTrace-Pro">GitHub</a> •
    <a href="https://pypi.org/project/errortrace-pro">PyPI</a>
  </p>
</div>
