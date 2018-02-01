#!/usr/bin/env python
import subprocess
import optparse
import platform

#---------------------------------------Globals----------------------------------------------------
install = []
PLATFORM = platform.system()
ARCHITECTURE = platform.architecture()[0]

#-------------------------------------Running commands---------------------------------------------
def run_commands(cmds):
    """
    Function for running commands one by one.
    """
	for cmd in cmds:
		try:
			subprocess.call(cmd, shell=True)
		except Exception as e:
			print e

#--------------------------------------Option parsing----------------------------------------------
def controller():
    """
    Function which does parsing on options received from command line. Also prepares commands
    that are used in installation.
    """
    global VERBOSE,install
    #Create instance of OptionParser Module, included in Standard Library
    p = optparse.OptionParser(description='For installing Anaconda',
                                            prog='install_anaconda',
                                            version='install_anaconda 0.1',
                                            usage= '%prog [option]')
    p.add_option('--install','-i', action="store_true", help='installs anaconda')
    p.add_option('--verbose', '-v',
                action = 'store_true',
                help='prints verbosely',
                default=False)

    #Option Handling passes correct parameter to runBash
    options, arguments = p.parse_args()
    
    if options.verbose:
        VERBOSE=True
    if options.install:
    	#----------------------------------------setting commands----------------------------------
		#Download the script
		if PLATFORM == "Linux":
				if ARCHITECTURE == "32bit":
					INSTALL.append("wget http://09c8d0b2229f813c1b93-c95ac804525aac4b6dba79b00b39d1d3.r79.cf1.rackcdn.com/Anaconda-2.1.0-Linux-x86.sh")
				elif ARCHITECTURE == "64bit":
					INSTALL.append("wget http://09c8d0b2229f813c1b93-c95ac804525aac4b6dba79b00b39d1d3.r79.cf1.rackcdn.com/Anaconda-2.1.0-Linux-x86_64.sh")
		else:
			print "Wrong operating system detected."
		
		#running script
		INSTALL.append("bash Anaconda-2.1.0-Linux*.sh")

		#setting the path
		INSTALL.append("export PATH=~/anaconda/bin:$PATH")

		value = run_commands(install)
    else:
        p.print_help()

#Runs all the functions
def main():
    controller()

#This idiom means the below code only runs when executed from command line
if __name__ == '__main__':
    main()
