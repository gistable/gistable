#!/usr/bin/python

"""
This script take a cloud-config file as input and returns the 'shellified'
script that would be produced by cloudinit from the runcmd stanza.

https://github.com/number5/cloud-init/blob/74e61ab27addbfcceac4eba254f739ef9964b0ed/cloudinit/config/cc_runcmd.py
https://github.com/number5/cloud-init/blob/74e61ab27addbfcceac4eba254f739ef9964b0ed/cloudinit/util.py#L1708
"""

import sys
import os
import yaml
import six

def handle(cfg):
    if "runcmd" not in cfg:
        print("Skipping, no 'runcmd' key in configuration")
        return

    cmd = cfg["runcmd"]
    try:
        content = shellify(cmd)
    except Exception as e:
        print("Failed to shellify:\nError: {0}\n{1}").format(e, cmd)

    return content

def shellify(cmdlist, add_header=True):
    content = ''
    if add_header:
        content += "#!/bin/sh\n"
    escaped = "%s%s%s%s" % ("'", '\\', "'", "'")
    cmds_made = 0
    for args in cmdlist:
        # If the item is a list, wrap all items in single tick.
        # If its not, then just write it directly.
        if isinstance(args, list):
            fixed = []
            for f in args:
                fixed.append("'%s'" % (six.text_type(f).replace("'", escaped)))
            content = "%s%s\n" % (content, ' '.join(fixed))
            cmds_made += 1
        elif isinstance(args, six.string_types):
            content = "%s%s\n" % (content, args)
            cmds_made += 1
        else:
            raise RuntimeError(("Unable to shellify type %s"
                                " which is not a list or string")
                               % (type_utils.obj_name(args)))
    print("Shellified {} commands.\n").format(cmds_made)

    return content

if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print("Requires the full path to a file with a list of tutorial slugs.")
        sys.exit()
    else:
        fn = sys.argv[1]
        with open(fn, 'r') as fh:
            try:
                cfg = yaml.safe_load(fh.read())
                script = handle(dict(cfg))
                if script:
                    print(script)
            except Exception as e:
                print("Error parsing yaml:\n\n{}").format(e)