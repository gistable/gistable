"""Usage:
  build.py find <regexp> <path> 
  build.py -h | --help | --version
"""
from docopt import docopt

def find(arguments):
	print(arguments)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1.1rc')
    command = [x for x in arguments if arguments[x] == True]
    if len(command) > 0 and command[0] in locals():
    	locals()[command[0]](arguments)