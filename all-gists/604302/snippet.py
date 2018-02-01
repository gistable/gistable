"""
Here's how to run a command from Python piping a string in to stdin and reading the 
output back in to another string. It took me way too long to work this out.
"""

from subprocess import Popen, PIPE

output = Popen(
    ['java', '-jar', 'yuicompressor-2.4.2.jar', '--type=css'], 
    stdin=PIPE, stdout=PIPE
).communicate(input='/* a comment */ .foo {color: red}')[0]
