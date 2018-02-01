# Example of using the Cinema 4D Tree View GUI in Python.

import c4d
import os
import weakref

# Be sure to use a unique ID obtained from http://www.plugincafe.com/.
PLUGIN_ID = 9912399
PLUGIN_NAME = "Python TreeView Example"
PLUGIN_HELP = "Show the current scene hierarchy in a tree."

# Bit for the Checkbox in the GUI. Kind of a bad practice to use this
# but reduces complexity for this example.
BIT_CHECKED = 256
S
# TreeView Column IDs.
ID_CHECKBOX = 1
ID_ICON = 2
ID_TREEVIEW = 3


class Hierarchy(c4d.gui.TreeViewFunctions):

  def __init__(self, dlg):
    # Avoid a cyclic reference.
    self._dlg = weakref.ref(dlg)

  def GetFirst(self, root, userdata):
    """
    Return the first element in the hierarchy. This can be any Python
    object. With Cinema 4D nodes, it is easy to implement, but it could
    as well be a Python integer which you can use as an index in a list.

    Returns:
      (any or None): The first element in the hierarchy or None.
    """

    doc = c4d.documents.GetActiveDocument()
    return doc.GetFirstObject()

  def GetDown(self, root, userdata, obj):
    """
    Returns:
      (any or None): The child element going from *obj* or None.
    """

    return obj.GetDown()

  def GetNext(self, root, userdata, obj):
    """
    Returns:
      (any or None): The next element going from *obj* or None.
    """

    return obj.GetNext()

  def GetPred(self, root, userdata, obj):
    """
    Returns:
      (any or None): The previous element going from *obj* or None.
    """

    return obj.GetPred()

  def GetName(self, root, userdata, obj):
    """
    Returns:
      (str): The name to display for *obj*.
    """

    return obj.GetName()

  def Open(self, root, userdata, obj, opened):
    """
    Called when the user opens or closes the children of *obj* in
    the Tree View.
    """

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE_SELECTION, obj)

    if opened:
      obj.SetBit(c4d.BIT_OFOLD)
    else:
      obj.DelBit(c4d.BIT_OFOLD)
    doc.EndUndo()
    c4d.EventAdd()

  def IsOpened(self, root, userdata, obj):
    """
    Returns:
      (bool): True if *obj* is opened (expaneded), False if it is
        closed (collapsed).
    """

    return obj.GetBit(c4d.BIT_OFOLD)

  def DeletePressed(self, root, userdata):
    """
    Called when the user right-click Deletes or presses the Delete key.
    Should delete all selected elements.
    """

    def delete_recursive(op):
      if op is None: return
      if op.GetBit(c4d.BIT_ACTIVE) == True:
        doc.AddUndo(c4d.UNDOTYPE_DELETE, op)
        op.Remove()
        return
      for child in op.GetChildren():
        delete_recursive(child)

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    for obj in doc.GetObjects():
      delete_recursive(obj)
    doc.EndUndo()
    c4d.EventAdd()

  def Select(self, root, userdata, obj, mode):
    """
    Called when the user selects an element.
    """

    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()

    def deselect_recursive(op):
      if op is None: return
      doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, op)
      op.DelBit(c4d.BIT_ACTIVE)
      for child in op.GetChildren():
        deselect_recursive(child)

    if mode == c4d.SELECTION_SUB:
      doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, obj)
      obj.DelBit(c4d.BIT_ACTIVE)
    else:
      if mode == c4d.SELECTION_NEW:
        deselect_recursive(obj.GetDocument().GetFirstObject())

      doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, obj)
      obj.SetBit(c4d.BIT_ACTIVE)

    doc.EndUndo()
    c4d.EventAdd()

  def IsSelected(self, root, userdata, obj):
    """
    Returns:
      (bool): True if *obj* is selected, False if not.
    """

    return obj.GetBit(c4d.BIT_ACTIVE)

  def DoubleClick(self, root, userdata, obj, col, mouseinfo):
    """
    Called when the user double-clicks on an entry in the TreeView.

    Returns:
      (bool): True if the double-click was handled, False if the
        default action should kick in. The default action will invoke
        the rename procedure for the object, causing `SetName()` to be
        called.
    """

    c4d.gui.MessageDialog("You clicked on " + obj.GetName())
    return True

  def IsResizeColAllowed(self, root, userdata, lColID):
    return True

  def IsTristate(self, root, userdata):
    return False

  def GetDragType(self, root, userdata, obj):
    """
    Returns:
      (int): The drag datatype.
    """

    return c4d.DRAGTYPE_ATOMARRAY

  def DragStart(self, root, userdata, obj):
    """
    Returns:
      (int): Bitmask specifying options for the drag, whether it is
        allowed, etc.
    """

    return c4d.TREEVIEW_DRAGSTART_ALLOW | c4d.TREEVIEW_DRAGSTART_SELECT

  def GetId(self, root, userdata, obj):
    """
    Return a unique ID for the element in the TreeView.
    """

    return obj.GetUniqueID()

  def SetName(self, root, userdata, obj, name):
    """
    Called when the user renames the element. `DoubleClick()` must return
    False for this to work.
    """

    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL, obj)
    doc.EndUndo()
    obj.SetName(name)
    c4d.EventAdd()

  def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
    """
    Called for a cell with layout type `c4d.LV_USER` or `c4d.LV_USERTREE`
    to draw the contents of a cell.
    """

    if col == ID_ICON:
      icon = obj.GetIcon()
      drawinfo["frame"].DrawBitmap(
        icon["bmp"], drawinfo["xpos"], drawinfo["ypos"],
        16, 16, icon["x"], icon["y"], icon["w"], icon["h"], c4d.BMP_ALLOWALPHA)

  def SetCheck(self, root, userdata, obj, column, checked, msg):
    """
    Called when the user clicks on a checkbox for an object in a
    `c4d.LV_CHECKBOX` column.
    """

    if checked:
      obj.SetBit(BIT_CHECKED)
    else:
      obj.DelBit(BIT_CHECKED)

    def checked_collect(op):
      if op is None: return
      elif isinstance(op, c4d.documents.BaseDocument):
        for obj in op.GetObjects():
          for x in checked_collect(obj):
            yield x
      else:
        if op.GetBit(BIT_CHECKED):
          yield op
        for child in op.GetChildren():
          for x in checked_collect(child):
            yield x

    status = ', '.join(obj.GetName() for obj in checked_collect(obj.GetDocument()))
    self._dlg().SetString(1001, "Checked: " + status)
    self._dlg()._treegui.Refresh()

  def IsChecked(self, root, userdata, obj, column):
    """
    Returns:
      (int): Status of the checkbox in the specified *column* for *obj*.
    """

    val = obj.GetBit(BIT_CHECKED)
    if val == True:
      return c4d.LV_CHECKBOX_CHECKED | c4d.LV_CHECKBOX_ENABLED
    else:
      return c4d.LV_CHECKBOX_ENABLED

  def HeaderClick(self, root, userdata, column, channel, is_double_click):
    """
    Called when the TreeView header was clicked.

    Returns:
      (bool): True if the event was handled, False if not.
    """

    c4d.gui.MessageDialog("You clicked on the '%i' header." % (column))
    return True

  def AcceptDragObject(self, root, userdata, obj, dragtype, dragobject):
    """
    Called when a drag & drop operation hovers over the TreeView to check
    if the drag can be accepted.

    Returns:
      (int, bool)
    """

    if dragtype != c4d.DRAGTYPE_ATOMARRAY:
      return 0

    return c4d.INSERT_BEFORE | c4d.INSERT_AFTER | c4d.INSERT_UNDER, True

  def GenerateDragArray(self, root, userdata, obj):
    """
    Return:
      (list of c4d.BaseList2D): Generate a list of objects that can be
        dragged from the TreeView for the `c4d.DRAGTYPE_ATOMARRAY` type.
    """

    if obj.GetBit(c4d.BIT_ACTIVE):
      return [obj, ]

  def InsertObject(self, root, userdata, obj, dragtype, dragobject, insertmode, bCopy):
    """
    Called when a drag is dropped on the TreeView.
    """

    if dragtype != c4d.DRAGTYPE_ATOMARRAY:
      return # Shouldnt happen, we catched that in AcceptDragObject

    for op in dragobject:
      op.Remove()
      if insertmode == c4d.INSERT_BEFORE:
        op.InsertBefore(obj)
      elif insertmode == c4d.INSERT_AFTER:
        op.InsertAfter(obj)
      elif insertmode == c4d.INSERT_UNDER:
        op.InsertUnder(obj)
    return

  def GetColumnWidth(self, root, userdata, obj, col, area):
    return 80 # All have the same initial width

  def IsMoveColAllowed(self, root, userdata, lColID):
    # The user is allowed to move all columns.
    # TREEVIEW_MOVE_COLUMN must be set in the container of AddCustomGui.
    return True

  def GetColors(self, root, userdata, obj, pNormal, pSelected):
    """
    Retrieve colors for the TreeView elements.

    Returns:
      (int or c4d.Vector, int or c4d.Vector): The colors for the normal
        and selected state of the element.
    """

    usecolor = obj[c4d.ID_BASEOBJECT_USECOLOR]
    if usecolor == c4d.ID_BASEOBJECT_USECOLOR_ALWAYS:
      pNormal = obj[c4d.ID_BASEOBJECT_COLOR]
    return pNormal, pSelected

  # Context menu entry for "Hello World!"
  ID_HELLOWORLD = 355435345

  def CreateContextMenu(self, root, userdata, obj, lColumn, bc):
    """
    User clicked with the right mouse button on an entry so
    we can here enhance the menu
    """

    bc.SetString(self.ID_HELLOWORLD, "Hello World!")

  def ContextMenuCall(self, root, userdata, obj, lColumn, lCommand):
    """
    The user executes an entry of the context menu.

    Returns:
      (bool): True if the event was handled, False if not.
    """

    if lCommand == self.ID_HELLOWORLD:
      obj.SetName("Hello World!")
      c4d.EventAdd()
      return True
    return False

  def SelectionChanged(self, root, userdata):
    """
    Called when the selected elements in the TreeView changed.
    """

    print "The selection changed"

  def Scrolled(self, root, userdata, h, v, x, y):
    """
    Called when the TreeView is scrolled.
    """

    self._dlg().SetString(1002, ("H: %i V: %i X: %i Y: %i" % (h, v, x, y)))


