# Tab completion
a<Tab> # first car and hit tab

# Instropection
a = 'Foo says hello'
a? # shows info about variable, docstrings if it is function/class
aa?? # shows source code

# Unix Commands
!git # normal git command inside Ipython. Most of the Unix commands can be used this way
!ls -la

# Magic Commands

# Running a script 
%run foo.py # No need to import, just run

# Pasting
%paste # paste code on Ipython, takes care of everything.

# Time reporting
%time statement # %timeit statement - for average of multiple excutions

# Debugging 
%debug # just after exceptation
%run -d foo.py # invoke debugger before excuting any code

# Profiling 
%prun -l -s foo() # profiling blocks of code

# Reloading 
# Every time code changes, restarting IPython is not cool. 
import foo_lib
reload(foo_lib)

# Notebook 
# Notebook is indeed notebook. Combine text, interactive programming and visuals in your browser
ipython notebook #FTW

# Open saved .ipynb files
ipython notebook saved_file.ipynb