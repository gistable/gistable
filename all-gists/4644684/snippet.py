'''
PyPi Binary Downloader

Pulls the latest binary package from pypi, and installs it intelligently

Accounts for current python version and path (including virtualenv), and 
system architecture (32 vs 64 bit)

If an alternate filename is provided, it will use that instead of the default
created by distutils (<package>-<version>.win**-py*.*.exe)
'''
import pip
import sys
import urllib
import tempfile
import zipfile
import os
import shutil


def get_latest_version(package):
    prev_stdout = sys.stdout
    tmp_file = tempfile.mktemp()
    with open(tmp_file, 'wb') as fid:
        sys.stdout = fid
        pip.main(['search', package])
        sys.stdout = prev_stdout
    with open(tmp_file) as fid:
        text = fid.readlines()
    if text:
        if not 'LATEST' in ''.join(text):
            return 'current'
        return text[2].split()[-1]


def download_file(url, fname):
    temp_path = tempfile.mkdtemp()
    temp_path = os.path.join(temp_path, fname)
    urllib.urlretrieve(url, temp_path)
    try:
        zf = zipfile.ZipFile(temp_path)
    except zipfile.BadZipfile:
        return
    else:
        zf.extractall(os.path.dirname(temp_path))
        zf.close()
    return temp_path
   
   
def get_binary(package, alt_name=None):
    version = get_latest_version(package)
    if not version:
        print('Could not locate package: ' + package)
        return
    if version == 'current':
        print('Already using latest version of: ' + package)
        return
    py_version = sys.version[:3]
    if '32 bit' in sys.version:
        arch = 'win32'
    else:
        arch = 'win-amd64'
    fname = "{0}-{1}.{2}-py{3}.exe".format(package, version, arch, py_version)
    if alt_name:
        fname = alt_name
    print('Downloading: ' + fname)
    url = "http://pypi.python.org/packages/any/{0}/{1}/{2}".format(package[0], package, fname)
    path = download_file(url, fname)
    if path:
        return path
    url = "http://pypi.python.org/packages/{0}/{1}/{2}/{3}".format(py_version, package[0], package, fname)
    path = download_file(url, fname)
    if path:
        return path
    else:
        print('Could not retreive file: {0} for {1}, consider alt_name'.format(fname, package))
    
    
def install_files(package, path):
    if os.path.exists(os.path.join(path, 'SCRIPTS')):
        site_package_dir = pip.util.site_packages
        lib_dir = os.path.dirname(site_package_dir)
        python_dir = os.path.dirname(lib_dir)
        script_dst = os.path.join(python_dir, 'Scripts')
        script_src = os.path.join(path, 'SCRIPTS')
        for fname in os.listdir(script_src):
            fpath = os.path.join(script_src, fname)
            shutil.copy(fpath, script_dst)
    package_dir = pip.util.site_packages
    if os.path.exists(os.path.join(path, 'PURELIB')):
        source_dir = os.path.join(path, 'PURELIB')
    else:
        source_dir = os.path.join(path, 'PLATLIB')
    for dpath in os.listdir(source_dir):
        src_path = os.path.join(source_dir, dpath)
        dst_path = os.path.join(package_dir, dpath)
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
    
    
def install_package(package, alt_name=None):
    path = get_binary(package, alt_name)
    if not path:
        return
    install_files(package, os.path.dirname(path))
    

if __name__ == '__main__':
    #install_package('oct2py')
    #install_package('ipython', 'ipython-0.13.1.py2-win32-PROPER.exe')
    #install_package('scikit-learn')
    install_package('pandas')
    