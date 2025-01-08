import os
import importlib


# Data Payload
__version__ = "0.0.1"
__author__ = "Small Shovel"
__license__ = "GPLv3"


# Get the current directory
current_dir = os.path.dirname(__file__)

# List all .py files in the directory excluding __init__.py
module_files = [
    f[:-3] for f in os.listdir(current_dir)
    if f.endswith(".py") and f != "__init__.py"
]

# Import classes dynamically
globals().update({
    module_name: getattr(importlib.import_module(f".{module_name}", __package__), module_name)
    for module_name in module_files
})
