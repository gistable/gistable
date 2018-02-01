"""ShaderBrowser
Based on: https://developers.maxon.net/?p=439"""

# ====== IMPORTS ====== #

import c4d


# ====== GLOBALS ====== #

debug = True

PLUGIN_ID = 1037564
PLUGIN_NAME = "Shader Browser"
PLUGIN_HELP = "A simple treeview example"


# ====== UTILS ====== #

def GetNextElement(op):
    """Returns the next material or shader after `op`."""

    if not op:
        return

    if op.IsInstanceOf(c4d.Mmaterial) and op.GetFirstShader():
        return op.GetFirstShader()
    elif op.GetDown():
        return op.GetDown()

    while (not op.GetNext()) and op.GetUp():
        op = op.GetUp()

    return op.GetNext()


# ====== TREEVIEW ====== #

class ShaderTree(c4d.gui.TreeViewFunctions):
    """Data structure for a TreeView of Materials & Shaders."""

    def GetFirst(self, root, userdata):
        """Returns the first Material in the document."""

        if not root:
            return

        doc = root
        return doc.GetFirstMaterial()

    def GetDown(self, root, userdata, obj):
        """Get the next shader in the list."""

        if not root or not obj:
            return

        mat = obj
        if mat.IsInstanceOf(c4d.Mmaterial):
            return mat.GetFirstShader()

        shader = mat
        return shader.GetDown()

    def GetNext(self, root, userdata, obj):
        """Get the next material/shader in the list."""

        if not root or not obj:
            return

        mat = obj
        return mat.GetNext()

    def IsSelected(self, root, userdata, obj):
        """Returns True if obj is selected."""

        if not root or not obj:
            return False

        mat = obj
        return mat.GetBit(c4d.BIT_ACTIVE)

    def Deselect(self, doc):
        """Deselects all Materials and Shaders in `doc`"""

        if not doc:
            return

        mat = doc.GetFirstMaterial()
        if not mat:
            return

        while mat:
            mat.DelBit(c4d.BIT_ACTIVE)
            mat = GetNextElement(mat)

    def Select(self, root, userdata, obj, mode):
        """Selects `obj` based on `mode`."""

        if not root or not obj:
            if debug:
                print "Select() no Root or Obj"
            return

        mat = obj
        doc = root

        # New Selection
        if mode == c4d.SELECTION_NEW:
            if debug:
                print "SELECTION_NEW"

            self.Deselect(doc)
            mat.SetBit(c4d.BIT_ACTIVE)

        # Add to Current Selection
        elif mode == c4d.SELECTION_ADD:
            if debug:
                print "SELECTION_ADD"

            mat.SetBit(c4d.BIT_ACTIVE)

        # Deselect
        elif mode == c4d.SELECTION_SUB:
            if debug:
                print "SELECTION_SUB"
            mat.DelBit(c4d.BIT_ACTIVE)

        c4d.EventAdd()

    def IsOpened(self, root, userdata, obj):
        """Returns True if obj is unfolded."""

        if not root or not obj:
            return False

        mat = obj
        return mat.GetBit(c4d.BIT_OFOLD)

    def Open(self, root, userdata, obj, onoff):
        """Folds or unfolds obj based on onoff."""

        if not root or not obj:
            return

        mat = obj

        if onoff:
            mat.SetBit(c4d.BIT_OFOLD)
        else:
            mat.DelBit(c4d.BIT_OFOLD)

    def GetName(self, root, userdata, obj):
        """Returns the name of obj."""

        if not root or not obj:
            return

        mat = obj
        if not mat:
            return

        return mat.GetName()

    def SetName(self, root, userdata, obj, name):
        """Update obj's name to name."""

        if not root or not obj or name is None:
            return

        mat = obj
        return mat.SetName(name)

    def GetId(self, root, userdata, obj):
        """Returns a unique ID for obj."""

        mat = obj
        if mat is None:
            return

        return mat.GetUniqueID()

    def GetDragType(self, root, userdata, obj):
        """Says that drag/drop is not okay."""

        return c4d.NOTOK

# ====== DIALOG ====== #

class ShaderBrowser(c4d.gui.GeDialog):
    """Dialog that contains a list of Materials & Shaders in the active document."""

    def __init__(self):
        self._shaderTreeGui = None
        pass

    def CreateLayout(self):
        """Build the overall dialog layout."""

        self.SetTitle(PLUGIN_NAME)

        # Build the ShaderTree GUI Element
        treedata = c4d.BaseContainer()
        self._shaderTreeGui = self.AddCustomGui(1000,
                                                c4d.CUSTOMGUI_TREEVIEW,
                                                "",
                                                c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                                                0, 0,
                                                treedata)

        if self._shaderTreeGui:
            layout = c4d.BaseContainer()
            layout.SetLong(0, c4d.LV_TREE)

            # Let C4D know there is one column
            if not self._shaderTreeGui.SetLayout(1, layout):
                return False

            # Tell the ShaderTree which document it belongs to.
            if not self._shaderTreeGui.SetRoot(c4d.documents.GetActiveDocument(), ShaderTree(), None):
                return False

            self._shaderTreeGui.Refresh()

        return True

    def UpdateTree(self, doc):
        """Rebuilds the shader tree gui element from scratch."""

        if not doc or not self._shaderTreeGui:
            return False

        if not self._shaderTreeGui.SetRoot(doc, ShaderTree(), None):
            return False

        self._shaderTreeGui.Refresh()
        return True

    def InitValues(self):
        """Set initial values when dialog is first opened."""

        doc = c4d.documents.GetActiveDocument()
        if not doc:
            return False
        if not self.UpdateTree(doc):
            return False

        return True

    def CoreMessage(self, id, msg):
        """Rebuild the shader tree gui when something big happens."""

        doc = c4d.documents.GetActiveDocument()
        if not doc:
            return False
        if not self.UpdateTree(doc):
            return False

        return True


# ====== COMMAND ====== #

class ShaderBrowserCommand(c4d.plugins.CommandData):
    """Command that opens a ShaderTree dialog."""

    dlg = None

    def Execute(self, doc):
        if self.dlg is None:
            self.dlg = ShaderBrowser()

        return self.dlg.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=PLUGIN_ID,
            xpos=-1,
            ypos=-1,
            defaultw=300,
            defaulth=500
        )

    def GetState(self, doc):
        return c4d.CMD_ENABLED

    def RestoreLayout(self, secret):
        return self.dlg.Restore(PLUGIN_ID, secret)

def main():
    """Register the plugin with Cinema 4D."""

    c4d.plugins.RegisterCommandPlugin(
        PLUGIN_ID,
        PLUGIN_NAME,
        0,
        None,
        PLUGIN_HELP,
        ShaderBrowserCommand()
    )

if __name__ == "__main__":
    main()