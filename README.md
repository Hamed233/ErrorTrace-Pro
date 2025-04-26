# ErrorTrace Pro

Enhanced exception handling for Python with visual tracebacks, solution suggestions, and cloud logging.

![Python versions](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-orange)

## Features

- 🎨 **Visual Traceback Mapping**: Beautiful, colorful, and informative tracebacks
- 💡 **Common Solution Database**: Suggests fixes for known exceptions
- ☁️ **Auto-logging to Cloud**: Log exceptions to various cloud providers
- 🚀 **Easy Integration**: Works with existing Python code
- 🛠️ **CLI Tool**: Run scripts with enhanced error handling

## Installation

```bash
pip install errortrace-pro
```

For additional features, you can install the package with extras:

```bash
# Install with Rich for enhanced visual output
pip install errortrace-pro[rich]

# Install with Click for better CLI experience
pip install errortrace-pro[cli]

# Install with all optional dependencies
pip install errortrace-pro[all]

# Install with Flask for the web interface
pip install errortrace-pro[web]
```

## Basic Usage

### As a Global Exception Handler

The simplest way to use ErrorTrace Pro is to install it as a global exception handler:

```python
import errortrace_pro

# Install as global exception handler
errortrace_pro.install()

# Your code here, now with enhanced error handling
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

### Using the CLI Tool

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

## Custom Solutions Database

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

## Cloud Logging

ErrorTrace Pro can log exceptions to various cloud providers:

- Generic HTTP endpoint
- Google Cloud Logging
- AWS CloudWatch
- Azure Application Insights

Set up cloud logging with environment variables:

```bash
# Set environment variables for cloud logging
export ERRORTRACE_PROVIDER="gcp"
export ERRORTRACE_API_KEY="your-api-key"
export ERRORTRACE_PROJECT_ID="your-project-id"
export ERRORTRACE_ENDPOINT="http://logs.example.com"
```

## Web Interface

ErrorTrace Pro includes a web interface for interactive error experimentation:

```python
from errortrace_pro.web import create_app

app = create_app()
app.run(host='0.0.0.0', port=5000, debug=True)
```

## API Reference

### `errortrace_pro.init()`

Initialize ErrorTrace Pro with custom settings.

### `errortrace_pro.install()`

Install ErrorTrace Pro as the global exception handler.

### `errortrace_pro.uninstall()`

Restore the original sys.excepthook.

### `errortrace_pro.handler.ExceptionHandler`

The main exception handler class.

### `errortrace_pro.visualizer.TracebackVisualizer`

The traceback visualization class.

### `errortrace_pro.solutions.SolutionProvider`

The solution provider class.

### `errortrace_pro.cloud_logger.CloudLogger`

The cloud logging class.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
