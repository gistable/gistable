import compileall
import os

# Get current working directory
curr_dir = os.getcwd()

# Compiles all python files to pyc
compileall.compile_dir(curr_dir, force=True)

# Recursively iterates to find .py files and remove them
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.py'):
            os.remove(os.path.join(root, file))