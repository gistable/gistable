import nuke


def duplicate_node(node, to_file = None):
    """Slightly convoluted but reliable(?) way duplicate a node, using
    the same functionality as the regular copy and paste.

    Could almost be done tidily by doing:

    for knobname in src_node.knobs():
        value = src_node[knobname].toScript()
        new_node[knobname].fromScript(value)

    ..but this lacks some subtly like handling custom knobs

    to_file can be set to a string, and the node will be written to a
    file instead of duplicated in the tree
    """

    # Store selection
    orig_selection = nuke.selectedNodes()

    # Select only the target node
    [n.setSelected(False) for n in nuke.selectedNodes()]
    node.setSelected(True)

    # If writing to a file, do that, restore the selection and return
    if to_file is not None:
        nuke.nodeCopy(to_file)
        [n.setSelected(False) for n in orig_selection]
        return


    # Copy the selected node and clear selection again
    nuke.nodeCopy("%clipboard%")
    node.setSelected(False)

    if to_file is None:
        # If not writing to a file, call paste function, and the new node
        # becomes the selected
        nuke.nodePaste("%clipboard%")
        new_node = nuke.selectedNode()

    # Restore original selection
    [n.setSelected(False) for n in nuke.selectedNodes()] # Deselect all
    [n.setSelected(True) for n in orig_selection] # Select originally selected

    return new_node
