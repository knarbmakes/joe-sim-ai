import os
import importlib

# Automatically import all modules in the current directory
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith('.py') and file != '__init__.py':
        module_name = file[:-3]
        importlib.import_module('.' + module_name, package='tools')
