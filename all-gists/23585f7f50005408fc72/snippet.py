#! python3.4
from setuptools import setup
import os
import py2exe
import matplotlib

includes = ["sip",
            "PyQt5",
            "PyQt5.QtCore",
            "PyQt5.QtGui",
            "numpy",
            "matplotlib.backends.backend_qt5agg",
            "scipy",
            "scipy.sparse.csgraph._validation",
            "scipy.special._ufuncs_cxx",
            "pandas"]

datafiles = [("platforms", ["C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins" +
                            "\\platforms\\qwindows.dll"]),
             ("", [r"c:\windows\syswow64\MSVCP100.dll",
                   r"c:\windows\syswow64\MSVCR100.dll"])] + \
            matplotlib.get_py2exe_datafiles()

setup(
    name='sampleapp',
    version=VERSION,
    packages=['sampleapp'],
    url='',
    license='',
    windows=[{"script": "startupscript.pyw"}],
    scripts=['startupscript.pyw'],
    data_files=datafiles,
    install_requires=['numpy>=1.8.1',
                      'matplotlib>=1.4.2',
                      'scipy>=0.14.0',
                      'pandas>=0.14.1'],
    options={
        "py2exe":{
            "includes": includes,
        }
    }
)
