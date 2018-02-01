def root_settings_to_string(root):
    """Serialise the project settings. Used when writing the selected
    nodes (otherwise things like the frame range would be lost)
    """

    # Write non-default settings, in .nk script format. Also write
    # user-knob definitons to avoid errors like NUKE-256
    rootstring = root.writeKnobs(nuke.TO_SCRIPT | nuke.WRITE_USER_KNOB_DEFS)

    # TODO: Why doesn't writeKnobs write [first/last]_frame? Also
    # should it ignore the 'name' (script location), or this is
    # accidental?
    rootstring = "%s\nfirst_frame %d\nlast_frame %d" % (rootstring, root['first_frame'].value(), root['last_frame'].value())
    # FIXME: Properly quote format name in case someone is insane and puts quotes etc in their format name
    rootstring = "%s\nproxy_format \"%s\"" % (rootstring, root['proxy_format'].toScript())
    rootstring = "Root {\n%s\n}" % rootstring

    return rootstring


def save_selected(path):
    # Copy selected nodes to file
    nuke.nodeCopy(path)

    # Hackishly persist root settings
    rootstring = root_settings_to_string(nuke.root())

    # Open saved nodes, then prepend the root settings string
    noroot = open(path).read()
    with open(path, "w+") as f:
        f.write((rootstring + "\n" + noroot))

# To add to menu:
#
# nuke.menu("Nuke").findItem("File").addCommand("Save selected (with root settings)",
#     lambda: save_selected(path=nuke.getFilename("File to save")))