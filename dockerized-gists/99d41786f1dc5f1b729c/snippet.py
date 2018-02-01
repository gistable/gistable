def hideAllViewerQtInfosWidgets():
    try:
        import PySide.QtGui as QtGui

        parentApp = QtGui.QApplication.allWidgets()
        parentName = "Viewer"
        name = "/"

        parentViewer = None
        for parent in parentApp:
            for child in parent.children():
                try:
                    if child.text() == name:
                        parentViewer = child.parent().parent().parent()
                        if parentName in parentViewer.objectName():
                            if child.parent().parent().parent().metaObject().className() == "Viewer_Window":
                                child.setChecked(True)
                                break
                except:
                    pass
    except Exception, e:
        print "ERROR:", e