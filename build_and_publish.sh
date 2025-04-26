#!/bin/bash
# Script to build and publish ErrorTrace Pro to PyPI

# Ensure we have the latest versions of packaging tools
pip install --upgrade pip build twine

# Clean up previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build

# Check the distribution
twine check dist/*

echo ""
echo "Build complete! The packages are in the 'dist/' directory."
echo ""
echo "To publish to PyPI Test, run:"
echo "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo ""
echo "To publish to PyPI, run:"
echo "twine upload dist/*"
echo ""
echo "Note: You will need PyPI credentials to upload."