"""Pytest bootstrap: ensure the project root is importable.

Lets tests use package imports like `from checkers.PUCInsurance import ...`
regardless of the directory pytest is invoked from.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
