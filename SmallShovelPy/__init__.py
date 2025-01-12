import os
import importlib
import json


# Metadata
with open('metadata.json', 'r') as file:
    metadata = json.load(file)

__version__ = metadata["__version__"]
__author__ = metadata["__author__"]
__license__ = metadata["__license__"]


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
