'''A simple example of a custom marking menu in Maya. The benefits of doing it this way with Python are that 
it is very flexible and easily maintainable. Additionally, you can keep it in a version control system.


This file is used for demonstration purposes, to be followed along with in this blog post

http://bindpose.com/custom-marking-menu-maya-python/
'''
import maya.cmds as mc

MENU_NAME = "markingMenu"


class markingMenu():
    '''The main class, which encapsulates everything we need to build and rebuild our marking menu. All
    that is done in the constructor, so all we need to do in order to build/update our marking menu is
    to initialize this class.'''

    def __init__(self):

        self._removeOld()
        self._build()

    def _build(self):
        '''Creates the marking menu context and calls the _buildMarkingMenu() method to populate it with all items.'''
        menu = mc.popupMenu(MENU_NAME, mm=1, b=2, aob=1, ctl=1, alt=1, sh=0, p="viewPanes", pmo=1, pmc=self._buildMarkingMenu)

    def _removeOld(self):
        '''Checks if there is a marking menu with the given name and if so deletes it to prepare for creating a new one.
        We do this in order to be able to easily update our marking menus.'''
        if mc.popupMenu(MENU_NAME, ex=1):
            mc.deleteUI(MENU_NAME)

    def _buildMarkingMenu(self, menu, parent):
        '''This is where all the elements of the marking menu our built.'''

        # Radial positioned
        mc.menuItem(p=menu, l="South West Button", rp="SW", c="print 'SouthWest'")
        mc.menuItem(p=menu, l="South East Button", rp="SE", c=exampleFunction)
        mc.menuItem(p=menu, l="North East Button", rp="NE", c="mc.circle()")

        subMenu = mc.menuItem(p=menu, l="North Sub Menu", rp="N", subMenu=1)
        mc.menuItem(p=subMenu, l="North Sub Menu Item 1")
        mc.menuItem(p=subMenu, l="North Sub Menu Item 2")

        mc.menuItem(p=menu, l="South", rp="S", c="print 'South'")
        mc.menuItem(p=menu, ob=1, c="print 'South with Options'")

        # List
        mc.menuItem(p=menu, l="First menu item")
        mc.menuItem(p=menu, l="Second menu item")
        mc.menuItem(p=menu, l="Third menu item")
        mc.menuItem(p=menu, l="Create poly cube", c="mc.polyCube()")

        # Rebuild
        mc.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)

markingMenu()


def exampleFunction(*args):
    '''Example function to demonstrate how to pass functions to menuItems'''
    print "example function"


def rebuildMarkingMenu(*args):
    '''This function assumes that this file has been imported in the userSetup.py
    and all it does is reload the module and initialize the markingMenu class which
    rebuilds our marking menu'''
    mc.evalDeferred("""
reload(markingMenu)
markingMenu.markingMenu()
""")
