##### Install a lot of stuff first #####

$sudo apt-get update

##install python 
$ wget http://09c8d0b2229f813c1b93-c95ac804525aac4b6dba79b00b39d1d3.r79.cf1.rackcdn.com/Anaconda-2.0.1-Linux-x86_64.sh
$ sudo bash anaconda........sh
 
##install necessary libs
$ sudo apt-get install -y python-matplotlib python-tornado ipython ipython-notebook python-setuptools python-pip
$ sudo pip install  ipython pyzmq jinja2 pygments sphinx
$ sudo pip install --upgrade ipython

$ sudo apt-get install -y  build-essential python-dev python-numpy python-scipy python-sklearn
                       libatlas-dev libatlas3gf-base
 
 
 
#### Start IPython, generate SHA1 password to use for IPython Notebook server
 
$ ipython
Python 2.7.5 |Anaconda 1.8.0 (x86_64)| (default, Oct 24 2013, 07:02:20)
Type "copyright", "credits" or "license" for more information.
 
IPython 1.1.0 -- An enhanced Interactive Python.
? -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help -> Python's own help system.
object? -> Details about 'object', use 'object??' for extra details.
 
In [1]: from IPython.lib import passwd
 
In [2]: passwd()
Enter password:
Verify password:
Out[2]: 'sha1:207eb1f4671f:92af695...'
 
#### Create nbserver profile
 
$ ipython profile create nbserver
[ProfileCreate] Generating default config file: u'/.ipython/profile_nbserver/ipython_config.py'
[ProfileCreate] Generating default config file: u'/.ipython/profile_nbserver/ipython_qtconsole_config.py'
[ProfileCreate] Generating default config file: u'/.ipython/profile_nbserver/ipython_notebook_config.py'
[ProfileCreate] Generating default config file: u'/.ipython/profile_nbserver/ipython_nbconvert_config.py'
 
#### Create self-signed SSL certificate
 
$ openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
 
#### Modify ipython_notebook_config.py configuration file
#### Add these lines to the top of the file; no other changes necessary
#### Obviously, you'll want to add your path to the .pem key and your password
 
# Configuration file for ipython-notebook.
 
c = get_config()
 
# Kernel config
c.IPKernelApp.pylab = 'inline' # if you want plotting support always
 
# Notebook config
c.NotebookApp.certfile = u'/home/ubuntu/certificates/mycert.pem'
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.password = u'sha1:207eb1f4671f:92af695...'
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = 8888
 
#### Start IPython Notebook on the remote server
 
$ ipython notebook --profile=nbserver