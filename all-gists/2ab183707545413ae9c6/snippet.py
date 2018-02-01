#!/usr/bin/python
import ctypes, ctypes.util

# Import CoreGraphics as a C library, so we can call some private functions
c_CoreGraphics = ctypes.CDLL(ctypes.util.find_library('CoreGraphics'))

def disable_beam_sync(doDisable):
    if doDisable:
        # Disabling beam sync:
        # 1st: Enable Quartz debug
        err = c_CoreGraphics.CGSSetDebugOptions(ctypes.c_uint64(0x08000000))
        # 2nd: Set beam sync to disabled mode
        err = c_CoreGraphics.CGSDeferredUpdates(0)
    else:
        # Enabling beam sync:
        # 1st: Disable Quartz debug
        err = c_CoreGraphics.CGSSetDebugOptions(0)
        # 2nd: Set beam sync to automatic mode (the default)
        err = c_CoreGraphics.CGSDeferredUpdates(1)

# Disable beam sync
disable_beam_sync(True)