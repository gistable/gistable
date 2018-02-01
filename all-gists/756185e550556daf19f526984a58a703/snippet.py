
# 1. Download and install the latest Anaconda distribution from  https://www.continuum.io/downloads#macos

# 2. Create a new Python environment. Make sure you choose python 3.5 as your python version for the virtual environment:

conda create -n myenv python=3.5

# 3. Activate the new environment using:

source activate myenv

# 4. OpenCV depends on NumPy, which can be installed with:

conda install numpy

# 5.Install the anaconda-client command utility to search for the OpenCV binary in Conda:

conda install anaconda-client

# 6. Search for OpenCV 3:

anaconda search -t conda opencv3

# 7. You will see a few options but choose a package that supports osx-64. For example choose https://conda.anaconda.org/menpo which support osx-64.

conda install --channel https://conda.anaconda.org/menpo opencv3

# 8. Test Open CV with below code. It should return the installed Open CV version.

import cv2
print("OpenCV version:")
print(cv2.__version__)