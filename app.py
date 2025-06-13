#!/usr/bin/env python3
"""
Once Noticias - Sistema Editorial Optimizado
Entry point for deployment
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main Streamlit app
from interfaces.streamlit_app import main

if __name__ == "__main__":
    main()