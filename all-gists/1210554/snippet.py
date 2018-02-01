#!/usr/bin/env python
#
# script name: meta-outliers.py
# 
# In the spirit of release early, release often, here's a script
# that's part of a larger project I'm working on.
#
# What does it do?
# Parses the output from the Sleuth Kit's fls command.
# More specifically fls -arp run against a disk image or dev.
#
# "Fantastic," you say. "What does fls -arp do?"
#
# fls -arp returns file type, deleted status, metadata address
# and full path information.
#
# "Hm, not much to that fls output. What does it parse from fls?"
#
# meta-outliers.py goes through the output of fls and returns
# the average metadata address and the standard deviation on
# a per path basis and returns a list of all files that have
# metadata addresses outside the standard deviation for their
# directory. It shows you a list of outliers, hence the name.
#
# "Why should I care?"
#
# You need more useless trivia in your life. This will help.
# At parties you'll say "On my Win7 box the metadata address of my
# SAM file is two standard deviations from normal."
#
# You win.
#
# Alternatively, you may be able to use this to find suspicious
# files in random file systems. But probably not. In my limited
# testing, this does greatly reduce the data set from hundreds
# of thousands of files, to a few thousand or a few hundred.
# But that's still more noise than most people want to deal
# with. So, there's more to come. 
#
# Release early. Release often.
#
# To use it: ./meta-outliers.py <fls_output>
#
# Adjust the stddevs value below to change what's considered
# an outlier.
# 
# Author: Dave Hull
# License: We don't need no stinking license. I hereby place
# this in the public domain.
#
# Todo: 
# fls seems to parse in alpha-order so it dives into sub
# dirs before completely returning results for all files in
# a given directory, need to compensate for that.
#
# 20110911: Fixed the issue relating to fls' parsing in alpha
# order, but Python dictionaries are unsorted so the output
# of the script is now mostly random. Newer versions of
# Python have a sorted() method for sorting dictionaries,
# but the version of Python on the host I'm developing on is
# hopelessly out of date (thanks CentOS & Red Hat).
#
# I'm moving development to a system with a newer version of
# Python and will fix it, but the resulting script may not
# run on as many systems.
#
# A newer version of Python will also let me use argparse
# for handling command line arguments like setting the 
# outlier threshhold.
# 
# Much more, this is just a PoC/starting point.

import re, fileinput, os, math

def get_deviants():
    current_path    = None
    meta_addr_total = 0
    deviation       = {}
    dev_sum         = 0
    stddevs         = 1   # Modify. This returns anything above 1 std dev
    path            = {}


    pattern = re.compile("./.\s(?P<deleted>\**\s*)(?P<meta_addr>\d+)-?"
        "(?P<meta_type>\d{3})?-?(?P<meta_id>\d+)?:\s(?P<path>.*$)")

    fi = fileinput.FileInput()
    for line in fi:
        matches = pattern.finditer(line)
        for m in matches:

            if len(m.group('deleted')) > 0:         # Skip deleted files
                continue

            fname = os.path.basename(m.group('path')).rstrip()
            pname = os.path.dirname(m.group('path')).rstrip()

            if fname == ".." or fname == ".":       # Parent directories skew path averages
                continue                            # On some systems '.' is different enough to skew

            if len(pname) == 0:
                pname = "/"

            if pname not in path:
                path[pname] = {}

            path[pname][fname] = int(m.group('meta_addr'))

    for pathname in path.keys():
        file_cnt = len(path[pathname])
        if file_cnt > 1:
            for filename in path[pathname].keys():
                meta_addr = path[pathname][filename]
                if meta_addr == 0:                   # Deleted files w/no meta addr skew results
                    del path[pathname][filename]     # This removes them from consideration
                    file_cnt -= 1
                    continue

                meta_addr_total += path[pathname][filename]

            avg = meta_addr_total / file_cnt

            for filename in path[pathname].keys():
                meta_addr = path[pathname][filename]
                deviation[filename] = meta_addr - avg
                dev_sum += (deviation[filename] ** 2)

            std_dev = math.sqrt((dev_sum * 1.0) / (file_cnt * 1.0))

            no_header = True
            for filename in path[pathname].keys():
                if math.fabs(deviation[filename]) > (stddevs * std_dev):
                    if no_header:
                        print "\nPath Meta Addr Avg: %10d -- Std. Dev.: %12.2f -- Path: %s" % (avg, std_dev, pathname)
                        no_header = False
                    print "    File Meta Addr: %10d --      Dev.: %12.2f -- File:   %s" % (path[pathname][filename], deviation[filename], filename)

            meta_addr_total = dev_sum = 0

get_deviants()