# Flask wsgi for simple application
# (dziala na linuxpl.com)

import os, sys
p = os.path.split(os.path.abspath(__file__))[0] 
activate_this = p + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, p) 
from app import app as application

if __name__ == '__main__':
    application.run(debug=True)