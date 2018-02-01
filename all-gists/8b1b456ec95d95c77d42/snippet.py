from PySide import QtGui


class QDictBox(QtGui.QDialog):
    WIDGETS = {str: QtGui.QLineEdit,
               unicode: QtGui.QLineEdit,
               int: QtGui.QSpinBox,
               float: QtGui.QDoubleSpinBox,
               list: QtGui.QComboBox,
               bool: QtGui.QCheckBox}
    GETTERS = {QtGui.QLineEdit: "text",
               QtGui.QSpinBox: "value",
               QtGui.QDoubleSpinBox: "value",
               QtGui.QComboBox: "currentText",
               QtGui.QCheckBox: "isChecked"}
    SETTERS = {QtGui.QLineEdit: "setText",
               QtGui.QSpinBox: "setValue",
               QtGui.QDoubleSpinBox: "setValue",
               QtGui.QComboBox: "addItems",
               QtGui.QCheckBox: "setChecked"}
    VALIDATORS = {QtGui.QLineEdit: lambda x: bool(len(x)),
                  QtGui.QSpinBox: lambda x: True,
                  QtGui.QDoubleSpinBox: lambda x: True,
                  QtGui.QComboBox: lambda x: True,
                  QtGui.QCheckBox: lambda x: True}

    @classmethod
    def getValues(cls, parent, options, required=None, title=None):
        d = cls(parent, options, required, title)

        ok = d.exec_()
        return d.values if ok else {}

    def __init__(self, parent, options, required=None, title=None):
        super(QDictBox, self).__init__(parent)
        self.__widgets = dict()
        self.__values = dict()

        if title:
            self.setWindowTitle(title)

        self.required = required or list()
        if len(options) == 1:
            self.required.append(options.keys()[0])

        _firstWidget = None
        formLayout = QtGui.QFormLayout()
        for k, v in options.iteritems():
            if isinstance(v, (list, tuple)):
                v = [str(x) for x in v]

            label = QtGui.QLabel(beautifyText(k))
            widget = self.WIDGETS[type(v)]()
            getattr(widget, self.SETTERS[type(widget)])(v)

            if k in self.required:
                label.setStyleSheet("color: red;")

            self.__widgets[k] = (label, widget)
            formLayout.addRow(label, widget)

            if _firstWidget is None:
                _firstWidget = widget

        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QtGui.QFrame.Shape(0))  # no frame
        w = QtGui.QWidget()
        w.setLayout(formLayout)
        scrollArea.setWidget(w)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(scrollArea)
        layout.addWidget(buttons)
        self.setLayout(layout)

        _firstWidget.setFocus()

    def accept(self):
        for k, (label, widget) in self.widgets.iteritems():
            value = getattr(widget, self.GETTERS[type(widget)])()
            self.__values[k] = value

        for k in self.required:
            value = self.values[k]
            label, widget = self.widgets[k]
            if not self.VALIDATORS[type(widget)](value) and widget.isVisible():
                widget.setFocus()
                return

        return super(QDictBox, self).accept()

    @property
    def widgets(self):
        return self.__widgets

    @property
    def values(self):
        return self.__values


def beautifyText(camelCasedText):
    rval = ""
    for i, ch in enumerate(camelCasedText):
        if i == 0:
            ch = ch.upper()
        elif ch.isupper():
            ch = " " + ch
        rval += ch
    return rval