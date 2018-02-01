################
#   CPROFILE   #
#############################################################################

# 1 - Profile myfunc() from ipython
import cProfile
filename = 'filename.prof'
cProfile.run('myfunc()', filename)

# 2 - Convert your file to a usable kcachegrind file in your shell
#    ?> sudo pip install pyprof2calltree
#    ?> pyprof2calltree -i filename.prof -o callgrind.filename.prof

# 3 - Open callgrind.filename.prof in kcachegrind

#############################################################################





########################
#   EMBEDDED CPROFILE   #
#############################################################################

# 1 - Profile few lines in your code.
import cProfile
filename = 'filename.prof'
pr = cProfile.Profile()
pr.enable()
# ... lines to profile ...
pr.disable()
pr.dump_stats(filename)

# 2 - Convert your file to a usable kcachegrind file in your shell
#    ?> sudo pip install pyprof2calltree
#    ?> pyprof2calltree -i filename.prof -o callgrind.filename.prof

# 3 - Open callgrind.filename.prof in kcachegrind

#############################################################################





#############
#   YAPPI   #
#############################################################################

# 1 - Profile myfunc() from ipython or from your code
import yappi
filename = 'callgrind.filename.prof'
yappi.set_clock_type('cpu')
yappi.start(builtins=True)
myfunc()
stats = yappi.get_func_stats()
stats.save(filename, type='callgrind')

# 2 - Open callgrind.filename.prof in kcachegrind

#############################################################################