class TestDialog(c4d.gui.GeDialog):

  _treegui = None

  def CreateLayout(self):
    # Create the TreeView GUI.
    customgui = c4d.BaseContainer()
    customgui.SetBool(c4d.TREEVIEW_BORDER, True)
    customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, True)
    customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, False)
    customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, True)
    customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True)
    customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True)
    customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True)
    self._treegui = self.AddCustomGui(
      1000, c4d.CUSTOMGUI_TREEVIEW, "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
      300, 300, customgui)
    if not self._treegui:
      print "[ERROR]: Could not create TreeView"
      return False

    self.AddMultiLineEditText(1001, c4d.BFH_SCALEFIT | c4d.BFV_SCALE | c4d.BFV_BOTTOM, 0, 40)
    self.AddEditText(1002, c4d.BFH_SCALEFIT, 0, 25)
    return True

  def CoreMessage(self, id, msg):
    if id == c4d.EVMSG_CHANGE:
      # Update the treeview on each change in the document.
      self._treegui.Refresh()
    return True

  def InitValues(self):
    # Initialize the column layout for the TreeView.
    layout = c4d.BaseContainer()
    layout.SetLong(ID_CHECKBOX, c4d.LV_CHECKBOX)
    layout.SetLong(ID_ICON, c4d.LV_USER)
    layout.SetLong(ID_TREEVIEW, c4d.LV_TREE)
    self._treegui.SetLayout(3, layout)

    # Set the header titles.
    self._treegui.SetHeaderText(ID_CHECKBOX, "Check")
    self._treegui.SetHeaderText(ID_ICON, "Icon")
    self._treegui.SetHeaderText(ID_TREEVIEW, "Name")
    self._treegui.Refresh()

    # Don't need to store the hierarchy, due to SetRoot()
    data_model = Hierarchy(self)
    self._treegui.SetRoot(None, data_model, None)

    self.SetString(1002, "Scroll values")
    return True


class MenuCommand(c4d.plugins.CommandData):

  dialog = None

  def Execute(self, doc):
    """
    Just create the dialog when the user clicked on the entry
    in the plugins menu to open it
    """

    if self.dialog is None:
       self.dialog = TestDialog()
    return self.dialog.Open(
      c4d.DLG_TYPE_ASYNC, PLUGIN_ID, defaulth=600, defaultw=600)

  def RestoreLayout(self, sec_ref):
    """
    Same for this method. Just allocate it when the dialog is needed.
    """

    if self.dialog is None:
       self.dialog = TestDialog()
    return self.dialog.Restore(PLUGIN_ID, secret=sec_ref)


def main():
  c4d.plugins.RegisterCommandPlugin(
    PLUGIN_ID, PLUGIN_NAME, 0, None, PLUGIN_HELP, MenuCommand())


if __name__ == "__main__":
  main()
