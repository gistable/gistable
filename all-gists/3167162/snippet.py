"""
A simple script to kick off a certain ROP remotely, optionally
with a given framerange.

Usage: hython path/to/script/houBatch.py /path/to/hipfile /hou/path/to/rop

TODO: Add options for multiple ROPs, hperf.
"""
import hou, sys

# Load the hip file
hou.hipFile.load(sys.argv[1])

# If framerange option, set it
#if sys.argv[3]:
#    hou.parmTuple( "%s/f" %(sys.argv[2]) ).set((sys.argv[3],sys.argv[4],1.0))

# Start the render
hou.node(sys.argv[2]).render()

# When finished, exit
sys.exit(0)