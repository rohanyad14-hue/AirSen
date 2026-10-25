# Root entrypoint for Streamlit
import os
import sys

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Run frontend/app.py
from frontend.app import *
