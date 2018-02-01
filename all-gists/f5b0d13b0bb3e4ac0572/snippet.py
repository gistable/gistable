# Isolate selection

import c4d
import c4d.gui as gui
import urllib
import datetime
import platform
import traceback
import contextlib
import webbrowser

REPORT_SUBJ = "Error report for C4D Isolate Script"
REPORT_ADDR = "support@provider.com"
LAYER = "ISOLATE"
SELECT_CHILDREN = 16388
SOLO = 100004726
CAMERA = 5103
assert c4d.GetCommandName(SELECT_CHILDREN) == "Select Children"
assert c4d.GetCommandName(SOLO) == "Solo"

@contextlib.contextmanager
def report():
    err = None
    try:
        yield
    except Exception:
        if gui.QuestionDialog("There was an error running the script. Would you like to send a brief report?"):
            # Generate Report
            webbrowser.open("mailto:{email}?subject={subject}&body={body}".format(
                email=REPORT_ADDR,
                subject=urllib.quote(REPORT_SUBJ),
                body=urllib.quote("\n".join((
                    str(datetime.datetime.now()),
                    platform.platform(),
                    __file__,
                    traceback.format_exc()
                )))
            ))
        raise

def solo_layer(layer, state):
    layer_data = layer.GetLayerData(doc)
    layer_data["solo"] = state
    layer.SetLayerData(doc, layer_data)
    c4d.CallButton(layer, SOLO) # Solo Layer
    c4d.EventAdd()

def walk(objs):
    for o in objs:
        yield o
        for child in walk(o.GetChildren()):
            yield child

def main():
    doc = c4d.documents.GetActiveDocument()
    layer_root = doc.GetLayerObjectRoot()

    for layer in layer_root.GetChildren(): # Ensure layer is there
        if layer.GetName() == LAYER:
            solo_layer(layer, False)
            layer.Remove()
            c4d.EventAdd()
            break

    selection = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

    if selection:
        doc.StartUndo()
        try:
            # Create Layer
            layer = c4d.documents.LayerObject()
            layer.SetName(LAYER)
            layer.InsertUnder(layer_root)
            solo_layer(layer, True)

            # Grab children
            c4d.CallCommand(SELECT_CHILDREN)
            tmp_selection = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

            # Add children to layer
            for sel in tmp_selection:
                sel[c4d.ID_LAYER_LINK] = layer

            # Add cameras to layer
            for cam in (cam for cam in walk(doc.GetObjects()) if cam.CheckType(CAMERA)):
                cam[c4d.ID_LAYER_LINK] = layer

            # Reinstate selection
            doc.SetActiveObject(selection.pop(), c4d.SELECTION_NEW)
            for obj in selection:
                doc.SetActiveObject(obj, c4d.SELECTION_ADD)
            c4d.EventAdd()
        finally:
            doc.EndUndo()

if __name__ == '__main__':
    with report():
        main()
