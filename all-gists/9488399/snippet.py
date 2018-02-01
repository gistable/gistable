#!/usr/bin/python
import subprocess
import os
import sys

#res = subprocess.Popen(['ls','-al','/ahome'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);
#output,error = res.communicate()

#if res.returncode:
#   #raise Exception(error)
#   print "error>>>> ",res.returncode
#else:
#   print "output>>>> ",output
 
try:
    res = subprocess.Popen(['ls','-al','/home'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);
    #res = subprocess.Popen(['xls','-al','/home'],stdout=subprocess.PIPE);
    output,error = res.communicate()
    if output:
        print "ret> ",res.returncode
        print "OK> output ",output
    if error:
        print "ret> ",res.returncode
        print "Error> error ",error.strip()
#except CalledProcessError as e:
#   print "CalledError > ",e.returncode
#   print "CalledError > ",e.output
except OSError as e:
    print "OSError > ",e.errno
    print "OSError > ",e.strerror
    print "OSError > ",e.filename
except:
    print "Error > ",sys.exc_info()[0]
