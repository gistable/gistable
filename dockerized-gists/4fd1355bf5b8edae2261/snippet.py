# Get a random line from the Zen of Python without a print (preferably for a colorful cow to chant!)

# Replace stdout by an anonymous class that returns nothing on write()
import sys
stdout = sys.stdout
sys.stdout = type('BlackHole', (), {'write': (lambda self, string: '')})()

# This import's output has now been supressed
import this

# Restate stdout
sys.stdout = stdout

# Get a list of this' zen-lines and print a random one.
import random
print random.choice(''.join([this.d.get(i, i) for i in this.s]).splitlines()[2:])


# Condensed into a line:
import sys, random; stdout = sys.stdout; sys.stdout = type('BlackHole', (), {'write': (lambda self, string: '')})(); import this; sys.stdout = stdout; print random.choice(''.join([this.d.get(i, i) for i in this.s]).splitlines()[2:]);




# For the colorful cow run in a shell and pipe to cowsay and lolcat :P
# python -c "import sys, random; stdout = sys.stdout; sys.stdout = type('BlackHole', (), {'write': (lambda self, string: '')})(); import this; sys.stdout = stdout; print random.choice(''.join([this.d.get(i, i) for i in this.s]).splitlines()[2:]);" | cowsay | lolcat

# cowsay: Likely to be in your distro's repository (e.g. sudo apt-get cowsay)
# lolcat: It's a Ruby gem. Make sure you have Ruby installed and run gem install lolcat

# Add to .bashrc for ultimate zen-ness