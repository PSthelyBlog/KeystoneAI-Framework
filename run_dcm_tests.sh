#!/bin/bash
# This script installs the required dependencies and runs the DCM tests

# Activate the virtual environment if it exists
if [ -d "venv/bin" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Install pytest and related dependencies
echo "Installing test dependencies..."
pip install pytest pytest-cov pytest-mock

# Run the tests
echo "Running DCM tests..."
python -m pytest tests/unit/framework_core/test_dcm.py -v

# Return to the previous state
echo "Test run complete."