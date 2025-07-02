import os
import sys

# Ensure the project root and the 'generated' directory are in the Python path
# so that pytest can find the main module and generated protobuf files.

# Assuming conftest.py is in the project root directory /app
_project_root = os.path.dirname(os.path.abspath(__file__))

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_generated_dir = os.path.join(_project_root, "generated")
if os.path.isdir(_generated_dir) and _generated_dir not in sys.path:
    sys.path.insert(0, _generated_dir)

print(f"PYTHONPATH for pytest (from conftest.py): {sys.path}")
