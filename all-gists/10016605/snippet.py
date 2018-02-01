# python

""" Snippet demonstrates how to filter item selection out so it contains
only items of required type (group items in this case).
Filtered items are printed out in Event Log.
"""

import lx
import lxu.select

# Grab current item selection using lxu.select module (see Editing Item Name gist).
selected_items = lxu.select.ItemSelection().current()

# Services in MODO are always available and they provide access to various parts of Nexus system.
# Usually services are used to get some data about the system or instance new objects
# that will be operated on later using lx.object.xxx interfaces.
# Scene service provides general information on the scene and its items.
# We are going to use scene service to get a group item type integer code.
# Typically, when you call a method that needs item type as argument it takes this integer code.
# However, you should NOT use the code directly as it may change from version to version
# and therefore is not reliable. Instead, we are going to use scene service's ItemTypeLookup method
# that will return the proper code after passing an item type string symbol to it.
# The symbol is one of lx.symbol.sITYPE_xxx.
scene_service = lx.service.Scene()
group_type_code = scene_service.ItemTypeLookup(lx.symbol.sITYPE_GROUP)

# The rest is simple now. We're walking selected items list,
# checking item type using Type() method of lx.object.Item() interface.
# Type() returns an integer type code so all we need to do is compare it
# with the code that we got from scene service.
# If the type fits the filter we're printing item's name in Event Log.
for item in selected_items:
    item = lx.object.Item(item)
    if item.Type() == group_type_code:
        lx.out(item.UniqueName())