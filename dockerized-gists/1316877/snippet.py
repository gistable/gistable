#!/usr/bin/env python
import sys, os, time, platform

sample_ansi = '\x1b[31mRED' + '\x1b[33mYELLOW' +  '\x1b[32mGREEN' + '\x1b[35mPINK' + '\x1b[0m' + '\n'


for handle in [sys.stdout, sys.stderr]:
    if (hasattr(handle, "isatty") and handle.isatty()) or \
        ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
        if platform.system()=='Windows' and not ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
            handle.write("Windows console, no ANSI support.\n")
        else:
            handle.write("ANSI output enabled.\n")
            handle.write(sample_ansi)
    else:
        handle.write("ANSI output disabled.\n")

    handle.write("\n\n")
    handle.flush()
    time.sleep(0.2)
