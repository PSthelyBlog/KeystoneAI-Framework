#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner with coverage reporting for DCM tests.
"""

import os
import sys
import unittest
import tempfile
import shutil
import coverage

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Start coverage
cov = coverage.Coverage(source=['framework_core.dcm'])
cov.start()

# Import the test cases
from test_dcm_basic import TestDCMBasic

# Run the tests
suite = unittest.TestLoader().loadTestsFromTestCase(TestDCMBasic)
result = unittest.TextTestRunner(verbosity=2).run(suite)

# Stop coverage and report
cov.stop()
cov.save()
cov.report(show_missing=True)

# Exit with appropriate status
sys.exit(not result.wasSuccessful())