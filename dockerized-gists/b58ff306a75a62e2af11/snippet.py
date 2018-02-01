#!/usr/bin/python
# encoding: utf-8
import os
import plistlib

def check_for_workflow(name):
    """Check if specified workflow name exists"""
    workflows_dir = os.path.dirname(os.getcwd())
    all_wfs = os.walk(workflows_dir).next()[1]
    found = False
    for wf in all_wfs:
        plist = workflows_dir + "/" + wf + "/info.plist"
        if os.path.isfile(plist):
            plist_info = plistlib.readPlist(plist)
            wf_name = plist_info['name'].lower()
            if wf_name == name.lower():
                found = True
                break
    return found