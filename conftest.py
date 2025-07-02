"""
Configuration for pytest.

This file is automatically discovered by pytest and is used to configure
aspects of the testing environment. Currently, its primary role is to
modify the system path (`sys.path`) to ensure that the main application
modules and generated protobuf files are discoverable by pytest during
test collection and execution.

By adding the project root and the 'generated' directory to `sys.path`,
tests can import modules like `build.py` and `generated.*_pb2` without
requiring complex relative imports or installation of the project as a package.
"""

import os
import sys

# Assuming conftest.py is in the project root directory.
_project_root: str = os.path.dirname(os.path.abspath(__file__))

# Add project root to sys.path
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Add 'generated' directory (for protobufs) to sys.path if it exists
_generated_dir: str = os.path.join(_project_root, "generated")
if os.path.isdir(_generated_dir) and _generated_dir not in sys.path:
    sys.path.insert(0, _generated_dir)

# For debugging sys.path issues during testing, uncomment the following line:
# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.debug("PYTHONPATH for pytest (from conftest.py): %s", sys.path)
# print(f"PYTHONPATH for pytest (from conftest.py): {sys.path}") # Original print
