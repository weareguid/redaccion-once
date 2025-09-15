from pathlib import Path
import runpy

# Run the root app.py so this file can be used as Streamlit entrypoint
root_app = Path(__file__).resolve().parents[2] / 'app.py'
runpy.run_path(str(root_app))
