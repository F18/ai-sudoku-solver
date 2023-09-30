# tests/conftest.py

import sys
import os

# Get the current directory (tests directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
project_root = os.path.dirname(current_dir)

# Add the project root directory to sys.path
sys.path.insert(0, project_root)