"""
Main application module for BRAID Manager.
This is the entry point that Briefcase uses to start the app.
"""

import sys
from pathlib import Path

# Ensure the src directory is in the path for imports
# This allows the existing src/ structure to work unchanged
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.ui_qt.app import main

# Export main for Briefcase
__all__ = ["main"]
