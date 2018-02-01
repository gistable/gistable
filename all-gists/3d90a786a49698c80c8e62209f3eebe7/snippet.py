# Python 2.x
import os.path
os.path.isfile(fname)

# Python 3.4
from pathlib import Path
my_file = Path("/path/to/file")
if my_file.is_file():
    # file exists